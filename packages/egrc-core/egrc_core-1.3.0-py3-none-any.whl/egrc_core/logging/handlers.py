"""
Custom log handlers for EGRC Platform.

This module provides custom log handlers for database logging,
audit logging, and other specialized logging needs.
"""

import logging
import logging.handlers
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


class DatabaseHandler(logging.Handler):
    """
    Custom handler for logging to database.

    This handler stores log records in the database for
    centralized logging and analysis.
    """

    def __init__(
        self,
        db_session: Session | None = None,
        async_db_session: AsyncSession | None = None,
        table_name: str = "system_logs",
        level: int = logging.NOTSET,
    ):
        """
        Initialize database handler.

        Args:
            db_session: Synchronous database session
            async_db_session: Asynchronous database session
            table_name: Name of the log table
            level: Log level
        """
        super().__init__(level)
        self.db_session = db_session
        self.async_db_session = async_db_session
        self.table_name = table_name

        if not self.db_session and not self.async_db_session:
            raise ValueError("Either db_session or async_db_session must be provided")

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the database.

        Args:
            record: Log record to emit
        """
        try:
            log_entry = self._create_log_entry(record)

            if self.async_db_session:
                # For async sessions, we need to handle this differently
                # This is a simplified version - in practice, you'd use asyncio
                pass
            else:
                self.db_session.add(log_entry)
                self.db_session.commit()

        except Exception:
            self.handleError(record)

    def _create_log_entry(self, record: logging.LogRecord) -> dict[str, Any]:
        """
        Create a log entry from a log record.

        Args:
            record: Log record

        Returns:
            Dictionary representing the log entry
        """
        return {
            "timestamp": datetime.fromtimestamp(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
            "request_id": getattr(record, "request_id", None),
            "tenant_id": getattr(record, "tenant_id", None),
            "user_id": getattr(record, "user_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
            "exception": (
                self.formatException(record.exc_info) if record.exc_info else None
            ),
        }


class AuditHandler(logging.Handler):
    """
    Custom handler for audit logging.

    This handler stores audit events in the audit log table
    for compliance and security monitoring.
    """

    def __init__(
        self,
        db_session: Session | None = None,
        async_db_session: AsyncSession | None = None,
        level: int = logging.NOTSET,
    ):
        """
        Initialize audit handler.

        Args:
            db_session: Synchronous database session
            async_db_session: Asynchronous database session
            level: Log level
        """
        super().__init__(level)
        self.db_session = db_session
        self.async_db_session = async_db_session

        if not self.db_session and not self.async_db_session:
            raise ValueError("Either db_session or async_db_session must be provided")

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit an audit log record to the database.

        Args:
            record: Log record to emit
        """
        try:
            audit_entry = self._create_audit_entry(record)

            if self.async_db_session:
                # For async sessions, we need to handle this differently
                pass
            else:
                self.db_session.add(audit_entry)
                self.db_session.commit()

        except Exception:
            self.handleError(record)

    def _create_audit_entry(self, record: logging.LogRecord):
        """
        Create an audit entry from a log record.

        Args:
            record: Log record

        Returns:
            AuditLog instance
        """
        # Lazy import to avoid circular dependency
        from ..audit.models import AuditLog

        return AuditLog(
            entity_name=getattr(record, "entity_name", "system"),
            entity_id=getattr(record, "entity_id", None),
            action=getattr(record, "action", "LOG"),
            user_id=getattr(record, "user_id", None),
            timestamp=datetime.fromtimestamp(record.created),
            change_details=getattr(record, "change_details", {}),
            ip_address=getattr(record, "ip_address", None),
            user_agent=getattr(record, "user_agent", None),
            correlation_id=getattr(record, "correlation_id", None),
            service_name=getattr(record, "service_name", "egrc-service"),
            status=getattr(record, "status", "SUCCESS"),
        )


class EmailHandler(logging.Handler):
    """
    Custom handler for sending critical logs via email.

    This handler sends critical log messages via email
    for immediate notification of important events.
    """

    def __init__(
        self,
        mailhost: str = "localhost",
        fromaddr: str = "noreply@egrc.com",
        toaddrs: list = None,
        subject: str = "EGRC Critical Log Alert",
        level: int = logging.ERROR,
    ):
        """
        Initialize email handler.

        Args:
            mailhost: SMTP server host
            fromaddr: From email address
            toaddrs: List of recipient email addresses
            subject: Email subject
            level: Log level
        """
        super().__init__(level)
        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs or []
        self.subject = subject

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record via email.

        Args:
            record: Log record to emit
        """
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            if not self.toaddrs:
                return

            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.fromaddr
            msg["To"] = ", ".join(self.toaddrs)
            msg["Subject"] = f"{self.subject} - {record.levelname}"

            # Create email body
            body = """
Critical Log Alert

Level: {record.levelname}
Logger: {record.name}
Message: {record.getMessage()}
Time: {datetime.fromtimestamp(record.created)}
Module: {record.module}
Function: {record.funcName}
Line: {record.lineno}

Request ID: {getattr(record, 'request_id', 'N/A')}
Tenant ID: {getattr(record, 'tenant_id', 'N/A')}
User ID: {getattr(record, 'user_id', 'N/A')}

Exception:
{self.formatException(record.exc_info) if record.exc_info else 'None'}
"""

            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(self.mailhost)
            server.send_message(msg)
            server.quit()

        except Exception:
            self.handleError(record)


class SlackHandler(logging.Handler):
    """
    Custom handler for sending logs to Slack.

    This handler sends log messages to a Slack channel
    for real-time monitoring and alerts.
    """

    def __init__(
        self,
        webhook_url: str,
        channel: str = "#alerts",
        username: str = "EGRC Bot",
        level: int = logging.WARNING,
    ):
        """
        Initialize Slack handler.

        Args:
            webhook_url: Slack webhook URL
            channel: Slack channel
            username: Bot username
            level: Log level
        """
        super().__init__(level)
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to Slack.

        Args:
            record: Log record to emit
        """
        try:
            import requests

            # Create Slack message
            color = {
                "DEBUG": "#36a64f",
                "INFO": "#36a64f",
                "WARNING": "#ffaa00",
                "ERROR": "#ff0000",
                "CRITICAL": "#8B0000",
            }.get(record.levelname, "#36a64f")

            payload = {
                "channel": self.channel,
                "username": self.username,
                "attachments": [
                    {
                        "color": color,
                        "title": f"{record.levelname} - {record.name}",
                        "text": record.getMessage(),
                        "fields": [
                            {
                                "title": "Module",
                                "value": f"{record.module}:{record.funcName}:{record.lineno}",
                                "short": True,
                            },
                            {
                                "title": "Time",
                                "value": datetime.fromtimestamp(
                                    record.created
                                ).strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True,
                            },
                            {
                                "title": "Request ID",
                                "value": getattr(record, "request_id", "N/A"),
                                "short": True,
                            },
                            {
                                "title": "User ID",
                                "value": getattr(record, "user_id", "N/A"),
                                "short": True,
                            },
                        ],
                        "footer": "EGRC Platform",
                        "ts": record.created,
                    }
                ],
            }

            # Send to Slack
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

        except Exception:
            self.handleError(record)


class MetricsHandler(logging.Handler):
    """
    Custom handler for metrics collection.

    This handler collects metrics from log records
    for monitoring and alerting purposes.
    """

    def __init__(self, level: int = logging.NOTSET):
        """
        Initialize metrics handler.

        Args:
            level: Log level
        """
        super().__init__(level)
        self.metrics = {
            "total_logs": 0,
            "by_level": {},
            "by_module": {},
            "by_hour": {},
            "errors": 0,
            "warnings": 0,
        }

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record and collect metrics.

        Args:
            record: Log record to emit
        """
        try:
            # Update metrics
            self.metrics["total_logs"] += 1

            # Count by level
            level = record.levelname
            self.metrics["by_level"][level] = self.metrics["by_level"].get(level, 0) + 1

            # Count by module
            module = record.module
            self.metrics["by_module"][module] = (
                self.metrics["by_module"].get(module, 0) + 1
            )

            # Count by hour
            hour = datetime.fromtimestamp(record.created).hour
            self.metrics["by_hour"][hour] = self.metrics["by_hour"].get(hour, 0) + 1

            # Count errors and warnings
            if level == "ERROR":
                self.metrics["errors"] += 1
            elif level == "WARNING":
                self.metrics["warnings"] += 1

        except Exception:
            self.handleError(record)

    def get_metrics(self) -> dict[str, Any]:
        """
        Get collected metrics.

        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            "total_logs": 0,
            "by_level": {},
            "by_module": {},
            "by_hour": {},
            "errors": 0,
            "warnings": 0,
        }
