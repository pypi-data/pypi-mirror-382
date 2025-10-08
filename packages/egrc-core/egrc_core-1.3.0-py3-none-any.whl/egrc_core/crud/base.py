"""
CRUD mixin classes for EGRC Platform.

This module provides mixin classes that can be used to add CRUD functionality
to any class that has access to a database session and model.

Note: Shared components (PaginatedResult, PaginationParams, FilterBuilder) are imported from ..database.base.
"""

from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..database.base import FilterBuilder, PaginatedResult, PaginationParams, BaseModel as SQLAlchemyBaseModel
from .sorting import SortParams


# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)


class CRUDMixin:
    """
    Mixin class providing common CRUD operations.

    This mixin can be used to add CRUD functionality to any class
    that has access to a database session and model.
    """

    def __init__(self, model: type[ModelType]):
        """Initialize the mixin with a model."""
        self.model = model
        self.filter_builder = FilterBuilder()

    def _apply_filters(self, query: Any, filters: dict[str, Any] | None = None) -> Any:
        """
        Apply filters to a query.

        Args:
            query: SQLAlchemy query
            filters: Dictionary of filters

        Returns:
            Filtered query
        """
        if not filters:
            return query

        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    query = query.filter(getattr(self.model, field).in_(value))
                elif isinstance(value, dict):
                    query = self._apply_dict_filter(query, field, value)
                else:
                    query = query.filter(getattr(self.model, field) == value)

        return query

    def _apply_dict_filter(self, query: Any, field: str, value: dict) -> Any:
        """
        Apply dictionary-based filters (range, like) to a query.

        Args:
            query: SQLAlchemy query
            field: Field name
            value: Dictionary of filter operations

        Returns:
            Filtered query
        """
        column = getattr(self.model, field)
        if "gte" in value:
            query = query.filter(column >= value["gte"])
        if "lte" in value:
            query = query.filter(column <= value["lte"])
        if "gt" in value:
            query = query.filter(column > value["gt"])
        if "lt" in value:
            query = query.filter(column < value["lt"])
        if "like" in value:
            query = query.filter(column.like(f"%{value['like']}%"))
        return query

    def _apply_sorting(self, query: Any, sort_params: SortParams | None = None) -> Any:
        """
        Apply sorting to a query.

        Args:
            query: SQLAlchemy query
            sort_params: Sorting parameters

        Returns:
            Sorted query
        """
        if not sort_params:
            return query

        for field, direction in sort_params.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                if direction == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        return query

    def _apply_pagination(
        self, query: Any, pagination: PaginationParams | None = None
    ) -> Any:
        """
        Apply pagination to a query.

        Args:
            query: SQLAlchemy query
            pagination: Pagination parameters

        Returns:
            Paginated query
        """
        if not pagination:
            return query

        return query.offset(pagination.skip).limit(pagination.limit)

    def build_query(
        self,
        db: Session | AsyncSession,
        filters: dict[str, Any] | None = None,
        sort_params: SortParams | None = None,
        pagination: PaginationParams | None = None,
    ) -> Any:
        """
        Build a complete query with filters, sorting, and pagination.

        Args:
            db: Database session
            filters: Dictionary of filters
            sort_params: Sorting parameters
            pagination: Pagination parameters

        Returns:
            Built query
        """
        query = select(self.model)

        # Apply filters
        query = self._apply_filters(query, filters)

        # Apply sorting
        query = self._apply_sorting(query, sort_params)

        # Apply pagination
        query = self._apply_pagination(query, pagination)

        return query

    def get_paginated_result(
        self,
        db: Session | AsyncSession,
        items: list[ModelType],
        total: int,
        pagination: PaginationParams,
    ) -> PaginatedResult[ModelType]:
        """
        Create a paginated result.

        Args:
            db: Database session
            items: List of items
            total: Total count
            pagination: Pagination parameters

        Returns:
            Paginated result
        """
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=(total + pagination.page_size - 1) // pagination.page_size,
        )
