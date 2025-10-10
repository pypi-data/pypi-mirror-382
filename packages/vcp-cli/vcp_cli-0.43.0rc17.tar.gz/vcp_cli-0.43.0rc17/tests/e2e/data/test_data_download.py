import os
import subprocess
import tempfile

import pytest

from tests.e2e.data.base_data_test import BaseDataTest


class TestDataDownload(BaseDataTest):
    """E2E tests for vcp data download command."""

    @pytest.mark.e2e
    def test_download_without_id_or_query(self, session_auth):
        """Test download command fails when neither --id nor --query is provided."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "download"],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        # Should fail with usage error
        assert result.returncode != 0
        assert (
            "At least one of --id or --query must be provided" in result.stderr
            or "--id" in result.stderr
        )

    @pytest.mark.e2e
    def test_download_with_positional_argument(self, session_auth):
        """Test download command shows helpful error for old positional syntax."""
        app_env, _ = session_auth

        result = subprocess.run(
            [
                "uv",
                "run",
                "vcp",
                "data",
                "download",
                "some-dataset-id-12345678901234567890",
            ],
            env=app_env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)

        # Should fail with helpful error about using --id
        assert result.returncode != 0
        assert "Unexpected argument" in result.stderr
        assert "--id" in result.stderr

    @pytest.mark.e2e
    def test_download_invalid_dataset_id(self, session_auth):
        """Test download with invalid dataset ID format."""
        app_env, _ = session_auth

        result = subprocess.run(
            ["uv", "run", "vcp", "data", "download", "--id", "invalid-id"],
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
    @pytest.mark.prod_only
    def test_download_by_id(self, session_auth):
        """Test download by dataset ID with small dataset."""
        app_env, _ = session_auth

        # Use a small dataset (33MB)
        dataset_id = "688ac756fbd79be5a98d786a"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download with confirmation
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "vcp",
                    "data",
                    "download",
                    "--id",
                    dataset_id,
                    "-o",
                    temp_dir,
                ],
                env=app_env,
                capture_output=True,
                text=True,
                input="y\n",  # Answer 'yes' to confirmation
            )
            print(result.stdout)
            print(result.stderr)

            self.assert_successful_command(result, "data download --id")
            self.assert_no_errors(result)

            # Verify file was downloaded
            downloaded_files = os.listdir(temp_dir)
            assert len(downloaded_files) > 0, "No files were downloaded"

    @pytest.mark.e2e
    def test_download_nonexistent_dataset(self, session_auth):
        """Test download with a valid format but nonexistent dataset ID."""
        app_env, _ = session_auth

        fake_id = "00000000-0000-0000-0000-000000000000"

        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "vcp",
                    "data",
                    "download",
                    "--id",
                    fake_id,
                    "-o",
                    temp_dir,
                ],
                env=app_env,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            print(result.stderr)

            # Should fail with error (API returns 500 for nonexistent datasets)
            assert result.returncode != 0
            assert "error" in result.stdout.lower()
