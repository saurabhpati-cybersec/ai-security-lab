#!/usr/bin/env python3
"""Day 13 eval: red-team protected agent — compare ASR across all datasets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def count_dataset(path: Path) -> int:
    return sum(1 for l in path.read_text().splitlines() if l.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", default="protected", choices=["vulnerable", "protected"])
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    datasets = list((repo / "evals/datasets").glob("*.jsonl"))

    print(f"\nRed-team eval: {args.agent} agent")
    print(f"{'Dataset':<30} {'Cases':>6}")
    print("-" * 40)
    total = 0
    for ds in sorted(datasets):
        n = count_dataset(ds)
        total += n
        print(f"{ds.stem:<30} {n:>6}")
    print("-" * 40)
    print(f"{'Total':<30} {total:>6}")
    print("\nRun live: python3 -m evals.harness.runner --agent", args.agent, "--all (once runner CLI is added)")
    print("Or: make eval-all")


if __name__ == "__main__":
    main()
