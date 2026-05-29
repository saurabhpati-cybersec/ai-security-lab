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

    asr = summary.get("asr")
    fpr = summary.get("fpr")
    metric_str = (
        f"ASR: {asr:.2%}" if asr is not None
        else (f"FPR: {fpr:.2%}" if fpr is not None else "ASR: n/a")
    )
    print(f"\nAgent: {args.agent} | Dataset: direct_injection | {metric_str} | Cases: {summary['total']}")
    print(f"Results: evals/results/{summary['run_id']}/")

    if summary.get("categories"):
        print("\nPer-category:")
        for cat, stats in sorted(summary["categories"].items()):
            metric = stats.get("asr", stats.get("fpr"))
            metric_str = f"{metric:.2%}" if metric is not None else "n/a"
            print(f"  {cat:<25} {metric_str}  ({stats['passed']}/{stats['total']})")

    print()
    if args.agent == "vulnerable":
        print("The vulnerable agent should report a high ASR — most attacks succeed.")
        print("Run again with --agent protected to see how the defense stack reduces ASR.")
    else:
        print("Lower ASR = defenses are working.")
        print("Compare against the vulnerable baseline to measure defense effectiveness.")


if __name__ == "__main__":
    main()
