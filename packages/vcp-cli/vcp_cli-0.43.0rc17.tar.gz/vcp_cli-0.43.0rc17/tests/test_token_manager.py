"""Unit tests for TokenManager class."""

from pathlib import Path
from unittest.mock import patch

from vcp.utils.token import TokenManager

from .helpers import (
    DEFAULT_EXPIRED_ACCESS,
    DEFAULT_EXPIRED_ID,
    DEFAULT_NEW_ACCESS,
    DEFAULT_NEW_ID,
    DEFAULT_REFRESH_TOKEN,
    create_token_store,
)


class TestTokenManager:
    """
    Critical tests for TokenManager class that handles encrypted token storage and automatic refresh.

    Covers:
    - Token save/load operations with encryption
    - Automatic refresh on expired tokens
    - Proactive refresh when tokens expire within 5 minutes
    - Error handling for refresh failures
    """

    @patch("vcp.utils.token.Path.home")
    def test_save_and_load_tokens_success(self, mock_home, temp_token_dir):
        """Test successful token save and load."""
        mock_home.return_value = Path(temp_token_dir)
        tm = TokenManager()

        # Create test tokens using helper
        original_tokens = create_token_store(
            access_token="test_access",
            id_token="test_id",
            refresh_token="test_refresh",
            expires_in_minutes=60,  # 1 hour
        )

        # Save tokens
        tm.save_tokens(original_tokens)
        assert tm.token_file.exists()

        # Load tokens
        loaded_tokens = tm.load_tokens()

        assert loaded_tokens is not None
        assert loaded_tokens.access_token == "test_access"
        assert loaded_tokens.id_token == "test_id"
        assert loaded_tokens.refresh_token == "test_refresh"
        assert loaded_tokens.expires_in == 3600

    @patch("vcp.utils.token.Path.home")
    def test_load_expired_tokens_without_refresh(self, mock_home, temp_token_dir):
        """Test loading expired tokens without refresh_token."""
        mock_home.return_value = Path(temp_token_dir)
        tm = TokenManager()

        # Create expired tokens without refresh token using helper
        expired_tokens = create_token_store(
            access_token=DEFAULT_EXPIRED_ACCESS,
            id_token=DEFAULT_EXPIRED_ID,
            refresh_token=None,  # No refresh token
            expired=True,
        )

        # Save the expired tokens
        tm.save_tokens(expired_tokens)

        # Load tokens - should return expired tokens, then clear file when refresh fails
        loaded_tokens = tm.load_tokens()
        result = tm.refresh_tokens_if_needed(loaded_tokens)

        assert result is None
        assert not tm.token_file.exists()

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.utils.token.TokenManager._refresh_expired_tokens")
    def test_load_expired_tokens_with_successful_refresh(
        self, mock_refresh, mock_home, temp_token_dir
    ):
        """Test loading expired tokens with successful refresh."""
        mock_home.return_value = Path(temp_token_dir)
        tm = TokenManager()

        # Create expired tokens with refresh token using helper
        expired_tokens = create_token_store(
            access_token=DEFAULT_EXPIRED_ACCESS,
            id_token=DEFAULT_EXPIRED_ID,
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expired=True,
        )

        # Mock successful refresh using helper
        new_tokens = create_token_store(
            access_token=DEFAULT_NEW_ACCESS,
            id_token=DEFAULT_NEW_ID,
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expires_in_minutes=60,  # 1 hour
        )
        mock_refresh.return_value = new_tokens

        # Save expired tokens
        tm.save_tokens(expired_tokens)

        # Load tokens - should return expired tokens, then refresh them
        loaded_tokens = tm.load_tokens()
        result = tm.refresh_tokens_if_needed(loaded_tokens)

        assert result is not None
        assert result.access_token == DEFAULT_NEW_ACCESS
        assert result.id_token == DEFAULT_NEW_ID
        assert result.refresh_token == DEFAULT_REFRESH_TOKEN
        mock_refresh.assert_called_once_with(DEFAULT_REFRESH_TOKEN)

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.utils.token.TokenManager._refresh_expired_tokens")
    def test_load_expired_tokens_with_failed_refresh(
        self, mock_refresh, mock_home, temp_token_dir
    ):
        """Test loading expired tokens with failed refresh."""
        mock_home.return_value = Path(temp_token_dir)
        tm = TokenManager()

        # Create expired tokens with refresh token using helper
        expired_tokens = create_token_store(
            access_token=DEFAULT_EXPIRED_ACCESS,
            id_token=DEFAULT_EXPIRED_ID,
            refresh_token="invalid_refresh",  # Keep invalid for failure test
            expired=True,
        )

        # Mock failed refresh
        mock_refresh.return_value = None

        # Save expired tokens
        tm.save_tokens(expired_tokens)

        # Load tokens - should return expired tokens, then fail refresh and clear tokens
        loaded_tokens = tm.load_tokens()
        result = tm.refresh_tokens_if_needed(loaded_tokens)

        assert result is None
        assert not tm.token_file.exists()
        mock_refresh.assert_called_once_with("invalid_refresh")

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.config.config.Config.load")
    @patch("vcp.auth.oauth.refresh_tokens")
    def test_refresh_expired_tokens_success(
        self,
        mock_refresh_func,
        mock_config_load,
        mock_home,
        temp_token_dir,
        mock_config_data,
    ):
        """Test successful token refresh."""
        mock_home.return_value = Path(temp_token_dir)
        mock_config_load.return_value = mock_config_data

        # Mock successful refresh using helper
        new_tokens = create_token_store(
            access_token="refreshed_access",
            id_token="refreshed_id",
            refresh_token="original_refresh",
            expires_in_minutes=60,  # 1 hour
        )
        mock_refresh_func.return_value = new_tokens

        tm = TokenManager()
        result = tm._refresh_expired_tokens("original_refresh")

        assert result is not None
        assert result.access_token == "refreshed_access"
        mock_refresh_func.assert_called_once()

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.utils.token.TokenManager._refresh_expired_tokens")
    def test_load_tokens_proactive_refresh_within_5_minutes(
        self, mock_refresh, mock_home, temp_token_dir
    ):
        """Test proactive refresh when tokens expire within 5 minutes."""
        mock_home.return_value = Path(temp_token_dir)
        tm = TokenManager()

        # Create tokens expiring in 3 minutes using helper
        tokens_expiring_soon = create_token_store(
            access_token="soon_to_expire_access",
            id_token="soon_to_expire_id",
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expires_in_minutes=3,  # Expires in 3 minutes
        )

        # Mock successful refresh using helper
        new_tokens = create_token_store(
            access_token="proactively_refreshed_access",
            id_token="proactively_refreshed_id",
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expires_in_minutes=60,  # 1 hour
        )
        mock_refresh.return_value = new_tokens

        # Save tokens expiring soon
        tm.save_tokens(tokens_expiring_soon)

        # Load tokens - should return tokens expiring soon, then trigger proactive refresh
        loaded_tokens = tm.load_tokens()
        result = tm.refresh_tokens_if_needed(loaded_tokens)

        assert result is not None
        assert result.access_token == "proactively_refreshed_access"
        assert result.id_token == "proactively_refreshed_id"
        mock_refresh.assert_called_once_with(DEFAULT_REFRESH_TOKEN)

    @patch("vcp.utils.token.Path.home")
    def test_load_tokens_no_refresh_when_fresh(self, mock_home, temp_token_dir):
        """Test that fresh tokens (>5 minutes remaining) don't get refreshed."""
        mock_home.return_value = Path(temp_token_dir)
        tm = TokenManager()

        # Create tokens expiring in 10 minutes using helper
        fresh_tokens = create_token_store(
            access_token="fresh_access_token",
            id_token="fresh_id_token",
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expires_in_minutes=10,  # Expires in 10 minutes (should not refresh)
        )

        # Save fresh tokens
        tm.save_tokens(fresh_tokens)

        # Mock refresh to ensure it's not called
        with patch(
            "vcp.utils.token.TokenManager._refresh_expired_tokens"
        ) as mock_refresh:
            loaded_tokens = tm.load_tokens()
            result = tm.refresh_tokens_if_needed(loaded_tokens)

            # Should return tokens as-is without refresh
            assert result is not None
            assert result.access_token == "fresh_access_token"
            assert result.id_token == "fresh_id_token"
            mock_refresh.assert_not_called()
