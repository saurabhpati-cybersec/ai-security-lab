"""Tests for the /api/helper/ask SSE endpoint and /api/helper/health."""

from __future__ import annotations

import os
from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from webapp.api import helper as helper_api
from webapp.helper.corpus import Chunk
from webapp.helper.retriever import BM25Retriever


@pytest.fixture
def app_with_helper():
    app = FastAPI()
    chunks = [
        Chunk("docs/threat-model.md", "STRIDE", "stride",
              "## STRIDE\nThe lab uses STRIDE to enumerate threats against agents."),
        Chunk("docs/glossary.md", "ASR", "asr",
              "## ASR\nAttack success rate, computed as failed cases over total."),
        Chunk("docs/agents.md", "Agents", "agents",
              "## Agents\nThe reference agent has three tools and a system prompt."),
        Chunk("docs/tools.md", "Tools", "tools",
              "## Tools\nweb_fetch, read_doc, and send_message form the tool surface."),
        Chunk("docs/eval.md", "Evals", "evals",
              "## Evals\nThe harness loads JSONL datasets and reports pass rates."),
        Chunk("docs/calibration.md", "Calibration", "calibration",
              "## Calibration\nMove the threshold slider and watch TPR/FPR move."),
    ]
    helper_api.init_retriever(BM25Retriever(chunks))
    app.include_router(helper_api.router, prefix="/api")
    return app


def _events_from_sse(body: str) -> list[tuple[str, str]]:
    """Parse text/event-stream body into a list of (event, data) tuples."""
    out: list[tuple[str, str]] = []
    event = None
    data_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("event:"):
            event = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data_lines.append(line[len("data:"):].strip())
        elif line == "":
            if event is not None:
                out.append((event, "\n".join(data_lines)))
            event = None
            data_lines = []
    return out


def test_health_returns_chunk_count_and_paths(app_with_helper):
    client = TestClient(app_with_helper)
    r = client.get("/api/helper/health")
    assert r.status_code == 200
    body = r.json()
    assert body["chunk_count"] == 6
    assert "docs/threat-model.md" in body["indexed_paths"]
    assert "has_anthropic" in body and "has_openai" in body


def test_ask_emits_citations_then_tokens_then_done(monkeypatch, app_with_helper):
    """With a key set and a mocked synthesizer, the stream must emit
    citations → token(s) → done in that order, and each citation must include
    a `url` field (None when the path has no rendered route)."""
    import json

    async def fake_stream(system, messages) -> AsyncIterator[str]:
        yield "Hello "
        yield "world."

    monkeypatch.setattr(helper_api, "stream_synthesis", fake_stream)
    monkeypatch.setattr(helper_api, "has_any_key", lambda: True)

    client = TestClient(app_with_helper)
    r = client.post(
        "/api/helper/ask",
        json={"question": "what is STRIDE?", "selection": None, "history": []},
    )
    assert r.status_code == 200
    events = _events_from_sse(r.text)
    names = [e for e, _ in events]
    assert names[0] == "citations"
    assert "token" in names
    assert names[-1] == "done"

    # Verify the citations payload shape, including url mapping for docs/*.
    citations_data = json.loads([d for e, d in events if e == "citations"][0])
    cites = citations_data["citations"]
    assert cites, "expected at least one citation"
    for c in cites:
        assert {"n", "path", "anchor", "heading", "url"} <= set(c.keys())
    docs_cites = [c for c in cites if c["path"].startswith("docs/")]
    assert docs_cites, "fixture has docs/* paths so at least one citation should be docs"
    for c in docs_cites:
        assert c["url"] and c["url"].startswith("/docs/")


def test_ask_no_key_mode_includes_snippet_text(monkeypatch, app_with_helper):
    monkeypatch.setattr(helper_api, "has_any_key", lambda: False)

    client = TestClient(app_with_helper)
    r = client.post(
        "/api/helper/ask",
        json={"question": "what is STRIDE?", "selection": None, "history": []},
    )
    assert r.status_code == 200
    events = _events_from_sse(r.text)
    names = [e for e, _ in events]
    assert "citations" in names
    # Search-only mode: a token event carrying the snippet text.
    token_payloads = [d for e, d in events if e == "token"]
    assert token_payloads, "expected at least one token event"
    joined = " ".join(token_payloads)
    assert "STRIDE" in joined or "threat-model" in joined
    assert names[-1] == "done"


def test_ask_returns_error_event_when_uninitialized(monkeypatch):
    """If init_retriever was never called, the route emits an error event."""
    helper_api.init_retriever(None)  # type: ignore[arg-type]
    app = FastAPI()
    app.include_router(helper_api.router, prefix="/api")
    client = TestClient(app)
    r = client.post(
        "/api/helper/ask",
        json={"question": "hi", "history": []},
    )
    assert r.status_code == 200
    events = _events_from_sse(r.text)
    assert any(e == "error" for e, _ in events)
