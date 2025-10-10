# E2E Tests for VCP CLI

This directory contains end-to-end tests for the VCP CLI, focusing on integration with staging environments.

## Setup

1. **Environment Configuration**:
   - Copy `.env.staging.example` to `.env.staging`
   - Fill in the actual staging values (API URLs, Cognito details, admin credentials)
   - Note: `.env.staging` is ignored by git - never commit sensitive credentials!

2. **Dependencies**:
   - Ensure project dependencies are installed: `uv sync --all-groups`
   - Tests use `uv run pytest` to run in the virtual environment

## Running Tests

Run all E2E tests against staging:
```bash
APP_ENV=staging uv run pytest tests/e2e -vs
```

Run a specific test:
```bash
APP_ENV=staging uv run pytest tests/e2e/test_models.py::test_model_list -vs
```

## Test Structure

- `conftest.py`: Sets up environment loading and session-wide fixtures (e.g., authentication)
- `test_models.py`: Tests for model-related commands (e.g., `vcp model list`)

Tests perform real CLI commands via subprocess, with isolated environments for token storage.

## Troubleshooting

- If login fails, verify Cognito credentials and client secret in `.env.staging`
