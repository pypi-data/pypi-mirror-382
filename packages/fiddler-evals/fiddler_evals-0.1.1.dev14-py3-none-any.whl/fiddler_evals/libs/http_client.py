from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar
from json import dumps as json_dumps
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from fiddler_evals.configs import REQUEST_TIMEOUT_SECONDS
from fiddler_evals.constants import (
    CONTENT_TYPE_HEADER_KEY,
    CORRELATION_ID_HEADER_KEY,
    JSON_CONTENT_TYPE,
    REQUEST_ID_HEADER_KEY,
)
from fiddler_evals.libs.json_encoder import RequestClientJSONEncoder

logger = logging.getLogger(__name__)

retry_strategy = Retry(
    total=5,  # Maximum number of retries
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
    backoff_factor=2,  # Exponential backoff factor for delays between retries
)

correlation_context = ContextVar("correlation_id", default=None)


class RequestClient:
    """
    HTTP client supporting retries, connection pooling, and request tracking.

    This client provides a convenient interface for making HTTP requests with robust
    retry logic, configurable connection pooling, and automatic request/correlation ID
    tracking for observability.

    :param str base_url: The base URL for all requests. Must start with ``http://`` or ``https://``.
    :param dict headers: Default headers to include with every request.
    :param bool verify: Whether to verify the server's SSL certificate. Defaults to True.
    :param dict proxies: Proxy configuration for requests. Defaults to None.
    :param float|tuple timeout: Timeout for requests, either as a single float (applies to both connect and read timeouts)
        or a tuple of two floats: (connect timeout, read timeout). If not provided, a default is used.
    :param int|urllib3.util.Retry max_retries: Retry strategy for failed requests. Can be an integer (number of retries)
        or a :class:`urllib3.util.Retry` instance for advanced configuration (e.g., which status codes to retry, backoff factor, etc.).
        By default, retries up to 5 times on transient errors (429, 500, 502, 503, 504) with exponential backoff.
        Set to False to disable retries.
    :param int pool_connections: Number of connection pools to cache. Defaults to 10.
    :param int pool_maxsize: Maximum number of connections to save in the pool. Defaults to 10.

    **Example:**

    .. code-block:: python

        proxies = {
            "http": "http://10.10.1.10:3128",
            "https": "http://10.10.1.10:1080",
        }
        client = RequestClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"},
            proxies=proxies,
        )

    .. note::
        - The ``headers`` parameter sets default headers for all requests.
        - The ``timeout`` parameter controls how long the client waits for a server response.
        - The ``max_retries`` parameter configures the retry strategy for transient errors.
        - The ``pool_connections`` and ``pool_maxsize`` parameters control HTTP connection pooling.
        - The ``verify`` parameter controls SSL certificate verification.
        - The ``proxies`` parameter allows routing requests through a proxy server.
    """

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        verify: bool = True,
        proxies: dict | None = None,
        timeout: float | tuple[float, float] | None = REQUEST_TIMEOUT_SECONDS,
        max_retries: int | Retry = retry_strategy,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ) -> None:
        """
        Initialize the HTTP client.

        :raises ValueError: If base_url is invalid or timeout is negative
        :raises TypeError: If headers or proxies are not dictionaries
        """
        # Validate base_url
        self._validate_base_url(base_url)

        # Validate headers
        if not isinstance(headers, dict):
            raise TypeError("headers must be a dictionary")

        # Validate timeout
        self._validate_timeout(timeout)

        # Validate proxies
        if proxies is not None and not isinstance(proxies, dict):
            raise TypeError("proxies must be a dictionary or None")

        # Validate connection pool parameters
        if not isinstance(pool_connections, int) or pool_connections <= 0:
            raise ValueError("pool_connections must be a positive integer")

        if not isinstance(pool_maxsize, int) or pool_maxsize <= 0:
            raise ValueError("pool_maxsize must be a positive integer")

        # Normalize base_url (remove trailing slash)
        self._base_url = base_url.rstrip("/")
        self._proxies = proxies
        self._timeout = timeout
        self._default_headers = headers

        self.session = requests.Session()
        self.session.verify = verify

        # Configure connection pooling
        self._adapter = HTTPAdapter(
            max_retries=max_retries,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )

        # Mount the adapter to the session for both http and https
        self.session.mount("http://", self._adapter)
        self.session.mount("https://", self._adapter)

    def _validate_base_url(self, base_url: str) -> None:
        """
        Validate base_url format.

        :param base_url: URL to validate
        :raises ValueError: If URL is empty or doesn't start with http:// or https://
        """
        if not base_url:
            raise ValueError("base_url cannot be empty")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")

    def _validate_timeout(self, timeout: float | tuple[float, float] | None) -> None:
        """
        Validate timeout parameter.

        :param timeout: Timeout value to validate
        :raises ValueError: If timeout is negative or tuple has wrong length
        :raises TypeError: If timeout is not a number or tuple
        """
        if timeout is None:
            return

        if isinstance(timeout, (int, float)):
            if timeout <= 0:
                raise ValueError("timeout must be positive")
        elif isinstance(timeout, tuple):
            if len(timeout) != 2:
                raise ValueError("timeout tuple must have exactly 2 elements")
            if any(t <= 0 for t in timeout):
                raise ValueError("timeout values must be positive")
        else:
            raise TypeError("timeout must be a number or tuple of two numbers")

    def _make_request(
        self,
        *,
        method: str,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | bytes | None = None,
        json: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Send HTTP request with retry strategy and request tracking.


        This method automatically injects two headers for observability and traceability:

        - ``correlation_id``: Used to track a workflow or logical group of requests. If a correlation ID
          is set in the current context (via the context variable), it is used; otherwise, a new one is generated.
          This allows requests across different services or components to be correlated together.

        - ``request_id``: A unique identifier for this specific request. A new request ID is generated for
          every outgoing HTTP request, enabling fine-grained tracking and debugging of individual requests.


          Use json argument when explict serialization is not required. And use data with application/json content type
          header for explicit serialization.


        :param method: HTTP method (GET, POST, etc.)
        :param url: Request URL (relative or absolute)
        :param params: Query parameters
        :param headers: Request headers
        :param data: Request body data
        :param timeout: Request timeout override
        :param kwargs: Additional arguments passed to requests
        :return: HTTP response object
        :raises ValueError: If JSON serialization fails
        :raises requests.exceptions.RequestException: For HTTP/connection errors
        """

        _headers = self._default_headers.copy()
        if headers:
            # override/update headers coming from the calling method
            _headers.update(headers)

        content_type = _headers.get(CONTENT_TYPE_HEADER_KEY)
        if (
            isinstance(data, dict)
            and content_type
            and JSON_CONTENT_TYPE in content_type
        ):
            try:
                # Explicitly serialize here to use a custom JSON encoder.
                data = json_dumps(
                    data,
                    cls=RequestClientJSONEncoder,  # type: ignore
                )
            except (TypeError, ValueError) as e:
                raise ValueError(f"Failed to serialize data to JSON: {e}") from e

        # Set default behaviour
        kwargs.setdefault("allow_redirects", True)
        kwargs.setdefault("verify", self.session.verify)

        # Set timeout - use method parameter first, then instance default
        effective_timeout = timeout if timeout is not None else self._timeout
        kwargs["timeout"] = effective_timeout
        kwargs["proxies"] = self._proxies

        correlation_id = correlation_context.get() or str(uuid.uuid4())[:8]
        request_id = str(uuid.uuid4())[:8]

        # Add request ID to headers for individual request tracking and correlation ID for workflow tracking
        _headers[REQUEST_ID_HEADER_KEY] = request_id
        _headers[CORRELATION_ID_HEADER_KEY] = correlation_id

        # Construct full URL if relative
        if not url.startswith(("http://", "https://")):
            url = urljoin(self._base_url, url)

        # Use session.prepared_request() so that session.auth and adapter's
        # mounted on session apply.
        request = self.session.prepare_request(
            requests.Request(
                method=method,
                url=url,
                headers=_headers,
                data=data,
                json=json,
                params=params,
                files=kwargs.pop("files", None),
                auth=kwargs.pop("auth", None),
                cookies=kwargs.pop("cookies", None),
                hooks=kwargs.pop("hooks", None),
            )
        )
        start_time = time.monotonic()
        response = None
        try:
            # Send the HTTP request
            logger.debug(
                "[%s] Sending %s request to %s (params=%s, timeout=%s)",
                request_id,
                method,
                url,
                params,
                effective_timeout,
            )
            response = self.session.send(request, **kwargs)
            duration = time.monotonic() - start_time
            logger.debug(
                "[%s] Received %s response from %s in %.2f seconds (status_code=%s)",
                request_id,
                method,
                url,
                duration,
                response.status_code,
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            return response
        except requests.exceptions.Timeout as e:
            duration = time.monotonic() - start_time
            logger.error(
                "[%s] Request to %s timed out after %.2f seconds: %s",
                request_id,
                url,
                duration,
                e,
            )
            raise requests.exceptions.Timeout(
                f"Request to {url} timed out after {duration:.2f} seconds"
            ) from e
        except requests.exceptions.ConnectionError as e:
            logger.error("[%s] Connection error for %s: %s", request_id, url, e)
            raise requests.exceptions.ConnectionError(
                f"Failed to connect to {url}: {e}"
            ) from e
        except requests.exceptions.HTTPError as e:
            # response is guaranteed to exist for HTTPError since it's raised by raise_for_status()
            status_code = getattr(response, "status_code", "unknown")
            logger.error(
                "[%s] HTTP error for %s: %s (status_code=%s)",
                request_id,
                url,
                e,
                status_code,
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error("[%s] Request failed for %s: %s", request_id, url, e)
            raise requests.exceptions.RequestException(
                f"Request to {url} failed: {e}"
            ) from e

    def get(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Send GET request.

        :param url: Request URL
        :param params: Query parameters
        :param headers: Request headers
        :param timeout: Request timeout
        :param kwargs: Additional arguments
        :return: HTTP response
        """
        return self._make_request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Send DELETE request.

        :param url: Request URL
        :param params: Query parameters
        :param headers: Request headers
        :param timeout: Request timeout
        :param kwargs: Additional arguments
        :return: HTTP response
        """
        return self._make_request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def post(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        data: dict | bytes | None = None,
        json: dict | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Send POST request.

        :param url: Request URL
        :param params: Query parameters
        :param headers: Request headers
        :param timeout: Request timeout
        :param data: Request body data
        :param kwargs: Additional arguments
        :return: HTTP response
        """
        return self._make_request(
            method="POST",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            json=json,
            **kwargs,
        )

    def put(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        data: dict | bytes | None = None,
        json: dict | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Send PUT request.

        :param url: Request URL
        :param params: Query parameters
        :param headers: Request headers
        :param timeout: Request timeout
        :param data: Request body data
        :param kwargs: Additional arguments
        :return: HTTP response
        """
        return self._make_request(
            method="PUT",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            json=json,
            **kwargs,
        )

    def patch(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
        data: dict | None = None,
        json: dict | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Send PATCH request.

        :param url: Request URL
        :param params: Query parameters
        :param headers: Request headers
        :param timeout: Request timeout
        :param data: Request body data
        :param kwargs: Additional arguments
        :return: HTTP response
        """
        return self._make_request(
            method="PATCH",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            json=json,
            **kwargs,
        )
