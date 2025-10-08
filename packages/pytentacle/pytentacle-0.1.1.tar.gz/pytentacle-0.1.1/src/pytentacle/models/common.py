"""Common models used across the API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Link(BaseModel):
    """HATEOAS link."""

    href: str = Field(description="URL of the linked resource")
    method: str = Field(description="HTTP method to use")
    rel: str = Field(description="Relationship type")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    count: int = Field(description="Total number of results")
    next: str | None = Field(None, description="URL to next page")
    previous: str | None = Field(None, description="URL to previous page")
    results: list[T] = Field(description="List of results for this page")


class GridSupplyPoint(BaseModel):
    """Grid Supply Point (GSP) identifier.

    GSPs are the 14 regional distribution zones in the UK.
    """

    group_id: str = Field(
        description="GSP group ID (e.g., '_A', '_B', '_H')",
        alias="groupId",
    )

    model_config = ConfigDict(populate_by_name=True)
