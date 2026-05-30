"""Grader: thin wrapper around evals/harness/runner.evaluate_criteria.

Reuses the same string-form criteria DSL the eval datasets use so the
Range cannot drift from the eval runner.
"""
from __future__ import annotations

from typing import Any

from evals.harness.runner import evaluate_criteria


def grade(
    criteria: str,
    *,
    response: str,
    tool_calls: list[dict[str, Any]],
    events: list[dict[str, Any]],  # accepted for future graders; currently unused
) -> bool:
    """Return True iff the criteria are satisfied. events accepted for future use."""
    return evaluate_criteria(criteria, response, tool_calls)


def summarize_blockage(events: list[dict[str, Any]]) -> tuple[bool, str | None]:
    """Inspect events to determine whether (and where) the run was blocked.

    Returns (blocked, fired_layer). fired_layer is one of:
      "RulesDetector"  — input-side block
      "ToolGateway"    — egress / budget / allowlist block
      "ClassifierDetector" — LLM-judge block (if used)
      None             — not blocked
    """
    for ev in events:
        if ev.get("event_type") != "policy_violation":
            continue
        meta = ev.get("metadata") or {}
        # Tool-side violations carry a `policy_violation` key from the gateway.
        if "policy_violation" in meta:
            return True, "ToolGateway"
        detector = ev.get("detector_name")
        if detector:
            return True, str(detector)
        return True, "unknown"
    return False, None
