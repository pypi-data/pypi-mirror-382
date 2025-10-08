"""
Custom log formatters for EGRC Platform.

This module provides custom log formatters for structured logging
across all EGRC services.
"""

import json
import logging
import traceback
from datetime import datetime
from uuid import uuid4


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    This formatter converts log records to JSON format with additional
    metadata for better log analysis and monitoring.
    """

    def __init__(
        self,
        service_name: str = "egrc-service",
        environment: str = "development",
        include_traceback: bool = True,
        include_extra: bool = True,
    ):
        """
        Initialize JSON formatter.

        Args:
            service_name: Name of the service
            environment: Environment (development, staging, production)
            include_traceback: Include traceback in error logs
            include_extra: Include extra fields in log record
        """
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.include_traceback = include_traceback
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }

        # Add request ID if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # Add tenant ID if available
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id

        # Add user ID if available
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # Add correlation ID if available
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add exception info if available
        if record.exc_info and self.include_traceback:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields if available
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "request_id",
                    "tenant_id",
                    "user_id",
                    "correlation_id",
                ]:
                    extra_fields[key] = value

            if extra_fields:
                log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str, ensure_ascii=False)


class StructuredFormatter(logging.Formatter):
    """
    Structured formatter for human-readable logs.

    This formatter provides a structured but human-readable format
    for development and debugging purposes.
    """

    def __init__(
        self,
        service_name: str = "egrc-service",
        include_traceback: bool = True,
        include_extra: bool = True,
    ):
        """
        Initialize structured formatter.

        Args:
            service_name: Name of the service
            include_traceback: Include traceback in error logs
            include_extra: Include extra fields in log record
        """
        super().__init__()
        self.service_name = service_name
        self.include_traceback = include_traceback
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record in structured format.

        Args:
            record: Log record

        Returns:
            Structured formatted log string
        """
        timestamp = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]

        # Base log line
        log_parts = [
            f"[{timestamp}]",
            f"[{record.levelname:8}]",
            f"[{self.service_name}]",
            f"[{record.name}]",
            record.getMessage(),
        ]

        # Add request context
        context_parts = []
        if hasattr(record, "request_id"):
            context_parts.append(f"req_id={record.request_id}")
        if hasattr(record, "tenant_id"):
            context_parts.append(f"tenant={record.tenant_id}")
        if hasattr(record, "user_id"):
            context_parts.append(f"user={record.user_id}")
        if hasattr(record, "correlation_id"):
            context_parts.append(f"corr_id={record.correlation_id}")

        if context_parts:
            log_parts.append(f"[{' '.join(context_parts)}]")

        # Add location info
        log_parts.append(f"[{record.module}:{record.funcName}:{record.lineno}]")

        log_line = " ".join(log_parts)

        # Add exception info if available
        if record.exc_info and self.include_traceback:
            log_line += "\n" + self.formatException(record.exc_info)

        # Add extra fields if available
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "request_id",
                    "tenant_id",
                    "user_id",
                    "correlation_id",
                ]:
                    extra_fields[key] = value

            if extra_fields:
                log_line += f"\nExtra: {json.dumps(extra_fields, default=str)}"

        return log_line


class AuditFormatter(logging.Formatter):
    """
    Specialized formatter for audit logs.

    This formatter is specifically designed for audit logs with
    additional security and compliance fields.
    """

    def __init__(self, service_name: str = "egrc-service"):
        """
        Initialize audit formatter.

        Args:
            service_name: Name of the service
        """
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """
        Format audit log record.

        Args:
            record: Log record

        Returns:
            Formatted audit log string
        """
        audit_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "audit_id": getattr(record, "audit_id", str(uuid4())),
            "event_type": getattr(record, "event_type", "AUDIT"),
            "action": getattr(record, "action", "UNKNOWN"),
            "resource": getattr(record, "resource", None),
            "resource_id": getattr(record, "resource_id", None),
            "user_id": getattr(record, "user_id", None),
            "tenant_id": getattr(record, "tenant_id", None),
            "ip_address": getattr(record, "ip_address", None),
            "user_agent": getattr(record, "user_agent", None),
            "request_id": getattr(record, "request_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
            "status": getattr(record, "status", "SUCCESS"),
            "details": getattr(record, "details", {}),
        }

        # Add exception info for failed operations
        if record.exc_info:
            audit_data["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }
            audit_data["status"] = "FAILURE"

        return json.dumps(audit_data, default=str, ensure_ascii=False)


class PerformanceFormatter(logging.Formatter):
    """
    Formatter for performance logs.

    This formatter is designed for performance monitoring logs
    with timing and metrics information.
    """

    def __init__(self, service_name: str = "egrc-service"):
        """
        Initialize performance formatter.

        Args:
            service_name: Name of the service
        """
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """
        Format performance log record.

        Args:
            record: Log record

        Returns:
            Formatted performance log string
        """
        perf_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "operation": getattr(record, "operation", "UNKNOWN"),
            "duration_ms": getattr(record, "duration_ms", None),
            "memory_mb": getattr(record, "memory_mb", None),
            "cpu_percent": getattr(record, "cpu_percent", None),
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
            "tenant_id": getattr(record, "tenant_id", None),
            "metrics": getattr(record, "metrics", {}),
        }

        return json.dumps(perf_data, default=str, ensure_ascii=False)
