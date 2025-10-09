from __future__ import annotations

from uuid import UUID

from fiddler_evals.pydantic_models.base import BaseModel


class OrganizationCompact(BaseModel):
    """Organization compact model"""

    id: UUID
    name: str


class ProjectCompact(BaseModel):
    """Project compact model"""

    id: UUID
    name: str


class UserCompact(BaseModel):
    """User compact model"""

    id: UUID
    full_name: str
    email: str


class ApplicationCompact(BaseModel):
    """Application compact model"""

    id: UUID
    name: str


class DatasetCompact(BaseModel):
    """Dataset compact model"""

    id: UUID
    name: str
