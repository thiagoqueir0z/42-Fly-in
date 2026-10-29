PYTHON := python3
SRC_DIR := src
MAIN := $(SRC_DIR)/main.py
MAP ?= maps/easy/01_linear_path.txt
VENV := venv

.PHONY: venv install run debug clean clean-venv fclean lint lint-strict re

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Run: source $(VENV)/bin/activate"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	PYTHONPATH=. $(PYTHON) $(MAIN) $(MAP)

debug:
	PYTHONPATH=. $(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	@echo "✓ Temporary files and caches removed."

clean-venv:
	rm -rf $(VENV)
	@echo "✓ Virtual environment '$(VENV)' removed."

fclean: clean clean-venv

re: fclean venv install run

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