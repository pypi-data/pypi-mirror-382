#!/usr/bin/env python3
#exonware/xwsystem/serialization/types.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: 07-Sep-2025

Serialization types and enums for XWSystem.
"""

from enum import Enum, Flag, auto


# ============================================================================
# SERIALIZATION ENUMS
# ============================================================================

class SerializationFormat(Enum):
    """Supported serialization formats."""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    TOML = "toml"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    CBOR = "cbor"
    BSON = "bson"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    NATIVE = "native"


class SerializationMode(Enum):
    """Serialization modes."""
    COMPACT = "compact"
    PRETTY = "pretty"
    BINARY = "binary"
    TEXT = "text"


class SerializationType(Enum):
    """Serialization types."""
    OBJECT = "object"
    ARRAY = "array"
    PRIMITIVE = "primitive"
    CUSTOM = "custom"


class SerializationCapability(Flag):
    """Serialization capabilities for introspection."""
    STREAMING = auto()
    PARTIAL_ACCESS = auto()
    TYPED_DECODE = auto()
    ZERO_COPY = auto()
    CANONICAL = auto()
    RANDOM_ACCESS = auto()
