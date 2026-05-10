"""Drop-in OpenAI adapter for the ai-security-lab reference agent.

Provides ``OpenAIAdapter``, which exposes the same ``run()`` interface as
``AnthropicAdapter`` so the two can be swapped transparently.  Tool definitions
are converted from Anthropic format (``input_schema``) to OpenAI format
(``parameters``) internally.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

import openai
from dotenv import load_dotenv

from starter.python.log_schema import LogWriter, log_event, make_event

__all__ = ["OpenAIAdapter"]

# Pick up OPENAI_API_KEY (and any other vars) from a .env file if present.
load_dotenv()


def _convert_messages(messages: list[dict]) -> list[dict]:
    """Convert Anthropic-format conversation history to OpenAI format.

    Handles two non-trivial cases:
    - assistant messages with tool_use blocks → assistant message with tool_calls
    - user messages with tool_result blocks → one role:tool message per result
    """
    import json as _json

    out: list[dict] = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if isinstance(content, str):
            out.append({"role": role, "content": content})
            continue

        if role == "assistant":
            text_parts = [b["text"] for b in content if b.get("type") == "text"]
            tool_use_blocks = [b for b in content if b.get("type") == "tool_use"]
            oai_msg: dict = {"role": "assistant", "content": "".join(text_parts) or None}
            if tool_use_blocks:
                oai_msg["tool_calls"] = [
                    {
                        "id": b["id"],
                        "type": "function",
                        "function": {
                            "name": b["name"],
                            "arguments": _json.dumps(b["input"]),
                        },
                    }
                    for b in tool_use_blocks
                ]
            out.append(oai_msg)

        elif role == "user":
            tool_result_blocks = [b for b in content if b.get("type") == "tool_result"]
            text_blocks = [b for b in content if b.get("type") == "text"]
            for b in tool_result_blocks:
                result_content = b.get("content", "")
                if isinstance(result_content, list):
                    result_content = "".join(
                        c.get("text", "") for c in result_content if c.get("type") == "text"
                    )
                out.append({"role": "tool", "tool_call_id": b["tool_use_id"], "content": result_content})
            if text_blocks:
                out.append({"role": "user", "content": "".join(b.get("text", "") for b in text_blocks)})
        else:
            out.append(msg)

    return out


def _convert_tool(anthropic_tool: dict) -> dict:
    """Convert a single Anthropic-format tool definition to OpenAI format.

    Anthropic uses the key ``input_schema`` for the JSON Schema of tool
    parameters; OpenAI calls the same thing ``parameters`` and nests it
    under a ``function`` key.

    Parameters
    ----------
    anthropic_tool:
        A dict with at least ``name``, ``description``, and ``input_schema``.

    Returns
    -------
    dict
        OpenAI ``{"type": "function", "function": {...}}`` tool definition.
    """
    return {
        "type": "function",
        "function": {
            "name": anthropic_tool["name"],
            "description": anthropic_tool.get("description", ""),
            "parameters": anthropic_tool.get("input_schema", {"type": "object", "properties": {}}),
        },
    }


class OpenAIAdapter:
    """Drop-in adapter using the official OpenAI Python SDK.

    Exposes the same ``run(messages, tools, system_prompt)`` interface as
    ``AnthropicAdapter``.

    Parameters
    ----------
    model:
        OpenAI model identifier.  Defaults to ``"gpt-4.1"``.
    temperature:
        Sampling temperature (0.0 = deterministic).
    max_tokens:
        Maximum tokens in the model response.
    agent_id:
        Logical identifier for the agent instance (used in log events).
    session_id:
        Session identifier grouping multiple ``run()`` calls (used in log events).
    log_writer:
        Optional ``LogWriter`` instance.  When ``None``, events are written to stdout.
    """

    def __init__(
        self,
        model: str = "gpt-4.1",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        agent_id: str = "openai-adapter",
        session_id: str = "default",
        log_writer: LogWriter | None = None,
    ) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set — add it to .env")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.agent_id = agent_id
        self.session_id = session_id
        self._log_writer = log_writer
        self._step = 0

        self._client = openai.OpenAI(api_key=api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> tuple[str, list[dict]]:
        """Call the OpenAI Chat Completions API and return ``(text_content, tool_calls)``.

        Parameters
        ----------
        messages:
            Conversation history in Anthropic message format (role/content pairs).
            The system prompt is prepended automatically.
        tools:
            List of tool definitions in **Anthropic** format (``input_schema``).
            These are converted to OpenAI format internally.
        system_prompt:
            System prompt text prepended to the message list.

        Returns
        -------
        tuple[str, list[dict]]
            ``text_content`` — text from the first choice (may be empty).
            ``tool_calls`` — list of ``{"name": str, "input": dict}`` dicts.
        """
        prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()

        self._emit_log(
            event_type="model_call",
            model=self.model,
            prompt_hash=prompt_hash,
        )

        # Prepend the system message in OpenAI format.
        openai_messages: list[dict] = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(_convert_messages(messages))

        # Convert tools from Anthropic format to OpenAI format.
        openai_tools = [_convert_tool(t) for t in tools] if tools else []

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": openai_messages,
        }
        if openai_tools:
            kwargs["tools"] = openai_tools

        response = self._client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        message = choice.message

        text_content: str = message.content or ""
        tool_calls: list[dict] = []

        if message.tool_calls:
            import json

            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, ValueError) as exc:
                    raise RuntimeError(
                        f"OpenAI returned invalid JSON for tool '{tc.function.name}': {exc}"
                    ) from exc
                tool_calls.append({"name": tc.function.name, "input": args})

        self._step += 1
        return text_content, tool_calls

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _emit_log(self, **kwargs: Any) -> None:
        event = make_event(
            agent_id=self.agent_id,
            session_id=self.session_id,
            step=self._step,
            **kwargs,
        )
        if self._log_writer is not None:
            self._log_writer.write(event)
        else:
            log_event(event)
