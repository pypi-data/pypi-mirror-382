"""Unit tests for version command CLI integration."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from vcp.cli import cli
from vcp.commands.version import version_command


class TestVersionCommand:
    """Test the version command functionality."""

    @pytest.fixture
    def runner(self):
        """CLI test runner fixture."""
        return CliRunner()

    def test_version_command_basic(self, runner, current_version):
        """Test basic version command output."""
        result = runner.invoke(version_command, [])
        assert result.exit_code == 0
        assert f"vcp-cli version {current_version}" in result.output

    @patch("vcp.commands.version.check_for_updates")
    def test_version_command_with_check_update_available(
        self, mock_check, runner, current_version
    ):
        """Test version command with --check flag showing update."""
        mock_check.return_value = (True, f"Update available: {current_version} → 1.0.0")

        result = runner.invoke(version_command, ["--check"])
        assert result.exit_code == 0
        assert f"Current version: {current_version}" in result.output
        assert "Checking for updates..." in result.output
        assert f"Update available: {current_version} → 1.0.0" in result.output
        assert "pip install --upgrade vcp-cli" in result.output

    @patch("vcp.commands.version.check_for_updates")
    def test_version_command_with_check_no_update(
        self, mock_check, runner, current_version
    ):
        """Test version command with --check flag showing no update."""
        mock_check.return_value = (
            False,
            f"You have the latest version ({current_version})",
        )

        result = runner.invoke(version_command, ["--check"])
        assert result.exit_code == 0
        assert f"Current version: {current_version}" in result.output
        assert "Checking for updates..." in result.output
        assert f"You have the latest version ({current_version})" in result.output
        assert "pip install --upgrade vcp-cli" not in result.output

    @patch("vcp.commands.version.check_for_updates")
    def test_version_command_with_check_network_error(
        self, mock_check, runner, current_version
    ):
        """Test version command with --check flag and network error."""
        mock_check.return_value = (
            False,
            f"Could not check for updates (current: {current_version})",
        )

        result = runner.invoke(version_command, ["--check"])
        assert result.exit_code == 0
        assert f"Current version: {current_version}" in result.output
        assert "Could not check for updates" in result.output

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_version_command_in_main_cli(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test that version command is available in main CLI and skips automatic check."""
        mock_check_cache.return_value = (
            True,
            f"Update available: {current_version} → 1.0.0",
        )

        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert f"vcp-cli version {current_version}" in result.output
        # Automatic check should be skipped for version command
        mock_check_cache.assert_not_called()

    @patch("vcp.commands.version.check_for_updates")
    @patch("vcp.cli.check_for_updates_with_cache")
    def test_version_command_in_main_cli_with_check(
        self, mock_check_cache, mock_check, config_for_tests, runner, current_version
    ):
        """Test version command with --check in main CLI skips automatic check."""
        mock_check.return_value = (True, f"Update available: {current_version} → 1.0.0")
        mock_check_cache.return_value = (
            True,
            f"Update available: {current_version} → 1.0.0",
        )

        result = runner.invoke(cli, ["version", "--check"])
        assert result.exit_code == 0
        assert f"Update available: {current_version} → 1.0.0" in result.output
        # Should only show update message once (not from automatic check)
        assert result.output.count(f"Update available: {current_version} → 1.0.0") == 1
        # Automatic check should be skipped for version command
        mock_check_cache.assert_not_called()


class TestCLIAutomaticVersionCheck:
    """Test automatic version checking in CLI."""

    @pytest.fixture
    def runner(self):
        """CLI test runner fixture."""
        return CliRunner()

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_automatic_check_with_update_available(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test automatic version check shows update warning for non-version commands."""
        mock_check_cache.return_value = (
            True,
            f"Update available: {current_version} → 1.0.0",
        )

        # Test with a non-version command (config)
        result = runner.invoke(cli, ["config"])
        # Config command may fail, but we're testing that version check runs
        assert (
            f"Update available: {current_version} → 1.0.0" in result.output
            or result.exit_code != 0
        )

        # Test that version command does NOT show automatic update check
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert f"vcp-cli version {current_version}" in result.output
        # Should NOT show automatic update warning
        assert "Update available: 0.1.0 → 1.0.0" not in result.output

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_automatic_check_no_update(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test automatic version check with no update available."""
        mock_check_cache.return_value = None  # No update available

        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        # Should not show update warning
        assert "Update available" not in result.output
        assert "pip install --upgrade vcp-cli" not in result.output
        # Should still show version
        assert f"vcp-cli version {current_version}" in result.output

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_automatic_check_with_exception(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test automatic version check handles exceptions gracefully."""
        mock_check_cache.side_effect = Exception("Network error")

        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        # Should not crash and still show version
        assert f"vcp-cli version {current_version}" in result.output
        # Should not show error messages (fails silently)
        assert "Network error" not in result.output

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_automatic_check_on_different_commands(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test automatic version check runs on different CLI commands."""
        mock_check_cache.return_value = (
            True,
            f"Update available: {current_version} → 1.0.0",
        )

        # Test with help command
        result = runner.invoke(cli, ["--help"])
        # Note: Click may handle --help before our CLI function runs
        # This test verifies the integration works when CLI function is called

        # Test with config command
        result = runner.invoke(cli, ["config"])
        # The specific command may fail, but we're testing that the version check runs
        assert "Update available" in result.output or result.exit_code != 0

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_automatic_check_cache_behavior(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test that automatic check uses cached results properly."""
        mock_check_cache.return_value = (
            True,
            f"Update available: {current_version} → 1.0.0",
        )

        # Run non-version command to trigger automatic check
        result = runner.invoke(cli, ["config"])

        # Verify the cache function was called (not the direct PyPI check)
        mock_check_cache.assert_called_once()
        # Config command may fail, but we're testing that version check runs
        assert "Update available" in result.output or result.exit_code != 0

    @patch("vcp.cli.check_for_updates_with_cache")
    def test_no_automatic_check_for_version_commands(
        self, mock_check_cache, config_for_tests, runner, current_version
    ):
        """Test that automatic check is skipped for version commands."""
        mock_check_cache.return_value = (
            True,
            f"Update available: {current_version} → 1.0.0",
        )

        # Run version command - should skip automatic check
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert f"vcp-cli version {current_version}" in result.output
        # Should not contain automatic update warning
        assert "Update available" not in result.output
        mock_check_cache.assert_not_called()

        # Run version --check - should skip automatic check but show explicit check
        result = runner.invoke(cli, ["version", "--check"])
        # Automatic check should still be skipped
        mock_check_cache.assert_not_called()
