"""Unit tests for GitHub authentication token caching functionality."""

import time
from unittest.mock import Mock, patch

import pytest
import requests

from vcp.auth.github import GitHubAuth, TokenInfo
from vcp.config.config import Config


class TestGitHubAuthTokenCaching:
    """Test cases for GitHub authentication token caching and expiration handling."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.models = Mock()
        config.models.base_url = "https://test.example.com"
        return config

    @pytest.fixture
    def github_auth(self, mock_config):
        """Create a GitHubAuth instance for testing."""
        return GitHubAuth(mock_config)

    @pytest.fixture
    def mock_token_manager(self):
        """Mock TokenManager for testing."""
        with patch("vcp.utils.token.TokenManager") as mock_tm:
            mock_instance = Mock()
            mock_instance.get_auth_headers.return_value = {
                "Authorization": "Bearer test-token"
            }
            mock_tm.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_requests_get(self):
        """Mock requests.get for testing."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"token": "test-github-token-12345"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            yield mock_get

    def test_initial_state(self, github_auth):
        """Test that GitHubAuth starts with no cached token."""
        assert github_auth._token_info is None
        assert github_auth.is_token_expired() is True
        assert github_auth.get_token_ttl_seconds() is None
        assert github_auth.get_token_info() is None

    def test_token_generation_and_caching(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test that tokens are generated and cached properly."""
        # First call should generate a new token
        token = github_auth.get_contributions_token()

        assert token == "test-github-token-12345"
        assert github_auth._token_info is not None
        assert github_auth._token_info.token == "test-github-token-12345"
        assert github_auth._token_info.expires_at is not None
        assert github_auth.is_token_expired() is False

        # Verify API was called
        mock_requests_get.assert_called_once()
        mock_token_manager.get_auth_headers.assert_called_once()

    def test_token_caching_reuse(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test that cached tokens are reused when not expired."""
        # First call
        token1 = github_auth.get_contributions_token()

        # Second call should use cached token
        token2 = github_auth.get_contributions_token()

        assert token1 == token2 == "test-github-token-12345"
        # API should only be called once
        assert mock_requests_get.call_count == 1

    def test_token_expiration_detection(self, github_auth):
        """Test token expiration detection."""
        # Set up an expired token
        github_auth._token_info = TokenInfo(
            token="test-token",
            expires_at=time.time() - 100,  # Expired 100 seconds ago
            created_at=time.time() - 3600,
        )

        assert github_auth.is_token_expired() is True
        assert github_auth.get_token_ttl_seconds() == 0

    def test_token_not_expired(self, github_auth):
        """Test that valid tokens are not considered expired."""
        # Set up a valid token
        github_auth._token_info = TokenInfo(
            token="test-token",
            expires_at=time.time() + 3000,  # Valid for 50 minutes
            created_at=time.time(),
        )

        assert github_auth.is_token_expired() is False
        ttl = github_auth.get_token_ttl_seconds()
        assert ttl is not None
        assert 2900 <= ttl <= 3000  # Should be close to 3000 seconds

    def test_automatic_token_refresh_on_expiration(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test that expired tokens are automatically refreshed."""
        # Set up an expired token
        github_auth._token_info = TokenInfo(
            token="old-token",
            expires_at=time.time() - 100,  # Expired
            created_at=time.time() - 3600,
        )

        # Call should refresh the token
        token = github_auth.get_contributions_token()

        assert token == "test-github-token-12345"
        assert github_auth._token_info is not None
        assert github_auth._token_info.token == "test-github-token-12345"
        assert github_auth._token_info.expires_at > time.time()

        # API should be called to refresh
        mock_requests_get.assert_called_once()

    def test_force_token_refresh(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test forced token refresh functionality."""
        # Set up a valid token
        github_auth._token_info = TokenInfo(
            token="old-token",
            expires_at=time.time() + 3000,  # Valid
            created_at=time.time(),
        )

        # Force refresh
        token = github_auth.force_token_refresh()

        assert token == "test-github-token-12345"
        assert github_auth._token_info is not None
        assert github_auth._token_info.token == "test-github-token-12345"
        assert github_auth._token_info.expires_at > time.time()

        # API should be called
        mock_requests_get.assert_called_once()

    def test_token_ttl_calculation(self, github_auth):
        """Test token TTL calculation."""
        # Set up a token with known expiration
        current_time = time.time()
        github_auth._token_info = TokenInfo(
            token="test-token",
            expires_at=current_time + 1000,  # Expires in 1000 seconds
            created_at=current_time,
        )

        ttl = github_auth.get_token_ttl_seconds()
        assert ttl is not None
        assert 990 <= ttl <= 1000  # Should be close to 1000 seconds

    def test_token_ttl_zero_when_expired(self, github_auth):
        """Test that TTL returns 0 for expired tokens."""
        # Set up an expired token
        github_auth._token_info = TokenInfo(
            token="test-token",
            expires_at=time.time() - 100,  # Expired
            created_at=time.time() - 3600,
        )

        ttl = github_auth.get_token_ttl_seconds()
        assert ttl == 0

    def test_token_ttl_none_when_no_token(self, github_auth):
        """Test that TTL returns None when no token is cached."""
        ttl = github_auth.get_token_ttl_seconds()
        assert ttl is None

    def test_api_error_handling(self, github_auth, mock_token_manager):
        """Test error handling when API call fails."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("API Error")

            with pytest.raises(
                RuntimeError, match="Failed to authenticate with GitHub contributions"
            ):
                github_auth.get_contributions_token()

    def test_invalid_response_format(self, github_auth, mock_token_manager):
        """Test error handling when API returns invalid response format."""
        with patch("vcp.auth.github.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "invalid": "response"
            }  # Missing "token" key
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with pytest.raises(
                RuntimeError, match="Invalid response from Model Hub API"
            ):
                github_auth.get_contributions_token()

    def test_no_auth_headers(self, github_auth, mock_token_manager):
        """Test error handling when no auth headers are available."""
        mock_token_manager.get_auth_headers.return_value = None

        with pytest.raises(RuntimeError, match="Not logged in to Model Hub"):
            github_auth.get_contributions_token()

    def test_token_expiration_logging(
        self, github_auth, mock_token_manager, mock_requests_get, caplog
    ):
        """Test that token expiration is properly logged."""
        with caplog.at_level("DEBUG"):
            # Set up an expired token
            github_auth._token_info = TokenInfo(
                token="old-token",
                expires_at=time.time() - 100,  # Expired
                created_at=time.time() - 3600,
            )

            # Call should log expiration and refresh
            github_auth.get_contributions_token()

            # Check that expiration was logged
            assert "GitHub token has expired, generating new token" in caplog.text

    def test_force_refresh_logging(
        self, github_auth, mock_token_manager, mock_requests_get, caplog
    ):
        """Test that forced refresh is properly logged."""
        with caplog.at_level("DEBUG"):
            github_auth.force_token_refresh()

            # Check that forced refresh was logged
            assert "Forcing GitHub token refresh" in caplog.text

    def test_token_caching_with_time_advancement(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test token caching behavior when time advances."""
        # First call - should generate token
        token1 = github_auth.get_contributions_token()

        # Second call should use cached token (within expiration window)
        token2 = github_auth.get_contributions_token()
        assert token1 == token2
        assert mock_requests_get.call_count == 1  # Still only called once

    def test_token_refresh_after_expiration_time(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test that token is refreshed after expiration time passes."""
        # First call - should generate token
        token1 = github_auth.get_contributions_token()

        # Manually set token as expired
        github_auth._token_info = TokenInfo(
            token=token1,
            expires_at=time.time() - 100,  # Expired
            created_at=time.time() - 3600,
        )

        # Should refresh token
        token2 = github_auth.get_contributions_token()
        assert token1 == token2  # Same token value from mock
        assert mock_requests_get.call_count == 2  # Called twice (initial + refresh)

    def test_multiple_instances_independent_caching(
        self, mock_config, mock_token_manager, mock_requests_get
    ):
        """Test that multiple GitHubAuth instances have independent token caches."""
        auth1 = GitHubAuth(mock_config)
        auth2 = GitHubAuth(mock_config)

        # Get token from first instance
        token1 = auth1.get_contributions_token()

        # Second instance should generate its own token
        token2 = auth2.get_contributions_token()

        assert token1 == token2  # Same mock response
        assert auth1._token_info is not None
        assert auth2._token_info is not None
        assert auth1._token_info.token == auth2._token_info.token
        # Token expiration times should be close (within 1 second)
        assert abs(auth1._token_info.expires_at - auth2._token_info.expires_at) < 1.0

        # Both instances should have called the API
        assert mock_requests_get.call_count == 2

    def test_token_expiration_edge_case_exactly_at_expiration(
        self, github_auth, mock_token_manager, mock_requests_get
    ):
        """Test token behavior exactly at expiration time."""
        # Set up a token that expires exactly now
        current_time = time.time()
        github_auth._contributions_token = "test-token"
        github_auth._token_expires_at = current_time

        # Should consider token expired and refresh
        token = github_auth.get_contributions_token()
        assert token == "test-github-token-12345"
        assert mock_requests_get.call_count == 1
