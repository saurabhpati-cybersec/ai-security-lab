"""Repo-relative paths used across the webapp."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEBAPP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = WEBAPP_DIR / "templates"
STATIC_DIR = WEBAPP_DIR / "static"

ENV_FILE = REPO_ROOT / ".env"
DATASETS_DIR = REPO_ROOT / "evals" / "datasets"
RESULTS_DIR = REPO_ROOT / "evals" / "results"
SUMMARY_FILE = RESULTS_DIR / "latest_summary.md"
LABS_DIR = REPO_ROOT / "labs"
CORPUS_DIR = REPO_ROOT / "agents" / "reference" / "corpus"
OUTBOX_FILE = REPO_ROOT / "agents" / "reference" / "outbox.jsonl"
