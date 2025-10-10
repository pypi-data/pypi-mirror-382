"""Integration tests for GitHub authentication and git operations."""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from vcp.auth.github import GitHubAuth
from vcp.config.config import Config


class TestGitHubAuthIntegration:
    """Integration tests for GitHub authentication functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.models = Mock()
        config.models.base_url = "https://test.example.com"
        return config

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_clone_repository_with_embedded_token(self, mock_config, temp_dir):
        """Test that clone_repository works with embedded token authentication."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock TokenManager to avoid authentication issues
            with patch("vcp.utils.token.TokenManager") as mock_token_manager:
                mock_token_instance = Mock()
                mock_token_instance.get_auth_headers.return_value = {
                    "Authorization": "Bearer test-token"
                }
                mock_token_manager.return_value = mock_token_instance

                # Mock subprocess.run to simulate successful git clone
                with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = "Cloning into 'test-repo'..."
                    mock_result.stderr = ""
                    mock_subprocess.return_value = mock_result

                    # Mock Repo creation
                    with patch("vcp.auth.github.Repo") as mock_repo:
                        mock_repo_instance = Mock()
                        mock_repo.return_value = mock_repo_instance

                        github_auth = GitHubAuth(mock_config)

                        # Test cloning
                        result = github_auth.clone_repository(
                            "https://github.com/test-org/test-repo.git",
                            os.path.join(temp_dir, "test-repo"),
                        )

                        # Verify the subprocess was called with the correct arguments
                        mock_subprocess.assert_called_once()
                        call_args = mock_subprocess.call_args

                        # Check that the URL contains the embedded token
                        git_args = call_args[0][0]
                        assert git_args[0] == "git"
                        assert git_args[1] == "clone"
                        assert "test-github-token-12345@github.com" in git_args[2]
                        assert git_args[3] == os.path.join(temp_dir, "test-repo")

                        # Verify the result
                        assert result == mock_repo_instance

    def test_clone_repository_with_temp_file_fallback(self, mock_config, temp_dir):
        """Test that clone_repository falls back to echo command when temp file creation fails."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock TokenManager to avoid authentication issues
            with patch("vcp.utils.token.TokenManager") as mock_token_manager:
                mock_token_instance = Mock()
                mock_token_instance.get_auth_headers.return_value = {
                    "Authorization": "Bearer test-token"
                }
                mock_token_manager.return_value = mock_token_instance

                # Mock tempfile.NamedTemporaryFile to raise an exception
                with patch(
                    "vcp.auth.github.tempfile.NamedTemporaryFile"
                ) as mock_tempfile:
                    mock_tempfile.side_effect = OSError("Permission denied")

                # Mock subprocess.run to simulate successful git clone
                with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = "Cloning into 'test-repo'..."
                    mock_result.stderr = ""
                    mock_subprocess.return_value = mock_result

                    # Mock Repo creation
                    with patch("vcp.auth.github.Repo") as mock_repo:
                        mock_repo_instance = Mock()
                        mock_repo.return_value = mock_repo_instance

                        github_auth = GitHubAuth(mock_config)

                        # Test cloning
                        result = github_auth.clone_repository(
                            "https://github.com/test-org/test-repo.git",
                            os.path.join(temp_dir, "test-repo"),
                        )

                        # Verify the subprocess was called
                        mock_subprocess.assert_called_once()

                        # Verify the result
                        assert result == mock_repo_instance

    def test_clone_repository_with_different_temp_directories(
        self, mock_config, temp_dir
    ):
        """Test that clone_repository tries different temp directories when /tmp is not writable."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock TokenManager to avoid authentication issues
            with patch("vcp.utils.token.TokenManager") as mock_token_manager:
                mock_token_instance = Mock()
                mock_token_instance.get_auth_headers.return_value = {
                    "Authorization": "Bearer test-token"
                }
                mock_token_manager.return_value = mock_token_instance

                # Mock os.access to simulate /tmp not being writable
                with patch("vcp.auth.github.os.access") as mock_access:

                    def access_side_effect(path, mode):
                        if path == "/tmp":
                            return False  # /tmp is not writable
                        return True  # Other directories are writable

                    mock_access.side_effect = access_side_effect

                    # Mock subprocess.run to simulate successful git clone
                    with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                        mock_result = Mock()
                        mock_result.returncode = 0
                        mock_result.stdout = "Cloning into 'test-repo'..."
                        mock_result.stderr = ""
                        mock_subprocess.return_value = mock_result

                        # Mock Repo creation
                        with patch("vcp.auth.github.Repo") as mock_repo:
                            mock_repo_instance = Mock()
                            mock_repo.return_value = mock_repo_instance

                            github_auth = GitHubAuth(mock_config)

                            # Test cloning
                            result = github_auth.clone_repository(
                                "https://github.com/test-org/test-repo.git",
                                os.path.join(temp_dir, "test-repo"),
                            )

                            # Verify the subprocess was called
                            mock_subprocess.assert_called_once()

                            # Verify the result
                            assert result == mock_repo_instance

    def test_clone_repository_git_failure(self, mock_config, temp_dir):
        """Test that clone_repository handles git clone failures properly."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock subprocess.run to simulate git clone failure
            with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "fatal: repository 'https://github.com/test-org/test-repo.git' not found"
                mock_subprocess.return_value = mock_result

                github_auth = GitHubAuth(mock_config)

                # Test cloning - should raise an exception
                with pytest.raises(RuntimeError, match="Failed to clone repository"):
                    github_auth.clone_repository(
                        "https://github.com/test-org/test-repo.git",
                        os.path.join(temp_dir, "test-repo"),
                    )

    def test_clone_repository_authentication_failure(self, mock_config, temp_dir):
        """Test that clone_repository handles authentication failures properly."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock subprocess.run to simulate authentication failure
            with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "fatal: could not read Password for 'https://test-github-token-12345@github.com': terminal prompts disabled"
                mock_subprocess.return_value = mock_result

                github_auth = GitHubAuth(mock_config)

                # Test cloning - should raise an exception
                with pytest.raises(RuntimeError, match="Failed to clone repository"):
                    github_auth.clone_repository(
                        "https://github.com/test-org/test-repo.git",
                        os.path.join(temp_dir, "test-repo"),
                    )

    def test_clone_repository_environment_cleanup(self, mock_config, temp_dir):
        """Test that clone_repository properly cleans up environment variables."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock TokenManager to avoid authentication issues
            with patch("vcp.utils.token.TokenManager") as mock_token_manager:
                mock_token_instance = Mock()
                mock_token_instance.get_auth_headers.return_value = {
                    "Authorization": "Bearer test-token"
                }
                mock_token_manager.return_value = mock_token_instance

                # Store original environment variables
                original_terminal_prompt = os.environ.get("GIT_TERMINAL_PROMPT")
                original_askpass = os.environ.get("GIT_ASKPASS")

                try:
                    # Mock subprocess.run to simulate successful git clone
                    with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                        mock_result = Mock()
                        mock_result.returncode = 0
                        mock_result.stdout = "Cloning into 'test-repo'..."
                        mock_result.stderr = ""
                        mock_subprocess.return_value = mock_result

                        # Mock Repo creation
                        with patch("vcp.auth.github.Repo") as mock_repo:
                            mock_repo_instance = Mock()
                            mock_repo.return_value = mock_repo_instance

                            github_auth = GitHubAuth(mock_config)

                            # Test cloning
                            result = github_auth.clone_repository(
                                "https://github.com/test-org/test-repo.git",
                                os.path.join(temp_dir, "test-repo"),
                            )

                            # Verify the result
                            assert result == mock_repo_instance

                    # Verify environment variables are restored
                    assert (
                        os.environ.get("GIT_TERMINAL_PROMPT")
                        == original_terminal_prompt
                    )
                    assert os.environ.get("GIT_ASKPASS") == original_askpass

                finally:
                    # Restore original environment variables
                    if original_terminal_prompt is not None:
                        os.environ["GIT_TERMINAL_PROMPT"] = original_terminal_prompt
                    else:
                        os.environ.pop("GIT_TERMINAL_PROMPT", None)

                    if original_askpass is not None:
                        os.environ["GIT_ASKPASS"] = original_askpass
                    else:
                        os.environ.pop("GIT_ASKPASS", None)

    def test_clone_repository_with_non_github_url(self, mock_config, temp_dir):
        """Test that clone_repository handles non-GitHub URLs correctly."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            # Mock the token generation
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_get.return_value = mock_response

            # Mock TokenManager to avoid authentication issues
            with patch("vcp.utils.token.TokenManager") as mock_token_manager:
                mock_token_instance = Mock()
                mock_token_instance.get_auth_headers.return_value = {
                    "Authorization": "Bearer test-token"
                }
                mock_token_manager.return_value = mock_token_instance

                # Mock subprocess.run to simulate successful git clone
                with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = "Cloning into 'test-repo'..."
                    mock_result.stderr = ""
                    mock_subprocess.return_value = mock_result

                    # Mock Repo creation
                    with patch("vcp.auth.github.Repo") as mock_repo:
                        mock_repo_instance = Mock()
                        mock_repo.return_value = mock_repo_instance

                        github_auth = GitHubAuth(mock_config)

                        # Test cloning with non-GitHub URL
                        result = github_auth.clone_repository(
                            "https://gitlab.com/test-org/test-repo.git",
                            os.path.join(temp_dir, "test-repo"),
                        )

                        # Verify the subprocess was called with the original URL
                        mock_subprocess.assert_called_once()
                        call_args = mock_subprocess.call_args

                        # Check that the URL was not modified
                        git_args = call_args[0][0]
                        assert (
                            git_args[2] == "https://gitlab.com/test-org/test-repo.git"
                        )

                        # Verify the result
                        assert result == mock_repo_instance
