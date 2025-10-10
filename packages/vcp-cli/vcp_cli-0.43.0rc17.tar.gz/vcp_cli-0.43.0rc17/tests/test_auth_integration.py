"""Integration tests for complete authentication refresh flow."""

import time
from pathlib import Path
from unittest.mock import patch

from vcp.utils.token import TokenManager

from .helpers import (
    DEFAULT_EXPIRED_ACCESS,
    DEFAULT_EXPIRED_ID,
    DEFAULT_REFRESH_TOKEN,
    create_token_store,
    setup_cognito_error_response,
    setup_cognito_success_response,
)


class TestAuthRefreshIntegration:
    """
    Critical integration tests for the complete authentication refresh flow.

    These tests verify the end-to-end token refresh functionality by testing
    the interaction between TokenManager, refresh_tokens(), and the complete
    authentication system.

    Key scenarios covered:
    - Complete token refresh flow with AWS Cognito integration
    - Proactive refresh when tokens expire within 5 minutes
    - Failed refresh handling across the entire stack
    - Valid tokens are not refreshed unnecessarily
    """

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.config.config.Config.load")
    @patch("vcp.auth.oauth.boto3.client")
    def test_end_to_end_token_refresh_flow(
        self,
        mock_boto3,
        mock_config_load,
        mock_home,
        temp_token_dir,
        mock_config_data,
        mock_cognito_client,
    ):
        """Test complete end-to-end token refresh flow."""
        # Setup mocks
        mock_home.return_value = Path(temp_token_dir)
        mock_config_load.return_value = mock_config_data
        mock_boto3.return_value = mock_cognito_client

        # Setup successful Cognito response using helper
        setup_cognito_success_response(
            mock_cognito_client,
            access_token="refreshed_access_token",
            id_token="refreshed_id_token",
            expires_in=3600,  # 1 hour
        )

        # Step 1: Create TokenManager and save expired tokens
        tm = TokenManager()

        expired_tokens = create_token_store(
            access_token=DEFAULT_EXPIRED_ACCESS,
            id_token=DEFAULT_EXPIRED_ID,
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expired=True,
        )

        tm.save_tokens(expired_tokens)
        assert tm.token_file.exists()

        # Step 2: Load tokens - should load expired tokens, then refresh them
        loaded_tokens = tm.load_tokens()
        refreshed_tokens = tm.refresh_tokens_if_needed(loaded_tokens)

        # Step 3: Verify tokens were refreshed
        assert refreshed_tokens is not None
        assert refreshed_tokens.access_token == "refreshed_access_token"
        assert refreshed_tokens.id_token == "refreshed_id_token"
        assert (
            refreshed_tokens.refresh_token == DEFAULT_REFRESH_TOKEN
        )  # Original preserved
        assert refreshed_tokens.expires_at > time.time()  # Should be fresh

        # Verify Cognito was called for refresh
        mock_cognito_client.initiate_auth.assert_called_once()
        call_args = mock_cognito_client.initiate_auth.call_args
        assert call_args[1]["AuthFlow"] == "REFRESH_TOKEN_AUTH"
        assert call_args[1]["ClientId"] == "test_client_id"
        assert "REFRESH_TOKEN" in call_args[1]["AuthParameters"]

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.config.config.Config.load")
    @patch("vcp.auth.oauth.boto3.client")
    def test_proactive_refresh_integration(
        self,
        mock_boto3,
        mock_config_load,
        mock_home,
        temp_token_dir,
        mock_config_data,
        mock_cognito_client,
    ):
        """Test proactive refresh integration when tokens expire within 5 minutes."""
        # Setup mocks
        mock_home.return_value = Path(temp_token_dir)
        mock_config_load.return_value = mock_config_data
        mock_boto3.return_value = mock_cognito_client

        # Setup successful Cognito response using helper
        setup_cognito_success_response(
            mock_cognito_client,
            access_token="proactively_refreshed_access_token",
            id_token="proactively_refreshed_id_token",
            expires_in=3600,  # 1 hour
        )

        # Step 1: Create TokenManager and save tokens expiring in 2 minutes
        tm = TokenManager()

        expiring_soon_tokens = create_token_store(
            access_token="expiring_soon_access_token",
            id_token="expiring_soon_id_token",
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expires_in_minutes=2,  # Expires in 2 minutes
        )

        tm.save_tokens(expiring_soon_tokens)
        assert tm.token_file.exists()

        # Step 2: Load tokens - should load expiring tokens, then proactively refresh them
        loaded_tokens = tm.load_tokens()
        refreshed_tokens = tm.refresh_tokens_if_needed(loaded_tokens)

        # Step 3: Verify tokens were proactively refreshed
        assert refreshed_tokens is not None
        assert refreshed_tokens.access_token == "proactively_refreshed_access_token"
        assert refreshed_tokens.id_token == "proactively_refreshed_id_token"
        assert refreshed_tokens.refresh_token == DEFAULT_REFRESH_TOKEN
        assert (
            refreshed_tokens.expires_at > time.time() + 3500
        )  # Should be fresh (58+ minutes remaining)

        # Verify Cognito was called for proactive refresh
        mock_cognito_client.initiate_auth.assert_called_once()
        call_args = mock_cognito_client.initiate_auth.call_args
        assert call_args[1]["AuthFlow"] == "REFRESH_TOKEN_AUTH"

    @patch("vcp.utils.token.Path.home")
    @patch("vcp.config.config.Config.load")
    @patch("vcp.auth.oauth.boto3.client")
    def test_end_to_end_refresh_failure_flow(
        self,
        mock_boto3,
        mock_config_load,
        mock_home,
        temp_token_dir,
        mock_config_data,
        mock_cognito_client,
    ):
        """Test complete flow when refresh fails."""
        # Setup mocks
        mock_home.return_value = Path(temp_token_dir)
        mock_config_load.return_value = mock_config_data
        mock_boto3.return_value = mock_cognito_client

        # Setup error response using helper

        setup_cognito_error_response(mock_cognito_client, "NotAuthorizedException")

        # Step 1: Save expired tokens
        tm = TokenManager()
        expired_tokens = create_token_store(
            access_token=DEFAULT_EXPIRED_ACCESS,
            id_token=DEFAULT_EXPIRED_ID,
            refresh_token="expired_refresh_token",  # Keep as unique for this failure test
            expired=True,
        )
        tm.save_tokens(expired_tokens)
        assert tm.token_file.exists()

        # Step 2: Load tokens - should load expired tokens, then fail refresh and clear tokens
        loaded_tokens = tm.load_tokens()
        refreshed_tokens = tm.refresh_tokens_if_needed(loaded_tokens)

        # Step 3: Verify tokens are cleared when refresh fails
        assert refreshed_tokens is None
        assert not tm.token_file.exists()  # Tokens should be cleared

        # Verify refresh was attempted
        mock_cognito_client.initiate_auth.assert_called_once()

    @patch("vcp.utils.token.Path.home")
    def test_end_to_end_valid_tokens_no_refresh(self, mock_home, temp_token_dir):
        """Test that valid tokens don't trigger refresh."""
        # Setup
        mock_home.return_value = Path(temp_token_dir)

        # Step 1: Save valid (non-expired) tokens using helper
        tm = TokenManager()
        valid_tokens = create_token_store(
            access_token="valid_access_token",
            id_token="valid_id_token",
            refresh_token=DEFAULT_REFRESH_TOKEN,
            expires_in_minutes=60,  # Will be fresh for 1 hour
        )
        tm.save_tokens(valid_tokens)

        # Step 2: Load tokens - should return without refresh
        with patch(
            "vcp.utils.token.TokenManager._refresh_expired_tokens"
        ) as mock_refresh:
            loaded_tokens = tm.load_tokens()
            refreshed_tokens = tm.refresh_tokens_if_needed(loaded_tokens)

            # Step 3: Verify tokens are returned as-is
            assert refreshed_tokens is not None
            assert refreshed_tokens.access_token == "valid_access_token"
            assert refreshed_tokens.id_token == "valid_id_token"
            assert refreshed_tokens.refresh_token == DEFAULT_REFRESH_TOKEN

            # Verify refresh was NOT called
            mock_refresh.assert_not_called()
