"""
Audit models for EGRC Platform.

This module defines comprehensive audit tables and models for tracking
all changes and activities across the EGRC platform.
"""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.declarative import Base


class AuditAction(PyEnum):
    """Enumeration of audit actions."""

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


class AuditSeverity(PyEnum):
    """Enumeration of audit severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditStatus(PyEnum):
    """Enumeration of audit entry status."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


class AuditLog(Base):
    """
    Main audit log table for tracking all system activities.

    This table stores comprehensive audit information for all entities
    and actions across the EGRC platform.
    """

    __tablename__ = "audit_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Entity information
    entity_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the entity being audited",
    )
    entity_id = Column(
        String(100),
        nullable=False,
        index=True,
        comment="ID of the entity being audited",
    )
    entity_type = Column(
        String(50), nullable=True, index=True, comment="Type/category of the entity"
    )

    # Action information
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed (CREATE, UPDATE, DELETE, etc.)",
    )
    action_category = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Category of the action (CRUD, AUTH, etc.)",
    )

    # User and session information
    user_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="ID of the user who performed the action",
    )
    user_name = Column(
        String(200), nullable=True, comment="Name of the user who performed the action"
    )
    user_email = Column(
        String(255), nullable=True, comment="Email of the user who performed the action"
    )
    session_id = Column(
        String(100), nullable=True, index=True, comment="Session ID of the user"
    )

    # Request information
    request_id = Column(
        String(100), nullable=True, index=True, comment="Unique request ID for tracing"
    )
    correlation_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Correlation ID for related operations",
    )

    # Change details
    old_values = Column(
        JSONB, nullable=True, comment="Previous values before the change"
    )
    new_values = Column(JSONB, nullable=True, comment="New values after the change")
    changed_fields = Column(
        JSONB, nullable=True, comment="List of fields that were changed"
    )
    change_summary = Column(
        Text, nullable=True, comment="Human-readable summary of changes"
    )

    # Context information
    tenant_id = Column(
        String(100), nullable=True, index=True, comment="Tenant ID for multi-tenancy"
    )
    organization_id = Column(
        String(100), nullable=True, index=True, comment="Organization ID"
    )
    department_id = Column(
        String(100), nullable=True, index=True, comment="Department ID"
    )

    # Technical details
    ip_address = Column(String(45), nullable=True, comment="IP address of the client")
    user_agent = Column(Text, nullable=True, comment="User agent string")
    endpoint = Column(String(500), nullable=True, comment="API endpoint accessed")
    method = Column(String(10), nullable=True, comment="HTTP method used")

    # Audit metadata
    severity = Column(
        String(20),
        nullable=False,
        default=AuditSeverity.LOW.value,
        comment="Severity level of the audit event",
    )
    status = Column(
        String(20),
        nullable=False,
        default=AuditStatus.SUCCESS.value,
        comment="Status of the operation",
    )
    error_message = Column(
        Text, nullable=True, comment="Error message if operation failed"
    )
    error_code = Column(
        String(50), nullable=True, comment="Error code if operation failed"
    )

    # Performance metrics
    execution_time_ms = Column(
        Integer, nullable=True, comment="Execution time in milliseconds"
    )
    memory_usage_mb = Column(Integer, nullable=True, comment="Memory usage in MB")

    # Additional metadata
    tags = Column(JSONB, nullable=True, comment="Additional tags for categorization")
    audit_metadata = Column(JSONB, nullable=True, comment="Additional metadata")
    custom_fields = Column(
        JSONB, nullable=True, comment="Custom fields specific to the entity"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    audit_details = relationship(
        "AuditDetail", back_populates="audit_log", cascade="all, delete-orphan"
    )
    audit_attachments = relationship(
        "AuditAttachment", back_populates="audit_log", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_audit_logs_entity", "entity_name", "entity_id"),
        Index("idx_audit_logs_user_action", "user_id", "action"),
        Index("idx_audit_logs_tenant_created", "tenant_id", "created_at"),
        Index("idx_audit_logs_action_created", "action", "created_at"),
        Index("idx_audit_logs_severity_status", "severity", "status"),
        Index("idx_audit_logs_correlation", "correlation_id"),
        Index("idx_audit_logs_session", "session_id"),
        Index("idx_audit_logs_request", "request_id"),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_audit_logs_severity",
        ),
        CheckConstraint(
            "status IN ('SUCCESS', 'FAILED', 'PARTIAL', 'PENDING')",
            name="ck_audit_logs_status",
        ),
    )

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, entity={self.entity_name}:"
            f"{self.entity_id}, action={self.action}, user={self.user_id})>"
        )


class AuditDetail(Base):
    """
    Detailed audit information for complex operations.

    This table stores additional details for audit entries that require
    more granular tracking or complex data structures.
    """

    __tablename__ = "audit_details"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to audit log
    audit_log_id = Column(
        UUID(as_uuid=True),
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Detail information
    detail_type = Column(
        String(50),
        nullable=False,
        comment="Type of detail (FIELD_CHANGE, VALIDATION_ERROR, etc.)",
    )
    detail_key = Column(String(100), nullable=True, comment="Key or field name")
    detail_value = Column(JSONB, nullable=True, comment="Detail value")
    detail_description = Column(
        Text, nullable=True, comment="Human-readable description"
    )

    # Ordering
    sequence = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Sequence number for ordering details",
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationships
    audit_log = relationship("AuditLog", back_populates="audit_details")

    # Indexes
    __table_args__ = (
        Index("idx_audit_details_log_type", "audit_log_id", "detail_type"),
        Index("idx_audit_details_sequence", "audit_log_id", "sequence"),
    )

    def __repr__(self):
        return (
            f"<AuditDetail(id={self.id}, audit_log_id={self.audit_log_id}, "
            f"type={self.detail_type})>"
        )


class AuditAttachment(Base):
    """
    File attachments for audit entries.

    This table stores references to files attached to audit entries,
    such as exported data, uploaded files, or generated reports.
    """

    __tablename__ = "audit_attachments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to audit log
    audit_log_id = Column(
        UUID(as_uuid=True),
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File information
    file_name = Column(String(255), nullable=False, comment="Original file name")
    file_path = Column(String(500), nullable=False, comment="Path to the stored file")
    file_size = Column(Integer, nullable=True, comment="File size in bytes")
    file_type = Column(String(100), nullable=True, comment="MIME type of the file")
    file_hash = Column(String(64), nullable=True, comment="SHA-256 hash of the file")

    # Attachment metadata
    attachment_type = Column(
        String(50),
        nullable=False,
        comment="Type of attachment (EXPORT, IMPORT, REPORT, etc.)",
    )
    description = Column(Text, nullable=True, comment="Description of the attachment")

    # Security
    is_encrypted = Column(
        Boolean, nullable=False, default=False, comment="Whether the file is encrypted"
    )
    encryption_key_id = Column(
        String(100), nullable=True, comment="ID of the encryption key used"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Expiration date for the attachment",
    )

    # Relationships
    audit_log = relationship("AuditLog", back_populates="audit_attachments")

    # Indexes
    __table_args__ = (
        Index("idx_audit_attachments_log_type", "audit_log_id", "attachment_type"),
        Index("idx_audit_attachments_expires", "expires_at"),
        Index("idx_audit_attachments_hash", "file_hash"),
    )

    def __repr__(self):
        return (
            f"<AuditAttachment(id={self.id}, audit_log_id={self.audit_log_id}, "
            f"file={self.file_name})>"
        )


class AuditConfiguration(Base):
    """
    Configuration for audit logging behavior.

    This table stores configuration settings that control how audit
    logging behaves for different entities and actions.
    """

    __tablename__ = "audit_configurations"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Configuration scope
    entity_name = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Entity name (null for global config)",
    )
    action = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Action name (null for all actions)",
    )
    tenant_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Tenant ID (null for global config)",
    )

    # Configuration settings
    is_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether audit logging is enabled",
    )
    log_level = Column(
        String(20),
        nullable=False,
        default="INFO",
        comment="Log level for this configuration",
    )
    capture_old_values = Column(
        Boolean, nullable=False, default=True, comment="Whether to capture old values"
    )
    capture_new_values = Column(
        Boolean, nullable=False, default=True, comment="Whether to capture new values"
    )
    capture_metadata = Column(
        Boolean, nullable=False, default=True, comment="Whether to capture metadata"
    )

    # Filtering
    excluded_fields = Column(
        JSONB, nullable=True, comment="Fields to exclude from audit logging"
    )
    included_fields = Column(
        JSONB,
        nullable=True,
        comment="Fields to include in audit logging (null for all)",
    )
    field_masks = Column(
        JSONB, nullable=True, comment="Fields to mask in audit logging"
    )

    # Retention
    retention_days = Column(
        Integer, nullable=True, comment="Number of days to retain audit logs"
    )
    archive_after_days = Column(
        Integer, nullable=True, comment="Number of days after which to archive"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
    created_by = Column(
        String(100), nullable=True, comment="User who created this configuration"
    )
    updated_by = Column(
        String(100), nullable=True, comment="User who last updated this configuration"
    )

    # Indexes
    __table_args__ = (
        Index("idx_audit_config_entity_action", "entity_name", "action"),
        Index("idx_audit_config_tenant", "tenant_id"),
        UniqueConstraint(
            "entity_name",
            "action",
            "tenant_id",
            name="uq_audit_config_entity_action_tenant",
        ),
    )

    def __repr__(self):
        return (
            f"<AuditConfiguration(id={self.id}, entity={self.entity_name}, "
            f"action={self.action}, enabled={self.is_enabled})>"
        )


class AuditRetentionPolicy(Base):
    """
    Retention policies for audit data.

    This table defines how long different types of audit data
    should be retained and when it should be archived or deleted.
    """

    __tablename__ = "audit_retention_policies"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Policy scope
    policy_name = Column(
        String(100), nullable=False, unique=True, comment="Name of the retention policy"
    )
    entity_name = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Entity name (null for all entities)",
    )
    action = Column(
        String(50), nullable=True, index=True, comment="Action (null for all actions)"
    )
    severity = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Severity level (null for all levels)",
    )
    tenant_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Tenant ID (null for all tenants)",
    )

    # Retention settings
    retention_days = Column(
        Integer, nullable=False, comment="Number of days to retain data"
    )
    archive_after_days = Column(
        Integer, nullable=True, comment="Number of days after which to archive"
    )
    delete_after_days = Column(
        Integer, nullable=True, comment="Number of days after which to delete"
    )

    # Archive settings
    archive_location = Column(
        String(500), nullable=True, comment="Location where archived data is stored"
    )
    archive_format = Column(
        String(20), nullable=True, default="JSON", comment="Format for archived data"
    )
    compression_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether to compress archived data",
    )

    # Policy status
    is_active = Column(
        Boolean, nullable=False, default=True, comment="Whether the policy is active"
    )
    last_executed = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the policy was last executed",
    )
    next_execution = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the policy should next execute",
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
    created_by = Column(
        String(100), nullable=True, comment="User who created this policy"
    )

    # Indexes
    __table_args__ = (
        Index("idx_audit_retention_entity", "entity_name"),
        Index("idx_audit_retention_action", "action"),
        Index("idx_audit_retention_severity", "severity"),
        Index("idx_audit_retention_tenant", "tenant_id"),
        Index("idx_audit_retention_next_execution", "next_execution"),
        CheckConstraint("retention_days > 0", name="ck_audit_retention_days_positive"),
    )

    def __repr__(self):
        return (
            f"<AuditRetentionPolicy(id={self.id}, name={self.policy_name}, "
            f"retention_days={self.retention_days})>"
        )


class AuditEvent(Base):
    """
    Event-driven audit entries for asynchronous processing.

    This table stores audit events that are processed asynchronously
    to improve performance and handle high-volume audit logging.
    """

    __tablename__ = "audit_events"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Event information
    event_type = Column(
        String(50), nullable=False, index=True, comment="Type of audit event"
    )
    event_data = Column(JSONB, nullable=False, comment="Event data payload")
    event_metadata = Column(JSONB, nullable=True, comment="Event metadata")

    # Processing status
    status = Column(
        String(20),
        nullable=False,
        default="PENDING",
        index=True,
        comment="Processing status",
    )
    priority = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Processing priority (1=highest, 10=lowest)",
    )
    retry_count = Column(
        Integer, nullable=False, default=0, comment="Number of retry attempts"
    )
    max_retries = Column(
        Integer, nullable=False, default=3, comment="Maximum number of retries"
    )

    # Processing timestamps
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    processed_at = Column(
        DateTime(timezone=True), nullable=True, comment="When the event was processed"
    )
    failed_at = Column(
        DateTime(timezone=True), nullable=True, comment="When the event failed"
    )
    next_retry_at = Column(
        DateTime(timezone=True), nullable=True, comment="When to retry processing"
    )

    # Error information
    error_message = Column(
        Text, nullable=True, comment="Error message if processing failed"
    )
    error_details = Column(JSONB, nullable=True, comment="Detailed error information")

    # Indexes
    __table_args__ = (
        Index("idx_audit_events_status_priority", "status", "priority"),
        Index("idx_audit_events_retry", "next_retry_at"),
        Index("idx_audit_events_created", "created_at"),
        CheckConstraint(
            "status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'RETRY')",
            name="ck_audit_events_status",
        ),
        CheckConstraint(
            "priority >= 1 AND priority <= 10", name="ck_audit_events_priority"
        ),
    )

    def __repr__(self):
        return (
            f"<AuditEvent(id={self.id}, type={self.event_type}, status={self.status})>"
        )
