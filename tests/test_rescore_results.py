"""Tests for scripts.rescore_results — back-fill legacy summary.json files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def _make_legacy_run(
    root: Path,
    run_id: str,
    cases: list[dict],
    legacy_asr: float,
    agent: str = "vulnerable",
    dataset: str = "evals/datasets/direct_injection.jsonl",
) -> Path:
    run_dir = root / run_id
    run_dir.mkdir(parents=True)
    cases_path = run_dir / "cases.jsonl"
    with cases_path.open("w", encoding="utf-8") as fh:
        for case in cases:
            fh.write(json.dumps(case) + "\n")
    summary = {
        "run_id": run_id,
        "dataset": dataset,
        "agent": agent,
        "total": len(cases),
        "passed": sum(1 for c in cases if c["passed"]),
        "failed": sum(1 for c in cases if not c["passed"] and not c.get("error")),
        "errors": sum(1 for c in cases if c.get("error")),
        "asr": legacy_asr,
        "categories": {},
        "runtime_seconds": 1.0,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return run_dir


def test_rescore_flips_attack_run(tmp_path) -> None:
    from scripts.rescore_results import rescore

    cases = [
        {"id": "1", "category": "x", "success_criteria": "regex:bar",
         "passed": True, "error": None},
        {"id": "2", "category": "x", "success_criteria": "regex:bar",
         "passed": True, "error": None},
        {"id": "3", "category": "x", "success_criteria": "regex:bar",
         "passed": False, "error": None},
        {"id": "4", "category": "x", "success_criteria": "regex:bar",
         "passed": False, "error": None},
    ]
    run_dir = _make_legacy_run(tmp_path, "vulnerable_x_20260101T000000Z",
                               cases, legacy_asr=0.5)

    rescore(tmp_path)

    new_summary = json.loads((run_dir / "summary.json").read_text())
    assert new_summary["schema_version"] == 2
    # Was 0.5 (mean of [T,T,F,F]); corrected = mean(not passed) = 0.5 as well
    # because of the symmetric split. Use an asymmetric case below for the flip.
    backup = run_dir / "summary.json.bak"
    assert backup.exists()


def test_rescore_asymmetric_attack_run_flips_value(tmp_path) -> None:
    from scripts.rescore_results import rescore

    cases = [
        {"id": "1", "category": "x", "success_criteria": "regex:bar",
         "passed": True, "error": None},
        {"id": "2", "category": "x", "success_criteria": "regex:bar",
         "passed": True, "error": None},
        {"id": "3", "category": "x", "success_criteria": "regex:bar",
         "passed": True, "error": None},
        {"id": "4", "category": "x", "success_criteria": "regex:bar",
         "passed": False, "error": None},
    ]
    run_dir = _make_legacy_run(tmp_path, "protected_x_20260101T000000Z",
                               cases, legacy_asr=0.75)

    rescore(tmp_path)

    new_summary = json.loads((run_dir / "summary.json").read_text())
    # Legacy was 0.75 (3 passed / 4). Corrected = 1 - 0.75 = 0.25.
    assert new_summary["asr"] == pytest.approx(0.25)
    assert new_summary["fpr"] is None


def test_rescore_benign_run_emits_fpr_not_asr(tmp_path) -> None:
    from scripts.rescore_results import rescore

    cases = [
        {"id": str(i), "category": "ok", "success_criteria": "benign",
         "passed": True, "error": None}
        for i in range(8)
    ] + [
        {"id": "fp", "category": "ok", "success_criteria": "benign",
         "passed": False, "error": None}
    ]
    run_dir = _make_legacy_run(
        tmp_path,
        "vulnerable_benign_20260101T000000Z",
        cases,
        legacy_asr=8 / 9,
        dataset="evals/datasets/benign.jsonl",
    )

    rescore(tmp_path)

    new_summary = json.loads((run_dir / "summary.json").read_text())
    assert new_summary["asr"] is None
    assert new_summary["fpr"] == pytest.approx(0.1111, abs=1e-4)


def test_rescore_excludes_errors_from_denominator(tmp_path) -> None:
    from scripts.rescore_results import rescore

    cases = [
        {"id": "1", "passed": False, "category": "x",
         "success_criteria": "regex:bar", "error": "Boom"},
        {"id": "2", "passed": False, "category": "x",
         "success_criteria": "regex:bar", "error": "Boom"},
        {"id": "3", "passed": True, "category": "x",
         "success_criteria": "regex:bar", "error": None},
        {"id": "4", "passed": False, "category": "x",
         "success_criteria": "regex:bar", "error": None},
    ]
    run_dir = _make_legacy_run(tmp_path, "vulnerable_x_20260101T000000Z",
                               cases, legacy_asr=0.25)

    rescore(tmp_path)

    new_summary = json.loads((run_dir / "summary.json").read_text())
    # 2 non-error cases, 1 compromised ⇒ ASR = 0.5 (NOT 1/4 = 0.25).
    assert new_summary["asr"] == pytest.approx(0.5)
    assert new_summary["errors"] == 2


def test_rescore_is_idempotent_via_schema_version(tmp_path) -> None:
    from scripts.rescore_results import rescore

    cases = [
        {"id": "1", "category": "x", "success_criteria": "regex:bar",
         "passed": False, "error": None}
    ]
    run_dir = _make_legacy_run(tmp_path, "vulnerable_x_20260101T000000Z",
                               cases, legacy_asr=0.0)

    rescore(tmp_path)
    first = json.loads((run_dir / "summary.json").read_text())
    rescore(tmp_path)
    second = json.loads((run_dir / "summary.json").read_text())

    # No re-flip on the second pass.
    assert first == second
    # The .bak captures the *original* legacy file, not an already-rescored one.
    backup = json.loads((run_dir / "summary.json.bak").read_text())
    assert "schema_version" not in backup


def test_rescore_benign_classification_uses_dataset_stem_not_per_case_criteria(tmp_path) -> None:
    """Mixed-criteria benign datasets (some 'benign', some 'agent_called_tool:...')
    must still be classified as benign by dataset stem and produce fpr, not asr."""
    from scripts.rescore_results import rescore

    cases = [
        {"id": "1", "category": "ok", "success_criteria": "benign",
         "passed": True, "error": None},
        {"id": "2", "category": "msg", "success_criteria": "agent_called_tool:send_message",
         "passed": False, "error": None},
    ]
    run_dir = _make_legacy_run(
        tmp_path, "vulnerable_benign_20260101T000000Z", cases,
        legacy_asr=0.5, dataset="evals/datasets/benign.jsonl",
    )

    rescore(tmp_path)

    new_summary = json.loads((run_dir / "summary.json").read_text())
    assert new_summary["asr"] is None
    assert new_summary["fpr"] == pytest.approx(0.5)
