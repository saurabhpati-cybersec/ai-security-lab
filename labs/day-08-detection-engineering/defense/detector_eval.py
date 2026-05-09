#!/usr/bin/env python3
"""Eval: measure RulesDetector and ClassifierDetector TPR/FPR with bootstrap 95% CIs."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from detectors.rules import RulesDetector
from evals.harness.scorers import bootstrap_ci, compute_asr, compute_tpr_fpr


def load_results(dataset_path: Path) -> list[bool]:
    """Load JSONL dataset, run RulesDetector, return list of is_injection bools."""
    detector = RulesDetector(threshold=0.5)
    results = []
    for line in dataset_path.read_text().splitlines():
        if not line.strip():
            continue
        case = json.loads(line)
        text = case["input"]
        result = detector.check(text)
        results.append(result.is_injection)
    return results


def main() -> None:
    repo = Path(__file__).parent.parent.parent.parent

    # Load attack datasets (TP — should detect)
    attack_datasets = [
        repo / "evals/datasets/direct_injection.jsonl",
        repo / "evals/datasets/indirect_injection.jsonl",
    ]
    # Load benign dataset (TN — should NOT detect)
    benign_dataset = repo / "evals/datasets/benign.jsonl"

    attack_results = []
    for ds in attack_datasets:
        attack_results.extend(load_results(ds))

    benign_results = load_results(benign_dataset)

    # Compute TPR (true positive rate on attacks) and FPR (false positive rate on benign)
    tpr = compute_asr(attack_results)
    fpr = compute_asr(benign_results)  # benign flagged as injection = FP
    tpr_ci = bootstrap_ci(attack_results)
    fpr_ci = bootstrap_ci(benign_results)

    print(f"\nRulesDetector @ threshold=0.5")
    print(f"  TPR: {tpr:.2%}  95% CI: [{tpr_ci[0]:.2%}, {tpr_ci[1]:.2%}]")
    print(f"  FPR: {fpr:.2%}  95% CI: [{fpr_ci[0]:.2%}, {fpr_ci[1]:.2%}]")
    print(f"\n  Attack cases: {len(attack_results)}")
    print(f"  Benign cases: {len(benign_results)}")
    print("\nNote: TPR on raw user input only — IPI via tool results requires check_tool_result().")
    print("Use ClassifierDetector (requires API key) for higher accuracy on ambiguous inputs.")


if __name__ == "__main__":
    main()
