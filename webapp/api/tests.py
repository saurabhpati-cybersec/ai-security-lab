"""API: run pytest from the UI, stream output."""

from __future__ import annotations

import asyncio
import subprocess
import sys
import threading
import uuid
from collections import deque
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from webapp.paths import REPO_ROOT

router = APIRouter(tags=["tests"])

_JOBS: dict[str, dict] = {}


def _run_pytest(job_id: str) -> None:
    job = _JOBS[job_id]
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--color=no"],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        job["proc"] = proc
        for line in proc.stdout:  # type: ignore[union-attr]
            job["buffer"].append(line.rstrip("\n"))
        proc.wait()
        job["exit_code"] = proc.returncode
        job["status"] = "completed"
    except Exception as exc:  # noqa: BLE001
        job["error"] = f"{type(exc).__name__}: {exc}"
        job["status"] = "error"


@router.post("/tests/start")
async def start_tests() -> dict:
    job_id = uuid.uuid4().hex[:12]
    _JOBS[job_id] = {
        "status": "running",
        "buffer": deque(),
        "exit_code": None,
        "cursor": 0,
    }
    threading.Thread(target=_run_pytest, args=(job_id,), daemon=True).start()
    return {"job_id": job_id}


async def _test_stream(job_id: str) -> AsyncIterator[str]:
    import json

    job = _JOBS.get(job_id)
    if job is None:
        yield f"event: error\ndata: {json.dumps({'message': 'unknown job'})}\n\n"
        return

    seen = 0
    while True:
        # Drain buffer
        buf = list(job["buffer"])
        while seen < len(buf):
            line = buf[seen]
            seen += 1
            yield f"event: line\ndata: {json.dumps({'text': line})}\n\n"

        status = job["status"]
        if status == "completed":
            yield (
                f"event: done\n"
                f"data: {json.dumps({'exit_code': job.get('exit_code')})}\n\n"
            )
            return
        if status == "error":
            yield f"event: error\ndata: {json.dumps({'message': job.get('error')})}\n\n"
            return
        await asyncio.sleep(0.25)


@router.get("/tests/{job_id}/stream")
async def tests_stream(job_id: str) -> StreamingResponse:
    return StreamingResponse(
        _test_stream(job_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
