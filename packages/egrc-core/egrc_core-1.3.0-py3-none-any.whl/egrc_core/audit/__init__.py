"""
Audit module for EGRC Platform.

This module provides comprehensive audit logging capabilities including:
- Generic audit tables with comprehensive columns
- SQLAlchemy models for audit data
- REST APIs for audit operations
- Event-driven asynchronous audit logging
- Pydantic schemas for data validation
- Middleware for automatic request/response logging
- ORM hooks for database operation tracking
"""

from .api import router as audit_router
from .middleware import (
    AuditMiddleware,
    DatabaseAuditHook,
    EventAuditLogger,
    log_application_event,
    log_business_event,
    log_security_event,
    register_model_for_audit,
    setup_audit_middleware,
)
from .models import (
    AuditAction,
    AuditAttachment,
    AuditConfiguration,
    AuditDetail,
    AuditEvent,
    AuditLog,
    AuditRetentionPolicy,
    AuditSeverity,
    AuditStatus,
)
from .processor import (
    EventPriority,
    EventProcessor,
    EventStatus,
    ProcessingResult,
    get_processor_stats,
    get_queue_status,
    start_event_processor,
    stop_event_processor,
    submit_audit_event,
)
from .schemas import (
    AuditAlertResponseSchema,
    AuditAlertSchema,
    AuditAttachmentCreateSchema,
    AuditAttachmentResponseSchema,
    AuditBulkCreateSchema,
    AuditBulkResponseSchema,
    AuditConfigurationCreateSchema,
    AuditConfigurationResponseSchema,
    AuditConfigurationUpdateSchema,
    AuditCreateSchema,
    AuditDetailCreateSchema,
    AuditDetailResponseSchema,
    AuditEventCreateSchema,
    AuditEventResponseSchema,
    AuditExportSchema,
    AuditQuerySchema,
    AuditResponseSchema,
    AuditRetentionPolicyCreateSchema,
    AuditRetentionPolicyResponseSchema,
    AuditRetentionPolicyUpdateSchema,
    AuditSearchSchema,
    AuditStatsSchema,
    AuditUpdateSchema,
    AuditValidationSchema,
)
from .service import AuditContext, AuditService, audit_hook, log_audit, log_audit_event


__all__ = [
    # Models
    "AuditLog",
    "AuditDetail",
    "AuditAttachment",
    "AuditConfiguration",
    "AuditRetentionPolicy",
    "AuditEvent",
    "AuditAction",
    "AuditSeverity",
    "AuditStatus",
    # Schemas
    "AuditCreateSchema",
    "AuditUpdateSchema",
    "AuditResponseSchema",
    "AuditDetailCreateSchema",
    "AuditDetailResponseSchema",
    "AuditAttachmentCreateSchema",
    "AuditAttachmentResponseSchema",
    "AuditConfigurationCreateSchema",
    "AuditConfigurationUpdateSchema",
    "AuditConfigurationResponseSchema",
    "AuditRetentionPolicyCreateSchema",
    "AuditRetentionPolicyUpdateSchema",
    "AuditRetentionPolicyResponseSchema",
    "AuditEventCreateSchema",
    "AuditEventResponseSchema",
    "AuditQuerySchema",
    "AuditStatsSchema",
    "AuditSearchSchema",
    "AuditBulkCreateSchema",
    "AuditBulkResponseSchema",
    "AuditExportSchema",
    "AuditValidationSchema",
    "AuditAlertSchema",
    "AuditAlertResponseSchema",
    # Service
    "AuditService",
    "audit_hook",
    "AuditContext",
    "log_audit",
    "log_audit_event",
    # API
    "audit_router",
    # Middleware
    "AuditMiddleware",
    "DatabaseAuditHook",
    "EventAuditLogger",
    "setup_audit_middleware",
    "register_model_for_audit",
    "log_application_event",
    "log_business_event",
    "log_security_event",
    # Processor
    "EventProcessor",
    "EventStatus",
    "EventPriority",
    "ProcessingResult",
    "start_event_processor",
    "stop_event_processor",
    "submit_audit_event",
    "get_processor_stats",
    "get_queue_status",
]
