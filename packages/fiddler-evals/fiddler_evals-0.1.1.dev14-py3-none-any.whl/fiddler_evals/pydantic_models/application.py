from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fiddler_evals.pydantic_models.base import BaseModel
from fiddler_evals.pydantic_models.compact import (
    OrganizationCompact,
    ProjectCompact,
    UserCompact,
)


class ApplicationResponse(BaseModel):
    """Application response from Fiddler API"""

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    created_by: UserCompact
    updated_by: UserCompact
    organization: OrganizationCompact
    project: ProjectCompact
