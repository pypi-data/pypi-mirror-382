"""
Logging configuration for EGRC Platform.

This module provides centralized logging configuration that can be used
across all EGRC services and microservices.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory

from ..config.settings import Settings
from ..constants.constants import Environment, LogLevel


def configure_logging(
    settings: Settings | None = None,
    log_level: str | None = None,
    environment: str | None = None,
    service_name: str | None = None,
    log_file: str | None = None,
    enable_json: bool = True,
    enable_console: bool = True,
    enable_file: bool = False,
    enable_database: bool = False,
    enable_audit: bool = False,
) -> None:
    """
    Configure logging for the EGRC platform.

    Args:
        settings: Application settings
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment (development, testing, staging, production)
        service_name: Name of the service
        log_file: Path to log file
        enable_json: Enable JSON formatting
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_database: Enable database logging
        enable_audit: Enable audit logging
    """
    # Use settings if provided
    if settings:
        log_level = log_level or settings.log_level
        environment = environment or settings.environment
        service_name = service_name or settings.app_name
        log_file = log_file or settings.log_file

    # Set defaults
    log_level = log_level or LogLevel.INFO
    environment = environment or Environment.DEVELOPMENT
    service_name = service_name or "egrc-service"
    log_file = log_file or "logs/egrc.log"

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            (
                structlog.processors.JSONRenderer()
                if enable_json
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging_config = _get_logging_config(
        log_level=log_level,
        environment=environment,
        service_name=service_name,
        log_file=log_file,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_database=enable_database,
        enable_audit=enable_audit,
    )

    logging.config.dictConfig(logging_config)


def _get_logging_config(
    log_level: str,
    environment: str,
    service_name: str,
    log_file: str,
    enable_console: bool,
    enable_file: bool,
    enable_database: bool,
    enable_audit: bool,
) -> dict[str, Any]:
    """
    Get logging configuration dictionary.

    Args:
        log_level: Log level
        environment: Environment
        service_name: Service name
        log_file: Log file path
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_database: Enable database logging
        enable_audit: Enable audit logging

    Returns:
        Logging configuration dictionary
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "egrc_core.logging.formatters.JSONFormatter",
                "service_name": service_name,
                "environment": environment,
            },
            "audit": {
                "()": "egrc_core.logging.formatters.AuditFormatter",
                "service_name": service_name,
            },
        },
        "filters": {
            "request_id": {
                "()": "egrc_core.logging.filters.RequestIDFilter",
            },
            "tenant": {
                "()": "egrc_core.logging.filters.TenantFilter",
            },
            "user": {
                "()": "egrc_core.logging.filters.UserFilter",
            },
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": [],
                "propagate": False,
            },
            "egrc_core": {
                "level": log_level,
                "handlers": [],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": [],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": [],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": [],
                "propagate": False,
            },
        },
    }

    # Add console handler
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": (
                "json" if environment == Environment.PRODUCTION else "detailed"
            ),
            "stream": sys.stdout,
            "filters": ["request_id", "tenant", "user"],
        }
        for logger in config["loggers"].values():
            logger["handlers"].append("console")

    # Add file handler
    if enable_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "filters": ["request_id", "tenant", "user"],
        }
        for logger in config["loggers"].values():
            logger["handlers"].append("file")

    # Add database handler
    if enable_database:
        config["handlers"]["database"] = {
            "()": "egrc_core.logging.handlers.DatabaseHandler",
            "level": log_level,
            "formatter": "json",
            "filters": ["request_id", "tenant", "user"],
        }
        for logger in config["loggers"].values():
            logger["handlers"].append("database")

    # Add audit handler
    if enable_audit:
        config["handlers"]["audit"] = {
            "()": "egrc_core.logging.handlers.AuditHandler",
            "level": "INFO",
            "formatter": "audit",
            "filters": ["request_id", "tenant", "user"],
        }
        config["loggers"]["audit"] = {
            "level": "INFO",
            "handlers": ["audit"],
            "propagate": False,
        }

    return config


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def get_standard_logger(name: str) -> logging.Logger:
    """
    Get a standard Python logger instance.

    Args:
        name: Logger name

    Returns:
        Standard logger instance
    """
    return logging.getLogger(name)


def set_log_level(logger_name: str, level: str) -> None:
    """
    Set log level for a specific logger.

    Args:
        logger_name: Name of the logger
        level: Log level
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))


def add_handler_to_logger(logger_name: str, handler: logging.Handler) -> None:
    """
    Add a handler to a specific logger.

    Args:
        logger_name: Name of the logger
        handler: Logging handler
    """
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)


def remove_handler_from_logger(logger_name: str, handler: logging.Handler) -> None:
    """
    Remove a handler from a specific logger.

    Args:
        logger_name: Name of the logger
        handler: Logging handler
    """
    logger = logging.getLogger(logger_name)
    logger.removeHandler(handler)


def get_logger_config() -> dict[str, Any]:
    """
    Get current logging configuration.

    Returns:
        Current logging configuration
    """
    return logging.getLogger().manager.loggerDict


def reset_logging() -> None:
    """Reset logging configuration to defaults."""
    # Clear all handlers
    for logger in logging.Logger.manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            logger.handlers.clear()

    # Reset root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.WARNING)

    # Reset structlog
    structlog.reset_defaults()
