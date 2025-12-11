"""Caching utilities."""

import time
from typing import Any, Optional, Tuple
from collections import OrderedDict


class TTLCache:
    """Simple time-to-live cache."""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize TTL cache.

        Args:
            ttl_seconds: Time to live in seconds
            max_size: Maximum number of entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest entry if at max size
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def remove(self, key: str) -> None:
        """Remove specific cache entry."""
        if key in self._cache:
            del self._cache[key]

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
