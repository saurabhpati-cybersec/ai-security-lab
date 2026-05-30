"""Tests for evals.harness.scorers."""

from __future__ import annotations

import pytest

from evals.harness.scorers import bootstrap_ci, compute_asr, compute_tpr_fpr


# ---------------------------------------------------------------------------
# compute_asr
# ---------------------------------------------------------------------------

def test_compute_asr_empty() -> None:
    assert compute_asr([]) == 0.0


def test_compute_asr_mixed() -> None:
    assert compute_asr([True, True, False]) == pytest.approx(2 / 3)


def test_compute_asr_all_false() -> None:
    assert compute_asr([False, False]) == 0.0


def test_compute_asr_all_true() -> None:
    assert compute_asr([True, True, True]) == 1.0


# ---------------------------------------------------------------------------
# bootstrap_ci
# ---------------------------------------------------------------------------

def test_bootstrap_ci_all_true_collapses() -> None:
    lower, upper = bootstrap_ci([True] * 100)
    assert lower == 1.0 and upper == 1.0


def test_bootstrap_ci_all_false_collapses() -> None:
    lower, upper = bootstrap_ci([False] * 100)
    assert lower == 0.0 and upper == 0.0


def test_bootstrap_ci_mixed_bounds_reasonable() -> None:
    mixed = [True] * 50 + [False] * 50
    lower, upper = bootstrap_ci(mixed, n_resamples=500)
    assert 0.0 <= lower <= 0.5
    assert 0.5 <= upper <= 1.0
    assert lower <= upper
    assert 0.0 <= lower <= 1.0
    assert 0.0 <= upper <= 1.0


def test_bootstrap_ci_contains_mean() -> None:
    results = [True, False, True, True, False, True, False, False, True, True]
    lower, upper = bootstrap_ci(results, n_resamples=2000, seed=0)
    assert isinstance(lower, float)
    assert isinstance(upper, float)
    assert lower <= upper
    assert 0.0 <= lower <= 1.0
    assert 0.0 <= upper <= 1.0
    # True count = 6/10 = 0.6; CI should straddle 0.6
    assert lower <= 0.6 <= upper


# ---------------------------------------------------------------------------
# compute_tpr_fpr
# ---------------------------------------------------------------------------

def test_compute_tpr_fpr_returns_all_keys() -> None:
    out = compute_tpr_fpr(
        attack_results=[True, True, False, True],
        benign_results=[True, True, True, False],
    )
    assert set(out.keys()) == {"tpr", "fpr", "tpr_ci", "fpr_ci"}


def test_compute_tpr_fpr_correct_values() -> None:
    out = compute_tpr_fpr(
        attack_results=[True, True, False, True],
        benign_results=[True, True, True, False],
    )
    assert out["tpr"] == pytest.approx(0.75)
    # 1 of 4 benign cases failed → FPR = 0.25
    assert out["fpr"] == pytest.approx(0.25)
