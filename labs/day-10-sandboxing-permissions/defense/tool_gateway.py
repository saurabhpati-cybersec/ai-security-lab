#!/usr/bin/env python3
"""Tool gateway: enforces per-tool policies between agent and tool execution."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class GatewayConfig:
    web_fetch_url_allowlist: list[str] = field(default_factory=list)
    send_message_recipient_allowlist: list[str] = field(default_factory=list)
    max_web_fetch_calls: int = 5
    max_send_message_calls: int = 2
    max_read_doc_calls: int = 10
    max_total_bytes: int = 32768
    hitl_enabled: bool = False
    hitl_callback: Callable[[str, dict[str, Any]], bool] | None = None
    egress_deny_patterns: list[str] = field(default_factory=lambda: [
        r"169\.254\.", r"192\.168\.", r"10\.", r"127\.", r"localhost",
    ])


@dataclass
class GatewayResult:
    allowed: bool
    reason: str | None = None
    tool_result: str = ""
    policy_violation: str | None = None


class ToolGateway:
    """Enforces tool call policies per session."""

    def __init__(self, config: GatewayConfig | None = None) -> None:
        self.config = config or GatewayConfig()
        self._call_counts: dict[str, int] = {}
        self._total_bytes: int = 0
        self._session_id: str = ""

    def new_session(self, session_id: str) -> None:
        self._session_id = session_id
        self._call_counts = {}
        self._total_bytes = 0

    def _check_budget(self, tool_name: str) -> GatewayResult | None:
        count = self._call_counts.get(tool_name, 0)
        attr = f"max_{tool_name}_calls"
        limit = getattr(self.config, attr, 10)
        if count >= limit:
            return GatewayResult(
                allowed=False,
                policy_violation=f"budget_exceeded:{tool_name}:{count}/{limit}",
            )
        if self._total_bytes >= self.config.max_total_bytes:
            return GatewayResult(
                allowed=False,
                policy_violation=f"bytes_budget_exceeded:{self._total_bytes}",
            )
        return None

    def _check_web_fetch(self, url: str) -> GatewayResult | None:
        for pattern in self.config.egress_deny_patterns:
            if re.search(pattern, url):
                return GatewayResult(
                    allowed=False,
                    policy_violation=f"egress_denied:internal:{url[:80]}",
                )
        if self.config.web_fetch_url_allowlist:
            if not any(allowed in url for allowed in self.config.web_fetch_url_allowlist):
                return GatewayResult(
                    allowed=False,
                    policy_violation=f"egress_denied:not_allowlisted:{url[:80]}",
                )
        return None

    def _check_send_message(self, recipient: str) -> GatewayResult | None:
        if not self.config.send_message_recipient_allowlist:
            return None
        allowlist = self.config.send_message_recipient_allowlist
        if "*" in allowlist:
            return None
        if not any(allowed in recipient for allowed in allowlist):
            return GatewayResult(
                allowed=False,
                policy_violation=f"recipient_denied:{recipient}",
            )
        return None

    def execute(
        self, tool_name: str, args: dict[str, Any], tool_fn: Callable[..., Any]
    ) -> GatewayResult:
        budget = self._check_budget(tool_name)
        if budget:
            return budget

        if tool_name == "web_fetch":
            url_check = self._check_web_fetch(args.get("url", ""))
            if url_check:
                return url_check

        if tool_name == "send_message":
            recip_check = self._check_send_message(args.get("recipient", ""))
            if recip_check:
                return recip_check

        if self.config.hitl_enabled and tool_name == "send_message":
            if self.config.hitl_callback:
                if not self.config.hitl_callback(tool_name, args):
                    return GatewayResult(
                        allowed=False,
                        policy_violation=f"hitl_denied:{tool_name}",
                    )
            else:
                return GatewayResult(
                    allowed=False,
                    policy_violation=f"hitl_no_callback:{tool_name}",
                )

        result = tool_fn(**args)
        result_str = getattr(result, "content", str(result))

        self._call_counts[tool_name] = self._call_counts.get(tool_name, 0) + 1
        self._total_bytes += len(str(result_str).encode())

        return GatewayResult(allowed=True, tool_result=str(result_str))
