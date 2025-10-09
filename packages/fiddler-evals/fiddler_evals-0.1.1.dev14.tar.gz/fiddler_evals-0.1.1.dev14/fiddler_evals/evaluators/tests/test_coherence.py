"""Tests for Coherence evaluator."""

import json

import pytest
import responses
from pydantic_core._pydantic_core import ValidationError

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators import Coherence
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_coherence() -> None:
    """When evaluating coherence
    Then it should return coherence score
    And should include proper score name."""
    evaluator = Coherence()

    # Mock the API response with coherent response score
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_coherent",
                    "value": 1.0,
                    "label": "True",
                    "reasoning": "The response has clear logical flow and structure.",
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

    score = evaluator.score(
        response="First, we need to understand the problem. Then, we can identify potential solutions. Finally, we should test our approach."
    )

    assert isinstance(score, Score)
    assert score.name == "is_coherent"
    assert score.evaluator_name == "coherence"
    assert score.value == 1.0
    assert score.label == "True"
    assert score.reasoning == "The response has clear logical flow and structure."
    assert score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "coherence"
    assert request_body["parameters"] == {}
    assert (
        request_body["inputs"]["response"]
        == "First, we need to understand the problem. Then, we can identify potential solutions. Finally, we should test our approach."
    )


@responses.activate
def test_coherence_with_prompt() -> None:
    """When evaluating coherence with prompt
    Then it should return coherence score
    And should include prompt in the request."""
    evaluator = Coherence()

    # Mock the API response with coherent response score
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_coherent",
                    "value": 1.0,
                    "label": "True",
                    "reasoning": "The response flows logically from the prompt and maintains coherence.",
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

    score = evaluator.score(
        prompt="Explain the process of making coffee",
        response="First, grind the beans. Then, heat the water. Next, pour water over grounds. Finally, enjoy your coffee.",
    )

    assert isinstance(score, Score)
    assert score.name == "is_coherent"
    assert score.evaluator_name == "coherence"
    assert score.value == 1.0
    assert score.label == "True"
    assert (
        score.reasoning
        == "The response flows logically from the prompt and maintains coherence."
    )
    assert score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body includes both prompt and response
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "coherence"
    assert request_body["parameters"] == {}
    assert (
        request_body["inputs"]["response"]
        == "First, grind the beans. Then, heat the water. Next, pour water over grounds. Finally, enjoy your coffee."
    )
    assert request_body["inputs"]["prompt"] == "Explain the process of making coffee"


@responses.activate
def test_coherence_incoherent_response() -> None:
    """When evaluating incoherent response
    Then it should return score 0.0
    And should include proper reasoning."""
    evaluator = Coherence()

    # Mock the API response with incoherent response score
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_coherent",
                    "value": 0.0,
                    "label": "False",
                    "reasoning": "The response lacks logical flow and has disconnected ideas.",
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

    score = evaluator.score(
        response="The sky is blue. I like pizza. Quantum physics is complex. Let's go shopping."
    )

    assert isinstance(score, Score)
    assert score.name == "is_coherent"
    assert score.evaluator_name == "coherence"
    assert score.value == 0.0
    assert score.label == "False"
    assert (
        score.reasoning == "The response lacks logical flow and has disconnected ideas."
    )
    assert score.status == ScoreStatus.SUCCESS

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "coherence"
    assert request_body["parameters"] == {}
    assert (
        request_body["inputs"]["response"]
        == "The sky is blue. I like pizza. Quantum physics is complex. Let's go shopping."
    )


@responses.activate
def test_coherence_empty_scores_response() -> None:
    """When API returns empty scores
    Then it should raise ValueError
    And should not return a score."""
    evaluator = Coherence()

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
        evaluator.score(response="Some response")


@responses.activate
def test_coherence_missing_scores_key() -> None:
    """When API response is missing scores key
    Then it should raise ValidationError
    And should not return a score."""
    evaluator = Coherence()

    # Mock the API response without scores key
    mock_response = {"status": "success"}

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    with pytest.raises(ValidationError):
        evaluator.score(response="Some response")


@responses.activate
def test_coherence_score_with_no_value_or_label() -> None:
    """When API returns score with both value and label as None
    Then it should return a failed score
    And should include proper error details."""
    evaluator = Coherence()

    # Mock the API response with score having no value or label
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_coherent",
                    "value": None,
                    "label": None,
                    "reasoning": "Unable to determine coherence",
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

    score = evaluator.score(response="Some response")

    assert isinstance(score, Score)
    assert score.name == "is_coherent"
    assert score.evaluator_name == "coherence"
    assert score.status == ScoreStatus.FAILED
    assert score.error_reason == "ValueError"
    assert score.error_message == "Score is_coherent has no value or label"
    assert score.value is None
    assert score.label is None
    assert score.reasoning == "Unable to determine coherence"


@responses.activate
def test_coherence_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return a score."""
    evaluator = Coherence()

    # Mock API error response
    responses.post(
        url=f"{URL}/v3/evals/score",
        json={"error": "Internal server error"},
        status=500,
    )

    with pytest.raises(Exception):
        evaluator.score(response="Some response")

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "coherence"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["response"] == "Some response"


@pytest.mark.parametrize(
    "response",
    [
        (""),
        ("   "),
        (None),
    ],
)
def test_coherence_validation_errors(response) -> None:
    """When providing invalid response
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = Coherence()

    with pytest.raises(
        ValueError, match="response is required for coherence evaluation"
    ):
        evaluator.score(response=response)

    # Verify no API call was made
    assert len(responses.calls) == 0


def test_coherence_with_empty_prompt() -> None:
    """When providing empty prompt
    Then it should not include prompt in the request
    And should work normally."""
    evaluator = Coherence()

    # Mock the API response
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_coherent",
                    "value": 1.0,
                    "label": "True",
                    "reasoning": "The response has clear logical flow.",
                }
            ]
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    with responses.RequestsMock() as rsps:
        rsps.post(
            url=f"{URL}/v3/evals/score",
            json=mock_response,
            headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
        )

        score = evaluator.score(response="A coherent response", prompt="")

        assert isinstance(score, Score)
        assert score.value == 1.0

        # Verify request body does not include empty prompt
        request_body = json.loads(rsps.calls[0].request.body)
        assert request_body["inputs"]["prompt"] == ""
        assert request_body["inputs"]["response"] == "A coherent response"
