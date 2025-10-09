import pytest

from fiddler_evals.connection import Connection, set_connection
from fiddler_evals.pydantic_models.server_info import ServerInfo
from fiddler_evals.tests.constants import ORG_ID, ORG_NAME, SERVER_VERSION, TOKEN, URL


@pytest.fixture(autouse=True, scope="session")
def set_sdk_connection() -> Connection:
    """Global connection instance for all tests."""
    connection = Connection(
        url=URL,
        token=TOKEN,
        validate=False,
    )

    connection.server_info = ServerInfo(
        **{
            "feature_flags": {},
            "server_version": SERVER_VERSION,
            "organization": {
                "id": ORG_ID,
                "name": ORG_NAME,
            },
        }
    )
    set_connection(connection)
    yield connection
