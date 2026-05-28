"""Load challenge YAMLs from range/challenges/ into Challenge objects."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from range.schema import Challenge

_CHALLENGES_DIR = Path(__file__).parent / "challenges"

_CATEGORY_NAMES = {
    "direct-injection": "Direct Injection",
    "indirect-injection": "Indirect Injection",
    "tool-abuse": "Tool Abuse",
    "rag-poison": "RAG Poisoning",
    "exfiltration": "Data Exfiltration",
}


@dataclass(frozen=True)
class CategorySummary:
    id: str
    name: str
    level_count: int = 4


@dataclass(frozen=True)
class LevelSummary:
    level: int
    title: str


def list_categories() -> list[CategorySummary]:
    """Return the 5 known categories regardless of which YAMLs are on disk."""
    return [CategorySummary(id=k, name=v) for k, v in _CATEGORY_NAMES.items()]


def list_levels(category: str) -> list[LevelSummary]:
    """Return the level summaries that exist on disk for *category*."""
    if category not in _CATEGORY_NAMES:
        raise KeyError(f"Unknown category {category!r}")
    out: list[LevelSummary] = []
    for level in range(4):
        try:
            c = get_challenge(category, level)
        except KeyError:
            continue
        out.append(LevelSummary(level=level, title=c.title))
    return out


@lru_cache(maxsize=64)
def get_challenge(category: str, level: int) -> Challenge:
    if category not in _CATEGORY_NAMES:
        raise KeyError(f"Unknown category {category!r}")
    if level not in (0, 1, 2, 3):
        raise KeyError(f"Unknown level {level!r}")
    path = _CHALLENGES_DIR / category / f"L{level}.yaml"
    if not path.exists():
        raise KeyError(f"No challenge file at {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return Challenge(**data)


def load_all() -> list[Challenge]:
    """Eagerly load every YAML on disk. Used by smoke tests."""
    out: list[Challenge] = []
    for category in _CATEGORY_NAMES:
        for level in range(4):
            try:
                out.append(get_challenge(category, level))
            except KeyError:
                continue
    return out


def reload_cache() -> None:
    """Drop the lru_cache (used by tests that mutate files on disk)."""
    get_challenge.cache_clear()
