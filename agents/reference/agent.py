"""Canonical agent interface. Vulnerable and protected variants implement this.

# Run from repo root: python -m agents.vulnerable.agent
"""

from __future__ import annotations

import abc
import hashlib
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict

from starter.python.log_schema import LogEvent, LogWriter


class ToolCall(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    args: dict[str, Any]


class ToolResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    tool_name: str
    content: str
    error: str | None = None


class AgentConfig(BaseModel):
    agent_id: str = "reference-agent"
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.0
    max_tokens: int = 4096
    max_steps: int = 10


class BaseAgent(abc.ABC):
    """Abstract base for all agent variants."""

    def __init__(self, config: AgentConfig, log_writer: LogWriter | None = None) -> None:
        self.config = config
        self.log_writer = log_writer
        self._session_id: str = ""
        self._step: int = 0

    def run(self, user_input: str) -> str:
        """Execute agent loop. Returns final text response."""
        self._session_id = str(uuid.uuid4())
        self._step = 0
        return self._run_loop(user_input)

    @abc.abstractmethod
    def _run_loop(self, user_input: str) -> str:
        """Concrete agents implement the step loop here."""
        ...

    @abc.abstractmethod
    def _execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a single tool call. Returns result."""
        ...

    def _emit(self, event: LogEvent) -> None:
        """Write log event to writer if configured."""
        if self.log_writer:
            self.log_writer.write(event)

    @staticmethod
    def _hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]


# Tool definitions for the Anthropic tools parameter
TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "web_fetch",
        "description": "Fetch content from a URL. Returns up to 8KB of text.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "The URL to fetch"}},
            "required": ["url"],
        },
    },
    {
        "name": "read_doc",
        "description": "Read a document from the corpus by name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Document filename (e.g. 'policy.md')",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "send_message",
        "description": "Send a message to a recipient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "Recipient email or identifier",
                },
                "body": {"type": "string", "description": "Message body"},
            },
            "required": ["recipient", "body"],
        },
    },
]
