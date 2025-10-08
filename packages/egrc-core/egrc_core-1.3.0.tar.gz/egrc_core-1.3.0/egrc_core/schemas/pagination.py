"""
Pagination schemas for EGRC Platform.

This module provides Pydantic schemas for pagination requests and responses.
"""

from typing import Generic, TypeVar

from pydantic import Field, validator

from .base import BaseSchema


T = TypeVar("T")


class PaginationRequest(BaseSchema):
    """Schema for pagination requests."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Number of items per page"
    )

    @validator("page_size")
    def validate_page_size(cls, v):
        """Validate page size is within limits."""
        if v > 100:
            raise ValueError("Page size cannot exceed 100")
        return v

    @property
    def skip(self) -> int:
        """Calculate number of items to skip."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get the limit (same as page_size)."""
        return self.page_size


class PaginationResponse(BaseSchema, Generic[T]):
    """Schema for paginated responses."""

    items: list[T] = Field(description="List of items in current page")
    total: int = Field(ge=0, description="Total number of items")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Number of items per page")
    pages: int = Field(ge=0, description="Total number of pages")

    @validator("pages", always=True)
    def calculate_pages(cls, v, values):
        """Calculate total pages based on total and page_size."""
        total = values.get("total", 0)
        page_size = values.get("page_size", 1)
        return (total + page_size - 1) // page_size if total > 0 else 0

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.pages

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1

    @property
    def next_page(self) -> int | None:
        """Get next page number."""
        return self.page + 1 if self.has_next else None

    @property
    def previous_page(self) -> int | None:
        """Get previous page number."""
        return self.page - 1 if self.has_previous else None
