.PHONY: help setup install dev test test-model lint format clean build generate-config generate-config-test

# Required files
CONFIG_EXAMPLE := config.yaml.example

# Default target
help:
	@echo "Available commands:"
	@echo "  make help      - Show this help message"
	@echo "  make setup     - Initial setup (install deps, create config)"
	@echo "  make install   - Install dependencies using uv"
	@echo "  make generate-config-test - Generate test config"
	@echo "  make generate-config - Generate production config"
	@echo "  make build     - Build the package"
	@echo "  make test      - Run tests (excludes E2E and integration)"
	@echo "  make test-model - Run all model-related tests (unit + integration)"
	@echo "  make test-integration - Run integration tests (requires network)"
	@echo "  make test-e2e  - Run E2E tests (requires APP_ENV)"
	@echo "  make test-all  - Run all tests including E2E (requires APP_ENV)"
	@echo "  make test-all-with-integration - Run all tests including integration"
	@echo "  make lint      - Run linting checks"
	@echo "  make lint-fix  - Format code and fix linting issues"
	@echo "  make clean     - Clean up build artifacts"
	@echo "  make dev       - Run the CLI in development mode"
	@echo "  make docs      - Build documentation"

# Initial setup
setup: install
	@echo "Creating default config..."
	@mkdir -p ~/.vcp
	@if [ ! -f ~/.vcp/config.yaml ]; then \
		cp $(CONFIG_EXAMPLE) ~/.vcp/config.yaml; \
		echo "Created default config at ~/.vcp/config.yaml"; \
	else \
		echo "Config already exists at ~/.vcp/config.yaml"; \
	fi

# Install dependencies with uv
install:
	@echo "Installing dependencies with uv..."
	uv sync --all-groups

# Generate test configuration
generate-config-test:
	@echo "Generating test config..."
	uv run python ci/generate_config.py --mode test

# Generate production configuration
generate-config:
	@echo "Generating config..."
	uv run python ci/generate_config.py

# Build the package
build:
	@echo "Building package..."
	uv build

# Run tests
# FIXME: We should only need the -m 'not integration' -m 'not e2e' markers, but apparently not all tests are marked correctly yet.
test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/ --ignore=tests/e2e --ignore=tests/integration -m 'not integration' -m 'not e2e' -v

# Alias of test-unit
test: test-unit

# Run all model-related tests (unit + integration)
test-model:
	@echo "Running all model-related tests..."
	@echo "This includes unit tests and integration tests for model commands"
	uv run pytest tests/test_github_auth_token_caching.py tests/test_github_auth_integration.py tests/test_model_init.py tests/test_workflow_assistant.py tests/integration/ -v

# Run integration tests (requires network access)
test-integration:
	@echo "Running integration tests..."
	@echo "Note: These tests require network access and may take longer"
	uv run pytest tests/integration -v

# Run E2E tests (requires APP_ENV)
test-e2e:
	@echo "Running E2E tests..."
	@if [ -z "$(APP_ENV)" ]; then \
		echo "Error: APP_ENV is required for E2E tests"; \
		echo "Example: APP_ENV=staging make test-e2e"; \
		exit 1; \
	fi
	uv run pytest tests/e2e

# Run all tests including E2E (requires APP_ENV)
test-all:
	@echo "Running all tests including E2E..."
	@if [ -z "$(APP_ENV)" ]; then \
		echo "Error: APP_ENV is required for E2E tests"; \
		echo "Example: APP_ENV=staging make test-all"; \
		exit 1; \
	fi
	uv run pytest tests/

# Run all tests including integration tests (requires network access)
test-all-with-integration:
	@echo "Running all tests including integration tests..."
	@echo "Note: This includes network-dependent tests"
	uv run pytest tests/ --ignore=tests/e2e

# Test dist packages
test-dist:
	@echo "Testing distribution packages..."
	./tests/test-dist.sh

# Run linting checks
lint:
	@echo "Running formatting and static analysis checks..."
	uv run ruff check
	uv run ruff format --check

# Format and fix code. Use pre-commit to match what GHA checks use.
lint-fix:
	@echo "Formatting and fixing static analysis violations..."
	uv run pre-commit run --all-files

# Clean up build artifacts
clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	(cd docs && uv run make clean)

# Development mode
dev: install
	@echo "Running in development mode..."
	uv run python -m vcp --help

# Build docs
docs: install
	@echo "Building documentation..."
	(cd docs && uv run make html)
