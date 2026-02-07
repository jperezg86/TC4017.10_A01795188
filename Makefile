.PHONY: help install lint format test clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install development dependencies"
	@echo "  make lint       - Run all linters (pylint, flake8)"
	@echo "  make format     - Format code with black and isort"
	@echo "  make test       - Run tests with pytest"
	@echo "  make clean      - Remove generated files"

install:
	pip install -r requirements-dev.txt

lint:
	@echo "Running pylint..."
	find . -type f -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./build/*" -not -path "./dist/*" | xargs pylint
	@echo "\nRunning flake8..."
	flake8 .
	@echo "\nRunning mypy..."
	mypy .

format:
	@echo "Running isort..."
	isort .
	@echo "Running black..."
	black --line-length 79 .

format-check:
	@echo "Checking isort..."
	isort --check-only .
	@echo "Checking black..."
	black --check --line-length 79 .

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
