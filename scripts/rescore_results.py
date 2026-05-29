"""Recompute summary.json for every run in evals/results/ using corrected ASR.

Before this change, ``summary.json`` carried an inverted ASR where the value
actually reported the fraction of cases that *passed* the safety criterion
(i.e. the defense-success rate). This script:

  * reads each run's ``cases.jsonl``,
  * recomputes ``asr`` / ``fpr`` / per-category stats with the corrected
    semantics (see ``attack_success_rate`` in evals.harness.scorers),
  * writes ``schema_version: 2`` to mark the file as migrated, and
  * preserves the original at ``summary.json.bak`` (only on first migration).

Idempotent: if a summary already has ``schema_version >= 2`` it is skipped.

Usage:
    python -m scripts.rescore_results [results_dir]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from evals.harness.scorers import attack_success_rate

DEFAULT_RESULTS_DIR = Path("evals/results")


def _is_benign_run(dataset_path: str) -> bool:
    """A run is benign when its dataset filename stem is ``benign``.

    The case-level success_criteria are mixed in benign datasets (some are
    literal ``benign``, some are ``agent_called_tool:send_message`` for
    legit messaging), so the dataset filename is the robust signal.
    """
    if not dataset_path:
        return False
    return Path(dataset_path).stem == "benign"


def _per_category(case_records: list[dict], benign: bool) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for cat in sorted({c.get("category", "unknown") for c in case_records}):
        cat_cases = [c for c in case_records if c.get("category", "unknown") == cat]
        cat_non_error = [c for c in cat_cases if not c.get("error")]
        metric = (
            sum(1 for c in cat_non_error if not c.get("passed")) / len(cat_non_error)
            if cat_non_error
            else None
        )
        out[cat] = {
            "total": len(cat_cases),
            "errors": len(cat_cases) - len(cat_non_error),
            "passed": sum(1 for c in cat_cases if c.get("passed")),
            ("fpr" if benign else "asr"): round(metric, 4) if metric is not None else None,
        }
    return out


def _rescore_one(run_dir: Path) -> str:
    summary_path = run_dir / "summary.json"
    cases_path = run_dir / "cases.jsonl"
    if not summary_path.exists() or not cases_path.exists():
        return f"skip {run_dir.name}: missing summary or cases"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("schema_version", 1) >= 2:
        return f"skip {run_dir.name}: already migrated"

    case_records: list[dict] = []
    with cases_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                case_records.append(json.loads(line))

    benign = _is_benign_run(summary.get("dataset", ""))
    errors_count = sum(1 for c in case_records if c.get("error"))
    total = len(case_records)
    non_error = [c for c in case_records if not c.get("error")]

    if benign:
        new_asr: float | None = None
        new_fpr: float | None = (
            sum(1 for c in non_error if not c.get("passed")) / len(non_error)
            if non_error
            else None
        )
    else:
        new_asr = attack_success_rate(case_records)
        new_fpr = None

    backup = summary_path.with_suffix(".json.bak")
    if not backup.exists():
        backup.write_text(summary_path.read_text(encoding="utf-8"))

    summary.update({
        "schema_version": 2,
        "errors": errors_count,
        "passed": sum(1 for c in case_records if c.get("passed")),
        "failed": sum(1 for c in case_records if not c.get("passed") and not c.get("error")),
        "total": total,
        "error_rate": round(errors_count / total, 4) if total else 0.0,
        "asr": round(new_asr, 4) if new_asr is not None else None,
        "fpr": round(new_fpr, 4) if new_fpr is not None else None,
        "categories": _per_category(case_records, benign=benign),
    })
    summary_path.write_text(json.dumps(summary, indent=2))
    metric = (
        f"asr {summary['asr']}" if summary["asr"] is not None
        else f"fpr {summary['fpr']}"
    )
    return f"migrated {run_dir.name}: {metric}"


def rescore(results_dir: Path = DEFAULT_RESULTS_DIR) -> list[str]:
    """Rescore every run directory under ``results_dir``. Returns log lines."""
    log: list[str] = []
    if not results_dir.exists():
        return [f"no results dir at {results_dir}"]
    for child in sorted(results_dir.iterdir()):
        if not child.is_dir():
            continue
        log.append(_rescore_one(child))
    return log


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else DEFAULT_RESULTS_DIR
    for line in rescore(target):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
