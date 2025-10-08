"""
GraphQL module for EGRC Core.

This module provides GraphQL-related functionality including schemas,
resolvers, and GraphQL API setup.
"""

# Note: example module contains CRUD examples but not GraphQL classes
from .main import create_app
from .schema import Mutation, Query, create_schema
from .schemas import AuditSchema, BaseSchema, PaginationSchema, TenantSchema


__all__ = [
    # GraphQL Core
    "Query",
    "Mutation",
    "create_schema",
    # Schemas
    "BaseSchema",
    "TenantSchema",
    "AuditSchema",
    "PaginationSchema",
    # FastAPI Integration
    "create_app",
]
