"""API: browse past eval runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from fastapi import APIRouter, HTTPException

from webapp.paths import RESULTS_DIR

router = APIRouter(tags=["runs"])


@dataclass
class RunSummary:
    run_id: str
    agent: str
    dataset: str
    asr: float | None
    fpr: float | None
    total: int
    passed: int
    failed: int
    errors: int
    error_rate: float
    runtime_seconds: float
    timestamp: str
    categories: dict
    schema_version: int
    first_error: str | None = None


def _first_error_from_cases(run_dir: Path) -> str | None:
    """Return the error message from the first errored case in cases.jsonl, or None."""
    cases_file = run_dir / "cases.jsonl"
    if not cases_file.exists():
        return None
    with cases_file.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            err = row.get("error")
            if err:
                # Truncate to keep the API response small.
                return str(err)[:200]
    return None


def _from_dir(run_dir: Path) -> RunSummary | None:
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        return None
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    asr_raw = data.get("asr")
    fpr_raw = data.get("fpr")
    errors = int(data.get("errors", 0))
    return RunSummary(
        run_id=data.get("run_id", run_dir.name),
        agent=data.get("agent", "unknown"),
        dataset=Path(data.get("dataset", "")).stem or "unknown",
        asr=float(asr_raw) if asr_raw is not None else None,
        fpr=float(fpr_raw) if fpr_raw is not None else None,
        total=int(data.get("total", 0)),
        passed=int(data.get("passed", 0)),
        failed=int(data.get("failed", 0)),
        errors=errors,
        error_rate=float(data.get("error_rate", 0.0)),
        runtime_seconds=float(data.get("runtime_seconds", 0.0)),
        timestamp=run_dir.name.rsplit("_", 1)[-1],
        categories=data.get("categories", {}),
        schema_version=int(data.get("schema_version", 1)),
        first_error=_first_error_from_cases(run_dir) if errors > 0 else None,
    )


@router.get("/runs")
async def list_runs() -> dict:
    out: list[dict] = []
    if not RESULTS_DIR.exists():
        return {"runs": out}
    for child in sorted(RESULTS_DIR.iterdir(), reverse=True):
        if child.is_dir():
            s = _from_dir(child)
            if s is not None:
                out.append(asdict(s))
    return {"runs": out}


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    run_dir = RESULTS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail="run not found")
    s = _from_dir(run_dir)
    cases_file = run_dir / "cases.jsonl"
    cases: list[dict] = []
    if cases_file.exists():
        with cases_file.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    cases.append(json.loads(line))
    return {"summary": asdict(s) if s else None, "cases": cases}
