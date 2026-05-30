"""Runner: turn a Challenge into a concrete ProtectedAgent + execute one attack.

The runner intentionally does NOT import ProtectedAgent at module scope —
imports happen inside build_agent_for_challenge so that test code can
substitute a fake agent without instantiating an LLM client.
"""
from __future__ import annotations

from typing import Any

from agents.protected.presets import PRESETS_BY_LEVEL
from range.grader import grade, summarize_blockage
from range.schema import Challenge, DefensePreset


def build_preset_for_challenge(challenge: Challenge) -> DefensePreset:
    """Resolve the effective preset for *challenge*.

    preset_overrides REPLACES the base preset entirely when set (not merged).
    This keeps challenge YAMLs explicit — authors declaring overrides must
    spell out every layer state they want.
    """
    if challenge.preset_overrides is not None:
        return challenge.preset_overrides
    return PRESETS_BY_LEVEL[challenge.preset_base_level]


def build_agent_for_challenge(challenge: Challenge):
    """Instantiate a ProtectedAgent configured for *challenge*."""
    # Local import to avoid LLM-client construction at module import time.
    from agents.protected.agent import ProtectedAgent
    from starter.python.log_schema import InMemoryLogWriter

    preset = build_preset_for_challenge(challenge)
    writer = InMemoryLogWriter()
    agent = ProtectedAgent(preset=preset, log_writer=writer)
    return agent, writer


def run_challenge_with_agent(
    challenge: Challenge,
    agent: Any,
    *,
    payload: str,
    log_writer: Any | None = None,
) -> dict[str, Any]:
    """Run *agent* on *payload* and grade the result against *challenge*.

    ``log_writer`` should be an ``InMemoryLogWriter`` that was passed to the
    agent's constructor.  When provided, events are read from its ``.events``
    list after the run, and ``tool_calls`` are derived from ``tool_call``-type
    events (so that the gateway path and the L0 direct-dispatch path are both
    captured correctly).

    When ``log_writer`` is *not* supplied the runner falls back to the legacy
    ``_last_events`` / ``_last_tool_calls`` accessors so that existing fake
    agents used in unit tests continue to work unchanged.

    Returns a dict with the same shape the API endpoint emits:
      {events, tool_calls, goal_achieved, detector_evaded, fired_layer,
       agent_response}
    """
    response = agent.run(payload)

    if log_writer is not None:
        # Primary path: read all events captured by the in-memory writer.
        raw_events: list[dict] = [
            ev.model_dump(mode="json") for ev in log_writer.events
        ]
        # Derive tool_calls from tool_call-type events (works for both the
        # gateway path and the L0 dispatch path).
        tool_calls: list[dict] = [
            {"name": ev["tool_name"], "input": ev.get("tool_args_redacted") or {}}
            for ev in raw_events
            if ev.get("event_type") == "tool_call" and ev.get("tool_name")
        ]
    else:
        # Legacy fallback for lightweight fake agents used in unit tests.
        raw_events = list(getattr(agent, "_last_events", []))
        tool_calls = list(getattr(agent, "_last_tool_calls", []))

    blocked, fired_layer = summarize_blockage(raw_events)

    goal_achieved = grade(
        challenge.grader_goal,
        response=response,
        tool_calls=tool_calls,
        events=raw_events,
    )

    return {
        "events": raw_events,
        "tool_calls": tool_calls,
        "goal_achieved": goal_achieved,
        "detector_evaded": not blocked,
        "fired_layer": fired_layer,
        "agent_response": response,
    }
