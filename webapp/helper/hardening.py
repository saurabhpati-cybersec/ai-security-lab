"""Run the lab's own RulesDetector over the user's selection.

If a rule trips, the caller wraps the selection in [UNTRUSTED]...[/UNTRUSTED]
and forces the answer to lead with a warning — turning the helper itself into
a live demo of input-side defense (the same pattern shipped on the protected
agent: detectors/rules.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from detectors.rules import RulesDetector

# Match the project default: confidence >= 0.6 blocks/tags.
_DETECTOR = RulesDetector(threshold=0.6)


@dataclass(frozen=True)
class HardeningResult:
    triggered: bool
    rule_name: str | None
    confidence: float


def check_selection(selection: str | None) -> HardeningResult:
    if not selection or not selection.strip():
        return HardeningResult(triggered=False, rule_name=None, confidence=0.0)
    result = _DETECTOR.check(selection)
    if result.is_injection:
        rule = result.matched_rules[0] if result.matched_rules else "unknown"
        return HardeningResult(
            triggered=True, rule_name=rule, confidence=result.confidence
        )
    return HardeningResult(
        triggered=False, rule_name=None, confidence=result.confidence
    )
