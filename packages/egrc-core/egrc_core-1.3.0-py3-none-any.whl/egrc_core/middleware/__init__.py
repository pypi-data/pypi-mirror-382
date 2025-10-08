"""
Common middleware components for EGRC Platform.

This module provides reusable middleware components that can be used
across all EGRC services and microservices.
"""

from .auth import AuthenticationMiddleware, AuthorizationMiddleware
from .cors import CORSMiddleware
from .error_handler import ErrorHandlerMiddleware
from .performance import PerformanceMiddleware
from .rate_limit import RateLimitMiddleware
from .request_id import RequestIDMiddleware
from .security import SecurityMiddleware
from .tenant import TenantMiddleware


__all__ = [
    "AuthenticationMiddleware",
    "AuthorizationMiddleware",
    "CORSMiddleware",
    "RateLimitMiddleware",
    "RequestIDMiddleware",
    "TenantMiddleware",
    "ErrorHandlerMiddleware",
    "SecurityMiddleware",
    "PerformanceMiddleware",
]
