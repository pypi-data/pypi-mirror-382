"""
Pydantic schemas for audit system.

This module defines Pydantic schemas for audit data validation,
serialization, and API request/response handling.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class AuditActionEnum(str, Enum):
    """Enumeration of audit actions for Pydantic."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SOFT_DELETE = "SOFT_DELETE"
    RESTORE = "RESTORE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
    PERMISSION_GRANT = "PERMISSION_GRANT"
    PERMISSION_REVOKE = "PERMISSION_REVOKE"
    ROLE_ASSIGN = "ROLE_ASSIGN"
    ROLE_UNASSIGN = "ROLE_UNASSIGN"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SUBMIT = "SUBMIT"
    PUBLISH = "PUBLISH"
    ARCHIVE = "ARCHIVE"
    UNARCHIVE = "UNARCHIVE"
    CUSTOM = "CUSTOM"


class AuditSeverityEnum(str, Enum):
    """Enumeration of audit severity levels for Pydantic."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditStatusEnum(str, Enum):
    """Enumeration of audit status for Pydantic."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


# Base schemas
class AuditBaseSchema(BaseModel):
    """Base schema for audit data."""

    entity_name: str = Field(
        ..., max_length=100, description="Name of the entity being audited"
    )
    entity_id: str = Field(
        ..., max_length=100, description="ID of the entity being audited"
    )
    entity_type: str | None = Field(
        None, max_length=50, description="Type/category of the entity"
    )
    action: AuditActionEnum = Field(..., description="Action performed")
    action_category: str | None = Field(
        None, max_length=50, description="Category of the action"
    )

    # User information
    user_id: str | None = Field(
        None, max_length=100, description="ID of the user who performed the action"
    )
    user_name: str | None = Field(None, max_length=200, description="Name of the user")
    user_email: str | None = Field(
        None, max_length=255, description="Email of the user"
    )
    session_id: str | None = Field(None, max_length=100, description="Session ID")

    # Request information
    request_id: str | None = Field(
        None, max_length=100, description="Unique request ID"
    )
    correlation_id: str | None = Field(
        None, max_length=100, description="Correlation ID"
    )

    # Change details
    old_values: dict[str, Any] | None = Field(None, description="Previous values")
    new_values: dict[str, Any] | None = Field(None, description="New values")
    changed_fields: list[str] | None = Field(None, description="List of changed fields")
    change_summary: str | None = Field(None, description="Summary of changes")

    # Context
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID")
    organization_id: str | None = Field(
        None, max_length=100, description="Organization ID"
    )
    department_id: str | None = Field(None, max_length=100, description="Department ID")

    # Technical details
    ip_address: str | None = Field(None, max_length=45, description="IP address")
    user_agent: str | None = Field(None, description="User agent string")
    endpoint: str | None = Field(None, max_length=500, description="API endpoint")
    method: str | None = Field(None, max_length=10, description="HTTP method")

    # Audit metadata
    severity: AuditSeverityEnum = Field(
        AuditSeverityEnum.LOW, description="Severity level"
    )
    status: AuditStatusEnum = Field(
        AuditStatusEnum.SUCCESS, description="Operation status"
    )
    error_message: str | None = Field(None, description="Error message")
    error_code: str | None = Field(None, max_length=50, description="Error code")

    # Performance metrics
    execution_time_ms: int | None = Field(
        None, ge=0, description="Execution time in milliseconds"
    )
    memory_usage_mb: int | None = Field(None, ge=0, description="Memory usage in MB")

    # Additional metadata
    tags: dict[str, Any] | None = Field(None, description="Additional tags")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    custom_fields: dict[str, Any] | None = Field(None, description="Custom fields")


class AuditCreateSchema(AuditBaseSchema):
    """Schema for creating audit entries."""


class AuditUpdateSchema(BaseModel):
    """Schema for updating audit entries."""

    status: AuditStatusEnum | None = None
    error_message: str | None = None
    error_code: str | None = None
    execution_time_ms: int | None = Field(None, ge=0)
    memory_usage_mb: int | None = Field(None, ge=0)
    metadata: dict[str, Any] | None = None


class AuditResponseSchema(AuditBaseSchema):
    """Schema for audit entry responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditDetailCreateSchema(BaseModel):
    """Schema for creating audit details."""

    detail_type: str = Field(..., max_length=50, description="Type of detail")
    detail_key: str | None = Field(
        None, max_length=100, description="Key or field name"
    )
    detail_value: dict[str, Any] | None = Field(None, description="Detail value")
    detail_description: str | None = Field(None, description="Description")
    sequence: int = Field(0, ge=0, description="Sequence number")


class AuditDetailResponseSchema(AuditDetailCreateSchema):
    """Schema for audit detail responses."""

    id: UUID
    audit_log_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AuditAttachmentCreateSchema(BaseModel):
    """Schema for creating audit attachments."""

    file_name: str = Field(..., max_length=255, description="File name")
    file_path: str = Field(..., max_length=500, description="File path")
    file_size: int | None = Field(None, ge=0, description="File size in bytes")
    file_type: str | None = Field(None, max_length=100, description="MIME type")
    file_hash: str | None = Field(None, max_length=64, description="File hash")
    attachment_type: str = Field(..., max_length=50, description="Type of attachment")
    description: str | None = Field(None, description="Description")
    is_encrypted: bool = Field(False, description="Whether file is encrypted")
    encryption_key_id: str | None = Field(
        None, max_length=100, description="Encryption key ID"
    )
    expires_at: datetime | None = Field(None, description="Expiration date")


class AuditAttachmentResponseSchema(AuditAttachmentCreateSchema):
    """Schema for audit attachment responses."""

    id: UUID
    audit_log_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AuditConfigurationCreateSchema(BaseModel):
    """Schema for creating audit configurations."""

    entity_name: str | None = Field(None, max_length=100, description="Entity name")
    action: str | None = Field(None, max_length=50, description="Action name")
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID")
    is_enabled: bool = Field(True, description="Whether audit logging is enabled")
    log_level: str = Field("INFO", max_length=20, description="Log level")
    capture_old_values: bool = Field(True, description="Whether to capture old values")
    capture_new_values: bool = Field(True, description="Whether to capture new values")
    capture_metadata: bool = Field(True, description="Whether to capture metadata")
    excluded_fields: list[str] | None = Field(None, description="Fields to exclude")
    included_fields: list[str] | None = Field(None, description="Fields to include")
    field_masks: dict[str, str] | None = Field(None, description="Fields to mask")
    retention_days: int | None = Field(
        None, ge=1, description="Retention period in days"
    )
    archive_after_days: int | None = Field(None, ge=1, description="Archive after days")


class AuditConfigurationUpdateSchema(BaseModel):
    """Schema for updating audit configurations."""

    is_enabled: bool | None = None
    log_level: str | None = Field(None, max_length=20)
    capture_old_values: bool | None = None
    capture_new_values: bool | None = None
    capture_metadata: bool | None = None
    excluded_fields: list[str] | None = None
    included_fields: list[str] | None = None
    field_masks: dict[str, str] | None = None
    retention_days: int | None = Field(None, ge=1)
    archive_after_days: int | None = Field(None, ge=1)


class AuditConfigurationResponseSchema(AuditConfigurationCreateSchema):
    """Schema for audit configuration responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        from_attributes = True


class AuditRetentionPolicyCreateSchema(BaseModel):
    """Schema for creating audit retention policies."""

    policy_name: str = Field(..., max_length=100, description="Policy name")
    entity_name: str | None = Field(None, max_length=100, description="Entity name")
    action: str | None = Field(None, max_length=50, description="Action")
    severity: AuditSeverityEnum | None = Field(None, description="Severity level")
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID")
    retention_days: int = Field(..., ge=1, description="Retention period in days")
    archive_after_days: int | None = Field(None, ge=1, description="Archive after days")
    delete_after_days: int | None = Field(None, ge=1, description="Delete after days")
    archive_location: str | None = Field(
        None, max_length=500, description="Archive location"
    )
    archive_format: str = Field("JSON", max_length=20, description="Archive format")
    compression_enabled: bool = Field(True, description="Whether to compress archives")
    is_active: bool = Field(True, description="Whether policy is active")


class AuditRetentionPolicyUpdateSchema(BaseModel):
    """Schema for updating audit retention policies."""

    policy_name: str | None = Field(None, max_length=100)
    retention_days: int | None = Field(None, ge=1)
    archive_after_days: int | None = Field(None, ge=1)
    delete_after_days: int | None = Field(None, ge=1)
    archive_location: str | None = Field(None, max_length=500)
    archive_format: str | None = Field(None, max_length=20)
    compression_enabled: bool | None = None
    is_active: bool | None = None


class AuditRetentionPolicyResponseSchema(AuditRetentionPolicyCreateSchema):
    """Schema for audit retention policy responses."""

    id: UUID
    last_executed: datetime | None = None
    next_execution: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None

    class Config:
        from_attributes = True


class AuditEventCreateSchema(BaseModel):
    """Schema for creating audit events."""

    event_type: str = Field(..., max_length=50, description="Event type")
    event_data: dict[str, Any] = Field(..., description="Event data")
    event_metadata: dict[str, Any] | None = Field(None, description="Event metadata")
    priority: int = Field(5, ge=1, le=10, description="Processing priority")
    max_retries: int = Field(3, ge=0, description="Maximum retries")


class AuditEventResponseSchema(AuditEventCreateSchema):
    """Schema for audit event responses."""

    id: UUID
    status: str
    retry_count: int
    created_at: datetime
    processed_at: datetime | None = None
    failed_at: datetime | None = None
    next_retry_at: datetime | None = None
    error_message: str | None = None
    error_details: dict[str, Any] | None = None

    class Config:
        from_attributes = True


# Query and filter schemas
class AuditQuerySchema(BaseModel):
    """Schema for audit query parameters."""

    entity_name: str | None = None
    entity_id: str | None = None
    entity_type: str | None = None
    action: AuditActionEnum | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    severity: AuditSeverityEnum | None = None
    status: AuditStatusEnum | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    correlation_id: str | None = None
    request_id: str | None = None
    session_id: str | None = None
    tags: dict[str, Any] | None = None

    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class AuditStatsSchema(BaseModel):
    """Schema for audit statistics."""

    total_audits: int
    audits_by_action: dict[str, int]
    audits_by_entity: dict[str, int]
    audits_by_user: dict[str, int]
    audits_by_severity: dict[str, int]
    audits_by_status: dict[str, int]
    audits_by_tenant: dict[str, int]
    audits_by_hour: dict[str, int]
    audits_by_day: dict[str, int]
    average_execution_time: float | None = None
    error_rate: float | None = None


class AuditExportSchema(BaseModel):
    """Schema for audit data export."""

    format: str = Field(
        "json", pattern="^(json|csv|xlsx)$", description="Export format"
    )
    entity_name: str | None = None
    action: AuditActionEnum | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    include_details: bool = Field(False, description="Include audit details")
    include_attachments: bool = Field(False, description="Include attachments")
    fields: list[str] | None = Field(None, description="Specific fields to export")
    filters: dict[str, Any] | None = Field(None, description="Additional filters")


class AuditBulkCreateSchema(BaseModel):
    """Schema for bulk audit creation."""

    audits: list[AuditCreateSchema] = Field(
        ..., min_items=1, max_items=1000, description="List of audits to create"
    )
    batch_id: str | None = Field(None, max_length=100, description="Batch identifier")
    correlation_id: str | None = Field(
        None, max_length=100, description="Correlation ID for the batch"
    )


class AuditBulkResponseSchema(BaseModel):
    """Schema for bulk audit response."""

    batch_id: str | None = None
    correlation_id: str | None = None
    total_created: int
    total_failed: int
    created_ids: list[UUID]
    failed_audits: list[dict[str, Any]]
    processing_time_ms: int


# Validation schemas
class AuditValidationSchema(BaseModel):
    """Schema for audit data validation."""

    entity_name: str = Field(..., min_length=1, max_length=100)
    entity_id: str = Field(..., min_length=1, max_length=100)
    action: AuditActionEnum

    @field_validator("entity_name")
    @classmethod
    def validate_entity_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Entity name cannot be empty")
        return v.strip()

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Entity ID cannot be empty")
        return v.strip()

    @model_validator(mode="before")
    def validate_change_data(cls, values):
        old_values = values.get("old_values")
        new_values = values.get("new_values")
        changed_fields = values.get("changed_fields")

        # If we have change data, validate consistency
        if old_values or new_values:
            if not changed_fields:
                # Auto-generate changed fields if not provided
                if old_values and new_values:
                    changed_fields = list(
                        set(old_values.keys()) | set(new_values.keys())
                    )
                    values["changed_fields"] = changed_fields

        return values


class AuditSearchSchema(BaseModel):
    """Schema for audit search."""

    query: str | None = Field(None, description="Search query")
    entity_name: str | None = None
    action: AuditActionEnum | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    severity: AuditSeverityEnum | None = None
    status: AuditStatusEnum | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    tags: dict[str, Any] | None = None

    # Search options
    search_fields: list[str] | None = Field(None, description="Fields to search in")
    fuzzy_search: bool = Field(False, description="Enable fuzzy search")
    case_sensitive: bool = Field(False, description="Case sensitive search")

    # Pagination
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

    # Sorting
    sort_by: str = Field("created_at")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class AuditAlertSchema(BaseModel):
    """Schema for audit alerts."""

    alert_name: str = Field(..., max_length=100, description="Alert name")
    description: str | None = Field(None, description="Alert description")
    conditions: dict[str, Any] = Field(..., description="Alert conditions")
    severity: AuditSeverityEnum = Field(
        AuditSeverityEnum.MEDIUM, description="Alert severity"
    )
    is_enabled: bool = Field(True, description="Whether alert is enabled")
    notification_channels: list[str] | None = Field(
        None, description="Notification channels"
    )
    cooldown_minutes: int = Field(60, ge=0, description="Cooldown period in minutes")
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID")


class AuditAlertResponseSchema(AuditAlertSchema):
    """Schema for audit alert responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    last_triggered: datetime | None = None
    trigger_count: int = 0

    class Config:
        from_attributes = True
