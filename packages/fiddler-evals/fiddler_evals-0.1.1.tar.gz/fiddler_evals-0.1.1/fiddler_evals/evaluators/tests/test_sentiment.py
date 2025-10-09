"""Tests for Sentiment evaluator."""

import json

import pytest
import responses
from pydantic_core._pydantic_core import ValidationError

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators import Sentiment
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_sentiment() -> None:
    """When evaluating sentiment
    Then it should return sentiment scores
    And should include proper score names."""
    evaluator = Sentiment()

    # Mock the API response with sentiment scores
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "sentiment",
                    "value": None,
                    "label": "positive",
                    "reasoning": "Text expresses positive sentiment",
                },
                {
                    "name": "sentiment_prob",
                    "value": 0.85,
                    "label": None,
                    "reasoning": "High confidence in positive sentiment",
                },
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

    scores = evaluator.score("I love this product! It's amazing!")

    assert isinstance(scores, list)
    assert len(scores) == 2

    # Check sentiment label score
    sentiment_score = scores[0]
    assert isinstance(sentiment_score, Score)
    assert sentiment_score.name == "sentiment"
    assert sentiment_score.evaluator_name == "sentiment_analysis"
    assert sentiment_score.value is None
    assert sentiment_score.label == "positive"
    assert sentiment_score.reasoning == "Text expresses positive sentiment"
    assert sentiment_score.status == ScoreStatus.SUCCESS

    # Check sentiment probability score
    sentiment_prob_score = scores[1]
    assert isinstance(sentiment_prob_score, Score)
    assert sentiment_prob_score.name == "sentiment_prob"
    assert sentiment_prob_score.evaluator_name == "sentiment_analysis"
    assert sentiment_prob_score.value == 0.85
    assert sentiment_prob_score.label is None
    assert sentiment_prob_score.reasoning == "High confidence in positive sentiment"
    assert sentiment_prob_score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "sentiment_analysis"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["text"] == "I love this product! It's amazing!"


@responses.activate
def test_sentiment_empty_scores_response() -> None:
    """When API returns empty scores
    Then it should raise ValueError
    And should not return scores."""
    evaluator = Sentiment()

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
def test_sentiment_missing_scores_key() -> None:
    """When API response is missing scores key
    Then it should raise ValidationError
    And should not return scores."""
    evaluator = Sentiment()

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
def test_sentiment_score_with_no_value_or_label() -> None:
    """When API returns score with both value and label as None
    Then it should return a failed score
    And should include proper error details."""
    evaluator = Sentiment()

    # Mock the API response with score having no value or label
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "sentiment",
                    "value": None,
                    "label": None,
                    "reasoning": "Unable to determine sentiment",
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

    scores = evaluator.score("Some text")

    assert isinstance(scores, list)
    assert len(scores) == 1
    score = scores[0]
    assert score.name == "sentiment"
    assert score.evaluator_name == "sentiment_analysis"
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Score sentiment has no value or label"
    assert score.value is None
    assert score.label is None
    assert score.reasoning == "Unable to determine sentiment"


@responses.activate
def test_sentiment_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return scores."""
    evaluator = Sentiment()

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
    assert request_body["evaluator_name"] == "sentiment_analysis"
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
def test_sentiment_validation_errors(text) -> None:
    """When providing invalid text
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = Sentiment()

    with pytest.raises(ValueError, match="text is required"):
        evaluator.score(text=text)

    # Verify no API call was made
    assert len(responses.calls) == 0
