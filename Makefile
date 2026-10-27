PYTHON := python3
SRC_DIR := src
MAIN := $(SRC_DIR)/main.py
MAP ?= maps/easy/01_linear_path.txt
VENV := venv
MAP_ARG = $(filter-out $@,$(MAKECMDGOALS))
CURRENT_MAP = $(if $(MAP_ARG),$(MAP_ARG),$(MAP))

.PHONY: install run run-map debug clean lint lint-strict help venv

all: lint run

help:
	@echo "Fly-in Project - Available targets:"
	@echo "  make install            - Install project dependencies"
	@echo "  make run                - Run with default map (easy/01_linear_path.txt)"
	@echo "  make run-map MAP=<file> - Run with specific map"
	@echo "  make debug              - Run in debug mode with pdb"
	@echo "  make clean              - Remove temporary files and caches"
	@echo "  make lint               - Run flake8 and mypy linters"
	@echo "  make lint-strict        - Run mypy with strict mode"
	@echo "  make venv               - Create virtual environment (optional)"

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Run: source $(VENV)/bin/activate"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	PYTHONPATH=. $(PYTHON) $(MAIN) $(MAP)

run-map:
	@echo "A executar o mapa: $(CURRENT_MAP)"
	PYTHONPATH=. $(PYTHON) $(MAIN) $(CURRENT_MAP)

%:
	@:

debug:
	PYTHONPATH=. $(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	@echo "✓ Cleanup complete."

lint:
	@echo "Running flake8..."
	flake8 $(SRC_DIR)
	@echo "Running mypy..."
	mypy $(SRC_DIR) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@echo "✓ All checks passed!"

lint-strict:
	@echo "Running strict mode..."
	flake8 $(SRC_DIR)
	mypy $(SRC_DIR) --strict
	@echo "✓ All strict checks passed!"
