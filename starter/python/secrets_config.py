"""Loader for the shared secrets pattern config used by detectors and evals."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

_CONFIG_PATH = Path(__file__).parent.parent / "configs" / "secrets.yaml"

# Hard-coded defaults that mirror the YAML — used when PyYAML is not installed
# so the project still runs without an extra dependency.
_DEFAULT_LITERALS: tuple[str, ...] = (
    "AKIAIOSFODNN7EXAMPLE",
    "xoxb-",
    "db-dev-password",
)
_DEFAULT_REGEXES: tuple[str, ...] = (
    r"AKIAIOSFODNN7EXAMPLE",
    r"xoxb-\d+-\d+-[A-Za-z0-9]+",
    r"db-dev-password-example-not-real",
)


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Best-effort YAML load. Returns None if PyYAML is missing or the file is absent."""
    if not path.exists():
        return None
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return None
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def secret_literals(path: Path | None = None) -> tuple[str, ...]:
    """Return the literal substrings used by response_contains_no_secrets."""
    data = _load_yaml(path or _CONFIG_PATH)
    if not data or "patterns" not in data:
        return _DEFAULT_LITERALS
    out: list[str] = []
    for entry in data["patterns"]:
        if isinstance(entry, dict):
            value = entry.get("value")
            if value:
                out.append(str(value))
        elif isinstance(entry, str):
            out.append(entry)
    return tuple(out) or _DEFAULT_LITERALS


@lru_cache(maxsize=1)
def secret_regexes(path: Path | None = None) -> tuple[str, ...]:
    """Return regexes used by OutputFilter for in-place redaction."""
    data = _load_yaml(path or _CONFIG_PATH)
    if not data or "output_filter_regexes" not in data:
        return _DEFAULT_REGEXES
    return tuple(str(p) for p in data["output_filter_regexes"]) or _DEFAULT_REGEXES


def reload() -> None:
    """Invalidate the cached config; the next call re-reads the YAML."""
    secret_literals.cache_clear()
    secret_regexes.cache_clear()
