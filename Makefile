.PHONY: install run debug clean lint lint-strict help

help:
	@echo "Available targets:"
	@echo "  make install      - Install project dependencies"
	@echo "  make run          - Run the main script"
	@echo "  make debug        - Run in debug mode with pdb"
	@echo "  make clean        - Remove temporary files and caches"
	@echo "  make lint         - Run flake8 and mypy linters"
	@echo "  make lint-strict  - Run mypy with strict mode"

install:
	pip install -r requirements.txt

run:
	python3 src/main.py

debug:
	python3 -m pdb src/main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
