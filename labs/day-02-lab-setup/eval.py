#!/usr/bin/env python3
"""Day 2 eval: verify environment setup."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def check_smoketest() -> bool:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "evals/harness/smoketest.py")],
        capture_output=True, text=True
    )
    if "Smoketest PASSED" in result.stdout:
        print("PASS: smoketest")
        return True
    print(f"FAIL: smoketest\n{result.stdout}\n{result.stderr}")
    return False


def check_imports() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, '.'); "
             "from agents.vulnerable.agent import VulnerableAgent; "
             "from starter.python.log_schema import LogEvent; "
             "from evals.harness.runner import run_eval, evaluate_criteria; "
             "print('imports OK')"],
            cwd=str(REPO_ROOT), capture_output=True, text=True
        )
        if "imports OK" in result.stdout:
            print("PASS: all critical imports")
            return True
        print(f"FAIL: imports\n{result.stdout}\n{result.stderr}")
        return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def check_datasets() -> bool:
    datasets = list((REPO_ROOT / "evals/datasets").glob("*.jsonl"))
    if len(datasets) >= 6:
        print(f"PASS: {len(datasets)} datasets found")
        return True
    print(f"FAIL: only {len(datasets)} datasets (need 6)")
    return False


if __name__ == "__main__":
    checks = [check_smoketest(), check_imports(), check_datasets()]
    sys.exit(0 if all(checks) else 1)
