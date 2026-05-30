"""Verify ProtectedAgent honors a DefensePreset."""
from __future__ import annotations

import pytest

from agents.protected.agent import ProtectedAgent
from agents.protected.presets import PRESET_L0, PRESET_L1, PRESET_L2, PRESET_L3


def test_default_preset_is_None_keeps_legacy_behavior():
    # No preset → existing default ⇒ all layers active.
    agent = ProtectedAgent()
    assert agent._preset is None or agent._preset.rules_input  # legacy default has rules on


def test_L0_preset_skips_input_check():
    """L0 has rules_input=False; input that would trip legacy default must pass through."""
    agent = ProtectedAgent(preset=PRESET_L0)
    assert agent._preset.rules_input is False
    # We test only the gating decision here, not the LLM call:
    assert agent._should_run_input_check() is False


def test_L1_preset_enables_input_check_only():
    agent = ProtectedAgent(preset=PRESET_L1)
    assert agent._should_run_input_check() is True
    assert agent._should_check_tool_result() is False
    assert agent._should_use_gateway() is False
    assert agent._should_filter_output() is False


def test_L2_preset_enables_input_tool_result_and_gateway():
    agent = ProtectedAgent(preset=PRESET_L2)
    assert agent._should_run_input_check() is True
    assert agent._should_check_tool_result() is True
    assert agent._should_use_gateway() is True
    assert agent._should_filter_output() is False


def test_L3_preset_enables_all_non_classifier_layers():
    agent = ProtectedAgent(preset=PRESET_L3)
    assert agent._should_run_input_check() is True
    assert agent._should_check_tool_result() is True
    assert agent._should_use_gateway() is True
    assert agent._should_filter_output() is True
