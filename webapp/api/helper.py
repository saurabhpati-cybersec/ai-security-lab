"""API: on-screen helper. Grounded Q&A over docs/labs with citations.

Streams Server-Sent Events:
    event: citations  — fired once, payload {citations: [{n, path, anchor, heading, url}]}
    event: token      — fired repeatedly, payload {delta: str}
    event: done       — fired once at end-of-stream, payload {}
    event: error      — fired and stream closed on failure, payload {message}
"""

from __future__ import annotations

import json
import os
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from webapp.helper.answerer import build_prompt, has_any_key, stream_synthesis
from webapp.helper.hardening import check_selection
from webapp.helper.retriever import BM25Retriever

router = APIRouter(tags=["helper"])


# ── Index state (populated by server startup) ─────────────────────────────

_retriever: BM25Retriever | None = None


def init_retriever(retriever: BM25Retriever | None) -> None:
    """Called from webapp/server.py on startup."""
    global _retriever
    _retriever = retriever


# ── Request schema ────────────────────────────────────────────────────────


class HelperHistoryMessage(BaseModel):
    role: str
    content: str


class HelperAskRequest(BaseModel):
    question: str
    selection: str | None = None
    page: str | None = None
    history: list[HelperHistoryMessage] = []


# ── SSE helpers ───────────────────────────────────────────────────────────


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _citation_url(path: str, anchor: str) -> str | None:
    """Map a corpus path to an in-app URL the user can click on.

    Only docs/*.md has a rendered route today (`/docs/{slug}`). Labs, README,
    GETTING_STARTED return None — the frontend renders those as non-clickable
    chips with a tooltip showing the path.
    """
    if path.startswith("docs/") and path.endswith(".md"):
        slug = path[len("docs/"):-len(".md")]
        return f"/docs/{slug}" + (f"#{anchor}" if anchor else "")
    return None


# ── Routes ────────────────────────────────────────────────────────────────


@router.get("/helper/health")
async def helper_health() -> dict:
    chunks = _retriever.chunks if _retriever is not None else []
    paths = sorted({c.path for c in chunks})
    return {
        "chunk_count": len(chunks),
        "indexed_paths": paths,
        "has_anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "has_openai": bool(os.environ.get("OPENAI_API_KEY")),
    }


@router.post("/helper/ask")
async def helper_ask(req: HelperAskRequest) -> StreamingResponse:
    async def gen() -> AsyncIterator[str]:
        if _retriever is None:
            yield _sse(
                "error",
                {"message": "helper retriever not initialized — server startup failed"},
            )
            return

        # 1. Retrieve
        query_text = (req.question + " " + (req.selection or "")).strip()
        ranked = _retriever.top_k(query_text, k=5, floor=0.0)
        chunks = [c for c, _ in ranked]

        # 2. Citations event (always — even if empty)
        citations_payload = [
            {
                "n": i + 1,
                "path": c.path,
                "anchor": c.anchor,
                "heading": c.heading,
                "url": _citation_url(c.path, c.anchor),
            }
            for i, c in enumerate(chunks)
        ]
        yield _sse("citations", {"citations": citations_payload})

        # 3. No-key fallback — emit search-only snippets, no LLM call.
        if not has_any_key():
            if not chunks:
                yield _sse(
                    "token",
                    {
                        "delta": "No API key set, and no relevant snippets found. "
                        "Open Settings to add a key, or try a more specific question."
                    },
                )
            else:
                preface = (
                    "**Search-only mode — no API key set.** "
                    "Open Settings to enable synthesized answers.\n\n"
                )
                yield _sse("token", {"delta": preface})
                for i, c in enumerate(chunks, start=1):
                    body = c.content[:500] + ("…" if len(c.content) > 500 else "")
                    snippet = (
                        f"### [{i}] {c.heading or c.path}\n"
                        f"`{c.path}`\n\n{body}\n\n"
                    )
                    yield _sse("token", {"delta": snippet})
            yield _sse("done", {})
            return

        # 4. Hardening + prompt build + synthesize
        hardening = check_selection(req.selection)
        history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
        system, messages = build_prompt(
            question=req.question,
            selection=req.selection,
            chunks=chunks,
            history=history_dicts,
            hardening=hardening,
        )
        try:
            async for delta in stream_synthesis(system, messages):
                yield _sse("token", {"delta": delta})
            yield _sse("done", {})
        except Exception as exc:  # noqa: BLE001
            yield _sse(
                "error",
                {"message": f"{type(exc).__name__}: {exc}"[:300]},
            )

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
