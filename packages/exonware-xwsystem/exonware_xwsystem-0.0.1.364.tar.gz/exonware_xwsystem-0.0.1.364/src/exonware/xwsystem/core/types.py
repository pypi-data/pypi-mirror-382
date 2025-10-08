#!/usr/bin/env python3
#exonware/xwsystem/core/types.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: 07-Sep-2025

Core types and enums for XWSystem.
"""

from enum import Enum


# ============================================================================
# CORE ENUMS
# ============================================================================

class DataType(Enum):
    """Core data types supported by XWSystem."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    BYTES = "bytes"
    NONE = "none"
    CUSTOM = "custom"


class CloneMode(Enum):
    """Cloning modes for object duplication."""
    SHALLOW = "shallow"
    DEEP = "deep"
    REFERENCE = "reference"


class CoreState(Enum):
    """Core system states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class CoreMode(Enum):
    """Core system modes."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEBUG = "debug"
    PERFORMANCE = "performance"


class CorePriority(Enum):
    """Core system priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
