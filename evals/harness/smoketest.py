"""Backwards-compatible shim that delegates to the pytest suite.

The tests previously expressed here have moved to ``tests/`` so they can be
collected by pytest and surfaced module-by-module in the GUI. This script
remains so existing instructions like ``python3 evals/harness/smoketest.py``
keep working.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=_REPO_ROOT,
    )
    if result.returncode == 0:
        print("\nSmoketest PASSED")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
