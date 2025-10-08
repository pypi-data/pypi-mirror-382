"""
Logging utilities for EGRC Platform.

This module provides centralized logging configuration and utilities
for all EGRC services and microservices.
"""

from .config import configure_logging, get_logger
from .filters import RequestIDFilter, TenantFilter, UserFilter
from .formatters import JSONFormatter, StructuredFormatter
from .handlers import AuditHandler, DatabaseHandler
from .middleware import LoggingMiddleware
from .utils import log_error, log_function_call, log_performance


__all__ = [
    "configure_logging",
    "get_logger",
    "JSONFormatter",
    "StructuredFormatter",
    "RequestIDFilter",
    "TenantFilter",
    "UserFilter",
    "DatabaseHandler",
    "AuditHandler",
    "LoggingMiddleware",
    "log_function_call",
    "log_performance",
    "log_error",
]
