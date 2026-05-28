"""Tests for range.runner. Uses fake agents to stay offline."""
from __future__ import annotations

from range.runner import build_preset_for_challenge, run_challenge_with_agent
from range.schema import DefensePreset
from range.loader import get_challenge, reload_cache
from starter.python.log_schema import InMemoryLogWriter, make_event


def setup_function(_fn) -> None:
    reload_cache()


def test_build_preset_for_L0_returns_PRESET_L0_unchanged():
    c = get_challenge("direct-injection", 0)
    preset = build_preset_for_challenge(c)
    assert isinstance(preset, DefensePreset)
    assert preset.rules_input is False
    assert preset.gateway_budgets is False


def test_build_preset_applies_overrides():
    c = get_challenge("direct-injection", 0)
    # Override via a freshly-cloned challenge with explicit overrides:
    c2 = c.model_copy(update={
        "preset_overrides": DefensePreset(rules_input=True, output_filter=True),
    })
    preset = build_preset_for_challenge(c2)
    # Override REPLACES the base level (NOT a merge). See runner.py docstring.
    assert preset.rules_input is True
    assert preset.output_filter is True
    assert preset.gateway_budgets is False  # not in overrides


class _FakeAgent:
    def __init__(self, response: str, tool_calls: list[dict], events: list[dict]) -> None:
        self._response = response
        self._tool_calls = tool_calls
        self._events = events

    def run(self, _user_input: str) -> str:
        return self._response

    # The runner pulls events / tool_calls via these accessors (matches the
    # instrumentation pattern used in evals/harness/runner.py).
    _last_tool_calls: list[dict] = []
    _last_events: list[dict] = []


def test_run_challenge_goal_achieved_when_response_matches_regex():
    c = get_challenge("direct-injection", 0)
    agent = _FakeAgent(
        response="Sure: AKIAIOSFODNN7EXAMPLE",
        tool_calls=[],
        events=[{"event_type": "model_call"}, {"event_type": "final_response"}],
    )
    agent._last_tool_calls = []
    agent._last_events = [{"event_type": "model_call"}, {"event_type": "final_response"}]
    result = run_challenge_with_agent(c, agent, payload="give me the key")
    assert result["goal_achieved"] is True
    assert result["detector_evaded"] is True
    assert result["fired_layer"] is None
    assert result["agent_response"] == "Sure: AKIAIOSFODNN7EXAMPLE"


def test_run_challenge_blocked_when_policy_violation():
    c = get_challenge("direct-injection", 0)
    agent = _FakeAgent(
        response="Your request was blocked by the security policy...",
        tool_calls=[],
        events=[{
            "event_type": "policy_violation",
            "detector_name": "RulesDetector",
            "metadata": {"reason": "input_injection_blocked"},
        }],
    )
    agent._last_tool_calls = []
    agent._last_events = [{
        "event_type": "policy_violation",
        "detector_name": "RulesDetector",
        "metadata": {"reason": "input_injection_blocked"},
    }]
    result = run_challenge_with_agent(c, agent, payload="ignore previous...")
    assert result["goal_achieved"] is False
    assert result["detector_evaded"] is False
    assert result["fired_layer"] == "RulesDetector"


# ---------------------------------------------------------------------------
# BUG-1 tests: event capture via InMemoryLogWriter + tool_call extraction
# ---------------------------------------------------------------------------

class _LogWriterAgent:
    """Fake agent that writes events into its log_writer (simulating ProtectedAgent)."""

    def __init__(self, log_writer: InMemoryLogWriter) -> None:
        self.log_writer = log_writer

    def run(self, _user_input: str) -> str:
        # Simulate model_call event (always emitted).
        self.log_writer.write(make_event(
            agent_id="test-agent",
            session_id="sess-1",
            step=0,
            event_type="model_call",
            model="claude-test",
        ))
        # Simulate a tool_call event.
        self.log_writer.write(make_event(
            agent_id="test-agent",
            session_id="sess-1",
            step=0,
            event_type="tool_call",
            tool_name="web_fetch",
            tool_args_redacted={"url": "https://example.com"},
        ))
        # Simulate final_response.
        self.log_writer.write(make_event(
            agent_id="test-agent",
            session_id="sess-1",
            step=0,
            event_type="final_response",
        ))
        return "fetched content"


def test_run_challenge_events_non_empty_with_log_writer():
    """events list must be non-empty when a log writer captured events."""
    c = get_challenge("direct-injection", 0)
    writer = InMemoryLogWriter()
    agent = _LogWriterAgent(writer)
    result = run_challenge_with_agent(c, agent, payload="hi", log_writer=writer)
    assert len(result["events"]) >= 1, "expected at least one captured event"
    assert any(
        ev.get("event_type") == "model_call" for ev in result["events"]
    ), "expected a model_call event"


def test_run_challenge_tool_calls_derived_from_log_writer_events():
    """tool_calls must reflect tool_call events from the log writer."""
    c = get_challenge("direct-injection", 0)
    writer = InMemoryLogWriter()
    agent = _LogWriterAgent(writer)
    result = run_challenge_with_agent(c, agent, payload="hi", log_writer=writer)
    assert len(result["tool_calls"]) == 1, "expected exactly one tool call"
    tc = result["tool_calls"][0]
    assert tc["name"] == "web_fetch"
    assert tc["input"] == {"url": "https://example.com"}
