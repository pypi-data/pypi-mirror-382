import subprocess

import pytest

from tests.e2e.data.base_data_test import BaseDataTest


class TestDataDescribe(BaseDataTest):
    """E2E tests for vcp data describe command."""

    @pytest.mark.e2e
    def test_describe_invalid_dataset_id(self, session_auth):
        """Test describe with an invalid dataset ID."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "describe", "invalid-id-123"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        # Should fail with validation error
        assert result.returncode != 0
        assert (
            "Invalid dataset ID" in result.stdout
            or "not a valid format" in result.stdout
        )

    @pytest.mark.e2e
    def test_describe_nonexistent_dataset(self, session_auth):
        """Test describe with a valid format but nonexistent dataset ID."""
        app_env, _ = session_auth

        # Use a valid format ID that doesn't exist
        fake_id = "00000000-0000-0000-0000-000000000000"
        result = subprocess.run(
            ["uv", "run", "vcp", "data", "describe", fake_id],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        # Should fail with server error (API returns 500 for nonexistent datasets)
        assert result.returncode != 0
        assert "error" in result.stdout.lower()

    @pytest.mark.e2e
    @pytest.mark.prod_only
    def test_describe_with_full(self, session_auth):
        """Test describe with --full flag (JSON output)."""
        app_env, _ = session_auth

        # Use a known dataset ID from prod
        dataset_id = "68db37283df7e0a925f37797"

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "describe", dataset_id, "--full"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data describe --full")
        self.assert_no_errors(result)

        # Validate JSON structure
        data = self.assert_json_valid(result)
        self.assert_contains_dataset_fields(data)

    @pytest.mark.e2e
    @pytest.mark.prod_only
    def test_describe_with_raw(self, session_auth):
        """Test describe with --raw flag."""
        app_env, _ = session_auth

        # Use a known dataset ID from prod
        dataset_id = "68db37283df7e0a925f37797"

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "describe", dataset_id, "--raw"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data describe --raw")
        self.assert_no_errors(result)
        # Raw format should contain JSON-like structure
        assert "{" in result.stdout and "}" in result.stdout
