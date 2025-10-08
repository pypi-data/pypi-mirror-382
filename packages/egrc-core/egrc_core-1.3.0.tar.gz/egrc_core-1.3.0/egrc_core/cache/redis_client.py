"""
Redis client for EGRC Platform caching.

This module provides a production-ready Redis client with connection pooling,
error handling, and comprehensive caching operations.
"""

import json
import pickle
from contextlib import asynccontextmanager
from typing import Any

import redis
import redis.asyncio as aioredis

from ..config.settings import Settings
from ..constants.constants import CacheConstants
from ..exceptions.exceptions import CacheException, ConfigurationError
from ..logging.utils import get_logger


logger = get_logger(__name__)


class RedisClient:
    """Production-ready Redis client with comprehensive caching operations."""

    def __init__(self, settings: Settings | None = None):
        """Initialize Redis client.

        Args:
            settings: Application settings instance
        """
        self.settings = settings or Settings()
        self._sync_client: redis.Redis | None = None
        self._async_client: aioredis.Redis | None = None
        self._connection_pool: redis.ConnectionPool | None = None
        self._async_connection_pool: aioredis.ConnectionPool | None = None

        self._initialize_connection_pools()

    def _initialize_connection_pools(self) -> None:
        """Initialize Redis connection pools."""
        try:
            redis_url = self.settings.cache_url
            if not redis_url:
                raise ConfigurationError("Redis URL not configured")

            # Parse Redis URL
            from urllib.parse import urlparse

            parsed = urlparse(redis_url)

            # Create connection pool for sync client
            self._connection_pool = redis.ConnectionPool(
                host=parsed.hostname or "localhost",
                port=parsed.port or 6379,
                password=parsed.password,
                db=int(parsed.path.lstrip("/")) if parsed.path else 0,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )

            # Create async connection pool
            self._async_connection_pool = aioredis.ConnectionPool.from_url(
                redis_url,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )

            logger.info("Initialized Redis connection pools")

        except Exception as e:
            logger.error(f"Failed to initialize Redis connection pools: {e}")
            raise CacheException(f"Redis initialization failed: {e}")

    @property
    def sync_client(self) -> redis.Redis:
        """Get synchronous Redis client."""
        if self._sync_client is None:
            self._sync_client = redis.Redis(connection_pool=self._connection_pool)
        return self._sync_client

    @property
    def async_client(self) -> aioredis.Redis:
        """Get asynchronous Redis client."""
        if self._async_client is None:
            self._async_client = aioredis.Redis(
                connection_pool=self._async_connection_pool
            )
        return self._async_client

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            value = self.sync_client.get(key)
            if value is None:
                return default

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)

        except Exception as e:
            logger.warning(f"Failed to get cache key {key}: {e}")
            return default

    async def aget(self, key: str, default: Any = None) -> Any:
        """Get value from cache asynchronously.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            value = await self.async_client.get(key)
            if value is None:
                return default

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)

        except Exception as e:
            logger.warning(f"Failed to get cache key {key}: {e}")
            return default

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to serialize as JSON first, fallback to pickle
            try:
                serialized = json.dumps(value, default=str)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)

            if ttl is None:
                ttl = CacheConstants.DEFAULT_TTL

            result = self.sync_client.setex(key, ttl, serialized)
            return bool(result)

        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    async def aset(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache asynchronously.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to serialize as JSON first, fallback to pickle
            try:
                serialized = json.dumps(value, default=str)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)

            if ttl is None:
                ttl = CacheConstants.DEFAULT_TTL

            result = await self.async_client.setex(key, ttl, serialized)
            return bool(result)

        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            result = self.sync_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    async def adelete(self, key: str) -> bool:
        """Delete key from cache asynchronously.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            result = await self.async_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(self.sync_client.exists(key))
        except Exception as e:
            logger.warning(f"Failed to check cache key {key}: {e}")
            return False

    async def aexists(self, key: str) -> bool:
        """Check if key exists in cache asynchronously.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(await self.async_client.exists(key))
        except Exception as e:
            logger.warning(f"Failed to check cache key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(self.sync_client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Failed to set expiration for key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get time to live for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            return self.sync_client.ttl(key)
        except Exception as e:
            logger.warning(f"Failed to get TTL for key {key}: {e}")
            return -2

    def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern.

        Args:
            pattern: Key pattern (supports wildcards)

        Returns:
            List of matching keys
        """
        try:
            return [key.decode("utf-8") for key in self.sync_client.keys(pattern)]
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern.

        Args:
            pattern: Key pattern to clear

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.keys(pattern)
            if keys:
                return self.sync_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear pattern {pattern}: {e}")
            return 0

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value after increment
        """
        try:
            return self.sync_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment key {key}: {e}")
            return 0

    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to decrement by

        Returns:
            New value after decrement
        """
        try:
            return self.sync_client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Failed to decrement key {key}: {e}")
            return 0

    def hash_set(self, name: str, mapping: dict[str, Any]) -> bool:
        """Set hash fields in cache.

        Args:
            name: Hash name
            mapping: Dictionary of field-value pairs

        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize values
            serialized_mapping = {}
            for field, value in mapping.items():
                try:
                    serialized_mapping[field] = json.dumps(value, default=str)
                except (TypeError, ValueError):
                    serialized_mapping[field] = pickle.dumps(value)

            return bool(self.sync_client.hset(name, mapping=serialized_mapping))
        except Exception as e:
            logger.error(f"Failed to set hash {name}: {e}")
            return False

    def hash_get(self, name: str, field: str, default: Any = None) -> Any:
        """Get hash field value from cache.

        Args:
            name: Hash name
            field: Field name
            default: Default value if field not found

        Returns:
            Field value or default
        """
        try:
            value = self.sync_client.hget(name, field)
            if value is None:
                return default

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)

        except Exception as e:
            logger.warning(f"Failed to get hash field {name}.{field}: {e}")
            return default

    def hash_get_all(self, name: str) -> dict[str, Any]:
        """Get all hash fields from cache.

        Args:
            name: Hash name

        Returns:
            Dictionary of all field-value pairs
        """
        try:
            hash_data = self.sync_client.hgetall(name)
            result = {}

            for field, value in hash_data.items():
                field_str = field.decode("utf-8") if isinstance(field, bytes) else field
                try:
                    result[field_str] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field_str] = pickle.loads(value)

            return result
        except Exception as e:
            logger.error(f"Failed to get all hash fields for {name}: {e}")
            return {}

    def list_push(self, name: str, *values: Any) -> int:
        """Push values to list in cache.

        Args:
            name: List name
            *values: Values to push

        Returns:
            New length of list
        """
        try:
            # Serialize values
            serialized_values = []
            for value in values:
                try:
                    serialized_values.append(json.dumps(value, default=str))
                except (TypeError, ValueError):
                    serialized_values.append(pickle.dumps(value))

            return self.sync_client.lpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Failed to push to list {name}: {e}")
            return 0

    def list_pop(self, name: str) -> Any:
        """Pop value from list in cache.

        Args:
            name: List name

        Returns:
            Popped value or None
        """
        try:
            value = self.sync_client.lpop(name)
            if value is None:
                return None

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)

        except Exception as e:
            logger.error(f"Failed to pop from list {name}: {e}")
            return None

    def get_stats(self) -> dict[str, Any]:
        """Get Redis server statistics.

        Returns:
            Dictionary of Redis statistics
        """
        try:
            info = self.sync_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {}

    def health_check(self) -> bool:
        """Check Redis connection health.

        Returns:
            True if Redis is healthy, False otherwise
        """
        try:
            self.sync_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    def close(self) -> None:
        """Close Redis connections."""
        try:
            if self._sync_client:
                self._sync_client.close()
            if self._connection_pool:
                self._connection_pool.disconnect()
            logger.info("Closed Redis connections")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")

    async def aclose(self) -> None:
        """Close async Redis connections."""
        try:
            if self._async_client:
                await self._async_client.close()
            if self._async_connection_pool:
                await self._async_connection_pool.disconnect()
            logger.info("Closed async Redis connections")
        except Exception as e:
            logger.error(f"Error closing async Redis connections: {e}")


# Global Redis client instance
_redis_client: RedisClient | None = None


def get_redis_client() -> RedisClient:
    """Get global Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


@asynccontextmanager
async def redis_context():
    """Context manager for Redis operations."""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()
