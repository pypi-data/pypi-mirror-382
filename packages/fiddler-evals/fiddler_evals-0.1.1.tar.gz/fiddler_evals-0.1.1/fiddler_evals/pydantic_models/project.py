from datetime import datetime
from uuid import UUID

from fiddler_evals.pydantic_models.base import BaseModel
from fiddler_evals.pydantic_models.compact import OrganizationCompact


class ProjectResponse(BaseModel):
    """Project response from Fiddler API"""

    id: UUID
    name: str
    asset_type: str
    created_at: datetime
    updated_at: datetime

    organization: OrganizationCompact
