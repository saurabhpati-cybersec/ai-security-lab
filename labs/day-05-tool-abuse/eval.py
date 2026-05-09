#!/usr/bin/env python3
"""Day 5 eval: run tool_abuse dataset against named agent.

Usage:
    python3 labs/day-05-tool-abuse/eval.py --agent vulnerable
    python3 labs/day-05-tool-abuse/eval.py --agent protected
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.harness.runner import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the tool_abuse dataset against a named agent."
    )
    parser.add_argument(
        "--agent",
        default="vulnerable",
        choices=["vulnerable", "protected"],
        help="Agent variant to evaluate (default: vulnerable)",
    )
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    dataset = repo / "evals/datasets/tool_abuse.jsonl"

    summary = run_eval(
        dataset_path=dataset,
        agent_name=args.agent,
        max_api_calls=60,
        output_dir=repo / "evals/results",
    )

    print(
        f"\nAgent: {args.agent} | Dataset: tool_abuse | "
        f"ASR: {summary['asr']:.2%} | Cases: {summary['total']}"
    )
    print(f"Results: evals/results/{summary['run_id']}/")

    if summary.get("categories"):
        print("\nPer-category ASR:")
        for cat, stats in sorted(summary["categories"].items()):
            print(f"  {cat:<30} {stats['asr']:.2%}  ({stats['passed']}/{stats['total']})")

    print()
    print("Note: SSRF tool calls may succeed (call made) even if HTTP returns an error.")
    print("Check cases.jsonl tool_calls_made field to see which tools were invoked.")
    print("Day 10 (sandboxing) addresses these with URL allowlisting and path sanitization.")


if __name__ == "__main__":
    main()
