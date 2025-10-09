import json
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import pytest
import responses
from responses import matchers

from fiddler_evals.entities.application import Application
from fiddler_evals.exceptions import Conflict, NotFound
from fiddler_evals.tests.constants import (
    APPLICATION_ID,
    APPLICATION_NAME,
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

API_RESPONSE_200 = {
    "data": {
        "id": APPLICATION_ID,
        "name": APPLICATION_NAME,
        "organization": {
            "id": ORG_ID,
            "name": ORG_NAME,
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
        "message": "Application already exists",
        "errors": [
            {
                "reason": "Conflict",
                "message": "Application already exists",
                "help": "",
            }
        ],
    }
}

API_RESPONSE_404 = {
    "error": {
        "code": 404,
        "message": "Application not found for the given identifier",
        "errors": [
            {
                "reason": "ObjectNotFound",
                "message": "Application not found for the given identifier",
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
                "name": "test_application_2",
                "organization": {
                    "id": ORG_ID,
                    "name": ORG_NAME,
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
def test_create_application_success() -> None:
    responses.post(
        url=f"{URL}/v3/applications",
        json=API_RESPONSE_200,
    )
    application = Application.create(name=APPLICATION_NAME, project_id=PROJECT_ID)
    assert isinstance(application, Application)
    assert application.id == UUID(APPLICATION_ID)
    assert application.name == APPLICATION_NAME
    assert application.created_at == datetime.fromisoformat(
        API_RESPONSE_200["data"]["created_at"]
    )
    assert application.updated_at == datetime.fromisoformat(
        API_RESPONSE_200["data"]["updated_at"]
    )
    assert application.project.id == UUID(PROJECT_ID)
    assert application.project.name == PROJECT_NAME
    assert application.created_by.id == UUID(USER_ID)
    assert application.created_by.email == USER_EMAIL
    assert application.created_by.full_name == USER_FULL_NAME

    assert json.loads(responses.calls[0].request.body) == {
        "name": APPLICATION_NAME,
        "project_id": PROJECT_ID,
    }


@responses.activate
def test_create_application_conflict() -> None:
    responses.post(
        url=f"{URL}/v3/applications", json=API_RESPONSE_409, status=HTTPStatus.CONFLICT
    )

    with pytest.raises(Conflict):
        Application.create(name=APPLICATION_NAME, project_id=PROJECT_ID)


@responses.activate
def test_get_application_by_id_success() -> None:
    responses.get(
        url=f"{URL}/v3/applications/{APPLICATION_ID}",
        json=API_RESPONSE_200,
    )
    application = Application.get_by_id(id_=APPLICATION_ID)
    assert isinstance(application, Application)
    assert application.id == UUID(APPLICATION_ID)
    assert application.name == APPLICATION_NAME


@responses.activate
def test_get_application_by_id_not_found() -> None:
    responses.get(
        url=f"{URL}/v3/applications/{APPLICATION_ID}",
        json=API_RESPONSE_404,
        status=HTTPStatus.NOT_FOUND,
    )

    with pytest.raises(NotFound):
        Application.get_by_id(id_=APPLICATION_ID)


@responses.activate
def test_get_application_by_name_success() -> None:
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{APPLICATION_NAME}"}},{{"field":"project_id","operator":"equal","value":"{PROJECT_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/applications",
        json=API_RESPONSE_FROM_NAME,
        match=[matchers.query_param_matcher(params)],
    )
    application = Application.get_by_name(name=APPLICATION_NAME, project_id=PROJECT_ID)
    assert isinstance(application, Application)
    assert application.id == UUID(APPLICATION_ID)
    assert application.name == APPLICATION_NAME


@responses.activate
def test_get_application_by_name_not_found() -> None:
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{APPLICATION_NAME}"}},{{"field":"project_id","operator":"equal","value":"{PROJECT_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/applications",
        json=resp,
        match=[matchers.query_param_matcher(params)],
    )

    with pytest.raises(NotFound):
        Application.get_by_name(name=APPLICATION_NAME, project_id=PROJECT_ID)


@responses.activate
def test_list_applications_success() -> None:
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"project_id","operator":"equal","value":"{PROJECT_ID}"}}]}}',
        "limit": 50,
        "offset": 0,
    }
    responses.get(
        url=f"{URL}/v3/applications",
        json=LIST_API_RESPONSE,
        match=[matchers.query_param_matcher(params)],
    )
    applications = list(Application.list(project_id=PROJECT_ID))
    assert len(applications) == 2
    for application in applications:
        assert isinstance(application, Application)
        assert application.project.id == UUID(PROJECT_ID)


@responses.activate
def test_list_applications_empty() -> None:
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"project_id","operator":"equal","value":"{PROJECT_ID}"}}]}}',
        "limit": 50,
        "offset": 0,
    }
    responses.get(
        url=f"{URL}/v3/applications",
        json=resp,
        match=[matchers.query_param_matcher(params)],
    )
    applications = list(Application.list(project_id=PROJECT_ID))
    assert len(applications) == 0


@responses.activate
def test_get_or_create_application_new() -> None:
    # When application doesn't exist
    resp = deepcopy(API_RESPONSE_FROM_NAME)
    resp["data"]["total"] = 0
    resp["data"]["item_count"] = 0
    resp["data"]["items"] = []

    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{APPLICATION_NAME}"}},{{"field":"project_id","operator":"equal","value":"{PROJECT_ID}"}}]}}'
    }

    # Find application by name
    responses.get(
        url=f"{URL}/v3/applications",
        json=resp,
        match=[
            matchers.query_param_matcher(params),
            matchers.header_matcher(HEADERS),
        ],
    )

    # POST call to create
    responses.post(
        url=f"{URL}/v3/applications",
        json=API_RESPONSE_200,
        match=[matchers.header_matcher({"Content-Type": "application/json"})],
    )

    # This call will create the application
    application = Application.get_or_create(
        name=APPLICATION_NAME, project_id=PROJECT_ID
    )
    assert application.id == UUID(APPLICATION_ID)
    assert application.name == APPLICATION_NAME

    assert len(responses.calls) == 2


@responses.activate
def test_get_or_create_application_exists() -> None:
    # When application exists
    params = {
        "filter": f'{{"condition":"AND","rules":[{{"field":"name","operator":"equal","value":"{APPLICATION_NAME}"}},{{"field":"project_id","operator":"equal","value":"{PROJECT_ID}"}}]}}'
    }
    responses.get(
        url=f"{URL}/v3/applications",
        json=API_RESPONSE_FROM_NAME,
        match=[
            matchers.query_param_matcher(params),
            matchers.header_matcher(HEADERS),
        ],
    )

    # This call will fetch the application
    application = Application.get_or_create(
        name=APPLICATION_NAME, project_id=PROJECT_ID
    )
    assert application.id == UUID(APPLICATION_ID)
    assert application.name == APPLICATION_NAME

    assert len(responses.calls) == 1
