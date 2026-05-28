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

    preset = build_preset_for_challenge(challenge)
    return ProtectedAgent(preset=preset)


def run_challenge_with_agent(
    challenge: Challenge,
    agent: Any,
    *,
    payload: str,
) -> dict[str, Any]:
    """Run *agent* on *payload* and grade the result against *challenge*.

    Returns a dict with the same shape the API endpoint emits:
      {events, goal_achieved, detector_evaded, fired_layer, agent_response}
    """
    # Use the instrumented helper from the eval harness when the agent supports
    # _execute_tool interception (i.e. real ProtectedAgent / VulnerableAgent).
    # Fall back to a plain .run() call for lightweight fake agents used in tests.
    if hasattr(agent, "_execute_tool"):
        from evals.harness.runner import _run_agent_instrumented
        response, tool_calls = _run_agent_instrumented(agent, payload)
    else:
        response = agent.run(payload)
        tool_calls = list(getattr(agent, "_last_tool_calls", []))

    events = list(getattr(agent, "_last_events", []))  # reference agent appends here

    blocked, fired_layer = summarize_blockage(events)

    goal_achieved = grade(
        challenge.grader_goal,
        response=response,
        tool_calls=tool_calls,
        events=events,
    )

    return {
        "events": events,
        "goal_achieved": goal_achieved,
        "detector_evaded": not blocked,
        "fired_layer": fired_layer,
        "agent_response": response,
    }
