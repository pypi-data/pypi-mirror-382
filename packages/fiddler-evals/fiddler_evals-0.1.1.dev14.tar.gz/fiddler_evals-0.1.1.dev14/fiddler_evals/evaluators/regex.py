from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Callable

from fiddler_evals.evaluators.base import Evaluator
from fiddler_evals.pydantic_models.score import Score


class _Regex(Evaluator, ABC):
    """
    Evaluator to check if an output string matches a given regular expression pattern.

    This returns a score of 1.0 if the output string matches the given regex pattern,
    and 0.0 otherwise.

    Args:
        regex: The regular expression pattern to match against. Can be a string or a compiled regex pattern.

    Example:
        >>> from fiddler_evals.evaluators import RegexSearch
        >>> regex = RegexSearch("\\d{6}", score_name="has_zipcode")
        >>> result = regex.score("My zipcode is 560010")
        >>> print(result.value)
        1.0
        >>> result = regex.score("My zipcode is 560-010")
        >>> print(result.value)
        0.0

    """

    def __init__(
        self, regex: str | re.Pattern, *, score_name: str | None = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._pattern = re.compile(regex) if isinstance(regex, str) else regex
        self.score_name = f"{self.score_name_prefix}{score_name or 'regex_match'}"

    @property
    @abstractmethod
    def match_fn(self) -> Callable:
        """Match function to use for the regex evaluator."""

    def score(self, output: str) -> Score:  # pylint: disable=arguments-differ
        """
        Calculate the score based on whether the output string matches the given
        regex pattern.

        Args:
            output: The output string to check against the regex pattern.

        Returns:
            Score: A Score instance with a value of 1.0 if the output matches the regex pattern, 0.0 otherwise.
        """
        output = output.strip() if output else ""

        if not output:
            raise ValueError("output is required for regex evaluation")

        match_result = self.match_fn(output)
        if match_result:
            matched_string = match_result.group() if match_result else ""
            return Score(
                name=self.score_name,
                evaluator_name=self.name,
                value=1.0,
                reasoning=f"Matched: {matched_string}",
            )

        return Score(
            name=self.score_name,
            evaluator_name=self.name,
            value=0.0,
            reasoning="No match",
        )


class RegexSearch(_Regex):
    """Regex search attempts to match the regex pattern only at the beginning
    of the string.
    """

    @property
    def match_fn(self) -> Callable:
        return self._pattern.search


class RegexMatch(_Regex):
    """Regex match scans the entire string from beginning to end, looking for the
    first occurrence where the regex pattern matches.
    """

    @property
    def match_fn(self) -> Callable:
        return self._pattern.match
