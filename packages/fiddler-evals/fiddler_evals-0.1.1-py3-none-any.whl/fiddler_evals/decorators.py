from __future__ import annotations

import logging
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, TypeVar, cast

import requests
from requests import PreparedRequest, Request, Response

from fiddler_evals.exceptions import (
    ApiError,
    Conflict,
    FiddlerEvalException,
    NotFound,
    Unsupported,
)
from fiddler_evals.pydantic_models.response import ErrorResponse

logger = logging.getLogger(__name__)

_WrappedFuncType = TypeVar(  # pylint: disable=invalid-name
    "_WrappedFuncType", bound=Callable[..., Any]
)


def _parse_error_response(response: Response) -> ErrorResponse | None:
    """Parse error response from HTTP response using the structured ErrorResponse model.

    Args:
        response: The HTTP response object

    Returns:
        Parsed ErrorResponse object or None if parsing fails
    """
    try:
        response_data = response.json()
        return ErrorResponse(**response_data)
    except (requests.JSONDecodeError, ValueError, TypeError):
        return None


def _create_error_from_response(response: Response) -> FiddlerEvalException:
    """Create appropriate exception from HTTP response.

    Args:
        response: The HTTP response object

    Returns:
        Appropriate exception instance
    """
    status_code = response.status_code

    # Try to parse structured error response
    error_response = _parse_error_response(response)

    if error_response is not None:
        # Extract error information from structured response
        error_data = error_response.error
        error_message = error_data.message

        # Extract reason from the first error item if available
        reason = None
        if error_data.errors and len(error_data.errors) > 0:
            reason = error_data.errors[0].reason

        # Map status codes to specific exceptions
        if status_code == HTTPStatus.CONFLICT:
            return Conflict(
                error_message,
                status_code=status_code,
                reason=reason,
                error_response=error_response,
            )
        if status_code == HTTPStatus.NOT_FOUND:
            return NotFound(
                error_message,
                status_code=status_code,
                reason=reason,
                error_response=error_response,
            )
        if status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            return Unsupported(
                error_message,
                status_code=status_code,
                reason=reason,
                error_response=error_response,
            )
        return ApiError(
            error_message,
            status_code=status_code,
            reason=reason,
            error_response=error_response,
        )

    # Fallback to generic error with status code
    return ApiError(f"HTTP {status_code} error", status_code=status_code)


def _log_request_error(
    request: Request | PreparedRequest | Any,
    response: Response | None,
    error: Exception,
) -> None:
    """Log request error with appropriate level and details.

    Args:
        request: The HTTP request object
        response: The HTTP response object (if available)
        error: The exception that occurred
    """
    url = getattr(request, "url", "unknown")
    method = getattr(request, "method", "unknown")

    if response is not None:
        status_code = response.status_code
        content_preview = getattr(response, "content", b"")[:200]

        # Log as warning for client errors (4xx), error for server errors (5xx)
        if 400 <= status_code < 500:
            logger.warning(
                "%s HTTP request to %s failed with %s - %s",
                method,
                url,
                status_code,
                content_preview,
            )
        else:
            logger.error(
                "%s HTTP request to %s failed with %s - %s",
                method,
                url,
                status_code,
                content_preview,
            )
    else:
        logger.error("%s HTTP request to %s failed: %s", method, url, str(error))


def handle_api_error(func: _WrappedFuncType) -> _WrappedFuncType:
    """Decorator to handle API errors and convert them to appropriate exceptions.

    This decorator catches various types of HTTP and API errors and converts
    them to appropriate FiddlerEvalException subclasses. It provides consistent
    error handling across all API methods.

    The decorator handles:
    - JSON decode errors -> ApiError
    - HTTP errors with structured error responses -> ApiError, Conflict, NotFound, Unsupported
    - HTTP errors without structured responses -> ApiError
    - Connection and timeout errors -> Re-raises requests.exceptions directly
    - Generic request exceptions -> ApiError

    Note:
        Connection and timeout errors are re-raised as their original requests
        exception types since they're already well-defined and don't need
        custom wrapping. This avoids shadowing Python built-in exceptions.

    Args:
        func: The function to wrap

    Returns:
        Wrapped function that handles errors appropriately
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except requests.JSONDecodeError as e:
            # This often indicates premature use of json() before checking status
            raise ApiError(f"Invalid JSON response - {e.doc}")  # type: ignore
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            # Re-raise requests exceptions directly - they're already well-defined
            # and don't need custom wrapping
            raise
        except requests.HTTPError as http_exc:
            # Handle HTTP errors with response
            response = http_exc.response
            _log_request_error(http_exc.request, response, http_exc)

            # Create appropriate exception from response
            raise _create_error_from_response(response)
        except requests.exceptions.RequestException as e:
            # Handle other request exceptions
            _log_request_error(getattr(e, "request", None), None, e)
            raise ApiError(f"Request failed: {e}")

    return cast(_WrappedFuncType, wrapper)
