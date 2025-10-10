"""Common test utilities for authentication and token management tests."""

import time
from unittest.mock import Mock

from botocore.exceptions import ClientError

from vcp.auth.oauth import AuthConfig
from vcp.utils.token import TokenStore


def create_token_store(
    access_token="test_access",
    id_token="test_id",
    refresh_token="test_refresh",
    expires_in=3600,
    expired=False,
    expires_in_minutes=None,
):
    """
    Factory for creating TokenStore instances with sensible defaults.

    Args:
        access_token: Access token value
        id_token: ID token value
        refresh_token: Refresh token value (None to exclude)
        expires_in: Expiration time in seconds
        expired: If True, set token to already be expired
        expires_in_minutes: If set, token expires in this many minutes from now

    Returns:
        TokenStore instance
    """
    tokens = TokenStore(
        access_token=access_token,
        id_token=id_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )

    # Override expires_at after model_post_init has run
    if expired:
        tokens.expires_at = int(time.time()) - 1000
    elif expires_in_minutes:
        tokens.expires_at = int(time.time()) + (expires_in_minutes * 60)

    return tokens


def create_auth_config(
    user_pool_id="us-west-2_TestPool",
    client_id="test_client_id",
    client_secret="test_secret",
    domain="test.auth.region.amazoncognito.com",
    region="us-west-2",
    username="testuser",
    flow="refresh",
):
    """
    Factory for creating AuthConfig instances with test defaults.

    Args:
        user_pool_id: AWS Cognito user pool ID
        client_id: OAuth client ID
        client_secret: OAuth client secret (None to exclude)
        domain: Cognito domain
        region: AWS region
        username: Username (None to exclude)
        flow: Authentication flow type

    Returns:
        AuthConfig instance
    """
    return AuthConfig(
        user_pool_id=user_pool_id,
        client_id=client_id,
        client_secret=client_secret,
        domain=domain,
        region=region,
        username=username,
        flow=flow,
    )


def setup_cognito_success_response(
    mock_cognito,
    access_token="new_access_token",
    id_token="new_id_token",
    expires_in=3600,
    refresh_token=None,
):
    """
    Setup mock Cognito client to return successful token refresh response.

    Args:
        mock_cognito: Mock Cognito client instance
        access_token: Access token to return
        id_token: ID token to return
        expires_in: Expiration time in seconds
        refresh_token: Refresh token to include (None to exclude)
    """
    response = {
        "AuthenticationResult": {
            "AccessToken": access_token,
            "IdToken": id_token,
            "ExpiresIn": expires_in,
        }
    }

    if refresh_token:
        response["AuthenticationResult"]["RefreshToken"] = refresh_token

    mock_cognito.initiate_auth.return_value = response


def setup_cognito_error_response(mock_cognito, error_code="NotAuthorizedException"):
    """
    Setup mock Cognito client to return an error response.

    Args:
        mock_cognito: Mock Cognito client instance
        error_code: AWS error code to simulate
    """
    mock_cognito.initiate_auth.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": error_code,
                "Message": f"Mock {error_code} error",
            }
        },
        operation_name="InitiateAuth",
    )


def create_mock_config_data(
    user_pool_id="us-west-2_TestPool",
    client_id="test_client_id",
    client_secret="test_secret",
    domain="test.auth.region.amazoncognito.com",
    region="us-west-2",
):
    """
    Create mock configuration data for AWS Cognito.

    Args:
        user_pool_id: AWS Cognito user pool ID
        client_id: OAuth client ID
        client_secret: OAuth client secret
        domain: Cognito domain
        region: AWS region

    Returns:
        Mock configuration object
    """
    mock_config = Mock()
    mock_config.aws.cognito.user_pool_id = user_pool_id
    mock_config.aws.cognito.client_id = client_id
    mock_config.aws.cognito.client_secret = client_secret
    mock_config.aws.cognito.domain = domain
    mock_config.aws.region = region
    return mock_config


# Common test data constants
DEFAULT_REFRESH_TOKEN = "valid_refresh_token_123"
DEFAULT_EXPIRED_ACCESS = "expired_access_token"
DEFAULT_EXPIRED_ID = "expired_id_token"
DEFAULT_NEW_ACCESS = "refreshed_access_token"
DEFAULT_NEW_ID = "refreshed_id_token"
