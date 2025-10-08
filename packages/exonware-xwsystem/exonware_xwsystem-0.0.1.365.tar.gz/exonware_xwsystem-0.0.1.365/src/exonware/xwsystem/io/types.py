#!/usr/bin/env python3
#exonware/xwsystem/io/types.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: 07-Sep-2025

IO types and enums for XWSystem.
"""

from enum import Enum
from ..shared.types import PathType, LockType, OperationResult


# ============================================================================
# IO ENUMS
# ============================================================================

class FileMode(Enum):
    """File operation modes."""
    READ = "r"
    WRITE = "w"
    APPEND = "a"
    READ_WRITE = "r+"
    WRITE_READ = "w+"
    APPEND_READ = "a+"
    BINARY_READ = "rb"
    BINARY_WRITE = "wb"
    BINARY_APPEND = "ab"
    BINARY_READ_WRITE = "rb+"
    BINARY_WRITE_READ = "wb+"
    BINARY_APPEND_READ = "ab+"


class FileType(Enum):
    """File types."""
    TEXT = "text"
    BINARY = "binary"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    CONFIG = "config"
    LOG = "log"
    TEMP = "temp"
    BACKUP = "backup"
