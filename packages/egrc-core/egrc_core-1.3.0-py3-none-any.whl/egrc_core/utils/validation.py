"""
Environment validation utilities for EGRC Platform.

This module provides utilities to validate environment variables and configuration
settings to ensure they meet security and operational requirements.
"""

import os
import re
from pathlib import Path

from ..constants.constants import EnvironmentConstants


class EnvironmentValidationError(Exception):
    """Exception raised when environment validation fails."""

    def __init__(self, message: str, errors: list[str] = None):
        super().__init__(message)
        self.errors = errors or []


class SecurityValidationError(EnvironmentValidationError):
    """Exception raised when security validation fails."""


class ConfigurationValidationError(EnvironmentValidationError):
    """Exception raised when configuration validation fails."""


class EnvironmentValidator:
    """Environment validation utility class."""

    def __init__(self, required_vars: set[str] | None = None):
        """
        Initialize environment validator.

        Args:
            required_vars: Set of required environment variable names
        """
        self.required_vars = required_vars or set()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_required_variables(self) -> bool:
        """
        Validate that all required environment variables are present.

        Returns:
            True if all required variables are present, False otherwise
        """
        missing_vars = []

        for var in self.required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.errors.append(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            return False

        return True

    def validate_security_settings(self) -> bool:
        """
        Validate security-related environment variables.

        Returns:
            True if security settings are valid, False otherwise
        """
        is_valid = True

        # Validate JWT secret key
        jwt_secret = os.getenv("EGRC_JWT_SECRET_KEY")
        if jwt_secret:
            if len(jwt_secret) < 32:
                self.errors.append("JWT secret key must be at least 32 characters long")
                is_valid = False

            if jwt_secret in [
                "your-super-secret-jwt-key-change-this-in-production",
                "dev-secret-key-not-for-production",
            ]:
                self.warnings.append(
                    "JWT secret key appears to be a default value - "
                    "change in production"
                )

        # Validate encryption key
        encryption_key = os.getenv("EGRC_ENCRYPTION_KEY")
        if encryption_key:
            if len(encryption_key) < 32:
                self.errors.append("Encryption key must be at least 32 characters long")
                is_valid = False

            if encryption_key in [
                "your-encryption-key-change-this-in-production",
                "dev-encryption-key-not-for-production",
            ]:
                self.warnings.append(
                    "Encryption key appears to be a default value - "
                    "change in production"
                )

        # Validate database password
        db_password = os.getenv("EGRC_DATABASE_PASSWORD")
        if db_password:
            if len(db_password) < 8:
                self.errors.append(
                    "Database password must be at least 8 characters long"
                )
                is_valid = False

            if db_password in ["postgres", "password", "admin", "root"]:
                self.warnings.append(
                    "Database password appears to be weak - use a stronger password"
                )

        # Validate Redis password
        redis_password = os.getenv("EGRC_REDIS_PASSWORD")
        if redis_password:
            if len(redis_password) < 8:
                self.errors.append("Redis password must be at least 8 characters long")
                is_valid = False

        # Validate RabbitMQ password
        rabbitmq_password = os.getenv("EGRC_RABBITMQ_PASSWORD")
        if rabbitmq_password:
            if len(rabbitmq_password) < 8:
                self.errors.append(
                    "RabbitMQ password must be at least 8 characters long"
                )
                is_valid = False

        return is_valid

    def validate_database_settings(self) -> bool:
        """
        Validate database-related environment variables.

        Returns:
            True if database settings are valid, False otherwise
        """
        is_valid = True

        # Validate database URL format
        db_url = os.getenv("EGRC_DATABASE_URL")
        if db_url:
            if not db_url.startswith(("postgresql://", "postgresql+asyncpg://")):
                self.errors.append(
                    "Database URL must start with 'postgresql://' or "
                    "'postgresql+asyncpg://'"
                )
                is_valid = False

        # Validate pool size
        pool_size = os.getenv("EGRC_DATABASE_POOL_SIZE")
        if pool_size:
            try:
                size = int(pool_size)
                if size < 1 or size > 100:
                    self.errors.append("Database pool size must be between 1 and 100")
                    is_valid = False
            except ValueError:
                self.errors.append("Database pool size must be a valid integer")
                is_valid = False

        # Validate max overflow
        max_overflow = os.getenv("EGRC_DATABASE_MAX_OVERFLOW")
        if max_overflow:
            try:
                overflow = int(max_overflow)
                if overflow < 0 or overflow > 1000:
                    self.errors.append(
                        "Database max overflow must be between 0 and 1000"
                    )
                    is_valid = False
            except ValueError:
                self.errors.append("Database max overflow must be a valid integer")
                is_valid = False

        return is_valid

    def validate_redis_settings(self) -> bool:
        """
        Validate Redis-related environment variables.

        Returns:
            True if Redis settings are valid, False otherwise
        """
        is_valid = True

        # Validate Redis URL format
        redis_url = os.getenv("EGRC_REDIS_URL")
        if redis_url:
            if not redis_url.startswith("redis://"):
                self.errors.append("Redis URL must start with 'redis://'")
                is_valid = False

        # Validate Redis database number
        redis_db = os.getenv("EGRC_REDIS_DB")
        if redis_db:
            try:
                db_num = int(redis_db)
                if db_num < 0 or db_num > 15:
                    self.errors.append("Redis database number must be between 0 and 15")
                    is_valid = False
            except ValueError:
                self.errors.append("Redis database number must be a valid integer")
                is_valid = False

        return is_valid

    def validate_rabbitmq_settings(self) -> bool:
        """
        Validate RabbitMQ-related environment variables.

        Returns:
            True if RabbitMQ settings are valid, False otherwise
        """
        is_valid = True

        # Validate RabbitMQ URL format
        rabbitmq_url = os.getenv("EGRC_RABBITMQ_URL")
        if rabbitmq_url:
            if not rabbitmq_url.startswith("amqp://"):
                self.errors.append("RabbitMQ URL must start with 'amqp://'")
                is_valid = False

        # Validate RabbitMQ port
        rabbitmq_port = os.getenv("EGRC_RABBITMQ_PORT")
        if rabbitmq_port:
            try:
                port = int(rabbitmq_port)
                if port < 1 or port > 65535:
                    self.errors.append("RabbitMQ port must be between 1 and 65535")
                    is_valid = False
            except ValueError:
                self.errors.append("RabbitMQ port must be a valid integer")
                is_valid = False

        return is_valid

    def validate_keycloak_settings(self) -> bool:
        """
        Validate Keycloak-related environment variables.

        Returns:
            True if Keycloak settings are valid, False otherwise
        """
        is_valid = True

        # Validate Keycloak URL format
        keycloak_url = os.getenv("EGRC_KEYCLOAK_URL")
        if keycloak_url:
            if not keycloak_url.startswith(("http://", "https://")):
                self.errors.append(
                    "Keycloak URL must start with 'http://' or 'https://'"
                )
                is_valid = False

        # Validate Keycloak realm name
        keycloak_realm = os.getenv("EGRC_KEYCLOAK_REALM")
        if keycloak_realm:
            if not re.match(r"^[a-zA-Z0-9_-]+$", keycloak_realm):
                self.errors.append(
                    "Keycloak realm name must contain only alphanumeric "
                    "characters, hyphens, and underscores"
                )
                is_valid = False

        # Validate Keycloak client ID
        keycloak_client_id = os.getenv("EGRC_KEYCLOAK_CLIENT_ID")
        if keycloak_client_id:
            if not re.match(r"^[a-zA-Z0-9_-]+$", keycloak_client_id):
                self.errors.append(
                    "Keycloak client ID must contain only alphanumeric "
                    "characters, hyphens, and underscores"
                )
                is_valid = False

        return is_valid

    def validate_logging_settings(self) -> bool:
        """
        Validate logging-related environment variables.

        Returns:
            True if logging settings are valid, False otherwise
        """
        is_valid = True

        # Validate log level
        log_level = os.getenv("EGRC_LOG_LEVEL")
        if log_level:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if log_level.upper() not in valid_levels:
                self.errors.append(
                    f"Log level must be one of: {', '.join(valid_levels)}"
                )
                is_valid = False

        # Validate log format
        log_format = os.getenv("EGRC_LOG_FORMAT")
        if log_format:
            valid_formats = ["json", "text", "colored"]
            if log_format.lower() not in valid_formats:
                self.errors.append(
                    f"Log format must be one of: {', '.join(valid_formats)}"
                )
                is_valid = False

        # Validate log file path
        log_file_path = os.getenv("EGRC_LOG_FILE_PATH")
        if log_file_path:
            log_path = Path(log_file_path)
            if not log_path.parent.exists():
                self.warnings.append(
                    f"Log file directory does not exist: {log_path.parent}"
                )

        return is_valid

    def validate_monitoring_settings(self) -> bool:
        """
        Validate monitoring-related environment variables.

        Returns:
            True if monitoring settings are valid, False otherwise
        """
        is_valid = True

        # Validate metrics port
        metrics_port = os.getenv("EGRC_METRICS_PORT")
        if metrics_port:
            try:
                port = int(metrics_port)
                if port < 1 or port > 65535:
                    self.errors.append("Metrics port must be between 1 and 65535")
                    is_valid = False
            except ValueError:
                self.errors.append("Metrics port must be a valid integer")
                is_valid = False

        # Validate tracing sample rate
        tracing_sample_rate = os.getenv("EGRC_TRACING_SAMPLE_RATE")
        if tracing_sample_rate:
            try:
                rate = float(tracing_sample_rate)
                if rate < 0.0 or rate > 1.0:
                    self.errors.append(
                        "Tracing sample rate must be between 0.0 and 1.0"
                    )
                    is_valid = False
            except ValueError:
                self.errors.append("Tracing sample rate must be a valid float")
                is_valid = False

        return is_valid

    def validate_api_settings(self) -> bool:
        """
        Validate API-related environment variables.

        Returns:
            True if API settings are valid, False otherwise
        """
        is_valid = True

        # Validate server port
        server_port = os.getenv("EGRC_PORT")
        if server_port:
            try:
                port = int(server_port)
                if port < 1 or port > 65535:
                    self.errors.append("Server port must be between 1 and 65535")
                    is_valid = False
            except ValueError:
                self.errors.append("Server port must be a valid integer")
                is_valid = False

        # Validate page size
        page_size = os.getenv("EGRC_DEFAULT_PAGE_SIZE")
        if page_size:
            try:
                size = int(page_size)
                if size < 1 or size > 1000:
                    self.errors.append("Default page size must be between 1 and 1000")
                    is_valid = False
            except ValueError:
                self.errors.append("Default page size must be a valid integer")
                is_valid = False

        return is_valid

    def validate_graphql_settings(self) -> bool:
        """
        Validate GraphQL-related environment variables.

        Returns:
            True if GraphQL settings are valid, False otherwise
        """
        is_valid = True

        # Validate query depth limit
        query_depth_limit = os.getenv("EGRC_GRAPHQL_QUERY_DEPTH_LIMIT")
        if query_depth_limit:
            try:
                depth = int(query_depth_limit)
                if depth < 1 or depth > 50:
                    self.errors.append(
                        "GraphQL query depth limit must be between 1 and 50"
                    )
                    is_valid = False
            except ValueError:
                self.errors.append("GraphQL query depth limit must be a valid integer")
                is_valid = False

        # Validate query complexity limit
        query_complexity_limit = os.getenv("EGRC_GRAPHQL_QUERY_COMPLEXITY_LIMIT")
        if query_complexity_limit:
            try:
                complexity = int(query_complexity_limit)
                if complexity < 1 or complexity > 10000:
                    self.errors.append(
                        "GraphQL query complexity limit must be between 1 and 10000"
                    )
                    is_valid = False
            except ValueError:
                self.errors.append(
                    "GraphQL query complexity limit must be a valid integer"
                )
                is_valid = False

        return is_valid

    def validate_environment_specific_settings(self) -> bool:
        """
        Validate environment-specific settings.

        Returns:
            True if environment settings are valid, False otherwise
        """
        is_valid = True

        environment = os.getenv(
            "EGRC_ENVIRONMENT", EnvironmentConstants.DEFAULT_ENVIRONMENT
        )

        # Validate environment value
        valid_environments = [
            EnvironmentConstants.ENV_DEVELOPMENT,
            EnvironmentConstants.ENV_TESTING,
            EnvironmentConstants.ENV_STAGING,
            EnvironmentConstants.ENV_PRODUCTION,
            EnvironmentConstants.ENV_LOCAL,
        ]

        if environment not in valid_environments:
            self.errors.append(
                f"Environment must be one of: {', '.join(valid_environments)}"
            )
            is_valid = False

        # Production-specific validations
        if environment == EnvironmentConstants.ENV_PRODUCTION:
            # Check for debug mode
            debug = os.getenv("EGRC_DEBUG", "false").lower()
            if debug == "true":
                self.errors.append("Debug mode cannot be enabled in production")
                is_valid = False

            # Check for default secrets
            jwt_secret = os.getenv("EGRC_JWT_SECRET_KEY")
            if jwt_secret and "change-this" in jwt_secret.lower():
                self.errors.append(
                    "JWT secret key must be changed from default value in production"
                )
                is_valid = False

            encryption_key = os.getenv("EGRC_ENCRYPTION_KEY")
            if encryption_key and "change-this" in encryption_key.lower():
                self.errors.append(
                    "Encryption key must be changed from default value in production"
                )
                is_valid = False

            # Check for introspection and playground
            introspection = os.getenv(
                "EGRC_GRAPHQL_ENABLE_INTROSPECTION", "false"
            ).lower()
            if introspection == "true":
                self.warnings.append(
                    "GraphQL introspection should be disabled in production"
                )

            playground = os.getenv("EGRC_GRAPHQL_ENABLE_PLAYGROUND", "false").lower()
            if playground == "true":
                self.warnings.append(
                    "GraphQL playground should be disabled in production"
                )

        return is_valid

    def validate_file_paths(self) -> bool:
        """
        Validate file path environment variables.

        Returns:
            True if file paths are valid, False otherwise
        """
        is_valid = True

        # Validate log file path
        log_file_path = os.getenv("EGRC_LOG_FILE_PATH")
        if log_file_path:
            log_path = Path(log_file_path)
            if not log_path.parent.exists():
                self.warnings.append(
                    f"Log file directory does not exist: {log_path.parent}"
                )

        # Validate storage path
        storage_path = os.getenv("EGRC_STORAGE_PATH")
        if storage_path and not storage_path.startswith("s3://"):
            storage_dir = Path(storage_path)
            if not storage_dir.exists():
                self.warnings.append(f"Storage directory does not exist: {storage_dir}")

        return is_valid

    def validate_all(self) -> tuple[bool, list[str], list[str]]:
        """
        Validate all environment variables and settings.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()

        # Run all validation methods
        validations = [
            self.validate_required_variables,
            self.validate_security_settings,
            self.validate_database_settings,
            self.validate_redis_settings,
            self.validate_rabbitmq_settings,
            self.validate_keycloak_settings,
            self.validate_logging_settings,
            self.validate_monitoring_settings,
            self.validate_api_settings,
            self.validate_graphql_settings,
            self.validate_environment_specific_settings,
            self.validate_file_paths,
        ]

        is_valid = True
        for validation in validations:
            if not validation():
                is_valid = False

        return is_valid, self.errors, self.warnings

    def get_validation_report(self) -> str:
        """
        Get a formatted validation report.

        Returns:
            Formatted validation report string
        """
        is_valid, errors, warnings = self.validate_all()

        report = []
        report.append("=" * 60)
        report.append("EGRC CORE ENVIRONMENT VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")

        if is_valid:
            report.append("✅ Environment validation PASSED")
        else:
            report.append("❌ Environment validation FAILED")

        report.append("")

        if errors:
            report.append("ERRORS:")
            report.append("-" * 20)
            for error in errors:
                report.append(f"❌ {error}")
            report.append("")

        if warnings:
            report.append("WARNINGS:")
            report.append("-" * 20)
            for warning in warnings:
                report.append(f"⚠️  {warning}")
            report.append("")

        if not errors and not warnings:
            report.append("✅ No issues found")

        report.append("=" * 60)

        return "\n".join(report)


def validate_environment(
    required_vars: set[str] | None = None, raise_on_error: bool = False
) -> tuple[bool, list[str], list[str]]:
    """
    Validate environment variables and configuration.

    Args:
        required_vars: Set of required environment variable names
        raise_on_error: Whether to raise an exception on validation failure

    Returns:
        Tuple of (is_valid, errors, warnings)

    Raises:
        EnvironmentValidationError: If validation fails and raise_on_error is True
    """
    validator = EnvironmentValidator(required_vars)
    is_valid, errors, warnings = validator.validate_all()

    if not is_valid and raise_on_error:
        raise EnvironmentValidationError("Environment validation failed", errors=errors)

    return is_valid, errors, warnings


def validate_security_settings(
    raise_on_error: bool = False,
) -> tuple[bool, list[str], list[str]]:
    """
    Validate security-related environment variables.

    Args:
        raise_on_error: Whether to raise an exception on validation failure

    Returns:
        Tuple of (is_valid, errors, warnings)

    Raises:
        SecurityValidationError: If security validation fails and raise_on_error is True
    """
    validator = EnvironmentValidator()
    is_valid = validator.validate_security_settings()
    errors = validator.errors
    warnings = validator.warnings

    if not is_valid and raise_on_error:
        raise SecurityValidationError("Security validation failed", errors=errors)

    return is_valid, errors, warnings


def validate_production_settings(
    raise_on_error: bool = False,
) -> tuple[bool, list[str], list[str]]:
    """
    Validate production environment settings.

    Args:
        raise_on_error: Whether to raise an exception on validation failure

    Returns:
        Tuple of (is_valid, errors, warnings)

    Raises:
        ConfigurationValidationError: If production validation fails and
            raise_on_error is True
    """
    environment = os.getenv(
        "EGRC_ENVIRONMENT", EnvironmentConstants.DEFAULT_ENVIRONMENT
    )

    if environment != EnvironmentConstants.ENV_PRODUCTION:
        return True, [], []

    validator = EnvironmentValidator()
    is_valid = validator.validate_environment_specific_settings()
    errors = validator.errors
    warnings = validator.warnings

    if not is_valid and raise_on_error:
        raise ConfigurationValidationError(
            "Production configuration validation failed", errors=errors
        )

    return is_valid, errors, warnings


def print_validation_report(required_vars: set[str] | None = None) -> None:
    """
    Print a formatted validation report to stdout.

    Args:
        required_vars: Set of required environment variable names
    """
    validator = EnvironmentValidator(required_vars)
    report = validator.get_validation_report()
    # Use proper logging instead of print
    import logging

    logger = logging.getLogger(__name__)
    logger.info(report)


# Default required environment variables for EGRC Core
DEFAULT_REQUIRED_VARS = {
    "EGRC_ENVIRONMENT",
    "EGRC_DATABASE_URL",
    "EGRC_REDIS_URL",
    "EGRC_RABBITMQ_URL",
    "EGRC_JWT_SECRET_KEY",
    "EGRC_ENCRYPTION_KEY",
    "EGRC_KEYCLOAK_URL",
    "EGRC_KEYCLOAK_REALM",
    "EGRC_KEYCLOAK_CLIENT_ID",
    "EGRC_KEYCLOAK_CLIENT_SECRET",
}


def validate_egrc_environment(
    raise_on_error: bool = False,
) -> tuple[bool, list[str], list[str]]:
    """
    Validate EGRC Core environment with default required variables.

    Args:
        raise_on_error: Whether to raise an exception on validation failure

    Returns:
        Tuple of (is_valid, errors, warnings)

    Raises:
        EnvironmentValidationError: If validation fails and raise_on_error is True
    """
    return validate_environment(
        required_vars=DEFAULT_REQUIRED_VARS, raise_on_error=raise_on_error
    )
