.PHONY: clean lint format test coverage docs dev-install install build help init-tests init-docs

# Variables
PYTHON := python
PIP := pip
RUFF := ruff
PYTEST := pytest
COVERAGE := coverage
SPHINX_BUILD := sphinx-build

# Project-specific settings
PACKAGE_NAME := dbt_erd
SOURCE_DIR := .
TEST_DIR := tests
DOCS_DIR := docs

# Default target when just running 'make'
all: lint test

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Linting
lint:
	@echo "Checking if directories exist..."
	@if [ ! -d "$(TEST_DIR)" ]; then \
		echo "Test directory $(TEST_DIR) does not exist. Linting just source."; \
		$(RUFF) check $(SOURCE_DIR); \
	else \
		echo "Running linting on source and tests..."; \
		$(RUFF) check $(SOURCE_DIR) $(TEST_DIR); \
	fi

# Auto-fix linting issues where possible
format:
	@echo "Formatting source code..."
	$(RUFF) format $(SOURCE_DIR)
	@if [ -d "$(TEST_DIR)" ]; then \
		echo "Formatting test code..."; \
		$(RUFF) format $(TEST_DIR); \
	fi
	@echo "Applying auto-fixes to linting issues..."
	$(RUFF) check --fix $(SOURCE_DIR)
	@if [ -d "$(TEST_DIR)" ]; then \
		$(RUFF) check --fix $(TEST_DIR); \
	fi

# Run tests
test:
	@if [ ! -d "$(TEST_DIR)" ]; then \
		echo "Warning: Test directory $(TEST_DIR) not found. Run 'make init-tests' first."; \
	else \
		$(PYTEST) $(TEST_DIR); \
	fi

# Run tests with coverage
coverage:
	@if [ ! -d "$(TEST_DIR)" ]; then \
		echo "Warning: Test directory $(TEST_DIR) not found. Run 'make init-tests' first."; \
	else \
		$(COVERAGE) run -m pytest $(TEST_DIR); \
		$(COVERAGE) report; \
		$(COVERAGE) html; \
	fi

# Create skeleton for tests
init-tests:
	@if [ ! -d "$(TEST_DIR)" ]; then \
		mkdir -p $(TEST_DIR); \
		mkdir -p $(TEST_DIR)/data/models; \
		touch $(TEST_DIR)/__init__.py; \
		touch $(TEST_DIR)/data/__init__.py; \
		echo "Created test directory structure"; \
		$(PYTHON) -c "import os, shutil; \
			src_dir = '$(TEST_DIR)'; \
			if not os.path.exists(os.path.join(src_dir, 'conftest.py')): \
				print('Creating basic conftest.py file'); \
				with open(os.path.join(src_dir, 'conftest.py'), 'w') as f: \
					f.write('\"\"\"Pytest configuration file for $(PACKAGE_NAME) tests.\"\"\"\\n\\nimport pytest\\n\\n@pytest.fixture\\ndef sample_config():\\n    \"\"\"Return a sample configuration.\"\"\"\\n    return {\\n        \"naming\": {\\n            \"dimension_patterns\": [\"dim_\"],\\n            \"fact_patterns\": [\"fact_\"],\\n        }\\n    }\\n')"; \
		echo "Run 'make install-test-deps' to install test dependencies"; \
	else \
		echo "Test directory already exists"; \
	fi

# Install test dependencies
install-test-deps:
	$(PIP) install pytest pytest-cov

# Create skeleton for documentation
init-docs:
	@if [ ! -d "$(DOCS_DIR)" ]; then \
		mkdir -p $(DOCS_DIR); \
		echo "Created docs directory. Run 'cd $(DOCS_DIR) && sphinx-quickstart' to initialize Sphinx docs."; \
	else \
		echo "Docs directory already exists"; \
	fi

# Build documentation
docs:
	@if [ ! -d "$(DOCS_DIR)" ]; then \
		echo "Warning: Docs directory $(DOCS_DIR) not found. Run 'make init-docs' first."; \
	elif [ ! -f "$(DOCS_DIR)/Makefile" ]; then \
		echo "Warning: Sphinx not initialized in $(DOCS_DIR). Run 'cd $(DOCS_DIR) && sphinx-quickstart' first."; \
	else \
		cd $(DOCS_DIR) && make html; \
	fi

# Install development dependencies
dev-install:
	$(PIP) install -e ".[dev]"

# Install the package
install:
	$(PIP) install -e .

# Build distribution packages
build: clean
	$(PYTHON) -m build

# Version operations
bump-patch:
	$(PYTHON) -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); \
	v = c['metadata']['version'].split('.'); v[-1] = str(int(v[-1]) + 1); \
	c['metadata']['version'] = '.'.join(v); f = open('setup.cfg', 'w'); c.write(f); f.close(); \
	print(f\"Version bumped to {c['metadata']['version']}\")"

bump-minor:
	$(PYTHON) -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); \
	v = c['metadata']['version'].split('.'); v[1] = str(int(v[1]) + 1); v[2] = '0'; \
	c['metadata']['version'] = '.'.join(v); f = open('setup.cfg', 'w'); c.write(f); f.close(); \
	print(f\"Version bumped to {c['metadata']['version']}\")"

bump-major:
	$(PYTHON) -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); \
	v = c['metadata']['version'].split('.'); v[0] = str(int(v[0]) + 1); v[1] = '0'; v[2] = '0'; \
	c['metadata']['version'] = '.'.join(v); f = open('setup.cfg', 'w'); c.write(f); f.close(); \
	print(f\"Version bumped to {c['metadata']['version']}\")"

# Help command to display available commands
help:
	@echo "Available commands:"
	@echo "  make clean            - Clean up build artifacts"
	@echo "  make lint             - Check code style with Ruff"
	@echo "  make format           - Auto-format code using Ruff"
	@echo "  make test             - Run tests"
	@echo "  make coverage         - Run tests with coverage report"
	@echo "  make init-tests       - Create initial test directory structure"
	@echo "  make install-test-deps - Install test dependencies"
	@echo "  make init-docs        - Create initial docs directory"
	@echo "  make docs             - Build documentation"
	@echo "  make dev-install      - Install package in development mode with dev dependencies"
	@echo "  make install          - Install the package in development mode"
	@echo "  make build            - Build distribution packages"
	@echo "  make bump-patch       - Bump patch version (0.0.x)"
	@echo "  make bump-minor       - Bump minor version (0.x.0)"
	@echo "  make bump-major       - Bump major version (x.0.0)"