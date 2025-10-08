"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Caching module errors - exception classes for caching functionality.
"""


class CacheError(Exception):
    """Base exception for caching errors."""
    pass


class CacheKeyError(CacheError):
    """Raised when cache key is invalid or not found."""
    pass


class CacheSizeError(CacheError):
    """Raised when cache size limit is exceeded."""
    pass


class CacheTTLError(CacheError):
    """Raised when cache TTL (Time To Live) is invalid."""
    pass


class CacheSerializationError(CacheError):
    """Raised when cache serialization fails."""
    pass


class CacheDeserializationError(CacheError):
    """Raised when cache deserialization fails."""
    pass


class CacheConnectionError(CacheError):
    """Raised when cache connection fails."""
    pass


class CacheTimeoutError(CacheError):
    """Raised when cache operation times out."""
    pass


class CachePermissionError(CacheError):
    """Raised when cache permission is denied."""
    pass


class CacheConfigurationError(CacheError):
    """Raised when cache configuration is invalid."""
    pass


class DistributedCacheError(CacheError):
    """Raised when distributed cache operation fails."""
    pass


class CacheLockError(CacheError):
    """Raised when cache lock operation fails."""
    pass


class CacheEvictionError(CacheError):
    """Raised when cache eviction fails."""
    pass
