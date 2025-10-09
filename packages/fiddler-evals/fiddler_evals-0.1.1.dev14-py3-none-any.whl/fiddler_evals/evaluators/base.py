from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Callable, Dict, Union

from fiddler_evals.connection import get_connection
from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.exceptions import ScoreFunctionInvalidArgs
from fiddler_evals.libs.http_client import RequestClient
from fiddler_evals.pydantic_models.evaluator import EvaluatorResponse
from fiddler_evals.pydantic_models.score import Score, ScoreStatus

# Map<String, String | Function<kwargs>
ScoreFnKwargsMappingType = Dict[str, Union[str, Callable[[Dict[str, Any]], Any]]]

ALLOWED_PARAM_KINDS = {
    inspect.Parameter.KEYWORD_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
}


class Evaluator(ABC):
    """Abstract base class for creating custom evaluators in Fiddler Evals.

    The Evaluator class provides a flexible framework for creating builtin and custom evaluators
    that can assess LLM outputs against various criteria. Each evaluator is
    responsible for a single, specific evaluation task (e.g., hallucination detection,
    answer relevance, exact match, etc.).

    Parameter Mapping:
        Evaluators can define their own parameter mappings using `score_fn_kwargs_mapping`
        in the constructor. These mappings specify how data from the evaluation context
        (inputs, outputs, expected_outputs) should be passed to the evaluator's `score` method.

        Mapping Priority (highest to lowest):
        1. Evaluator-level score_fn_kwargs_mapping (set in constructor)
        2. Evaluation-level kwargs_mapping (passed to evaluate function)
        3. Default parameter resolution

        This allows evaluators to define sensible defaults while still permitting
        customization at the evaluation level.

    Creating Custom Evaluators:
        To create a custom evaluator, inherit from this class and implement the `score` method
        with parameters specific to your evaluation needs:

        Example - Custom evaluator with parameter mapping:
        class ExactMatchEvaluator(Evaluator):
            def __init__(self, output_key: str = "answer", score_name_prefix: str = None):
                super().__init__(
                    score_name_prefix=score_name_prefix,
                    score_fn_kwargs_mapping={"output": output_key}
                )

            def score(self, output: str, expected_output: str) -> Score:
                is_match = output.strip().lower() == expected_output.strip().lower()
                return Score(
                    name=f"{self.score_name_prefix}exact_match",
                    value=1.0 if is_match else 0.0,
                    reasoning=f"Match: {is_match}"
                )

    Args:
        score_name_prefix: Optional prefix to prepend to score names. Useful for
            distinguishing scores when using multiple instances of the same evaluator
            on different fields or with different configurations.
        score_fn_kwargs_mapping: Optional mapping for parameter transformation.
            Maps parameter names to either string keys or transformation functions.
            This mapping takes precedence over evaluation-level mappings when running
            the evaluate method.

    Note:
        The `score` method signature is intentionally flexible using `*args` and `**kwargs`
        to allow each evaluator to define its own parameter requirements. This design
        enables maximum flexibility while maintaining a consistent interface across
        all evaluators in the framework.
    """

    def __init__(
        self,
        score_name_prefix: str | None = None,
        score_fn_kwargs_mapping: ScoreFnKwargsMappingType | None = None,
    ) -> None:
        """Initialize the evaluator with parameter mapping configuration.

        Args:
            score_name_prefix: Optional prefix to prepend to score names. Useful for
                distinguishing scores when using multiple instances of the same evaluator
                on different fields or with different configurations.
            score_fn_kwargs_mapping: Optional mapping for parameter transformation.
                Maps parameter names to either string keys or transformation functions.
                This mapping takes precedence over evaluation-level mappings when running
                the evaluate method.

        Example:
            >>> # Simple string mapping
            >>> evaluator = MyEvaluator(score_fn_kwargs_mapping={"output": "answer"})
            >>>
            >>> # Complex transformation function
            >>> evaluator = MyEvaluator(score_fn_kwargs_mapping={
            ...     "question": lambda x: x["inputs"]["question"],
            ...     "response": "answer"
            ... })
            >>>
            >>> # Using score name prefix for multiple instances
            >>> evaluator1 = RegexSearch(r"\\d+", score_name_prefix="question")
            >>> evaluator2 = RegexSearch(r"\\d+", score_name_prefix="answer")
            >>> # Results in scores named "question_has_number" and "answer_has_number"

        Raises:
            ScoreFunctionInvalidArgs: If the mapping contains invalid parameter names
                that don't match the evaluator's score method signature.
        """
        self.score_name_prefix = score_name_prefix or ""
        # Append underscore at the end of the prefix if not already exists as a separator
        if score_name_prefix and not self.score_name_prefix.endswith("_"):
            self.score_name_prefix += "_"

        self.score_fn_kwargs_mapping = score_fn_kwargs_mapping or {}
        self._validate_kwargs_mapping()

    @property
    def _score_fn(self) -> Callable:
        """Return the score function."""
        return self.score

    def _validate_kwargs_mapping(self) -> None:
        """Validate parameter mappings against score method signature.

        This method is called in the constructor to validate the mapping.

        Raises:
            ScoreFunctionInvalidArgs: If the mapping is invalid.
        """

        # Get all parameters (excluding *args, **kwargs)
        all_params = {
            name
            for name, param in inspect.signature(self._score_fn).parameters.items()
            if param.kind in ALLOWED_PARAM_KINDS
        }

        # Check for invalid mappings
        invalid_mappings = set(self.score_fn_kwargs_mapping.keys()) - all_params
        if invalid_mappings:
            raise ScoreFunctionInvalidArgs(
                f"Invalid evaluator level score_fn_kwargs_mapping: {invalid_mappings}. "
                f"Valid parameters: {all_params}"
            )

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def score(self, *args: Any, **kwargs: Any) -> Score | list[Score]:
        """Evaluate inputs and return a score or list of scores.

        This method must be implemented by all concrete evaluator classes.
        Each evaluator can define its own parameter signature based on what
        it needs for evaluation.

        Common parameter patterns:
            - Output-only: score(self, output: str) -> Score
            - Input-Output: score(self, input: str, output: str) -> Score
            - Comparison: score(self, output: str, expected_output: str) -> Score
            - All parameters: score(self, input: str, output: str, context: list[str]) -> Score

        Args:
            *args: Positional arguments specific to the evaluator's needs.
            **kwargs: Keyword arguments specific to the evaluator's needs.

        Returns:
            Score | list[Score]: A single Score object or list of Score objects
                representing the evaluation results. Each Score should include:
                - name: The score name (e.g., "has_zipcode")
                - evaluator_name: The evaluator name (e.g., "RegexMatch")
                - value: The score value (typically 0.0 to 1.0)
                - status: SUCCESS, FAILED, or SKIPPED
                - reasoning: Optional explanation of the score
                - error: Optional error information if evaluation failed

        Raises:
            ValueError: If required parameters are missing or invalid.
            TypeError: If parameters have incorrect types.
            Exception: Any other evaluation-specific errors.

        """


class FiddlerEvaluator(Evaluator, ABC):
    """Base class for evaluators that use Fiddler's evaluator API."""

    @cached_property
    def _client(self) -> RequestClient:
        """Get the HTTP client for making API requests."""
        return get_connection().client

    def make_call(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Make a call to the evaluator API."""
        response = self._client.post(
            url="v3/evals/score",
            data=payload,
            headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
        )
        return response.json().get("data", {})

    def _parse_scores(self, data: dict[str, Any]) -> list[Score]:
        """Parse the scores from the API response.

        Args:
            data (dict[str, Any]): The API response data.

        Returns:
            Score | list[Score]: A single Score object or list of Score objects.
        """
        scores_response = EvaluatorResponse(**data)
        if not scores_response.scores:
            raise ValueError("No scores returned from Fiddler Evaluator")

        scores = []
        for score_response in scores_response.scores:
            if score_response.value is None and score_response.label is None:
                score = Score(
                    name=f"{self.score_name_prefix}{score_response.name}",
                    evaluator_name=self.name,
                    status=ScoreStatus.FAILED,
                    error_reason="ValueError",
                    error_message=f"Score {score_response.name} has no value or label",
                    reasoning=score_response.reasoning,
                )
            else:
                score = Score(
                    name=f"{self.score_name_prefix}{score_response.name}",
                    evaluator_name=self.name,
                    value=score_response.value,
                    label=score_response.label,
                    reasoning=score_response.reasoning,
                )

            scores.append(score)

        return scores
