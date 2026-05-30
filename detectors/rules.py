"""Rule-based prompt injection detector using regex heuristics.

Target latency: <5ms per check on modern hardware.
"""
from __future__ import annotations

import base64
import binascii
import re
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionResult:
    is_injection: bool
    confidence: float  # 0.0-1.0
    matched_rules: list[str]
    latency_ms: float
    text_length: int


# Long-ish base64 blob — picked up before we try to decode and rescan.
_BASE64_BLOB = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")


class RulesDetector:
    """Fast regex-based injection detector.

    Tuned for low false positive rate on benign enterprise queries.
    Threshold: confidence >= 0.5 triggers a detection.
    """

    # Each rule: (name, pattern, weight)
    RULES: list[tuple[str, str, float]] = [
        # Instruction override patterns
        ("ignore_previous", r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", 0.9),
        (
            "new_instructions",
            r"(your\s+new\s+|updated\s+)(instructions?|task|goal|objective)\s*(is|are|:)",
            0.85,
        ),
        ("forget_instructions", r"forget\s+(everything|all|your|previous)", 0.8),
        (
            "disregard",
            r"disregard\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|rules?|guidelines?)",
            0.85,
        ),
        # Role hijack patterns
        ("dan_pattern", r"\b(DAN|STAN|jailbreak|do\s+anything\s+now)\b", 0.8),
        (
            "you_are_now",
            r"you\s+are\s+now\s+(a\s+)?(different|new|another|an?\s+AI|DAN|jailbroken)",
            0.75,
        ),
        (
            "act_as",
            r"(act|pretend|behave|respond)\s+as\s+(if\s+you\s+(are|were)\s+)?(a\s+)?(?!helpful|an?\s+assistant)([\w\s]{1,30})",
            0.5,
        ),
        # System prompt manipulation
        ("system_prefix", r"^(SYSTEM|ADMIN|OPERATOR|ROOT)\s*:\s*(?!prompt)", 0.7),
        (
            "reveal_system",
            r"(repeat|reveal|show|output|print|display)\s+(your\s+)?(system\s+prompt|instructions?|original\s+prompt)",
            0.85,
        ),
        (
            "override_context",
            r"(override|replace|update|modify)\s+(your\s+)?(context|system|instructions?|prompt|configuration)",
            0.8,
        ),
        # Exfiltration trigger patterns
        ("send_to_attacker", r"send\s+(it|them|the\s+\w+|all|everything)\s+to\s+\S+@\S+", 0.9),
        ("fetch_with_data", r"fetch\s+https?://\S+\?.*=", 0.75),
        (
            "markdown_image_exfil",
            r"!\[.*\]\(https?://(?!company\.example\.com)\S+\)",
            0.7,
        ),
        # Hidden instruction markers
        (
            "html_comment_injection",
            r"<!--.*?(ignore|instruction|system|override|send|fetch).*?-->",
            0.8,
        ),
        ("zero_width_injection", r"[​‌‍﻿­]", 0.4),
        ("unicode_tag_block", r"[\U000e0000-\U000e007f]+", 0.85),
        # Encoded payload indicators
        (
            "base64_instruction",
            r"[A-Za-z0-9+/]{40,}={0,2}(?=\s|$)",
            0.3,
        ),  # low weight — FP prone
    ]

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self._compiled = [
            (name, re.compile(pattern, re.IGNORECASE | re.DOTALL), weight)
            for name, pattern, weight in self.RULES
        ]

    def check(self, text: str) -> DetectionResult:
        """Check text for injection patterns. Returns DetectionResult.

        When a long base64-looking blob is found, the blob is decoded and the
        decoded text is rescanned against every rule *except* the base64
        indicator itself. If a high-weight rule fires inside the decoded
        payload, both the indicator and the decoded match are reported and
        the confidence reflects the decoded match — this is what catches
        attacks like di-010 where the real instruction is hidden in base64.
        """
        t0 = time.perf_counter()
        matched, max_confidence = self._scan(text)

        # Try base64 decode-and-rescan when the indicator fired.
        if "base64_instruction" in matched:
            for decoded in self._iter_decoded(text):
                sub_matched, sub_max = self._scan(decoded, skip={"base64_instruction"})
                for rule in sub_matched:
                    tagged = f"decoded:{rule}"
                    if tagged not in matched:
                        matched.append(tagged)
                if sub_max > max_confidence:
                    max_confidence = sub_max

        # Combine: max single-rule confidence, boosted by co-occurrence.
        confidence = max_confidence
        if len(matched) > 1:
            confidence = min(1.0, max_confidence + 0.05 * (len(matched) - 1))

        latency_ms = (time.perf_counter() - t0) * 1000
        return DetectionResult(
            is_injection=confidence >= self.threshold,
            confidence=confidence,
            matched_rules=matched,
            latency_ms=latency_ms,
            text_length=len(text),
        )

    def _scan(
        self, text: str, skip: set[str] | None = None
    ) -> tuple[list[str], float]:
        """Apply every rule (minus *skip*) to *text*; return (matches, max_weight)."""
        skip = skip or set()
        matched: list[str] = []
        max_confidence = 0.0
        for name, pattern, weight in self._compiled:
            if name in skip:
                continue
            if pattern.search(text):
                matched.append(name)
                if weight > max_confidence:
                    max_confidence = weight
        return matched, max_confidence

    @staticmethod
    def _iter_decoded(text: str) -> list[str]:
        """Return UTF-8 decodings of plausible base64 blobs found in *text*."""
        out: list[str] = []
        for match in _BASE64_BLOB.finditer(text):
            blob = match.group(0)
            # Skip unrealistically short fragments that the rule weight already
            # discounts for false positives.
            if len(blob) < 24:
                continue
            try:
                raw = base64.b64decode(blob, validate=True)
            except (binascii.Error, ValueError):
                continue
            try:
                decoded = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            out.append(decoded)
        return out

    def check_tool_result(self, tool_name: str, content: str) -> DetectionResult:
        """Check tool result content for IPI patterns (indirect injection via tool output)."""
        return self.check(content)
