"""
Service Factory for EGRC Platform.

This module provides a centralized factory for creating and managing
all EGRC services and their dependencies.
"""

from functools import lru_cache
from typing import Any, TypeVar

from .cache.redis_client import RedisClient
from .config.settings import Settings
from .database.tenant_manager import TenantDatabaseManager
from .http.client import HTTPClient
from .logging.utils import get_logger
from .messaging.kafka_client import KafkaClient
from .messaging.rabbitmq_client import RabbitMQClient
from .monitoring.health_checks import HealthChecker
from .monitoring.metrics import MetricsCollector
from .security.encryption import EncryptionService
from .storage.file_handler import FileHandler


logger = get_logger(__name__)

T = TypeVar("T")


class ServiceFactory:
    """Factory for creating and managing EGRC services."""

    def __init__(self, settings: Settings | None = None):
        """Initialize service factory.

        Args:
            settings: Application settings instance
        """
        self.settings = settings or Settings()
        self._services: dict[str, Any] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all services."""
        if self._initialized:
            return

        try:
            # Initialize core services
            self._initialize_database()
            self._initialize_cache()
            self._initialize_messaging()
            self._initialize_security()
            self._initialize_monitoring()
            self._initialize_storage()
            self._initialize_http()

            self._initialized = True
            logger.info("Service factory initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize service factory: {e}")
            raise

    def _initialize_database(self) -> None:
        """Initialize database services."""
        try:
            tenant_manager = TenantDatabaseManager(self.settings)
            self._services["tenant_manager"] = tenant_manager
            logger.info("Database services initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database services: {e}")
            raise

    def _initialize_cache(self) -> None:
        """Initialize cache services."""
        try:
            redis_client = RedisClient(self.settings)
            self._services["redis_client"] = redis_client
            logger.info("Cache services initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize cache services: {e}")
            # Cache is optional, don't raise

    def _initialize_messaging(self) -> None:
        """Initialize messaging services."""
        try:
            if self.settings.rabbitmq_url:
                rabbitmq_client = RabbitMQClient(self.settings)
                self._services["rabbitmq_client"] = rabbitmq_client
                logger.info("RabbitMQ client initialized")

            if self.settings.kafka_bootstrap_servers:
                kafka_client = KafkaClient(self.settings)
                self._services["kafka_client"] = kafka_client
                logger.info("Kafka client initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize messaging services: {e}")
            # Messaging is optional, don't raise

    def _initialize_security(self) -> None:
        """Initialize security services."""
        try:
            encryption_service = EncryptionService(self.settings)
            self._services["encryption_service"] = encryption_service
            logger.info("Security services initialized")
        except Exception as e:
            logger.error(f"Failed to initialize security services: {e}")
            raise

    def _initialize_monitoring(self) -> None:
        """Initialize monitoring services."""
        try:
            metrics_collector = MetricsCollector(self.settings)
            self._services["metrics_collector"] = metrics_collector

            health_checker = HealthChecker(self.settings)
            self._services["health_checker"] = health_checker
            logger.info("Monitoring services initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize monitoring services: {e}")
            # Monitoring is optional, don't raise

    def _initialize_storage(self) -> None:
        """Initialize storage services."""
        try:
            file_handler = FileHandler(self.settings)
            self._services["file_handler"] = file_handler
            logger.info("Storage services initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize storage services: {e}")
            # Storage is optional, don't raise

    def _initialize_http(self) -> None:
        """Initialize HTTP services."""
        try:
            http_client = HTTPClient(self.settings)
            self._services["http_client"] = http_client
            logger.info("HTTP services initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize HTTP services: {e}")
            # HTTP client is optional, don't raise

    def get_service(self, service_name: str) -> Any:
        """Get a service by name.

        Args:
            service_name: Name of the service

        Returns:
            Service instance

        Raises:
            ValueError: If service is not found
        """
        if not self._initialized:
            self.initialize()

        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found")

        return self._services[service_name]

    def get_tenant_manager(self) -> TenantDatabaseManager:
        """Get tenant database manager."""
        return self.get_service("tenant_manager")

    def get_redis_client(self) -> RedisClient | None:
        """Get Redis client."""
        return self._services.get("redis_client")

    def get_rabbitmq_client(self) -> RabbitMQClient | None:
        """Get RabbitMQ client."""
        return self._services.get("rabbitmq_client")

    def get_kafka_client(self) -> KafkaClient | None:
        """Get Kafka client."""
        return self._services.get("kafka_client")

    def get_encryption_service(self) -> EncryptionService:
        """Get encryption service."""
        return self.get_service("encryption_service")

    def get_metrics_collector(self) -> MetricsCollector | None:
        """Get metrics collector."""
        return self._services.get("metrics_collector")

    def get_health_checker(self) -> HealthChecker | None:
        """Get health checker."""
        return self._services.get("health_checker")

    def get_file_handler(self) -> FileHandler | None:
        """Get file handler."""
        return self._services.get("file_handler")

    def get_http_client(self) -> HTTPClient | None:
        """Get HTTP client."""
        return self._services.get("http_client")

    def health_check(self) -> dict[str, Any]:
        """Perform health check on all services.

        Returns:
            Dictionary with health status of all services
        """
        health_status = {"factory_initialized": self._initialized, "services": {}}

        for service_name, service in self._services.items():
            try:
                if hasattr(service, "health_check"):
                    health_status["services"][service_name] = service.health_check()
                else:
                    health_status["services"][service_name] = True
            except Exception as e:
                health_status["services"][service_name] = False
                logger.warning(f"Health check failed for {service_name}: {e}")

        return health_status

    def shutdown(self) -> None:
        """Shutdown all services."""
        logger.info("Shutting down service factory...")

        for service_name, service in self._services.items():
            try:
                if hasattr(service, "close"):
                    service.close()
                elif hasattr(service, "shutdown"):
                    service.shutdown()
                logger.info(f"Shutdown {service_name}")
            except Exception as e:
                logger.error(f"Error shutting down {service_name}: {e}")

        self._services.clear()
        self._initialized = False
        logger.info("Service factory shutdown complete")


# Global service factory instance
_service_factory: ServiceFactory | None = None


@lru_cache(maxsize=1)
def get_service_factory(settings: Settings | None = None) -> ServiceFactory:
    """Get global service factory instance.

    Args:
        settings: Application settings instance

    Returns:
        Service factory instance
    """
    global _service_factory
    if _service_factory is None:
        _service_factory = ServiceFactory(settings)
        _service_factory.initialize()
    return _service_factory


def get_service(service_name: str) -> Any:
    """Get a service by name from the global factory.

    Args:
        service_name: Name of the service

    Returns:
        Service instance
    """
    factory = get_service_factory()
    return factory.get_service(service_name)


# Convenience functions for common services
def get_tenant_manager() -> TenantDatabaseManager:
    """Get tenant database manager."""
    return get_service_factory().get_tenant_manager()


def get_redis_client() -> RedisClient | None:
    """Get Redis client."""
    return get_service_factory().get_redis_client()


def get_rabbitmq_client() -> RabbitMQClient | None:
    """Get RabbitMQ client."""
    return get_service_factory().get_rabbitmq_client()


def get_kafka_client() -> KafkaClient | None:
    """Get Kafka client."""
    return get_service_factory().get_kafka_client()


def get_encryption_service() -> EncryptionService:
    """Get encryption service."""
    return get_service_factory().get_encryption_service()


def get_metrics_collector() -> MetricsCollector | None:
    """Get metrics collector."""
    return get_service_factory().get_metrics_collector()


def get_health_checker() -> HealthChecker | None:
    """Get health checker."""
    return get_service_factory().get_health_checker()


def get_file_handler() -> FileHandler | None:
    """Get file handler."""
    return get_service_factory().get_file_handler()


def get_http_client() -> HTTPClient | None:
    """Get HTTP client."""
    return get_service_factory().get_http_client()


def health_check() -> dict[str, Any]:
    """Perform health check on all services."""
    return get_service_factory().health_check()


def shutdown_services() -> None:
    """Shutdown all services."""
    global _service_factory
    if _service_factory:
        _service_factory.shutdown()
        _service_factory = None
