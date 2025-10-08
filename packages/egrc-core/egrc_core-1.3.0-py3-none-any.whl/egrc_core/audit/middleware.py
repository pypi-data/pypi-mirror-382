"""
Audit middleware for EGRC Platform.

This module provides middleware components for automatic audit logging
of HTTP requests, responses, and application events.
"""

import asyncio
import json
import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .models import AuditAction, AuditSeverity, AuditStatus
from .schemas import AuditCreateSchema
from .service import AuditService, log_audit


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic audit logging of HTTP requests and responses.

    This middleware automatically logs all HTTP requests and responses
    with comprehensive metadata including timing, user information,
    and request/response details.
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
        exclude_methods: list[str] | None = None,
        capture_request_body: bool = False,
        capture_response_body: bool = False,
        max_body_size: int = 1024 * 1024,  # 1MB
        sensitive_headers: list[str] | None = None,
        sensitive_fields: list[str] | None = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        self.exclude_methods = exclude_methods or ["OPTIONS", "HEAD"]
        self.capture_request_body = capture_request_body
        self.capture_response_body = capture_response_body
        self.max_body_size = max_body_size
        self.sensitive_headers = sensitive_headers or [
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
        ]
        self.sensitive_fields = sensitive_fields or [
            "password",
            "token",
            "secret",
            "key",
            "credential",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and response with audit logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in the chain

        Returns:
            HTTP response
        """
        # Skip audit logging for excluded paths and methods
        if self._should_skip_audit(request):
            return await call_next(request)

        # Generate request ID and correlation ID
        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))

        # Add request ID to headers
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # Extract request information
        start_time = time.time()
        request_info = await self._extract_request_info(request)

        # Process the request
        response = None
        error_message = None
        status = AuditStatus.SUCCESS

        try:
            response = await call_next(request)
            return response

        except Exception as e:
            error_message = str(e)
            status = AuditStatus.FAILED

            # Create error response
            if isinstance(e, HTTPException):
                response = JSONResponse(
                    status_code=e.status_code, content={"detail": e.detail}
                )
            else:
                response = JSONResponse(
                    status_code=500, content={"detail": "Internal server error"}
                )

            raise e

        finally:
            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)

            # Extract response information
            response_info = self._extract_response_info(response) if response else {}

            # Create audit log entry
            await self._create_audit_log(
                request=request,
                response=response,
                request_info=request_info,
                response_info=response_info,
                execution_time=execution_time,
                error_message=error_message,
                status=status,
                request_id=request_id,
                correlation_id=correlation_id,
            )

    def _should_skip_audit(self, request: Request) -> bool:
        """
        Determine if audit logging should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if audit should be skipped
        """
        # Skip excluded methods
        if request.method in self.exclude_methods:
            return True

        # Skip excluded paths
        for exclude_path in self.exclude_paths:
            if request.url.path.startswith(exclude_path):
                return True

        return False

    async def _extract_request_info(self, request: Request) -> dict[str, Any]:
        """
        Extract comprehensive request information.

        Args:
            request: HTTP request

        Returns:
            Request information dictionary
        """
        # Parse URL (for future use)
        # parsed_url = urlparse(str(request.url))

        # Extract headers (excluding sensitive ones)
        headers = dict(request.headers)
        for sensitive_header in self.sensitive_headers:
            if sensitive_header.lower() in headers:
                headers[sensitive_header.lower()] = "[REDACTED]"

        # Extract query parameters
        query_params = dict(request.query_params)

        # Extract request body if enabled
        request_body = None
        if self.capture_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    # Try to parse as JSON
                    try:
                        request_body = json.loads(body.decode())
                        # Redact sensitive fields
                        request_body = self._redact_sensitive_fields(request_body)
                    except json.JSONDecodeError:
                        request_body = body.decode()[:1000]  # Truncate if not JSON
            except Exception:
                request_body = "[ERROR_READING_BODY]"

        # Extract user information from headers or JWT
        user_id = headers.get("x-user-id")
        user_name = headers.get("x-user-name")
        user_email = headers.get("x-user-email")
        tenant_id = headers.get("x-tenant-id")
        session_id = headers.get("x-session-id")

        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": query_params,
            "headers": headers,
            "body": request_body,
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "tenant_id": tenant_id,
            "session_id": session_id,
            "client_ip": request.client.host if request.client else None,
            "user_agent": headers.get("user-agent"),
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length"),
        }

    def _extract_response_info(self, response: Response) -> dict[str, Any]:
        """
        Extract response information.

        Args:
            response: HTTP response

        Returns:
            Response information dictionary
        """
        # Extract headers
        headers = dict(response.headers)

        # Extract response body if enabled
        response_body = None
        if self.capture_response_body and hasattr(response, "body"):
            try:
                body = response.body
                if len(body) <= self.max_body_size:
                    # Try to parse as JSON
                    try:
                        response_body = json.loads(body.decode())
                        # Redact sensitive fields
                        response_body = self._redact_sensitive_fields(response_body)
                    except json.JSONDecodeError:
                        response_body = body.decode()[:1000]  # Truncate if not JSON
            except Exception:
                response_body = "[ERROR_READING_BODY]"

        return {
            "status_code": response.status_code,
            "headers": headers,
            "body": response_body,
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length"),
        }

    def _redact_sensitive_fields(self, data: Any) -> Any:
        """
        Redact sensitive fields from data.

        Args:
            data: Data to redact

        Returns:
            Data with sensitive fields redacted
        """
        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    redacted[key] = "[REDACTED]"
                else:
                    redacted[key] = self._redact_sensitive_fields(value)
            return redacted
        elif isinstance(data, list):
            return [self._redact_sensitive_fields(item) for item in data]
        else:
            return data

    async def _create_audit_log(
        self,
        request: Request,
        response: Response | None,
        request_info: dict[str, Any],
        response_info: dict[str, Any],
        execution_time: int,
        error_message: str | None,
        status: AuditStatus,
        request_id: str,
        correlation_id: str,
    ):
        """
        Create audit log entry for the request/response.

        Args:
            request: HTTP request
            response: HTTP response
            request_info: Request information
            response_info: Response information
            execution_time: Execution time in milliseconds
            error_message: Error message if any
            status: Audit status
            request_id: Request ID
            correlation_id: Correlation ID
        """
        try:
            # Determine action based on HTTP method
            action_map = {
                "GET": AuditAction.READ,
                "POST": AuditAction.CREATE,
                "PUT": AuditAction.UPDATE,
                "PATCH": AuditAction.UPDATE,
                "DELETE": AuditAction.DELETE,
            }
            action = action_map.get(request.method, AuditAction.CUSTOM)

            # Determine severity based on status code
            if response and response.status_code >= 500:
                severity = AuditSeverity.HIGH
            elif response and response.status_code >= 400:
                severity = AuditSeverity.MEDIUM
            else:
                severity = AuditSeverity.LOW

            # Create audit data
            audit_data = AuditCreateSchema(
                entity_name="HTTP_REQUEST",
                entity_id=request_id,
                entity_type="API_ENDPOINT",
                action=action,
                action_category="HTTP_REQUEST",
                user_id=request_info.get("user_id"),
                user_name=request_info.get("user_name"),
                user_email=request_info.get("user_email"),
                session_id=request_info.get("session_id"),
                request_id=request_id,
                correlation_id=correlation_id,
                old_values=None,
                new_values={"request": request_info, "response": response_info},
                changed_fields=None,
                change_summary=(
                    f"{request.method} {request.url.path} - "
                    f"{response.status_code if response else 'ERROR'}"
                ),
                tenant_id=request_info.get("tenant_id"),
                ip_address=request_info.get("client_ip"),
                user_agent=request_info.get("user_agent"),
                endpoint=request.url.path,
                method=request.method,
                severity=severity,
                status=status,
                error_message=error_message,
                execution_time_ms=execution_time,
                tags={
                    "http_method": request.method,
                    "endpoint": request.url.path,
                    "status_code": response.status_code if response else None,
                },
                metadata={"request_info": request_info, "response_info": response_info},
            )

            # Create audit log asynchronously
            await log_audit(
                entity_name=audit_data.entity_name,
                entity_id=audit_data.entity_id,
                action=audit_data.action,
                user_id=audit_data.user_id,
                tenant_id=audit_data.tenant_id,
                old_values=audit_data.old_values,
                new_values=audit_data.new_values,
                change_summary=audit_data.change_summary,
                severity=audit_data.severity,
                status=audit_data.status,
                error_message=audit_data.error_message,
                execution_time_ms=audit_data.execution_time_ms,
                ip_address=audit_data.ip_address,
                user_agent=audit_data.user_agent,
                endpoint=audit_data.endpoint,
                method=audit_data.method,
                request_id=audit_data.request_id,
                correlation_id=audit_data.correlation_id,
                tags=audit_data.tags,
                metadata=audit_data.metadata,
            )

        except Exception as e:
            # Log the error but don't fail the request
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log: {e}")


class DatabaseAuditHook:
    """
    Database audit hook for SQLAlchemy models.

    This hook automatically creates audit entries when database
    operations are performed on tracked models.
    """

    def __init__(self, audit_service: AuditService | None = None):
        self.audit_service = audit_service
        self.tracked_models = set()

    def register_model(self, model_class):
        """
        Register a model for audit tracking.

        Args:
            model_class: SQLAlchemy model class to track
        """
        self.tracked_models.add(model_class)

        # Add event listeners
        from sqlalchemy import event

        @event.listens_for(model_class, "after_insert")
        def after_insert(mapper, connection, target):
            asyncio.create_task(self._audit_insert(target))

        @event.listens_for(model_class, "after_update")
        def after_update(mapper, connection, target):
            asyncio.create_task(self._audit_update(target))

        @event.listens_for(model_class, "after_delete")
        def after_delete(mapper, connection, target):
            asyncio.create_task(self._audit_delete(target))

    async def _audit_insert(self, instance):
        """Audit model insertion."""
        try:
            await log_audit(
                entity_name=instance.__class__.__name__,
                entity_id=str(getattr(instance, "id", "unknown")),
                action=AuditAction.CREATE,
                new_values=self._extract_model_data(instance),
                change_summary=f"Created {instance.__class__.__name__}",
                severity=AuditSeverity.LOW,
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to audit insert: {e}")

    async def _audit_update(self, instance):
        """Audit model update."""
        try:
            # Get the old values from the history
            old_values = {}
            if hasattr(instance, "_sa_instance_state"):
                state = instance._sa_instance_state
                if hasattr(state, "committed_state"):
                    old_values = state.committed_state or {}

            await log_audit(
                entity_name=instance.__class__.__name__,
                entity_id=str(getattr(instance, "id", "unknown")),
                action=AuditAction.UPDATE,
                old_values=old_values,
                new_values=self._extract_model_data(instance),
                change_summary=f"Updated {instance.__class__.__name__}",
                severity=AuditSeverity.LOW,
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to audit update: {e}")

    async def _audit_delete(self, instance):
        """Audit model deletion."""
        try:
            await log_audit(
                entity_name=instance.__class__.__name__,
                entity_id=str(getattr(instance, "id", "unknown")),
                action=AuditAction.DELETE,
                old_values=self._extract_model_data(instance),
                change_summary=f"Deleted {instance.__class__.__name__}",
                severity=AuditSeverity.MEDIUM,
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to audit delete: {e}")

    def _extract_model_data(self, instance) -> dict[str, Any]:
        """
        Extract data from a model instance.

        Args:
            instance: Model instance

        Returns:
            Dictionary of model data
        """
        data = {}
        for column in instance.__table__.columns:
            value = getattr(instance, column.name, None)
            # Convert non-serializable types
            if hasattr(value, "isoformat"):  # datetime
                value = value.isoformat()
            elif hasattr(value, "__dict__"):  # complex objects
                value = str(value)
            data[column.name] = value
        return data


class EventAuditLogger:
    """
    Event-based audit logger for application events.

    This logger provides a simple interface for logging
    application events and business logic operations.
    """

    def __init__(self, audit_service: AuditService | None = None):
        self.audit_service = audit_service

    async def log_event(
        self,
        event_name: str,
        entity_name: str,
        entity_id: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
        data: dict[str, Any] | None = None,
        severity: AuditSeverity = AuditSeverity.LOW,
    ):
        """
        Log an application event.

        Args:
            event_name: Name of the event
            entity_name: Name of the entity
            entity_id: ID of the entity
            user_id: User ID
            tenant_id: Tenant ID
            data: Event data
            severity: Severity level
        """
        try:
            await log_audit(
                entity_name=entity_name,
                entity_id=entity_id,
                action=AuditAction.CUSTOM,
                user_id=user_id,
                tenant_id=tenant_id,
                new_values=data,
                change_summary=f"Event: {event_name}",
                severity=severity,
                tags={"event_name": event_name},
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log event: {e}")

    async def log_business_event(
        self,
        event_name: str,
        entity_name: str,
        entity_id: str,
        old_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ):
        """
        Log a business logic event with state changes.

        Args:
            event_name: Name of the event
            entity_name: Name of the entity
            entity_id: ID of the entity
            old_state: Previous state
            new_state: New state
            user_id: User ID
            tenant_id: Tenant ID
        """
        try:
            # Determine action based on event
            action = AuditAction.CUSTOM
            if "create" in event_name.lower():
                action = AuditAction.CREATE
            elif "update" in event_name.lower():
                action = AuditAction.UPDATE
            elif "delete" in event_name.lower():
                action = AuditAction.DELETE

            await log_audit(
                entity_name=entity_name,
                entity_id=entity_id,
                action=action,
                user_id=user_id,
                tenant_id=tenant_id,
                old_values=old_state,
                new_values=new_state,
                change_summary=f"Business Event: {event_name}",
                severity=AuditSeverity.MEDIUM,
                tags={"event_name": event_name, "event_type": "business"},
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log business event: {e}")

    async def log_security_event(
        self,
        event_name: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
        details: dict[str, Any] | None = None,
        severity: AuditSeverity = AuditSeverity.HIGH,
    ):
        """
        Log a security-related event.

        Args:
            event_name: Name of the security event
            user_id: User ID
            tenant_id: Tenant ID
            details: Event details
            severity: Severity level
        """
        try:
            await log_audit(
                entity_name="SECURITY_EVENT",
                entity_id=str(uuid.uuid4()),
                action=AuditAction.CUSTOM,
                user_id=user_id,
                tenant_id=tenant_id,
                new_values=details,
                change_summary=f"Security Event: {event_name}",
                severity=severity,
                tags={"event_name": event_name, "event_type": "security"},
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log security event: {e}")


# Global instances
audit_middleware = None
database_audit_hook = DatabaseAuditHook()
event_audit_logger = EventAuditLogger()


def setup_audit_middleware(app: ASGIApp, **kwargs) -> AuditMiddleware:
    """
    Setup audit middleware for the application.

    Args:
        app: FastAPI application
        **kwargs: Middleware configuration options

    Returns:
        Configured audit middleware
    """
    global audit_middleware
    audit_middleware = AuditMiddleware(app, **kwargs)
    return audit_middleware


def register_model_for_audit(model_class):
    """
    Register a model for automatic audit tracking.

    Args:
        model_class: SQLAlchemy model class
    """
    database_audit_hook.register_model(model_class)


async def log_application_event(
    event_name: str, entity_name: str, entity_id: str, **kwargs
):
    """
    Log an application event.

    Args:
        event_name: Name of the event
        entity_name: Name of the entity
        entity_id: ID of the entity
        **kwargs: Additional event data
    """
    await event_audit_logger.log_event(
        event_name=event_name, entity_name=entity_name, entity_id=entity_id, **kwargs
    )


async def log_business_event(
    event_name: str, entity_name: str, entity_id: str, **kwargs
):
    """
    Log a business logic event.

    Args:
        event_name: Name of the event
        entity_name: Name of the entity
        entity_id: ID of the entity
        **kwargs: Additional event data
    """
    await event_audit_logger.log_business_event(
        event_name=event_name, entity_name=entity_name, entity_id=entity_id, **kwargs
    )


async def log_security_event(event_name: str, **kwargs):
    """
    Log a security event.

    Args:
        event_name: Name of the security event
        **kwargs: Additional event data
    """
    await event_audit_logger.log_security_event(event_name=event_name, **kwargs)
