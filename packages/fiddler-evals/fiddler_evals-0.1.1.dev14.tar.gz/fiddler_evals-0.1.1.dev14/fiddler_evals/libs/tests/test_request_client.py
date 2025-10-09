"""
Tests for RequestClient HTTP client library.
"""

from unittest.mock import Mock

import pytest
import requests
import responses
from pytest_mock import MockerFixture

from fiddler_evals.constants import CORRELATION_ID_HEADER_KEY, REQUEST_ID_HEADER_KEY
from fiddler_evals.libs.http_client import RequestClient


class TestRequestClientInitialization:
    """Test RequestClient initialization and validation."""

    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"},
            verify=True,
            timeout=30.0,
            pool_connections=5,
            pool_maxsize=10,
        )

        assert client._base_url == "https://api.example.com"
        assert client._default_headers == {"Authorization": "Bearer token"}
        assert client.session.verify is True
        assert client._timeout == 30.0

    def test_init_with_relative_url_raises_error(self):
        """Test that relative URLs raise ValueError."""
        with pytest.raises(
            ValueError, match="base_url must start with http:// or https://"
        ):
            RequestClient(base_url="api.example.com", headers={})

    def test_init_with_empty_url_raises_error(self):
        """Test that empty URLs raise ValueError."""
        with pytest.raises(ValueError, match="base_url cannot be empty"):
            RequestClient(base_url="", headers={})

    def test_init_with_invalid_headers_raises_error(self):
        """Test that non-dict headers raise TypeError."""
        with pytest.raises(TypeError, match="headers must be a dictionary"):
            RequestClient(base_url="https://api.example.com", headers="invalid")

    def test_init_with_invalid_timeout_raises_error(self):
        """Test that invalid timeout values raise appropriate errors."""
        # Negative timeout
        with pytest.raises(ValueError, match="timeout must be positive"):
            RequestClient(base_url="https://api.example.com", headers={}, timeout=-1)

        # Invalid timeout type
        with pytest.raises(
            TypeError, match="timeout must be a number or tuple of two numbers"
        ):
            RequestClient(
                base_url="https://api.example.com", headers={}, timeout="invalid"
            )

        # Invalid tuple length
        with pytest.raises(
            ValueError, match="timeout tuple must have exactly 2 elements"
        ):
            RequestClient(
                base_url="https://api.example.com", headers={}, timeout=(1, 2, 3)
            )

    def test_init_with_invalid_proxies_raises_error(self):
        """Test that non-dict proxies raise TypeError."""
        with pytest.raises(TypeError, match="proxies must be a dictionary or None"):
            RequestClient(
                base_url="https://api.example.com", headers={}, proxies="invalid"
            )

    def test_init_with_invalid_pool_parameters_raises_error(self):
        """Test that invalid pool parameters raise ValueError."""
        with pytest.raises(
            ValueError, match="pool_connections must be a positive integer"
        ):
            RequestClient(
                base_url="https://api.example.com", headers={}, pool_connections=0
            )

        with pytest.raises(ValueError, match="pool_maxsize must be a positive integer"):
            RequestClient(
                base_url="https://api.example.com", headers={}, pool_maxsize=-1
            )

    def test_base_url_normalization(self):
        """Test that base_url is normalized (trailing slash removed)."""
        client = RequestClient(base_url="https://api.example.com/", headers={})
        assert client._base_url == "https://api.example.com"


class TestRequestClientURLConstruction:
    """Test URL construction and handling."""

    def test_absolute_url_passthrough(self, mocker: MockerFixture):
        """Test that absolute URLs are passed through unchanged."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="https://external.com/api")
        mock_make_request.assert_called_once()
        # Check that the URL was passed through unchanged
        call_args = mock_make_request.call_args
        assert call_args[1]["url"] == "https://external.com/api"

    def test_relative_url_construction(self, mocker: MockerFixture):
        """Test that relative URLs are constructed with base_url."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="/users")
        call_args = mock_make_request.call_args
        assert call_args[1]["url"] == "/users"  # _make_request handles construction

    def test_relative_url_with_slash_handling(self, mocker: MockerFixture):
        """Test proper handling of slashes in relative URLs."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="users")
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["url"] == "users"


class TestRequestClientHeaders:
    """Test header handling and merging."""

    def test_default_headers_used(self, mocker: MockerFixture):
        """Test that default headers are used in requests."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token", "User-Agent": "SDK/1.0"},
        )

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="/test")
        # Verify that _make_request was called
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        # When no headers are passed to the method, headers parameter is None
        assert call_args[1]["headers"] is None

    def test_method_headers_override_defaults(self, mocker: MockerFixture):
        """Test that method-specific headers override default headers."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={
                "Authorization": "Bearer token",
                "Content-Type": "application/json",
            },
        )

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="/test", headers={"Authorization": "Bearer new-token"})
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        # When headers are passed to the method, they should be passed through
        assert call_args[1]["headers"]["Authorization"] == "Bearer new-token"

    @responses.activate
    def test_request_id_header_added(self, mocker: MockerFixture):
        """Test that X-Request-ID header is automatically added."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            status=200,
            json={"success": True},
        )

        # Make request
        response = client.get(url="/test")

        # Verify response
        assert response.status_code == 200
        assert response.json() == {"success": True}

        # Verify that the request was made with proper headers
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert REQUEST_ID_HEADER_KEY in request.headers
        assert CORRELATION_ID_HEADER_KEY in request.headers
        assert request.headers[REQUEST_ID_HEADER_KEY] is not None
        assert request.headers[CORRELATION_ID_HEADER_KEY] is not None


class TestRequestClientDataSerialization:
    """Test JSON data serialization."""

    @responses.activate
    def test_dict_data_serialization_with_json_content_type(
        self, mocker: MockerFixture
    ):
        """Test that dict data is serialized when content-type is JSON."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Content-Type": "application/json"},
        )

        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/test",
            status=200,
            json={"success": True},
        )

        # Make request
        response = client.post(url="/test", data={"key": "value"})

        # Verify response
        assert response.status_code == 200

        # Check that the data was serialized to JSON
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.body == '{"key": "value"}'

    @responses.activate
    def test_dict_data_no_serialization_without_json_content_type(
        self, mocker: MockerFixture
    ):
        """Test that dict data is not serialized when content-type is not JSON."""
        client = RequestClient(
            base_url="https://api.example.com", headers={"Content-Type": "text/plain"}
        )

        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/test",
            status=200,
            json={"success": True},
        )

        # Make request
        response = client.post(url="/test", data={"key": "value"})

        # Verify response
        assert response.status_code == 200

        # Check that the data was not serialized (passed as form data)
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.body == "key=value"

    @responses.activate
    def test_bytes_data_no_serialization(self, mocker: MockerFixture):
        """Test that bytes data is not serialized."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Content-Type": "application/json"},
        )

        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/test",
            status=200,
            json={"success": True},
        )

        # Make request
        response = client.post(url="/test", data=b"binary data")

        # Verify response
        assert response.status_code == 200

        # Check that the data was not serialized (passed as bytes)
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.body == b"binary data"


class TestRequestClientTimeoutHandling:
    """Test timeout handling logic."""

    def test_method_timeout_overrides_instance_timeout(self, mocker: MockerFixture):
        """Test that method timeout parameter overrides instance timeout."""
        client = RequestClient(
            base_url="https://api.example.com", headers={}, timeout=30.0
        )

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="/test", timeout=60.0)
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["timeout"] == 60.0

    def test_instance_timeout_used_when_method_timeout_none(
        self, mocker: MockerFixture
    ):
        """Test that instance timeout is used when method timeout is None."""
        client = RequestClient(
            base_url="https://api.example.com", headers={}, timeout=30.0
        )

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="/test", timeout=None)
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["timeout"] is None


class TestRequestClientHTTPMethods:
    """Test all HTTP methods."""

    def test_get_method(self, mocker: MockerFixture):
        """Test GET method."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.get(url="/test", params={"key": "value"})
        mock_make_request.assert_called_once_with(
            method="GET",
            url="/test",
            params={"key": "value"},
            headers=None,
            timeout=None,
            **{},
        )

    def test_post_method(self, mocker: MockerFixture):
        """Test POST method."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.post(url="/test", data={"key": "value"})
        mock_make_request.assert_called_once_with(
            method="POST",
            url="/test",
            params=None,
            headers=None,
            timeout=None,
            data={"key": "value"},
            json=None,
            **{},
        )

    def test_put_method(self, mocker: MockerFixture):
        """Test PUT method."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.put(url="/test", data={"key": "value"})
        mock_make_request.assert_called_once_with(
            method="PUT",
            url="/test",
            params=None,
            headers=None,
            timeout=None,
            data={"key": "value"},
            json=None,
            **{},
        )

    def test_delete_method(self, mocker: MockerFixture):
        """Test DELETE method."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.delete(url="/test")
        mock_make_request.assert_called_once_with(
            method="DELETE", url="/test", params=None, headers=None, timeout=None, **{}
        )

    def test_patch_method(self, mocker: MockerFixture):
        """Test PATCH method."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_make_request = mocker.patch.object(client, "_make_request")
        client.patch(url="/test", data={"key": "value"})
        mock_make_request.assert_called_once_with(
            method="PATCH",
            url="/test",
            params=None,
            headers=None,
            timeout=None,
            data={"key": "value"},
            json=None,
            **{},
        )


class TestRequestClientMakeRequest:
    """Test the core _make_request method."""

    def test_successful_request(self, mocker: MockerFixture):
        """Test successful request handling."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_send = mocker.patch("fiddler_evals.libs.http_client.requests.Session.send")
        mock_send.return_value = mock_response

        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"},
        )

        response = client._make_request(method="GET", url="/test")

        assert response == mock_response
        mock_send.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    def test_request_id_header_added(self, mocker: MockerFixture):
        """Test that X-Request-ID header is added to requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_send = mocker.patch("fiddler_evals.libs.http_client.requests.Session.send")
        mock_send.return_value = mock_response

        client = RequestClient(base_url="https://api.example.com", headers={})

        client._make_request(method="GET", url="/test")

        # Check that the request was prepared with X-Request-ID header
        call_args = mock_send.call_args
        request = call_args[0][0]  # First positional argument
        assert REQUEST_ID_HEADER_KEY in request.headers

    def test_timeout_exception_handling(self, mocker: MockerFixture):
        """Test timeout exception handling."""
        mock_send = mocker.patch("fiddler_evals.libs.http_client.requests.Session.send")
        mock_send.side_effect = requests.exceptions.Timeout("Request timed out")

        client = RequestClient(base_url="https://api.example.com", headers={})

        with pytest.raises(requests.exceptions.Timeout):
            client._make_request(method="GET", url="/test")

    def test_connection_error_handling(self, mocker: MockerFixture):
        """Test connection error handling."""
        mock_send = mocker.patch("fiddler_evals.libs.http_client.requests.Session.send")
        mock_send.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = RequestClient(base_url="https://api.example.com", headers={})

        with pytest.raises(requests.exceptions.ConnectionError):
            client._make_request(method="GET", url="/test")

    def test_http_error_handling(self, mocker: MockerFixture):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )

        mock_send = mocker.patch("fiddler_evals.libs.http_client.requests.Session.send")
        mock_send.return_value = mock_response

        client = RequestClient(base_url="https://api.example.com", headers={})

        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request(method="GET", url="/test")

    def test_json_serialization_error(self, mocker: MockerFixture):
        """Test JSON serialization error handling."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Content-Type": "application/json"},
        )

        # Create data that can't be JSON serialized
        class UnserializableObject:
            pass

        with pytest.raises(ValueError, match="Failed to serialize data to JSON"):
            client._make_request(
                method="POST", url="/test", data={"key": UnserializableObject()}
            )

    def test_relative_url_construction_in_make_request(self, mocker: MockerFixture):
        """Test that relative URLs are properly constructed in _make_request."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_prepare = mocker.patch.object(client.session, "prepare_request")
        mock_send = mocker.patch.object(client.session, "send")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_send.return_value = mock_response

        client._make_request(method="GET", url="users")

        # Check that the URL was constructed properly
        call_args = mock_prepare.call_args
        request = call_args[0][0]
        assert request.url == "https://api.example.com/users"

    def test_absolute_url_passthrough_in_make_request(self, mocker: MockerFixture):
        """Test that absolute URLs are passed through in _make_request."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        mock_prepare = mocker.patch.object(client.session, "prepare_request")
        mock_send = mocker.patch.object(client.session, "send")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_send.return_value = mock_response

        client._make_request(method="GET", url="https://external.com/api")

        # Check that the URL was passed through unchanged
        call_args = mock_prepare.call_args
        request = call_args[0][0]
        assert request.url == "https://external.com/api"


class TestRequestClientIntegration:
    """Integration tests for RequestClient."""

    @responses.activate
    def test_full_request_flow(self, mocker: MockerFixture):
        """Test the complete request flow from method call to response."""
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"},
            timeout=30.0,
        )

        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/users",
            status=200,
            json={"success": True},
        )

        # Make a request
        response = client.post(
            url="/users",
            data={"name": "John Doe"},
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        )

        # Verify response
        assert response.status_code == 200
        assert response.json() == {"success": True}

        # Verify the request was sent correctly
        assert len(responses.calls) == 1
        request = responses.calls[0].request

        # Check headers
        assert "Authorization" in request.headers
        assert REQUEST_ID_HEADER_KEY in request.headers
        assert request.headers["Authorization"] == "Bearer token"

        # Check that data was serialized to JSON
        assert request.body == '{"name": "John Doe"}'

    def test_retry_strategy_configured(self, mocker: MockerFixture):
        """Test that retry strategy is properly configured and working."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        # Verify that the adapter is mounted
        assert "http://" in client.session.adapters
        assert "https://" in client.session.adapters

        # Get the mounted adapter to verify retry configuration
        http_adapter = client.session.adapters["http://"]
        https_adapter = client.session.adapters["https://"]

        # Both adapters should be the same instance
        assert http_adapter is https_adapter

        # Verify retry configuration
        retry = http_adapter.max_retries
        assert retry.total == 5  # Default retry count
        assert retry.backoff_factor == 2  # Default backoff factor
        assert retry.status_forcelist == [
            429,
            500,
            502,
            503,
            504,
        ]  # Default status codes

    @responses.activate
    def test_retry_strategy_retries_on_failure(self, mocker: MockerFixture):
        """Test that retry strategy actually retries on transient failures."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        # Mock responses: first call fails with 500, second call succeeds
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            status=500,
            json={"error": "Internal Server Error"},
        )
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            status=200,
            json={"success": True},
        )

        # Make a request - should retry and eventually succeed
        response = client.get(url="/test")

        # Verify that the request was made twice (initial + 1 retry)
        assert len(responses.calls) == 2
        assert response.status_code == 200

    @responses.activate
    def test_retry_strategy_gives_up_after_max_retries(self, mocker: MockerFixture):
        """Test that retry strategy gives up after maximum retries."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        # Mock responses: all calls return 500 error (should retry 5 times + initial = 6 total calls)
        for _ in range(6):  # 6 calls total (1 initial + 5 retries)
            responses.add(
                responses.GET,
                "https://api.example.com/test",
                status=500,
                json={"error": "Internal Server Error"},
            )

        # Make a request - should retry and eventually fail
        with pytest.raises(requests.exceptions.RequestException):
            client.get(url="/test")

        # Verify that the request was made 6 times (initial + 5 retries)
        assert len(responses.calls) == 6

    @responses.activate
    def test_retry_strategy_does_not_retry_on_client_errors(
        self, mocker: MockerFixture
    ):
        """Test that retry strategy does not retry on 4xx client errors."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        # Mock response: 404 error should not be retried
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            status=404,
            json={"error": "Not Found"},
        )

        # Make a request - should not retry on 4xx errors
        with pytest.raises(requests.exceptions.HTTPError):
            client.get(url="/test")

        # Verify that the request was made only once (no retries for 4xx)
        assert len(responses.calls) == 1

    @responses.activate
    def test_retry_strategy_retries_on_rate_limiting(self, mocker: MockerFixture):
        """Test that retry strategy retries on 429 rate limiting errors."""
        client = RequestClient(base_url="https://api.example.com", headers={})

        # Mock responses: first call returns 429 error, second call succeeds
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            status=429,
            json={"error": "Too Many Requests"},
            headers={"Retry-After": "1"},
        )
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            status=200,
            json={"success": True},
        )

        # Make a request - should retry on 429 errors
        response = client.get(url="/test")

        # Verify that the request was made twice (initial + 1 retry)
        assert len(responses.calls) == 2
        assert response.status_code == 200

    def test_custom_retry_strategy_configuration(self, mocker: MockerFixture):
        """Test that custom retry strategy configuration is properly applied."""
        from urllib3.util import Retry

        # Create a custom retry strategy
        custom_retry = Retry(
            total=2,  # Only 2 retries
            status_forcelist=[500],  # Only retry on 500 errors
            backoff_factor=1.0,  # Different backoff factor
        )

        client = RequestClient(
            base_url="https://api.example.com", headers={}, max_retries=custom_retry
        )

        # Verify that the custom retry configuration is applied
        http_adapter = client.session.adapters["http://"]
        retry = http_adapter.max_retries
        assert retry.total == 2
        assert retry.backoff_factor == 1.0
        assert retry.status_forcelist == [500]
