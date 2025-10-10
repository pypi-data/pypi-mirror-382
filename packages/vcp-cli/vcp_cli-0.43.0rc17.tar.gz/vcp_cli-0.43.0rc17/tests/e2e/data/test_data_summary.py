import subprocess

import pytest

from tests.e2e.data.base_data_test import BaseDataTest


class TestDataSummary(BaseDataTest):
    """E2E tests for vcp data summary command."""

    @pytest.mark.e2e
    def test_summary_organism(self, session_auth):
        """Test summary for organism field."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "summary", "organism"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data summary organism")
        self.assert_no_errors(result)
        self.assert_no_traceback(result)

        # Should contain table with counts
        assert "Value" in result.stdout or "Count" in result.stdout

    @pytest.mark.e2e
    def test_summary_tissue(self, session_auth):
        """Test summary for tissue field."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "summary", "tissue"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data summary tissue")
        self.assert_no_errors(result)

    @pytest.mark.e2e
    def test_summary_with_search_term(self, session_auth):
        """Test summary with search query filter."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "summary", "organism", "--query", "human"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data summary with query")
        self.assert_no_errors(result)

    @pytest.mark.e2e
    def test_summary_invalid_field(self, session_auth):
        """Test summary with invalid field name."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "summary", "invalid_field_xyz"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        # Should fail with validation error
        assert result.returncode != 0
        assert "not supported" in result.stdout or "not a valid" in result.stdout

    @pytest.mark.e2e
    def test_summary_disease(self, session_auth):
        """Test summary for disease field."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "summary", "disease"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data summary disease")
        self.assert_no_errors(result)
