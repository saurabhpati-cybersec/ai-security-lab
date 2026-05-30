"""API: start an eval run, stream cases via Server-Sent Events."""

from __future__ import annotations

import asyncio
import json
import threading
import time
import uuid
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from webapp.paths import DATASETS_DIR, RESULTS_DIR

router = APIRouter(tags=["eval"])

# In-memory registry of in-flight runs, keyed by short job_id.
_JOBS: dict[str, dict] = {}


class StartEvalRequest(BaseModel):
    dataset: str  # e.g. "direct_injection"
    agent: str  # "vulnerable" | "protected"
    max_api_calls: int = 50


class StartEvalResponse(BaseModel):
    job_id: str
    run_dir: str
    dataset_path: str
    total_cases: int


def _datasets() -> list[str]:
    return sorted(p.stem for p in DATASETS_DIR.glob("*.jsonl"))


@router.get("/eval/datasets")
async def list_datasets() -> dict:
    return {"datasets": _datasets()}


@router.get("/eval/datasets/{name}")
async def get_dataset(name: str) -> dict:
    """Return all cases in a dataset for preview before running."""
    path = DATASETS_DIR / f"{name}.jsonl"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"dataset not found: {name}")
    cases: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return {"name": name, "count": len(cases), "cases": cases}


def _count_dataset(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def _run_in_thread(job_id: str, dataset_path: Path, agent_name: str, max_calls: int) -> None:
    from evals.harness.runner import run_eval

    try:
        summary = run_eval(
            dataset_path=dataset_path,
            agent_name=agent_name,
            max_api_calls=max_calls,
            output_dir=RESULTS_DIR,
        )
        _JOBS[job_id]["summary"] = summary
        _JOBS[job_id]["status"] = "completed"
    except Exception as exc:  # noqa: BLE001
        _JOBS[job_id]["error"] = f"{type(exc).__name__}: {exc}"
        _JOBS[job_id]["status"] = "error"


@router.post("/eval/start", response_model=StartEvalResponse)
async def start_eval(req: StartEvalRequest) -> StartEvalResponse:
    dataset_path = DATASETS_DIR / f"{req.dataset}.jsonl"
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"dataset not found: {req.dataset}")

    if req.agent not in ("vulnerable", "protected"):
        raise HTTPException(status_code=400, detail=f"unknown agent: {req.agent}")

    job_id = uuid.uuid4().hex[:12]
    existing = {p.name for p in RESULTS_DIR.iterdir()} if RESULTS_DIR.exists() else set()

    _JOBS[job_id] = {
        "status": "running",
        "dataset": req.dataset,
        "agent": req.agent,
        "existing_dirs": existing,
        "total_cases": _count_dataset(dataset_path),
        "run_dir": None,
    }

    threading.Thread(
        target=_run_in_thread,
        args=(job_id, dataset_path, req.agent, req.max_api_calls),
        daemon=True,
    ).start()

    return StartEvalResponse(
        job_id=job_id,
        run_dir="",
        dataset_path=str(dataset_path),
        total_cases=_JOBS[job_id]["total_cases"],
    )


def _find_new_run_dir(job: dict) -> Path | None:
    if job.get("run_dir"):
        return Path(job["run_dir"])
    if not RESULTS_DIR.exists():
        return None
    existing = job["existing_dirs"]
    for child in sorted(RESULTS_DIR.iterdir()):
        if child.is_dir() and child.name not in existing:
            job["run_dir"] = str(child)
            return child
    return None


def _read_cases(run_dir: Path) -> list[dict]:
    cases_file = run_dir / "cases.jsonl"
    if not cases_file.exists():
        return []
    rows: list[dict] = []
    with cases_file.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


async def _eval_stream(job_id: str) -> AsyncIterator[str]:
    """SSE stream: 'case' events per row, then 'done' with summary or 'error'."""
    job = _JOBS.get(job_id)
    if job is None:
        yield f"event: error\ndata: {json.dumps({'message': 'unknown job'})}\n\n"
        return

    seen = 0
    while True:
        run_dir = _find_new_run_dir(job)
        if run_dir is not None:
            rows = _read_cases(run_dir)
            while seen < len(rows):
                row = rows[seen]
                seen += 1
                yield f"event: case\ndata: {json.dumps(row)}\n\n"

        status = job["status"]
        if status == "completed":
            yield f"event: done\ndata: {json.dumps(job.get('summary', {}))}\n\n"
            return
        if status == "error":
            yield f"event: error\ndata: {json.dumps({'message': job.get('error')})}\n\n"
            return
        await asyncio.sleep(0.4)


@router.get("/eval/{job_id}/stream")
async def eval_stream(job_id: str) -> StreamingResponse:
    return StreamingResponse(
        _eval_stream(job_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
