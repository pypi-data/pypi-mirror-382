#exonware/xsystem/performance/errors.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

Performance module errors - exception classes for performance functionality.
"""


class PerformanceError(Exception):
    """Base exception for performance errors."""
    pass


class PerformanceManagerError(PerformanceError):
    """Raised when performance manager operation fails."""
    pass


class PerformanceProfilerError(PerformanceError):
    """Raised when performance profiling fails."""
    pass


class PerformanceOptimizerError(PerformanceError):
    """Raised when performance optimization fails."""
    pass


class PerformanceBenchmarkError(PerformanceError):
    """Raised when performance benchmarking fails."""
    pass


class PerformanceCacheError(PerformanceError):
    """Raised when performance cache operation fails."""
    pass


class PerformanceMetricError(PerformanceError):
    """Raised when performance metric operation fails."""
    pass


class PerformanceThresholdError(PerformanceError):
    """Raised when performance threshold is invalid."""
    pass


class PerformanceConfigurationError(PerformanceError):
    """Raised when performance configuration is invalid."""
    pass


class PerformanceResourceError(PerformanceError):
    """Raised when performance resource operation fails."""
    pass


class PerformanceTimeoutError(PerformanceError):
    """Raised when performance operation times out."""
    pass


class PerformanceMemoryError(PerformanceError):
    """Raised when performance memory operation fails."""
    pass


class PerformanceCPUError(PerformanceError):
    """Raised when performance CPU operation fails."""
    pass


class PerformanceIOError(PerformanceError):
    """Raised when performance I/O operation fails."""
    pass


class PerformanceNetworkError(PerformanceError):
    """Raised when performance network operation fails."""
    pass


class PerformanceConcurrencyError(PerformanceError):
    """Raised when performance concurrency operation fails."""
    pass
