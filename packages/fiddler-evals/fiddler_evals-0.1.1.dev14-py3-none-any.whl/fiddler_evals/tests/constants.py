from uuid import UUID

from fiddler_evals.constants import CLIENT_NAME
from fiddler_evals.pydantic_models.compact import (
    ApplicationCompact,
    DatasetCompact,
    ProjectCompact,
    UserCompact,
)
from fiddler_evals.version import __version__

URL = "https://dev.fiddler.ai"
TOKEN = "footoken"
ORG_ID = "5531bfd9-2ca2-4a7b-bb5a-136c8da09ca0"
ORG_NAME = "fiddler_dev"
SERVER_VERSION = "25.2.0"
PROJECT_NAME = "bank_churn"
PROJECT_ID = "1531bfd9-2ca2-4a7b-bb5a-136c8da09ca1"
APPLICATION_ID = "2531bfd9-2ca2-4a7b-bb5a-136c8da09ca2"
APPLICATION_NAME = "test_application"
DATASET_ID = "4531bfd9-2ca2-4a7b-bb5a-136c8da09ca4"
DATASET_NAME = "test_dataset"
EXPERIMENT_ID = "5531bfd9-2ca2-4a7b-bb5a-136c8da09ca5"
EXPERIMENT_NAME = "test_experiment"
DATASET_ITEM_ID_1 = "6631bfd9-2ca2-4a7b-bb5a-136c8da09ca6"
DATASET_ITEM_ID_2 = "7731bfd9-2ca2-4a7b-bb5a-136c8da09ca7"
USER_ID = "3531bfd9-2ca2-4a7b-bb5a-136c8da09ca3"
USER_EMAIL = "testuser@fiddler.ai"
USER_FULL_NAME = "testuser"

HEADERS = {
    "Authorization": "Bearer footoken",
    "X-Fiddler-Client-Name": CLIENT_NAME,
    "X-Fiddler-Client-Version": __version__,
}

USER_COMPACT = UserCompact(id=UUID(USER_ID), email=USER_EMAIL, full_name=USER_FULL_NAME)
PROJECT_COMPACT = ProjectCompact(id=UUID(PROJECT_ID), name=PROJECT_NAME)
APPLICATION_COMPACT = ApplicationCompact(id=UUID(APPLICATION_ID), name=APPLICATION_NAME)
DATASET_COMPACT = DatasetCompact(id=UUID(DATASET_ID), name=DATASET_NAME)
