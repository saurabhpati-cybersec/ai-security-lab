"""Canonical defense presets for the Adversary Range levels L0..L3."""
from __future__ import annotations

from range.schema import DefensePreset

PRESET_L0 = DefensePreset()  # all off — equivalent to VulnerableAgent

PRESET_L1 = DefensePreset(rules_input=True)

PRESET_L2 = DefensePreset(
    rules_input=True,
    rules_tool_result=True,
    gateway_budgets=True,
    gateway_egress_blocks=True,
)

PRESET_L3 = DefensePreset(
    rules_input=True,
    rules_tool_result=True,
    gateway_budgets=True,
    gateway_egress_blocks=True,
    output_filter=True,
)

PRESETS_BY_LEVEL: dict[int, DefensePreset] = {
    0: PRESET_L0,
    1: PRESET_L1,
    2: PRESET_L2,
    3: PRESET_L3,
}
