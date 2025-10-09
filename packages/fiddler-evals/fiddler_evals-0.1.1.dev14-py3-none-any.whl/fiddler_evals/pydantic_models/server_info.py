from typing import Annotated, Any, Dict

from pydantic import BeforeValidator

from fiddler_evals.libs.semver import VersionInfo
from fiddler_evals.pydantic_models.base import BaseModel
from fiddler_evals.pydantic_models.compact import OrganizationCompact


def parse_version_string(v: Any) -> VersionInfo:
    """Parse version string into VersionInfo object."""
    if isinstance(v, str):
        return VersionInfo.parse(v)
    return v


class ServerInfo(BaseModel):
    feature_flags: Dict
    server_version: Annotated[VersionInfo, BeforeValidator(parse_version_string)]
    organization: OrganizationCompact
