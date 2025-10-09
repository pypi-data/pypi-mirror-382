"""Tests for TopicClassification evaluator."""

import json

import pytest
import responses
from pydantic_core._pydantic_core import ValidationError

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators import TopicClassification
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_topic_classification() -> None:
    """When evaluating topic classification
    Then it should return topic scores
    And should include proper score names."""
    evaluator = TopicClassification(
        topics=["technology", "sports", "politics", "entertainment"]
    )

    # Mock the API response with topic classification scores
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "top_topic",
                    "value": None,
                    "label": "technology",
                    "reasoning": "Text discusses AI and natural language processing",
                },
                {
                    "name": "top_topic_prob",
                    "value": 0.92,
                    "label": None,
                    "reasoning": "High confidence in technology topic classification",
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

    scores = evaluator.score(
        "The new AI model shows promising results in natural language processing."
    )

    assert isinstance(scores, list)
    assert len(scores) == 2

    # Check topic name score
    topic_score = scores[0]
    assert isinstance(topic_score, Score)
    assert topic_score.name == "top_topic"
    assert topic_score.evaluator_name == "topic_classification"
    assert topic_score.value is None
    assert topic_score.label == "technology"
    assert topic_score.reasoning == "Text discusses AI and natural language processing"
    assert topic_score.status == ScoreStatus.SUCCESS

    # Check topic probability score
    topic_prob_score = scores[1]
    assert isinstance(topic_prob_score, Score)
    assert topic_prob_score.name == "top_topic_prob"
    assert topic_prob_score.evaluator_name == "topic_classification"
    assert topic_prob_score.value == 0.92
    assert topic_prob_score.label is None
    assert (
        topic_prob_score.reasoning
        == "High confidence in technology topic classification"
    )
    assert topic_prob_score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "topic_classification"
    assert request_body["parameters"]["topics"] == [
        "technology",
        "sports",
        "politics",
        "entertainment",
    ]
    assert (
        request_body["inputs"]["text"]
        == "The new AI model shows promising results in natural language processing."
    )


@responses.activate
def test_topic_classification_empty_scores_response() -> None:
    """When API returns empty scores
    Then it should raise ValueError
    And should not return scores."""
    evaluator = TopicClassification(topics=["technology", "sports"])

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
def test_topic_classification_missing_scores_key() -> None:
    """When API response is missing scores key
    Then it should raise ValidationError
    And should not return scores."""
    evaluator = TopicClassification(topics=["technology", "sports"])

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
def test_topic_classification_score_with_no_value_or_label() -> None:
    """When API returns score with both value and label as None
    Then it should return a failed score
    And should include proper error details."""
    evaluator = TopicClassification(topics=["technology", "sports"])

    # Mock the API response with score having no value or label
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "top_topic",
                    "value": None,
                    "label": None,
                    "reasoning": "Unable to determine topic",
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
    assert score.name == "top_topic"
    assert score.evaluator_name == "topic_classification"
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Score top_topic has no value or label"
    assert score.value is None
    assert score.label is None
    assert score.reasoning == "Unable to determine topic"


@responses.activate
def test_topic_classification_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return scores."""
    evaluator = TopicClassification(topics=["technology", "sports"])

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
    assert request_body["evaluator_name"] == "topic_classification"
    assert request_body["parameters"]["topics"] == ["technology", "sports"]
    assert request_body["inputs"]["text"] == "Some text"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        None,
    ],
)
def test_topic_classification_validation_errors(text) -> None:
    """When providing invalid text
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = TopicClassification(topics=["technology", "sports"])

    with pytest.raises(ValueError, match="text is required"):
        evaluator.score(text=text)

    # Verify no API call was made
    assert len(responses.calls) == 0


def test_topic_classification_empty_topics() -> None:
    """When providing empty topics
    Then it should raise ValueError
    And should not make API call."""
    with pytest.raises(
        ValueError, match="Topics are required for topic classification"
    ):
        TopicClassification(topics=[])
