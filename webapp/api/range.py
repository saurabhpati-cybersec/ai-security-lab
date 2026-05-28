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


import re as _re

_CATEGORY_TO_NAME = {c.id: c.name for c in list_categories()}
_LEVEL_PATTERN = _re.compile(r"^L([0-3])$")


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


@router.get("/{category}/{level_str}")
async def get_challenge_endpoint(category: str, level_str: str, reveal: int = 0) -> dict:
    """Return one challenge.

    ``reveal`` is required to include ``fix_reveal`` in the payload (so the L3
    canonical fix isn't trivially visible in the browser's dev-tools network
    log before the user explicitly opens the tab).
    """
    m = _LEVEL_PATTERN.match(level_str)
    if m is None:
        raise HTTPException(status_code=404, detail=f"Unknown level {level_str!r}")
    level = int(m.group(1))
    try:
        c = get_challenge(category, level)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    payload = c.model_dump(mode="json")
    if not reveal:
        payload["fix_reveal"] = None
    return payload


from pydantic import BaseModel

from agents.protected.agent import ProtectedAgent  # noqa: E402
from range.runner import (  # noqa: E402
    build_preset_for_challenge,
    run_challenge_with_agent,
)


class _RunBody(BaseModel):
    challenge_id: str
    payload: str
    switchboard: dict | None = None  # optional layer-state override


@router.post("/run")
async def run_challenge_endpoint(body: _RunBody) -> dict:
    # Parse "category/L{n}" from challenge_id.
    if "/" not in body.challenge_id:
        raise HTTPException(status_code=404, detail="Malformed challenge_id")
    category, level_str = body.challenge_id.split("/", 1)
    m = _LEVEL_PATTERN.match(level_str)
    if m is None:
        raise HTTPException(status_code=404, detail="Malformed challenge_id")
    level = int(m.group(1))
    try:
        c = get_challenge(category, level)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    preset = build_preset_for_challenge(c)
    if body.switchboard:
        # Merge switchboard overrides field-by-field onto the resolved preset.
        # Unknown keys will raise ValidationError (caught as 422 by FastAPI).
        from range.schema import DefensePreset
        preset = DefensePreset(**{**preset.model_dump(), **body.switchboard})

    from starter.python.log_schema import InMemoryLogWriter
    writer = InMemoryLogWriter()
    agent = ProtectedAgent(preset=preset, log_writer=writer)
    result = run_challenge_with_agent(c, agent, payload=body.payload, log_writer=writer)
    return result
