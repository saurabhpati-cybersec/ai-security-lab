#!/usr/bin/env python3
"""Day 4 eval: run indirect injection dataset against named agent.

Usage:
    python3 labs/day-04-indirect-injection/eval.py --agent vulnerable
    python3 labs/day-04-indirect-injection/eval.py --agent protected
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.harness.runner import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the indirect_injection dataset against a named agent."
    )
    parser.add_argument(
        "--agent",
        default="vulnerable",
        choices=["vulnerable", "protected"],
        help="Agent variant to evaluate (default: vulnerable)",
    )
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    dataset = repo / "evals/datasets/indirect_injection.jsonl"

    summary = run_eval(
        dataset_path=dataset,
        agent_name=args.agent,
        max_api_calls=60,
        output_dir=repo / "evals/results",
    )

    print(
        f"\nAgent: {args.agent} | Dataset: indirect_injection | "
        f"ASR: {summary['asr']:.2%} | Cases: {summary['total']}"
    )
    print(f"Results: evals/results/{summary['run_id']}/")

    if summary.get("categories"):
        print("\nPer-category ASR:")
        for cat, stats in sorted(summary["categories"].items()):
            print(f"  {cat:<30} {stats['asr']:.2%}  ({stats['passed']}/{stats['total']})")

    print()
    print("Compare web_fetch_injection vs rag_doc_injection ASR.")
    print("IPI ASR is typically higher than direct injection ASR on well-trained models.")
    print("This is the highest-priority attack class: no user cooperation required.")


if __name__ == "__main__":
    main()
