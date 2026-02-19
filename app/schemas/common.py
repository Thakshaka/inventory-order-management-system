"""
Common/shared Pydantic schemas.
"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str
