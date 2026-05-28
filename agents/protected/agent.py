"""Protected agent: all defenses composed. Reference implementation for portfolio."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.protected.gateway import GatewayConfig, ToolGateway
from agents.reference.agent import AgentConfig, BaseAgent, ToolCall, ToolResult, TOOL_DEFINITIONS
from detectors.output_filter import OutputFilter
from detectors.rules import RulesDetector
from range.schema import DefensePreset
from starter.python.log_schema import LogWriter, make_event

try:
    from detectors.classifier import ClassifierDetector

    _CLASSIFIER_AVAILABLE = True
except ImportError:
    _CLASSIFIER_AVAILABLE = False

try:
    from starter.python.anthropic_client import AnthropicAdapter

    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

try:
    from starter.python.openai_client import OpenAIAdapter

    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

SYSTEM_PROMPT_PATH = (
    Path(__file__).parent.parent.parent / "starter/python/prompt_templates/system_prompt.txt"
)

# Confidence thresholds for the rule-based detector.
_INPUT_BLOCK_CONFIDENCE = 0.6  # block user input if injection confidence >= this
_TOOL_RESULT_TAG_CONFIDENCE = 0.5  # tag tool result if IPI confidence >= this

# Prefix prepended to tool results that contain injection patterns.
_UNTRUSTED_PREFIX = "[UNTRUSTED_INJECTION_DETECTED] "


def _make_default_gateway_config() -> GatewayConfig:
    """Return the hardened default gateway configuration.

    - web_fetch: no URL allowlist (all public URLs allowed except RFC1918 + loopback + AWS metadata)
    - send_message: empty recipient allowlist → deny all external sends by default
    - max_web_fetch_calls: 5
    - max_send_message_calls: 2
    - hitl_enabled: False
    """
    return GatewayConfig(
        web_fetch_url_allowlist=[],  # allow any non-internal URL
        send_message_recipient_allowlist=[],  # deny all — caller must pre-authorise
        max_web_fetch_calls=5,
        max_send_message_calls=2,
        max_read_doc_calls=10,
        max_total_bytes=32768,
        hitl_enabled=False,
    )


class ProtectedAgent(BaseAgent):
    """Concrete agent with ALL security defenses composed in layers.

    Defense stack (in order of application):
    1. Input validation — RulesDetector blocks injections before the LLM sees them.
    2. Tool gateway — ToolGateway enforces per-tool call budgets and egress policies.
    3. Tool-result validation — RulesDetector tags IPI patterns in tool output.
    4. Output filtering — OutputFilter strips exfiltration vectors from final responses.
    5. Structured logging — all six event types are emitted throughout.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        log_writer: LogWriter | None = None,
        gateway_config: GatewayConfig | None = None,
        allowed_recipients: list[str] | None = None,
        enable_classifier: bool = False,
        preset: DefensePreset | None = None,
    ) -> None:
        super().__init__(config or AgentConfig(agent_id="protected-agent"), log_writer)
        self._system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

        # --- Defense preset (None ⇒ legacy hardcoded behavior) ---
        self._preset: DefensePreset | None = preset

        # --- LLM adapter (Anthropic preferred, OpenAI fallback) ---
        # Adapter initialisation is deferred to first use so that the object can
        # be constructed in environments where API keys are not yet configured.
        self._adapter = None
        self._adapter_initialized = False

        # --- Defense layer 1: rule-based injection detector ---
        self._detector = RulesDetector()

        # --- Defense layer 1b (opt-in): LLM-as-judge classifier ---
        # Only instantiated when the caller asks for it AND the SDK + API key
        # are available. Silently falls back to rules-only when not usable.
        self._classifier = None
        if enable_classifier and _CLASSIFIER_AVAILABLE:
            try:
                self._classifier = ClassifierDetector()
            except RuntimeError:
                # No API key configured — keep classifier off and continue.
                self._classifier = None

        # --- Defense layer 2: tool gateway ---
        cfg = gateway_config or _make_default_gateway_config()
        if allowed_recipients:
            # Merge caller-supplied recipients into the allowlist.
            cfg = GatewayConfig(
                web_fetch_url_allowlist=cfg.web_fetch_url_allowlist,
                send_message_recipient_allowlist=list(allowed_recipients),
                max_web_fetch_calls=cfg.max_web_fetch_calls,
                max_send_message_calls=cfg.max_send_message_calls,
                max_read_doc_calls=cfg.max_read_doc_calls,
                max_total_bytes=cfg.max_total_bytes,
                hitl_enabled=cfg.hitl_enabled,
                hitl_callback=cfg.hitl_callback,
                egress_deny_patterns=cfg.egress_deny_patterns,
            )
        self._gateway = ToolGateway(cfg)

        # --- Defense layer 3: output filter ---
        self._output_filter = OutputFilter()

    # ------------------------------------------------------------------
    # Preset gating helpers
    # ------------------------------------------------------------------

    def _should_run_input_check(self) -> bool:
        if self._preset is None:
            return True  # legacy default
        return self._preset.rules_input

    def _should_check_tool_result(self) -> bool:
        if self._preset is None:
            return True
        return self._preset.rules_tool_result

    def _should_use_gateway(self) -> bool:
        if self._preset is None:
            return True
        return self._preset.gateway_budgets or self._preset.gateway_egress_blocks

    def _should_filter_output(self) -> bool:
        if self._preset is None:
            return True
        return self._preset.output_filter

    def _input_threshold(self) -> float:
        if self._preset is None:
            return _INPUT_BLOCK_CONFIDENCE
        return self._preset.rules_input_threshold

    def _tool_result_threshold(self) -> float:
        if self._preset is None:
            return _TOOL_RESULT_TAG_CONFIDENCE
        return self._preset.rules_tool_result_threshold

    # ------------------------------------------------------------------
    # BaseAgent implementation
    # ------------------------------------------------------------------

    def _run_loop(self, user_input: str) -> str:  # noqa: PLR0912
        """Step loop with all defense layers applied.

        Uses Anthropic-native message format throughout (same as VulnerableAgent) so
        the conversation history is valid for both adapters.
        """
        # ── Defense 1: input validation ──────────────────────────────────────
        block_confidence = 0.0
        block_detector = ""
        block_matches: list[str] = []
        if self._should_run_input_check():
            input_check = self._detector.check(user_input)
            block_confidence = input_check.confidence
            block_detector = "RulesDetector"
            block_matches = list(input_check.matched_rules)

        # Defense 1b: ask the LLM judge too (opt-in). If it agrees with higher
        # confidence than the rules, we use its score for the block decision.
        # Only runs when the input-check layer is enabled by the preset.
        if self._classifier is not None and self._should_run_input_check():
            judge = self._classifier.check(user_input)
            if judge.error is None and judge.confidence > block_confidence:
                block_confidence = judge.confidence
                block_detector = "ClassifierDetector"
                block_matches.append(f"classifier:{judge.reasoning[:80]}")

        if self._should_run_input_check() and block_confidence >= self._input_threshold():
            self._emit(
                make_event(
                    agent_id=self.config.agent_id,
                    session_id=self._session_id,
                    step=0,
                    event_type="policy_violation",
                    detector_name=block_detector,
                    detector_score=block_confidence,
                    severity="high",
                    metadata={
                        "reason": "input_injection_blocked",
                        "matched_rules": block_matches,
                    },
                )
            )
            return (
                "Your request was blocked by the security policy because it contains "
                "patterns associated with prompt injection. Please rephrase your query."
            )

        # Initialise the gateway for this session.
        self._gateway.new_session(self._session_id)

        # Lazily initialise the LLM adapter (deferred to avoid crashing on import
        # when API keys are absent).
        self._ensure_adapter()

        messages: list[dict] = [{"role": "user", "content": user_input}]

        for step in range(self.config.max_steps):
            self._step = step

            # Emit model_call event.
            self._emit(
                make_event(
                    agent_id=self.config.agent_id,
                    session_id=self._session_id,
                    step=step,
                    event_type="model_call",
                    model=self.config.model,
                    prompt_hash=self._hash_prompt(self._system_prompt),
                )
            )

            text, tool_calls = self._adapter.run(messages, TOOL_DEFINITIONS, self._system_prompt)

            if not tool_calls:
                # ── Defense 4: output filtering ───────────────────────────────
                output_was_filtered = False
                if self._should_filter_output():
                    filter_result = self._output_filter.filter(text)
                    if filter_result.was_modified:
                        output_was_filtered = True
                        self._emit(
                            make_event(
                                agent_id=self.config.agent_id,
                                session_id=self._session_id,
                                step=step,
                                event_type="detector_hit",
                                detector_name="OutputFilter",
                                detector_score=1.0,
                                severity="medium",
                                metadata={"violations": filter_result.violations},
                            )
                        )
                    final_text = filter_result.filtered_text
                else:
                    final_text = text

                self._emit(
                    make_event(
                        agent_id=self.config.agent_id,
                        session_id=self._session_id,
                        step=step,
                        event_type="final_response",
                        model=self.config.model,
                        metadata={"output_filtered": output_was_filtered},
                    )
                )
                return final_text

            # Build the assistant message in Anthropic-native block format.
            assistant_content: list[dict] = []
            if text:
                assistant_content.append({"type": "text", "text": text})

            annotated: list[tuple[str, dict]] = []
            for tc in tool_calls:
                tool_id = f"toolu_{uuid.uuid4().hex[:24]}"
                assistant_content.append(
                    {
                        "type": "tool_use",
                        "id": tool_id,
                        "name": tc["name"],
                        "input": tc["input"],
                    }
                )
                annotated.append((tool_id, tc))

            messages.append({"role": "assistant", "content": assistant_content})

            tool_result_blocks: list[dict] = []

            for tool_id, tc in annotated:
                tool_call = ToolCall(name=tc["name"], args=tc["input"])

                self._emit(
                    make_event(
                        agent_id=self.config.agent_id,
                        session_id=self._session_id,
                        step=step,
                        event_type="tool_call",
                        tool_name=tc["name"],
                        tool_args_redacted=tc["input"],
                    )
                )

                if self._should_use_gateway():
                    result_text = self._execute_tool_with_gateway(tool_call, step)
                else:
                    # L0 path: direct dispatch, no policy checks.
                    from agents.reference.tools import dispatch_tool
                    raw_result = dispatch_tool(tool_call)
                    result_text = raw_result.content if not raw_result.error else f"Error: {raw_result.error}"

                # ── Defense 3: tool-result injection check ────────────────────
                if self._should_check_tool_result():
                    ipi_check = self._detector.check_tool_result(tc["name"], result_text)
                    if ipi_check.is_injection and ipi_check.confidence >= self._tool_result_threshold():
                        self._emit(
                            make_event(
                                agent_id=self.config.agent_id,
                                session_id=self._session_id,
                                step=step,
                                event_type="detector_hit",
                                detector_name="RulesDetector",
                                detector_score=ipi_check.confidence,
                                severity="high",
                                tool_name=tc["name"],
                                metadata={
                                    "reason": "ipi_detected_in_tool_result",
                                    "matched_rules": ipi_check.matched_rules,
                                },
                            )
                        )
                        result_text = _UNTRUSTED_PREFIX + result_text

                self._emit(
                    make_event(
                        agent_id=self.config.agent_id,
                        session_id=self._session_id,
                        step=step,
                        event_type="tool_result",
                        tool_name=tc["name"],
                        tool_result_size=len(result_text.encode()),
                    )
                )

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result_text,
                    }
                )

            messages.append({"role": "user", "content": tool_result_blocks})

        return "Maximum steps reached without final response."

    def _execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute tool via the gateway (policy-checked)."""
        gateway_result = self._gateway.execute(
            tool_name=tool_call.name,
            args=tool_call.args,
            tool_fn=self._raw_tool_fn(tool_call.name),
        )
        if not gateway_result.allowed:
            return ToolResult(
                tool_name=tool_call.name,
                content="",
                error=f"Blocked by policy: {gateway_result.policy_violation}",
            )
        return ToolResult(tool_name=tool_call.name, content=gateway_result.tool_result)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_adapter(self) -> None:
        """Lazily initialise the LLM adapter on first use."""
        if self._adapter_initialized:
            return
        if _ANTHROPIC_AVAILABLE:
            try:
                self._adapter = AnthropicAdapter(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                self._adapter_initialized = True
                return
            except RuntimeError:
                pass  # fall through to OpenAI

        if _OPENAI_AVAILABLE:
            try:
                from starter.python.openai_client import OpenAIAdapter

                self._adapter = OpenAIAdapter(
                    model="gpt-4.1",
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                self._adapter_initialized = True
                return
            except RuntimeError:
                pass

        raise RuntimeError(
            "No LLM adapter available. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file."
        )

    def _execute_tool_with_gateway(self, tool_call: ToolCall, step: int) -> str:
        """Run the tool through the gateway; emit policy_violation if blocked."""
        gateway_result = self._gateway.execute(
            tool_name=tool_call.name,
            args=tool_call.args,
            tool_fn=self._raw_tool_fn(tool_call.name),
        )

        if not gateway_result.allowed:
            self._emit(
                make_event(
                    agent_id=self.config.agent_id,
                    session_id=self._session_id,
                    step=step,
                    event_type="policy_violation",
                    tool_name=tool_call.name,
                    severity="high",
                    metadata={
                        "policy_violation": gateway_result.policy_violation,
                        "tool_args": tool_call.args,
                    },
                )
            )
            return f"Tool call blocked: {gateway_result.policy_violation}"

        return gateway_result.tool_result

    def _raw_tool_fn(self, tool_name: str):  # type: ignore[return]
        """Return the unwrapped callable for *tool_name* (used by ToolGateway)."""
        from agents.reference.tools import read_doc, send_message, web_fetch

        match tool_name:
            case "web_fetch":
                return web_fetch
            case "read_doc":
                return read_doc
            case "send_message":
                return send_message
            case _:
                def _unknown(**_kwargs: object) -> ToolResult:
                    return ToolResult(
                        tool_name=tool_name,
                        content="",
                        error=f"Unknown tool: {tool_name}",
                    )

                return _unknown


def main() -> None:
    """Quick smoke-test: run the protected agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the protected agent (all defenses).")
    parser.add_argument(
        "query",
        nargs="?",
        default="What tools do you have available?",
    )
    parser.add_argument(
        "--enable-classifier",
        action="store_true",
        help="Also run the LLM-as-judge classifier on user input (extra API call per request).",
    )
    args = parser.parse_args()

    agent = ProtectedAgent(enable_classifier=args.enable_classifier)
    response = agent.run(args.query)
    print(response)


if __name__ == "__main__":
    main()
