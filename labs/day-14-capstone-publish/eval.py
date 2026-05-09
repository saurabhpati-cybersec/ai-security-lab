#!/usr/bin/env python3
"""Day 14 eval: verify portfolio completeness."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent

REQUIRED_FILES = [
    "README.md",
    "docs/threat-model.md",
    "docs/00-honest-assessment.md",
    "docs/ai-agent-security-checklist.md",
    "docs/glossary.md",
    "docs/references.md",
    "agents/vulnerable/agent.py",
    "agents/protected/agent.py",
    "evals/harness/runner.py",
    "evals/harness/smoketest.py",
    "detectors/rules.py",
    "detectors/classifier.py",
    "detectors/output_filter.py",
    "soar-companion/shared/log-schema.md",
    "soar-companion/shared/alert-catalog.md",
    "labs/day-14-capstone-publish/defense/demo_script.md",
    "labs/day-14-capstone-publish/defense/blog_outlines.md",
    "labs/day-14-capstone-publish/defense/talk_abstract.md",
]

REQUIRED_DIRS = [
    "evals/datasets",
    "labs/day-03-direct-injection",
    "labs/day-08-detection-engineering",
    "soar-companion/tines",
    "soar-companion/xsoar",
]


def check_files() -> bool:
    missing = [f for f in REQUIRED_FILES if not (REPO / f).exists()]
    if missing:
        print("Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False
    print(f"PASS: all {len(REQUIRED_FILES)} required files present")
    return True


def check_dirs() -> bool:
    missing = [d for d in REQUIRED_DIRS if not (REPO / d).is_dir()]
    if missing:
        print("Missing directories:")
        for d in missing:
            print(f"  - {d}")
        return False
    print(f"PASS: all {len(REQUIRED_DIRS)} required directories present")
    return True


def check_readme_length() -> bool:
    readme = (REPO / "README.md").read_text()
    word_count = len(readme.split())
    if word_count < 500:
        print(f"WARN: README is only {word_count} words (target 600-900)")
        return False
    print(f"PASS: README is {word_count} words")
    return True


def main() -> None:
    results = [check_files(), check_dirs(), check_readme_length()]
    if all(results):
        print("\nDay 14 eval: PASS — portfolio complete")
        sys.exit(0)
    else:
        print("\nDay 14 eval: PARTIAL — some items missing (see above)")
        sys.exit(1)


if __name__ == "__main__":
    main()
