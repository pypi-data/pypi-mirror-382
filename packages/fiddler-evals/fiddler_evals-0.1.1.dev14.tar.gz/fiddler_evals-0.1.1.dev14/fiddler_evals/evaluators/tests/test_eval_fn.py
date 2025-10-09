import pytest

from fiddler_evals.evaluators.eval_fn import EvalFn
from fiddler_evals.exceptions import ScoreFunctionInvalidArgs, SkipEval
from fiddler_evals.pydantic_models.score import Score, ScoreStatus


def test_eval_fn_with_bool_function() -> None:
    """When using EvalFn with a boolean function
    Then it should return correct score values
    And should handle both True and False results."""

    def equals(a, b):
        return a == b

    evaluator = EvalFn(equals, score_name="exact_match")

    # Test True result
    score = evaluator.score(a="hello", b="hello")
    assert isinstance(score, Score)
    assert score.name == "exact_match"
    assert score.evaluator_name == "exact_match"
    assert score.value == 1.0
    assert score.label == "True"
    assert score.status == ScoreStatus.SUCCESS
    assert score.reasoning == "Function result: True"

    # Test False result
    score = evaluator.score(a="hello", b="world")
    assert score.value == 0.0
    assert score.label == "False"
    assert score.reasoning == "Function result: False"


def test_eval_fn_with_numeric_function() -> None:
    """When using EvalFn with a numeric function
    Then it should return the numeric value as score
    And should handle different numeric types."""

    def calculate_score(accuracy, precision):
        return (accuracy + precision) / 2

    evaluator = EvalFn(calculate_score)

    # Test with float result
    score = evaluator.score(accuracy=0.9, precision=0.8)
    assert isinstance(score, Score)
    assert score.name == "calculate_score"
    assert score.evaluator_name == "calculate_score"
    assert score.value == 0.8500000000000001
    assert score.label is None
    assert score.status == ScoreStatus.SUCCESS
    assert score.reasoning == "Function result: 0.8500000000000001"

    # Test with integer result
    def count_words(text):
        return len(text.split())

    evaluator = EvalFn(count_words)
    score = evaluator.score(text="hello world test")
    assert score.value == 3.0
    assert score.label is None
    assert score.reasoning == "Function result: 3"


def test_eval_fn_with_string_function() -> None:
    """When using EvalFn with a string function
    Then it should handle string results appropriately
    And should attempt float conversion when possible."""

    def get_status():
        return "success"

    evaluator = EvalFn(get_status)

    # Test non-numeric string
    score = evaluator.score()
    assert score.value is None
    assert score.label == "success"
    assert score.reasoning == "Function result: success"

    # Test numeric string
    def get_score():
        return "0.75"

    evaluator = EvalFn(get_score)
    score = evaluator.score()
    assert score.value is None
    assert score.label == "0.75"
    assert score.reasoning == "Function result: 0.75"


def test_eval_fn_with_score_result() -> None:
    """When using EvalFn with a function that returns Score
    Then it should return the Score object as-is
    And should not perform additional conversion."""

    def custom_evaluator(input_text):
        return Score(
            name="custom",
            evaluator_name="custom",
            value=0.5,
            reasoning="Custom evaluation",
        )

    evaluator = EvalFn(custom_evaluator)
    score = evaluator.score(input_text="test")

    assert isinstance(score, Score)
    assert score.name == "custom"
    assert score.evaluator_name == "custom"
    assert score.value == 0.5
    assert score.label is None
    assert score.reasoning == "Custom evaluation"


def test_eval_fn_with_other_types() -> None:
    """When using EvalFn with functions returning other types
    Then it should convert them to appropriate scores
    And should handle truthy/falsy values correctly."""

    def return_list():
        return [1, 2, 3]

    evaluator = EvalFn(return_list)
    score = evaluator.score()
    assert score.value is None
    assert score.label == "[1, 2, 3]"
    assert score.reasoning == "Function result: [1, 2, 3]"


def test_eval_fn_with_skip() -> None:
    """When using EvalFn with functions returning None or raising SkipEval
    Then it should convert them to skipped scores
    And should handle value/label correctly."""

    def return_none():
        return None

    evaluator = EvalFn(return_none)
    score = evaluator.score()
    assert score.value is None
    assert score.label is None
    assert score.status == ScoreStatus.SKIPPED
    assert score.reasoning == "Function result: None"

    def raise_skip_eval():
        raise SkipEval("Skip evaluation")

    evaluator = EvalFn(raise_skip_eval)
    score = evaluator.score()
    assert score.value is None
    assert score.label is None
    assert score.status == ScoreStatus.SKIPPED
    assert score.reasoning == "Function raised SkipEval: SkipEval: Skip evaluation"


def test_eval_fn_with_default_parameters() -> None:
    """When using EvalFn with functions having default parameters
    Then it should work with and without providing those parameters
    And should apply default values correctly."""

    def length_check(text, min_length=5, case_sensitive=True):
        if case_sensitive:
            return len(text) >= min_length
        return len(text.lower()) >= min_length

    evaluator = EvalFn(length_check)

    # Test with all parameters
    score = evaluator.score(text="hello", min_length=3, case_sensitive=False)
    assert score.value == 1.0

    # Test with default parameters
    score = evaluator.score(text="hello")
    assert score.value == 1.0  # len("hello") >= 5

    # Test with partial parameters
    score = evaluator.score(text="hi", min_length=3)
    assert score.value == 0.0  # len("hi") < 5


def test_eval_fn_extra_arguments() -> None:
    """When using EvalFn with extra kwargs
    Then it should throw error
    """

    def simple_check(value):
        return value > 0

    evaluator = EvalFn(simple_check)

    with pytest.raises(ScoreFunctionInvalidArgs):
        evaluator.score(value=5, extra_param="ignored", another_extra=123)


def test_eval_fn_invalid_arguments() -> None:
    """When using EvalFn with invalid arguments
    Then it should raise TypeError with helpful message
    And should not execute the function."""

    def requires_two_params(a, b):
        return a == b

    evaluator = EvalFn(requires_two_params)

    # Test missing required parameter
    with pytest.raises(
        ScoreFunctionInvalidArgs,
        match="Invalid arguments for function 'requires_two_params'",
    ):
        evaluator.score(a="hello")  # Missing 'b'

    # Test wrong parameter name
    with pytest.raises(
        ScoreFunctionInvalidArgs,
        match="Invalid arguments for function 'requires_two_params'",
    ):
        evaluator.score(wrong_param="value")


def test_eval_fn_function_execution_error() -> None:
    """When using EvalFn with a function that raises an exception
    Then it should return a failed Score
    And should include error information."""

    def error_function(value):
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2

    evaluator = EvalFn(error_function)

    # Test function that raises exception
    score = evaluator.score(value=-5)
    assert isinstance(score, Score)
    assert score.name == "error_function"
    assert score.evaluator_name == "error_function"
    assert score.value is None
    assert score.label is None
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Value must be positive"


def test_eval_fn_name_property() -> None:
    """When creating EvalFn with and without custom name
    Then the name property should return correct values
    And should use function name as default."""

    def test_function():
        return True

    # Test with custom name
    evaluator = EvalFn(test_function, score_name="custom_name")
    assert evaluator.name == "custom_name"

    # Test with default name
    evaluator = EvalFn(test_function)
    assert evaluator.name == "test_function"


def test_eval_fn_complex_function() -> None:
    """When using EvalFn with a complex function
    Then it should handle multiple parameters and logic
    And should work with the evaluation framework."""

    def complex_evaluation(text, threshold=0.5, case_sensitive=True, max_length=None):
        if max_length and len(text) > max_length:
            return False

        if case_sensitive:
            return len(text) >= threshold * 10
        return len(text.lower()) >= threshold * 10

    evaluator = EvalFn(complex_evaluation, score_name="complex_check")

    # Test with all parameters
    score = evaluator.score(
        text="Hello World", threshold=0.8, case_sensitive=True, max_length=20
    )
    assert score.value == 1.0  # len("Hello World") >= 8

    # Test with default parameters
    score = evaluator.score(text="Hi")
    assert score.value == 0.0  # len("Hi") < 5 (threshold * 10)

    # Test with max_length constraint
    score = evaluator.score(text="Very long text that exceeds limit", max_length=10)
    assert score.value == 0.0  # Exceeds max_length


def test_eval_fn_with_positional_and_keyword_args() -> None:
    """When using EvalFn with mixed positional and keyword arguments
    Then it should handle both types correctly
    And should maintain argument order."""

    def mixed_args(a, b, c=10, d=20):
        return a + b + c + d

    evaluator = EvalFn(mixed_args)

    # Test with positional args
    score = evaluator.score(1, 2)
    assert score.value == 33.0  # 1 + 2 + 10 + 20

    # Test with mixed args
    score = evaluator.score(1, 2, c=5)
    assert score.value == 28.0  # 1 + 2 + 5 + 20

    # Test with keyword args
    score = evaluator.score(a=1, b=2, c=5, d=15)
    assert score.value == 23.0  # 1 + 2 + 5 + 15


def test_eval_fn_empty_string_handling() -> None:
    """When using EvalFn with functions returning empty strings
    Then it should handle them as falsy values
    And should provide appropriate reasoning."""

    def empty_string_check(text):
        return text.strip()

    evaluator = EvalFn(empty_string_check)

    # Test with empty string
    score = evaluator.score(text="")
    assert score.value is None
    assert score.reasoning == "Function result: "

    # Test with whitespace only
    score = evaluator.score(text="   ")
    assert score.value is None
    assert score.reasoning == "Function result: "


def test_eval_fn_zero_and_false_handling() -> None:
    """When using EvalFn with functions returning zero or False
    Then it should handle them correctly
    And should distinguish between different falsy values."""

    def zero_check(value):
        return value

    evaluator = EvalFn(zero_check)

    # Test with zero
    score = evaluator.score(value=0)
    assert score.value == 0.0
    assert score.reasoning == "Function result: 0"

    # Test with False
    def false_check():
        return False

    evaluator = EvalFn(false_check)
    score = evaluator.score()
    assert score.value == 0.0
    assert score.reasoning == "Function result: False"


def test_score_fn_kwargs_mapping() -> None:
    """When using EvalFn with a score_fn_kwargs_mapping
    Then it should validate the mapping
    And should raise an error if the mapping is invalid."""

    def equals(a, b):
        return a == b

    # Valid mapping
    EvalFn(
        equals,
        score_name="exact_match",
        score_fn_kwargs_mapping={"a": "answer", "b": "expected_answer"},
    )

    # Invalid mapping
    with pytest.raises(ScoreFunctionInvalidArgs):
        EvalFn(
            equals,
            score_name="exact_match",
            score_fn_kwargs_mapping={"c": "question"},
        )


@pytest.mark.parametrize(
    "score_name,score_name_prefix,expected_score_name",
    [
        (None, None, "equals"),
        ("exact_match", None, "exact_match"),
        (None, "question", "question_equals"),
        (None, "question_", "question_equals"),
        ("exact_match", "question_", "question_exact_match"),
    ],
)
def test_score_name_prefix(score_name, score_name_prefix, expected_score_name) -> None:
    """When creating EvalFn with score_name_prefix
    then it should use the score_name_prefix correctly
    """

    def equals(a, b):
        return a == b

    evaluator = EvalFn(
        equals,
        score_name=score_name,
        score_name_prefix=score_name_prefix,
    )

    score = evaluator.score(a=10, b=10.5)
    assert score.name == expected_score_name
