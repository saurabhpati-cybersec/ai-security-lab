#!/usr/bin/env python3
"""Day 1 eval: verify threat model completeness."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
THREAT_MODEL = REPO_ROOT / "docs/threat-model.md"


def check_threat_model() -> bool:
    if not THREAT_MODEL.exists():
        print("FAIL: docs/threat-model.md not found")
        return False
    content = THREAT_MODEL.read_text()
    # Count threat rows: lines starting with "| T-"
    threat_rows = [l for l in content.splitlines() if l.strip().startswith("| T-")]
    if len(threat_rows) < 15:
        print(f"FAIL: only {len(threat_rows)} threats found, need 15+")
        return False
    # Check trifecta matrix present
    if "Trifecta" not in content:
        print("FAIL: trifecta matrix section not found")
        return False
    print(f"PASS: {len(threat_rows)} threats tagged with STRIDE/OWASP/trifecta")
    return True


if __name__ == "__main__":
    sys.exit(0 if check_threat_model() else 1)
