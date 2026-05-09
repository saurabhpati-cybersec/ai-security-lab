#!/usr/bin/env python3
"""Day 9 eval: I/O validation defense — measure ASR delta on exfil + injection datasets."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from detectors.output_filter import OutputFilter
from detectors.rules import RulesDetector
from evals.harness.scorers import compute_asr


def run_validation_eval(dataset_path: Path) -> float:
    """Run ValidationLayer eval without live API (input-only check + output filter check)."""
    detector = RulesDetector(threshold=0.5)
    output_filter = OutputFilter()

    results = []
    for line in dataset_path.read_text().splitlines():
        if not line.strip():
            continue
        case = json.loads(line)
        text = case["input"]

        # Check if input would be blocked
        det_result = detector.check(text)
        if det_result.is_injection:
            # Blocked — attack failed → success_criteria "not_agent_called_tool" would be True
            results.append(True)
            continue

        # Check if the input contains obvious exfil patterns the filter would catch
        filter_result = output_filter.check_only(text)
        if filter_result:
            results.append(True)
            continue

        # Not caught by validation alone
        results.append(False)

    return compute_asr(results)


def main() -> None:
    repo = Path(__file__).parent.parent.parent
    for ds_name in ["direct_injection", "exfiltration"]:
        ds_path = repo / f"evals/datasets/{ds_name}.jsonl"
        caught_rate = run_validation_eval(ds_path)
        print(
            f"{ds_name}: {caught_rate:.2%} of cases blocked by I/O validation (no live API needed)"
        )
    print("\nNote: This eval uses input pattern matching only — not live agent execution.")
    print("For full defense eval, run make eval-all after building the protected agent.")


if __name__ == "__main__":
    main()
