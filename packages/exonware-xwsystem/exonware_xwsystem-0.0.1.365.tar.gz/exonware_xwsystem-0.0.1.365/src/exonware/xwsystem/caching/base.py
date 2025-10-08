#exonware/xsystem/caching/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

Caching module base classes - abstract classes for caching functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from .contracts import CacheType, EvictionPolicy, CacheStrategy


class ACacheBase(ABC):
    """Abstract base class for all cache implementations."""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[int] = None):
        """
        Initialize cache base.
        
        Args:
            max_size: Maximum cache size
            ttl: Time to live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._creation_times: Dict[str, float] = {}
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get cache size."""
        pass
    
    @abstractmethod
    def is_full(self) -> bool:
        """Check if cache is full."""
        pass
    
    @abstractmethod
    def evict(self) -> None:
        """Evict entries from cache."""
        pass


class ACacheManager(ABC):
    """Abstract base class for cache management."""
    
    @abstractmethod
    def create_cache(self, name: str, cache_type: CacheType, **kwargs) -> ACacheBase:
        """Create a new cache instance."""
        pass
    
    @abstractmethod
    def get_cache(self, name: str) -> Optional[ACacheBase]:
        """Get cache instance by name."""
        pass
    
    @abstractmethod
    def remove_cache(self, name: str) -> bool:
        """Remove cache instance."""
        pass
    
    @abstractmethod
    def list_caches(self) -> List[str]:
        """List all cache names."""
        pass
    
    @abstractmethod
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        pass


class ADistributedCache(ABC):
    """Abstract base class for distributed cache implementations."""
    
    @abstractmethod
    def connect(self, nodes: List[str]) -> None:
        """Connect to distributed cache nodes."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from distributed cache."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to distributed cache."""
        pass
    
    @abstractmethod
    def get_node_info(self) -> Dict[str, Any]:
        """Get distributed cache node information."""
        pass
    
    @abstractmethod
    def sync(self) -> None:
        """Synchronize cache across nodes."""
        pass


class ACacheDecorator(ABC):
    """Abstract base class for cache decorators."""
    
    @abstractmethod
    def __call__(self, func):
        """Decorate function with caching."""
        pass
    
    @abstractmethod
    def invalidate(self, *args, **kwargs) -> None:
        """Invalidate cache for specific arguments."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached results."""
        pass
