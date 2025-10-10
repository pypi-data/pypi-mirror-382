# Development

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/chanzuckerberg/vcp-cli.git
   cd vcp-cli
   ```

2. Install development dependencies:
   ```bash
   make setup
   ```

   This will:
   - Install all dependencies using uv
   - Create a default config file at `~/.vcp/config.yaml`

   Alternatively, you can run individual steps:
   ```bash
   uv sync --all-groups  # Install dependencies
   ```

## Commands

Available development commands:
   ```
  make help      - Show this help message
  make setup     - Initial setup (install deps, create config)
  make install   - Install dependencies using uv
  make generate-config-test - Generate test config
  make generate-config - Generate production config
  make build     - Build the package
  make test      - Run tests (excludes E2E and integration)
  make test-model - Run all model-related tests (unit + integration)
  make test-integration - Run integration tests (requires network)
  make test-e2e  - Run E2E tests (requires APP_ENV)
  make test-all  - Run all tests including E2E (requires APP_ENV)
  make test-all-with-integration - Run all tests including integration
  make lint      - Run linting checks
  make lint-fix  - Format code and fix linting issues
  make clean     - Clean up build artifacts
  make dev       - Run the CLI in development mode
  make docs      - Build documentation
   ```

## CLI Usage

To run the CLI:
* Option 1: `make dev --help`
* Option 2: `uv run vcp --help`
