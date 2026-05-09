"""Canonical log schema for the ai-security-lab reference agent.

All structured log events emitted by adapters, detectors, and the agent loop
use these Pydantic v2 models. Events are written as JSONL — one JSON object per line.
"""

from __future__ import annotations

import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "LogEvent",
    "LogWriter",
    "make_event",
    "log_event",
]

EventType = Literal[
    "model_call",
    "tool_call",
    "tool_result",
    "detector_hit",
    "policy_violation",
    "human_review_requested",
    "final_response",
]

Severity = Literal["low", "medium", "high", "critical"]

TrifectaLeg = Literal["data", "untrusted_input", "egress"]


class LogEvent(BaseModel):
    """Canonical structured log event for the ai-security-lab agent pipeline."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    event_id: str = Field(description="UUID4 unique identifier for this event")
    ts: datetime = Field(description="UTC timestamp of the event")
    agent_id: str = Field(description="Identifier of the agent emitting this event")
    session_id: str = Field(description="Session identifier grouping related events")
    step: int = Field(description="Zero-indexed step within the session")
    event_type: EventType = Field(description="Discriminator for event kind")

    # Model-call fields
    model: str | None = Field(default=None, description="LLM model identifier")
    prompt_hash: str | None = Field(
        default=None, description="SHA-256 hex digest of the system prompt"
    )

    # Tool-call / tool-result fields
    tool_name: str | None = Field(default=None, description="Name of the tool invoked")
    tool_args_redacted: dict | None = Field(
        default=None,
        description="Tool arguments with secret values replaced by '<REDACTED>'",
    )
    tool_result_size: int | None = Field(
        default=None, description="Size of the tool result in bytes"
    )

    # Detector fields
    detector_name: str | None = Field(default=None, description="Detector that fired")
    detector_score: float | None = Field(
        default=None, description="Confidence score from the detector (0.0–1.0)"
    )
    severity: Severity | None = Field(default=None, description="Severity of a finding")
    trifecta_legs_active: list[TrifectaLeg] = Field(
        default_factory=list,
        description="Active legs of the prompt-injection trifecta for this event",
    )

    # Identity fields
    user_id: str | None = Field(default=None, description="Authenticated user identifier")
    org_id: str | None = Field(default=None, description="Organisation identifier")

    # Catch-all
    metadata: dict = Field(default_factory=dict, description="Arbitrary extra metadata")


def make_event(**kwargs: Any) -> LogEvent:
    """Factory that auto-populates *event_id* (uuid4) and *ts* (UTC now).

    Pass any other ``LogEvent`` fields as keyword arguments.

    Example::

        event = make_event(
            agent_id="ref-agent",
            session_id="abc123",
            step=0,
            event_type="model_call",
            model="claude-sonnet-4-5",
        )
    """
    kwargs.setdefault("event_id", str(uuid.uuid4()))
    kwargs.setdefault("ts", datetime.now(tz=UTC))
    return LogEvent(**kwargs)


def log_event(event: LogEvent, path: Path | None = None) -> None:
    """Append *event* as a single JSON line to *path*.

    If *path* is ``None`` the event is written to stdout instead.
    The output is newline-delimited JSON (JSONL) with no pretty-printing so
    that downstream tools (``jq``, Splunk, etc.) can consume it directly.
    """
    line = event.model_dump_json()
    if path is None:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
    else:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


class LogWriter:
    """Context manager that writes ``LogEvent`` objects to a JSONL file.

    Usage::

        with LogWriter(Path("run.jsonl")) as writer:
            event = make_event(agent_id="ref", session_id="s1", step=0,
                               event_type="model_call", model="claude-sonnet-4-5")
            writer.write(event)

    If *path* is ``None`` events are written to stdout.
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._fh = None

    def __enter__(self) -> LogWriter:
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._fh = self._path.open("a", encoding="utf-8")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if self._fh is not None:
            self._fh.close()
            self._fh = None
        return False  # do not suppress exceptions

    def write(self, event: LogEvent) -> None:
        """Write *event* as a single JSONL line."""
        line = event.model_dump_json()
        if self._fh is not None:
            self._fh.write(line + "\n")
            self._fh.flush()
        else:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
