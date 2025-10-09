from __future__ import annotations

from fiddler_evals.pydantic_models.base import BaseModel


class ScoreResponse(BaseModel):
    """A single score response of an evaluator."""

    name: str
    value: float | None = None
    label: str | None = None
    reasoning: str | None = None


class EvaluatorResponse(BaseModel):
    """Evaluator response from Fiddler API"""

    scores: list[ScoreResponse]
