"""
Audit Logging System for EGRC Platform.

This module provides comprehensive audit logging for all access decisions,
authentication events, and authorization checks with structured logging
and integration with the EGRC audit system.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from ..audit.models import AuditLog
from ..database import get_async_session
from .exceptions import AuditError


logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""

    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_SUCCESS = "authorization_success"
    AUTHORIZATION_FAILURE = "authorization_failure"
    PERMISSION_CHECK = "permission_check"
    ROLE_CHECK = "role_check"
    TENANT_ACCESS = "tenant_access"
    RESOURCE_ACCESS = "resource_access"
    TOKEN_REVOCATION = "token_revocation"
    ABAC_RULE_EVALUATION = "abac_rule_evaluation"


class AuditSeverity(Enum):
    """Audit event severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditContext:
    """
    Context information for audit events.
    """

    user_id: str
    username: str
    tenant_id: str
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    additional_context: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}


@dataclass
class AuditEvent:
    """
    Structured audit event for security operations.
    """

    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    context: AuditContext
    action: str
    resource: str
    result: str  # "allowed", "denied", "error"
    reason: Optional[str] = None
    details: Dict[str, Any] = None
    risk_score: Optional[float] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class AccessAuditLogger:
    """
    Comprehensive audit logger for access decisions and security events.
    """

    def __init__(
        self, enable_database_logging: bool = True, enable_console_logging: bool = True
    ):
        """
        Initialize audit logger.

        Args:
            enable_database_logging: Whether to log to database
            enable_console_logging: Whether to log to console
        """
        self.enable_database_logging = enable_database_logging
        self.enable_console_logging = enable_console_logging
        self.console_logger = logging.getLogger("security_audit")

    async def log_authentication_success(
        self,
        context: AuditContext,
        token_info: Dict[str, Any],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log successful authentication.

        Args:
            context: Audit context
            token_info: JWT token information
            details: Additional details
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.AUTHENTICATION_SUCCESS,
            severity=AuditSeverity.LOW,
            timestamp=datetime.utcnow(),
            context=context,
            action="authenticate",
            resource="system",
            result="allowed",
            details=details or {},
        )

        await self._log_event(event)

    async def log_authentication_failure(
        self,
        context: AuditContext,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log failed authentication.

        Args:
            context: Audit context
            reason: Failure reason
            details: Additional details
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.AUTHENTICATION_FAILURE,
            severity=AuditSeverity.MEDIUM,
            timestamp=datetime.utcnow(),
            context=context,
            action="authenticate",
            resource="system",
            result="denied",
            reason=reason,
            details=details or {},
            risk_score=self._calculate_auth_failure_risk(context),
        )

        await self._log_event(event)

    async def log_authorization_success(
        self,
        context: AuditContext,
        permission: str,
        resource_attributes: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log successful authorization.

        Args:
            context: Audit context
            permission: Granted permission
            resource_attributes: Resource attributes
            details: Additional details
        """
        event_details = details or {}
        if resource_attributes:
            event_details["resource_attributes"] = resource_attributes

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.AUTHORIZATION_SUCCESS,
            severity=AuditSeverity.LOW,
            timestamp=datetime.utcnow(),
            context=context,
            action="authorize",
            resource=permission,
            result="allowed",
            details=event_details,
        )

        await self._log_event(event)

    async def log_authorization_failure(
        self,
        context: AuditContext,
        permission: str,
        reason: str,
        resource_attributes: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log failed authorization.

        Args:
            context: Audit context
            permission: Denied permission
            reason: Failure reason
            resource_attributes: Resource attributes
            details: Additional details
        """
        event_details = details or {}
        if resource_attributes:
            event_details["resource_attributes"] = resource_attributes

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.AUTHORIZATION_FAILURE,
            severity=AuditSeverity.HIGH,
            timestamp=datetime.utcnow(),
            context=context,
            action="authorize",
            resource=permission,
            result="denied",
            reason=reason,
            details=event_details,
            risk_score=self._calculate_authz_failure_risk(context, permission),
        )

        await self._log_event(event)

    async def log_permission_check(
        self,
        context: AuditContext,
        permission: str,
        result: bool,
        reason: Optional[str] = None,
        resource_attributes: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log permission check.

        Args:
            context: Audit context
            permission: Permission checked
            result: Check result
            reason: Reason for result
            resource_attributes: Resource attributes
            details: Additional details
        """
        event_details = details or {}
        if resource_attributes:
            event_details["resource_attributes"] = resource_attributes

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.PERMISSION_CHECK,
            severity=AuditSeverity.LOW if result else AuditSeverity.MEDIUM,
            timestamp=datetime.utcnow(),
            context=context,
            action="check_permission",
            resource=permission,
            result="allowed" if result else "denied",
            reason=reason,
            details=event_details,
        )

        await self._log_event(event)

    async def log_abac_rule_evaluation(
        self,
        context: AuditContext,
        permission: str,
        rule_description: str,
        result: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log ABAC rule evaluation.

        Args:
            context: Audit context
            permission: Permission being checked
            rule_description: Rule description
            result: Rule evaluation result
            details: Additional details
        """
        event_details = details or {}
        event_details["rule_description"] = rule_description

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.ABAC_RULE_EVALUATION,
            severity=AuditSeverity.LOW,
            timestamp=datetime.utcnow(),
            context=context,
            action="evaluate_abac_rule",
            resource=permission,
            result="allowed" if result else "denied",
            details=event_details,
        )

        await self._log_event(event)

    async def log_token_revocation(
        self,
        context: AuditContext,
        token_id: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log token revocation.

        Args:
            context: Audit context
            token_id: Revoked token identifier
            reason: Revocation reason
            details: Additional details
        """
        event_details = details or {}
        event_details["token_id"] = token_id

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.TOKEN_REVOCATION,
            severity=AuditSeverity.MEDIUM,
            timestamp=datetime.utcnow(),
            context=context,
            action="revoke_token",
            resource="token",
            result="revoked",
            reason=reason,
            details=event_details,
        )

        await self._log_event(event)

    async def log_tenant_access(
        self,
        context: AuditContext,
        target_tenant_id: str,
        result: bool,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log tenant access attempt.

        Args:
            context: Audit context
            target_tenant_id: Target tenant ID
            result: Access result
            reason: Reason for result
            details: Additional details
        """
        event_details = details or {}
        event_details["target_tenant_id"] = target_tenant_id

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=AuditEventType.TENANT_ACCESS,
            severity=AuditSeverity.MEDIUM if result else AuditSeverity.HIGH,
            timestamp=datetime.utcnow(),
            context=context,
            action="access_tenant",
            resource=f"tenant:{target_tenant_id}",
            result="allowed" if result else "denied",
            reason=reason,
            details=event_details,
        )

        await self._log_event(event)

    async def _log_event(self, event: AuditEvent) -> None:
        """
        Log audit event to configured destinations.

        Args:
            event: Audit event to log
        """
        try:
            # Log to console if enabled
            if self.enable_console_logging:
                self._log_to_console(event)

            # Log to database if enabled
            if self.enable_database_logging:
                await self._log_to_database(event)

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Don't raise exception to avoid breaking the main flow

    def _log_to_console(self, event: AuditEvent) -> None:
        """
        Log event to console.

        Args:
            event: Audit event
        """
        log_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.context.user_id,
            "username": event.context.username,
            "tenant_id": event.context.tenant_id,
            "action": event.action,
            "resource": event.resource,
            "result": event.result,
            "reason": event.reason,
            "risk_score": event.risk_score,
            "details": event.details,
        }

        if event.result == "denied":
            self.console_logger.warning(f"Security event: {json.dumps(log_data)}")
        else:
            self.console_logger.info(f"Security event: {json.dumps(log_data)}")

    async def _log_to_database(self, event: AuditEvent) -> None:
        """
        Log event to database.

        Args:
            event: Audit event
        """
        try:
            async with get_async_session() as db:
                # Create audit log entry
                audit_log = AuditLog(
                    event_type=event.event_type.value,
                    severity=event.severity.value,
                    user_id=event.context.user_id,
                    username=event.context.username,
                    tenant_id=event.context.tenant_id,
                    session_id=event.context.session_id,
                    request_id=event.context.request_id,
                    ip_address=event.context.ip_address,
                    user_agent=event.context.user_agent,
                    endpoint=event.context.endpoint,
                    method=event.context.method,
                    resource_type=event.context.resource_type,
                    resource_id=event.context.resource_id,
                    action=event.action,
                    resource=event.resource,
                    result=event.result,
                    reason=event.reason,
                    details=json.dumps(event.details),
                    risk_score=event.risk_score,
                    timestamp=event.timestamp,
                )

                db.add(audit_log)
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to log audit event to database: {e}")
            raise AuditError(f"Database audit logging failed: {e}")

    def _calculate_auth_failure_risk(self, context: AuditContext) -> float:
        """
        Calculate risk score for authentication failure.

        Args:
            context: Audit context

        Returns:
            Risk score (0.0 to 1.0)
        """
        risk_score = 0.3  # Base risk for auth failure

        # Increase risk for repeated failures from same IP
        # This would typically check against recent failures
        if context.ip_address:
            # In a real implementation, you'd check recent failures
            # For now, we'll use a simple heuristic
            risk_score += 0.2

        return min(risk_score, 1.0)

    def _calculate_authz_failure_risk(
        self, context: AuditContext, permission: str
    ) -> float:
        """
        Calculate risk score for authorization failure.

        Args:
            context: Audit context
            permission: Denied permission

        Returns:
            Risk score (0.0 to 1.0)
        """
        risk_score = 0.4  # Base risk for authz failure

        # Increase risk for sensitive permissions
        sensitive_permissions = [
            "user.delete",
            "tenant.manage",
            "audit.read",
            "action_plan.approve",
        ]

        if permission in sensitive_permissions:
            risk_score += 0.3

        # Increase risk for admin actions
        if permission.startswith("admin."):
            risk_score += 0.2

        return min(risk_score, 1.0)


# Global audit logger instance
_audit_logger: Optional[AccessAuditLogger] = None


def get_audit_logger() -> AccessAuditLogger:
    """
    Get global audit logger instance.

    Returns:
        Audit logger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AccessAuditLogger()
    return _audit_logger


# Convenience functions for common audit operations
async def log_auth_success(context: AuditContext, token_info: Dict[str, Any]) -> None:
    """Log successful authentication."""
    logger = get_audit_logger()
    await logger.log_authentication_success(context, token_info)


async def log_auth_failure(context: AuditContext, reason: str) -> None:
    """Log failed authentication."""
    logger = get_audit_logger()
    await logger.log_authentication_failure(context, reason)


async def log_authz_success(
    context: AuditContext,
    permission: str,
    resource_attributes: Optional[Dict[str, Any]] = None,
) -> None:
    """Log successful authorization."""
    logger = get_audit_logger()
    await logger.log_authorization_success(context, permission, resource_attributes)


async def log_authz_failure(
    context: AuditContext,
    permission: str,
    reason: str,
    resource_attributes: Optional[Dict[str, Any]] = None,
) -> None:
    """Log failed authorization."""
    logger = get_audit_logger()
    await logger.log_authorization_failure(
        context, permission, reason, resource_attributes
    )


async def log_permission_check(
    context: AuditContext,
    permission: str,
    result: bool,
    reason: Optional[str] = None,
    resource_attributes: Optional[Dict[str, Any]] = None,
) -> None:
    """Log permission check."""
    logger = get_audit_logger()
    await logger.log_permission_check(
        context, permission, result, reason, resource_attributes
    )
