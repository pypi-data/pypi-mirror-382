import json
from copy import deepcopy
from http import HTTPStatus
from uuid import UUID

import pytest
import responses
from responses import matchers

from fiddler_evals.entities.experiment import Experiment, ExperimentStatus
from fiddler_evals.exceptions import Conflict, NotFound
from fiddler_evals.tests.constants import (
    APPLICATION_ID,
    APPLICATION_NAME,
    DATASET_ID,
    DATASET_NAME,
    EXPERIMENT_ID,
    EXPERIMENT_NAME,
    HEADERS,
    ORG_ID,
    ORG_NAME,
    PROJECT_ID,
    PROJECT_NAME,
    URL,
    USER_EMAIL,
    USER_FULL_NAME,
    USER_ID,
)

# Test constants
EXPERIMENT_DESCRIPTION = "Test experiment"
EXPERIMENT_METADATA = {"model": "gpt-4o"}

API_RESPONSE_200 = {
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
        "organization": {
            "id": ORG_ID,
            "name": ORG_NAME,
        },
        "application": {
            "id": APPLICATION_ID,
            "name": APPLICATION_NAME,
        },
        "dataset": {
            "id": DATASET_ID,
            "name": DATASET_NAME,
        },
        "project": {
            "id": PROJECT_ID,
            "name": PROJECT_NAME,
            "asset_type": "GEN_AI_APP",
        },
        "created_at": "2023-11-22 16:50:57.705784",
        "updated_at": "2023-11-22 16:50:57.705784",
        "created_by": {
            "id": USER_ID,
            "full_name": USER_FULL_NAME,
            "email": USER_EMAIL,
        },
        "updated_by": {
            "id": USER_ID,
            "full_name": USER_FULL_NAME,
            "email": USER_EMAIL,
        },
    },
    "api_version": "3.0",
    "kind": "NORMAL",
}

API_RESPONSE_409 = {
    "error": {
        "code": 409,
        "message": "Experiment already exists",
        "errors": [
            {
                "reason": "Conflict",
                "message": "Experiment already exists",
                "help": "",
            }
        ],
    }
}

API_RESPONSE_404 = {
    "error": {
        "code": 404,
        "message": "Experiment not found for the given identifier",
        "errors": [
            {
                "reason": "ObjectNotFound",
                "message": "Experiment not found for the given identifier",
                "help": "",
            }
        ],
    }
}

API_RESPONSE_FROM_NAME = {
    "data": {
        "page_size": 100,
        "total": 1,
        "item_count": 1,
        "page_count": 1,
        "page_index": 1,
        "offset": 0,
        "items": [API_RESPONSE_200["data"]],
    },
    "api_version": "3.0",
    "kind": "PAGINATED",
}

LIST_API_RESPONSE = {
    "data": {
        "page_size": 100,
        "total": 2,
        "item_count": 2,
        "page_count": 1,
        "page_index": 1,
        "offset": 0,
        "items": [
            API_RESPONSE_200["data"],
            {
                "id": "6531bfd9-2ca2-4a7b-bb5a-136c8da09ca6",
                "name": "test_experiment_2",
                "description": "Test experiment 2",
                "metadata": {"source": "from api"},
                "status": "COMPLETED",
                "error_reason": None,
                "error_message": None,
                "traceback": None,
                "duration_ms": None,
                "organization": {
                    "id": ORG_ID,
                    "name": ORG_NAME,
                },
                "application": {
                    "id": APPLICATION_ID,
                    "name": APPLICATION_NAME,
                },
                "dataset": {
                    "id": DATASET_ID,
                    "name": DATASET_NAME,
                },
                "project": {
                    "id": PROJECT_ID,
                    "name": PROJECT_NAME,
                    "asset_type": "GEN_AI_APP",
                },
                "created_at": "2023-11-22 16:50:57.705784",
                "updated_at": "2023-11-22 16:50:57.705784",
                "created_by": {
                    "id": USER_ID,
                    "full_name": USER_FULL_NAME,
                    "email": USER_EMAIL,
                },
                "updated_by": {
                    "id": USER_ID,
                    "full_name": USER_FULL_NAME,
                    "email": USER_EMAIL,
                },
            },
        ],
    },
    "api_version": "3.0",
    "kind": "PAGINATED",
}


@responses.activate
def test_create_experiment_success() -> None:
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
    )
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )
    assert isinstance(experiment, Experiment)
    assert experiment.id == UUID(EXPERIMENT_ID)
    assert experiment.name == EXPERIMENT_NAME
    assert experiment.description == EXPERIMENT_DESCRIPTION
    assert experiment.metadata == EXPERIMENT_METADATA
    assert experiment.status == ExperimentStatus.COMPLETED
    assert experiment.application.id == UUID(APPLICATION_ID)
    assert experiment.application.name == APPLICATION_NAME
    assert experiment.dataset.id == UUID(DATASET_ID)
    assert experiment.dataset.name == DATASET_NAME
    assert experiment.project.id == UUID(PROJECT_ID)
    assert experiment.project.name == PROJECT_NAME
    assert experiment.created_by.id == UUID(USER_ID)
    assert experiment.created_by.email == USER_EMAIL
    assert experiment.created_by.full_name == USER_FULL_NAME

    assert json.loads(responses.calls[0].request.body) == {
        "name": EXPERIMENT_NAME,
        "application_id": APPLICATION_ID,
        "dataset_id": DATASET_ID,
        "description": EXPERIMENT_DESCRIPTION,
        "metadata": EXPERIMENT_METADATA,
    }


@responses.activate
def test_create_experiment_minimal() -> None:
    """Test creating experiment with minimal required fields."""
    minimal_response = deepcopy(API_RESPONSE_200)
    minimal_response["data"]["description"] = None
    minimal_response["data"]["metadata"] = {}

    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=minimal_response,
    )
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
    )
    assert isinstance(experiment, Experiment)
    assert experiment.id == UUID(EXPERIMENT_ID)
    assert experiment.name == EXPERIMENT_NAME
    assert experiment.description is None
    assert experiment.metadata == {}

    assert json.loads(responses.calls[0].request.body) == {
        "name": EXPERIMENT_NAME,
        "application_id": APPLICATION_ID,
        "dataset_id": DATASET_ID,
        "description": None,
        "metadata": {},
    }


@responses.activate
def test_create_experiment_conflict() -> None:
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_409,
        status=HTTPStatus.CONFLICT,
    )

    with pytest.raises(Conflict):
        Experiment.create(
            name=EXPERIMENT_NAME,
            application_id=APPLICATION_ID,
            dataset_id=DATASET_ID,
            description=EXPERIMENT_DESCRIPTION,
            metadata=EXPERIMENT_METADATA,
        )


@responses.activate
def test_get_experiment_by_id_success() -> None:
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=API_RESPONSE_200,
    )
    experiment = Experiment.get_by_id(id_=EXPERIMENT_ID)
    assert isinstance(experiment, Experiment)
    assert experiment.id == UUID(EXPERIMENT_ID)
    assert experiment.name == EXPERIMENT_NAME
    assert experiment.description == EXPERIMENT_DESCRIPTION


@responses.activate
def test_get_experiment_by_id_not_found() -> None:
    responses.get(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=API_RESPONSE_404,
        status=HTTPStatus.NOT_FOUND,
    )

    with pytest.raises(NotFound):
        Experiment.get_by_id(id_=EXPERIMENT_ID)


@responses.activate
def test_get_experiment_by_name_success() -> None:
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{EXPERIMENT_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_FROM_NAME,
        match=[matchers.query_param_matcher(params)],
    )
    experiment = Experiment.get_by_name(
        name=EXPERIMENT_NAME, application_id=APPLICATION_ID
    )
    assert isinstance(experiment, Experiment)
    assert experiment.id == UUID(EXPERIMENT_ID)
    assert experiment.name == EXPERIMENT_NAME


@responses.activate
def test_get_experiment_by_name_not_found() -> None:
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{EXPERIMENT_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=resp,
        match=[matchers.query_param_matcher(params)],
    )

    with pytest.raises(NotFound):
        Experiment.get_by_name(name=EXPERIMENT_NAME, application_id=APPLICATION_ID)


@responses.activate
def test_list_experiments_success() -> None:
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}',
        "limit": 50,
        "offset": 0,
    }
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=LIST_API_RESPONSE,
        match=[matchers.query_param_matcher(params)],
    )
    experiments = list(Experiment.list(application_id=APPLICATION_ID))
    assert len(experiments) == 2
    for experiment in experiments:
        assert isinstance(experiment, Experiment)
        assert experiment.application.id == UUID(APPLICATION_ID)


@responses.activate
def test_list_experiments_with_dataset_filter() -> None:
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}},{{"field":"dataset_id","operator":"equal","value":"{DATASET_ID}"}}]}}',
        "limit": 50,
        "offset": 0,
    }
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=LIST_API_RESPONSE,
        match=[matchers.query_param_matcher(params)],
    )
    experiments = list(
        Experiment.list(application_id=APPLICATION_ID, dataset_id=DATASET_ID)
    )
    assert len(experiments) == 2
    for experiment in experiments:
        assert isinstance(experiment, Experiment)
        assert experiment.application.id == UUID(APPLICATION_ID)
        assert experiment.dataset.id == UUID(DATASET_ID)


@responses.activate
def test_list_experiments_empty() -> None:
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}',
        "limit": 50,
        "offset": 0,
    }
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=resp,
        match=[matchers.query_param_matcher(params)],
    )
    experiments = list(Experiment.list(application_id=APPLICATION_ID))
    assert len(experiments) == 0


@responses.activate
def test_get_or_create_experiment_new() -> None:
    # When experiment doesn't exist
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{EXPERIMENT_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }

    # Find experiment by name
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=resp,
        match=[
            matchers.query_param_matcher(params),
            matchers.header_matcher(HEADERS),
        ],
    )

    # POST call to create
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the experiment
    experiment = Experiment.get_or_create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )
    assert experiment.id == UUID(EXPERIMENT_ID)
    assert experiment.name == EXPERIMENT_NAME
    assert experiment.description == EXPERIMENT_DESCRIPTION

    assert len(responses.calls) == 2


@responses.activate
def test_get_or_create_experiment_exists() -> None:
    # When experiment exists
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{EXPERIMENT_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_FROM_NAME,
        match=[
            matchers.query_param_matcher(params),
            matchers.header_matcher(HEADERS),
        ],
    )

    # This call will fetch the experiment
    experiment = Experiment.get_or_create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )
    assert experiment.id == UUID(EXPERIMENT_ID)
    assert experiment.name == EXPERIMENT_NAME

    assert len(responses.calls) == 1


@responses.activate
def test_experiment_with_none_values() -> None:
    """Test experiment creation with None values for optional fields."""
    minimal_response = deepcopy(API_RESPONSE_200)
    minimal_response["data"]["description"] = None
    minimal_response["data"]["metadata"] = {}

    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=minimal_response,
    )

    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=None,
        metadata=None,
    )

    assert experiment.description is None
    assert experiment.metadata == {}

    assert json.loads(responses.calls[0].request.body) == {
        "name": EXPERIMENT_NAME,
        "application_id": APPLICATION_ID,
        "dataset_id": DATASET_ID,
        "description": None,
        "metadata": {},
    }


@responses.activate
def test_update_experiment_success() -> None:
    update_response = deepcopy(API_RESPONSE_200)
    update_response["data"]["description"] = "foo description"

    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=update_response,
    )

    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the experiment
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )

    updated_experiment = experiment.update(description="foo description")
    assert updated_experiment.description == "foo description"
    assert updated_experiment.metadata == EXPERIMENT_METADATA


@responses.activate
def test_update_all_none() -> None:
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the experiment
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )

    with pytest.raises(ValueError):
        experiment.update(description=None, metadata=None)


@responses.activate
def test_update_clear_field() -> None:
    update_response = deepcopy(API_RESPONSE_200)
    update_response["data"]["metadata"] = {}

    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=update_response,
    )
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )

    updated_experiment = experiment.update(metadata={})
    assert updated_experiment.metadata == {}
    assert updated_experiment.description == EXPERIMENT_DESCRIPTION


@responses.activate
def test_delete_experiment_success() -> None:
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the experiment
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )

    responses.delete(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        status=HTTPStatus.NO_CONTENT,
    )

    # This should not raise an exception
    experiment.delete()

    # Verify the delete call was made
    assert len(responses.calls) == 2
    assert responses.calls[1].request.method == "DELETE"
    assert (
        responses.calls[1].request.url == f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}"
    )


@responses.activate
def test_experiment_with_error_fields() -> None:
    """Test experiment with error information."""
    error_response = deepcopy(API_RESPONSE_200)
    error_response["data"]["status"] = "FAILED"
    error_response["data"]["error_reason"] = "ValidationError"
    error_response["data"]["error_message"] = "Invalid input data"
    error_response["data"]["traceback"] = (
        "Traceback (most recent call last):\n  File..."
    )

    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=error_response,
    )
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
    )

    assert experiment.status == ExperimentStatus.FAILED
    assert experiment.error_reason == "ValidationError"
    assert experiment.error_message == "Invalid input data"
    assert experiment.traceback == "Traceback (most recent call last):\n  File..."


@responses.activate
def test_update_experiment_failed_status() -> None:
    """When updating experiment status to FAILED with error details
    Then the experiment should be updated with error information
    And the status should be set to FAILED."""

    # Mock the initial experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # Mock the update response with FAILED status and error details
    update_response = deepcopy(API_RESPONSE_200)
    update_response["data"]["status"] = "FAILED"
    update_response["data"]["error_reason"] = "Evaluation timeout"
    update_response["data"]["error_message"] = (
        "The evaluation process exceeded the maximum allowed time"
    )
    update_response["data"]["traceback"] = (
        'Traceback (most recent call last):\n  File "evaluate.py", line 42, in run_evaluation\n    result = evaluator.score(output)\nTimeoutError: Evaluation timeout'
    )

    responses.patch(
        url=f"{URL}/v3/evals/experiments/{EXPERIMENT_ID}",
        json=update_response,
    )

    # Create the experiment
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )

    # Update experiment status to FAILED with error details
    updated_experiment = experiment.update(
        status=ExperimentStatus.FAILED,
        error_reason="Evaluation timeout",
        error_message="The evaluation process exceeded the maximum allowed time",
        traceback='Traceback (most recent call last):\n  File "evaluate.py", line 42, in run_evaluation\n    result = evaluator.score(output)\nTimeoutError: Evaluation timeout',
    )

    # Verify the update was successful
    assert updated_experiment.status == ExperimentStatus.FAILED
    assert updated_experiment.error_reason == "Evaluation timeout"
    assert (
        updated_experiment.error_message
        == "The evaluation process exceeded the maximum allowed time"
    )
    assert updated_experiment.traceback is not None


@responses.activate
def test_update_experiment_failed_status_missing_error_params() -> None:
    """When updating experiment status to FAILED without required error parameters
    Then it should raise ValueError
    And the experiment should not be updated."""

    # Mock the initial experiment creation
    responses.post(
        url=f"{URL}/v3/evals/experiments",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # Create the experiment
    experiment = Experiment.create(
        name=EXPERIMENT_NAME,
        application_id=APPLICATION_ID,
        dataset_id=DATASET_ID,
        description=EXPERIMENT_DESCRIPTION,
        metadata=EXPERIMENT_METADATA,
    )

    # Try to update status to FAILED without required error parameters
    with pytest.raises(
        ValueError, match="error_reason, error_message, and traceback must be provided"
    ):
        experiment.update(status=ExperimentStatus.FAILED)

    # Verify no PATCH request was made
    assert len(responses.calls) == 1  # Only POST for create, no PATCH
