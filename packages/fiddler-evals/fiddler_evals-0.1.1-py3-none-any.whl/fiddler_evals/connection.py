from __future__ import annotations

import logging
from functools import cached_property
from uuid import UUID

from fiddler_evals.constants import (
    CLIENT_NAME,
    FIDDLER_CLIENT_NAME_HEADER,
    FIDDLER_CLIENT_VERSION_HEADER,
)
from fiddler_evals.decorators import handle_api_error
from fiddler_evals.libs.http_client import RequestClient
from fiddler_evals.libs.semver import VersionInfo
from fiddler_evals.pydantic_models.server_info import ServerInfo
from fiddler_evals.version import __version__

logger = logging.getLogger(__name__)


class Connection:
    """Manages authenticated connections to the Fiddler platform.

    The Connection class handles all aspects of connecting to and communicating
    with the Fiddler platform, including authentication, HTTP client management,
    server version compatibility checking, and organization context management.

    This class provides the foundation for all API interactions with Fiddler,
    managing connection parameters, authentication tokens, and ensuring proper
    communication protocols are established.

    Attributes
    ----------
    url : str
        Base URL of the Fiddler platform instance
    token : str
        Authentication token for API access
    proxies : dict, optional
        Optional proxy configuration for HTTP requests
    timeout : float or tuple, optional
        HTTP request timeout settings
    verify : bool
        Whether to verify SSL/TLS certificates
    request_headers : dict
        HTTP headers including authentication and client info
    client : RequestClient
        Cached HTTP client instance for making requests
    server_info : ServerInfo
        Cached server information and metadata
    server_version : VersionInfo
        Version of the connected Fiddler server
    organization_name : str
        Name of the connected organization
    organization_id : UUID
        UUID of the connected organization

    Examples
    --------
    Creating a basic connection:

    .. code-block:: python

        connection = Connection(
            url="https://your-fiddler-instance.com",
            token="your-auth-token"
        )

    Creating a connection with custom timeout and proxy:

    .. code-block:: python

        connection = Connection(
            url="https://your-fiddler-instance.com",
            token="your-auth-token",
            timeout=(5.0, 30.0),  # (connect_timeout, read_timeout)
            proxies={"https": "https://proxy.company.com:8080"}
        )

    Creating a connection without SSL verification:

    .. code-block:: python

        connection = Connection(
            url="https://your-fiddler-instance.com",
            token="your-auth-token",
            verify=False,  # Not recommended for production
            validate=False  # Skip version compatibility check
        )
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str,
        token: str,
        proxies: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        verify: bool = True,
        validate: bool = True,
    ) -> None:
        """Initialize a connection to the Fiddler platform.

        Parameters
        ----------
        url : str
            The base URL to your Fiddler platform instance
        token : str
            Authentication token obtained from the Fiddler UI
        proxies : dict, optional
            Dictionary mapping protocol to proxy URL for HTTP requests
        timeout : float or tuple, optional
            HTTP request timeout settings (float or tuple of connect/read timeouts)
        verify : bool, default True
            Whether to verify server's TLS certificate
        validate : bool, default True
            Whether to validate server/client version compatibility

        Raises
        ------
        ValueError
            If url or token parameters are empty
        IncompatibleClient
            If server version is incompatible with client version
        """

        self.url = url
        self.token = token
        self.proxies = proxies
        self.timeout = timeout
        self.verify = verify

        if not url:
            raise ValueError("`url` is empty")

        if not token:
            raise ValueError("`token` is empty")

        self.request_headers = {
            "Authorization": f"Bearer {token}",
            FIDDLER_CLIENT_NAME_HEADER: CLIENT_NAME,
            FIDDLER_CLIENT_VERSION_HEADER: __version__,
        }

        if validate:
            self._check_server_version()
            self._check_version_compatibility()

    @cached_property
    def client(self) -> RequestClient:
        """Get the HTTP request client instance for API communication.

        Returns:
            RequestClient: Configured HTTP client with authentication headers,
            proxy settings, and timeout configurations.
        """
        return RequestClient(
            base_url=self.url,
            headers=self.request_headers,
            proxies=self.proxies,
            verify=self.verify,
            timeout=self.timeout,
        )

    @cached_property
    def server_info(self) -> ServerInfo:
        """Get server information and metadata from the Fiddler platform.

        Returns:
            ServerInfo: Server information including version, organization details,
            and platform configuration.
        """
        return self._get_server_info()

    @cached_property
    def server_version(self) -> VersionInfo:
        """Get the semantic version of the connected Fiddler server.

        Returns:
            VersionInfo: Semantic version object representing the server version.
        """
        return self.server_info.server_version

    @cached_property
    def organization_name(self) -> str:
        """Get the name of the connected organization.

        Returns:
            str: Name of the organization associated with this connection.
        """
        return self.server_info.organization.name

    @cached_property
    def organization_id(self) -> UUID:
        """Get the UUID of the connected organization.

        Returns:
            UUID: Unique identifier of the organization associated with this connection.
        """
        return self.server_info.organization.id

    @handle_api_error
    def _get_server_info(self) -> ServerInfo:
        """Retrieve server information from the Fiddler platform.

        Returns:
            ServerInfo: Server information including version and organization details.

        Raises:
            ApiError: If the server info request fails.
        """

        response = self.client.get(url="/v3/server-info")

        return ServerInfo(**response.json().get("data"))

    @handle_api_error
    def _check_version_compatibility(self) -> None:
        """Check whether the SDK version is compatible with the Fiddler platform version.

        Raises:
            ApiError: If the version compatibility check fails.
            IncompatibleClient: If the client version is not compatible with the server.
        """
        # @TODO https://github.com/fiddler-labs/fiddler/issues/14650

    def _check_server_version(self) -> None:
        """Check whether the Fiddler platform version is compatible with the client version.

        Raises:
            IncompatibleClient: If the server version is below the minimum required version.
        """
        # @TODO https://github.com/fiddler-labs/fiddler/issues/14650


class ConnectionMixin:
    """Mixin class providing connection-related functionality to other classes.

    ConnectionMixin provides a standardized way for other classes to access
    the global Fiddler connection instance and its associated properties.
    This mixin enables classes throughout the Fiddler client to access
    connection details, HTTP client functionality, and organization context
    without directly managing connection state.

    This pattern ensures consistent access to connection resources across
    all client components while maintaining a clean separation of concerns.

    Methods:
        _connection: Access to the global Connection instance
        _client: Access to the HTTP client for API requests
        organization_name: Property access to organization name
        organization_id: Property access to organization UUID
        get_organization_name: Class method to retrieve organization name
        get_organization_id: Class method to retrieve organization UUID

    Examples:
        Using ConnectionMixin in a custom class:

        class CustomModel(ConnectionMixin):
            def fetch_data(self):
                # Access HTTP client through mixin
                response = self._client().get('/api/data')
                return response.json()

            def get_org_info(self):
                # Access organization info through mixin
                return {
                    'name': self.organization_name,
                    'id': str(self.organization_id)
                }

        Using class methods without instantiation:

        org_name = SomeEntityClass.get_organization_name()
        org_id = SomeEntityClass.get_organization_id()
    """

    @classmethod
    def _connection(cls) -> Connection:
        """Get the global Fiddler connection instance.

        Returns:
            Connection: The singleton Connection instance used throughout the client.

        Raises:
            RuntimeError: If no connection has been initialized via fiddler_evals.init().
        """

        return get_connection()

    @classmethod
    def _client(cls) -> RequestClient:
        """Get the HTTP request client from the global connection.

        Returns:
            RequestClient: HTTP client instance for making API requests.
        """
        return cls._connection().client

    @property
    def organization_name(self) -> str:
        """Get the organization name from the connection.

        Returns:
            str: Name of the organization associated with the current connection.
        """
        return self._connection().server_info.organization.name

    @property
    def organization_id(self) -> UUID:
        """Get the organization UUID from the connection.

        Returns:
            UUID: Unique identifier of the organization associated with the current connection.
        """
        return self._connection().server_info.organization.id

    @classmethod
    def get_organization_name(cls) -> str:
        """Get the organization name from the global connection.

        Returns:
            str: Name of the organization associated with the current connection.
        """
        return cls._connection().server_info.organization.name

    @classmethod
    def get_organization_id(cls) -> UUID:
        """Get the organization UUID from the global connection.

        Returns:
            UUID: Unique identifier of the organization associated with the current connection.
        """
        return cls._connection().server_info.organization.id


def init(  # pylint: disable=too-many-arguments
    url: str,
    token: str,
    proxies: dict | None = None,
    timeout: float | tuple[float, float] | None = None,
    verify: bool = True,
    validate: bool = True,
) -> None:
    """Initialize the Fiddler client with connection parameters and global configuration.

    This function establishes a connection to the Fiddler platform and configures
    the global client state. It handles authentication, server compatibility
    validation, logging setup, and creates the singleton connection instance
    used throughout the client library.

    Args:
        url: The base URL to your Fiddler platform instance
        token: Authentication token obtained from the Fiddler UI Credentials tab
        proxies: Dictionary mapping protocol to proxy URL for HTTP requests
        timeout: HTTP request timeout settings (float or tuple of connect/read timeouts)
        verify: Whether to verify server's TLS certificate (default: True)
        validate: Whether to validate server/client version compatibility (default: True)

    Raises:
        ValueError: If url or token parameters are empty
        IncompatibleClient: If server version is incompatible with client version
        ConnectionError: If unable to connect to the Fiddler platform

    Examples:
        Basic initialization:

        import fiddler as fdl

        fdl.init(
            url="https://your-fiddler-instance.com",
            token="your-auth-token"
        )

        Initialization with custom timeout and proxy:

        fdl.init(
            url="https://your-fiddler-instance.com",
            token="your-auth-token",
            timeout=(10.0, 60.0),  # 10s connect, 60s read timeout
            proxies={"https": "https://proxy.company.com:8080"}
        )

        Initialization for development with relaxed settings:

        fdl.init(
            url="https://dev-fiddler-instance.com",
            token="dev-token",
            verify=False,  # Skip SSL verification
            validate=False,  # Skip version compatibility check
        )



    Note:
        The client implements automatic retry strategies for transient failures.
        Configure retry duration via FIDDLER_CLIENT_RETRY_MAX_DURATION_SECONDS
        environment variable (default: 300 seconds).

        Logging is performed under the 'fiddler' namespace at INFO level.
        If no root logger is configured, a stderr handler is automatically
        attached unless auto_attach_log_handler=False.
    """
    logger.info("Initializing Fiddler Evals SDK with version %s", __version__)
    # Singleton object in Python interpreter.
    conn = Connection(
        url=url,
        token=token,
        proxies=proxies,
        timeout=timeout,
        verify=verify,
        validate=validate,
    )
    set_connection(conn)

    logger.info(
        "Connection established successfully with Fiddler Platform version %s",
        conn.server_version,
    )


def get_connection() -> Connection:
    """Get the current global connection instance.

    Returns:
        Connection: The current connection instance.

    Raises
        AssertionError: If no connection has been initialized via fiddler_evals.init().
    """
    from fiddler_evals import (
        connection_context,  # pylint: disable=import-outside-toplevel
    )

    conn = connection_context.get()
    if conn is None:
        raise RuntimeError(
            "No connection has been initialized. Call fiddler_evals.init() first."
        )
    return conn


def set_connection(conn: Connection) -> None:
    """Set the current global connection instance.

    Args:
        conn: The connection instance to set.
    """
    from fiddler_evals import (
        connection_context,  # pylint: disable=import-outside-toplevel
    )

    connection_context.set(conn)
