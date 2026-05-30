"""Tests for range.loader."""
from __future__ import annotations

from pathlib import Path

import pytest

from range.loader import get_challenge, list_categories, list_levels, load_all


def test_list_categories_returns_five():
    cats = list_categories()
    assert sorted(c.id for c in cats) == [
        "direct-injection", "exfiltration", "indirect-injection",
        "rag-poison", "tool-abuse",
    ]


def test_each_category_has_four_levels():
    for cat in list_categories():
        levels = list_levels(cat.id)
        assert sorted(l.level for l in levels) == [0, 1, 2, 3]


def test_get_challenge_returns_valid_challenge():
    c = get_challenge("direct-injection", 0)
    assert c.id == "direct-injection/L0"
    assert c.level == 0


def test_get_challenge_unknown_category_raises():
    with pytest.raises(KeyError):
        get_challenge("not-a-category", 0)


def test_get_challenge_unknown_level_raises():
    with pytest.raises(KeyError):
        get_challenge("direct-injection", 7)


def test_load_all_returns_twenty_challenges():
    all_challenges = load_all()
    assert len(all_challenges) == 20
    ids = {c.id for c in all_challenges}
    assert len(ids) == 20  # all unique
