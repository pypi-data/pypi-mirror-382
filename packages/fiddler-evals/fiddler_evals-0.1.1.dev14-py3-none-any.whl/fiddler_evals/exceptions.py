from __future__ import annotations

from typing import TYPE_CHECKING

from fiddler_evals.version import __version__

if TYPE_CHECKING:
    from fiddler_evals.pydantic_models.response import ErrorResponse


class FiddlerEvalException(Exception):
    """Base exception class for Fiddler errors.

    This is the parent class for all custom exceptions in the Fiddler client
    library. It provides common functionality for error handling, message
    formatting, and error identification.

    Attributes
    ----------
    message : str
        Human-readable error message describing the issue
    name : str
        Name of the specific error type (class name)

    Examples
    --------
    Catching any Fiddler-specific error:

    .. code-block:: python

        try:
            # Some Fiddler operation
            pass
        except FiddlerEvalException as e:
            print(f"Fiddler error occurred: {e.name} - {e.message}")
    """

    message: str = "Something went wrong"

    def __init__(self, message: str | None = None) -> None:
        """Initialize the exception with an optional message.

        :param message: optional custom error message
        """
        self.message = message or self.message
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception.

        :return: formatted error message with error name
        """
        return f"{self.name}: {self.message}"

    @property
    def name(self) -> str:
        """Name of the error type."""
        return self.__class__.__name__


class IncompatibleClient(FiddlerEvalException):
    """Raised when the SDK version is incompatible with the Fiddler platform version.

    This exception occurs during connection initialization when the evals SDK
    version is not compatible with the connected Fiddler platform version. This
    ensures that users are aware of version mismatches that could cause unexpected
    behavior or missing functionality.

    The exception includes both the client version and server version in the error
    message to help users understand what versions are involved in the incompatibility.

    Attributes
    ----------
    message : str
        Formatted message showing both client and server versions

    Examples
    --------
    Handling version incompatibility:

    .. code-block:: python

        try:
            fdl.init(url="https://old-fiddler.com", token="token")
        except IncompatibleClient as e:
            print(f"Version mismatch: {e.message}")
            # Upgrade client or contact administrator

    Typical error message format:
    "Python Client version (3.8.0) is not compatible with your
    Fiddler Platform version (3.5.0)."
    """

    message = (
        "Fiddler Evals SDK version ({client_version}) is not compatible with your "
        "Fiddler Platform version ({server_version})."
    )

    def __init__(self, server_version: str, message: str | None = None) -> None:
        """Initialize the incompatible client exception.

        :param server_version: version of the Fiddler server
        :param message: optional custom error message
        """
        self.message = message or self.message.format(
            client_version=__version__, server_version=server_version
        )

        super().__init__(self.message)


class ApiError(FiddlerEvalException):
    """Raised when an API request fails with a structured error response.

    This exception is raised when the Fiddler API returns an error response
    that can be parsed into a structured error format. It provides access to
    the detailed error information returned by the server.

    Attributes
    ----------
    message : str
        Human-readable error message from the API
    status_code : int, optional
        HTTP status code of the failed request
    reason : str, optional
        Specific reason from the API response
    error_response : ErrorResponse, optional
        Full structured error response object
    """

    message = "An error occurred while making the API request"

    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        reason: str | None = None,
        error_response: ErrorResponse | None = None,
    ) -> None:
        """Initialize the API error exception.

        :param message: Error message from the API
        :param status_code: HTTP status code of the failed request
        :param reason: Specific reason from the API response
        :param error_response: Full structured error response object
        """
        self.status_code = status_code
        self.reason = reason or self.name
        self.error_response = error_response
        super().__init__(message)


class Conflict(ApiError):
    """Raised when a request conflicts with the current state of the resource.

    This exception is raised when attempting to perform an operation that
    conflicts with the current state of a resource, such as creating a
    resource that already exists or updating a resource that has been
    modified by another process.

    Examples
    --------
    .. code-block:: python

        try:
            client.create_model("existing-model")
        except Conflict as e:
            print(f"Resource conflict: {e.message}")
    """

    message = "The request conflicts with the current state of the resource"


class NotFound(ApiError):
    """Raised when a requested resource is not found.

    This exception is raised when attempting to access a resource that
    doesn't exist or has been deleted.

    Examples
    --------
    .. code-block:: python

        try:
            client.get_model("non-existent-model")
        except NotFound as e:
            print(f"Resource not found: {e.message}")
    """

    message = "The requested resource was not found"


class Unsupported(ApiError):
    """Raised when a request method is not supported.

    This exception is raised when attempting to use an HTTP method that
    is not supported for the requested endpoint.

    Examples
    --------
    .. code-block:: python

        try:
            client.delete("/unsupported-endpoint")
        except Unsupported as e:
            print(f"Method not supported: {e.message}")
    """

    message = "The requested method is not supported for this endpoint"


class ScoreFunctionInvalidArgs(FiddlerEvalException):
    """Raised when an evaluation score function is called with invalid arguments (missing/extra args)."""


class TaskFunctionInvalidArgs(FiddlerEvalException):
    """Raised when an evaluation task function called with invalid arguments (missing/extra args)."""


class SkipEval(FiddlerEvalException):
    """Exception raised when an evaluation should be skipped."""
