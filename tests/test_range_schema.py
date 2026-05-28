"""Tests for range.schema models."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from range.schema import DefensePreset


def test_default_preset_has_all_layers_off():
    p = DefensePreset()
    assert p.rules_input is False
    assert p.rules_tool_result is False
    assert p.gateway_budgets is False
    assert p.gateway_egress_blocks is False
    assert p.output_filter is False
    assert p.classifier is False


def test_default_thresholds_match_legacy_protected_agent():
    p = DefensePreset()
    assert p.rules_input_threshold == 0.6
    assert p.rules_tool_result_threshold == 0.5


def test_default_allowlists_are_empty_and_independent():
    a = DefensePreset()
    b = DefensePreset()
    a.gateway_send_message_allowlist.append("x@y.z")
    # If the default list were shared, b would see "x@y.z" too.
    assert b.gateway_send_message_allowlist == []


def test_invalid_threshold_rejected():
    with pytest.raises(ValidationError):
        DefensePreset(rules_input_threshold=1.5)
    with pytest.raises(ValidationError):
        DefensePreset(rules_input_threshold=-0.1)
