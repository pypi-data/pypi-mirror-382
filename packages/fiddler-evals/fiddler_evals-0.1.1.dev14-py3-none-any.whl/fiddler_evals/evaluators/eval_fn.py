from __future__ import annotations

import inspect
import logging
from typing import Any, Callable

from fiddler_evals.evaluators.base import Evaluator
from fiddler_evals.exceptions import ScoreFunctionInvalidArgs, SkipEval
from fiddler_evals.pydantic_models.error import get_error_from_exception
from fiddler_evals.pydantic_models.score import Score, ScoreStatus

logger = logging.getLogger(__name__)


class EvalFn(Evaluator):
    """Evaluator that wraps a user-provided function for dynamic evaluation.

    This class allows users to create evaluators from any callable function,
    automatically handling parameter passing, validation, and result conversion to Score objects.

    Key Features:
        - **Dynamic Function Wrapping**: Converts any callable into an evaluator
        - **Argument Validation**: Validates that provided arguments match function signature
        - **Smart Result Conversion**: Automatically converts various return types to Score
        - **Error Handling**: Gracefully handles function execution and argument errors
        - **Parameter Flexibility**: Supports functions with any parameter signature

    Args:
        fn: The callable function to wrap as an evaluator.
        score_name: Optional custom name for the score. If not provided,
                   uses the function name.

    Example:
        >>> def equals(a, b):
        ...     return a == b
        >>>
        >>> evaluator = EvalFn(equals, score_name="exact_match")
        >>> score = evaluator.score(a="hello", b="hello")
        >>> print(score.value)  # 1.0
        >>>
        >>> def length_check(text, min_length=5):
        ...     return len(text) >= min_length
        >>>
        >>> evaluator = EvalFn(length_check)
        >>>
        >>> # Invalid arguments raise TypeError
        >>> try:
        ...     evaluator.score(wrong_param="value")
        ... except TypeError as e:
        ...     print(f"Error: {e}")
    """

    def __init__(
        self,
        fn: Callable,
        score_name: str | None = None,
        **kwargs: Any,
    ):
        self.fn = fn
        self.score_name = score_name or fn.__name__

        # Assign at least fn before calling init for _score_fn property to work properly
        super().__init__(**kwargs)

        self.score_name = f"{self.score_name_prefix}{self.score_name}"

    @property
    def name(self) -> str:
        return self.score_name

    @property
    def _score_fn(self) -> Callable:
        """Return the custom function as the scoring function"""
        return self.fn

    def score(self, *args: Any, **kwargs: Any) -> Score | list[Score]:  # pylint: disable=arguments-differ
        """Execute the wrapped function and convert result to Score.

        Calls the wrapped function with the provided arguments and converts
        the result to a Score object. Validates that the provided arguments
        match the function's signature.

        Args:
            *args: Positional arguments to pass to the wrapped function.
            **kwargs: Keyword arguments to pass to the wrapped function.
                     Only kwargs that match the function's parameters are used.

        Returns:
            Score: A Score object representing the function's evaluation result.

        Raises:
            TypeError: If the provided arguments don't match the function signature.

        Note:
            The function result is converted to a Score as follows:
            - bool: 1.0 for True, 0.0 for False
            - int/float: Direct value conversion
            - Score: Returns as-is
        """
        try:
            # Validate and filter arguments
            filtered_args, filtered_kwargs = self._validate_and_filter_args(
                args, kwargs
            )

            result = self.fn(*filtered_args, **filtered_kwargs)
            return self._convert_to_score(result)
        except SkipEval as e:
            logger.debug(
                "Skipping evaluation score since the user defined function raised Skip exception"
            )
            return Score(
                name=self.score_name,
                evaluator_name=self.name,
                reasoning=f"Function raised SkipEval: {e}",
                status=ScoreStatus.SKIPPED,
            )
        except ScoreFunctionInvalidArgs:
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            error = get_error_from_exception(e)
            return Score(
                name=self.score_name,
                evaluator_name=self.name,
                status=ScoreStatus.FAILED,
                error_reason=error.reason,
                error_message=error.message,
            )

    def _validate_and_filter_args(
        self, args: tuple, kwargs: dict
    ) -> tuple[tuple, dict]:
        """Validate and filter arguments to match the wrapped function's signature.

        Validates that the provided arguments are compatible with the wrapped
        function's signature and filters out any kwargs that don't match
        the function's parameters.

        Args:
            args: Positional arguments to validate and filter.
            kwargs: Keyword arguments to validate and filter.

        Returns:
            tuple: A tuple containing (filtered_args, filtered_kwargs).

        Raises:
            TypeError: If the arguments don't match the function signature.
        """
        try:
            # Get the function signature
            sig = inspect.signature(self.fn)

            # Bind the arguments to the signature
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Extract filtered arguments
            filtered_args = bound_args.args
            filtered_kwargs = bound_args.kwargs

            return filtered_args, filtered_kwargs

        except TypeError as e:
            # Provide more helpful error message
            sig = inspect.signature(self.fn)
            param_names = list(sig.parameters.keys())

            raise ScoreFunctionInvalidArgs(
                f"Invalid arguments for function '{self.fn.__name__}'. "
                f"Expected parameters: {param_names}. "
                f"Provided args: {args}, kwargs: {list(kwargs.keys())}. "
                f"Original error: {str(e)}"
            ) from e

    def _convert_to_score(self, result: Any) -> Score | list[Score]:
        """Convert function result to Score object.

        Args:
            result: The result from the wrapped function.

        Returns:
            Score: A Score object representing the result.
        """
        if result is None:
            logger.debug(
                "Skipping evaluation score since the user defined function returned None"
            )
            return Score(
                name=self.score_name,
                evaluator_name=self.name,
                reasoning="Function result: None",
                status=ScoreStatus.SKIPPED,
            )
        if isinstance(result, Score):
            return result

        if isinstance(result, list) and all(isinstance(x, Score) for x in result):
            return result

        reasoning = f"Function result: {result}"

        if isinstance(result, bool):
            return Score(
                name=self.score_name,
                evaluator_name=self.name,
                value=1.0 if result else 0.0,
                label=str(result),
                reasoning=reasoning,
            )

        if isinstance(result, (int, float)):
            return Score(
                name=self.score_name,
                evaluator_name=self.name,
                value=float(result),
                reasoning=reasoning,
            )

        return Score(
            name=self.score_name,
            evaluator_name=self.name,
            label=str(result),
            reasoning=reasoning,
        )
