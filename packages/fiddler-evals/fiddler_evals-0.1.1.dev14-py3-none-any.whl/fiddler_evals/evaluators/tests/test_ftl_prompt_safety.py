"""Tests for FTLPromptSafety evaluator."""

import json

import pytest
import responses
from pydantic_core._pydantic_core import ValidationError

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators.ftl_prompt_safety import FTLPromptSafety
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_ftl_prompt_safety_safe_content() -> None:
    """When evaluating safe content
    Then it should return low risk scores for all categories
    And should include proper score names."""
    evaluator = FTLPromptSafety()

    # Mock the API response with safe content scores
    mock_response = {
        "data": {
            "scores": [
                {"name": "illegal_prob", "value": 0.01},
                {"name": "hateful_prob", "value": 0.02},
                {"name": "harassing_prob", "value": 0.01},
                {"name": "racist_prob", "value": 0.01},
                {"name": "sexist_prob", "value": 0.01},
                {"name": "violent_prob", "value": 0.01},
                {"name": "sexual_prob", "value": 0.01},
                {"name": "harmful_prob", "value": 0.02},
                {"name": "unethical_prob", "value": 0.01},
                {"name": "jailbreaking_prob", "value": 0.01},
                {"name": "max_risk_prob", "value": 0.02},
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

    scores = evaluator.score("What is the weather like today?")

    assert isinstance(scores, list)
    assert len(scores) == 11

    # Verify all expected safety categories are present
    expected_categories = [
        "illegal_prob",
        "hateful_prob",
        "harassing_prob",
        "racist_prob",
        "sexist_prob",
        "violent_prob",
        "sexual_prob",
        "harmful_prob",
        "unethical_prob",
        "jailbreaking_prob",
        "max_risk_prob",
    ]

    for score in scores:
        assert isinstance(score, Score)
        assert score.evaluator_name == "ftl_prompt_safety"
        assert score.name in expected_categories
        assert score.status == ScoreStatus.SUCCESS
        assert 0.0 <= score.value <= 1.0

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "ftl_prompt_safety"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["text"] == "What is the weather like today?"


@responses.activate
def test_ftl_prompt_safety_empty_scores_response() -> None:
    """When API returns empty scores
    Then it should raise ValueError
    And should not return a score."""
    evaluator = FTLPromptSafety()

    # Mock the API response with empty scores
    mock_response = {"data": {"scores": []}, "api_version": "3.0", "kind": "NORMAL"}

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    with pytest.raises(ValueError):
        evaluator.score("Some text")


@responses.activate
def test_ftl_prompt_safety_missing_scores_key() -> None:
    """When API returns invalid response
    Then it should raise ValueError
    And should not return a score."""
    evaluator = FTLPromptSafety()

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
def test_ftl_prompt_safety_score_with_no_value_or_label() -> None:
    """When API returns score with both value and label as None
    Then it should return a failed score
    And should include proper error details."""
    evaluator = FTLPromptSafety()

    # Mock the API response with score having no value or label
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "illegal_prob",
                    "value": None,
                    "label": None,
                    "reasoning": "Unable to determine safety",
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
    assert score.name == "illegal_prob"
    assert score.evaluator_name == "ftl_prompt_safety"
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Score illegal_prob has no value or label"
    assert score.value is None
    assert score.label is None
    assert score.reasoning == "Unable to determine safety"


@responses.activate
def test_ftl_prompt_safety_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return scores."""
    evaluator = FTLPromptSafety()

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
    assert request_body["evaluator_name"] == "ftl_prompt_safety"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["text"] == "Some text"


@pytest.mark.parametrize(
    "text",
    [
        # Empty text validation tests
        "",
        None,
        "   \t\n  ",
    ],
)
def test_ftl_prompt_safety_validation_errors(text) -> None:
    """When providing invalid text
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = FTLPromptSafety()

    with pytest.raises(ValueError, match="text is required"):
        evaluator.score(text=text)

    # Verify no API call was made
    assert len(responses.calls) == 0
