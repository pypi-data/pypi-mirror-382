"""
Pagination utilities for EGRC Platform.

This module provides pagination classes and utilities for handling
paginated results across all EGRC services.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, validator

from ..constants.constants import DatabaseConstants


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=DatabaseConstants.DEFAULT_PAGE_SIZE,
        ge=1,
        le=DatabaseConstants.MAX_PAGE_SIZE,
        description="Number of items per page",
    )

    @validator("page_size")
    def validate_page_size(cls, v):
        """Validate page size is within limits."""
        if v > DatabaseConstants.MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size cannot exceed {DatabaseConstants.MAX_PAGE_SIZE}"
            )
        return v

    @property
    def skip(self) -> int:
        """Calculate number of items to skip."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get the limit (same as page_size)."""
        return self.page_size

    @property
    def offset(self) -> int:
        """Get the offset (same as skip)."""
        return self.skip


class PaginatedResult(BaseModel, Generic[T]):
    """Paginated result container."""

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

    @property
    def start_index(self) -> int:
        """Get the start index of items in current page."""
        return (self.page - 1) * self.page_size + 1 if self.total > 0 else 0

    @property
    def end_index(self) -> int:
        """Get the end index of items in current page."""
        return min(self.page * self.page_size, self.total)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "items": self.items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "pages": self.pages,
                "has_next": self.has_next,
                "has_previous": self.has_previous,
                "next_page": self.next_page,
                "previous_page": self.previous_page,
                "start_index": self.start_index,
                "end_index": self.end_index,
            },
        }


class CursorPaginationParams(BaseModel):
    """Parameters for cursor-based pagination."""

    cursor: str | None = Field(default=None, description="Cursor for pagination")
    limit: int = Field(
        default=DatabaseConstants.DEFAULT_PAGE_SIZE,
        ge=1,
        le=DatabaseConstants.MAX_PAGE_SIZE,
        description="Number of items to return",
    )
    direction: str = Field(default="next", description="Direction: 'next' or 'prev'")

    @validator("direction")
    def validate_direction(cls, v):
        """Validate direction is either 'next' or 'prev'."""
        if v not in ["next", "prev"]:
            raise ValueError("Direction must be 'next' or 'prev'")
        return v


class CursorPaginatedResult(BaseModel, Generic[T]):
    """Cursor-based paginated result container."""

    items: list[T] = Field(description="List of items")
    next_cursor: str | None = Field(default=None, description="Cursor for next page")
    prev_cursor: str | None = Field(
        default=None, description="Cursor for previous page"
    )
    has_next: bool = Field(default=False, description="Whether there is a next page")
    has_previous: bool = Field(
        default=False, description="Whether there is a previous page"
    )
    total: int | None = Field(default=None, description="Total count (if available)")

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "items": self.items,
            "pagination": {
                "next_cursor": self.next_cursor,
                "prev_cursor": self.prev_cursor,
                "has_next": self.has_next,
                "has_previous": self.has_previous,
                "total": self.total,
            },
        }


def create_pagination_params(
    page: int | None = None, page_size: int | None = None
) -> PaginationParams:
    """
    Create pagination parameters with defaults.

    Args:
        page: Page number (defaults to 1)
        page_size: Page size (defaults to DEFAULT_PAGE_SIZE)

    Returns:
        PaginationParams instance
    """
    return PaginationParams(
        page=page or 1, page_size=page_size or DatabaseConstants.DEFAULT_PAGE_SIZE
    )


def create_cursor_pagination_params(
    cursor: str | None = None, limit: int | None = None, direction: str = "next"
) -> CursorPaginationParams:
    """
    Create cursor pagination parameters with defaults.

    Args:
        cursor: Cursor for pagination
        limit: Number of items to return
        direction: Direction ('next' or 'prev')

    Returns:
        CursorPaginationParams instance
    """
    return CursorPaginationParams(
        cursor=cursor,
        limit=limit or DatabaseConstants.DEFAULT_PAGE_SIZE,
        direction=direction,
    )
