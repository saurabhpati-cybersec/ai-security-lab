.PHONY: setup test eval eval-all clean

setup:
	pip install -r requirements.txt

test:
	pytest

eval:
	@echo "Not yet implemented"

eval-all:
	@echo "Not yet implemented"

clean:
	find . -name __pycache__ -exec rm -rf {} +
