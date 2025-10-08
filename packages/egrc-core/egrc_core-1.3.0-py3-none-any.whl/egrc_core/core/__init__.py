"""
Core module for EGRC Core.

This module provides core functionality including authentication,
tenant management, logging, and type definitions.
"""

from .auth import AuthMiddleware
from .global_id import GlobalID, decode_global_id, encode_global_id

# Note: logging functionality is available in the main logging module
from .tenant import TenantMiddleware


# Note: types functionality is available in the types module


__all__ = [
    # Authentication
    "AuthMiddleware",
    # Tenant Management
    "TenantMiddleware",
    # Global ID
    "GlobalID",
    "encode_global_id",
    "decode_global_id",
]
