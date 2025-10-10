"""Unit tests for version checking functionality."""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from vcp.utils.version_check import (
    PYPI_PACKAGE_NAME,
    check_for_updates,
    check_for_updates_with_cache,
    compare_versions,
    get_cache_file,
    get_cached_version_info,
    get_current_version,
    get_latest_pypi_version,
    is_cache_valid,
    save_version_info_to_cache,
)


class TestVersionUtilities:
    """Test basic version utility functions."""

    def test_get_current_version(self, current_version):
        """Test getting current version."""
        version = get_current_version()
        assert version == current_version
        assert isinstance(version, str)

    def test_get_cache_file(self):
        """Test cache file path generation."""
        cache_file = get_cache_file()
        assert isinstance(cache_file, Path)
        assert cache_file.name == "version_check.json"
        assert ".vcp/cache" in str(cache_file)


class TestCacheFunctionality:
    """Test version checking cache functionality."""

    def test_is_cache_valid_nonexistent_file(self):
        """Test cache validation with nonexistent file."""
        fake_path = Path("/nonexistent/file.json")
        assert not is_cache_valid(fake_path)

    def test_is_cache_valid_recent_file(self):
        """Test cache validation with recent file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            # File was just created, so it should be valid
            assert is_cache_valid(temp_path, max_age_hours=1)
        finally:
            temp_path.unlink()

    def test_is_cache_valid_old_file(self):
        """Test cache validation with old file."""

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            # Modify file time to be very old
            old_time = time.time() - (25 * 3600)  # 25 hours ago
            os.utime(temp_path, (old_time, old_time))

            assert not is_cache_valid(temp_path, max_age_hours=24)
        finally:
            temp_path.unlink()

    def test_get_cached_version_info_valid(self, current_version):
        """Test getting valid cached version info."""
        test_data = {
            "latest_version": "1.0.0",
            "timestamp": time.time(),
            "current_version": current_version,
        }

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            json.dump(test_data, temp_file)
            temp_path = Path(temp_file.name)

        try:
            cached_info = get_cached_version_info(temp_path)
            assert cached_info == test_data
        finally:
            temp_path.unlink()

    def test_get_cached_version_info_invalid_json(self):
        """Test getting cached version info with invalid JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            temp_file.write("invalid json content")
            temp_path = Path(temp_file.name)

        try:
            cached_info = get_cached_version_info(temp_path)
            assert cached_info is None
        finally:
            temp_path.unlink()

    def test_get_cached_version_info_nonexistent(self):
        """Test getting cached version info from nonexistent file."""
        fake_path = Path("/nonexistent/file.json")
        cached_info = get_cached_version_info(fake_path)
        assert cached_info is None

    def test_save_version_info_to_cache(self, current_version):
        """Test saving version info to cache."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            save_version_info_to_cache(temp_path, "1.2.3")

            # Verify the file was written correctly
            with open(temp_path, "r") as f:
                data = json.load(f)

            assert data["latest_version"] == "1.2.3"
            assert data["current_version"] == current_version
            assert "timestamp" in data
            assert isinstance(data["timestamp"], float)
        finally:
            temp_path.unlink()


class TestPyPIIntegration:
    """Test PyPI API integration."""

    @patch("vcp.utils.version_check.requests.get")
    def test_get_latest_pypi_version_success(self, mock_get):
        """Test successful PyPI version retrieval."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"info": {"version": "2.1.0"}}
        mock_get.return_value = mock_response

        version = get_latest_pypi_version("test-package")
        assert version == "2.1.0"

        mock_get.assert_called_once_with(
            "https://pypi.org/pypi/test-package/json", timeout=5
        )

    @patch("vcp.utils.version_check.requests.get")
    def test_get_latest_pypi_version_http_error(self, mock_get):
        """Test PyPI version retrieval with HTTP error."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        version = get_latest_pypi_version("test-package")
        assert version is None

    @patch("vcp.utils.version_check.requests.get")
    def test_get_latest_pypi_version_timeout(self, mock_get):
        """Test PyPI version retrieval with timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout error")

        version = get_latest_pypi_version("test-package")
        assert version is None

    @patch("vcp.utils.version_check.requests.get")
    def test_get_latest_pypi_version_invalid_response(self, mock_get):
        """Test PyPI version retrieval with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        version = get_latest_pypi_version("test-package")
        assert version is None


class TestVersionComparison:
    """Test version comparison logic."""

    def test_compare_versions_update_available(self):
        """Test version comparison when update is available."""
        is_update, message = compare_versions("1.0.0", "1.1.0")
        assert is_update is True
        assert "Update available: 1.0.0 → 1.1.0" in message

    def test_compare_versions_latest(self):
        """Test version comparison when already latest."""
        is_update, message = compare_versions("1.1.0", "1.1.0")
        assert is_update is False
        assert "You have the latest version (1.1.0)" in message

    def test_compare_versions_newer_than_pypi(self):
        """Test version comparison when local is newer than PyPI."""
        is_update, message = compare_versions("1.2.0", "1.1.0")
        assert is_update is False
        assert "You have a newer version (1.2.0) than PyPI (1.1.0)" in message

    def test_compare_versions_complex_versions(self):
        """Test version comparison with complex version strings."""
        is_update, message = compare_versions("1.0.0a1", "1.0.0")
        assert is_update is True
        assert "Update available" in message

    def test_compare_versions_invalid_version(self):
        """Test version comparison with invalid version string."""
        is_update, message = compare_versions("invalid", "1.0.0")
        assert is_update is False
        assert "Error comparing versions" in message


class TestUpdateChecking:
    """Test high-level update checking functions."""

    @patch("vcp.utils.version_check.get_latest_pypi_version")
    def test_check_for_updates_success(self, mock_get_latest, current_version):
        """Test successful update check."""
        mock_get_latest.return_value = "1.1.0"

        is_update, message = check_for_updates(PYPI_PACKAGE_NAME)
        assert is_update is True
        assert f"Update available: {current_version} → 1.1.0" in message

    @patch("vcp.utils.version_check.get_latest_pypi_version")
    def test_check_for_updates_network_failure(self, mock_get_latest):
        """Test update check with network failure."""
        mock_get_latest.return_value = None

        is_update, message = check_for_updates(PYPI_PACKAGE_NAME)
        assert is_update is False
        assert "Could not check for updates" in message

    @patch("vcp.utils.version_check.is_cache_valid")
    @patch("vcp.utils.version_check.get_cached_version_info")
    @patch("vcp.utils.version_check.get_cache_file")
    def test_check_for_updates_with_cache_hit(
        self, mock_get_cache_file, mock_get_cached, mock_is_valid, current_version
    ):
        """Test update check with valid cache hit."""
        # Setup mocks
        mock_cache_file = MagicMock()
        mock_get_cache_file.return_value = mock_cache_file
        mock_is_valid.return_value = True
        mock_get_cached.return_value = {
            "latest_version": "1.1.0",
            "current_version": current_version,
        }

        result = check_for_updates_with_cache(PYPI_PACKAGE_NAME)
        assert result is not None
        is_update, message = result
        assert is_update is True
        assert f"Update available: {current_version} → 1.1.0" in message

    @patch("vcp.utils.version_check.is_cache_valid")
    @patch("vcp.utils.version_check.get_cached_version_info")
    @patch("vcp.utils.version_check.get_cache_file")
    def test_check_for_updates_with_cache_latest_version(
        self, mock_get_cache_file, mock_get_cached, mock_is_valid, current_version
    ):
        """Test update check with cache showing latest version."""
        # Setup mocks
        mock_cache_file = MagicMock()
        mock_get_cache_file.return_value = mock_cache_file
        mock_is_valid.return_value = True
        mock_get_cached.return_value = {
            "latest_version": "0.1.0",
            "current_version": current_version,
        }

        result = check_for_updates_with_cache(PYPI_PACKAGE_NAME)
        # Should return None when no update is available (to avoid showing message)
        assert result is None

    @patch("vcp.utils.version_check.is_cache_valid")
    @patch("vcp.utils.version_check.get_latest_pypi_version")
    @patch("vcp.utils.version_check.save_version_info_to_cache")
    @patch("vcp.utils.version_check.get_cache_file")
    def test_check_for_updates_with_cache_miss(
        self,
        mock_get_cache_file,
        mock_save_cache,
        mock_get_latest,
        mock_is_valid,
        current_version,
    ):
        """Test update check with cache miss (expired)."""
        # Setup mocks
        mock_cache_file = MagicMock()
        mock_get_cache_file.return_value = mock_cache_file
        mock_is_valid.return_value = False  # Cache is invalid
        mock_get_latest.return_value = "1.2.0"

        result = check_for_updates_with_cache(PYPI_PACKAGE_NAME)
        assert result is not None
        is_update, message = result
        assert is_update is True
        assert f"Update available: {current_version} → 1.2.0" in message

        # Verify cache was updated
        mock_save_cache.assert_called_once_with(mock_cache_file, "1.2.0")

    @patch("vcp.utils.version_check.is_cache_valid")
    @patch("vcp.utils.version_check.get_latest_pypi_version")
    @patch("vcp.utils.version_check.get_cache_file")
    def test_check_for_updates_with_cache_network_failure(
        self, mock_get_cache_file, mock_get_latest, mock_is_valid
    ):
        """Test update check with cache miss and network failure."""
        # Setup mocks
        mock_cache_file = MagicMock()
        mock_get_cache_file.return_value = mock_cache_file
        mock_is_valid.return_value = False  # Cache is invalid
        mock_get_latest.return_value = None  # Network failure

        result = check_for_updates_with_cache(PYPI_PACKAGE_NAME)
        assert result is None  # No result when network fails
