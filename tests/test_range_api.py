"""Tests for the Adversary Range FastAPI endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _client() -> TestClient:
    from webapp.server import app
    return TestClient(app)


def test_get_categories_returns_five():
    r = _client().get("/api/range/categories")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 5
    ids = sorted(c["id"] for c in body)
    assert ids == [
        "direct-injection", "exfiltration", "indirect-injection",
        "rag-poison", "tool-abuse",
    ]
    for c in body:
        assert "name" in c
        assert c["level_count"] == 4


def test_get_category_returns_levels():
    r = _client().get("/api/range/direct-injection")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "direct-injection"
    assert "name" in body
    # Only L0 exists at this point in the implementation;
    # remaining levels appear after Task 21.
    levels = body["levels"]
    assert any(l["level"] == 0 and l["title"] for l in levels)


def test_get_category_unknown_returns_404():
    r = _client().get("/api/range/not-a-category")
    assert r.status_code == 404
