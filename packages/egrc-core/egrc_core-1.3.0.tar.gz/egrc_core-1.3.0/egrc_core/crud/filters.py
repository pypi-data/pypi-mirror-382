"""
Filter utilities for EGRC Platform.

This module provides filtering classes and utilities for handling
query filters across all EGRC services.
"""

from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Query


class QueryFilter(BaseModel):
    """Individual query filter."""

    field: str = Field(description="Field name to filter by")
    operator: str = Field(default="eq", description="Filter operator")
    value: Any = Field(description="Filter value")
    case_sensitive: bool = Field(
        default=True, description="Case sensitivity for text filters"
    )

    class Config:
        arbitrary_types_allowed = True


class FilterBuilder:
    """Builder for creating complex query filters."""

    def __init__(self):
        """Initialize filter builder."""
        self.filters: list[QueryFilter] = []
        self.logical_operator: str = "and"  # "and" or "or"

    def add_filter(
        self, field: str, value: Any, operator: str = "eq", case_sensitive: bool = True
    ) -> "FilterBuilder":
        """
        Add a filter to the builder.

        Args:
            field: Field name
            value: Filter value
            operator: Filter operator
            case_sensitive: Case sensitivity for text filters

        Returns:
            Self for method chaining
        """
        filter_obj = QueryFilter(
            field=field, operator=operator, value=value, case_sensitive=case_sensitive
        )
        self.filters.append(filter_obj)
        return self

    def eq(self, field: str, value: Any) -> "FilterBuilder":
        """Add equality filter."""
        return self.add_filter(field, value, "eq")

    def ne(self, field: str, value: Any) -> "FilterBuilder":
        """Add not equal filter."""
        return self.add_filter(field, value, "ne")

    def gt(self, field: str, value: Any) -> "FilterBuilder":
        """Add greater than filter."""
        return self.add_filter(field, value, "gt")

    def gte(self, field: str, value: Any) -> "FilterBuilder":
        """Add greater than or equal filter."""
        return self.add_filter(field, value, "gte")

    def lt(self, field: str, value: Any) -> "FilterBuilder":
        """Add less than filter."""
        return self.add_filter(field, value, "lt")

    def lte(self, field: str, value: Any) -> "FilterBuilder":
        """Add less than or equal filter."""
        return self.add_filter(field, value, "lte")

    def like(
        self, field: str, value: str, case_sensitive: bool = True
    ) -> "FilterBuilder":
        """Add LIKE filter."""
        return self.add_filter(field, value, "like", case_sensitive)

    def ilike(self, field: str, value: str) -> "FilterBuilder":
        """Add case-insensitive LIKE filter."""
        return self.add_filter(field, value, "ilike", False)

    def in_(self, field: str, values: list[Any]) -> "FilterBuilder":
        """Add IN filter."""
        return self.add_filter(field, values, "in")

    def not_in(self, field: str, values: list[Any]) -> "FilterBuilder":
        """Add NOT IN filter."""
        return self.add_filter(field, values, "not_in")

    def is_null(self, field: str) -> "FilterBuilder":
        """Add IS NULL filter."""
        return self.add_filter(field, None, "is_null")

    def is_not_null(self, field: str) -> "FilterBuilder":
        """Add IS NOT NULL filter."""
        return self.add_filter(field, None, "is_not_null")

    def between(self, field: str, start: Any, end: Any) -> "FilterBuilder":
        """Add BETWEEN filter."""
        return self.add_filter(field, [start, end], "between")

    def contains(
        self, field: str, value: str, case_sensitive: bool = True
    ) -> "FilterBuilder":
        """Add CONTAINS filter."""
        return self.add_filter(field, value, "contains", case_sensitive)

    def starts_with(
        self, field: str, value: str, case_sensitive: bool = True
    ) -> "FilterBuilder":
        """Add STARTS WITH filter."""
        return self.add_filter(field, value, "starts_with", case_sensitive)

    def ends_with(
        self, field: str, value: str, case_sensitive: bool = True
    ) -> "FilterBuilder":
        """Add ENDS WITH filter."""
        return self.add_filter(field, value, "ends_with", case_sensitive)

    def regex(
        self, field: str, pattern: str, case_sensitive: bool = True
    ) -> "FilterBuilder":
        """Add regex filter."""
        return self.add_filter(field, pattern, "regex", case_sensitive)

    def set_logical_operator(self, operator: str) -> "FilterBuilder":
        """
        Set the logical operator for combining filters.

        Args:
            operator: "and" or "or"

        Returns:
            Self for method chaining
        """
        if operator not in ["and", "or"]:
            raise ValueError("Logical operator must be 'and' or 'or'")
        self.logical_operator = operator
        return self

    def clear(self) -> "FilterBuilder":
        """Clear all filters."""
        self.filters.clear()
        return self

    def build(self, model_class: Any) -> Any:
        """
        Build SQLAlchemy filter expression.

        Args:
            model_class: SQLAlchemy model class

        Returns:
            SQLAlchemy filter expression
        """
        if not self.filters:
            return None

        conditions = []

        for filter_obj in self.filters:
            if not hasattr(model_class, filter_obj.field):
                continue

            column = getattr(model_class, filter_obj.field)
            condition = self._build_condition(column, filter_obj)

            if condition is not None:
                conditions.append(condition)

        if not conditions:
            return None

        if self.logical_operator == "or":
            return or_(*conditions)
        else:
            return and_(*conditions)

    def _build_condition(self, column: Any, filter_obj: QueryFilter) -> Any:
        """
        Build a single filter condition.

        Args:
            column: SQLAlchemy column
            filter_obj: Filter object

        Returns:
            SQLAlchemy condition
        """
        operator = filter_obj.operator
        value = filter_obj.value

        if operator == "eq":
            return column == value
        elif operator == "ne":
            return column != value
        elif operator == "gt":
            return column > value
        elif operator == "gte":
            return column >= value
        elif operator == "lt":
            return column < value
        elif operator == "lte":
            return column <= value
        elif operator == "like":
            if filter_obj.case_sensitive:
                return column.like(f"%{value}%")
            else:
                return func.lower(column).like(f"%{value.lower()}%")
        elif operator == "ilike":
            return column.ilike(f"%{value}%")
        elif operator == "in":
            return column.in_(value)
        elif operator == "not_in":
            return ~column.in_(value)
        elif operator == "is_null":
            return column.is_(None)
        elif operator == "is_not_null":
            return column.is_not(None)
        elif operator == "between":
            return column.between(value[0], value[1])
        elif operator == "contains":
            if filter_obj.case_sensitive:
                return column.contains(value)
            else:
                return func.lower(column).contains(value.lower())
        elif operator == "starts_with":
            if filter_obj.case_sensitive:
                return column.like(f"{value}%")
            else:
                return func.lower(column).like(f"{value.lower()}%")
        elif operator == "ends_with":
            if filter_obj.case_sensitive:
                return column.like(f"%{value}")
            else:
                return func.lower(column).like(f"%{value.lower()}")
        elif operator == "regex":
            if filter_obj.case_sensitive:
                return column.op("~")(value)
            else:
                return column.op("~*")(value)

        return None


class FilterParams(BaseModel):
    """Filter parameters container."""

    filters: dict[str, Any] = Field(
        default_factory=dict, description="Filter dictionary"
    )
    search: str | None = Field(default=None, description="Search query")
    search_fields: list[str] = Field(
        default_factory=list, description="Fields to search in"
    )

    def to_filter_builder(self, model_class: Any) -> FilterBuilder:
        """
        Convert to FilterBuilder.

        Args:
            model_class: SQLAlchemy model class

        Returns:
            FilterBuilder instance
        """
        builder = FilterBuilder()

        # Add regular filters
        for field, value in self.filters.items():
            if isinstance(value, dict):
                # Handle complex filters
                for op, val in value.items():
                    builder.add_filter(field, val, op)
            elif isinstance(value, list):
                # Handle IN filters
                builder.in_(field, value)
            else:
                # Handle simple equality
                builder.eq(field, value)

        # Add search filter
        if self.search and self.search_fields:
            # search_conditions = []
            for field in self.search_fields:
                if hasattr(model_class, field):
                    builder.like(field, self.search, case_sensitive=False)

        return builder

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FilterParams":
        """
        Create FilterParams from dictionary.

        Args:
            data: Dictionary containing filter data

        Returns:
            FilterParams instance
        """
        return cls(
            filters=data.get("filters", {}),
            search=data.get("search"),
            search_fields=data.get("search_fields", []),
        )


def create_filter_builder() -> FilterBuilder:
    """
    Create a new FilterBuilder instance.

    Returns:
        FilterBuilder instance
    """
    return FilterBuilder()


def apply_filters_to_query(
    query: Query,
    model_class: Any,
    filters: dict[str, Any] | FilterParams | FilterBuilder | None = None,
) -> Query:
    """
    Apply filters to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model_class: SQLAlchemy model class
        filters: Filter parameters

    Returns:
        Query with filters applied
    """
    if not filters:
        return query

    if isinstance(filters, dict):
        filter_params = FilterParams.from_dict(filters)
        builder = filter_params.to_filter_builder(model_class)
    elif isinstance(filters, FilterParams):
        builder = filters.to_filter_builder(model_class)
    elif isinstance(filters, FilterBuilder):
        builder = filters
    else:
        return query

    condition = builder.build(model_class)
    if condition is not None:
        query = query.filter(condition)

    return query
