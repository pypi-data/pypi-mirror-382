"""
GraphQL sorting implementation.

This module provides sorting functionality for GraphQL queries
with support for multiple sort fields and directions.
"""

from enum import Enum

import strawberry
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query


@strawberry.enum
class SortDirection(Enum):
    """Sort direction enum."""

    ASC = "ASC"
    DESC = "DESC"


@strawberry.input
class SortField:
    """Sort field input type."""

    field: str = strawberry.field(description="Field name to sort by")
    direction: SortDirection = strawberry.field(
        default=SortDirection.ASC, description="Sort direction"
    )


@strawberry.input
class SortInput:
    """Sort input type for multiple fields."""

    fields: list[SortField] = strawberry.field(description="List of sort fields")


class SortFieldHandler:
    """Handler for sort field operations."""

    def __init__(self, field_name: str, allowed_fields: list[str] | None = None):
        """Initialize sort field handler.

        Args:
            field_name: The database field name
            allowed_fields: List of allowed field names for validation
        """
        self.field_name = field_name
        self.allowed_fields = allowed_fields or []

    def validate_field(self, field_name: str) -> bool:
        """Validate if field is allowed for sorting.

        Args:
            field_name: Field name to validate

        Returns:
            True if field is allowed
        """
        if not self.allowed_fields:
            return True
        return field_name in self.allowed_fields

    def get_sort_function(self, direction: SortDirection):
        """Get SQLAlchemy sort function.

        Args:
            direction: Sort direction

        Returns:
            SQLAlchemy sort function
        """
        if direction == SortDirection.ASC:
            return asc
        else:
            return desc


class SortSet:
    """Base class for sort sets."""

    def __init__(self):
        """Initialize sort set."""
        self.sort_handlers: dict[str, SortFieldHandler] = {}
        self.default_sort: list[SortField] | None = None

    def add_sort_field(
        self, name: str, field_name: str, allowed_fields: list[str] | None = None
    ) -> None:
        """Add a sort field.

        Args:
            name: Sort field name
            field_name: Database field name
            allowed_fields: Allowed field names for validation
        """
        self.sort_handlers[name] = SortFieldHandler(field_name, allowed_fields)

    def set_default_sort(self, sort_fields: list[SortField]) -> None:
        """Set default sort fields.

        Args:
            sort_fields: Default sort fields
        """
        self.default_sort = sort_fields

    def apply_sort(self, query: Query, sort_input: SortInput | None) -> Query:
        """Apply sorting to query.

        Args:
            query: SQLAlchemy query
            sort_input: Sort input object

        Returns:
            Modified query
        """
        if sort_input is None or not sort_input.fields:
            if self.default_sort:
                return self._apply_sort_fields(query, self.default_sort)
            return query

        return self._apply_sort_fields(query, sort_input.fields)

    def _apply_sort_fields(self, query: Query, sort_fields: list[SortField]) -> Query:
        """Apply sort fields to query.

        Args:
            query: SQLAlchemy query
            sort_fields: List of sort fields

        Returns:
            Modified query
        """
        sort_expressions = []

        for sort_field in sort_fields:
            if not self._validate_sort_field(sort_field):
                continue

            handler = self.sort_handlers.get(sort_field.field)
            if handler is None:
                continue

            # Get the database field
            field = getattr(query.column_descriptions[0]["entity"], handler.field_name)

            # Get sort function
            sort_func = handler.get_sort_function(sort_field.direction)

            # Add to sort expressions
            sort_expressions.append(sort_func(field))

        if sort_expressions:
            query = query.order_by(*sort_expressions)

        return query

    def _validate_sort_field(self, sort_field: SortField) -> bool:
        """Validate sort field.

        Args:
            sort_field: Sort field to validate

        Returns:
            True if valid
        """
        handler = self.sort_handlers.get(sort_field.field)
        if handler is None:
            return False

        return handler.validate_field(sort_field.field)


# Common sort sets
class BaseSortSet(SortSet):
    """Base sort set with common fields."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("id", "id")
        self.add_sort_field("created_at", "created_at")
        self.add_sort_field("updated_at", "updated_at")

        # Set default sort by created_at desc
        self.set_default_sort(
            [SortField(field="created_at", direction=SortDirection.DESC)]
        )


class TenantSortSet(BaseSortSet):
    """Sort set for tenant-related entities."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("tenant_id", "tenant_id")


class NameSortSet(BaseSortSet):
    """Sort set for entities with name."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("name", "name")
        self.add_sort_field("display_name", "display_name")

        # Set default sort by name asc
        self.set_default_sort([SortField(field="name", direction=SortDirection.ASC)])


class CodeSortSet(BaseSortSet):
    """Sort set for entities with code."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("code", "code")

        # Set default sort by code asc
        self.set_default_sort([SortField(field="code", direction=SortDirection.ASC)])


class PrioritySortSet(BaseSortSet):
    """Sort set for entities with priority."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("priority", "priority")

        # Set default sort by priority desc (high priority first)
        self.set_default_sort(
            [SortField(field="priority", direction=SortDirection.DESC)]
        )


class StatusSortSet(BaseSortSet):
    """Sort set for entities with status."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("status", "status")
        self.add_sort_field("is_active", "is_active")


class ApprovalSortSet(BaseSortSet):
    """Sort set for entities with approval."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("is_approved", "is_approved")
        self.add_sort_field("approved_at", "approved_at")
        self.add_sort_field("approved_by", "approved_by")


class ExpirySortSet(BaseSortSet):
    """Sort set for entities with expiry."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("effective_date", "effective_date")
        self.add_sort_field("expiry_date", "expiry_date")


class AuditSortSet(BaseSortSet):
    """Sort set for audit-related entities."""

    def __init__(self):
        super().__init__()
        self.add_sort_field("created_by", "created_by")
        self.add_sort_field("updated_by", "updated_by")
        self.add_sort_field("version", "version")


# Utility functions for common sorting operations
def create_sort_input(
    field: str, direction: SortDirection = SortDirection.ASC
) -> SortInput:
    """Create a simple sort input.

    Args:
        field: Field name to sort by
        direction: Sort direction

    Returns:
        SortInput instance
    """
    return SortInput(fields=[SortField(field=field, direction=direction)])


def create_multi_sort_input(sort_fields: list[tuple]) -> SortInput:
    """Create a multi-field sort input.

    Args:
        sort_fields: List of (field, direction) tuples

    Returns:
        SortInput instance
    """
    fields = [
        SortField(field=field, direction=direction) for field, direction in sort_fields
    ]
    return SortInput(fields=fields)


def get_sort_direction_from_string(direction_str: str) -> SortDirection:
    """Get sort direction from string.

    Args:
        direction_str: Direction string ("asc" or "desc")

    Returns:
        SortDirection enum value
    """
    if direction_str.lower() == "desc":
        return SortDirection.DESC
    return SortDirection.ASC


def validate_sort_fields(
    allowed_fields: list[str], sort_input: SortInput | None
) -> bool:
    """Validate sort fields against allowed fields.

    Args:
        allowed_fields: List of allowed field names
        sort_input: Sort input to validate

    Returns:
        True if all fields are allowed
    """
    if sort_input is None or not sort_input.fields:
        return True

    for sort_field in sort_input.fields:
        if sort_field.field not in allowed_fields:
            return False

    return True


def apply_sort_to_query(
    query: Query, sort_set: SortSet, sort_input: SortInput | None
) -> Query:
    """Apply sorting to query using sort set.

    Args:
        query: SQLAlchemy query
        sort_set: Sort set instance
        sort_input: Sort input

    Returns:
        Modified query
    """
    return sort_set.apply_sort(query, sort_input)
