#!/usr/bin/env python3
#exonware/xwsystem/enterprise/types.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: 07-Sep-2025

Enterprise types and enums for XWSystem.
"""

from enum import Enum
from ..shared.types import AuthType


# ============================================================================
# ENTERPRISE ENUMS
# ============================================================================


class SchemaType(Enum):
    """Schema type enumeration."""
    AVRO = "avro"
    JSON = "json"
    PROTOBUF = "protobuf"
    OPENAPI = "openapi"


class TracingLevel(Enum):
    """Tracing level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CompatibilityLevel(Enum):
    """Schema compatibility levels."""
    NONE = "NONE"
    BACKWARD = "BACKWARD"
    BACKWARD_TRANSITIVE = "BACKWARD_TRANSITIVE"
    FORWARD = "FORWARD"
    FORWARD_TRANSITIVE = "FORWARD_TRANSITIVE"
    FULL = "FULL"
    FULL_TRANSITIVE = "FULL_TRANSITIVE"


class SpanKind(Enum):
    """Span kinds for different operation types."""
    INTERNAL = "INTERNAL"
    SERVER = "SERVER"
    CLIENT = "CLIENT"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"


class OAuth2GrantType(Enum):
    """OAuth2 grant types."""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    RESOURCE_OWNER = "password"
    REFRESH_TOKEN = "refresh_token"
