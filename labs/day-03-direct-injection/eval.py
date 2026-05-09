#!/usr/bin/env python3
"""Day 3 eval: run direct injection dataset against named agent.

Usage:
    python3 labs/day-03-direct-injection/eval.py --agent vulnerable
    python3 labs/day-03-direct-injection/eval.py --agent protected
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.harness.runner import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the direct_injection dataset against a named agent."
    )
    parser.add_argument(
        "--agent",
        default="vulnerable",
        choices=["vulnerable", "protected"],
        help="Agent variant to evaluate (default: vulnerable)",
    )
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    dataset = repo / "evals/datasets/direct_injection.jsonl"

    summary = run_eval(
        dataset_path=dataset,
        agent_name=args.agent,
        max_api_calls=50,
        output_dir=repo / "evals/results",
    )

    print(
        f"\nAgent: {args.agent} | Dataset: direct_injection | "
        f"ASR: {summary['asr']:.2%} | Cases: {summary['total']}"
    )
    print(f"Results: evals/results/{summary['run_id']}/")

    if summary.get("categories"):
        print("\nPer-category ASR:")
        for cat, stats in sorted(summary["categories"].items()):
            print(f"  {cat:<25} {stats['asr']:.2%}  ({stats['passed']}/{stats['total']})")

    print()
    if args.agent == "vulnerable":
        print("Higher ASR = more attacks succeeded = expected for the vulnerable agent.")
        print("Record this baseline before running Day 8 defenses.")
    else:
        print("Lower ASR = defenses are working.")
        print("Compare against the vulnerable baseline to measure defense effectiveness.")


if __name__ == "__main__":
    main()
