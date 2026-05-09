"""Thin wrapper around the official Anthropic Python SDK.

Provides ``AnthropicAdapter``, a lightweight class that drives the reference agent
loop using ``anthropic.Anthropic`` and emits structured ``LogEvent`` records for
every API call.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

import anthropic
from dotenv import load_dotenv

from starter.python.log_schema import LogWriter, make_event

__all__ = ["AnthropicAdapter"]

# Pick up ANTHROPIC_API_KEY (and any other vars) from a .env file if present.
load_dotenv()


class AnthropicAdapter:
    """Thin wrapper around the Anthropic Python SDK for the reference agent.

    Parameters
    ----------
    model:
        Anthropic model identifier.  Defaults to ``"claude-sonnet-4-5"``.
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
        model: str = "claude-sonnet-4-5",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        agent_id: str = "anthropic-adapter",
        session_id: str = "default",
        log_writer: LogWriter | None = None,
    ) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set — add it to .env")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.agent_id = agent_id
        self.session_id = session_id
        self._log_writer = log_writer
        self._step = 0

        self._client = anthropic.Anthropic(api_key=api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> tuple[str, list[dict]]:
        """Call the Anthropic API and return ``(text_content, tool_calls)``.

        Parameters
        ----------
        messages:
            Conversation history in Anthropic message format.
        tools:
            List of tool definitions in Anthropic format (uses ``input_schema``).
        system_prompt:
            System prompt text sent to the model.

        Returns
        -------
        tuple[str, list[dict]]
            ``text_content`` — the first text block from the response (may be empty).
            ``tool_calls`` — list of ``{"name": str, "input": dict}`` dicts.
        """
        prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()

        self._emit_log(
            event_type="model_call",
            model=self.model,
            prompt_hash=prompt_hash,
        )

        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=messages,
            tools=tools,  # type: ignore[arg-type]
        )

        text_content = ""
        tool_calls: list[dict] = []

        for block in response.content:
            if block.type == "text":
                text_content += block.text
            elif block.type == "tool_use":
                tool_calls.append({"name": block.name, "input": block.input})

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
            from starter.python.log_schema import log_event

            log_event(event)
