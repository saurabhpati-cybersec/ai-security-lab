"""Semantic tests for ASR / FPR / TPR — pin the corrected orientation.

Key contract:
- ``attack_success_rate(case_results)`` returns the fraction of *non-error*
  attack cases whose ``passed`` is False (i.e. attack succeeded). Error cases
  are excluded from the denominator.
- ``compute_tpr_fpr`` expects booleans where True means *attack succeeded*
  for attack inputs and True means *agent passed benign criteria* for
  benign inputs. This file pins that contract so future refactors cannot
  silently re-invert it.
"""

from __future__ import annotations

import pytest

from evals.harness.scorers import (
    attack_success_rate,
    compute_asr,
    compute_tpr_fpr,
)


def _case(passed: bool, error: str | None = None) -> dict:
    return {"passed": passed, "error": error}


# ---------------------------------------------------------------------------
# attack_success_rate
# ---------------------------------------------------------------------------

def test_attack_success_rate_refuse_all_is_zero() -> None:
    # Every case meets criteria (agent refused / behaved safely) ⇒ ASR = 0.
    cases = [_case(True) for _ in range(10)]
    assert attack_success_rate(cases) == 0.0


def test_attack_success_rate_comply_all_is_one() -> None:
    # Every case violates criteria (agent complied with attack) ⇒ ASR = 1.
    cases = [_case(False) for _ in range(10)]
    assert attack_success_rate(cases) == 1.0


def test_attack_success_rate_mixed() -> None:
    # 3 passed (safe) + 7 failed (compromised) ⇒ ASR = 0.7.
    cases = [_case(True)] * 3 + [_case(False)] * 7
    assert attack_success_rate(cases) == pytest.approx(0.7)


def test_attack_success_rate_excludes_errors_from_denominator() -> None:
    # 2 safe + 2 compromised + 6 errors → denominator is 4, ASR = 0.5.
    cases = (
        [_case(True)] * 2
        + [_case(False)] * 2
        + [_case(False, error="ConnectionError")] * 6
    )
    assert attack_success_rate(cases) == pytest.approx(0.5)


def test_attack_success_rate_all_errors_returns_none() -> None:
    # No non-error cases ⇒ ASR is undefined; helper returns None so callers
    # can render "N/A" instead of a misleading 0.0.
    cases = [_case(False, error="X") for _ in range(5)]
    assert attack_success_rate(cases) is None


def test_attack_success_rate_empty_returns_none() -> None:
    assert attack_success_rate([]) is None


# ---------------------------------------------------------------------------
# compute_tpr_fpr orientation pin (do NOT change without intent)
# ---------------------------------------------------------------------------

def test_compute_tpr_fpr_attack_true_means_attack_succeeded() -> None:
    # 3 of 4 attacks succeeded → TPR = 0.75.
    out = compute_tpr_fpr(
        attack_results=[True, True, True, False],
        benign_results=[True, True, True, True],
    )
    assert out["tpr"] == pytest.approx(0.75)
    assert out["fpr"] == pytest.approx(0.0)


def test_compute_tpr_fpr_benign_true_means_passed_so_false_means_blocked() -> None:
    # 1 of 4 benign cases blocked → FPR = 0.25.
    out = compute_tpr_fpr(
        attack_results=[False, False],
        benign_results=[True, True, True, False],
    )
    assert out["fpr"] == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# compute_asr is unchanged — keep it as a generic mean for reuse.
# ---------------------------------------------------------------------------

def test_compute_asr_remains_a_generic_mean() -> None:
    # Pin: compute_asr is the mean of a boolean list, nothing more.
    assert compute_asr([True, False, True, False]) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# webapp/api/calibrate.py — detector-score TPR / FPR orientation pin
# ---------------------------------------------------------------------------

def test_calibrate_endpoint_tpr_fpr_use_detector_flagged_orientation(
    tmp_path, monkeypatch
) -> None:
    """TPR = fraction of attack rows the detector flagged (score >= threshold).
    FPR = fraction of benign rows the detector flagged.

    Pins the orientation against an accidental re-mapping during a future
    consolidation with compute_tpr_fpr."""
    import asyncio

    import webapp.api.calibrate as cal

    # Fake the scores cache: pretend the detector returned [0.9, 0.9] on
    # attack inputs and [0.1] on benign inputs.
    fake_scores = {
        "direct_injection": (0.9, 0.9),
        "benign": (0.1,),
    }

    def _fake_scores(name: str) -> tuple[float, ...]:
        return fake_scores.get(name, ())

    monkeypatch.setattr(cal, "_scores", _fake_scores)

    req = cal.CalibrateRequest(threshold=0.5, attack_datasets=["direct_injection"])
    out = asyncio.run(cal.calibrate(req))

    # Both attacks scored 0.9 ≥ 0.5 → TPR = 1.0 (detector caught everything).
    assert out["tpr"] == pytest.approx(1.0)
    # Benign scored 0.1 < 0.5 → FPR = 0.0 (no false alarm).
    assert out["fpr"] == pytest.approx(0.0)
