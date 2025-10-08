"""
Shared database components for EGRC Platform.

This module provides shared database components including pagination,
filtering, and utility classes that are used across the EGRC platform.
"""

import logging
from typing import Any, Generic, TypeVar, Union

from sqlalchemy import func, select

# Type aliases
ModelType = TypeVar("ModelType")
IDType = Union[int, str]
FilterType = dict[str, Any]
OrderByType = Union[str, list[str]]


# Simple pagination result class
class PaginatedResult(Generic[ModelType]):
    """Paginated result container."""

    def __init__(self, items: list[ModelType], total: int, page: int, size: int):
        self.items = items
        self.total = total
        self.page = page
        self.size = size


# Simple pagination params class
class PaginationParams:
    """Pagination parameters."""

    def __init__(self, page: int = 1, size: int = 20):
        self.page = page
        self.size = size


# Simple filter builder
class FilterBuilder:
    """Filter builder for database queries."""

    def __init__(self, model: type[ModelType], filters: dict[str, Any]):
        self.model = model
        self.filters = filters

    def build(self) -> list[Any]:
        """Build filter expressions from the filters dict."""
        expressions = []
        for field, value in self.filters.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                if isinstance(value, dict):
                    # Handle complex filters like {"gte": 10, "lte": 20}
                    for op, val in value.items():
                        if op == "eq":
                            expressions.append(column == val)
                        elif op == "ne":
                            expressions.append(column != val)
                        elif op == "gt":
                            expressions.append(column > val)
                        elif op == "gte":
                            expressions.append(column >= val)
                        elif op == "lt":
                            expressions.append(column < val)
                        elif op == "lte":
                            expressions.append(column <= val)
                        elif op == "like":
                            expressions.append(column.like(f"%{val}%"))
                        elif op == "ilike":
                            expressions.append(column.ilike(f"%{val}%"))
                        elif op == "in":
                            expressions.append(column.in_(val))
                        elif op == "not_in":
                            expressions.append(~column.in_(val))
                else:
                    # Simple equality filter
                    expressions.append(column == value)
        return expressions


def parse_filter_dict(model: type[ModelType], filters: dict[str, Any]) -> FilterBuilder:
    """Parse filter dictionary and return a FilterBuilder instance."""
    return FilterBuilder(model, filters)


# Simple pagination helper
class PaginationHelper:
    """Helper class for pagination operations."""

    @staticmethod
    async def get_total_count(db, query: Any) -> int:
        """Get total count for a query."""
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar() or 0

    @staticmethod
    def apply_pagination(query: Any, pagination: PaginationParams) -> Any:
        """Apply pagination to a query."""
        offset = (pagination.page - 1) * pagination.size
        return query.offset(offset).limit(pagination.size)

    @staticmethod
    def create_paginated_result(
        items: list[ModelType], total: int, pagination: PaginationParams
    ) -> PaginatedResult[ModelType]:
        """Create a paginated result."""
        return PaginatedResult(
            items=items, total=total, page=pagination.page, size=pagination.size
        )


# Logger for this module
logger = logging.getLogger(__name__)
