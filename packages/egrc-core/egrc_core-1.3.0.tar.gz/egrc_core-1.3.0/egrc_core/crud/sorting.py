"""
Sorting utilities for EGRC Platform.

This module provides sorting classes and utilities for handling
sorting parameters across all EGRC services.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..constants.constants import DatabaseConstants


class SortDirection(str, Enum):
    """Sort direction enumeration."""

    ASC = "asc"
    DESC = "desc"


class SortParams(BaseModel):
    """Parameters for sorting."""

    def __init__(self, **data: Any):
        """Initialize sort parameters from dictionary."""
        super().__init__(**data)

    def __setitem__(self, key: str, value: str | SortDirection) -> None:
        """Set a sort field and direction."""
        if isinstance(value, str):
            value = SortDirection(value.lower())
        setattr(self, key, value)

    def __getitem__(self, key: str) -> SortDirection:
        """Get sort direction for a field."""
        return getattr(self, key, SortDirection.ASC)

    def __contains__(self, key: str) -> bool:
        """Check if a field is in sort parameters."""
        return hasattr(self, key)

    def __iter__(self):
        """Iterate over sort parameters."""
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                yield key, value

    def items(self):
        """Get items as key-value pairs."""
        return [(key, value) for key, value in self.__iter__()]

    def keys(self):
        """Get field names."""
        return [key for key, _ in self.__iter__()]

    def values(self):
        """Get sort directions."""
        return [value for _, value in self.__iter__()]

    def get(
        self, key: str, default: SortDirection | None = None
    ) -> SortDirection | None:
        """Get sort direction for a field with default."""
        return getattr(self, key, default)

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {key: value.value for key, value in self.__iter__()}

    def to_list(self) -> list[dict[str, str]]:
        """Convert to list of field-direction pairs."""
        return [
            {"field": key, "direction": value.value} for key, value in self.__iter__()
        ]

    @classmethod
    def from_string(cls, sort_string: str) -> "SortParams":
        """
        Create SortParams from a string.

        Format: "field1:asc,field2:desc" or "field1,field2:desc"

        Args:
            sort_string: Sort string

        Returns:
            SortParams instance
        """
        params = cls()

        if not sort_string:
            return params

        for part in sort_string.split(","):
            part = part.strip()
            if ":" in part:
                field, direction = part.split(":", 1)
                field = field.strip()
                direction = direction.strip().lower()

                if direction not in ["asc", "desc"]:
                    raise ValueError(f"Invalid sort direction: {direction}")

                params[field] = SortDirection(direction)
            else:
                # Default to ascending
                params[part.strip()] = SortDirection.ASC

        return params

    @classmethod
    def from_dict(cls, sort_dict: dict[str, str | SortDirection]) -> "SortParams":
        """
        Create SortParams from a dictionary.

        Args:
            sort_dict: Dictionary of field-direction pairs

        Returns:
            SortParams instance
        """
        params = cls()

        for field, direction in sort_dict.items():
            if isinstance(direction, str):
                direction = SortDirection(direction.lower())
            params[field] = direction

        return params

    @classmethod
    def from_list(cls, sort_list: list[dict[str, str]]) -> "SortParams":
        """
        Create SortParams from a list of field-direction pairs.

        Args:
            sort_list: List of {"field": "name", "direction": "asc/desc"}

        Returns:
            SortParams instance
        """
        params = cls()

        for item in sort_list:
            field = item.get("field")
            direction = item.get("direction", "asc")

            if not field:
                continue

            if isinstance(direction, str):
                direction = SortDirection(direction.lower())

            params[field] = direction

        return params


class SortField(BaseModel):
    """Individual sort field configuration."""

    field: str = Field(description="Field name to sort by")
    direction: SortDirection = Field(
        default=SortDirection.ASC, description="Sort direction"
    )
    priority: int = Field(default=0, description="Sort priority (lower numbers first)")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field": self.field,
            "direction": self.direction.value,
            "priority": self.priority,
        }


class SortConfig(BaseModel):
    """Sort configuration with allowed fields and defaults."""

    allowed_fields: list[str] = Field(
        default_factory=list, description="Allowed sort fields"
    )
    default_field: str = Field(
        default=DatabaseConstants.DEFAULT_ORDER_BY, description="Default sort field"
    )
    default_direction: SortDirection = Field(
        default=SortDirection.DESC, description="Default sort direction"
    )
    max_fields: int = Field(default=5, description="Maximum number of sort fields")

    def validate_field(self, field: str) -> bool:
        """
        Validate if a field is allowed for sorting.

        Args:
            field: Field name to validate

        Returns:
            True if field is allowed
        """
        return field in self.allowed_fields

    def get_default_sort(self) -> SortParams:
        """
        Get default sort parameters.

        Returns:
            SortParams with default field and direction
        """
        return SortParams.from_dict({self.default_field: self.default_direction})

    def apply_defaults(self, sort_params: SortParams) -> SortParams:
        """
        Apply default sorting to sort parameters.

        Args:
            sort_params: Input sort parameters

        Returns:
            SortParams with defaults applied
        """
        if not sort_params:
            return self.get_default_sort()

        # If no fields specified, add default
        if not list(sort_params.keys()):
            sort_params[self.default_field] = self.default_direction

        return sort_params

    def validate_and_filter(self, sort_params: SortParams) -> SortParams:
        """
        Validate and filter sort parameters.

        Args:
            sort_params: Input sort parameters

        Returns:
            Validated and filtered SortParams
        """
        if not self.allowed_fields:
            return sort_params

        validated = SortParams()
        field_count = 0

        for field, direction in sort_params.items():
            if field_count >= self.max_fields:
                break

            if self.validate_field(field):
                validated[field] = direction
                field_count += 1

        return validated


def create_sort_params(
    sort_string: str | None = None,
    sort_dict: dict[str, str | SortDirection] | None = None,
    sort_list: list[dict[str, str]] | None = None,
) -> SortParams:
    """
    Create sort parameters from various input formats.

    Args:
        sort_string: Sort string (e.g., "field1:asc,field2:desc")
        sort_dict: Dictionary of field-direction pairs
        sort_list: List of field-direction dictionaries

    Returns:
        SortParams instance
    """
    if sort_string:
        return SortParams.from_string(sort_string)
    elif sort_dict:
        return SortParams.from_dict(sort_dict)
    elif sort_list:
        return SortParams.from_list(sort_list)
    else:
        return SortParams()


def apply_sorting_to_query(
    query: Any, sort_params: SortParams, model_class: Any
) -> Any:
    """
    Apply sorting to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        sort_params: Sort parameters
        model_class: SQLAlchemy model class

    Returns:
        Query with sorting applied
    """
    for field, direction in sort_params.items():
        if hasattr(model_class, field):
            column = getattr(model_class, field)
            if direction == SortDirection.DESC:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

    return query
