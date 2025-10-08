"""
Custom log filters for EGRC Platform.

This module provides custom log filters for adding context information
to log records across all EGRC services.
"""

import logging
from contextvars import ContextVar


# Context variables for request context
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class RequestIDFilter(logging.Filter):
    """
    Filter to add request ID to log records.

    This filter adds the current request ID to log records
    for better request tracing.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request ID to log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        request_id = request_id_var.get()
        if request_id:
            record.request_id = request_id
        return True


class TenantFilter(logging.Filter):
    """
    Filter to add tenant ID to log records.

    This filter adds the current tenant ID to log records
    for multi-tenant logging support.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add tenant ID to log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        tenant_id = tenant_id_var.get()
        if tenant_id:
            record.tenant_id = tenant_id
        return True


class UserFilter(logging.Filter):
    """
    Filter to add user ID to log records.

    This filter adds the current user ID to log records
    for user-specific logging.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add user ID to log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        user_id = user_id_var.get()
        if user_id:
            record.user_id = user_id
        return True


class CorrelationIDFilter(logging.Filter):
    """
    Filter to add correlation ID to log records.

    This filter adds the current correlation ID to log records
    for distributed tracing support.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add correlation ID to log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        correlation_id = correlation_id_var.get()
        if correlation_id:
            record.correlation_id = correlation_id
        return True


class ContextFilter(logging.Filter):
    """
    Combined filter to add all context information to log records.

    This filter adds request ID, tenant ID, user ID, and correlation ID
    to log records for comprehensive context tracking.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add all context information to log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        # Add request ID
        request_id = request_id_var.get()
        if request_id:
            record.request_id = request_id

        # Add tenant ID
        tenant_id = tenant_id_var.get()
        if tenant_id:
            record.tenant_id = tenant_id

        # Add user ID
        user_id = user_id_var.get()
        if user_id:
            record.user_id = user_id

        # Add correlation ID
        correlation_id = correlation_id_var.get()
        if correlation_id:
            record.correlation_id = correlation_id

        return True


class LevelFilter(logging.Filter):
    """
    Filter to include/exclude specific log levels.

    This filter allows fine-grained control over which log levels
    are processed by handlers.
    """

    def __init__(
        self,
        include_levels: list | None = None,
        exclude_levels: list | None = None,
    ):
        """
        Initialize level filter.

        Args:
            include_levels: List of levels to include (if specified,
                 only these levels pass)
            exclude_levels: List of levels to exclude
        """
        super().__init__()
        self.include_levels = include_levels or []
        self.exclude_levels = exclude_levels or []

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record based on level.

        Args:
            record: Log record

        Returns:
            True if record should be included
        """
        level_name = record.levelname

        # If include_levels is specified, only include those levels
        if self.include_levels:
            return level_name in self.include_levels

        # If exclude_levels is specified, exclude those levels
        if self.exclude_levels:
            return level_name not in self.exclude_levels

        # If neither is specified, include all levels
        return True


class ModuleFilter(logging.Filter):
    """
    Filter to include/exclude specific modules.

    This filter allows filtering log records based on the module
    that generated them.
    """

    def __init__(
        self,
        include_modules: list | None = None,
        exclude_modules: list | None = None,
    ):
        """
        Initialize module filter.

        Args:
            include_modules: List of modules to include
            exclude_modules: List of modules to exclude
        """
        super().__init__()
        self.include_modules = include_modules or []
        self.exclude_modules = exclude_modules or []

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record based on module.

        Args:
            record: Log record

        Returns:
            True if record should be included
        """
        module_name = record.module

        # If include_modules is specified, only include those modules
        if self.include_modules:
            return any(
                module_name.startswith(module) for module in self.include_modules
            )

        # If exclude_modules is specified, exclude those modules
        if self.exclude_modules:
            return not any(
                module_name.startswith(module) for module in self.exclude_modules
            )

        # If neither is specified, include all modules
        return True


class SensitiveDataFilter(logging.Filter):
    """
    Filter to remove sensitive data from log records.

    This filter removes or masks sensitive information like passwords,
    tokens, and other confidential data from log records.
    """

    def __init__(self, sensitive_fields: list | None = None, mask_char: str = "*"):
        """
        Initialize sensitive data filter.

        Args:
            sensitive_fields: List of field names to mask
            mask_char: Character to use for masking
        """
        super().__init__()
        self.sensitive_fields = sensitive_fields or [
            "password",
            "token",
            "secret",
            "key",
            "auth",
            "credential",
            "ssn",
            "social_security",
            "credit_card",
            "cvv",
            "pin",
        ]
        self.mask_char = mask_char

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and mask sensitive data in log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        # Mask sensitive data in the message
        message = record.getMessage()
        for field in self.sensitive_fields:
            if field.lower() in message.lower():
                # Simple masking - replace with asterisks
                message = message.replace(field, f"{self.mask_char * len(field)}")

        # Update the record message
        record.msg = message
        record.args = ()

        return True


class PerformanceFilter(logging.Filter):
    """
    Filter for performance-related log records.

    This filter adds performance metrics to log records
    for monitoring and analysis.
    """

    def __init__(self, include_metrics: bool = True):
        """
        Initialize performance filter.

        Args:
            include_metrics: Whether to include performance metrics
        """
        super().__init__()
        self.include_metrics = include_metrics

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add performance metrics to log record.

        Args:
            record: Log record

        Returns:
            True to include the record
        """
        if self.include_metrics:
            import time

            import psutil

            # Add basic performance metrics
            record.memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            record.cpu_percent = psutil.Process().cpu_percent()
            record.timestamp = time.time()

        return True


# Utility functions for setting context variables
def set_request_id(request_id: str) -> None:
    """Set the current request ID."""
    request_id_var.set(request_id)


def set_tenant_id(tenant_id: str) -> None:
    """Set the current tenant ID."""
    tenant_id_var.set(tenant_id)


def set_user_id(user_id: str) -> None:
    """Set the current user ID."""
    user_id_var.set(user_id)


def set_correlation_id(correlation_id: str) -> None:
    """Set the current correlation ID."""
    correlation_id_var.set(correlation_id)


def get_request_id() -> str | None:
    """Get the current request ID."""
    return request_id_var.get()


def get_tenant_id() -> str | None:
    """Get the current tenant ID."""
    return tenant_id_var.get()


def get_user_id() -> str | None:
    """Get the current user ID."""
    return user_id_var.get()


def get_correlation_id() -> str | None:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def clear_context() -> None:
    """Clear all context variables."""
    request_id_var.set(None)
    tenant_id_var.set(None)
    user_id_var.set(None)
    correlation_id_var.set(None)
