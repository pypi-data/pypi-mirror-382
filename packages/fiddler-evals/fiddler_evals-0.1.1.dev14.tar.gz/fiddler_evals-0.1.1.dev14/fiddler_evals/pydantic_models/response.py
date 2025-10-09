import enum
from typing import Dict, List

from fiddler_evals.pydantic_models.base import BaseModel


@enum.unique
class ApiResponseKind(str, enum.Enum):
    NORMAL = "NORMAL"
    PAGINATED = "PAGINATED"
    ERROR = "ERROR"


class ApiResponse(BaseModel):
    data: Dict
    api_version: str = "3.0"
    kind: str = ApiResponseKind.NORMAL


class PaginatedResponseData(BaseModel):
    page_size: int  # Num of items per page
    total: int  # Total num of items matching the query
    item_count: int  # Num of items in the current page
    page_count: int  # Total num of pages based on page size
    page_index: int  # Index of this page, starting from 1
    offset: int  # Offset for this page
    items: List[Dict]  # Items of the current page


class PaginatedApiResponse(BaseModel):
    data: PaginatedResponseData
    api_version: str = "3.0"
    kind: str = ApiResponseKind.PAGINATED


class ErrorItem(BaseModel):
    reason: str
    message: str
    help: str


class ErrorData(BaseModel):
    code: int
    message: str
    errors: List[ErrorItem]


class ErrorResponse(BaseModel):
    error: ErrorData
    api_version: str = "3.0"
    kind: str = ApiResponseKind.ERROR
