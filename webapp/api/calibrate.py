"""API: re-score datasets against RulesDetector at a given threshold."""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel

from webapp.paths import DATASETS_DIR

router = APIRouter(tags=["calibrate"])

_ATTACK_NAMES = [
    "direct_injection",
    "indirect_injection",
    "tool_abuse",
    "rag_poison",
    "exfiltration",
]


def _load_inputs(name: str) -> list[str]:
    path = DATASETS_DIR / f"{name}.jsonl"
    if not path.exists():
        return []
    rows: list[str] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            text = row.get("input", "")
            if isinstance(text, str) and text:
                rows.append(text)
    return rows


@lru_cache(maxsize=8)
def _scores(name: str) -> tuple[float, ...]:
    from detectors.rules import RulesDetector

    det = RulesDetector(threshold=0.0)
    return tuple(det.check(t).confidence for t in _load_inputs(name))


class CalibrateRequest(BaseModel):
    threshold: float = 0.6
    attack_datasets: list[str] | None = None


@router.post("/calibrate")
async def calibrate(req: CalibrateRequest) -> dict:
    chosen = req.attack_datasets or _ATTACK_NAMES
    benign_scores = list(_scores("benign"))
    attack_scores: dict[str, list[float]] = {}
    for name in chosen:
        scores = list(_scores(name))
        if scores:
            attack_scores[name] = scores
    all_attacks = [s for ss in attack_scores.values() for s in ss]
    tpr = sum(1 for s in all_attacks if s >= req.threshold) / max(len(all_attacks), 1)
    fpr = sum(1 for s in benign_scores if s >= req.threshold) / max(len(benign_scores), 1)

    # TPR/FPR curve — sweeps 41 threshold points from 0 to 1.
    # RulesDetector scores are step-like (each rule contributes 0 or a fixed
    # weight), so scores cluster near 0.0 and 0.75–1.0 with almost nothing
    # between. The curve therefore looks like a staircase: large jumps at the
    # cluster boundaries, flat everywhere else. This is expected behavior, not
    # a bug — dragging the slider through the empty 0.08–0.70 gap won't change
    # any classification.
    ts = np.linspace(0.0, 1.0, 41).tolist()
    curve = [
        {
            "threshold": float(t),
            "tpr": sum(1 for s in all_attacks if s >= t) / max(len(all_attacks), 1),
            "fpr": sum(1 for s in benign_scores if s >= t) / max(len(benign_scores), 1),
        }
        for t in ts
    ]

    per_dataset = []
    for name, scores in attack_scores.items():
        detected = sum(1 for s in scores if s >= req.threshold)
        per_dataset.append({
            "dataset": name,
            "cases": len(scores),
            "detected": detected,
            "tpr": detected / len(scores) if scores else 0.0,
            "mean_score": sum(scores) / len(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
        })

    return {
        "threshold": req.threshold,
        "tpr": tpr,
        "fpr": fpr,
        "curve": curve,
        "per_dataset": per_dataset,
        "benign_cases": len(benign_scores),
        "benign_blocked": sum(1 for s in benign_scores if s >= req.threshold),
    }
