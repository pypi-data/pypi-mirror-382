from __future__ import annotations

import traceback

from fiddler_evals.pydantic_models.base import BaseModel


class Error(BaseModel):
    """An error that occurred while scoring."""

    reason: str
    message: str
    traceback: str | None = None


def get_error_from_exception(e: Exception) -> Error:
    """Get an error object from an exception."""
    return Error(
        reason=e.__class__.__name__,
        message=str(e),
        traceback=traceback.format_exc(),
    )
