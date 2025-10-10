"""Unit tests for OAuth refresh functionality."""

from unittest.mock import patch

from vcp.auth.oauth import refresh_tokens

from .helpers import (
    DEFAULT_REFRESH_TOKEN,
    create_auth_config,
    setup_cognito_error_response,
    setup_cognito_success_response,
)


class TestRefreshTokens:
    """
    Critical tests for refresh_tokens function that handles AWS Cognito token refresh.

    Covers:
    - Successful refresh with and without client secrets
    - Error handling for expired refresh tokens
    - Proper handling of refresh token rotation when Cognito returns new tokens
    """

    @patch("vcp.auth.oauth.boto3.client")
    @patch("vcp.auth.oauth.compute_secret_hash")
    def test_refresh_tokens_success_with_secret(
        self, mock_compute_hash, mock_boto3, mock_auth_config, mock_cognito_client
    ):
        """Test successful token refresh with client secret."""
        mock_boto3.return_value = mock_cognito_client
        mock_compute_hash.return_value = "computed_secret_hash"

        # Setup successful response
        setup_cognito_success_response(
            mock_cognito_client,
            access_token="new_access_token_123",
            id_token="new_id_token_123",
            expires_in=3600,  # 1 hour
        )

        # Call refresh_tokens
        result = refresh_tokens(mock_auth_config, DEFAULT_REFRESH_TOKEN, verbose=False)

        # Verify result
        assert result is not None
        assert result.access_token == "new_access_token_123"
        assert result.id_token == "new_id_token_123"
        assert result.refresh_token == DEFAULT_REFRESH_TOKEN  # Original preserved
        assert result.expires_in == 3600

        # Verify Cognito client was called correctly
        mock_boto3.assert_called_once_with("cognito-idp", region_name="us-west-2")
        mock_cognito_client.initiate_auth.assert_called_once_with(
            AuthFlow="REFRESH_TOKEN_AUTH",
            ClientId="test_client_id",
            AuthParameters={
                "REFRESH_TOKEN": DEFAULT_REFRESH_TOKEN,
                "SECRET_HASH": "computed_secret_hash",
            },
        )

        # Verify secret hash was computed
        mock_compute_hash.assert_called_once_with(
            "testuser", "test_client_id", "test_secret"
        )

    def test_refresh_tokens_success_without_secret(self, mock_cognito_client):
        """Test successful token refresh without client secret."""

        # Config without secret
        config_no_secret = create_auth_config(client_secret=None, username=None)

        # Setup successful response
        setup_cognito_success_response(
            mock_cognito_client,
            access_token="new_access_token_456",
            id_token="new_id_token_456",
            expires_in=1800,  # 30 minutes
        )

        # Call refresh_tokens
        result = refresh_tokens(config_no_secret, DEFAULT_REFRESH_TOKEN, verbose=False)

        # Verify result
        assert result is not None
        assert result.access_token == "new_access_token_456"
        assert result.id_token == "new_id_token_456"
        assert result.expires_in == 1800

        # Verify Cognito client was called without SECRET_HASH
        mock_cognito_client.initiate_auth.assert_called_once_with(
            AuthFlow="REFRESH_TOKEN_AUTH",
            ClientId="test_client_id",
            AuthParameters={
                "REFRESH_TOKEN": DEFAULT_REFRESH_TOKEN,
            },
        )

    @patch("vcp.auth.oauth.boto3.client")
    def test_refresh_tokens_not_authorized_error(
        self, mock_boto3, mock_auth_config, mock_cognito_client
    ):
        """Test refresh tokens with NotAuthorizedException (expired refresh token)."""
        mock_boto3.return_value = mock_cognito_client

        # Setup error response
        setup_cognito_error_response(mock_cognito_client, "NotAuthorizedException")

        # Call refresh_tokens
        result = refresh_tokens(mock_auth_config, DEFAULT_REFRESH_TOKEN, verbose=False)

        # Should return None for expired refresh token
        assert result is None

    @patch("vcp.auth.oauth.boto3.client")
    def test_refresh_tokens_with_new_refresh_token_returned(
        self, mock_boto3, mock_auth_config, mock_cognito_client
    ):
        """Test refresh tokens when Cognito returns a new refresh token."""
        mock_boto3.return_value = mock_cognito_client

        # Setup response with new refresh token
        setup_cognito_success_response(
            mock_cognito_client,
            access_token="new_access_token",
            id_token="new_id_token",
            expires_in=3600,  # 1 hour
            refresh_token="new_refresh_token",  # New refresh token returned
        )

        # Call refresh_tokens
        result = refresh_tokens(mock_auth_config, DEFAULT_REFRESH_TOKEN, verbose=False)

        # Verify result - should use the NEW refresh token when provided by Cognito
        assert result is not None
        assert result.access_token == "new_access_token"
        assert result.id_token == "new_id_token"
        assert result.refresh_token == "new_refresh_token"  # Should use the new one
        assert result.expires_in == 3600

    @patch("vcp.auth.oauth.boto3.client")
    def test_refresh_tokens_no_new_refresh_token_returned(
        self, mock_boto3, mock_auth_config, mock_cognito_client
    ):
        """Test refresh tokens when Cognito doesn't return a new refresh token."""
        mock_boto3.return_value = mock_cognito_client

        # Setup response without new refresh token (typical case)
        setup_cognito_success_response(
            mock_cognito_client,
            access_token="refreshed_access_token",
            id_token="refreshed_id_token",
            expires_in=7200,  # 2 hours
            # No refresh_token parameter = no new refresh token
        )

        # Call refresh_tokens
        result = refresh_tokens(mock_auth_config, DEFAULT_REFRESH_TOKEN, verbose=False)

        # Verify result - should keep original refresh token
        assert result is not None
        assert result.access_token == "refreshed_access_token"
        assert result.id_token == "refreshed_id_token"
        assert result.refresh_token == DEFAULT_REFRESH_TOKEN  # Keep original
        assert result.expires_in == 7200
