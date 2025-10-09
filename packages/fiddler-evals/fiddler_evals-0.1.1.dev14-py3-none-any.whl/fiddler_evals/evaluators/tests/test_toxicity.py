"""Tests for Toxicity evaluator."""

import json

import pytest
import responses
from pydantic_core._pydantic_core import ValidationError

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators import Toxicity
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_toxicity() -> None:
    """When evaluating toxicity
    Then it should return low toxicity score
    And should include proper score name."""
    evaluator = Toxicity()

    # Mock the API response with safe content score
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "toxicity_prob",
                    "value": 0.02,
                    "label": "Low Toxicity",
                    "reasoning": "Content appears safe and non-toxic",
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

    score = evaluator.score("Hello, how are you today?")

    assert isinstance(score, Score)
    assert score.name == "toxicity_prob"
    assert score.evaluator_name == "toxicity"
    assert score.value == 0.02
    assert score.label == "Low Toxicity"
    assert score.reasoning == "Content appears safe and non-toxic"
    assert score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "toxicity"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["text"] == "Hello, how are you today?"


@responses.activate
def test_toxicity_empty_scores_response() -> None:
    """When API returns empty scores
    Then it should return a failed score
    And should include proper error details."""
    evaluator = Toxicity()

    # Mock the API response with empty scores
    mock_response = {
        "data": {"scores": []},
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    with pytest.raises(ValueError):
        evaluator.score("Some text")


@responses.activate
def test_toxicity_missing_scores_key() -> None:
    """When API response is missing scores key
    Then it should raise ValidationError
    And should not return a score."""
    evaluator = Toxicity()

    # Mock the API response without scores key
    mock_response = {"status": "success"}

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    with pytest.raises(ValidationError):
        evaluator.score("Some text")


@responses.activate
def test_toxicity_score_with_no_value_or_label() -> None:
    """When API returns score with both value and label as None
    Then it should return a failed score
    And should include proper error details."""
    evaluator = Toxicity()

    # Mock the API response with score having no value or label
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "toxicity_prob",
                    "value": None,
                    "label": None,
                    "reasoning": "Unable to determine toxicity",
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

    score = evaluator.score("Some text")

    assert isinstance(score, Score)
    assert score.name == "toxicity_prob"
    assert score.evaluator_name == "toxicity"
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Score toxicity_prob has no value or label"
    assert score.value is None
    assert score.label is None
    assert score.reasoning == "Unable to determine toxicity"


@responses.activate
def test_toxicity_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return a score."""
    evaluator = Toxicity()

    # Mock API error response
    responses.post(
        url=f"{URL}/v3/evals/score",
        json={"error": "Internal server error"},
        status=500,
    )

    with pytest.raises(Exception):
        evaluator.score("Some text")

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "toxicity"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["text"] == "Some text"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        None,
    ],
)
def test_toxicity_validation_errors(text) -> None:
    """When providing invalid text
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = Toxicity()

    with pytest.raises(ValueError, match="text is required"):
        evaluator.score(text=text)

    # Verify no API call was made
    assert len(responses.calls) == 0
