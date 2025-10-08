"""
Caching decorators for EGRC Platform.

This module provides decorators for automatic caching of function results,
cache invalidation, and cache key generation.
"""

import functools
import hashlib
import inspect
from collections.abc import Callable
from datetime import datetime
from typing import Any

from ..constants.constants import CacheConstants
from ..logging.utils import get_logger
from .redis_client import get_redis_client


logger = get_logger(__name__)


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Generated cache key
    """
    # Create a string representation of arguments
    key_parts = []

    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif hasattr(arg, "__dict__"):
            key_parts.append(str(sorted(arg.__dict__.items())))
        else:
            key_parts.append(str(arg))

    # Add keyword arguments
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}:{value}")
        elif hasattr(value, "__dict__"):
            key_parts.append(f"{key}:{str(sorted(value.__dict__.items()))}")
        else:
            key_parts.append(f"{key}:{str(value)}")

    # Create hash of the key parts
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(
    ttl: int | None = None,
    key_prefix: str = "",
    key_suffix: str = "",
    condition: Callable | None = None,
    serialize: bool = True,
    cache_none: bool = False,
) -> Callable:
    """Decorator to cache function results.

    Args:
        ttl: Time to live in seconds (default: CacheConstants.DEFAULT_TTL)
        key_prefix: Prefix for cache key
        key_suffix: Suffix for cache key
        condition: Function to determine if result should be cached
        serialize: Whether to serialize the result
        cache_none: Whether to cache None results

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            func_key = f"{key_prefix}{func.__module__}.{func.__name__}{key_suffix}"
            arg_key = cache_key(*args, **kwargs)
            full_key = f"{func_key}:{arg_key}"

            # Get Redis client
            redis_client = get_redis_client()

            # Try to get from cache
            try:
                cached_result = redis_client.get(full_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {full_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for key {full_key}: {e}")

            # Execute function
            logger.debug(f"Cache miss for key: {full_key}")
            result = func(*args, **kwargs)

            # Check if we should cache the result
            should_cache = True
            if condition is not None:
                should_cache = condition(result)
            elif not cache_none and result is None:
                should_cache = False

            if should_cache:
                try:
                    # Set cache with TTL
                    cache_ttl = ttl or CacheConstants.DEFAULT_TTL
                    redis_client.set(full_key, result, ttl=cache_ttl)
                    logger.debug(f"Cached result for key: {full_key}")
                except Exception as e:
                    logger.warning(f"Cache set failed for key {full_key}: {e}")

            return result

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            func_key = f"{key_prefix}{func.__module__}.{func.__name__}{key_suffix}"
            arg_key = cache_key(*args, **kwargs)
            full_key = f"{func_key}:{arg_key}"

            # Get Redis client
            redis_client = get_redis_client()

            # Try to get from cache
            try:
                cached_result = await redis_client.aget(full_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {full_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for key {full_key}: {e}")

            # Execute function
            logger.debug(f"Cache miss for key: {full_key}")
            result = await func(*args, **kwargs)

            # Check if we should cache the result
            should_cache = True
            if condition is not None:
                should_cache = condition(result)
            elif not cache_none and result is None:
                should_cache = False

            if should_cache:
                try:
                    # Set cache with TTL
                    cache_ttl = ttl or CacheConstants.DEFAULT_TTL
                    await redis_client.aset(full_key, result, ttl=cache_ttl)
                    logger.debug(f"Cached result for key: {full_key}")
                except Exception as e:
                    logger.warning(f"Cache set failed for key {full_key}: {e}")

            return result

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def cache_invalidate(
    key_pattern: str,
    key_prefix: str = "",
    key_suffix: str = "",
) -> Callable:
    """Decorator to invalidate cache entries.

    Args:
        key_pattern: Pattern to match cache keys for invalidation
        key_prefix: Prefix for cache key
        key_suffix: Suffix for cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Execute function first
            result = func(*args, **kwargs)

            # Generate cache key pattern
            func_key = f"{key_prefix}{func.__module__}.{func.__name__}{key_suffix}"
            full_pattern = f"{func_key}:{key_pattern}"

            # Get Redis client and clear cache
            try:
                redis_client = get_redis_client()
                deleted_count = redis_client.clear_pattern(full_pattern)
                logger.info(
                    f"Invalidated {deleted_count} cache entries matching "
                    f"pattern: {full_pattern}"
                )
            except Exception as e:
                logger.warning(
                    f"Cache invalidation failed for pattern {full_pattern}: " f"{e}"
                )

            return result

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Execute function first
            result = await func(*args, **kwargs)

            # Generate cache key pattern
            func_key = f"{key_prefix}{func.__module__}.{func.__name__}{key_suffix}"
            full_pattern = f"{func_key}:{key_pattern}"

            # Get Redis client and clear cache
            try:
                redis_client = get_redis_client()
                deleted_count = redis_client.clear_pattern(full_pattern)
                logger.info(
                    f"Invalidated {deleted_count} cache entries matching "
                    f"pattern: {full_pattern}"
                )
            except Exception as e:
                logger.warning(
                    f"Cache invalidation failed for pattern {full_pattern}: " f"{e}"
                )

            return result

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def cache_memoize(
    ttl: int | None = None,
    max_size: int = 1000,
    key_prefix: str = "",
) -> Callable:
    """Decorator for memoization with size limit and TTL.

    Args:
        ttl: Time to live in seconds
        max_size: Maximum number of cached items
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key = f"{key_prefix}{func.__name__}:{cache_key(*args, **kwargs)}"
            current_time = datetime.now()

            # Check if key exists and is not expired
            if key in cache:
                if ttl is None or (current_time - cache_times[key]).seconds < ttl:
                    logger.debug(f"Memoization hit for key: {key}")
                    return cache[key]
                else:
                    # Remove expired entry
                    del cache[key]
                    del cache_times[key]

            # Check cache size limit
            if len(cache) >= max_size:
                # Remove oldest entry
                oldest_key = min(cache_times.keys(), key=lambda k: cache_times[k])
                del cache[oldest_key]
                del cache_times[oldest_key]

            # Execute function and cache result
            logger.debug(f"Memoization miss for key: {key}")
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = current_time

            return result

        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear() or cache_times.clear()
        wrapper.cache_info = lambda: {
            "hits": getattr(wrapper, "_hits", 0),
            "misses": getattr(wrapper, "_misses", 0),
            "current_size": len(cache),
            "max_size": max_size,
        }

        return wrapper

    return decorator


def cache_conditional(
    condition: Callable[[Any], bool],
    ttl: int | None = None,
    key_prefix: str = "",
) -> Callable:
    """Decorator to cache results based on a condition.

    Args:
        condition: Function that determines if result should be cached
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            func_key = f"{key_prefix}{func.__module__}.{func.__name__}"
            arg_key = cache_key(*args, **kwargs)
            full_key = f"{func_key}:{arg_key}"

            # Get Redis client
            redis_client = get_redis_client()

            # Try to get from cache
            try:
                cached_result = redis_client.get(full_key)
                if cached_result is not None:
                    logger.debug(f"Conditional cache hit for key: {full_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Conditional cache get failed for key {full_key}: {e}")

            # Execute function
            logger.debug(f"Conditional cache miss for key: {full_key}")
            result = func(*args, **kwargs)

            # Check condition and cache if needed
            if condition(result):
                try:
                    cache_ttl = ttl or CacheConstants.DEFAULT_TTL
                    redis_client.set(full_key, result, ttl=cache_ttl)
                    logger.debug(f"Conditionally cached result for key: {full_key}")
                except Exception as e:
                    logger.warning(
                        f"Conditional cache set failed for key {full_key}: {e}"
                    )

            return result

        return wrapper

    return decorator


def cache_with_fallback(
    fallback_func: Callable,
    ttl: int | None = None,
    key_prefix: str = "",
) -> Callable:
    """Decorator to use fallback function when cache fails.

    Args:
        fallback_func: Function to call when cache operations fail
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            func_key = f"{key_prefix}{func.__module__}.{func.__name__}"
            arg_key = cache_key(*args, **kwargs)
            full_key = f"{func_key}:{arg_key}"

            # Get Redis client
            redis_client = get_redis_client()

            # Try to get from cache
            try:
                cached_result = redis_client.get(full_key)
                if cached_result is not None:
                    logger.debug(f"Fallback cache hit for key: {full_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Fallback cache get failed for key {full_key}: {e}")
                return fallback_func(*args, **kwargs)

            # Execute function
            logger.debug(f"Fallback cache miss for key: {full_key}")
            result = func(*args, **kwargs)

            # Try to cache result
            try:
                cache_ttl = ttl or CacheConstants.DEFAULT_TTL
                redis_client.set(full_key, result, ttl=cache_ttl)
                logger.debug(f"Fallback cached result for key: {full_key}")
            except Exception as e:
                logger.warning(f"Fallback cache set failed for key {full_key}: {e}")
                # Don't return fallback here, return the actual result

            return result

        return wrapper

    return decorator
