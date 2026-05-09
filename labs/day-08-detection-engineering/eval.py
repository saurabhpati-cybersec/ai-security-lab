#!/usr/bin/env python3
"""Day 8 eval: run detector eval and print TPR/FPR."""
import subprocess
import sys
from pathlib import Path


def main():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "defense/detector_eval.py")],
        capture_output=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
