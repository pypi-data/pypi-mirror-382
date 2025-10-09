from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from fiddler_evals.pydantic_models.base import BaseModel
from fiddler_evals.pydantic_models.compact import (
    ApplicationCompact,
    OrganizationCompact,
    ProjectCompact,
    UserCompact,
)


class DatasetResponse(BaseModel):
    """Dataset response from Fiddler API"""

    id: UUID
    name: str
    description: str | None
    metadata: dict
    active: bool
    created_at: datetime
    updated_at: datetime
    created_by: UserCompact
    updated_by: UserCompact
    organization: OrganizationCompact
    project: ProjectCompact
    application: ApplicationCompact


class NewDatasetItem(BaseModel):
    """Model to create a new dataset"""

    id: UUID | None = Field(default_factory=uuid4)
    inputs: dict[str, Any]
    expected_outputs: dict[str, Any] | None = None
    metadata: dict = Field(default_factory=dict)
    extras: dict = Field(default_factory=dict)
    source_name: str | None = None
    source_id: str | None = None


class DatasetItem(BaseModel):
    """Dataset item from Fiddler API"""

    id: UUID
    inputs: dict[str, Any]
    expected_outputs: dict[str, Any] | None = None
    metadata: dict = Field(default_factory=dict)
    extras: dict = Field(default_factory=dict)
    source_name: str | None = None
    source_id: str | None = None
    created_at: datetime
    updated_at: datetime
