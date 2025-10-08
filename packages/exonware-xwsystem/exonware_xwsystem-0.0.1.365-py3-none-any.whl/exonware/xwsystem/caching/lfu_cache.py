"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

LFU (Least Frequently Used) Cache implementation with thread-safety and async support.
"""

import asyncio
import threading
import time
from typing import Any, Dict, Optional, Hashable

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.caching.lfu_cache")


class LFUCache:
    """
    Thread-safe LFU (Least Frequently Used) Cache.
    
    Features:
    - O(1) get and put operations
    - Thread-safe operations
    - Frequency-based eviction
    - Statistics tracking
    """
    
    def __init__(self, capacity: int = 128, name: Optional[str] = None):
        """Initialize LFU cache."""
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.name = name or f"LFUCache-{id(self)}"
        
        self._cache: Dict[Hashable, Any] = {}
        self._frequencies: Dict[Hashable, int] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        logger.debug(f"LFU cache {self.name} initialized with capacity {capacity}")
    
    def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default
            
            # Increment frequency
            self._frequencies[key] += 1
            self._hits += 1
            return self._cache[key]
    
    def put(self, key: Hashable, value: Any) -> None:
        """Put key-value pair in cache."""
        with self._lock:
            if key in self._cache:
                self._cache[key] = value
                self._frequencies[key] += 1
            else:
                if len(self._cache) >= self.capacity:
                    # Find least frequently used key
                    lfu_key = min(self._frequencies, key=self._frequencies.get)
                    del self._cache[lfu_key]
                    del self._frequencies[lfu_key]
                    self._evictions += 1
                
                self._cache[key] = value
                self._frequencies[key] = 1
    
    def delete(self, key: Hashable) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._frequencies[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()
            self._frequencies.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'name': self.name,
                'type': 'LFU',
                'capacity': self.capacity,
                'size': len(self._cache),
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate': hit_rate,
            }


class AsyncLFUCache:
    """
    Async-safe LFU (Least Frequently Used) Cache.
    """
    
    def __init__(self, capacity: int = 128, name: Optional[str] = None):
        """Initialize async LFU cache."""
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.name = name or f"AsyncLFUCache-{id(self)}"
        
        self._cache: Dict[Hashable, Any] = {}
        self._frequencies: Dict[Hashable, int] = {}
        self._lock = asyncio.Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    async def get(self, key: Hashable, default: Any = None) -> Any:
        """Get value by key asynchronously."""
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default
            
            self._frequencies[key] += 1
            self._hits += 1
            return self._cache[key]
    
    async def put(self, key: Hashable, value: Any) -> None:
        """Put key-value pair in cache asynchronously."""
        async with self._lock:
            if key in self._cache:
                self._cache[key] = value
                self._frequencies[key] += 1
            else:
                if len(self._cache) >= self.capacity:
                    lfu_key = min(self._frequencies, key=self._frequencies.get)
                    del self._cache[lfu_key]
                    del self._frequencies[lfu_key]
                    self._evictions += 1
                
                self._cache[key] = value
                self._frequencies[key] = 1
    
    async def delete(self, key: Hashable) -> bool:
        """Delete key from cache asynchronously."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._frequencies[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all items from cache asynchronously."""
        async with self._lock:
            self._cache.clear()
            self._frequencies.clear()
    
    async def size(self) -> int:
        """Get current cache size asynchronously."""
        return len(self._cache)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics asynchronously."""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'name': self.name,
                'type': 'AsyncLFU',
                'capacity': self.capacity,
                'size': len(self._cache),
                'hits': self._hits,
                'misses': self._misses,
                'evictions': self._evictions,
                'hit_rate': hit_rate,
            }
