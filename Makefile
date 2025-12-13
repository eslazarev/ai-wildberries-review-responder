.PHONY: help ci lint format black mypy pylint bandit radon test

PYTHON ?= python
PYTEST ?= pytest
PYTHONPATH ?= $(CURDIR)

help:
	@echo "Targets:"
	@echo "  make ci       - run lint + tests (like CI)"
	@echo "  make lint     - run black/mypy/pylint/bandit/radon"
	@echo "  make format   - run black (format code)"
	@echo "  make test     - run pytest with coverage.json"

ci: lint test

lint: black mypy pylint bandit radon

format:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m black . -l 120

black:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m black . -l 120 --check

mypy:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m mypy --install-types --non-interactive --explicit-package-bases .

pylint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pylint src

bandit:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m bandit -r src

radon:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m radon mi src tests -s

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTEST) --cov=src --cov-report=term --cov-report=json:coverage.json
