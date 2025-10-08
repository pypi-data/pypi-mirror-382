"""
CORS middleware for EGRC Platform.

This module provides CORS middleware for handling cross-origin requests
across all EGRC services.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware


def setup_cors(
    app: FastAPI,
    allow_origins: list[str] | None = None,
    allow_credentials: bool = True,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
    expose_headers: list[str] | None = None,
    max_age: int = 600,
) -> None:
    """
    Setup CORS middleware for FastAPI application.

    Args:
        app: FastAPI application
        allow_origins: List of allowed origins
        allow_credentials: Whether to allow credentials
        allow_methods: List of allowed HTTP methods
        allow_headers: List of allowed headers
        expose_headers: List of headers to expose
        max_age: Maximum age for preflight requests
    """
    # Default allowed origins
    if allow_origins is None:
        allow_origins = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ]

    # Default allowed methods
    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    # Default allowed headers
    if allow_headers is None:
        allow_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Tenant-ID",
            "X-User-ID",
            "X-Correlation-ID",
            "X-API-Key",
        ]

    # Default exposed headers
    if expose_headers is None:
        expose_headers = [
            "X-Request-ID",
            "X-Correlation-ID",
            "X-Total-Count",
            "X-Page-Count",
        ]

    app.add_middleware(
        FastAPICORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=expose_headers,
        max_age=max_age,
    )
