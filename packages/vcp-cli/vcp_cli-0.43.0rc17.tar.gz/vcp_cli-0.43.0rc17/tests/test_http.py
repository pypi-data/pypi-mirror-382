"""Tests for HTTP utility module functionality."""

from unittest.mock import MagicMock, patch

import pytest
import requests_mock
from requests.exceptions import HTTPError

from vcp import __version__
from vcp.commands.benchmarks.utils import CLIError
from vcp.utils.http import get_json, get_user_agent, post_json


@pytest.fixture
def mock_requests():
    """Fixture that provides a requests mock for testing."""
    with requests_mock.Mocker() as m:
        # Set up default responses
        m.get(
            requests_mock.ANY,
            json={"data": "test"},
            headers={"Content-Type": "application/json"},
        )
        m.post(
            requests_mock.ANY,
            json={"result": "success"},
            headers={"Content-Type": "application/json"},
        )
        yield m


def test_get_user_agent():
    """Test that get_user_agent returns correct format."""
    user_agent = get_user_agent()
    assert user_agent == f"vcp-cli/{__version__}"


@patch("vcp.utils.http.TokenManager")
def test_get_json_adds_user_agent_and_accept_header(
    mock_token_manager_class, mock_requests
):
    """Test that get_json() adds user-agent and accept headers."""
    # Mock TokenManager to return no auth headers
    mock_token_manager = MagicMock()
    mock_token_manager.get_auth_headers.return_value = None
    mock_token_manager_class.return_value = mock_token_manager

    test_url = "https://api.example.com/test"

    # Make the request
    result = get_json(test_url)

    # Verify the headers were set correctly
    request = mock_requests.last_request
    assert request.headers["User-Agent"] == f"vcp-cli/{__version__}"
    assert request.headers["Accept"] == "application/json"

    # Verify JSON parsing is correct
    assert result == {"data": "test"}


def test_get_json_rejects_user_agent_override():
    """Test that get_json() rejects user-agent header override."""
    with pytest.raises(RuntimeError, match="Cannot override User-Agent header"):
        get_json("https://example.com", headers={"User-Agent": "old-agent"})


def test_get_json_rejects_accept_header_override():
    """Test that get_json() rejects accept header override."""
    with pytest.raises(RuntimeError, match="Cannot override Accept header"):
        get_json("https://example.com", headers={"Accept": "text/plain"})


@patch("vcp.utils.http.TokenManager")
def test_post_json_adds_user_agent_and_accept_header(
    mock_token_manager_class, mock_requests
):
    """Test that post_json() adds content-type for JSON requests."""
    # Mock TokenManager to return no auth headers
    mock_token_manager = MagicMock()
    mock_token_manager.get_auth_headers.return_value = None
    mock_token_manager_class.return_value = mock_token_manager

    test_url = "https://api.example.com/test"

    # Make the request
    result = post_json(test_url, json={"key": "value"})

    # Verify the headers were set correctly
    request = mock_requests.last_request
    assert request.headers["User-Agent"] == f"vcp-cli/{__version__}"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["Content-Type"] == "application/json"

    # Verify JSON parsing is correct
    assert result == {"result": "success"}


def test_post_json_rejects_user_agent_override():
    """Test that post_json() rejects user-agent header override."""
    with pytest.raises(RuntimeError, match="Cannot override User-Agent header"):
        post_json(
            "https://example.com",
            json={"key": "value"},
            headers={"User-Agent": "old-agent"},
        )


def test_post_json_rejects_accept_header_override():
    """Test that post_json() rejects accept header override."""
    with pytest.raises(RuntimeError, match="Cannot override Accept header"):
        post_json(
            "https://example.com",
            json={"key": "value"},
            headers={"Accept": "text/plain"},
        )


@patch("vcp.utils.http.TokenManager")
def test_get_json_adds_auth_token_when_available(
    mock_token_manager_class, mock_requests
):
    """Test that get_json() adds authentication token when available."""
    # Mock TokenManager to return auth headers
    mock_token_manager = MagicMock()
    mock_token_manager.get_auth_headers.return_value = {
        "Authorization": "Bearer test_token_123"
    }
    mock_token_manager_class.return_value = mock_token_manager

    test_url = "https://api.example.com/test"

    # Make the request
    result = get_json(test_url)

    # Verify the auth header was set correctly
    request = mock_requests.last_request
    assert request.headers["Authorization"] == "Bearer test_token_123"

    # Verify other headers are still set
    assert request.headers["User-Agent"] == f"vcp-cli/{__version__}"
    assert request.headers["Accept"] == "application/json"

    # Verify JSON parsing is correct
    assert result == {"data": "test"}


@patch("vcp.utils.http.TokenManager")
def test_post_json_adds_auth_token_when_available(
    mock_token_manager_class, mock_requests
):
    """Test that post_json() adds authentication token when available."""
    # Mock TokenManager to return auth headers
    mock_token_manager = MagicMock()
    mock_token_manager.get_auth_headers.return_value = {
        "Authorization": "Bearer test_token_456"
    }
    mock_token_manager_class.return_value = mock_token_manager

    test_url = "https://api.example.com/test"

    # Make the request
    result = post_json(test_url, json={"key": "value"})

    # Verify the auth header was set correctly
    request = mock_requests.last_request
    assert request.headers["Authorization"] == "Bearer test_token_456"

    # Verify other headers are still set
    assert request.headers["User-Agent"] == f"vcp-cli/{__version__}"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["Content-Type"] == "application/json"

    # Verify JSON parsing is correct
    assert result == {"result": "success"}


@patch("vcp.utils.http._get_session")
def test_get_json_errors_on_non_json_response(mock_get_session):
    """Test that get_json() raises error for non-JSON content-type."""

    mock_session = MagicMock()
    mock_get_session.return_value = mock_session
    mock_response = mock_session.get.return_value
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/plain"}
    mock_response.raise_for_status.return_value = None

    with pytest.raises(CLIError, match="Expected JSON response but got 'text/plain'"):
        get_json("https://example.com")


@patch("vcp.utils.http._get_session")
def test_get_json_handles_api_error_in_http_error_response(mock_get_session):
    """Test that get_json() raises CLIError for error details in HTTP error response."""
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session
    mock_response = mock_session.get.return_value
    mock_response.status_code = 400
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json.return_value = {"detail": "Bad request"}

    # Create HTTPError with response attached
    http_error = HTTPError("Bad Request")
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error

    with pytest.raises(CLIError, match="API Error: Bad request"):
        get_json("https://api.example.com/data")


@patch("vcp.utils.http._get_session")
def test_get_json_handles_401_error(mock_get_session):
    """Test that get_json() raises CLIError with authentication message for 401."""
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session
    mock_response = mock_session.get.return_value
    mock_response.status_code = 401
    http_error = HTTPError()
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error

    with pytest.raises(
        CLIError, match="Authentication failed. Please run 'vcp login'."
    ):
        get_json("https://api.example.com/data")
