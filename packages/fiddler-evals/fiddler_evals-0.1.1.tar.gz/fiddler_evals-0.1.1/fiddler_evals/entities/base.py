from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, TypeVar

from requests import Response

from fiddler_evals.configs import REQUEST_PAGE_SIZE
from fiddler_evals.connection import ConnectionMixin
from fiddler_evals.pydantic_models.response import PaginatedApiResponse

BaseEntityType = TypeVar(  # pylint: disable=invalid-name
    "BaseEntityType", bound="BaseEntity"
)


class BaseEntity(ABC, ConnectionMixin):
    """Abstract base class for all Fiddler API entities.

    Provides common functionality for response parsing, pagination, and connection
    management. All entity classes must inherit from this and implement _from_dict.
    """

    @classmethod
    def _from_response(cls: type[BaseEntityType], response: Response) -> BaseEntityType:
        """Create entity instance from HTTP response."""
        return cls._from_dict(data=response.json()["data"])

    @classmethod
    @abstractmethod
    def _from_dict(cls: type[BaseEntityType], data: dict) -> BaseEntityType:
        """Create entity instance from dictionary data. Must be implemented by subclasses."""

    @classmethod
    def _paginate(
        cls, url: str, params: dict | None = None, page_size: int = REQUEST_PAGE_SIZE
    ) -> Iterator[dict]:
        """Iterate over paginated API endpoints using offset-based pagination."""
        offset = 0
        params = params or {}
        params.update({"limit": page_size})

        while True:
            params.update({"offset": offset})
            response = cls._client().get(
                url=url,
                params=params,
            )
            resp_obj = PaginatedApiResponse(**response.json()).data

            yield from resp_obj.items

            if resp_obj.page_index >= resp_obj.page_count:
                # Last page
                break

            # Update offset
            offset = resp_obj.offset + page_size
