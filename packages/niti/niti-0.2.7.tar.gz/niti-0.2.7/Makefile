.PHONY: help format format-check lint test clean install install-dev check-all

# Default target
help:
	@echo "Available targets:"
	@echo "  format      - Format code with autoflake, black, and isort"
	@echo "  lint        - Run linting with flake8 and mypy"
	@echo "  test        - Run tests with pytest"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  install     - Install package in editable mode"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  clean       - Remove build artifacts and cache files"

# Formatting rules
format:
	@echo "Running autoflake to remove unused imports and variables..."
	autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --in-place --recursive --exclude="__init__.py" niti/ test/
	@echo "Running black to format code..."
	black niti/ test/
	@echo "Running isort to sort imports..."
	isort niti/ test/
	@echo "Formatting complete!"

# Linting rules
lint:
	@echo "Running flake8 linting..."
	flake8 niti/ test/
	@echo "Running mypy type checking..."
	mypy niti/
	@echo "Linting complete!"

# Testing rules
test:
	@echo "Running tests..."
	pytest

test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=niti --cov-report=html --cov-report=term-missing
# Installation rules
install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Cleanup
clean:
	@echo "Cleaning up build artifacts and cache files..."
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf test_reports/
	@echo "Cleanup complete!" 