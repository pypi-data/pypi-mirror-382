"""
Logging utilities for EGRC Platform.

This module provides utility functions for logging operations
across all EGRC services.
"""

import functools
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

import structlog

from .filters import get_request_id, get_tenant_id, get_user_id


T = TypeVar("T")


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def log_function_call(
    logger: structlog.BoundLogger | None = None,
    level: str = "info",
    include_args: bool = True,
    include_result: bool = True,
    include_duration: bool = True,
    exclude_args: list | None = None,
):
    """
    Decorator to log function calls with arguments and results.

    Args:
        logger: Logger instance (if None, will create one)
        level: Log level
        include_args: Whether to include function arguments
        include_result: Whether to include function result
        include_duration: Whether to include execution duration
        exclude_args: List of argument names to exclude from logging

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if logger is None:
                func_logger = get_logger(func.__module__)
            else:
                func_logger = logger

            start_time = time.time()

            # Prepare log data
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
            }

            # Add context information
            request_id = get_request_id()
            if request_id:
                log_data["request_id"] = request_id

            tenant_id = get_tenant_id()
            if tenant_id:
                log_data["tenant_id"] = tenant_id

            user_id = get_user_id()
            if user_id:
                log_data["user_id"] = user_id

            # Add arguments
            if include_args:
                args_data = {}

                # Get function signature
                import inspect

                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                for param_name, param_value in bound_args.arguments.items():
                    if exclude_args and param_name in exclude_args:
                        args_data[param_name] = "<excluded>"
                    else:
                        # Convert to string representation, handling large objects
                        try:
                            if hasattr(param_value, "__dict__"):
                                args_data[param_name] = (
                                    f"<{type(param_value).__name__} object>"
                                )
                            else:
                                args_data[param_name] = str(param_value)
                        except Exception:
                            args_data[param_name] = "<unable to serialize>"

                log_data["args"] = args_data

            # Log function start
            getattr(func_logger, level)("Function call started", **log_data)

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Calculate duration
                duration = time.time() - start_time

                # Add result and duration
                if include_result:
                    try:
                        if hasattr(result, "__dict__"):
                            log_data["result"] = f"<{type(result).__name__} object>"
                        else:
                            log_data["result"] = str(result)
                    except Exception:
                        log_data["result"] = "<unable to serialize>"

                if include_duration:
                    log_data["duration"] = round(duration, 4)

                # Log function completion
                getattr(func_logger, level)("Function call completed", **log_data)

                return result

            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time

                # Add error information
                log_data["error"] = str(e)
                log_data["error_type"] = type(e).__name__

                if include_duration:
                    log_data["duration"] = round(duration, 4)

                # Log function error
                func_logger.error("Function call failed", **log_data, exc_info=True)

                raise

        return wrapper

    return decorator


def log_performance(
    logger: structlog.BoundLogger | None = None,
    threshold: float = 1.0,
    level: str = "warning",
):
    """
    Decorator to log slow function calls.

    Args:
        logger: Logger instance (if None, will create one)
        threshold: Duration threshold in seconds
        level: Log level for slow calls

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if logger is None:
                func_logger = get_logger(func.__module__)
            else:
                func_logger = logger

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if duration >= threshold:
                    log_data = {
                        "function": func.__name__,
                        "module": func.__module__,
                        "duration": round(duration, 4),
                        "threshold": threshold,
                    }

                    # Add context information
                    request_id = get_request_id()
                    if request_id:
                        log_data["request_id"] = request_id

                    getattr(func_logger, level)(
                        "Slow function call detected", **log_data
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time

                if duration >= threshold:
                    log_data = {
                        "function": func.__name__,
                        "module": func.__module__,
                        "duration": round(duration, 4),
                        "threshold": threshold,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }

                    getattr(func_logger, level)("Slow function call failed", **log_data)

                raise

        return wrapper

    return decorator


def log_error(
    logger: structlog.BoundLogger | None = None,
    level: str = "error",
    include_traceback: bool = True,
    reraise: bool = True,
):
    """
    Decorator to log function errors.

    Args:
        logger: Logger instance (if None, will create one)
        level: Log level for errors
        include_traceback: Whether to include traceback
        reraise: Whether to reraise the exception

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if logger is None:
                func_logger = get_logger(func.__module__)
            else:
                func_logger = logger

            try:
                return func(*args, **kwargs)

            except Exception as e:
                log_data = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

                # Add context information
                request_id = get_request_id()
                if request_id:
                    log_data["request_id"] = request_id

                tenant_id = get_tenant_id()
                if tenant_id:
                    log_data["tenant_id"] = tenant_id

                user_id = get_user_id()
                if user_id:
                    log_data["user_id"] = user_id

                # Log error
                if include_traceback:
                    getattr(func_logger, level)(
                        "Function error", **log_data, exc_info=True
                    )
                else:
                    getattr(func_logger, level)("Function error", **log_data)

                if reraise:
                    raise
                else:
                    return None

        return wrapper

    return decorator


@contextmanager
def log_context(
    logger: structlog.BoundLogger | None = None,
    operation: str = "operation",
    level: str = "info",
):
    """
    Context manager for logging operation start and completion.

    Args:
        logger: Logger instance (if None, will create one)
        operation: Operation name
        level: Log level

    Yields:
        Logger instance
    """
    if logger is None:
        context_logger = get_logger("egrc_core.context")
    else:
        context_logger = logger

    start_time = time.time()

    # Prepare log data
    log_data = {
        "operation": operation,
    }

    # Add context information
    request_id = get_request_id()
    if request_id:
        log_data["request_id"] = request_id

    tenant_id = get_tenant_id()
    if tenant_id:
        log_data["tenant_id"] = tenant_id

    user_id = get_user_id()
    if user_id:
        log_data["user_id"] = user_id

    # Log operation start
    getattr(context_logger, level)(f"{operation} started", **log_data)

    try:
        yield context_logger

        # Log operation completion
        duration = time.time() - start_time
        log_data["duration"] = round(duration, 4)
        getattr(context_logger, level)(f"{operation} completed", **log_data)

    except Exception as e:
        # Log operation error
        duration = time.time() - start_time
        log_data.update(
            {
                "duration": round(duration, 4),
                "error": str(e),
                "error_type": type(e).__name__,
            }
        )
        context_logger.error(f"{operation} failed", **log_data, exc_info=True)
        raise


def log_database_operation(
    operation: str,
    table: str,
    record_id: str | None = None,
    changes: dict[str, Any] | None = None,
    logger: structlog.BoundLogger | None = None,
) -> None:
    """
    Log database operations for audit purposes.

    Args:
        operation: Database operation (CREATE, READ, UPDATE, DELETE)
        table: Table name
        record_id: Record ID
        changes: Dictionary of changes
        logger: Logger instance
    """
    if logger is None:
        db_logger = get_logger("egrc_core.database")
    else:
        db_logger = logger

    log_data = {
        "operation": operation,
        "table": table,
    }

    if record_id:
        log_data["record_id"] = record_id

    if changes:
        log_data["changes"] = changes

    # Add context information
    request_id = get_request_id()
    if request_id:
        log_data["request_id"] = request_id

    tenant_id = get_tenant_id()
    if tenant_id:
        log_data["tenant_id"] = tenant_id

    user_id = get_user_id()
    if user_id:
        log_data["user_id"] = user_id

    db_logger.info("Database operation", **log_data)


def log_api_call(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    request_size: int | None = None,
    response_size: int | None = None,
    logger: structlog.BoundLogger | None = None,
) -> None:
    """
    Log API calls for monitoring and analysis.

    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration
        request_size: Request size in bytes
        response_size: Response size in bytes
        logger: Logger instance
    """
    if logger is None:
        api_logger = get_logger("egrc_core.api")
    else:
        api_logger = logger

    log_data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration": round(duration, 4),
    }

    if request_size:
        log_data["request_size"] = request_size

    if response_size:
        log_data["response_size"] = response_size

    # Add context information
    request_id = get_request_id()
    if request_id:
        log_data["request_id"] = request_id

    tenant_id = get_tenant_id()
    if tenant_id:
        log_data["tenant_id"] = tenant_id

    user_id = get_user_id()
    if user_id:
        log_data["user_id"] = user_id

    # Log level based on status code
    if status_code >= 500:
        api_logger.error("API call", **log_data)
    elif status_code >= 400:
        api_logger.warning("API call", **log_data)
    else:
        api_logger.info("API call", **log_data)


def log_business_event(
    event_type: str,
    entity_type: str,
    entity_id: str,
    action: str,
    details: dict[str, Any] | None = None,
    logger: structlog.BoundLogger | None = None,
) -> None:
    """
    Log business events for audit and compliance.

    Args:
        event_type: Type of business event
        entity_type: Type of entity
        entity_id: Entity ID
        action: Action performed
        details: Additional details
        logger: Logger instance
    """
    if logger is None:
        business_logger = get_logger("egrc_core.business")
    else:
        business_logger = logger

    log_data = {
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
    }

    if details:
        log_data["details"] = details

    # Add context information
    request_id = get_request_id()
    if request_id:
        log_data["request_id"] = request_id

    tenant_id = get_tenant_id()
    if tenant_id:
        log_data["tenant_id"] = tenant_id

    user_id = get_user_id()
    if user_id:
        log_data["user_id"] = user_id

    business_logger.info("Business event", **log_data)
