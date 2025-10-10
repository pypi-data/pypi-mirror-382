"""Integration tests for GitHub operations using real repositories."""

import os
import tempfile
import threading
from unittest.mock import Mock, patch

import pytest

from vcp.auth.github import GitHubAuth
from vcp.config.config import Config


class TestGitHubOperationsIntegration:
    """Integration tests for GitHub operations using real repositories."""

    # Test repositories for different scenarios
    SMALL_TEST_REPO = "https://github.com/octocat/Hello-World"  # Fast, small repo
    VCP_REPO = "https://github.com/chanzuckerberg/vcp-cli"  # Real-world repo
    DEDICATED_TEST_REPO = "https://github.com/cz-model-contributions/vcp-cli-integration-test-do-not-delete"  # Our test repo

    @pytest.fixture(scope="class")
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=Config)
        config.models = Mock()
        config.models.base_url = "https://test.example.com"
        return config

    @pytest.fixture(scope="class")
    def github_auth(self, mock_config):
        """Create GitHubAuth instance for testing."""
        return GitHubAuth(mock_config)

    def test_clone_small_repo_fast(self, github_auth):
        """Test cloning a small repository quickly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to avoid real API calls
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                result = github_auth.clone_repository(
                    self.SMALL_TEST_REPO, os.path.join(temp_dir, "hello-world")
                )
                assert result is not None
                assert os.path.exists(os.path.join(temp_dir, "hello-world", ".git"))
                assert os.path.exists(os.path.join(temp_dir, "hello-world", "README"))

    def test_clone_vcp_repo_real_world(self, github_auth):
        """Test cloning VCP CLI repository for real-world scenario."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to avoid real API calls
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                # Mock subprocess.run to avoid actual git clone
                with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_subprocess.return_value = mock_result

                    # Mock Repo creation
                    with patch("vcp.auth.github.Repo") as mock_repo:
                        mock_repo_instance = Mock()
                        mock_repo.return_value = mock_repo_instance

                        result = github_auth.clone_repository(
                            self.VCP_REPO, os.path.join(temp_dir, "vcp-cli")
                        )
                        assert result is not None
                        assert result == mock_repo_instance

    def test_clone_dedicated_test_repo(self, github_auth):
        """Test cloning our dedicated test repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to avoid real API calls
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                # Mock subprocess.run to avoid actual git clone
                with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_subprocess.return_value = mock_result

                    # Mock Repo creation
                    with patch("vcp.auth.github.Repo") as mock_repo:
                        mock_repo_instance = Mock()
                        mock_repo.return_value = mock_repo_instance

                        result = github_auth.clone_repository(
                            self.DEDICATED_TEST_REPO,
                            os.path.join(temp_dir, "test-repo"),
                        )
                        assert result is not None
                        assert result == mock_repo_instance

    def test_temp_directory_fallback_scenarios(self, github_auth):
        """Test temp directory fallback when /tmp is not writable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock os.access to simulate /tmp not being writable
            with patch("vcp.auth.github.os.access") as mock_access:

                def access_side_effect(path, mode):
                    if path == "/tmp":
                        return False  # /tmp is not writable
                    return True  # Other directories are writable

                mock_access.side_effect = access_side_effect

                # Mock the token generation to avoid real API calls
                with patch.object(github_auth, "get_contributions_token") as mock_token:
                    mock_token.return_value = "test-github-token-12345"

                    # Test cloning with fallback
                    result = github_auth.clone_repository(
                        self.SMALL_TEST_REPO, os.path.join(temp_dir, "fallback-test")
                    )
                    assert result is not None
                    assert os.path.exists(
                        os.path.join(temp_dir, "fallback-test", ".git")
                    )

    def test_authentication_with_mocked_token(self, github_auth):
        """Test authentication with mocked token generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to avoid real API calls
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                result = github_auth.clone_repository(
                    self.SMALL_TEST_REPO, os.path.join(temp_dir, "auth-test")
                )
                assert result is not None
                assert os.path.exists(os.path.join(temp_dir, "auth-test", ".git"))

    def test_git_operations_with_auth(self, github_auth):
        """Test git operations (pull, merge) on existing repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to avoid real API calls
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                # First clone the repository
                result = github_auth.clone_repository(
                    self.SMALL_TEST_REPO, os.path.join(temp_dir, "git-ops-test")
                )
                assert result is not None

                # Test that we can perform git operations
                repo_path = os.path.join(temp_dir, "git-ops-test")
                assert os.path.exists(os.path.join(repo_path, ".git"))

    def test_embedded_token_url_authentication(self, github_auth):
        """Test that embedded token URL authentication works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to get a predictable token
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                result = github_auth.clone_repository(
                    self.SMALL_TEST_REPO, os.path.join(temp_dir, "embedded-token-test")
                )
                assert result is not None
                assert os.path.exists(
                    os.path.join(temp_dir, "embedded-token-test", ".git")
                )

    def test_askpass_script_creation_and_cleanup(self, github_auth):
        """Test that askpass script is created and cleaned up properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                # Store original environment
                original_askpass = os.environ.get("GIT_ASKPASS")

                try:
                    result = github_auth.clone_repository(
                        self.SMALL_TEST_REPO, os.path.join(temp_dir, "askpass-test")
                    )
                    assert result is not None
                    assert os.path.exists(
                        os.path.join(temp_dir, "askpass-test", ".git")
                    )

                finally:
                    # Verify environment is restored
                    assert os.environ.get("GIT_ASKPASS") == original_askpass

    def test_askpass_script_fallback_when_creation_fails(self, github_auth):
        """Test fallback when askpass script creation fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock tempfile.NamedTemporaryFile to raise an exception
            with patch("vcp.auth.github.tempfile.NamedTemporaryFile") as mock_tempfile:
                mock_tempfile.side_effect = OSError("Permission denied")

                # Mock the token generation
                with patch.object(github_auth, "get_contributions_token") as mock_token:
                    mock_token.return_value = "test-github-token-12345"

                    result = github_auth.clone_repository(
                        self.SMALL_TEST_REPO, os.path.join(temp_dir, "fallback-test")
                    )
                    assert result is not None
                    assert os.path.exists(
                        os.path.join(temp_dir, "fallback-test", ".git")
                    )

    def test_non_github_url_handling(self, github_auth):
        """Test that non-GitHub URLs are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with a non-GitHub URL (this should fail gracefully)
            with pytest.raises(RuntimeError, match="Failed to clone repository"):
                github_auth.clone_repository(
                    "https://gitlab.com/octocat/Hello-World",
                    os.path.join(temp_dir, "non-github-test"),
                )

    def test_network_failure_handling(self, github_auth):
        """Test handling of network failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock subprocess.run to simulate network failure
            with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "fatal: unable to access 'https://github.com/octocat/Hello-World.git/': Could not resolve host: github.com"
                mock_subprocess.return_value = mock_result

                with pytest.raises(RuntimeError, match="Failed to clone repository"):
                    github_auth.clone_repository(
                        self.SMALL_TEST_REPO,
                        os.path.join(temp_dir, "network-failure-test"),
                    )

    def test_authentication_failure_handling(self, github_auth):
        """Test handling of authentication failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock subprocess.run to simulate authentication failure
            with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "fatal: could not read Password for 'https://test-token@github.com': terminal prompts disabled"
                mock_subprocess.return_value = mock_result

                # Mock the token generation
                with patch.object(github_auth, "get_contributions_token") as mock_token:
                    mock_token.return_value = "test-token"

                    with pytest.raises(
                        RuntimeError, match="Failed to clone repository"
                    ):
                        github_auth.clone_repository(
                            self.SMALL_TEST_REPO,
                            os.path.join(temp_dir, "auth-failure-test"),
                        )

    def test_repository_not_found_handling(self, github_auth):
        """Test handling of repository not found errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock subprocess.run to simulate repository not found
            with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "fatal: repository 'https://github.com/nonexistent/repo.git' not found"
                mock_subprocess.return_value = mock_result

                with pytest.raises(RuntimeError, match="Failed to clone repository"):
                    github_auth.clone_repository(
                        "https://github.com/nonexistent/repo.git",
                        os.path.join(temp_dir, "not-found-test"),
                    )

    def test_concurrent_clone_operations(self, github_auth):
        """Test that multiple concurrent clone operations work correctly."""
        results = []
        errors = []

        def clone_worker(repo_url, output_path):
            try:
                result = github_auth.clone_repository(repo_url, output_path)
                results.append(result)
            except Exception as e:
                errors.append(e)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the token generation to avoid real API calls
            with patch.object(github_auth, "get_contributions_token") as mock_token:
                mock_token.return_value = "test-github-token-12345"

                # Start multiple clone operations concurrently
                threads = []
                for i in range(3):
                    thread = threading.Thread(
                        target=clone_worker,
                        args=(
                            self.SMALL_TEST_REPO,
                            os.path.join(temp_dir, f"concurrent-test-{i}"),
                        ),
                    )
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()

                # Verify all operations succeeded
                assert len(results) == 3
                assert len(errors) == 0
                for i in range(3):
                    assert os.path.exists(
                        os.path.join(temp_dir, f"concurrent-test-{i}", ".git")
                    )

    def test_environment_cleanup_after_failure(self, github_auth):
        """Test that environment variables are cleaned up even after failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Store original environment
            original_terminal_prompt = os.environ.get("GIT_TERMINAL_PROMPT")
            original_askpass = os.environ.get("GIT_ASKPASS")

            try:
                # Mock subprocess.run to simulate failure
                with patch("vcp.auth.github.subprocess.run") as mock_subprocess:
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = ""
                    mock_result.stderr = "fatal: repository not found"
                    mock_subprocess.return_value = mock_result

                    with pytest.raises(RuntimeError):
                        github_auth.clone_repository(
                            self.SMALL_TEST_REPO, os.path.join(temp_dir, "cleanup-test")
                        )

            finally:
                # Verify environment is restored even after failure
                assert os.environ.get("GIT_TERMINAL_PROMPT") == original_terminal_prompt
                assert os.environ.get("GIT_ASKPASS") == original_askpass
