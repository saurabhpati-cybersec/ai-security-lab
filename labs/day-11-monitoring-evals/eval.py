#!/usr/bin/env python3
"""Day 11 eval: verify monitoring pipeline — smoketest + log schema check."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    repo = Path(__file__).parent.parent.parent

    result = subprocess.run(
        [sys.executable, str(repo / "evals/harness/smoketest.py")],
        capture_output=True,
        text=True,
    )
    if "Smoketest PASSED" in result.stdout:
        print("PASS: eval harness smoketest")
    else:
        print("FAIL: smoketest")
        print(result.stdout)
        sys.exit(1)

    result2 = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; sys.path.insert(0, '.');"
                "from starter.python.log_schema import LogEvent, make_event;"
                "e = make_event(agent_id='test', session_id='s1', step=0,"
                " event_type='model_call', model='test');"
                "print('log schema OK:', e.event_type)"
            ),
        ],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    if "log schema OK" in result2.stdout:
        print("PASS: canonical log schema")
    else:
        print("FAIL: log schema")
        print(result2.stderr)
        sys.exit(1)

    print("\nDay 11 eval: PASS")
    print("For full monitoring eval, run the protected agent against attack datasets")
    print("and check that detector_hit events appear in evals/results/*/cases.jsonl")


if __name__ == "__main__":
    main()
