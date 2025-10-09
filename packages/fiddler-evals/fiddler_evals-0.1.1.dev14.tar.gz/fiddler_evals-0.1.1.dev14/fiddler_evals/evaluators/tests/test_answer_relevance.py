import json

import pytest
import responses

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators.answer_relevance import AnswerRelevance
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import URL


@responses.activate
def test_answer_relevance_relevant_answer() -> None:
    """When evaluating a relevant answer
    Then it should return score 1.0
    And should include proper reasoning."""
    evaluator = AnswerRelevance()

    # Mock the API response
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_answer_relevant",
                    "value": 1.0,
                    "label": "True",
                    "reasoning": "The answer directly addresses the question about France's capital.",
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
        prompt="What is the capital of France?",
        response="The capital of France is Paris.",
    )

    assert isinstance(score, Score)
    assert score.name == "is_answer_relevant"
    assert score.evaluator_name == "answer_relevance"
    assert score.value == 1.0
    assert score.label == "True"
    assert score.status == ScoreStatus.SUCCESS
    assert (
        score.reasoning
        == "The answer directly addresses the question about France's capital."
    )

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "answer_relevance"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["prompt"] == "What is the capital of France?"
    assert request_body["inputs"]["response"] == "The capital of France is Paris."


@responses.activate
def test_answer_relevance_irrelevant_answer() -> None:
    """When evaluating an irrelevant answer
    Then it should return score 0.0
    And should include proper reasoning."""
    evaluator = AnswerRelevance()

    # Mock the API response
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_answer_relevant",
                    "value": 0.0,
                    "label": "False",
                    "reasoning": "The answer does not address the question about France's capital.",
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
        prompt="What is the capital of France?",
        response="I like pizza and Italian food.",
    )

    assert isinstance(score, Score)
    assert score.name == "is_answer_relevant"
    assert score.evaluator_name == "answer_relevance"
    assert score.value == 0.0
    assert score.label == "False"
    assert score.status == ScoreStatus.SUCCESS
    assert (
        score.reasoning
        == "The answer does not address the question about France's capital."
    )

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "answer_relevance"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["prompt"] == "What is the capital of France?"
    assert request_body["inputs"]["response"] == "I like pizza and Italian food."


@responses.activate
def test_answer_relevance_missing_reasoning() -> None:
    """When API response has no reasoning
    Then it should return score with None reasoning
    And should handle missing fields gracefully."""
    evaluator = AnswerRelevance()

    # Mock the API response without reasoning
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_answer_relevant",
                    "value": 1.0,
                    "label": "True",
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
        prompt="What is the capital of France?",
        response="The capital of France is Paris.",
    )

    assert score.value == 1.0
    assert score.label == "True"
    assert score.reasoning is None

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "answer_relevance"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["prompt"] == "What is the capital of France?"
    assert request_body["inputs"]["response"] == "The capital of France is Paris."


@responses.activate
def test_answer_relevance_api_error_handling() -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return a score."""
    evaluator = AnswerRelevance()

    # Mock API error response
    responses.post(
        url=f"{URL}/v3/evals/score",
        json={"error": "Internal server error"},
        status=500,
    )

    with pytest.raises(Exception):
        evaluator.score(
            "What is the capital of France?", "The capital of France is Paris."
        )

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "answer_relevance"
    assert request_body["parameters"] == {}
    assert request_body["inputs"]["prompt"] == "What is the capital of France?"
    assert request_body["inputs"]["response"] == "The capital of France is Paris."


@pytest.mark.parametrize(
    "prompt,response",
    [
        # Prompt validation tests
        ("", "Some response"),
        (None, "Some response"),
        ("   \t\n  ", "Some response"),
        # Response validation tests
        ("What is the capital of France?", ""),
        ("What is the capital of France?", None),
        ("What is the capital of France?", "   \t\n  "),
    ],
)
def test_answer_relevance_validation_errors(prompt, response) -> None:
    """When providing invalid prompt or response
    Then it should raise appropriate ValueError
    And should not make API call."""
    evaluator = AnswerRelevance()

    with pytest.raises(ValueError, match="prompt and response are required"):
        evaluator.score(prompt=prompt, response=response)

    # Verify no API call was made
    assert len(responses.calls) == 0
