#!/usr/bin/env python3
"""Input/output validation defense layer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from detectors.output_filter import OutputFilter
from detectors.rules import RulesDetector


class ValidationLayer:
    """Wraps an agent with input validation and output filtering."""

    def __init__(self, agent, threshold: float = 0.5) -> None:
        self._agent = agent
        self._detector = RulesDetector(threshold=threshold)
        self._filter = OutputFilter()

    def run(self, user_input: str) -> dict:
        """Run agent with I/O validation. Returns dict with response, violations, blocked."""
        # Input validation
        input_check = self._detector.check(user_input)
        if input_check.is_injection:
            return {
                "response": "Request blocked: potential injection detected.",
                "blocked": True,
                "input_violations": input_check.matched_rules,
                "output_violations": [],
            }

        # Run agent
        response = self._agent.run(user_input)

        # Output filtering
        filter_result = self._filter.filter(response)

        return {
            "response": filter_result.filtered_text,
            "blocked": False,
            "input_violations": [],
            "output_violations": filter_result.violations,
        }
