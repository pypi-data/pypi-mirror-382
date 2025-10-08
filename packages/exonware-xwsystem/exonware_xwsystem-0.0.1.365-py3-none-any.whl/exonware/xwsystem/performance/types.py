#!/usr/bin/env python3
#exonware/xwsystem/performance/types.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: 07-Sep-2025

Performance types and enums for XWSystem.
"""

from enum import Enum
from ..shared.types import PerformanceLevel


# ============================================================================
# PERFORMANCE ENUMS
# ============================================================================

class PerformanceMetric(Enum):
    """Performance metric types."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CUSTOM = "custom"


class OptimizationStrategy(Enum):
    """Optimization strategies."""
    CPU_OPTIMIZED = "cpu_optimized"
    MEMORY_OPTIMIZED = "memory_optimized"
    IO_OPTIMIZED = "io_optimized"
    BALANCED = "balanced"
    CUSTOM = "custom"
