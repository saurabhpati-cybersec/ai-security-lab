"""Pydantic models for the Adversary Range."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


_VALID_CRITERIA_PREFIXES = (
    "benign",
    "response_contains_no_secrets",
    "regex:",
    "agent_called_tool:",
    "not_agent_called_tool:",
    "and:",
    "or:",
)

_VALID_CATEGORIES = (
    "direct-injection",
    "indirect-injection",
    "tool-abuse",
    "rag-poison",
    "exfiltration",
)


class Challenge(BaseModel):
    """One Adversary Range challenge — content + grader + preset shape."""

    model_config = ConfigDict(frozen=False, validate_assignment=True)

    id: str
    category: Literal["direct-injection", "indirect-injection", "tool-abuse", "rag-poison", "exfiltration"]
    level: int = Field(ge=0, le=3)
    title: str
    scenario: str
    flag: str
    example_payload: str | None = None
    hints: list[str] = Field(min_length=3, max_length=3)
    grader_goal: str
    preset_base_level: int = Field(ge=0, le=3)
    preset_overrides: DefensePreset | None = None
    diff_from_prev: str = ""
    fix_reveal: str | None = None

    @field_validator("grader_goal")
    @classmethod
    def _grader_goal_known_prefix(cls, v: str) -> str:
        if not any(v == p or v.startswith(p) for p in _VALID_CRITERIA_PREFIXES):
            raise ValueError(
                f"grader_goal {v!r} must start with one of {_VALID_CRITERIA_PREFIXES}"
            )
        return v

    @model_validator(mode="after")
    def _id_matches_category_level(self) -> "Challenge":
        expected = f"{self.category}/L{self.level}"
        if self.id != expected:
            raise ValueError(f"id {self.id!r} must equal {expected!r}")
        return self

    @model_validator(mode="after")
    def _fix_reveal_iff_L3(self) -> "Challenge":
        if self.level == 3 and self.fix_reveal is None:
            raise ValueError("level 3 challenges must define fix_reveal")
        if self.level != 3 and self.fix_reveal is not None:
            raise ValueError("only level 3 challenges may define fix_reveal")
        return self
