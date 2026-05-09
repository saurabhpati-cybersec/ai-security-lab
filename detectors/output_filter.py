"""Output filter: strip exfiltration vectors from agent responses.

Handles:
- Markdown image URLs pointing to non-allowlisted domains
- Hyperlinks to non-allowlisted domains
- Known secret patterns (fake credentials from corpus)
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class FilterResult:
    filtered_text: str
    violations: list[str]
    was_modified: bool


# Patterns for fake secrets in the corpus (for lab purposes — real secrets need vault integration)
SECRET_PATTERNS = [
    r"AKIAIOSFODNN7EXAMPLE",
    r"xoxb-\d+-\d+-[A-Za-z0-9]+",
    r"db-dev-password-example-not-real",
]

# Allowlisted domains (no exfil to these)
DEFAULT_ALLOWLIST = {
    "anthropic.com",
    "openai.com",
    "python.org",
    "github.com",
    "docs.python.org",
    "company.example.com",
}


class OutputFilter:
    """Filters agent output to prevent exfiltration via markdown/links."""

    def __init__(self, domain_allowlist: set[str] | None = None) -> None:
        self._allowlist = domain_allowlist or DEFAULT_ALLOWLIST
        self._image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
        self._link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self._url_pattern = re.compile(r"https?://([^/\s?#]+)")
        self._secret_patterns = [re.compile(p) for p in SECRET_PATTERNS]

    def _is_allowed_url(self, url: str) -> bool:
        match = self._url_pattern.search(url)
        if not match:
            return True  # not a URL, allow
        domain = match.group(1).lower()
        return any(
            domain == allowed or domain.endswith("." + allowed) for allowed in self._allowlist
        )

    def filter(self, text: str) -> FilterResult:
        """Apply all filters to output text. Returns filtered text and list of violations."""
        violations: list[str] = []
        result = text

        # Strip markdown images with non-allowlisted URLs
        def replace_image(m: re.Match) -> str:
            alt, url = m.group(1), m.group(2)
            if not self._is_allowed_url(url):
                violations.append(f"blocked_image_url:{url[:80]}")
                return f"[image blocked: {alt}]"
            return m.group(0)

        result = self._image_pattern.sub(replace_image, result)

        # Strip hyperlinks with non-allowlisted URLs
        def replace_link(m: re.Match) -> str:
            label, url = m.group(1), m.group(2)
            if not self._is_allowed_url(url):
                violations.append(f"blocked_link_url:{url[:80]}")
                return f"[link blocked: {label}]"
            return m.group(0)

        result = self._link_pattern.sub(replace_link, result)

        # Redact known secret patterns
        for pattern in self._secret_patterns:
            if pattern.search(result):
                violations.append(f"secret_redacted:{pattern.pattern[:30]}")
                result = pattern.sub("[REDACTED]", result)

        return FilterResult(
            filtered_text=result,
            violations=violations,
            was_modified=result != text,
        )

    def check_only(self, text: str) -> list[str]:
        """Return list of violations without modifying text."""
        return self.filter(text).violations
