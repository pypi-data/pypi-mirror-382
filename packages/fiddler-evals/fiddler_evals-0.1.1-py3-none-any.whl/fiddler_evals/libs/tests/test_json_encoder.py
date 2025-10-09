import json
from datetime import datetime
from uuid import UUID

import pytest

from fiddler_evals.libs.json_encoder import RequestClientJSONEncoder


def test_json_encoder_uuid():
    data = {"uuid_field": UUID("6ea7243e-0bf7-4323-ba1b-9f788b4a9257")}
    with pytest.raises(TypeError):
        json.dumps(data)

    assert json.dumps(data, cls=RequestClientJSONEncoder) == json.dumps(
        {"uuid_field": "6ea7243e-0bf7-4323-ba1b-9f788b4a9257"}
    )


def test_json_encoder_datetime():
    data = {"datetime_field": datetime(2024, 1, 30, 11, 1, 46)}
    with pytest.raises(TypeError):
        json.dumps(data)

    assert json.dumps(data, cls=RequestClientJSONEncoder) == json.dumps(
        {"datetime_field": "2024-01-30 11:01:46"},
    )
