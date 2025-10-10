import subprocess

import pytest

from tests.e2e.data.base_data_test import BaseDataTest


class TestDataSearch(BaseDataTest):
    """E2E tests for vcp data search command."""

    @pytest.mark.e2e
    def test_search_basic(self, session_auth):
        """Test basic search functionality."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "search", "human"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data search")
        self.assert_no_errors(result)
        self.assert_no_traceback(result)

        # Should contain table headers
        assert "Dataset ID" in result.stdout or "Internal ID" in result.stdout
        assert "Name" in result.stdout

    @pytest.mark.e2e
    def test_search_with_exact(self, session_auth):
        """Test search with exact match parameter."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "search", "Homo sapiens", "--exact"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data search --exact")
        self.assert_no_errors(result)

    @pytest.mark.e2e
    def test_search_with_full_details(self, session_auth):
        """Test search with full details flag."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "search", "human", "--full"],
            env=app_env,
            capture_output=True,
            text=True,
            input="q\n",  # Quit pagination if prompted
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data search --full")
        self.assert_no_errors(result)

    @pytest.mark.e2e
    def test_search_no_results(self, session_auth):
        """Test search with query that returns no results."""
        app_env, _ = session_auth

        result = subprocess.run(
            [
                "uv",
                "run",
                "vcp",
                "data",
                "search",
                "nonexistent_dataset_query_12345",
            ],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        self.assert_successful_command(result, "data search (no results)")
        # Should indicate no results found
        assert (
            "No datasets found" in result.stdout or "0 datasets" in result.stdout
        ), "Expected indication of no results"
