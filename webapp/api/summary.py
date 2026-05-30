"""API: parse evals/results/latest_summary.md for headline metrics."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from fastapi import APIRouter

from webapp.paths import SUMMARY_FILE

router = APIRouter(tags=["summary"])


@dataclass
class SummaryHighlights:
    vuln_avg_asr: float | None
    prot_avg_asr: float | None
    delta: float | None
    relative_reduction: float | None
    estimated: bool
    total_cases: int
    rows: list[dict]


_TABLE_RE = re.compile(
    r"^\|\s*(?P<dataset>[\w_]+)(?:\s*\(FPR\))?\s*\|\s*"
    r"(?P<cases>\d+)\s*\|\s*(?P<vuln>[\d.]+)\s*\|\s*(?P<prot>[\d.]+)\s*\|",
    re.MULTILINE,
)


def _load_highlights() -> dict | None:
    if not SUMMARY_FILE.exists():
        return None
    text = SUMMARY_FILE.read_text(encoding="utf-8")
    rows: list[dict] = []
    for m in _TABLE_RE.finditer(text):
        rows.append({
            "dataset": m.group("dataset"),
            "cases": int(m.group("cases")),
            "vuln_asr": float(m.group("vuln")),
            "prot_asr": float(m.group("prot")),
        })
    if not rows:
        return None
    attack_rows = [r for r in rows if r["dataset"] != "benign"]
    vuln_avg = sum(r["vuln_asr"] for r in attack_rows) / len(attack_rows) if attack_rows else None
    prot_avg = sum(r["prot_asr"] for r in attack_rows) / len(attack_rows) if attack_rows else None
    delta = prot_avg - vuln_avg if (vuln_avg is not None and prot_avg is not None) else None
    rel = delta / vuln_avg if (vuln_avg not in (None, 0.0) and delta is not None) else None
    estimated = "estimated" in text.lower() or "static analysis" in text.lower()
    return asdict(SummaryHighlights(
        vuln_avg_asr=vuln_avg,
        prot_avg_asr=prot_avg,
        delta=delta,
        relative_reduction=rel,
        estimated=estimated,
        total_cases=sum(r["cases"] for r in rows),
        rows=rows,
    ))


@router.get("/summary")
async def get_summary() -> dict:
    h = _load_highlights()
    return {"highlights": h}
