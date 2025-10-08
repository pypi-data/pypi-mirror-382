"""
Cache models for EGRC Platform.

This module provides Pydantic models for cache configuration and statistics.
"""

from pydantic import BaseModel, Field


class CacheConfig(BaseModel):
    """Cache configuration model."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: str | None = Field(default=None, description="Redis password")
    max_connections: int = Field(default=10, description="Maximum connections")
    socket_timeout: int = Field(default=5, description="Socket timeout")
    socket_connect_timeout: int = Field(default=5, description="Socket connect timeout")
    retry_on_timeout: bool = Field(default=True, description="Retry on timeout")
    decode_responses: bool = Field(default=True, description="Decode responses")


class CacheStats(BaseModel):
    """Cache statistics model."""

    hits: int = Field(default=0, description="Cache hits")
    misses: int = Field(default=0, description="Cache misses")
    total_requests: int = Field(default=0, description="Total requests")
    hit_rate: float = Field(default=0.0, description="Hit rate percentage")
    memory_usage: int = Field(default=0, description="Memory usage in bytes")
    key_count: int = Field(default=0, description="Number of keys")
    expired_keys: int = Field(default=0, description="Number of expired keys")

    def calculate_hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100
