"""
Base schemas for EGRC Platform.

This module provides base Pydantic schemas and mixins that can be
used across all EGRC services.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.

    This schema provides common configuration and methods
    for all EGRC schemas.
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
    )

    def dict_exclude_none(self, **kwargs) -> dict[str, Any]:
        """
        Return dictionary representation excluding None values.

        Args:
            **kwargs: Additional arguments for dict()

        Returns:
            Dictionary with None values excluded
        """
        return self.model_dump(exclude_none=True, **kwargs)

    def dict_exclude_unset(self, **kwargs) -> dict[str, Any]:
        """
        Return dictionary representation excluding unset values.

        Args:
            **kwargs: Additional arguments for dict()

        Returns:
            Dictionary with unset values excluded
        """
        return self.model_dump(exclude_unset=True, **kwargs)


class TimestampMixin(BaseSchema):
    """
    Mixin for schemas that include timestamp fields.

    This mixin adds created_at and updated_at timestamp fields
    to schemas.
    """

    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        default=None, description="Last update timestamp"
    )


class IDMixin(BaseSchema):
    """
    Mixin for schemas that include ID field.

    This mixin adds an ID field to schemas.
    """

    id: UUID = Field(description="Unique identifier")


class SoftDeleteMixin(BaseSchema):
    """
    Mixin for schemas that support soft deletion.

    This mixin adds soft deletion fields to schemas.
    """

    is_deleted: bool = Field(default=False, description="Soft deletion flag")
    deleted_at: datetime | None = Field(default=None, description="Deletion timestamp")

    """
    Mixin for schemas that are tenant-specific.

    This mixin adds tenant_id field to schemas.
    """

    tenant_id: UUID = Field(description="Tenant identifier")


class UserMixin(BaseSchema):
    """
    Mixin for schemas that track user information.

    This mixin adds created_by and updated_by fields to schemas.
    """

    created_by: UUID | None = Field(
        default=None, description="User who created the record"
    )
    updated_by: UUID | None = Field(
        default=None, description="User who last updated the record"
    )


class VersionMixin(BaseSchema):
    """
    Mixin for schemas that support versioning.

    This mixin adds version field to schemas.
    """

    version: int = Field(default=1, description="Record version")


class MetadataMixin(BaseSchema):
    """
    Mixin for schemas that include metadata.

    This mixin adds metadata field to schemas.
    """

    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional metadata"
    )


class StatusMixin(BaseSchema):
    """
    Mixin for schemas that have status fields.

    This mixin adds status field to schemas.
    """

    status: str = Field(default="active", description="Record status")


class BaseResponseSchema(BaseSchema):
    """
    Base schema for API responses.

    This schema provides common fields for all API responses.
    """

    success: bool = Field(default=True, description="Response success status")
    message: str | None = Field(default=None, description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class BaseRequestSchema(BaseSchema):
    """
    Base schema for API requests.

    This schema provides common fields for all API requests.
    """

    request_id: str | None = Field(default=None, description="Request identifier")
    correlation_id: str | None = Field(
        default=None, description="Correlation identifier"
    )


class PaginationMixin(BaseSchema):
    """
    Mixin for schemas that support pagination.

    This mixin adds pagination fields to schemas.
    """

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Number of items per page"
    )


class SortMixin(BaseSchema):
    """
    Mixin for schemas that support sorting.

    This mixin adds sorting fields to schemas.
    """

    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", description="Sort order (asc or desc)")


class FilterMixin(BaseSchema):
    """
    Mixin for schemas that support filtering.

    This mixin adds filtering fields to schemas.
    """

    filters: dict[str, Any] | None = Field(
        default_factory=dict, description="Filter criteria"
    )
    search: str | None = Field(default=None, description="Search query")


class AuditMixin(BaseSchema):
    """
    Mixin for schemas that support audit logging.

    This mixin adds audit fields to schemas.
    """

    audit_id: str | None = Field(default=None, description="Audit identifier")
    audit_action: str | None = Field(default=None, description="Audit action")
    audit_timestamp: datetime | None = Field(
        default=None, description="Audit timestamp"
    )


class ValidationMixin(BaseSchema):
    """
    Mixin for schemas that support validation.

    This mixin adds validation fields to schemas.
    """

    is_valid: bool = Field(default=True, description="Validation status")
    validation_errors: dict[str, Any] | None = Field(
        default_factory=dict, description="Validation errors"
    )
    validated_at: datetime | None = Field(
        default=None, description="Validation timestamp"
    )
