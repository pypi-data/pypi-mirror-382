# Data Command E2E Tests

End-to-end tests for VCP CLI data commands.

## Test Coverage

### `test_data_search.py`
- Basic search functionality
- Search with limit parameter
- JSON output format
- Exact match searching
- Handling of no results

### `test_data_describe.py`
- Invalid dataset ID validation
- Nonexistent dataset handling
- JSON output format (prod only)
- Raw output format (prod only)

### `test_data_summary.py`
- Summary by various fields (organism, tissue, disease)
- Summary with search query filter
- Invalid field validation

### `test_data_download.py`
- Validation of required --id or --query parameters
- Helpful error for old positional syntax
- Invalid dataset ID validation
- Nonexistent dataset handling
- Download by ID (prod only)

## Running Tests

Run all data E2E tests:
```bash
APP_ENV=staging uv run pytest tests/e2e/data -vs  # Run against staging
APP_ENV=prod uv run pytest tests/e2e/data -vs     # Run against prod
```

Run specific test file:
```bash
APP_ENV=staging uv run pytest tests/e2e/data/test_data_search.py -vs
```

Run specific test:
```bash
APP_ENV=staging uv run pytest tests/e2e/data/test_data_search.py::TestDataSearch::test_search_basic -vs
```

## Notes

- Tests require environment-specific configuration in `tests/e2e/.env.staging` or `tests/e2e/.env.prod`
- Tests marked with `@pytest.mark.prod_only` use real dataset IDs and only run when `APP_ENV=prod`
- Tests use the `session_auth` fixture from `tests/e2e/conftest.py` for authentication
