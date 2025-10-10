import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vcp.config.config import Config

from .helpers import create_auth_config, create_mock_config_data


def mock_config_load():
    """Some tests require loading the config, so use a dummy one"""

    default_config_data = {
        "api": {
            "base_url": "https://api.default.com/v1",
            "endpoints": {
                "login": "/auth/login",
                "submit": "/api/models/submit",
                "download": "/api/models/download",
                "list": "/api/models/list",
            },
        },
        "data_api": {"base_url": "https://data.default.com"},
        "aws": {
            "region": "us-west-2",
            "cognito": {
                "user_pool_id": "default_pool",
                "client_id": "default_client",
                "client_secret": "default_secret",
                "domain": "default_domain",
            },
        },
        "databricks": {
            "host": "https://default.databricks.com",
            "token": "default-token",
        },
    }
    return Config._from_dict(default_config_data)


@pytest.fixture
def config_for_tests():
    """Patches Config.load() to return the dummy one"""
    with patch("vcp.config.config.Config.load", side_effect=mock_config_load):
        yield


@pytest.fixture
def current_version():
    """Get current version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    return match.group(1) if match else "0.43.0"


# Fixtures for auth testing
@pytest.fixture
def mock_cognito_client():
    """Fixture for mock AWS Cognito client."""
    with patch("vcp.auth.oauth.boto3.client") as mock_boto3:
        mock_cognito = Mock()
        mock_boto3.return_value = mock_cognito
        yield mock_cognito


@pytest.fixture
def mock_auth_config():
    """Standard AuthConfig for testing."""
    return create_auth_config()


@pytest.fixture
def mock_config_data():
    """Standard mock configuration data for AWS Cognito."""
    return create_mock_config_data()


@pytest.fixture
def temp_token_dir(tmp_path):
    """Fixture for temporary token directory using pytest's tmp_path."""
    return tmp_path
