import json
from datetime import datetime
from typing import Any
from unittest import mock
from uuid import UUID

import pytest
import responses

from fiddler_evals.entities.dataset import Dataset
from fiddler_evals.entities.experiment import ExperimentItemStatus, ExperimentStatus
from fiddler_evals.evaluators import RegexSearch
from fiddler_evals.exceptions import ScoreFunctionInvalidArgs, TaskFunctionInvalidArgs
from fiddler_evals.pydantic_models.score import ScoreStatus
from fiddler_evals.runner.evaluation import evaluate
from fiddler_evals.tests.constants import (
    APPLICATION_COMPACT,
    APPLICATION_ID,
    APPLICATION_NAME,
    DATASET_ID,
    DATASET_ITEM_ID_1,
    DATASET_ITEM_ID_2,
    DATASET_NAME,
    EXPERIMENT_ID,
    EXPERIMENT_NAME,
    ORG_ID,
    ORG_NAME,
    PROJECT_COMPACT,
    PROJECT_ID,
    PROJECT_NAME,
    URL,
    USER_COMPACT,
    USER_EMAIL,
    USER_FULL_NAME,
    USER_ID,
)

# Test constants
DATASET_DESCRIPTION = "Test dataset for evaluation"
DATASET_METADATA = {"source": "test", "version": "1.0"}
EXPERIMENT_DESCRIPTION = "Test experiment for evaluation"
EXPERIMENT_METADATA = {"model": "gpt-4o", "temperature": 0.7}

dataset = Dataset(
    id=UUID(DATASET_ID),
    name=DATASET_NAME,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    created_by=USER_COMPACT,
    updated_by=USER_COMPACT,
    project=PROJECT_COMPACT,
    application=APPLICATION_COMPACT,
)

# Sample dataset items
SAMPLE_DATASET_ITEMS = [
    {
        "inputs": {"question": "What is the capital of France?"},
        "expected_outputs": {"answer": "The capital of France is Paris."},
        "metadata": {"difficulty": "easy", "category": "geography"},
        "extras": {},
        "source_name": "test_source",
        "source_id": "1",
    },
    {
        "inputs": {"question": "What is 2+2?"},
        "expected_outputs": {"answer": "2+2 equals 4."},
        "metadata": {"difficulty": "easy", "category": "math"},
        "extras": {},
        "source_name": "test_source",
        "source_id": "2",
    },
]

EXPERIMENT_API_RESPONSE = {
    "data": {
        "id": EXPERIMENT_ID,
        "name": EXPERIMENT_NAME,
        "description": EXPERIMENT_DESCRIPTION,
        "metadata": EXPERIMENT_METADATA,
        "status": "PENDING",
        "error_reason": None,
        "error_message": None,
        "traceback": None,
        "duration_ms": 500,
        "organization": {"id": ORG_ID, "name": ORG_NAME},
        "application": {"id": APPLICATION_ID, "name": APPLICATION_NAME},
        "project": {"id": PROJECT_ID, "name": PROJECT_NAME},
        "dataset": {"id": DATASET_ID, "name": DATASET_NAME},
        "created_by": {"id": USER_ID, "email": USER_EMAIL, "full_name": USER_FULL_NAME},
        "updated_by": {"id": USER_ID, "email": USER_EMAIL, "full_name": USER_FULL_NAME},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    },
    "api_version": "3.0",
    "kind": "NORMAL",
}

DATASET_ITEMS_API_RESPONSE = {
    "data": {
        "page_size": 100,
        "total": 2,
        "item_count": 2,
        "page_count": 1,
        "page_index": 1,
        "offset": 0,
        "items": [
            {
                "id": DATASET_ITEM_ID_1,
                "timestamp": "2024-01-01T00:00:00Z",
                "inputs": SAMPLE_DATASET_ITEMS[0]["inputs"],
                "expected_outputs": SAMPLE_DATASET_ITEMS[0]["expected_outputs"],
                "metadata": SAMPLE_DATASET_ITEMS[0]["metadata"],
                "extras": SAMPLE_DATASET_ITEMS[0]["extras"],
                "source_name": SAMPLE_DATASET_ITEMS[0]["source_name"],
                "source_id": SAMPLE_DATASET_ITEMS[0]["source_id"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": DATASET_ITEM_ID_2,
                "timestamp": "2024-01-01T00:00:01Z",
                "inputs": SAMPLE_DATASET_ITEMS[1]["inputs"],
                "expected_outputs": SAMPLE_DATASET_ITEMS[1]["expected_outputs"],
                "metadata": SAMPLE_DATASET_ITEMS[1]["metadata"],
                "extras": SAMPLE_DATASET_ITEMS[1]["extras"],
                "source_name": SAMPLE_DATASET_ITEMS[1]["source_name"],
                "source_id": SAMPLE_DATASET_ITEMS[1]["source_id"],
                "created_at": "2024-01-01T00:00:01Z",
                "updated_at": "2024-01-01T00:00:01Z",
            },
        ],
    },
    "api_version": "3.0",
    "kind": "PAGINATED",
}

EXPERIMENT_SUCCESS_UPDATE_RESPONSE = {
    "data": {
        "id": EXPERIMENT_ID,
        "name": EXPERIMENT_NAME,
        "description": EXPERIMENT_DESCRIPTION,
        "metadata": EXPERIMENT_METADATA,
        "status": "COMPLETED",
        "error_reason": None,
        "error_message": None,
        "traceback": None,
        "duration_ms": 500,
        "organization": {"id": ORG_ID, "name": ORG_NAME},
        "application": {"id": APPLICATION_ID, "name": APPLICATION_NAME},
        "project": {"id": PROJECT_ID, "name": PROJECT_NAME},
        "dataset": {"id": DATASET_ID, "name": DATASET_NAME},
        "created_by": {
            "id": USER_ID,
            "email": USER_EMAIL,
            "full_name": USER_FULL_NAME,
        },
        "updated_by": {
            "id": USER_ID,
            "email": USER_EMAIL,
            "full_name": USER_FULL_NAME,
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    },
    "api_version": "3.0",
    "kind": "NORMAL",
}


@responses.activate
def test_evaluate_with_regex_with_kwargs_mapping() -> None:
    """When starting an experiment with dataset and evaluators with kwargs mapping
    Then it should successfully evaluate all dataset items
    And should create experiment items with scores."""

    # Mock experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=EXPERIMENT_API_RESPONSE,
    )

    # Mock experiment status update to IN_PROGRESS with request body verification
    in_progress_response = EXPERIMENT_API_RESPONSE.copy()
    in_progress_response["data"]["status"] = ExperimentStatus.IN_PROGRESS

    def in_progress_callback(request):
        # Verify that the request body contains the correct status
        request_body = json.loads(request.body)
        assert request_body["status"] == ExperimentStatus.IN_PROGRESS
        return (200, {}, json.dumps(in_progress_response))

    responses.add_callback(
        responses.PATCH,
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        callback=in_progress_callback,
    )

    # Mock experiment updation to COMPLETED
    updated_response = EXPERIMENT_API_RESPONSE.copy()
    updated_response["data"]["status"] = ExperimentStatus.COMPLETED
    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=updated_response,
    )

    # Mock experiment add_results calls (for ExperimentResultPublisher)
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/results",
        json={"message": "Results added successfully"},
    )

    # Mock dataset items retrieval
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}/items",
        json=DATASET_ITEMS_API_RESPONSE,
    )

    # Create evaluators
    evaluators = [
        RegexSearch(r"\d+", score_name="has_number"),
    ]

    # Eval task
    def eval_task(
        inputs: dict[str, Any], extras: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        matched_item = list(
            filter(lambda x: x["inputs"] == inputs, SAMPLE_DATASET_ITEMS)
        )
        if matched_item:
            return matched_item[0]["expected_outputs"]
        return {}

    # Call evaluate method
    result = evaluate(
        dataset=dataset,
        task=eval_task,
        evaluators=evaluators,
        score_fn_kwargs_mapping={"output": "answer"},
    )

    assert len(result.results) == 2
    assert [x.model_dump() for x in result.results] == [
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_1),
                "outputs": {"answer": "The capital of France is Paris."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "created_at": mock.ANY,
                "expected_outputs": {"answer": "The capital of France is Paris."},
                "extras": {},
                "id": mock.ANY,
                "inputs": {"question": "What is the capital of France?"},
                "metadata": {"category": "geography", "difficulty": "easy"},
                "source_id": "1",
                "source_name": "test_source",
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number",
                    "evaluator_name": "RegexSearch",
                    "value": 0.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "No match",
                    "error_reason": None,
                    "error_message": None,
                }
            ],
        },
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_2),
                "outputs": {"answer": "2+2 equals 4."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "inputs": {"question": "What is 2+2?"},
                "expected_outputs": {"answer": "2+2 equals 4."},
                "metadata": {"difficulty": "easy", "category": "math"},
                "extras": {},
                "source_name": "test_source",
                "source_id": "2",
                "created_at": mock.ANY,
                "id": mock.ANY,
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number",
                    "evaluator_name": "RegexSearch",
                    "value": 1.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Matched: 2",
                    "error_reason": None,
                    "error_message": None,
                }
            ],
        },
    ]


@responses.activate
def test_evaluate_with_regex_without_kwargs_mapping() -> None:
    """When starting an experiment with dataset and evaluators without kwargs mapping
    Then it should successfully evaluate all dataset items
    And should create experiment items with scores."""

    # Mock experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=EXPERIMENT_API_RESPONSE,
    )

    # Mock experiment updation
    updated_response = EXPERIMENT_API_RESPONSE.copy()
    updated_response["data"]["status"] = ExperimentStatus.COMPLETED
    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=updated_response,
    )

    # Mock experiment add_results calls (for ExperimentResultPublisher)
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/results",
        json={"message": "Results added successfully"},
    )

    # Mock dataset items retrieval
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}/items",
        json=DATASET_ITEMS_API_RESPONSE,
    )

    # Create evaluators
    evaluators = [
        RegexSearch(r"\d+", score_name="has_number"),
    ]

    # Eval task
    def eval_task(
        inputs: dict[str, Any], extras: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        matched_item = list(
            filter(lambda x: x["inputs"] == inputs, SAMPLE_DATASET_ITEMS)
        )
        if matched_item:
            return {"output": matched_item[0]["expected_outputs"]["answer"]}
        return {}

    # Call evaluate method
    result = evaluate(
        dataset=dataset,
        task=eval_task,
        evaluators=evaluators,
    )

    assert len(result.results) == 2
    expected_results = [
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_1),
                "outputs": {"output": "The capital of France is Paris."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "created_at": mock.ANY,
                "expected_outputs": {"answer": "The capital of France is Paris."},
                "extras": {},
                "id": mock.ANY,
                "inputs": {"question": "What is the capital of France?"},
                "metadata": {"category": "geography", "difficulty": "easy"},
                "source_id": "1",
                "source_name": "test_source",
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number",
                    "evaluator_name": "RegexSearch",
                    "value": 0.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "No match",
                    "error_reason": None,
                    "error_message": None,
                }
            ],
        },
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_2),
                "outputs": {"output": "2+2 equals 4."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "inputs": {"question": "What is 2+2?"},
                "expected_outputs": {"answer": "2+2 equals 4."},
                "metadata": {"difficulty": "easy", "category": "math"},
                "extras": {},
                "source_name": "test_source",
                "source_id": "2",
                "created_at": mock.ANY,
                "id": mock.ANY,
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number",
                    "evaluator_name": "RegexSearch",
                    "value": 1.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Matched: 2",
                    "error_reason": None,
                    "error_message": None,
                }
            ],
        },
    ]
    assert [x.model_dump() for x in result.results] == expected_results

    # Call evaluate method with max_workers=2
    result = evaluate(
        dataset=dataset,
        task=eval_task,
        evaluators=evaluators,
        max_workers=2,
    )
    assert [x.model_dump() for x in result.results] == expected_results


@responses.activate
def test_evaluate_with_regex_with_missing_args() -> None:
    """When starting an experiment with dataset and evaluators
    Then it should raise an error
    """

    experiment_error_response = {
        "data": {
            "id": EXPERIMENT_ID,
            "name": EXPERIMENT_NAME,
            "description": EXPERIMENT_DESCRIPTION,
            "metadata": EXPERIMENT_METADATA,
            "status": "FAILED",
            "error_reason": "ScoreFunctionInvalidArgs",
            "error_message": "Missing required arguments: output",
            "traceback": "",
            "duration_ms": 500,
            "organization": {"id": ORG_ID, "name": ORG_NAME},
            "application": {"id": APPLICATION_ID, "name": APPLICATION_NAME},
            "project": {"id": PROJECT_ID, "name": PROJECT_NAME},
            "dataset": {"id": DATASET_ID, "name": DATASET_NAME},
            "created_by": {
                "id": USER_ID,
                "email": USER_EMAIL,
                "full_name": USER_FULL_NAME,
            },
            "updated_by": {
                "id": USER_ID,
                "email": USER_EMAIL,
                "full_name": USER_FULL_NAME,
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    # Mock experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=EXPERIMENT_API_RESPONSE,
    )

    # Mock experiment update
    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=experiment_error_response,
    )

    # Mock experiment add_results calls (for ExperimentResultPublisher)
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/results",
        json={"message": "Results added successfully"},
    )

    # Mock dataset items retrieval
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}/items",
        json=DATASET_ITEMS_API_RESPONSE,
    )

    # Create evaluators
    evaluators = [
        RegexSearch(r"\d+", score_name="has_number"),
    ]

    # Eval task
    def eval_task(
        inputs: dict[str, Any], extras: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        matched_item = list(
            filter(lambda x: x["inputs"] == inputs, SAMPLE_DATASET_ITEMS)
        )
        if matched_item:
            return matched_item[0]["expected_outputs"]
        return {}

    # Call evaluate method with no mapping
    with pytest.raises(ScoreFunctionInvalidArgs):
        evaluate(
            dataset=dataset,
            task=eval_task,
            evaluators=evaluators,
        )

    # Call evaluate method with wrong mapping
    with pytest.raises(ScoreFunctionInvalidArgs):
        evaluate(
            dataset=dataset,
            task=eval_task,
            evaluators=evaluators,
            score_fn_kwargs_mapping={"output": "non_existing_key"},
        )


@responses.activate
def test_evaluate_with_regex_with_missing_task_args() -> None:
    """When starting an experiment with dataset and evaluators with missing task args
    Then it should raise an error"""

    experiment_error_response = {
        "data": {
            "id": EXPERIMENT_ID,
            "name": EXPERIMENT_NAME,
            "description": EXPERIMENT_DESCRIPTION,
            "metadata": EXPERIMENT_METADATA,
            "status": "FAILED",
            "error_reason": "TaskFunctionInvalidArgs",
            "error_message": "Missing required arguments: extra_param",
            "traceback": "",
            "duration_ms": 500,
            "organization": {"id": ORG_ID, "name": ORG_NAME},
            "application": {"id": APPLICATION_ID, "name": APPLICATION_NAME},
            "project": {"id": PROJECT_ID, "name": PROJECT_NAME},
            "dataset": {"id": DATASET_ID, "name": DATASET_NAME},
            "created_by": {
                "id": USER_ID,
                "email": USER_EMAIL,
                "full_name": USER_FULL_NAME,
            },
            "updated_by": {
                "id": USER_ID,
                "email": USER_EMAIL,
                "full_name": USER_FULL_NAME,
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    # Mock experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=EXPERIMENT_API_RESPONSE,
    )

    # Mock experiment update
    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=experiment_error_response,
    )

    # Mock experiment add_results calls (for ExperimentResultPublisher)
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/results",
        json={"message": "Results added successfully"},
    )

    # Mock dataset items retrieval
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}/items",
        json=DATASET_ITEMS_API_RESPONSE,
    )

    # Create evaluators
    evaluators = [
        RegexSearch(r"\d+", score_name="has_number"),
    ]

    # Eval task
    def eval_task(inputs: dict[str, Any], extras: dict[str, Any]) -> dict[str, Any]:
        return {}

    # Call evaluate method
    with pytest.raises(TaskFunctionInvalidArgs):
        evaluate(
            dataset=dataset,
            task=eval_task,
            evaluators=evaluators,
        )


@responses.activate
def test_evaluate_with_user_defined_evaluator() -> None:
    """When starting an experiment with dataset and evaluators with user defined evaluator
    Then it should raise an error"""

    experiment_error_response = {
        "data": {
            "id": EXPERIMENT_ID,
            "name": EXPERIMENT_NAME,
            "description": EXPERIMENT_DESCRIPTION,
            "metadata": EXPERIMENT_METADATA,
            "status": "FAILED",
            "error_reason": None,
            "error_message": None,
            "traceback": None,
            "duration_ms": 500,
            "organization": {"id": ORG_ID, "name": ORG_NAME},
            "application": {"id": APPLICATION_ID, "name": APPLICATION_NAME},
            "project": {"id": PROJECT_ID, "name": PROJECT_NAME},
            "dataset": {"id": DATASET_ID, "name": DATASET_NAME},
            "created_by": {
                "id": USER_ID,
                "email": USER_EMAIL,
                "full_name": USER_FULL_NAME,
            },
            "updated_by": {
                "id": USER_ID,
                "email": USER_EMAIL,
                "full_name": USER_FULL_NAME,
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    # Mock experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=EXPERIMENT_API_RESPONSE,
    )

    # Mock experiment update
    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=experiment_error_response,
    )

    # Mock experiment add_results calls (for ExperimentResultPublisher)
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/results",
        json={"message": "Results added successfully"},
    )

    # Mock dataset items retrieval
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}/items",
        json=DATASET_ITEMS_API_RESPONSE,
    )

    # Create evaluators
    def equals(a, b):
        return a == b

    evaluators = [
        RegexSearch(r"\d+", score_name="has_number"),
        equals,
    ]

    # Eval task
    def eval_task(
        inputs: dict[str, Any], extras: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        matched_item = list(
            filter(lambda x: x["inputs"] == inputs, SAMPLE_DATASET_ITEMS)
        )
        if matched_item:
            return matched_item[0]["expected_outputs"]
        return {}

    # Call evaluate method
    result = evaluate(
        dataset=dataset,
        task=eval_task,
        evaluators=evaluators,
        score_fn_kwargs_mapping={
            "output": "answer",
            "a": "outputs",
            "b": "expected_outputs",
        },
    )
    assert [x.model_dump() for x in result.results] == [
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_1),
                "outputs": {"answer": "The capital of France is Paris."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "created_at": mock.ANY,
                "expected_outputs": {"answer": "The capital of France is Paris."},
                "extras": {},
                "id": mock.ANY,
                "inputs": {"question": "What is the capital of France?"},
                "metadata": {"category": "geography", "difficulty": "easy"},
                "source_id": "1",
                "source_name": "test_source",
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number",
                    "evaluator_name": "RegexSearch",
                    "value": 0.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "No match",
                    "error_reason": None,
                    "error_message": None,
                },
                {
                    "name": "equals",
                    "evaluator_name": "equals",
                    "value": 1.0,
                    "label": "True",
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Function result: True",
                    "error_reason": None,
                    "error_message": None,
                },
            ],
        },
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_2),
                "outputs": {"answer": "2+2 equals 4."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "inputs": {"question": "What is 2+2?"},
                "expected_outputs": {"answer": "2+2 equals 4."},
                "metadata": {"difficulty": "easy", "category": "math"},
                "extras": {},
                "source_name": "test_source",
                "source_id": "2",
                "created_at": mock.ANY,
                "id": mock.ANY,
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number",
                    "evaluator_name": "RegexSearch",
                    "value": 1.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Matched: 2",
                    "error_reason": None,
                    "error_message": None,
                },
                {
                    "name": "equals",
                    "evaluator_name": "equals",
                    "value": 1.0,
                    "label": "True",
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Function result: True",
                    "error_reason": None,
                    "error_message": None,
                },
            ],
        },
    ]


@responses.activate
def test_evaluate_with_multiple_evaluator_instances() -> None:
    """"""
    # Mock experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=EXPERIMENT_API_RESPONSE,
    )

    # Mock experiment update
    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=EXPERIMENT_SUCCESS_UPDATE_RESPONSE,
    )

    # Mock experiment add_results calls (for ExperimentResultPublisher)
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/results",
        json={"message": "Results added successfully"},
    )

    # Mock dataset items retrieval
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}/items",
        json=DATASET_ITEMS_API_RESPONSE,
    )

    evaluators = [
        RegexSearch(
            r"\d+",
            score_name="has_number_question",
            score_fn_kwargs_mapping={"output": "question"},
        ),
        RegexSearch(
            r"\d+",
            score_name="has_number_answer",
            score_fn_kwargs_mapping={"output": "answer"},
        ),
    ]

    # Eval task
    def eval_task(
        inputs: dict[str, Any], extras: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        matched_item = list(
            filter(lambda x: x["inputs"] == inputs, SAMPLE_DATASET_ITEMS)
        )
        if matched_item:
            return matched_item[0]["expected_outputs"]

        return {}

    # Call evaluate method
    result = evaluate(
        dataset=dataset,
        task=eval_task,
        evaluators=evaluators,
        score_fn_kwargs_mapping={
            # No need for answer -> output mapping since output_key is set to "answer"
            "question": lambda x: x["inputs"]["question"],
        },
    )
    assert [x.model_dump() for x in result.results] == [
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_1),
                "outputs": {"answer": "The capital of France is Paris."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "created_at": mock.ANY,
                "expected_outputs": {"answer": "The capital of France is Paris."},
                "extras": {},
                "id": mock.ANY,
                "inputs": {"question": "What is the capital of France?"},
                "metadata": {"category": "geography", "difficulty": "easy"},
                "source_id": "1",
                "source_name": "test_source",
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number_question",
                    "evaluator_name": "RegexSearch",
                    "value": 0.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "No match",
                    "error_reason": None,
                    "error_message": None,
                },
                {
                    "name": "has_number_answer",
                    "evaluator_name": "RegexSearch",
                    "value": 0.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "No match",
                    "error_reason": None,
                    "error_message": None,
                },
            ],
        },
        {
            "experiment_item": {
                "id": mock.ANY,
                "timestamp": mock.ANY,
                "dataset_item_id": UUID(DATASET_ITEM_ID_2),
                "outputs": {"answer": "2+2 equals 4."},
                "duration_ms": mock.ANY,
                "status": ExperimentItemStatus.SUCCESS,
                "error_reason": None,
                "error_message": None,
            },
            "dataset_item": {
                "inputs": {"question": "What is 2+2?"},
                "expected_outputs": {"answer": "2+2 equals 4."},
                "metadata": {"difficulty": "easy", "category": "math"},
                "extras": {},
                "source_name": "test_source",
                "source_id": "2",
                "created_at": mock.ANY,
                "id": mock.ANY,
                "updated_at": mock.ANY,
            },
            "scores": [
                {
                    "name": "has_number_question",
                    "evaluator_name": "RegexSearch",
                    "value": 1.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Matched: 2",
                    "error_reason": None,
                    "error_message": None,
                },
                {
                    "name": "has_number_answer",
                    "evaluator_name": "RegexSearch",
                    "value": 1.0,
                    "label": None,
                    "status": ScoreStatus.SUCCESS,
                    "reasoning": "Matched: 2",
                    "error_reason": None,
                    "error_message": None,
                },
            ],
        },
    ]
