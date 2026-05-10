.PHONY: setup test eval eval-all clean

setup:
	pip install -r requirements.txt

test:
	python3 evals/harness/smoketest.py

eval:
	@echo "Usage: make eval DATASET=direct_injection AGENT=vulnerable"
	@echo "Or run directly: python3 evals/harness/runner.py"

eval-all:
	python3 scripts/eval_all.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
