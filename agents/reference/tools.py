"""Concrete tool implementations for the reference agent."""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from agents.reference.agent import ToolCall, ToolResult

CORPUS_DIR = Path(__file__).parent / "corpus"
OUTBOX_PATH = Path(__file__).parent / "outbox.jsonl"
MAX_FETCH_BYTES = 8192


def web_fetch(url: str) -> ToolResult:
    """GET a URL, return up to MAX_FETCH_BYTES of text."""
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            text = response.text[:MAX_FETCH_BYTES]
            return ToolResult(tool_name="web_fetch", content=text)
    except httpx.HTTPStatusError as e:
        return ToolResult(
            tool_name="web_fetch",
            content="",
            error=f"HTTP {e.response.status_code}: {e}",
        )
    except httpx.RequestError as e:
        return ToolResult(tool_name="web_fetch", content="", error=f"Request failed: {e}")


def read_doc(name: str) -> ToolResult:
    """Read a corpus document by filename."""
    # Prevent path traversal
    safe_name = Path(name).name
    doc_path = CORPUS_DIR / safe_name
    if not doc_path.exists():
        return ToolResult(
            tool_name="read_doc", content="", error=f"Document not found: {safe_name}"
        )
    try:
        content = doc_path.read_text(encoding="utf-8")
        return ToolResult(tool_name="read_doc", content=content)
    except OSError as e:
        return ToolResult(tool_name="read_doc", content="", error=f"Read error: {e}")


def send_message(recipient: str, body: str) -> ToolResult:
    """Append a message to outbox.jsonl."""
    import datetime

    record = {
        "ts": datetime.datetime.now(tz=datetime.UTC).isoformat(),
        "recipient": recipient,
        "body": body,
    }
    try:
        with OUTBOX_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return ToolResult(
            tool_name="send_message",
            content=json.dumps({"status": "sent", "recipient": recipient}),
        )
    except OSError as e:
        return ToolResult(tool_name="send_message", content="", error=f"Write error: {e}")


def dispatch_tool(tool_call: ToolCall) -> ToolResult:
    """Route a ToolCall to the appropriate implementation."""
    match tool_call.name:
        case "web_fetch":
            return web_fetch(tool_call.args["url"])
        case "read_doc":
            return read_doc(tool_call.args["name"])
        case "send_message":
            return send_message(tool_call.args["recipient"], tool_call.args["body"])
        case _:
            return ToolResult(
                tool_name=tool_call.name,
                content="",
                error=f"Unknown tool: {tool_call.name}",
            )
