"""
Exceptions module for EGRC Platform.

This module provides custom exception classes for better error handling
and API responses throughout the EGRC platform.
"""

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    CacheException,
    ConfigurationError,
    ConflictError,
    DatabaseError,
    EGRCException,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


__all__ = [
    "EGRCException",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "BusinessLogicError",
    "ExternalServiceError",
    "DatabaseError",
    "RateLimitError",
    "ConfigurationError",
    "CacheException",
]
