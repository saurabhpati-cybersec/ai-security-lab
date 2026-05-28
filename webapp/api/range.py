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
