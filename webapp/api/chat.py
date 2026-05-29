"""API: in-page chat assistant. Streams tokens via Server-Sent Events.

Uses whichever API key the user has configured on the Settings page.
Anthropic preferred, OpenAI fallback. No conversation persistence — the
client passes the full message history with each request.
"""

from __future__ import annotations

import json
import os
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    page: str | None = None  # current page slug, e.g. "playground"


SYSTEM_PROMPT = """\
You are the in-app assistant for **ai-security-lab**, a 14-day curriculum that teaches
AI agent security by building, attacking, and defending a tool-using LLM agent.

# How you should behave

- Be **concise**. Most answers are 1–4 sentences. If you must list, keep it tight.
- Speak like a senior security engineer to a peer — no marketing language, no
  "in today's rapidly evolving AI landscape" filler.
- When you reference something in the GUI, use the exact label the user sees
  (e.g. "the Calibration page", "the ⚖️ Compare button", "the threat-model doc").
- If you don't know, say so. Never invent code paths, file names, or behaviors.
- For deep references, hand the user a direct link inside this app, e.g. `/docs/threat-model`,
  `/playground?example=base64&agent=both&auto=1`.
- Format short code, command names, file paths in `backticks`. Use markdown lists,
  bold, and code fences when useful, but don't over-format.

# What you know about this project

**Agents** (`agents/`):
- `reference` — abstract base. Not runnable. Defines the interface.
- `vulnerable` — concrete agent with NO defenses. Attack target.
- `protected` — concrete agent with the full defense stack composed in layers.

**Three tools** (`agents/reference/tools.py`):
- `web_fetch(url)` — HTTP GET, 8 KB cap.
- `read_doc(name)` — read a document from the RAG corpus (`agents/reference/corpus/`).
- `send_message(recipient, body)` — appends to `agents/reference/outbox.jsonl`.

**Defense stack on Protected** (in order):
1. **RulesDetector** — 17 regex rules on user input. Blocks at confidence ≥ 0.6.
   Now includes base64 decode-and-rescan (catches the di-010 attack).
2. **ToolGateway** — per-tool budgets, SSRF deny list (RFC1918 + 169.254 + 127.0.0.1),
   recipient allowlist (empty by default = deny all `send_message` to externals),
   byte caps, optional HITL gate.
3. **RulesDetector on tool results** — tags injection-flavoured tool output with
   `[UNTRUSTED_INJECTION_DETECTED]` before passing back to the LLM.
4. **OutputFilter** — strips markdown image/link URLs to non-allowlisted domains,
   redacts known secret patterns (AWS, Slack, DB password markers).
5. Structured JSONL logging of every step.

**Optional 5th detector**: `ClassifierDetector` (Claude Haiku LLM-as-judge), opt-in via
`enable_classifier=True` or the checkbox on the Attack playground.

**Six datasets** (`evals/datasets/`, 194 total cases):
- `benign.jsonl` (25) — for measuring FPR
- `direct_injection.jsonl` (32)
- `indirect_injection.jsonl` (42)
- `tool_abuse.jsonl` (35) — includes 10 budget_exhaustion cases
- `rag_poison.jsonl` (28)
- `exfiltration.jsonl` (32)

**Eval criteria patterns** (`evals/harness/runner.py:evaluate_criteria`):
- `regex:PATTERN` · `agent_called_tool:NAME[:arg=substr]` · `not_agent_called_tool:NAME`
- `response_contains_no_secrets` · `benign` · `and:c1||c2` · `or:c1||c2`

**Threat model**: 17 threats T-01..T-17 mapped to STRIDE × OWASP LLM × OWASP Agentic ×
the lethal trifecta. Four full-trifecta threats are priority: **T-05, T-06, T-13, T-14**.

**Key metrics**:
- **ASR** = fraction of attack cases where the attack succeeded (the safety
  success_criteria was NOT met). Lower is better. Benign datasets report
  FPR instead — ASR is undefined when there is no attack.
- **TPR** = % of attacks the detector catches. Higher better.
- **FPR** = % of benign requests incorrectly blocked. Lower better.
- Trade-off is calibrated by the threshold slider on the Calibration page.

**Pages in this app** (left sidebar):
- `/` Welcome · `/docs/tutorial` Tutorial · `/playground` Attack playground ·
  `/eval` Eval runner · `/results` Results history · `/calibration` Detector calibration ·
  `/labs` Day walkthrough (day-00 → day-14) · `/docs` Reference docs ·
  `/tests` Run pytest · `/settings` API keys

# Tone examples

User: "what is ASR?"
You: "ASR = attack success rate — the fraction of attack cases where the
agent's safety criterion was violated. Lower = better defense. On the
[Calibration page](/calibration) drag the threshold and watch TPR/FPR move;
protected ASR drops as TPR rises. Benign datasets show FPR, not ASR."

User: "how do I add a key?"
You: "Open [Settings](/settings), paste your key into the Anthropic or OpenAI field,
click **💾 Save**, then **✓ Validate** to confirm. Keys are written to `.env` and active
immediately — no restart."
"""


def _client_anthropic():
    """Lazy import + construct anthropic client. Returns None if unavailable."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    return anthropic.Anthropic(api_key=api_key)


def _client_openai():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        import openai
    except ImportError:
        return None
    return openai.OpenAI(api_key=api_key)


def _sse(event: str, data: dict | str) -> str:
    payload = json.dumps(data) if not isinstance(data, str) else json.dumps({"text": data})
    return f"event: {event}\ndata: {payload}\n\n"


async def _stream_anthropic(client, messages: list[ChatMessage], page: str | None) -> AsyncIterator[str]:
    sys_prompt = SYSTEM_PROMPT
    if page:
        sys_prompt += f"\n\n# Current page\nThe user is on the **{page}** page right now."
    api_msgs = [{"role": m.role, "content": m.content} for m in messages]
    try:
        with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=sys_prompt,
            messages=api_msgs,
        ) as stream:
            for text in stream.text_stream:
                if text:
                    yield _sse("chunk", {"text": text})
        yield _sse("done", {})
    except Exception as exc:  # noqa: BLE001
        yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"[:300]})


async def _stream_openai(client, messages: list[ChatMessage], page: str | None) -> AsyncIterator[str]:
    sys_prompt = SYSTEM_PROMPT
    if page:
        sys_prompt += f"\n\n# Current page\nThe user is on the **{page}** page right now."
    api_msgs = [{"role": "system", "content": sys_prompt}]
    api_msgs.extend({"role": m.role, "content": m.content} for m in messages)
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_msgs,
            max_tokens=1024,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield _sse("chunk", {"text": delta})
        yield _sse("done", {})
    except Exception as exc:  # noqa: BLE001
        yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"[:300]})


@router.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    """Stream a chat response. Picks Anthropic if available, else OpenAI."""
    client_a = _client_anthropic()
    if client_a is not None:
        return StreamingResponse(
            _stream_anthropic(client_a, req.messages, req.page),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    client_o = _client_openai()
    if client_o is not None:
        return StreamingResponse(
            _stream_openai(client_o, req.messages, req.page),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    async def _no_key() -> AsyncIterator[str]:
        yield _sse("error", {
            "message": "No API key set. Open Settings (⚙️) and add an Anthropic or OpenAI key.",
            "no_key": True,
        })

    return StreamingResponse(_no_key(), media_type="text/event-stream")
