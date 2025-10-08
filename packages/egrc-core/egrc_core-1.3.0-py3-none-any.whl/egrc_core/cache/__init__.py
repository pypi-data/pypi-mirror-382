"""
Caching module for EGRC Platform.

This module provides Redis-based caching functionality with decorators,
utilities, and comprehensive cache management for all EGRC services.
"""

from .decorators import cache_invalidate, cache_key, cache_result
from .models import CacheConfig, CacheStats
from .redis_client import RedisClient, get_redis_client
from .utils import (
    clear_cache_pattern,
    deserialize_data,
    generate_cache_key,
    get_cache_stats,
    serialize_data,
    warm_cache,
)


__all__ = [
    # Redis client
    "RedisClient",
    "get_redis_client",
    # Decorators
    "cache_result",
    "cache_invalidate",
    "cache_key",
    # Utilities
    "generate_cache_key",
    "serialize_data",
    "deserialize_data",
    "get_cache_stats",
    "clear_cache_pattern",
    "warm_cache",
    # Models
    "CacheConfig",
    "CacheStats",
]
