#!/usr/bin/env python3
"""Day 6 eval: run rag_poison dataset against named agent.

The rag_poison dataset simulates poisoned corpus retrieval by embedding
the poison document content in the user query (as if read_doc had returned
it). This measures whether the agent follows injected instructions in
retrieved documents without requiring actual corpus writes.

To also test with actual corpus poisoning, run poison_corpus.py first,
then query the agent directly — see DELIVERABLE.md for the full workflow.

Usage:
    python3 labs/day-06-rag-poisoning/eval.py --agent vulnerable
    python3 labs/day-06-rag-poisoning/eval.py --agent protected
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.harness.runner import run_eval


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the rag_poison dataset against a named agent."
    )
    parser.add_argument(
        "--agent",
        default="vulnerable",
        choices=["vulnerable", "protected"],
        help="Agent variant to evaluate (default: vulnerable)",
    )
    args = parser.parse_args()

    repo = Path(__file__).parent.parent.parent
    dataset = repo / "evals/datasets/rag_poison.jsonl"

    summary = run_eval(
        dataset_path=dataset,
        agent_name=args.agent,
        max_api_calls=60,
        output_dir=repo / "evals/results",
    )

    print(
        f"\nAgent: {args.agent} | Dataset: rag_poison | "
        f"ASR: {summary['asr']:.2%} | Cases: {summary['total']}"
    )
    print(f"Results: evals/results/{summary['run_id']}/")

    if summary.get("categories"):
        print("\nPer-category ASR:")
        for cat, stats in sorted(summary["categories"].items()):
            print(f"  {cat:<30} {stats['asr']:.2%}  ({stats['passed']}/{stats['total']})")

    print()
    print("Run 'python3 attack/poison_corpus.py poison hidden' then query the agent")
    print("directly to test actual corpus poisoning (not simulated via dataset).")
    print("Always run 'python3 attack/poison_corpus.py clean' afterward.")


if __name__ == "__main__":
    main()
