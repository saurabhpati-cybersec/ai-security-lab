"""FastAPI endpoints for the Adversary Range."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from range.loader import get_challenge, list_categories, list_levels

router = APIRouter(prefix="/range", tags=["range"])


@router.get("/categories")
async def get_categories() -> list[dict]:
    """Return the 5 known categories (content-only — no progress state)."""
    return [
        {"id": c.id, "name": c.name, "level_count": c.level_count}
        for c in list_categories()
    ]


_CATEGORY_TO_NAME = {c.id: c.name for c in list_categories()}


@router.get("/{category}")
async def get_category(category: str) -> dict:
    if category not in _CATEGORY_TO_NAME:
        raise HTTPException(status_code=404, detail=f"Unknown category {category!r}")
    levels = list_levels(category)
    return {
        "id": category,
        "name": _CATEGORY_TO_NAME[category],
        "levels": [{"level": l.level, "title": l.title} for l in levels],
    }
