#!/usr/bin/env python3
"""Day 12 eval: protected agent vs baseline — benign and direct injection."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.harness.runner import run_eval
from evals.harness.scorers import compute_asr


def run_static_eval(dataset_path: Path, agent_name: str) -> dict:
    """Run a dataset-only check without live API for initial verification."""
    import json
    cases = [json.loads(l) for l in dataset_path.read_text().splitlines() if l.strip()]
    return {"dataset": dataset_path.stem, "agent": agent_name, "total": len(cases), "note": "static count only"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", default="protected", choices=["vulnerable", "protected"])
    parser.add_argument("--dataset", default="direct_injection",
                        choices=["benign", "direct_injection", "all"])
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    datasets = {
        "benign": repo / "evals/datasets/benign.jsonl",
        "direct_injection": repo / "evals/datasets/direct_injection.jsonl",
    }

    if args.dataset == "all":
        to_run = list(datasets.values())
    else:
        to_run = [datasets[args.dataset]]

    for ds_path in to_run:
        cases = [json.loads(l) for l in ds_path.read_text().splitlines() if l.strip()]
        print(f"\nDataset: {ds_path.stem} | Agent: {args.agent} | Cases: {len(cases)}")
        print("Run with live API key: python3 -c \"import sys; sys.path.insert(0,'.'); from evals.harness.runner import run_eval; r = run_eval('" + str(ds_path) + "', '" + args.agent + "', 60, 'evals/results'); print(f'ASR: {r[\"asr\"]:.2%}')\"")

    print("\nNote: Live eval requires ANTHROPIC_API_KEY or OPENAI_API_KEY.")
    print("Static check: all datasets found:", all(p.exists() for p in datasets.values()))


if __name__ == "__main__":
    main()
