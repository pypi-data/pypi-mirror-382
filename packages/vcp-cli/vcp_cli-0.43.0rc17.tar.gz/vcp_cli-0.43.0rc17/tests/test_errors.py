from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from vcp.utils.errors import (
    AuthenticationError,
    InvalidInputError,
    NetworkError,
    ResourceNotFoundError,
    ServerError,
    VCPError,
    VCPPermissionError,
    check_authentication_status,
    handle_http_error,
    handle_request_error,
    validate_dataset_id,
    validate_search_term,
    with_error_handling,
)


class TestVCPError:
    def test_basic_error_creation(self):
        error = VCPError("Test error")
        assert error.message == "Test error"
        assert error.suggestion is None

    def test_error_with_suggestion(self):
        error = VCPError("Test error", "Try this instead")
        assert error.message == "Test error"
        assert error.suggestion == "Try this instead"

    def test_show_method_without_suggestion(self, capsys):
        with patch("vcp.utils.errors.console") as mock_console:
            error = VCPError("Test error")
            error.show()
            mock_console.print.assert_called_once_with("[red]Error:[/red] Test error")

    def test_show_method_with_suggestion(self, capsys):
        with patch("vcp.utils.errors.console") as mock_console:
            error = VCPError("Test error", "Try this")
            error.show()
            assert mock_console.print.call_count == 2
            mock_console.print.assert_any_call("[red]Error:[/red] Test error")
            mock_console.print.assert_any_call("[yellow]Try this[/yellow]")


class TestAuthenticationError:
    def test_default_message(self):
        error = AuthenticationError()
        assert error.message == "Authentication required"
        assert error.suggestion == "Please run 'vcp login' to authenticate."

    def test_custom_message(self):
        error = AuthenticationError("Custom auth error")
        assert error.message == "Custom auth error"
        assert error.suggestion == "Please run 'vcp login' to authenticate."


class TestVCPPermissionError:
    def test_default_resource(self):
        error = VCPPermissionError()
        assert error.message == "Access denied for resource"
        assert "You don't have permission" in error.suggestion

    def test_custom_resource(self):
        error = VCPPermissionError("dataset xyz")
        assert error.message == "Access denied for dataset xyz"
        assert "You don't have permission" in error.suggestion


class TestResourceNotFoundError:
    def test_resource_not_found(self):
        error = ResourceNotFoundError("dataset", "abc123")
        assert error.message == "Dataset 'abc123' not found"
        assert error.suggestion == "Please check that the dataset ID is correct."

    def test_model_not_found(self):
        error = ResourceNotFoundError("model", "xyz456")
        assert error.message == "Model 'xyz456' not found"
        assert error.suggestion == "Please check that the model ID is correct."


class TestNetworkError:
    def test_default_message(self):
        error = NetworkError()
        assert error.message == "Network request failed"
        assert (
            error.suggestion == "Please check your internet connection and try again."
        )

    def test_custom_message(self):
        error = NetworkError("Connection timeout")
        assert error.message == "Connection timeout"
        assert (
            error.suggestion == "Please check your internet connection and try again."
        )


class TestServerError:
    def test_server_error_500(self):
        error = ServerError(500)
        assert error.message == "Server error occurred"
        assert error.suggestion is None

    def test_server_error_502(self):
        error = ServerError(502)
        assert error.message == "Server error occurred"
        assert "temporarily unavailable" in error.suggestion

    def test_server_error_503(self):
        error = ServerError(503)
        assert error.message == "Server error occurred"
        assert "temporarily unavailable" in error.suggestion

    def test_server_error_504(self):
        error = ServerError(504)
        assert error.message == "Server error occurred"
        assert "temporarily unavailable" in error.suggestion

    def test_service_error_400(self):
        error = ServerError(400)
        assert error.message == "Server error occurred"
        assert error.suggestion is None

    def test_default_error(self):
        error = ServerError()
        assert error.message == "Server error occurred"
        assert error.suggestion is None


class TestInvalidInputError:
    def test_input_error_without_details(self):
        error = InvalidInputError("email")
        assert error.message == "Invalid email"
        assert error.suggestion == "Please check your email format and try again."

    def test_input_error_with_details(self):
        error = InvalidInputError("email", "must contain @ symbol")
        assert error.message == "Invalid email: must contain @ symbol"
        assert error.suggestion == "Please check your email format and try again."


class TestHandleHttpError:
    def create_mock_http_error(self, status_code):
        response = Mock()
        response.status_code = status_code
        error = HTTPError()
        error.response = response
        return error

    def test_401_error(self):
        error = self.create_mock_http_error(401)
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            handle_http_error(error)

    def test_403_error_with_resource_id(self):
        error = self.create_mock_http_error(403)
        with pytest.raises(
            VCPPermissionError, match="Access denied for dataset 'abc123'"
        ):
            handle_http_error(error, "dataset", "abc123")

    def test_403_error_without_resource_id(self):
        error = self.create_mock_http_error(403)
        with pytest.raises(VCPPermissionError, match="Access denied for dataset"):
            handle_http_error(error, "dataset")

    def test_404_error_with_resource_id(self):
        error = self.create_mock_http_error(404)
        with pytest.raises(ResourceNotFoundError, match="Dataset 'abc123' not found"):
            handle_http_error(error, "dataset", "abc123")

    def test_404_error_without_resource_id(self):
        error = self.create_mock_http_error(404)
        with pytest.raises(VCPError, match="Dataset not found"):
            handle_http_error(error, "dataset")

    def test_500_error(self):
        error = self.create_mock_http_error(500)
        with pytest.raises(ServerError):
            handle_http_error(error)

    def test_400_error(self):
        error = self.create_mock_http_error(400)
        with pytest.raises(ServerError):
            handle_http_error(error)


class TestHandleRequestError:
    def test_timeout_error(self):
        error = Timeout()
        with pytest.raises(NetworkError, match="Request timed out"):
            handle_request_error(error)

    def test_connection_error(self):
        error = ConnectionError()
        with pytest.raises(NetworkError, match="Unable to connect to the service"):
            handle_request_error(error)

    def test_generic_request_error(self):
        error = RequestException("Something went wrong")
        with pytest.raises(NetworkError, match="Request failed: Something went wrong"):
            handle_request_error(error)


class TestWithErrorHandling:
    def test_vcp_error_passthrough(self):
        @with_error_handling("dataset", "test")
        def func():
            raise AuthenticationError("Not authenticated")

        with pytest.raises(AuthenticationError, match="Not authenticated"):
            func()

    def test_http_error_handling(self):
        @with_error_handling("dataset", "test")
        def func(dataset_id=None):
            response = Mock()
            response.status_code = 404
            error = HTTPError()
            error.response = response
            raise error

        with pytest.raises(ResourceNotFoundError):
            func(dataset_id="abc123")

    def test_request_error_handling(self):
        @with_error_handling("dataset", "test")
        def func():
            raise Timeout()

        with pytest.raises(NetworkError, match="Request timed out"):
            func()

    def test_file_not_found_error(self):
        @with_error_handling("dataset", "test")
        def func():
            raise FileNotFoundError("No such file")

        with pytest.raises(VCPError, match="File not found"):
            func()

    def test_permission_error_system(self):
        resource = "dataset"

        @with_error_handling("dataset", "test")
        def func():
            raise VCPPermissionError(resource)

        with pytest.raises(VCPError, match=f"Access denied for {resource}"):
            func()

    def test_generic_exception(self):
        @with_error_handling("dataset", "test")
        def func():
            raise ValueError("Something bad happened")

        with pytest.raises(VCPError, match="An unexpected error occurred during test"):
            func()

    def test_resource_id_extraction(self):
        @with_error_handling("dataset", "test")
        def func(dataset_id=None, model_id=None, id=None):
            response = Mock()
            response.status_code = 404
            error = HTTPError()
            error.response = response
            raise error

        with pytest.raises(ResourceNotFoundError, match="Dataset 'data123' not found"):
            func(dataset_id="data123")

        with pytest.raises(ResourceNotFoundError, match="Dataset 'model456' not found"):
            func(model_id="model456")

        with pytest.raises(
            ResourceNotFoundError, match="Dataset 'generic789' not found"
        ):
            func(id="generic789")


class TestValidateDatasetId:
    def test_valid_dataset_id(self):
        # Should not raise
        validate_dataset_id("688bc7fe111f194a9ff123abc")

    def test_empty_dataset_id(self):
        with pytest.raises(InvalidInputError, match="ID cannot be empty"):
            validate_dataset_id("")

    def test_short_dataset_id(self):
        with pytest.raises(InvalidInputError, match="not a valid format"):
            validate_dataset_id("a" * 19)

    @pytest.mark.parametrize(
        "invalid_id",
        [
            "abc_def_123456789012345",
            "invalid*chars!@#",
            "with space 1234567890",
        ],
    )
    def test_invalid_characters(self, invalid_id):
        with pytest.raises(InvalidInputError, match="not a valid format"):
            validate_dataset_id(invalid_id)

    def test_special_characters_allowed(self):
        # Should not raise - hyphens are allowed
        validate_dataset_id("35e73102-1234-5678-9abc-86bb587102bf")

    def test_only_number_dataset_id(self):
        validate_dataset_id("123456789012345678901234567890")

    def test_only_char_dataset_id(self):
        validate_dataset_id("a" * 20)


class TestValidateSearchTerm:
    def test_valid_search_term(self):
        # Should not raise
        validate_search_term("cancer research")

    def test_empty_search_term(self):
        with pytest.raises(InvalidInputError, match="Search term cannot be empty"):
            validate_search_term("")

    def test_whitespace_only_search_term(self):
        with pytest.raises(InvalidInputError, match="Search term cannot be empty"):
            validate_search_term("   ")


class TestCheckAuthenticationStatus:
    def test_authenticated_user(self):
        tokens = Mock()
        # Should not raise
        check_authentication_status(tokens)

    def test_unauthenticated_user(self):
        with pytest.raises(AuthenticationError, match="Not authenticated"):
            check_authentication_status(None)
