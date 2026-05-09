#!/usr/bin/env python3
"""Day 7 eval: run exfiltration dataset against named agent.

Usage:
    python3 labs/day-07-data-exfiltration/eval.py --agent vulnerable
    python3 labs/day-07-data-exfiltration/eval.py --agent protected
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.harness.runner import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the exfiltration dataset against a named agent."
    )
    parser.add_argument(
        "--agent",
        default="vulnerable",
        choices=["vulnerable", "protected"],
        help="Agent variant to evaluate (default: vulnerable)",
    )
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    dataset = repo / "evals/datasets/exfiltration.jsonl"

    summary = run_eval(
        dataset_path=dataset,
        agent_name=args.agent,
        max_api_calls=60,
        output_dir=repo / "evals/results",
    )

    print(
        f"\nAgent: {args.agent} | Dataset: exfiltration | "
        f"ASR: {summary['asr']:.2%} | Cases: {summary['total']}"
    )
    print(f"Results: evals/results/{summary['run_id']}/")

    if summary.get("categories"):
        print("\nPer-channel ASR:")
        for cat, stats in sorted(summary["categories"].items()):
            print(f"  {cat:<30} {stats['asr']:.2%}  ({stats['passed']}/{stats['total']})")

    print()
    print("This is the Day 3-7 culmination: injection delivers the instruction,")
    print("access retrieves the data, egress completes the breach (lethal trifecta).")
    print("Days 8-10 implement defenses against each channel.")


if __name__ == "__main__":
    main()
