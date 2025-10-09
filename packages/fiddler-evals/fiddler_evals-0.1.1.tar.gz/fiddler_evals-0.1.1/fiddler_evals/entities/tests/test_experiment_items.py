import json
from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import pytest
import responses
from pydantic import ValidationError

from fiddler_evals.entities.experiment import Experiment, ExperimentStatus
from fiddler_evals.pydantic_models.experiment import NewExperimentItem
from fiddler_evals.tests.constants import (
    APPLICATION_COMPACT,
    DATASET_COMPACT,
    DATASET_ITEM_ID_1,
    DATASET_ITEM_ID_2,
    EXPERIMENT_ID,
    EXPERIMENT_NAME,
    PROJECT_COMPACT,
    URL,
    USER_COMPACT,
)

# Sample experiment items for testing
SAMPLE_ITEM_1 = {
    "dataset_item_id": DATASET_ITEM_ID_1,
    "outputs": {"answer": "The watermelon seeds pass through your digestive system"},
    "duration_ms": 500,
    "status": "COMPLETED",
    "error_reason": None,
    "error_message": None,
}

SAMPLE_ITEM_2 = {
    "dataset_item_id": DATASET_ITEM_ID_2,
    "outputs": {},
    "duration": 300,
    "status": "FAILED",
    "error_reason": "ValidationError",
    "error_message": "Invalid input format",
}


# API response for successful item insertion
INSERT_RESPONSE_SUCCESS = {
    "data": {
        "ids": [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        ]
    },
    "api_version": "3.0",
    "kind": "NORMAL",
}

# API response for validation error
INSERT_RESPONSE_VALIDATION_ERROR = {
    "error": {
        "code": 400,
        "message": "Validation error",
        "errors": [
            {
                "reason": "ValidationError",
                "message": "Invalid input format",
                "help": "Outputs must be a dictionary",
            }
        ],
    }
}

# API response for experiment not found
INSERT_RESPONSE_404 = {
    "error": {
        "code": 404,
        "message": "Experiment not found",
        "errors": [
            {
                "reason": "NotFound",
                "message": "Experiment not found",
                "help": "",
            }
        ],
    }
}

# Create experiment instance for testing
experiment = Experiment(
    id=UUID(EXPERIMENT_ID),
    name=EXPERIMENT_NAME,
    status=ExperimentStatus.PENDING,
    error_reason=None,
    error_message=None,
    traceback=None,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    created_by=USER_COMPACT,
    updated_by=USER_COMPACT,
    project=PROJECT_COMPACT,
    application=APPLICATION_COMPACT,
    dataset=DATASET_COMPACT,
)


@responses.activate
def test_add_items_success() -> None:
    """Test adding items as NewExperimentItem objects."""

    # Mock item insertion
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json=INSERT_RESPONSE_SUCCESS,
    )

    # Create NewExperimentItem objects
    item1 = NewExperimentItem(**SAMPLE_ITEM_1)
    item2 = NewExperimentItem(**SAMPLE_ITEM_2)
    items = [item1, item2]

    # Add items
    item_ids = experiment.add_items(items)

    # Verify response
    assert len(item_ids) == 2
    assert item_ids[0] == UUID("550e8400-e29b-41d4-a716-446655440001")
    assert item_ids[1] == UUID("550e8400-e29b-41d4-a716-446655440002")

    # Verify request body
    request_body = json.loads(responses.calls[0].request.body)
    assert "items" in request_body
    assert len(request_body["items"]) == 2

    # Verify request body has auto-generated fields    request_body = json.loads(responses.calls[0].request.body)
    first_item = request_body["items"][0]
    assert "id" in first_item
    assert "timestamp" in first_item
    assert first_item["id"] is not None
    assert first_item["timestamp"] is not None


@responses.activate
def test_add_items_empty_list() -> None:
    """Test adding empty list of items."""

    with pytest.raises(ValueError, match="Items cannot be empty"):
        experiment.add_items([])


@responses.activate
def test_add_items_validation_error() -> None:
    """Test adding items with validation error."""

    # Mock item insertion with validation error
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json=INSERT_RESPONSE_VALIDATION_ERROR,
        status=HTTPStatus.BAD_REQUEST,
    )

    # Try to add invalid items
    invalid_items = [{"invalid": "structure"}]  # Missing required fields

    with pytest.raises(ValidationError):  # Should raise validation error
        experiment.add_items([NewExperimentItem(**item) for item in invalid_items])


@responses.activate
def test_add_items_with_minimal_data() -> None:
    """Test adding items with minimal required data."""

    # Mock item insertion
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json=INSERT_RESPONSE_SUCCESS,
    )

    # Create minimal item (only required fields)
    items = [
        {
            "dataset_item_id": DATASET_ITEM_ID_1,
            "outputs": {"answer": "Test answer 1"},
            "status": "COMPLETED",
        },
        {
            "dataset_item_id": DATASET_ITEM_ID_2,
            "outputs": {"answer": "Test answer 2"},
            "status": "COMPLETED",
        },
    ]

    # Add items
    item_ids = experiment.add_items([NewExperimentItem(**item) for item in items])

    # Verify response
    assert len(item_ids) == 2


@responses.activate
def test_add_items_with_complex_outputs() -> None:
    """Test adding items with complex output structures."""

    # Mock item insertion
    responses.post(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json=INSERT_RESPONSE_SUCCESS,
    )

    # Create items with complex outputs
    complex_outputs = {
        "answer": "The answer to the question",
        "confidence": 0.95,
        "reasoning": "Based on the provided context...",
        "sources": ["source1", "source2"],
        "metadata": {"model_version": "1.0", "temperature": 0.7},
    }

    items = [
        {
            "dataset_item_id": DATASET_ITEM_ID_1,
            "outputs": complex_outputs,
            "duration_ms": 500,
            "status": "COMPLETED",
        }
    ]

    # Add items
    experiment.add_items([NewExperimentItem(**item) for item in items])

    # Verify request body contains complex outputs
    request_body = json.loads(responses.calls[0].request.body)
    first_item = request_body["items"][0]
    assert first_item["outputs"] == complex_outputs


@responses.activate
def test_get_items_empty() -> None:
    """Test that Experiment.get_items returns empty iterator when no items."""

    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json={
            "data": {
                "page_size": 100,
                "total": 0,
                "item_count": 0,
                "page_count": 1,
                "page_index": 1,
                "offset": 0,
                "items": [],
            },
            "api_version": "3.0",
            "kind": "PAGINATED",
        },
    )

    result = list(experiment.get_items())
    assert result == []


@responses.activate
def test_get_items_with_different_statuses() -> None:
    """Test that Experiment.get_items returns items with different statuses."""

    # Prepare mock paginated API response with different statuses
    items = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "timestamp": "2024-01-01T00:00:00Z",
            "dataset_item_id": DATASET_ITEM_ID_1,
            "outputs": {"answer": "Success answer"},
            "duration_ms": 500,
            "status": "COMPLETED",
            "error_reason": None,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "timestamp": "2024-01-01T00:00:06Z",
            "dataset_item_id": DATASET_ITEM_ID_2,
            "outputs": {},
            "duration_ms": 500,
            "status": "FAILED",
            "error_reason": "ValidationError",
            "error_message": "Invalid input format",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "timestamp": "2024-01-01T00:00:12Z",
            "dataset_item_id": "44444444-4444-4444-4444-444444444444",
            "outputs": {},
            "duration_ms": 500,
            "status": "PENDING",
            "error_reason": None,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
    ]
    # Simulate a paginated response (single page)
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json={
            "data": {
                "page_size": 100,
                "total": 3,
                "item_count": 3,
                "page_count": 1,
                "page_index": 1,
                "offset": 0,
                "items": items,
            },
            "api_version": "3.0",
            "kind": "PAGINATED",
        },
    )

    # Call get_items and collect results
    result = list(experiment.get_items())

    # Check that all items are returned with correct statuses
    assert len(result) == 3
    assert result[0].status == ExperimentStatus.COMPLETED
    assert result[0].error_reason is None
    assert result[1].status == ExperimentStatus.FAILED
    assert result[1].error_reason == "ValidationError"
    assert result[2].status == ExperimentStatus.PENDING
    assert result[2].error_reason is None


@responses.activate
def test_get_items_with_complex_outputs() -> None:
    """Test that Experiment.get_items returns items with complex output structures."""

    # Prepare mock paginated API response with complex outputs
    complex_outputs = {
        "answer": "The answer to the question",
        "confidence": 0.95,
        "reasoning": "Based on the provided context...",
        "sources": ["source1", "source2"],
        "metadata": {"model_version": "1.0", "temperature": 0.7},
    }

    items = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "timestamp": "2024-01-01T00:00:00Z",
            "dataset_item_id": DATASET_ITEM_ID_1,
            "outputs": complex_outputs,
            "duration_ms": 500,
            "status": "COMPLETED",
            "error_reason": None,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]
    # Simulate a paginated response (single page)
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json={
            "data": {
                "page_size": 100,
                "total": 1,
                "item_count": 1,
                "page_count": 1,
                "page_index": 1,
                "offset": 0,
                "items": items,
            },
            "api_version": "3.0",
            "kind": "PAGINATED",
        },
    )

    # Call get_items and collect results
    result = list(experiment.get_items())

    # Check that complex outputs are preserved
    assert len(result) == 1
    assert result[0].outputs == complex_outputs
    assert result[0].outputs["confidence"] == 0.95
    assert result[0].outputs["sources"] == ["source1", "source2"]


@responses.activate
def test_get_items_pagination() -> None:
    """Test that Experiment.get_items handles pagination correctly."""

    # Prepare mock paginated API response with multiple pages
    page1_items = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "timestamp": "2024-01-01T00:00:00Z",
            "dataset_item_id": DATASET_ITEM_ID_1,
            "outputs": {"answer": "Page 1 item 1"},
            "duration_ms": 500,
            "status": "COMPLETED",
            "error_reason": None,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]

    page2_items = [
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "timestamp": "2024-01-01T00:00:06Z",
            "dataset_item_id": DATASET_ITEM_ID_2,
            "outputs": {"answer": "Page 2 item 1"},
            "duration_ms": 500,
            "status": "COMPLETED",
            "error_reason": None,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]

    # Mock first page
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json={
            "data": {
                "page_size": 1,
                "total": 2,
                "item_count": 1,
                "page_count": 2,
                "page_index": 1,
                "offset": 0,
                "items": page1_items,
            },
            "api_version": "3.0",
            "kind": "PAGINATED",
        },
    )

    # Mock second page
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json={
            "data": {
                "page_size": 1,
                "total": 2,
                "item_count": 1,
                "page_count": 2,
                "page_index": 2,
                "offset": 1,
                "items": page2_items,
            },
            "api_version": "3.0",
            "kind": "PAGINATED",
        },
    )

    # Call get_items and collect results
    result = list(experiment.get_items())

    # Check that all items from both pages are returned
    assert len(result) == 2
    assert result[0].outputs["answer"] == "Page 1 item 1"
    assert result[1].outputs["answer"] == "Page 2 item 1"


@responses.activate
def test_get_items_api_error() -> None:
    """Test that Experiment.get_items handles API errors properly."""

    # Mock API error response
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}/items",
        json={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "errors": [
                    {
                        "reason": "InternalError",
                        "message": "Internal server error",
                        "help": "",
                    }
                ],
            }
        },
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    # Call get_items and expect it to raise an exception
    with pytest.raises(
        Exception
    ):  # The decorator will handle the specific exception type
        list(experiment.get_items())
