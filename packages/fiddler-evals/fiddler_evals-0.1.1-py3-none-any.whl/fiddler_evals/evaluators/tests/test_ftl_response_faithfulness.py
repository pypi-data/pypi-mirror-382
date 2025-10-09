"""Tests for FTLResponseFaithfulness evaluator."""

import json

import pytest
import responses
from pydantic_core._pydantic_core import ValidationError

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators.ftl_response_faithfulness import FTLResponseFaithfulness
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_ftl_response_faithfulness() -> None:
    """When evaluating faithful response
    Then it should return faithfulness score
    And should include proper score name."""
    evaluator = FTLResponseFaithfulness()

    # Mock the API response with faithfulness score
    mock_response = {
        "data": {"scores": [{"name": "faithful_prob", "value": 0.95}]},
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    score = evaluator.score(
        response="Paris is the capital of France.",
        context="The capital of France is Paris. It is located in northern Europe.",
    )

    assert isinstance(score, Score)
    assert score.name == "faithful_prob"
    assert score.evaluator_name == "ftl_response_faithfulness"
    assert score.value == 0.95
    assert score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "ftl_response_faithfulness"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["response"] == "Paris is the capital of France."
    assert (
        request_body["inputs"]["context"]
        == "The capital of France is Paris. It is located in northern Europe."
    )


@responses.activate
def test_ftl_response_faithfulness_empty_scores_response() -> None:
    """When API returns empty scores
    Then it should raise ValueError
    And should not return a score."""
    evaluator = FTLResponseFaithfulness()

    # Mock the API response with empty scores
    mock_response = {"data": {"scores": []}, "api_version": "3.0", "kind": "NORMAL"}

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    with pytest.raises(ValueError):
        evaluator.score(response="Some response", context="Some context")


@responses.activate
def test_ftl_response_faithfulness_missing_scores_key() -> None:
    """When API returns empty scores
    Then it should raise ValueError
    And should not return a score."""
    evaluator = FTLResponseFaithfulness()

    # Mock the API response without scores key
    mock_response = {"status": "success"}

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    with pytest.raises(ValidationError):
        evaluator.score(response="Some response", context="Some context")


@responses.activate
def test_ftl_response_faithfulness_score_with_no_value_or_label() -> None:
    """When API returns score with both value and label as None
    Then it should return a failed score
    And should include proper error details."""
    evaluator = FTLResponseFaithfulness()

    # Mock the API response with score having no value or label
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "faithful_prob",
                    "value": None,
                    "label": None,
                    "reasoning": "Unable to determine faithfulness",
                }
            ]
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    score = evaluator.score(response="Some response", context="Some context")

    assert isinstance(score, Score)
    assert score.name == "faithful_prob"
    assert score.evaluator_name == "ftl_response_faithfulness"
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Score faithful_prob has no value or label"
    assert score.value is None
    assert score.label is None
    assert score.reasoning == "Unable to determine faithfulness"


@responses.activate
def test_ftl_response_faithfulness_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return a score."""
    evaluator = FTLResponseFaithfulness()

    # Mock API error response
    responses.post(
        url=f"{URL}/v3/evals/score",
        json={"error": "Internal server error"},
        status=500,
    )

    with pytest.raises(Exception):
        evaluator.score(response="Some response", context="Some context")

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "ftl_response_faithfulness"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["response"] == "Some response"
    assert request_body["inputs"]["context"] == "Some context"


@pytest.mark.parametrize(
    "response,context",
    [
        # Response validation tests
        (
            "",
            "Some context",
        ),
        (None, "Some context"),
        ("   \t\n  ", "Some context"),
        # Context validation tests
        ("Some response", ""),
        ("Some response", None),
        ("Some response", "   \t\n  "),
    ],
)
def test_ftl_response_faithfulness_validation_errors(response, context) -> None:
    """When providing invalid response or context
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = FTLResponseFaithfulness()

    with pytest.raises(
        ValueError,
        match="response and context are required for faithfulness evaluation",
    ):
        evaluator.score(response=response, context=context)

    # Verify no API call was made
    assert len(responses.calls) == 0
