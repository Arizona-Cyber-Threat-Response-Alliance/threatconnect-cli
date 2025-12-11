"""Tests for cache utilities."""

import pytest
import time
from tc_tui.utils import TTLCache


def test_cache_set_and_get():
    """Test basic cache operations."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_expiration():
    """Test cache TTL expiration."""
    cache = TTLCache(ttl_seconds=1, max_size=10)

    cache.set("key1", "value1")
    time.sleep(1.1)  # Wait for expiration

    assert cache.get("key1") is None


def test_cache_max_size():
    """Test cache size limit."""
    cache = TTLCache(ttl_seconds=60, max_size=3)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    cache.set("key4", "value4")  # Should evict key1

    assert cache.get("key1") is None
    assert cache.get("key4") == "value4"


def test_cache_clear():
    """Test cache clearing."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.size() == 0


def test_cache_remove():
    """Test removing specific cache entry."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache.remove("key1")

    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"


def test_cache_cleanup_expired():
    """Test expired entry cleanup."""
    cache = TTLCache(ttl_seconds=1, max_size=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    time.sleep(1.1)  # Wait for expiration

    removed_count = cache.cleanup_expired()
    assert removed_count == 2
    assert cache.size() == 0
