"""Tests for agents.protected.presets."""
from __future__ import annotations

from agents.protected.presets import PRESET_L0, PRESET_L1, PRESET_L2, PRESET_L3, PRESETS_BY_LEVEL


def test_L0_is_all_off():
    p = PRESET_L0
    assert not p.rules_input
    assert not p.rules_tool_result
    assert not p.gateway_budgets
    assert not p.gateway_egress_blocks
    assert not p.output_filter
    assert not p.classifier


def test_L1_only_rules_input():
    p = PRESET_L1
    assert p.rules_input is True
    assert p.rules_tool_result is False
    assert p.gateway_budgets is False
    assert p.gateway_egress_blocks is False
    assert p.output_filter is False


def test_L2_adds_gateway_and_tool_result_check():
    p = PRESET_L2
    assert p.rules_input is True
    assert p.rules_tool_result is True
    assert p.gateway_budgets is True
    assert p.gateway_egress_blocks is True
    assert p.output_filter is False


def test_L3_adds_output_filter():
    p = PRESET_L3
    assert p.rules_input is True
    assert p.rules_tool_result is True
    assert p.gateway_budgets is True
    assert p.gateway_egress_blocks is True
    assert p.output_filter is True
    # Classifier remains opt-in per challenge.
    assert p.classifier is False


def test_presets_by_level_indexable():
    assert PRESETS_BY_LEVEL[0] is PRESET_L0
    assert PRESETS_BY_LEVEL[1] is PRESET_L1
    assert PRESETS_BY_LEVEL[2] is PRESET_L2
    assert PRESETS_BY_LEVEL[3] is PRESET_L3
