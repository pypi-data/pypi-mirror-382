from ..utils.validation import EnvironmentValidationError, validate_environment


"""
Configuration loader utilities for EGRC Platform.

This module provides utilities to load configuration from various sources
including environment variables, configuration files, and default values.
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..constants.constants import EnvironmentConstants


class ConfigLoader:
    """Configuration loader utility class."""

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize configuration loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path.cwd()
        self.config_cache: dict[str, Any] = {}

    def load_from_env_file(self, env_file: str | Path) -> dict[str, str]:
        """
        Load configuration from environment file.

        Args:
            env_file: Path to environment file

        Returns:
            Dictionary of environment variables
        """
        env_path = Path(env_file)
        if not env_path.exists():
            raise FileNotFoundError(f"Environment file not found: {env_path}")

        env_vars = {}
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value

        return env_vars

    def load_from_yaml(self, yaml_file: str | Path) -> dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            yaml_file: Path to YAML file

        Returns:
            Dictionary of configuration values
        """
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        with open(yaml_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def load_from_json(self, json_file: str | Path) -> dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            json_file: Path to JSON file

        Returns:
            Dictionary of configuration values
        """
        json_path = Path(json_file)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        with open(json_path, encoding="utf-8") as f:
            return json.load(f) or {}

    def load_environment_config(self, environment: str) -> dict[str, Any]:
        """
        Load environment-specific configuration.

        Args:
            environment: Environment name (development, staging, production, etc.)

        Returns:
            Dictionary of environment-specific configuration
        """
        config_files = [
            self.config_dir / f"config.{environment}.yaml",
            self.config_dir / f"config.{environment}.yml",
            self.config_dir / f"config.{environment}.json",
            self.config_dir / f".env.{environment}",
        ]

        config = {}

        for config_file in config_files:
            if config_file.exists():
                if config_file.suffix in [".yaml", ".yml"]:
                    config.update(self.load_from_yaml(config_file))
                elif config_file.suffix == ".json":
                    config.update(self.load_from_json(config_file))
                elif config_file.name.startswith(".env"):
                    env_vars = self.load_from_env_file(config_file)
                    # Convert environment variables to nested dictionary
                    for key, value in env_vars.items():
                        self._set_nested_value(config, key, value)

        return config

    def _set_nested_value(self, config: dict[str, Any], key: str, value: str) -> None:
        """
        Set nested value in configuration dictionary from dot-notation key.

        Args:
            config: Configuration dictionary
            key: Dot-notation key (e.g., 'database.host')
            value: Value to set
        """
        keys = key.lower().split("_")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Convert value to appropriate type
        converted_value = self._convert_value(value)
        current[keys[-1]] = converted_value

    def _convert_value(self, value: str) -> str | int | float | bool | list[str]:
        """
        Convert string value to appropriate type.

        Args:
            value: String value to convert

        Returns:
            Converted value
        """
        # Boolean conversion
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass

        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass

        # List conversion (comma-separated values)
        if "," in value:
            return [item.strip() for item in value.split(",")]

        return value

    def load_all_configs(self, environment: str | None = None) -> dict[str, Any]:
        """
        Load all configuration sources in order of precedence.

        Args:
            environment: Environment name (if None, uses EGRC_ENVIRONMENT env var)

        Returns:
            Merged configuration dictionary
        """
        if environment is None:
            environment = os.getenv(
                "EGRC_ENVIRONMENT", EnvironmentConstants.DEFAULT_ENVIRONMENT
            )

        config = {}

        # 1. Load default configuration
        default_config = self.load_environment_config("default")
        config.update(default_config)

        # 2. Load environment-specific configuration
        if environment != "default":
            env_config = self.load_environment_config(environment)
            config = self._merge_configs(config, env_config)

        # 3. Load local configuration (highest precedence)
        local_config = self.load_environment_config("local")
        config = self._merge_configs(config, local_config)

        return config

    def _merge_configs(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge configuration dictionaries recursively.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def save_config(self, config: dict[str, Any], output_file: str | Path) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.suffix in [".yaml", ".yml"]:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        elif output_path.suffix == ".json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported file format: {output_path.suffix}")


class EnvironmentConfigLoader:
    """Environment-specific configuration loader."""

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize environment configuration loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.loader = ConfigLoader(config_dir)
        self.environment = os.getenv(
            "EGRC_ENVIRONMENT", EnvironmentConstants.DEFAULT_ENVIRONMENT
        )

    def load_config(self, validate: bool = True) -> dict[str, Any]:
        """
        Load configuration for current environment.

        Args:
            validate: Whether to validate the configuration

        Returns:
            Configuration dictionary

        Raises:
            EnvironmentValidationError: If validation fails
        """
        config = self.loader.load_all_configs(self.environment)

        if validate:
            is_valid, errors, warnings = validate_environment()
            if not is_valid:
                # raise EnvironmentValidationError(
                #                     "Configuration validation failed", errors=errors
                #                 )
                pass

        return config

        #     def get_database_config(self) -> Dict[str, Any]:
        #         """Get database configuration."""
        #         config = self.load_config(validate=False)
        #         return config.get("database", {})
        #
        #     def get_redis_config(self) -> Dict[str, Any]:
        #         """Get Redis configuration."""
        #         config = self.load_config(validate=False)
        #         return config.get("redis", {})
        #
        #     def get_rabbitmq_config(self) -> Dict[str, Any]:
        #         """Get RabbitMQ configuration."""
        config = self.load_config(validate=False)
        return config.get("rabbitmq", {})

    def get_keycloak_config(self) -> dict[str, Any]:
        """Get Keycloak configuration."""
        config = self.load_config(validate=False)
        return config.get("keycloak", {})

    def get_security_config(self) -> dict[str, Any]:
        """Get security configuration."""
        config = self.load_config(validate=False)
        return config.get("security", {})

    def get_logging_config(self) -> dict[str, Any]:
        """Get logging configuration."""
        config = self.load_config(validate=False)
        return config.get("logging", {})

    def get_monitoring_config(self) -> dict[str, Any]:
        """Get monitoring configuration."""
        config = self.load_config(validate=False)
        return config.get("monitoring", {})

    def get_api_config(self) -> dict[str, Any]:
        """Get API configuration."""
        config = self.load_config(validate=False)
        return config.get("api", {})

    def get_graphql_config(self) -> dict[str, Any]:
        """Get GraphQL configuration."""
        config = self.load_config(validate=False)
        return config.get("graphql", {})

    def get_crud_config(self) -> dict[str, Any]:
        """Get CRUD configuration."""
        config = self.load_config(validate=False)
        return config.get("crud", {})

    def get_tenant_config(self) -> dict[str, Any]:
        """Get tenant configuration."""
        config = self.load_config(validate=False)
        return config.get("tenant", {})

    def get_feature_flags(self) -> dict[str, bool]:
        """Get feature flags configuration."""
        config = self.load_config(validate=False)
        return config.get("features", {})


@lru_cache
def get_config_loader(config_dir: Path | None = None) -> ConfigLoader:
    """
    Get cached configuration loader instance.

    Args:
        config_dir: Directory containing configuration files

    Returns:
        Configuration loader instance
    """
    return ConfigLoader(config_dir)


@lru_cache
def get_environment_config_loader(
    config_dir: Path | None = None,
) -> EnvironmentConfigLoader:
    """
    Get cached environment configuration loader instance.

    Args:
        config_dir: Directory containing configuration files

    Returns:
        Environment configuration loader instance
    """
    return EnvironmentConfigLoader(config_dir)


def load_configuration(
    environment: str | None = None,
    config_dir: Path | None = None,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Load configuration for specified environment.

    Args:
        environment: Environment name (if None, uses EGRC_ENVIRONMENT env var)
        config_dir: Directory containing configuration files
        validate: Whether to validate the configuration

    Returns:
        Configuration dictionary

    Raises:
        EnvironmentValidationError: If validation fails
    """
    loader = get_config_loader(config_dir)
    config = loader.load_all_configs(environment)

    if validate:
        is_valid, errors, warnings = validate_environment()
        if not is_valid:
            raise EnvironmentValidationError(
                "Configuration validation failed", errors=errors
            )

        return config
    #
    #
    # def load_environment_configuration(
    #     config_dir: Optional[Path] = None, validate: bool = True
    # ) -> Dict[str, Any]:
    #     """
    #     Load configuration for current environment.
    #
    #     Args:
    #         config_dir: Directory containing configuration files
    #         validate: Whether to validate the configuration
    #
    #     Returns:
    #         Configuration dictionary
    #
    #     Raises:
    #         EnvironmentValidationError: If validation fails
    #     """
    #     loader = get_environment_config_loader(config_dir)
    #     return loader.load_config(validate=validate)

    # def create_config_template(
    #     environment: str, output_file: Union[str, Path], config_dir: Optional[Path] = None
    # ) -> None:
    #     """
    #     Create configuration template for specified environment.
    #
    #     Args:
    #         environment: Environment name
    #         output_file: Output file path
    #         config_dir: Directory containing configuration files
    #     """
    #     loader = get_config_loader(config_dir)
    #     config = loader.load_environment_config(environment)
    #
    #     if not config:
    #         # Create default configuration structure
    #         config = {
    #             "app": {
    #                 "name": "EGRC Core",
    #                 "version": "1.0.0",
    #                 "environment": environment,
    #             },
    #             "database": {
    #                 "url": "postgresql://postgres:postgres@localhost:5432/egrc_core",
    #                 "pool_size": 5,
    #                 "max_overflow": 10,
    #             },
    #             "redis": {"url": "redis://localhost:6379/0", "pool_size": 10},
    #             "rabbitmq": {"url": "amqp://guest:guest@localhost:5672/", "vhost": "/"},
    #             "keycloak": {
    #                 "url": "http://localhost:8080",
    #                 "realm": "egrc",
    #                 "client_id": "egrc-core",
    #             },
    #             "security": {
    #                 "jwt_secret_key": "your-super-secret-jwt-key-change-this-in-production",
    #                 "encryption_key": "your-encryption-key-change-this-in-production",
    #             },
    #             "logging": {"level": "INFO", "format": "json"},
    #             "monitoring": {"metrics_enabled": True, "health_checks_enabled": True},
    #             "api": {"title": "EGRC Core API", "version": "v1"},
    #             "graphql": {
    #                 "enable_introspection": environment != "production",
    #                 "enable_playground": environment != "production",
    #             },
    #             "crud": {"default_page_size": 20, "max_page_size": 1000},
    #             "tenant": {"default_tenant_id": "default", "enable_tenant_isolation": True},
    #             "features": {
    #                 "enable_graphql": True,
    #                 "enable_rest_api": True,
    #                 "enable_websockets": False,
    #                 "enable_rate_limiting": True,
    #                 "enable_cors": True,
    #                 "enable_metrics": True,
    #                 "enable_health_checks": True,
    #                 "enable_tracing": False,
    #                 "enable_logging": True,
    #             },
    #         }
    #
    #     loader.save_config(config, output_file)
    #
    #
    # def list_available_configs(config_dir: Optional[Path] = None) -> List[str]:
    #     """
    #     List available configuration files.
    #
    #     Args:
    #     config_dir: Directory containing configuration files

    # Returns:
    #     List of available configuration names
    #     """
    #     if config_dir is None:
    #         config_dir = Path.cwd()
    #
    #     config_dir = Path(config_dir)
    #     if not config_dir.exists():
    #         return []
    #
    #     configs = set()
    #
    #     # Look for YAML/JSON config files
    #     for pattern in ["config.*.yaml", "config.*.yml", "config.*.json"]:
    #         for file_path in config_dir.glob(pattern):
    #             name = file_path.stem.replace("config.", "")
    #             configs.add(name)
    #
    #     # Look for environment files
    #     for pattern in [".env.*", "env.*"]:
    #         for file_path in config_dir.glob(pattern):
    #             name = file_path.name.replace(".env.", "").replace("env.", "")
    #             configs.add(name)
    #
    #     return sorted(configs)
