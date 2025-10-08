"""
Security Cache System for EGRC Platform.

This module provides Redis-based caching for security operations including
JWT tokens, role-permission mappings, and JWKS keys for optimal performance.
"""

import json
import logging
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import redis
from redis.exceptions import RedisError

from ..config.settings import settings
from .exceptions import CacheError


logger = logging.getLogger(__name__)


class SecurityCache:
    """
    Redis-based cache for security operations with TTL support.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        key_prefix: str = "egrc_security:",
        default_ttl: int = 3600,
    ):
        """
        Initialize security cache.

        Args:
            redis_url: Redis connection URL
            key_prefix: Key prefix for all cache keys
            default_ttl: Default TTL in seconds
        """
        self.redis_url = redis_url or settings.redis.url
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self._redis_client: Optional[redis.Redis] = None

    @property
    def redis_client(self) -> redis.Redis:
        """
        Get Redis client instance.

        Returns:
            Redis client

        Raises:
            CacheError: If Redis connection fails
        """
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=False,  # We'll handle encoding ourselves
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                # Test connection
                self._redis_client.ping()
                logger.info("Connected to Redis for security cache")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise CacheError(f"Redis connection failed: {e}")

        return self._redis_client

    def _make_key(self, key: str) -> str:
        """
        Make full cache key with prefix.

        Args:
            key: Base key

        Returns:
            Full cache key
        """
        return f"{self.key_prefix}{key}"

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True,
    ) -> bool:
        """
        Set cache value.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (None for default)
            serialize: Whether to serialize the value

        Returns:
            True if successful, False otherwise
        """
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl

            if serialize:
                # Use pickle for complex objects, JSON for simple ones
                if isinstance(value, (dict, list, tuple, set)):
                    try:
                        serialized_value = json.dumps(value, default=str)
                    except (TypeError, ValueError):
                        serialized_value = pickle.dumps(value)
                else:
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = value

            result = self.redis_client.setex(full_key, ttl, serialized_value)
            return bool(result)

        except RedisError as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting cache key {key}: {e}")
            return False

    def get(
        self,
        key: str,
        deserialize: bool = True,
        default: Any = None,
    ) -> Any:
        """
        Get cache value.

        Args:
            key: Cache key
            deserialize: Whether to deserialize the value
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            full_key = self._make_key(key)
            value = self.redis_client.get(full_key)

            if value is None:
                return default

            if not deserialize:
                return value

            # Try to deserialize
            try:
                # First try JSON
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    # Then try pickle
                    return pickle.loads(value)
                except (pickle.PickleError, TypeError):
                    # Return as string if all else fails
                    return value.decode("utf-8") if isinstance(value, bytes) else value

        except RedisError as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error getting cache key {key}: {e}")
            return default

    def delete(self, key: str) -> bool:
        """
        Delete cache key.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            full_key = self._make_key(key)
            result = self.redis_client.delete(full_key)
            return bool(result)

        except RedisError as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting cache key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if cache key exists.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        try:
            full_key = self._make_key(key)
            return bool(self.redis_client.exists(full_key))

        except RedisError as e:
            logger.error(f"Failed to check cache key existence {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking cache key existence {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set TTL for existing key.

        Args:
            key: Cache key
            ttl: TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            full_key = self._make_key(key)
            return bool(self.redis_client.expire(full_key, ttl))

        except RedisError as e:
            logger.error(f"Failed to set TTL for cache key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting TTL for cache key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """
        Get TTL for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds (-1 if no TTL, -2 if key doesn't exist)
        """
        try:
            full_key = self._make_key(key)
            return self.redis_client.ttl(full_key)

        except RedisError as e:
            logger.error(f"Failed to get TTL for cache key {key}: {e}")
            return -2
        except Exception as e:
            logger.error(f"Unexpected error getting TTL for cache key {key}: {e}")
            return -2

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = self._make_key(pattern)
            keys = self.redis_client.keys(full_pattern)

            if keys:
                return self.redis_client.delete(*keys)
            return 0

        except RedisError as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error clearing cache pattern {pattern}: {e}")
            return 0

    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple cache values.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary mapping keys to values
        """
        result = {}
        for key in keys:
            result[key] = self.get(key)
        return result

    def set_multiple(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple cache values.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: TTL in seconds

        Returns:
            True if all successful, False otherwise
        """
        success = True
        for key, value in mapping.items():
            if not self.set(key, value, ttl):
                success = False
        return success


class TokenCache:
    """
    Specialized cache for JWT tokens with automatic expiration handling.
    """

    def __init__(self, cache: SecurityCache):
        """
        Initialize token cache.

        Args:
            cache: Security cache instance
        """
        self.cache = cache
        self.token_prefix = "token:"
        self.user_tokens_prefix = "user_tokens:"

    def cache_token(
        self,
        token: str,
        payload: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache JWT token with payload.

        Args:
            token: JWT token
            payload: Decoded token payload
            ttl: TTL in seconds (calculated from exp if not provided)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate TTL from token expiration
            if ttl is None:
                exp_timestamp = payload.get("exp")
                if exp_timestamp:
                    exp_time = datetime.fromtimestamp(exp_timestamp)
                    ttl = int((exp_time - datetime.utcnow()).total_seconds())
                    ttl = max(ttl, 0)  # Ensure non-negative
                else:
                    ttl = 3600  # Default 1 hour

            # Cache token
            token_hash = self._hash_token(token)
            cache_key = f"{self.token_prefix}{token_hash}"

            success = self.cache.set(cache_key, payload, ttl)

            if success:
                # Also cache user token mapping
                user_id = payload.get("sub")
                if user_id:
                    user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
                    user_tokens = self.cache.get(user_tokens_key, default=set())
                    if isinstance(user_tokens, list):
                        user_tokens = set(user_tokens)
                    user_tokens.add(token_hash)
                    self.cache.set(user_tokens_key, list(user_tokens), ttl)

            return success

        except Exception as e:
            logger.error(f"Failed to cache token: {e}")
            return False

    def get_cached_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get cached token payload.

        Args:
            token: JWT token

        Returns:
            Cached payload or None
        """
        try:
            token_hash = self._hash_token(token)
            cache_key = f"{self.token_prefix}{token_hash}"
            return self.cache.get(cache_key)

        except Exception as e:
            logger.error(f"Failed to get cached token: {e}")
            return None

    def invalidate_token(self, token: str) -> bool:
        """
        Invalidate cached token.

        Args:
            token: JWT token

        Returns:
            True if successful, False otherwise
        """
        try:
            token_hash = self._hash_token(token)
            cache_key = f"{self.token_prefix}{token_hash}"

            # Get payload to find user_id
            payload = self.cache.get(cache_key)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    # Remove from user tokens
                    user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
                    user_tokens = self.cache.get(user_tokens_key, default=set())
                    if isinstance(user_tokens, list):
                        user_tokens = set(user_tokens)
                    user_tokens.discard(token_hash)
                    self.cache.set(user_tokens_key, list(user_tokens))

            return self.cache.delete(cache_key)

        except Exception as e:
            logger.error(f"Failed to invalidate token: {e}")
            return False

    def invalidate_user_tokens(self, user_id: str) -> int:
        """
        Invalidate all tokens for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of tokens invalidated
        """
        try:
            user_tokens_key = f"{self.user_tokens_prefix}{user_id}"
            user_tokens = self.cache.get(user_tokens_key, default=set())

            if isinstance(user_tokens, list):
                user_tokens = set(user_tokens)

            invalidated = 0
            for token_hash in user_tokens:
                cache_key = f"{self.token_prefix}{token_hash}"
                if self.cache.delete(cache_key):
                    invalidated += 1

            # Clear user tokens mapping
            self.cache.delete(user_tokens_key)

            return invalidated

        except Exception as e:
            logger.error(f"Failed to invalidate user tokens: {e}")
            return 0

    def _hash_token(self, token: str) -> str:
        """Create hash of token for storage."""
        import hashlib

        return hashlib.sha256(token.encode()).hexdigest()


class PermissionCache:
    """
    Specialized cache for role-permission mappings.
    """

    def __init__(self, cache: SecurityCache):
        """
        Initialize permission cache.

        Args:
            cache: Security cache instance
        """
        self.cache = cache
        self.role_permissions_prefix = "role_permissions:"
        self.user_permissions_prefix = "user_permissions:"

    def cache_role_permissions(
        self,
        tenant_id: str,
        role_permissions: Dict[str, Set[str]],
        ttl: int = 3600,
    ) -> bool:
        """
        Cache role-permission mappings.

        Args:
            tenant_id: Tenant identifier
            role_permissions: Role to permissions mapping
            ttl: TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert sets to lists for JSON serialization
            serializable_mapping = {
                role: list(permissions)
                for role, permissions in role_permissions.items()
            }

            cache_key = f"{self.role_permissions_prefix}{tenant_id}"
            return self.cache.set(cache_key, serializable_mapping, ttl)

        except Exception as e:
            logger.error(f"Failed to cache role permissions: {e}")
            return False

    def get_cached_role_permissions(
        self, tenant_id: str
    ) -> Optional[Dict[str, Set[str]]]:
        """
        Get cached role-permission mappings.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Role-permission mapping or None
        """
        try:
            cache_key = f"{self.role_permissions_prefix}{tenant_id}"
            mapping = self.cache.get(cache_key)

            if mapping:
                # Convert lists back to sets
                return {role: set(permissions) for role, permissions in mapping.items()}

            return None

        except Exception as e:
            logger.error(f"Failed to get cached role permissions: {e}")
            return None

    def cache_user_permissions(
        self,
        user_id: str,
        tenant_id: str,
        permissions: Set[str],
        ttl: int = 1800,
    ) -> bool:
        """
        Cache user permissions.

        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            permissions: Set of permissions
            ttl: TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = f"{self.user_permissions_prefix}{user_id}:{tenant_id}"
            return self.cache.set(cache_key, list(permissions), ttl)

        except Exception as e:
            logger.error(f"Failed to cache user permissions: {e}")
            return False

    def get_cached_user_permissions(
        self,
        user_id: str,
        tenant_id: str,
    ) -> Optional[Set[str]]:
        """
        Get cached user permissions.

        Args:
            user_id: User identifier
            tenant_id: Tenant identifier

        Returns:
            Set of permissions or None
        """
        try:
            cache_key = f"{self.user_permissions_prefix}{user_id}:{tenant_id}"
            permissions = self.cache.get(cache_key)

            if permissions:
                return set(permissions)

            return None

        except Exception as e:
            logger.error(f"Failed to get cached user permissions: {e}")
            return None

    def invalidate_user_permissions(self, user_id: str, tenant_id: str) -> bool:
        """
        Invalidate cached user permissions.

        Args:
            user_id: User identifier
            tenant_id: Tenant identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = f"{self.user_permissions_prefix}{user_id}:{tenant_id}"
            return self.cache.delete(cache_key)

        except Exception as e:
            logger.error(f"Failed to invalidate user permissions: {e}")
            return False

    def invalidate_tenant_permissions(self, tenant_id: str) -> int:
        """
        Invalidate all permission caches for a tenant.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Number of keys deleted
        """
        try:
            # Clear role permissions
            role_perms_key = f"{self.role_permissions_prefix}{tenant_id}"
            self.cache.delete(role_perms_key)

            # Clear user permissions for this tenant
            pattern = f"{self.user_permissions_prefix}*:{tenant_id}"
            return self.cache.clear_pattern(pattern)

        except Exception as e:
            logger.error(f"Failed to invalidate tenant permissions: {e}")
            return 0


# Global cache instances
_security_cache: Optional[SecurityCache] = None
_token_cache: Optional[TokenCache] = None
_permission_cache: Optional[PermissionCache] = None


def get_security_cache() -> SecurityCache:
    """Get global security cache instance."""
    global _security_cache
    if _security_cache is None:
        _security_cache = SecurityCache()
    return _security_cache


def get_token_cache() -> TokenCache:
    """Get global token cache instance."""
    global _token_cache
    if _token_cache is None:
        _token_cache = TokenCache(get_security_cache())
    return _token_cache


def get_permission_cache() -> PermissionCache:
    """Get global permission cache instance."""
    global _permission_cache
    if _permission_cache is None:
        _permission_cache = PermissionCache(get_security_cache())
    return _permission_cache
