"""Caching implementation for togglr-sdk-python."""

import time
from typing import Any, Optional, Tuple
from dataclasses import dataclass, field
from cachetools import TTLCache


@dataclass
class CacheEntry:
    """A cache entry containing evaluation result."""
    
    value: str
    enabled: bool
    found: bool
    timestamp: float = field(default_factory=time.time)
    
    def is_expired(self, ttl: float) -> bool:
        """Check if the entry is expired."""
        return time.time() - self.timestamp > ttl


class LRUCache:
    """LRU cache with TTL for feature evaluation results."""
    
    def __init__(self, max_size: int, ttl_seconds: float):
        """Initialize the cache.
        
        Args:
            max_size: Maximum number of entries
            ttl_seconds: Time to live in seconds
        """
        self._cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Tuple[Optional[CacheEntry], bool]:
        """Get an entry from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Tuple of (entry, hit) where hit indicates if the key was found
        """
        entry = self._cache.get(key)
        if entry is None:
            return None, False
        
        # Check if expired manually (TTLCache handles this, but we do it for safety)
        if entry.is_expired(self._ttl):
            self._cache.pop(key, None)
            return None, False
        
        return entry, True
    
    def set(self, key: str, value: str, enabled: bool, found: bool) -> None:
        """Set an entry in the cache.
        
        Args:
            key: Cache key
            value: Feature value
            enabled: Whether feature is enabled
            found: Whether feature was found
        """
        entry = CacheEntry(value=value, enabled=enabled, found=found)
        self._cache[key] = entry
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get the current cache size."""
        return len(self._cache)
    
    def max_size(self) -> int:
        """Get the maximum cache size."""
        return self._cache.maxsize
