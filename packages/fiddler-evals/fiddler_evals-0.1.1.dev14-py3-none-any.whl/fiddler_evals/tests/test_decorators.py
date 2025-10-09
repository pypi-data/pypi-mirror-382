"""Tests for the handle_api_error decorator."""

from unittest.mock import Mock

import pytest
import requests

from fiddler_evals.decorators import handle_api_error
from fiddler_evals.exceptions import ApiError, Conflict, NotFound, Unsupported


class TestHandleApiError:
    """Test cases for the handle_api_error decorator."""

    def test_successful_request(self):
        """Test that successful requests pass through unchanged."""

        @handle_api_error
        def successful_request():
            return {"status": "success"}

        result = successful_request()
        assert result == {"status": "success"}

    def test_json_decode_error(self):
        """Test handling of JSON decode errors."""

        @handle_api_error
        def json_decode_request():
            raise requests.JSONDecodeError("Invalid JSON", "doc", 0)

        with pytest.raises(ApiError) as exc_info:
            json_decode_request()

        assert "Invalid JSON response" in str(exc_info.value)

    def test_timeout_error(self):
        """Test handling of timeout errors."""

        @handle_api_error
        def timeout_request():
            raise requests.exceptions.Timeout("Request timed out")

        with pytest.raises(requests.exceptions.Timeout) as exc_info:
            timeout_request()

        assert "Request timed out" in str(exc_info.value)

    def test_connection_error(self):
        """Test handling of connection errors."""

        @handle_api_error
        def connection_request():
            raise requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
            connection_request()

        assert "Connection failed" in str(exc_info.value)

    def test_conflict_error(self):
        """Test handling of 409 Conflict errors."""

        @handle_api_error
        def conflict_request():
            response = Mock()
            response.status_code = 409
            response.json.return_value = {
                "error": {
                    "code": 409,
                    "message": "Resource already exists",
                    "errors": [
                        {
                            "reason": "CONFLICT",
                            "message": "Resource already exists",
                            "help": "Try updating the existing resource instead",
                        }
                    ],
                },
                "api_version": "3.0",
                "kind": "ERROR",
            }
            response.content = (
                b'{"error": {"code": 409, "message": "Resource already exists"}}'
            )

            http_error = requests.HTTPError("Conflict")
            http_error.response = response
            http_error.request = Mock()
            http_error.request.url = "https://api.example.com/resource"
            http_error.request.method = "POST"
            raise http_error

        with pytest.raises(Conflict) as exc_info:
            conflict_request()

        assert exc_info.value.message == "Resource already exists"
        assert exc_info.value.status_code == 409
        assert exc_info.value.reason == "CONFLICT"

    def test_not_found_error(self):
        """Test handling of 404 Not Found errors."""

        @handle_api_error
        def not_found_request():
            response = Mock()
            response.status_code = 404
            response.json.return_value = {
                "error": {
                    "code": 404,
                    "message": "Resource not found",
                    "errors": [
                        {
                            "reason": "NOT_FOUND",
                            "message": "Resource not found",
                            "help": "Check the resource identifier and try again",
                        }
                    ],
                },
                "api_version": "3.0",
                "kind": "ERROR",
            }
            response.content = (
                b'{"error": {"code": 404, "message": "Resource not found"}}'
            )

            http_error = requests.HTTPError("Not Found")
            http_error.response = response
            http_error.request = Mock()
            http_error.request.url = "https://api.example.com/resource"
            http_error.request.method = "GET"
            raise http_error

        with pytest.raises(NotFound) as exc_info:
            not_found_request()

        assert exc_info.value.message == "Resource not found"
        assert exc_info.value.status_code == 404
        assert exc_info.value.reason == "NOT_FOUND"

    def test_method_not_allowed_error(self):
        """Test handling of 405 Method Not Allowed errors."""

        @handle_api_error
        def method_not_allowed_request():
            response = Mock()
            response.status_code = 405
            response.json.return_value = {
                "error": {
                    "code": 405,
                    "message": "Method not allowed",
                    "errors": [
                        {
                            "reason": "METHOD_NOT_ALLOWED",
                            "message": "Method not allowed",
                            "help": "Use a supported HTTP method for this endpoint",
                        }
                    ],
                },
                "api_version": "3.0",
                "kind": "ERROR",
            }
            response.content = (
                b'{"error": {"code": 405, "message": "Method not allowed"}}'
            )

            http_error = requests.HTTPError("Method Not Allowed")
            http_error.response = response
            http_error.request = Mock()
            http_error.request.url = "https://api.example.com/resource"
            http_error.request.method = "DELETE"
            raise http_error

        with pytest.raises(Unsupported) as exc_info:
            method_not_allowed_request()

        assert exc_info.value.message == "Method not allowed"
        assert exc_info.value.status_code == 405
        assert exc_info.value.reason == "METHOD_NOT_ALLOWED"

    def test_generic_api_error(self):
        """Test handling of generic API errors."""

        @handle_api_error
        def generic_api_request():
            response = Mock()
            response.status_code = 500
            response.json.return_value = {
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "errors": [
                        {
                            "reason": "INTERNAL_ERROR",
                            "message": "Internal server error",
                            "help": "Please try again later or contact support",
                        }
                    ],
                },
                "api_version": "3.0",
                "kind": "ERROR",
            }
            response.content = (
                b'{"error": {"code": 500, "message": "Internal server error"}}'
            )

            http_error = requests.HTTPError("Internal Server Error")
            http_error.response = response
            http_error.request = Mock()
            http_error.request.url = "https://api.example.com/resource"
            http_error.request.method = "GET"
            raise http_error

        with pytest.raises(ApiError) as exc_info:
            generic_api_request()

        assert exc_info.value.message == "Internal server error"
        assert exc_info.value.status_code == 500
        assert exc_info.value.reason == "INTERNAL_ERROR"

    def test_structured_error_response_parsing(self):
        """Test that structured error responses are properly parsed and error details are accessible."""

        @handle_api_error
        def structured_error_request():
            response = Mock()
            response.status_code = 400
            response.json.return_value = {
                "error": {
                    "code": 400,
                    "message": "Validation failed",
                    "errors": [
                        {
                            "reason": "VALIDATION_ERROR",
                            "message": "Field 'name' is required",
                            "help": "Please provide a valid name for the resource",
                        },
                        {
                            "reason": "VALIDATION_ERROR",
                            "message": "Field 'email' must be a valid email address",
                            "help": "Please provide a valid email address",
                        },
                    ],
                },
                "api_version": "3.0",
                "kind": "ERROR",
            }
            response.content = (
                b'{"error": {"code": 400, "message": "Validation failed"}}'
            )

            http_error = requests.HTTPError("Bad Request")
            http_error.response = response
            http_error.request = Mock()
            http_error.request.url = "https://api.example.com/resource"
            http_error.request.method = "POST"
            raise http_error

        with pytest.raises(ApiError) as exc_info:
            structured_error_request()

        assert exc_info.value.message == "Validation failed"
        assert exc_info.value.status_code == 400
        assert exc_info.value.reason == "VALIDATION_ERROR"

        # Test that error response is accessible
        assert exc_info.value.error_response is not None
        assert exc_info.value.error_response.error.code == 400
        assert exc_info.value.error_response.error.message == "Validation failed"
        assert len(exc_info.value.error_response.error.errors) == 2
        assert (
            exc_info.value.error_response.error.errors[0].reason == "VALIDATION_ERROR"
        )
        assert (
            exc_info.value.error_response.error.errors[0].message
            == "Field 'name' is required"
        )
        assert (
            exc_info.value.error_response.error.errors[0].help
            == "Please provide a valid name for the resource"
        )
        assert (
            exc_info.value.error_response.error.errors[1].reason == "VALIDATION_ERROR"
        )
        assert (
            exc_info.value.error_response.error.errors[1].message
            == "Field 'email' must be a valid email address"
        )
        assert (
            exc_info.value.error_response.error.errors[1].help
            == "Please provide a valid email address"
        )

    def test_error_without_structured_response(self):
        """Test handling of errors without structured JSON response."""

        @handle_api_error
        def unstructured_error_request():
            response = Mock()
            response.status_code = 400
            response.json.side_effect = requests.JSONDecodeError(
                "Invalid JSON", "doc", 0
            )
            response.content = b"Invalid response"

            http_error = requests.HTTPError("Bad Request")
            http_error.response = response
            http_error.request = Mock()
            http_error.request.url = "https://api.example.com/resource"
            http_error.request.method = "POST"
            raise http_error

        with pytest.raises(ApiError) as exc_info:
            unstructured_error_request()

        assert "HTTP 400 error" in str(exc_info.value)
        assert exc_info.value.status_code == 400

    def test_generic_request_exception(self):
        """Test handling of generic request exceptions."""

        @handle_api_error
        def generic_request():
            raise requests.exceptions.RequestException("Generic request error")

        with pytest.raises(ApiError) as exc_info:
            generic_request()

        assert "Request failed" in str(exc_info.value)

    def test_preserves_function_metadata(self):
        """Test that the decorator preserves function metadata."""

        @handle_api_error
        def test_function(arg1: str, arg2: int = 42) -> str:
            """Test function with docstring."""
            return f"{arg1}_{arg2}"

        # Check that metadata is preserved
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function with docstring."
        assert test_function.__annotations__ == {
            "arg1": str,
            "arg2": int,
            "return": str,
        }
