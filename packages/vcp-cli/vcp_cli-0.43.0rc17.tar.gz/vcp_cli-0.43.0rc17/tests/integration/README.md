# Integration Tests

This directory contains integration tests for the VCP CLI that test real-world scenarios with actual network operations and external services.

## Test Categories

### GitHub Operations (`test_github_operations.py`)
Tests real GitHub operations including:
- Repository cloning with authentication
- Token-based authentication flows
- Temp directory fallback scenarios
- Network failure handling
- Concurrent operations
- Environment cleanup

### Model Init Workflow (`test_model_init_workflow.py`)
Tests the complete model initialization workflow including:
- New model creation
- Existing model handling
- Work directory creation
- API failure handling
- Interactive mode
- Metadata validation

## Running Integration Tests

### Prerequisites
- Network access to GitHub
- Valid authentication tokens (if testing authenticated operations)
- Write permissions in temp directories

### Commands
```bash
# Run all integration tests
make test-integration

# Run specific test file
uv run pytest tests/integration/test_github_operations.py -v

# Run with network timeout
uv run pytest tests/integration/ --timeout=300
```

### Test Repositories
The tests use these repositories:
- `octocat/Hello-World` - Small, fast repository for basic tests
- `chanzuckerberg/vcp-cli` - Real-world repository for comprehensive tests
- `cz-model-contributions/vcp-cli-integration-test-do-not-delete` - Dedicated test repository

## Test Environment Considerations

### Network Dependencies
- Tests require internet connectivity
- GitHub API rate limits may apply
- Some tests may be slower due to network latency

### Authentication
- Tests use mock authentication by default
- Real authentication tests require valid tokens
- Token expiration scenarios are tested

### Temp Directory Handling
- Tests create temporary directories for isolation
- Fallback mechanisms are tested for different environments
- Permission scenarios are simulated

## Debugging Integration Tests

### Verbose Output
```bash
uv run pytest tests/integration/ -v -s
```

### Specific Test
```bash
uv run pytest tests/integration/test_github_operations.py::TestGitHubOperationsIntegration::test_clone_small_repo_fast -v
```

### Network Issues
If tests fail due to network issues:
1. Check internet connectivity
2. Verify GitHub is accessible
3. Check for firewall/proxy issues
4. Consider running tests in a different environment

## Adding New Integration Tests

### Guidelines
1. Use real repositories when possible
2. Test both success and failure scenarios
3. Include proper cleanup in teardown
4. Mock only when necessary for isolation
5. Test edge cases and error conditions

### Example Test Structure
```python
def test_new_integration_scenario(self, temp_work_dir):
    """Test description of what this test validates."""
    # Setup
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test execution
        result = some_operation()
        
        # Assertions
        assert result is not None
        assert os.path.exists(expected_path)
```

## CI/CD Considerations

Integration tests are excluded from the default test suite because they:
- Require network access
- May be slower than unit tests
- Can be flaky due to external dependencies
- Need special environment setup

They should be run:
- Before major releases
- In dedicated CI environments
- With proper network access
- With appropriate timeouts
