"""Pydantic models for the Adversary Range."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DefensePreset(BaseModel):
    """Toggleable defense layers for ProtectedAgent.

    Default (all flags False) is equivalent to today's VulnerableAgent.
    PRESET_L0..PRESET_L3 (see agents/protected/presets.py) instantiate
    canonical level shapes.
    """

    model_config = ConfigDict(frozen=False, validate_assignment=True)

    rules_input: bool = False
    rules_input_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    rules_tool_result: bool = False
    rules_tool_result_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    gateway_budgets: bool = False
    gateway_egress_blocks: bool = False
    gateway_send_message_allowlist: list[str] = Field(default_factory=list)

    output_filter: bool = False
    output_filter_domain_allowlist: list[str] = Field(default_factory=list)

    classifier: bool = False
