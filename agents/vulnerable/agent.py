"""Vulnerable agent: no defenses. For educational red-teaming only."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.reference.agent import AgentConfig, BaseAgent, ToolCall, ToolResult, TOOL_DEFINITIONS
from agents.reference.tools import dispatch_tool
from starter.python.log_schema import LogWriter, make_event
from starter.python.openai_client import OpenAIAdapter

try:
    from starter.python.anthropic_client import AnthropicAdapter
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

SYSTEM_PROMPT_PATH = (
    Path(__file__).parent.parent.parent / "starter/python/prompt_templates/system_prompt.txt"
)


class VulnerableAgent(BaseAgent):
    """Concrete agent with NO security defenses.

    Intentionally omits:
    - Injection detection
    - Output filtering
    - Tool allowlist enforcement
    - Egress URL checking
    - Tool argument validation
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        log_writer: LogWriter | None = None,
    ) -> None:
        super().__init__(config or AgentConfig(), log_writer)
        self._system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

        # Try Anthropic first, fall back to OpenAI.
        # AnthropicAdapter.__init__ raises RuntimeError when ANTHROPIC_API_KEY is absent,
        # and ImportError propagates if the 'anthropic' package is not installed — both
        # cases are caught so the agent can fall back to OpenAI transparently.
        if _ANTHROPIC_AVAILABLE:
            try:
                self._adapter = AnthropicAdapter(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
            except RuntimeError:
                self._adapter = OpenAIAdapter(
                    model="gpt-4.1",
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
        else:
            self._adapter = OpenAIAdapter(
                model="gpt-4.1",
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

    # ------------------------------------------------------------------
    # BaseAgent implementation
    # ------------------------------------------------------------------

    def _run_loop(self, user_input: str) -> str:
        """Step loop — explicit iteration, no recursion.

        Uses Anthropic-native message format throughout so that the conversation
        history is valid for both AnthropicAdapter (primary) and OpenAIAdapter
        (fallback, which accepts the same format and converts internally).

        Tool call IDs are generated locally because AnthropicAdapter.run()
        strips the ``id`` field from tool_use blocks when returning tool_calls.
        The generated IDs are used to wire up the matching tool_result blocks.
        """
        # Anthropic-native format: content is a list of content blocks.
        messages: list[dict] = [{"role": "user", "content": user_input}]

        for step in range(self.config.max_steps):
            self._step = step

            # Emit model_call event before hitting the API.
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
                # No tool calls — final response.
                self._emit(
                    make_event(
                        agent_id=self.config.agent_id,
                        session_id=self._session_id,
                        step=step,
                        event_type="final_response",
                        model=self.config.model,
                    )
                )
                return text

            # Build the assistant message in Anthropic-native block format.
            # Assign fresh IDs to tool_use blocks because the adapter strips them.
            assistant_content: list[dict] = []
            if text:
                assistant_content.append({"type": "text", "text": text})

            # Pair each tool call with a generated ID for round-tripping.
            annotated: list[tuple[str, dict]] = []
            for tc in tool_calls:
                tool_id = f"toolu_{uuid.uuid4().hex[:24]}"
                assistant_content.append(
                    {"type": "tool_use", "id": tool_id, "name": tc["name"], "input": tc["input"]}
                )
                annotated.append((tool_id, tc))

            messages.append({"role": "assistant", "content": assistant_content})

            # Execute tools and collect results.
            tool_result_blocks: list[dict] = []

            for tool_id, tc in annotated:
                tool_call = ToolCall(name=tc["name"], args=tc["input"])

                # Log tool_call — no redaction in the vulnerable variant.
                self._emit(
                    make_event(
                        agent_id=self.config.agent_id,
                        session_id=self._session_id,
                        step=step,
                        event_type="tool_call",
                        tool_name=tc["name"],
                        tool_args_redacted=tc["input"],  # intentionally unredacted
                    )
                )

                result = self._execute_tool(tool_call)

                result_text = (
                    result.content if not result.error else f"Error: {result.error}"
                )

                # Log tool_result.
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

            # Anthropic-native format: tool results go in a "user" turn.
            messages.append({"role": "user", "content": tool_result_blocks})

        return "Maximum steps reached without final response."

    def _execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute tool with NO validation — vulnerable by design."""
        return dispatch_tool(tool_call)


def main() -> None:
    """Quick test: run the vulnerable agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the vulnerable agent (no defenses).")
    parser.add_argument(
        "query",
        nargs="?",
        default="What tools do you have available?",
    )
    args = parser.parse_args()

    agent = VulnerableAgent()
    response = agent.run(args.query)
    print(response)


if __name__ == "__main__":
    main()
