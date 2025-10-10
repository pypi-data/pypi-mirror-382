# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VCP CLI is a command-line interface for interacting with the VCP (Virtual Cells Platform) service. It's built in Python using Click for CLI framework, Rich for terminal output, and includes OAuth2 authentication with AWS Cognito.

## Development Commands

### Setup and Installation
```bash
make setup          # Complete setup: install deps + create default config
make install        # Install dependencies only (uv sync --all-groups)
```

### Testing and Code Quality
```bash
make test           # Run tests with pytest
make lint           # Run linting checks (ruff check + format --check)
make format         # Format code with ruff
uv run pytest      # Run specific tests
```

### Build and Development
```bash
make build          # Build package (uv build)
make dev            # Run CLI in development mode
make clean          # Clean build artifacts
```

### Configuration Generation
```bash
make generate-config        # Generate production config
make generate-config-test   # Generate test config
```

## Code Architecture

### Package Structure
- `src/vcp/` - Main package directory
- `src/vcp/cli.py` - Main CLI entry point using Click groups
- `src/vcp/commands/` - All CLI command implementations organized by domain:
  - `auth/` - Authentication (login, logout)
  - `model/` - Model operations (list, download, submit, stage, init)
  - `data/` - Data operations (search, describe, download)
  - `benchmarks/` - Benchmark operations (list, get, run)
  - `config.py`, `version.py`, `cache.py` - Utility commands
- `src/vcp/config/` - Configuration management
- `src/vcp/auth/` - OAuth2 authentication with AWS Cognito
- `src/vcp/datasets/` - Dataset download and API interactions
- `src/vcp/utils/` - Shared utilities (encryption, caching, version checking)

### Key Patterns
- Commands are organized into Click groups (model, data, benchmarks)
- Configuration management supports multiple file locations (~/.vcp/config.yaml, ./config.yaml, etc.)
- Token encryption and secure credential storage
- Automatic version update checking with caching
- Rich console output for user-friendly messaging
- SQLite-based download candidate management with resume functionality
- Parallel downloads with optimized credential fetching

### Authentication Flow
- OAuth2 with AWS Cognito integration
- Encrypted token storage using cryptography library
- Browser-based authentication flow with local callback server
- Support for direct username/password authentication

### Configuration System
The CLI uses YAML configuration files with this hierarchy:
1. `~/.vcp/config.yaml` (default location)
2. `./config.yaml` (current directory)
3. Custom path via `--config` flag

### Download System Architecture
The data download functionality (`vcp data search --download`) uses an advanced SQLite-based system:

#### Key Features
- **SQLite Candidate Database**: `~/.vcp/downloads/candidates_*.db` stores download targets with query metadata and expiration
- **Resume Functionality**: Interrupted downloads can be resumed by matching query signatures
- **Parallel Downloads**: ThreadPoolExecutor with configurable concurrency (default: 5 datasets)
- **Optimized Credential Fetching**: S3 credentials only requested when datasets contain S3 locations
- **Individual Dataset Credentials**: Each dataset gets separate credentials due to AWS policy size limitations
- **Atomic Transactions**: Candidate collection uses transactions with rollback on interruption

#### Core Components
- `DownloadDatabase` (`src/vcp/datasets/download_db.py`): SQLite management for candidates
- `download_from_candidates_db()` (`src/vcp/datasets/download.py`): Parallel download orchestration
- `get_credentials_for_datasets()` (`src/vcp/datasets/api.py`): Batch credential fetching API
- Database expiration cleanup and query matching for resume functionality

#### Download Flow
1. Check for existing non-expired candidate database matching the query
2. If none found, exhaust all search API pages and atomically store candidates
3. Group candidates by dataset ID and process in parallel
4. Fetch credentials only for datasets with S3 locations
5. Download all files for each dataset, marking candidates as completed
6. Support CTRL-C interruption with graceful shutdown

## Dependencies and Tools

### Package Management
- **uv** - Fast Python package installer and resolver (primary tool)
- Python 3.10+ required

### Key Dependencies
- Click 8.0+ for CLI framework
- Rich 10.0+ for terminal output
- PyYAML for configuration
- Requests for HTTP calls
- Cryptography for token encryption
- Authlib + Werkzeug for OAuth2
- Boto3 for AWS services
- MLflow 2.0+ for model operations
- Pydantic 2.0+ for data validation

### Code Quality Tools
- **ruff** - Linting and formatting (replaces flake8, black, isort)
- **mypy** - Type checking with strict settings
- **pytest** - Testing framework
- **pre-commit** - Git hooks with ruff

## Testing

### Test Structure
- `tests/` directory with pytest-based tests
- `conftest.py` - Shared test fixtures and configuration
- Tests cover CLI commands, configuration, and version checking
- Tests are written in Pytest style, taking advantage of its ability to
  generate rich failure messages from high-level asserts

### Running Tests

```bash
make test                    # Run all tests
uv run pytest              # Run with uv
uv run pytest tests/test_*.py  # Run specific test files
```

## Build and Release

### Package Building
- Uses **hatchling** build backend with hatch-vcs for version management
- Wheel packages built with `make build` or `uv build`
- Main entry point: `vcp = "vcp.cli:cli"`

### Release Process
- Automated with release-please
- Version bumps tracked in `.release-please-manifest.json`
- Changelog automatically generated in `CHANGELOG.md`
