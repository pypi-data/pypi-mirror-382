"""
Cache utilities for EGRC Platform.

This module provides utility functions for cache operations including
key generation, data serialization, and cache management.
"""

import hashlib
import json
import pickle
from typing import Any


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from a prefix and arguments.

    Args:
        prefix: Cache key prefix
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key

    Returns:
        Generated cache key string
    """
    # Create a dictionary of all arguments
    key_data = {"prefix": prefix, "args": args, "kwargs": kwargs}

    # Serialize the data to a string
    key_string = json.dumps(key_data, sort_keys=True, default=str)

    # Generate a hash of the string
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    # Return the prefixed key
    return f"{prefix}:{key_hash}"


def serialize_data(data: Any) -> bytes:
    """Serialize data for caching.

    Args:
        data: Data to serialize

    Returns:
        Serialized data as bytes
    """
    try:
        # Try JSON serialization first (for simple data types)
        return json.dumps(data, default=str).encode("utf-8")
    except (TypeError, ValueError):
        # Fall back to pickle for complex objects
        return pickle.dumps(data)


def deserialize_data(data: bytes) -> Any:
    """Deserialize cached data.

    Args:
        data: Serialized data as bytes

    Returns:
        Deserialized data
    """
    try:
        # Try JSON deserialization first
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Fall back to pickle for complex objects
        return pickle.loads(data)


def is_cacheable(data: Any) -> bool:
    """Check if data can be cached.

    Args:
        data: Data to check

    Returns:
        True if data can be cached, False otherwise
    """
    try:
        # Try to serialize the data
        serialize_data(data)
        return True
    except (TypeError, ValueError, pickle.PicklingError):
        return False


def get_cache_ttl(ttl: int | float | None = None) -> int:
    """Get cache TTL (time to live) in seconds.

    Args:
        ttl: TTL value (if None, returns default)

    Returns:
        TTL in seconds
    """
    if ttl is None:
        from ..constants.constants import CacheConstants

        return CacheConstants.DEFAULT_TTL
    return int(ttl)


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics.

    Returns:
        Dictionary containing cache statistics
    """
    # This is a placeholder implementation
    # In a real implementation, you would query Redis for actual stats
    return {
        "hits": 0,
        "misses": 0,
        "total_requests": 0,
        "hit_rate": 0.0,
        "memory_usage": 0,
        "key_count": 0,
        "expired_keys": 0,
    }


def clear_cache_pattern(pattern: str) -> int:
    """Clear cache keys matching a pattern.

    Args:
        pattern: Pattern to match keys

    Returns:
        Number of keys cleared
    """
    # This is a placeholder implementation
    # In a real implementation, you would use Redis SCAN and DEL
    return 0


def warm_cache() -> dict[str, Any]:
    """Warm up the cache with frequently accessed data.

    Returns:
        Dictionary containing warm-up results
    """
    # This is a placeholder implementation
    # In a real implementation, you would preload common data
    return {"status": "completed", "keys_warmed": 0, "duration_ms": 0}
