import json
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import pytest
import responses
from responses import matchers

from fiddler_evals.entities.dataset import Dataset
from fiddler_evals.exceptions import Conflict, NotFound
from fiddler_evals.tests.constants import (
    APPLICATION_ID,
    APPLICATION_NAME,
    DATASET_ID,
    DATASET_NAME,
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
DATASET_DESCRIPTION = "Test dataset"
DATASET_METADATA = {"source": "from web"}


API_RESPONSE_200 = {
    "data": {
        "id": DATASET_ID,
        "name": DATASET_NAME,
        "description": DATASET_DESCRIPTION,
        "metadata": DATASET_METADATA,
        "active": True,
        "organization": {
            "id": ORG_ID,
            "name": ORG_NAME,
        },
        "application": {
            "id": APPLICATION_ID,
            "name": APPLICATION_NAME,
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
        "message": "Dataset already exists",
        "errors": [
            {
                "reason": "Conflict",
                "message": "Dataset already exists",
                "help": "",
            }
        ],
    }
}

API_RESPONSE_404 = {
    "error": {
        "code": 404,
        "message": "Dataset not found for the given identifier",
        "errors": [
            {
                "reason": "ObjectNotFound",
                "message": "Dataset not found for the given identifier",
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
                "id": "3531bfd9-2ca2-4a7b-bb5a-136c8da09ca4",
                "name": "test_dataset_2",
                "description": "Test dataset 2",
                "metadata": {"source": "from api"},
                "active": True,
                "organization": {
                    "id": ORG_ID,
                    "name": ORG_NAME,
                },
                "application": {
                    "id": APPLICATION_ID,
                    "name": APPLICATION_NAME,
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
def test_create_dataset_success() -> None:
    """When creating a dataset with all fields provided
    Then the dataset should be created successfully
    And all fields should match the provided values."""
    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_200,
    )
    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )
    assert isinstance(dataset, Dataset)
    assert dataset.id == UUID(DATASET_ID)
    assert dataset.name == DATASET_NAME
    assert dataset.description == DATASET_DESCRIPTION
    assert dataset.metadata == DATASET_METADATA
    assert dataset.active is True
    assert dataset.created_at == datetime.fromisoformat(
        API_RESPONSE_200["data"]["created_at"]
    )
    assert dataset.updated_at == datetime.fromisoformat(
        API_RESPONSE_200["data"]["updated_at"]
    )
    assert dataset.application.id == UUID(APPLICATION_ID)
    assert dataset.application.name == APPLICATION_NAME
    assert dataset.project.id == UUID(PROJECT_ID)
    assert dataset.project.name == PROJECT_NAME
    assert dataset.created_by.id == UUID(USER_ID)
    assert dataset.created_by.email == USER_EMAIL
    assert dataset.created_by.full_name == USER_FULL_NAME

    assert json.loads(responses.calls[0].request.body) == {
        "name": DATASET_NAME,
        "application_id": APPLICATION_ID,
        "description": DATASET_DESCRIPTION,
        "metadata": DATASET_METADATA,
        "active": True,
    }


@responses.activate
def test_create_dataset_minimal() -> None:
    """When creating a dataset with only required fields
    Then the dataset should be created successfully
    And optional fields should have default values."""
    minimal_response = deepcopy(API_RESPONSE_200)
    minimal_response["data"]["description"] = None
    minimal_response["data"]["metadata"] = {}

    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=minimal_response,
    )
    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
    )
    assert isinstance(dataset, Dataset)
    assert dataset.id == UUID(DATASET_ID)
    assert dataset.name == DATASET_NAME
    assert dataset.description is None
    assert dataset.metadata == {}

    assert json.loads(responses.calls[0].request.body) == {
        "name": DATASET_NAME,
        "application_id": APPLICATION_ID,
        "description": None,
        "metadata": {},
        "active": True,
    }


@responses.activate
def test_create_dataset_conflict() -> None:
    """When attempting to create a dataset with a name that already exists
    Then the creation should fail with a Conflict exception
    And the existing dataset should remain unchanged."""
    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_409,
        status=HTTPStatus.CONFLICT,
    )

    with pytest.raises(Conflict):
        Dataset.create(
            name=DATASET_NAME,
            application_id=APPLICATION_ID,
            description=DATASET_DESCRIPTION,
            metadata=DATASET_METADATA,
        )


@responses.activate
def test_get_dataset_by_id_success() -> None:
    """When retrieving a dataset by its ID
    Then the dataset should be returned successfully
    And all dataset fields should be populated correctly."""
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}",
        json=API_RESPONSE_200,
    )
    dataset = Dataset.get_by_id(id_=DATASET_ID)
    assert isinstance(dataset, Dataset)
    assert dataset.id == UUID(DATASET_ID)
    assert dataset.name == DATASET_NAME
    assert dataset.description == DATASET_DESCRIPTION


@responses.activate
def test_get_dataset_by_id_not_found() -> None:
    """When attempting to retrieve a dataset by non-existent ID
    Then a NotFound exception should be raised
    And no dataset should be returned."""
    responses.get(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}",
        json=API_RESPONSE_404,
        status=HTTPStatus.NOT_FOUND,
    )

    with pytest.raises(NotFound):
        Dataset.get_by_id(id_=DATASET_ID)


@responses.activate
def test_get_dataset_by_name_success() -> None:
    """When retrieving a dataset by name within an application
    Then the dataset should be returned successfully
    And the dataset should belong to the specified application."""
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{DATASET_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_FROM_NAME,
        match=[matchers.query_param_matcher(params)],
    )
    dataset = Dataset.get_by_name(name=DATASET_NAME, application_id=APPLICATION_ID)
    assert isinstance(dataset, Dataset)
    assert dataset.id == UUID(DATASET_ID)
    assert dataset.name == DATASET_NAME


@responses.activate
def test_get_dataset_by_name_not_found() -> None:
    """When attempting to retrieve a dataset by non-existent name
    Then a NotFound exception should be raised
    And no dataset should be returned."""
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{DATASET_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/evals/datasets",
        json=resp,
        match=[matchers.query_param_matcher(params)],
    )

    with pytest.raises(NotFound):
        Dataset.get_by_name(name=DATASET_NAME, application_id=APPLICATION_ID)


@responses.activate
def test_list_datasets_success() -> None:
    """When listing all datasets in an application
    Then all accessible datasets should be returned
    And each dataset should belong to the specified application."""
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}',
        "limit": 50,
        "offset": 0,
    }
    responses.get(
        url=f"{URL}/v3/evals/datasets",
        json=LIST_API_RESPONSE,
        match=[matchers.query_param_matcher(params)],
    )
    datasets = list(Dataset.list(application_id=APPLICATION_ID))
    assert len(datasets) == 2
    for dataset in datasets:
        assert isinstance(dataset, Dataset)
        assert dataset.application.id == UUID(APPLICATION_ID)


@responses.activate
def test_list_datasets_empty() -> None:
    """When listing datasets in an application with no datasets
    Then an empty list should be returned
    And no datasets should be found."""
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
        url=f"{URL}/v3/evals/datasets",
        json=resp,
        match=[matchers.query_param_matcher(params)],
    )
    datasets = list(Dataset.list(application_id=APPLICATION_ID))
    assert len(datasets) == 0


@responses.activate
def test_get_or_create_dataset_new() -> None:
    """When attempting to get_or_create a dataset that doesn't exist
    Then a new dataset should be created
    And the new dataset should be returned with the specified parameters."""
    # When dataset doesn't exist
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{DATASET_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }

    # Find dataset by name
    responses.get(
        url=f"{URL}/v3/evals/datasets",
        json=resp,
        match=[
            matchers.query_param_matcher(params),
            matchers.header_matcher(HEADERS),
        ],
    )

    # POST call to create
    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the dataset
    dataset = Dataset.get_or_create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )
    assert dataset.id == UUID(DATASET_ID)
    assert dataset.name == DATASET_NAME
    assert dataset.description == DATASET_DESCRIPTION

    assert len(responses.calls) == 2


@responses.activate
def test_get_or_create_dataset_exists() -> None:
    """When attempting to get_or_create a dataset that already exists
    Then the existing dataset should be returned
    And no new dataset should be created."""
    # When dataset exists
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{DATASET_NAME}"}},{{"field":"application_id","operator":"equal","value":"{APPLICATION_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_FROM_NAME,
        match=[
            matchers.query_param_matcher(params),
            matchers.header_matcher(HEADERS),
        ],
    )

    # This call will fetch the dataset
    dataset = Dataset.get_or_create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )
    assert dataset.id == UUID(DATASET_ID)
    assert dataset.name == DATASET_NAME

    assert len(responses.calls) == 1


@responses.activate
def test_create_dataset_with_none_values() -> None:
    """When creating a dataset with None values for optional fields
    Then the dataset should be created successfully
    And the optional fields should have None values of their respective types."""
    minimal_response = deepcopy(API_RESPONSE_200)
    minimal_response["data"]["description"] = None
    minimal_response["data"]["metadata"] = {}

    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=minimal_response,
    )

    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=None,
        metadata=None,
    )

    assert dataset.description is None
    assert dataset.metadata == {}

    assert json.loads(responses.calls[0].request.body) == {
        "name": DATASET_NAME,
        "application_id": APPLICATION_ID,
        "description": None,
        "metadata": {},
        "active": True,
    }


@responses.activate
def test_update_dataset_success() -> None:
    """When updating a dataset with new field values
    Then the dataset should be updated successfully
    And the new values should be reflected in the returned dataset."""
    update_response = deepcopy(API_RESPONSE_200)
    update_response["data"]["description"] = "foo description"

    responses.patch(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}",
        json=update_response,
    )

    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the dataset
    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )

    updated_dataset = dataset.update(description="foo description")
    assert updated_dataset.description == "foo description"
    assert updated_dataset.metadata == DATASET_METADATA


@responses.activate
def test_update_all_none() -> None:
    """When attempting to update a dataset with all None parameters
    Then a ValueError should be raised
    And the dataset should remain unchanged."""
    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the dataset
    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )

    with pytest.raises(ValueError):
        dataset.update(description=None, metadata=None)


@responses.activate
def test_update_clear_field() -> None:
    """When updating a dataset with empty values for fields
    Then the fields should be cleared successfully
    And the empty values should be reflected in the returned dataset."""
    update_response = deepcopy(API_RESPONSE_200)
    update_response["data"]["metadata"] = {}

    responses.patch(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}",
        json=update_response,
    )
    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )

    updated_dataset = dataset.update(metadata={})
    assert updated_dataset.metadata == {}
    assert updated_dataset.description == DATASET_DESCRIPTION


@responses.activate
def test_delete_dataset_success() -> None:
    """When deleting a dataset
    Then the dataset should be deleted successfully
    And the dataset should no longer be accessible."""
    responses.post(
        url=f"{URL}/v3/evals/datasets",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the dataset
    dataset = Dataset.create(
        name=DATASET_NAME,
        application_id=APPLICATION_ID,
        description=DATASET_DESCRIPTION,
        metadata=DATASET_METADATA,
    )

    responses.delete(
        url=f"{URL}/v3/evals/datasets/{DATASET_ID}",
        status=HTTPStatus.NO_CONTENT,
    )

    # This should not raise an exception
    dataset.delete()

    # Verify the delete call was made
    assert len(responses.calls) == 2
    assert responses.calls[1].request.method == "DELETE"
    assert responses.calls[1].request.url == f"{URL}/v3/evals/datasets/{DATASET_ID}"
