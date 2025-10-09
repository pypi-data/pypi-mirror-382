from __future__ import annotations

import enum

from fiddler_evals.pydantic_models.base import BaseModel


class ScoreStatus(str, enum.Enum):
    """The status of a score."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Score(BaseModel):
    """A single output of an evaluator."""

    name: str
    evaluator_name: str
    value: float | None = None
    label: str | None = None
    status: ScoreStatus = ScoreStatus.SUCCESS
    reasoning: str | None = None
    error_reason: str | None = None
    error_message: str | None = None
