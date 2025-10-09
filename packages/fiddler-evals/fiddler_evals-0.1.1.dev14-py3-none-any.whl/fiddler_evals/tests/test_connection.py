"""Tests for connection management functions."""

import pytest
import responses

from fiddler_evals import connection_context
from fiddler_evals.connection import Connection, get_connection, init, set_connection
from fiddler_evals.tests.constants import ORG_ID

SERVER_INFO_RESPONSE = {
    "data": {
        "server_version": "24.1.0-pre-3e889ef",
        "feature_flags": {},
        "organization": {"id": ORG_ID, "name": "Test Organization"},
    },
    "api_version": "3.0",
    "kind": "NORMAL",
}


class TestConnectionManagement:
    """Test core connection management functionality."""

    def test_set_connection(self):
        """Test setting a connection."""
        # Clear any existing connection
        connection_context.set(None)

        # Create a real connection object
        connection = Connection(
            url="https://test.fiddler.ai",
            token="test-token",
            validate=False,  # Skip validation for testing
        )

        # Set the connection
        set_connection(connection)

        # Verify the connection was set in the context
        assert connection_context.get() is connection

    def test_get_connection(self):
        """Test getting a connection."""
        # Clear any existing connection
        connection_context.set(None)

        # Test that no connection exists initially
        with pytest.raises(RuntimeError, match="No connection has been initialized"):
            get_connection()

        # Create and set a connection
        connection = Connection(
            url="https://test.fiddler.ai", token="test-token", validate=False
        )
        set_connection(connection)

        # Verify we can get the same connection back
        retrieved_connection = get_connection()
        assert retrieved_connection is connection
        assert retrieved_connection.url == "https://test.fiddler.ai"
        assert retrieved_connection.token == "test-token"

    @responses.activate
    def test_init_sets_connection(self):
        """Test that init method properly sets the connection."""
        # Clear any existing connection
        connection_context.set(None)

        # Mock the /v3/server-info endpoint
        responses.add(
            responses.GET,
            "https://test.fiddler.ai/v3/server-info",
            json=SERVER_INFO_RESPONSE,
            status=200,
        )

        # Test init with real Connection object
        init(
            url="https://test.fiddler.ai",
            token="test-token",
            validate=False,  # Skip validation for testing
        )

        # Verify connection was set and can be retrieved
        connection = get_connection()
        assert isinstance(connection, Connection)
        assert connection.url == "https://test.fiddler.ai"
        assert connection.token == "test-token"
        assert connection.verify is True  # Default value

    @responses.activate
    def test_init_with_custom_parameters(self):
        """Test init with custom parameters."""
        # Clear any existing connection
        connection_context.set(None)

        # Mock the /v3/server-info endpoint
        responses.add(
            responses.GET,
            "https://test.fiddler.ai/v3/server-info",
            json=SERVER_INFO_RESPONSE,
            status=200,
        )

        proxies = {"https": "https://proxy.example.com:8080"}
        timeout = (5.0, 30.0)

        init(
            url="https://test.fiddler.ai",
            token="test-token",
            proxies=proxies,
            timeout=timeout,
            verify=False,
            validate=False,
        )

        # Verify connection has correct parameters
        connection = get_connection()
        assert connection.url == "https://test.fiddler.ai"
        assert connection.token == "test-token"
        assert connection.proxies == proxies
        assert connection.timeout == timeout
        assert connection.verify is False

    def test_connection_client_passes_right_parameters(self):
        """Test that Connection client passes the right parameters to RequestClient."""
        # Clear any existing connection
        connection_context.set(None)

        # Create connection with specific parameters
        proxies = {"https": "https://proxy.example.com:8080"}
        timeout = (5.0, 30.0)

        connection = Connection(
            url="https://test.fiddler.ai",
            token="test-token",
            proxies=proxies,
            timeout=timeout,
            verify=False,
            validate=False,
        )

        # Mock RequestClient to verify parameters

        # Access the client property
        assert connection.client is not None
        assert connection.client._base_url == "https://test.fiddler.ai"
        assert connection.client._timeout == timeout
        assert connection.client.session.verify is False
        assert connection.client._proxies == proxies

    @responses.activate
    def test_init_populates_server_info_and_version(self):
        """Test that init populates server info and server version."""
        # Clear any existing connection
        connection_context.set(None)

        # Mock the /v3/server-info endpoint
        responses.add(
            responses.GET,
            "https://test.fiddler.ai/v3/server-info",
            json=SERVER_INFO_RESPONSE,
            status=200,
        )

        # Create connection with validation enabled
        connection = Connection(
            url="https://test.fiddler.ai", token="test-token", validate=True
        )

        # Verify server_info is populated with real data
        assert connection.server_info is not None
        assert connection.server_version == "24.1.0-pre-3e889ef"
        assert connection.organization_name == "Test Organization"
        assert str(connection.organization_id) == ORG_ID

    def test_init_validation_errors(self):
        """Test init with validation errors."""
        # Clear any existing connection
        connection_context.set(None)

        # Test with empty URL - should raise ValueError from Connection.__init__
        with pytest.raises(ValueError, match="`url` is empty"):
            init(url="", token="test-token")

        # Test with empty token - should raise ValueError from Connection.__init__
        with pytest.raises(ValueError, match="`token` is empty"):
            init(url="https://test.fiddler.ai", token="")

        # Test with None URL
        with pytest.raises(ValueError, match="`url` is empty"):
            init(url=None, token="test-token")

        # Test with None token
        with pytest.raises(ValueError, match="`token` is empty"):
            init(url="https://test.fiddler.ai", token=None)

    def test_connection_context_isolation(self):
        """Test that connection context is properly isolated."""
        # Clear any existing connection
        connection_context.set(None)

        # Verify no connection exists
        with pytest.raises(RuntimeError):
            get_connection()

        # Set a connection
        connection1 = Connection(
            url="https://test1.fiddler.ai", token="token1", validate=False
        )
        set_connection(connection1)

        # Verify we can get it
        assert get_connection() is connection1

        # Set a different connection
        connection2 = Connection(
            url="https://test2.fiddler.ai", token="token2", validate=False
        )
        set_connection(connection2)

        # Verify we get the new connection
        assert get_connection() is connection2
        assert get_connection() is not connection1
