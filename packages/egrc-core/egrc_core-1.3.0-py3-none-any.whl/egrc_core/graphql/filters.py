"""
GraphQL filters implementation.

This module provides filtering functionality for GraphQL queries
with support for various filter types and operations.
"""

from datetime import datetime
from typing import Any

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Query


@strawberry.input
class StringFilter:
    """String filter input type."""

    eq: str | None = strawberry.field(default=None, description="Equal to")
    ne: str | None = strawberry.field(default=None, description="Not equal to")
    like: str | None = strawberry.field(default=None, description="Like pattern")
    ilike: str | None = strawberry.field(
        default=None, description="Case-insensitive like"
    )
    in_: list[str] | None = strawberry.field(
        default=None, name="in", description="In list"
    )
    nin: list[str] | None = strawberry.field(default=None, description="Not in list")
    is_null: bool | None = strawberry.field(default=None, description="Is null")
    is_not_null: bool | None = strawberry.field(default=None, description="Is not null")


@strawberry.input
class IntFilter:
    """Integer filter input type."""

    eq: int | None = strawberry.field(default=None, description="Equal to")
    ne: int | None = strawberry.field(default=None, description="Not equal to")
    gt: int | None = strawberry.field(default=None, description="Greater than")
    gte: int | None = strawberry.field(
        default=None, description="Greater than or equal"
    )
    lt: int | None = strawberry.field(default=None, description="Less than")
    lte: int | None = strawberry.field(default=None, description="Less than or equal")
    in_: list[int] | None = strawberry.field(
        default=None, name="in", description="In list"
    )
    nin: list[int] | None = strawberry.field(default=None, description="Not in list")
    is_null: bool | None = strawberry.field(default=None, description="Is null")
    is_not_null: bool | None = strawberry.field(default=None, description="Is not null")


@strawberry.input
class FloatFilter:
    """Float filter input type."""

    eq: float | None = strawberry.field(default=None, description="Equal to")
    ne: float | None = strawberry.field(default=None, description="Not equal to")
    gt: float | None = strawberry.field(default=None, description="Greater than")
    gte: float | None = strawberry.field(
        default=None, description="Greater than or equal"
    )
    lt: float | None = strawberry.field(default=None, description="Less than")
    lte: float | None = strawberry.field(default=None, description="Less than or equal")
    in_: list[float] | None = strawberry.field(
        default=None, name="in", description="In list"
    )
    nin: list[float] | None = strawberry.field(default=None, description="Not in list")
    is_null: bool | None = strawberry.field(default=None, description="Is null")
    is_not_null: bool | None = strawberry.field(default=None, description="Is not null")


@strawberry.input
class BooleanFilter:
    """Boolean filter input type."""

    eq: bool | None = strawberry.field(default=None, description="Equal to")
    ne: bool | None = strawberry.field(default=None, description="Not equal to")
    is_null: bool | None = strawberry.field(default=None, description="Is null")
    is_not_null: bool | None = strawberry.field(default=None, description="Is not null")


@strawberry.input
class DateFilter:
    """Date filter input type."""

    eq: datetime | None = strawberry.field(default=None, description="Equal to")
    ne: datetime | None = strawberry.field(default=None, description="Not equal to")
    gt: datetime | None = strawberry.field(default=None, description="Greater than")
    gte: datetime | None = strawberry.field(
        default=None, description="Greater than or equal"
    )
    lt: datetime | None = strawberry.field(default=None, description="Less than")
    lte: datetime | None = strawberry.field(
        default=None, description="Less than or equal"
    )
    in_: list[datetime] | None = strawberry.field(
        default=None, name="in", description="In list"
    )
    nin: list[datetime] | None = strawberry.field(
        default=None, description="Not in list"
    )
    is_null: bool | None = strawberry.field(default=None, description="Is null")
    is_not_null: bool | None = strawberry.field(default=None, description="Is not null")


@strawberry.input
class JSONFilter:
    """JSON filter input type."""

    contains: str | None = strawberry.field(default=None, description="Contains key")
    contains_key: str | None = strawberry.field(
        default=None, description="Contains specific key"
    )
    contains_value: str | None = strawberry.field(
        default=None, description="Contains specific value"
    )
    is_null: bool | None = strawberry.field(default=None, description="Is null")
    is_not_null: bool | None = strawberry.field(default=None, description="Is not null")


class FilterField:
    """Base class for filter fields."""

    def __init__(self, field_name: str, filter_type: type):
        """Initialize filter field.

        Args:
            field_name: The database field name
            filter_type: The filter type class
        """
        self.field_name = field_name
        self.filter_type = filter_type

    def apply(self, query: Query, filter_value: Any) -> Query:
        """Apply filter to query.

        Args:
            query: SQLAlchemy query
            filter_value: Filter value

        Returns:
            Modified query
        """
        if filter_value is None:
            return query

        field = getattr(query.column_descriptions[0]["entity"], self.field_name)
        return self._apply_filter(query, field, filter_value)

    def _apply_filter(self, query: Query, field: Any, filter_value: Any) -> Query:
        """Apply specific filter logic.

        Args:
            query: SQLAlchemy query
            field: Database field
            filter_value: Filter value

        Returns:
            Modified query
        """
        raise NotImplementedError


class StringFilterField(FilterField):
    """String filter field implementation."""

    def __init__(self, field_name: str):
        super().__init__(field_name, StringFilter)

    def _apply_filter(
        self, query: Query, field: Any, filter_value: StringFilter
    ) -> Query:
        """Apply string filter."""
        conditions = []

        if filter_value.eq is not None:
            conditions.append(field == filter_value.eq)

        if filter_value.ne is not None:
            conditions.append(field != filter_value.ne)

        if filter_value.like is not None:
            conditions.append(field.like(filter_value.like))

        if filter_value.ilike is not None:
            conditions.append(field.ilike(filter_value.ilike))

        if filter_value.in_ is not None:
            conditions.append(field.in_(filter_value.in_))

        if filter_value.nin is not None:
            conditions.append(~field.in_(filter_value.nin))

        if filter_value.is_null is not None:
            if filter_value.is_null:
                conditions.append(field.is_(None))
            else:
                conditions.append(field.is_not(None))

        if filter_value.is_not_null is not None:
            if filter_value.is_not_null:
                conditions.append(field.is_not(None))
            else:
                conditions.append(field.is_(None))

        if conditions:
            query = query.filter(and_(*conditions))

        return query


class IntFilterField(FilterField):
    """Integer filter field implementation."""

    def __init__(self, field_name: str):
        super().__init__(field_name, IntFilter)

    def _apply_filter(self, query: Query, field: Any, filter_value: IntFilter) -> Query:
        """Apply integer filter."""
        conditions = []

        if filter_value.eq is not None:
            conditions.append(field == filter_value.eq)

        if filter_value.ne is not None:
            conditions.append(field != filter_value.ne)

        if filter_value.gt is not None:
            conditions.append(field > filter_value.gt)

        if filter_value.gte is not None:
            conditions.append(field >= filter_value.gte)

        if filter_value.lt is not None:
            conditions.append(field < filter_value.lt)

        if filter_value.lte is not None:
            conditions.append(field <= filter_value.lte)

        if filter_value.in_ is not None:
            conditions.append(field.in_(filter_value.in_))

        if filter_value.nin is not None:
            conditions.append(~field.in_(filter_value.nin))

        if filter_value.is_null is not None:
            if filter_value.is_null:
                conditions.append(field.is_(None))
            else:
                conditions.append(field.is_not(None))

        if filter_value.is_not_null is not None:
            if filter_value.is_not_null:
                conditions.append(field.is_not(None))
            else:
                conditions.append(field.is_(None))

        if conditions:
            query = query.filter(and_(*conditions))

        return query


class BooleanFilterField(FilterField):
    """Boolean filter field implementation."""

    def __init__(self, field_name: str):
        super().__init__(field_name, BooleanFilter)

    def _apply_filter(
        self, query: Query, field: Any, filter_value: BooleanFilter
    ) -> Query:
        """Apply boolean filter."""
        conditions = []

        if filter_value.eq is not None:
            conditions.append(field == filter_value.eq)

        if filter_value.ne is not None:
            conditions.append(field != filter_value.ne)

        if filter_value.is_null is not None:
            if filter_value.is_null:
                conditions.append(field.is_(None))
            else:
                conditions.append(field.is_not(None))

        if filter_value.is_not_null is not None:
            if filter_value.is_not_null:
                conditions.append(field.is_not(None))
            else:
                conditions.append(field.is_(None))

        if conditions:
            query = query.filter(and_(*conditions))

        return query


class DateFilterField(FilterField):
    """Date filter field implementation."""

    def __init__(self, field_name: str):
        super().__init__(field_name, DateFilter)

    def _apply_filter(
        self, query: Query, field: Any, filter_value: DateFilter
    ) -> Query:
        """Apply date filter."""
        conditions = []

        if filter_value.eq is not None:
            conditions.append(field == filter_value.eq)

        if filter_value.ne is not None:
            conditions.append(field != filter_value.ne)

        if filter_value.gt is not None:
            conditions.append(field > filter_value.gt)

        if filter_value.gte is not None:
            conditions.append(field >= filter_value.gte)

        if filter_value.lt is not None:
            conditions.append(field < filter_value.lt)

        if filter_value.lte is not None:
            conditions.append(field <= filter_value.lte)

        if filter_value.in_ is not None:
            conditions.append(field.in_(filter_value.in_))

        if filter_value.nin is not None:
            conditions.append(~field.in_(filter_value.nin))

        if filter_value.is_null is not None:
            if filter_value.is_null:
                conditions.append(field.is_(None))
            else:
                conditions.append(field.is_not(None))

        if filter_value.is_not_null is not None:
            if filter_value.is_not_null:
                conditions.append(field.is_not(None))
            else:
                conditions.append(field.is_(None))

        if conditions:
            query = query.filter(and_(*conditions))

        return query


class JSONFilterField(FilterField):
    """JSON filter field implementation."""

    def __init__(self, field_name: str):
        super().__init__(field_name, JSONFilter)

    def _apply_filter(
        self, query: Query, field: Any, filter_value: JSONFilter
    ) -> Query:
        """Apply JSON filter."""
        conditions = []

        if filter_value.contains is not None:
            conditions.append(field.contains(filter_value.contains))

        if filter_value.contains_key is not None:
            conditions.append(field.has_key(filter_value.contains_key))

        if filter_value.contains_value is not None:
            conditions.append(field.contains_value(filter_value.contains_value))

        if filter_value.is_null is not None:
            if filter_value.is_null:
                conditions.append(field.is_(None))
            else:
                conditions.append(field.is_not(None))

        if filter_value.is_not_null is not None:
            if filter_value.is_not_null:
                conditions.append(field.is_not(None))
            else:
                conditions.append(field.is_(None))

        if conditions:
            query = query.filter(and_(*conditions))

        return query


class FilterSet:
    """Base class for filter sets."""

    def __init__(self):
        """Initialize filter set."""
        self.filters: dict[str, FilterField] = {}

    def add_filter(self, name: str, filter_field: FilterField) -> None:
        """Add a filter field.

        Args:
            name: Filter name
            filter_field: Filter field instance
        """
        self.filters[name] = filter_field

    def apply_filters(self, query: Query, filter_input: Any) -> Query:
        """Apply all filters to query.

        Args:
            query: SQLAlchemy query
            filter_input: Filter input object

        Returns:
            Modified query
        """
        if filter_input is None:
            return query

        for filter_name, filter_field in self.filters.items():
            filter_value = getattr(filter_input, filter_name, None)
            if filter_value is not None:
                query = filter_field.apply(query, filter_value)

        return query


# Common filter sets
class BaseFilterSet(FilterSet):
    """Base filter set with common fields."""

    def __init__(self):
        super().__init__()
        self.add_filter("id", StringFilterField("id"))
        self.add_filter("created_at", DateFilterField("created_at"))
        self.add_filter("updated_at", DateFilterField("updated_at"))


class TenantFilterSet(BaseFilterSet):
    """Filter set for tenant-related entities."""

    def __init__(self):
        super().__init__()
        self.add_filter("tenant_id", StringFilterField("tenant_id"))


class SoftDeleteFilterSet(BaseFilterSet):
    """Filter set for soft-deletable entities."""

    def __init__(self):
        super().__init__()
        self.add_filter("is_deleted", BooleanFilterField("is_deleted"))
        self.add_filter("deleted_at", DateFilterField("deleted_at"))


class StatusFilterSet(BaseFilterSet):
    """Filter set for entities with status."""

    def __init__(self):
        super().__init__()
        self.add_filter("status", StringFilterField("status"))


class NameFilterSet(BaseFilterSet):
    """Filter set for entities with name."""

    def __init__(self):
        super().__init__()
        self.add_filter("name", StringFilterField("name"))
        self.add_filter("description", StringFilterField("description"))


class CodeFilterSet(BaseFilterSet):
    """Filter set for entities with code."""

    def __init__(self):
        super().__init__()
        self.add_filter("code", StringFilterField("code"))


class PriorityFilterSet(BaseFilterSet):
    """Filter set for entities with priority."""

    def __init__(self):
        super().__init__()
        self.add_filter("priority", StringFilterField("priority"))


class CategoryFilterSet(BaseFilterSet):
    """Filter set for entities with category."""

    def __init__(self):
        super().__init__()
        self.add_filter("category", StringFilterField("category"))


class ApprovalFilterSet(BaseFilterSet):
    """Filter set for entities with approval."""

    def __init__(self):
        super().__init__()
        self.add_filter("is_approved", BooleanFilterField("is_approved"))
        self.add_filter("approved_at", DateFilterField("approved_at"))
        self.add_filter("approved_by", StringFilterField("approved_by"))


class ExpiryFilterSet(BaseFilterSet):
    """Filter set for entities with expiry."""

    def __init__(self):
        super().__init__()
        self.add_filter("effective_date", DateFilterField("effective_date"))
        self.add_filter("expiry_date", DateFilterField("expiry_date"))
