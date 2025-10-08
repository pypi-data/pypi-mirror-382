"""
Pydantic schemas for EGRC Platform.

This module provides base Pydantic schemas and common schema patterns
used across all EGRC services for request/response validation.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base Pydantic schema with common configuration."""

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TenantSchema(BaseSchema):
    """Schema with tenant information."""

    tenant_id: str = Field(..., description="Tenant identifier")


class AuditSchema(BaseSchema):
    """Schema with audit fields."""

    created_by: str | None = Field(None, description="User who created the record")
    updated_by: str | None = Field(None, description="User who last updated the record")
    version: int = Field(1, description="Record version")


class SoftDeleteSchema(BaseSchema):
    """Schema with soft delete fields."""

    is_deleted: bool = Field(False, description="Soft delete flag")
    deleted_at: datetime | None = Field(None, description="Deletion timestamp")
    deleted_by: str | None = Field(None, description="User who deleted the record")


class PaginationSchema(BaseSchema):
    """Schema for pagination parameters."""

    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(50, ge=1, le=1000, description="Items per page")
    sort_by: str | None = Field(None, description="Sort field")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")
    search: str | None = Field(None, description="Search query")

    @field_validator("limit")
    def validate_limit(cls, v: int) -> int:
        """Validate limit value."""
        if v > 1000:
            raise ValueError("Limit cannot exceed 1000")
        return v


class PaginationMetaSchema(BaseSchema):
    """Schema for pagination metadata."""

    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total items")
    total_pages: int = Field(..., description="Total pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class PaginatedResponseSchema(BaseSchema, Generic[T]):
    """Schema for paginated responses."""

    data: list[T] = Field(..., description="Response data")
    meta: PaginationMetaSchema = Field(..., description="Pagination metadata")


class ResponseSchema(BaseSchema, Generic[T]):
    """Base response schema."""

    success: bool = Field(True, description="Success status")
    data: T | None = Field(None, description="Response data")
    message: str | None = Field(None, description="Response message")
    errors: list[str] | None = Field(None, description="Error messages")


class ErrorResponseSchema(BaseSchema):
    """Error response schema."""

    success: bool = Field(False, description="Success status")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class ValidationErrorSchema(BaseSchema):
    """Validation error schema."""

    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
    value: Any | None = Field(None, description="Invalid value")


class ValidationErrorResponseSchema(BaseSchema):
    """Validation error response schema."""

    success: bool = Field(False, description="Success status")
    message: str = Field("Validation error", description="Error message")
    errors: list[ValidationErrorSchema] = Field(..., description="Validation errors")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class HealthCheckSchema(BaseSchema):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Check timestamp"
    )
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")
    dependencies: dict[str, str] | None = Field(None, description="Dependency status")


class StatusSchema(BaseSchema):
    """Status schema."""

    status: str = Field(..., description="Status value")


class NameSchema(BaseSchema):
    """Schema with name and description."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: str | None = Field(None, description="Description")


class CodeSchema(BaseSchema):
    """Schema with code field."""

    code: str = Field(..., min_length=1, max_length=100, description="Code")


class ExternalIdSchema(BaseSchema):
    """Schema with external ID."""

    external_id: str | None = Field(
        None, max_length=255, description="External identifier"
    )


class MetadataSchema(BaseSchema):
    """Schema with metadata."""

    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class PrioritySchema(BaseSchema):
    """Schema with priority field."""

    priority: str = Field(
        "medium", pattern="^(low|medium|high|critical)$", description="Priority level"
    )


class CategorySchema(BaseSchema):
    """Schema with category field."""

    category: str | None = Field(None, max_length=100, description="Category")


class TagsSchema(BaseSchema):
    """Schema with tags field."""

    tags: list[str] | None = Field(None, description="Tags list")

    @field_validator("tags", pre=True)
    def parse_tags(cls, v: Any) -> list[str] | None:
        """Parse tags from various formats."""
        if v is None:
            return None

        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]

        if isinstance(v, list):
            return [str(tag).strip() for tag in v if str(tag).strip()]

        return None


class ExpirySchema(BaseSchema):
    """Schema with expiry fields."""

    effective_date: datetime | None = Field(None, description="Effective date")
    expiry_date: datetime | None = Field(None, description="Expiry date")

    @field_validator("expiry_date")
    def validate_expiry_date(
        cls, v: datetime | None, values: dict[str, Any]
    ) -> datetime | None:
        """Validate expiry date is after effective date."""
        if v and "effective_date" in values and values["effective_date"]:
            if v <= values["effective_date"]:
                raise ValueError("Expiry date must be after effective date")
        return v


class ApprovalSchema(BaseSchema):
    """Schema with approval fields."""

    is_approved: bool = Field(False, description="Approval status")
    approved_at: datetime | None = Field(None, description="Approval timestamp")
    approved_by: str | None = Field(None, description="User who approved")
    approval_notes: str | None = Field(None, description="Approval notes")


class FilterSchema(BaseSchema):
    """Schema for filtering parameters."""

    filters: dict[str, Any] | None = Field(None, description="Filter criteria")
    date_from: datetime | None = Field(None, description="Filter from date")
    date_to: datetime | None = Field(None, description="Filter to date")

    @field_validator("date_to")
    def validate_date_range(
        cls, v: datetime | None, values: dict[str, Any]
    ) -> datetime | None:
        """Validate date range."""
        if v and "date_from" in values and values["date_from"]:
            if v <= values["date_from"]:
                raise ValueError("Date to must be after date from")
        return v


class BulkOperationSchema(BaseSchema):
    """Schema for bulk operations."""

    ids: list[str] = Field(..., min_items=1, max_items=1000, description="Entity IDs")
    operation: str = Field(
        ...,
        pattern="^(delete|update|activate|deactivate)$",
        description="Operation type",
    )
    data: dict[str, Any] | None = Field(None, description="Operation data")


class BulkOperationResultSchema(BaseSchema):
    """Schema for bulk operation results."""

    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    errors: list[dict[str, Any]] | None = Field(None, description="Error details")


class FileUploadSchema(BaseSchema):
    """Schema for file upload."""

    filename: str = Field(..., description="File name")
    content_type: str = Field(..., description="File content type")
    size: int = Field(..., ge=1, description="File size in bytes")
    checksum: str | None = Field(None, description="File checksum")


class FileResponseSchema(BaseSchema):
    """Schema for file response."""

    id: str = Field(..., description="File ID")
    filename: str = Field(..., description="File name")
    content_type: str = Field(..., description="File content type")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="File URL")
    created_at: datetime = Field(..., description="Upload timestamp")


class NotificationSchema(BaseSchema):
    """Schema for notifications."""

    type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: str = Field(
        "medium", pattern="^(low|medium|high|urgent)$", description="Priority"
    )
    recipient: str = Field(..., description="Recipient identifier")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class EventSchema(BaseSchema):
    """Schema for events."""

    event_type: str = Field(..., description="Event type")
    entity_type: str = Field(..., description="Entity type")
    entity_id: str = Field(..., description="Entity ID")
    user_id: str | None = Field(None, description="User ID")
    tenant_id: str | None = Field(None, description="Tenant ID")
    data: dict[str, Any] | None = Field(None, description="Event data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )
