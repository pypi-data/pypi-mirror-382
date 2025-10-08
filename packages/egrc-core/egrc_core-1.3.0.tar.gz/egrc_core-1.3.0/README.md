# EGRC Core

EGRC Core is a comprehensive, production-grade foundation service for the Enterprise Governance, Risk, and Compliance (EGRC) platform. It provides shared functionality, utilities, and infrastructure components that other microservices can use to build robust, scalable, and maintainable applications.

## Features

- **Multi-Tenant Database Management**: Automatic tenant database creation and management
- **Comprehensive Caching**: Redis-based caching with decorators and utilities
- **Security**: Encryption, JWT handling, input validation, and security middleware
- **Monitoring**: Metrics collection, health checks, and observability
- **File Handling**: Cloud storage integration and file processing utilities
- **Inter-Service Communication**: HTTP clients with retry and circuit breaker patterns
- **Message Queues**: RabbitMQ and Kafka integration for event-driven architecture
- **Testing**: Comprehensive testing utilities and fixtures
- **GraphQL Support**: Complete GraphQL implementation with filtering, sorting, and pagination
- **Audit System**: Comprehensive audit logging and event tracking

## Installation

```bash
pip install egrc-core
```

## Quick Start

```python
from egrc_core import get_service_factory, Settings

# Initialize with settings
settings = Settings(
    database_url="postgresql://user:pass@localhost:5432/mydb",
    redis_url="redis://localhost:6379/0",
)

# Get service factory
factory = get_service_factory(settings)

# Use services
tenant_manager = factory.get_tenant_manager()
redis_client = factory.get_redis_client()
```

## Documentation

For detailed usage instructions, see the [Usage Guide](docs/EGRC_CORE_USAGE_GUIDE.md).

## License

MIT License - see LICENSE file for details.
