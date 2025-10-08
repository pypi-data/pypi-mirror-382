#exonware/xsystem/enterprise/errors.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Enterprise module errors - exception classes for enterprise functionality.
"""


class EnterpriseError(Exception):
    """Base exception for enterprise errors."""
    pass


class TracingError(EnterpriseError):
    """Base exception for tracing operations."""
    pass


class AuthenticationError(EnterpriseError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(EnterpriseError):
    """Raised when authorization fails."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when authentication token has expired."""
    pass


class SchemaRegistryError(EnterpriseError):
    """Raised when schema registry operation fails."""
    pass


class SchemaNotFoundError(SchemaRegistryError):
    """Raised when schema is not found."""
    pass


class SchemaValidationError(SchemaRegistryError):
    """Raised when schema validation fails."""
    pass


class SchemaVersionError(SchemaRegistryError):
    """Raised when schema version is invalid."""
    pass


class SpanError(TracingError):
    """Raised when span operation fails."""
    pass


class TraceContextError(TracingError):
    """Raised when trace context is invalid."""
    pass


class OAuth2Error(AuthenticationError):
    """Raised when OAuth2 operation fails."""
    pass


class JWTError(AuthenticationError):
    """Raised when JWT operation fails."""
    pass


class SAMLError(AuthenticationError):
    """Raised when SAML operation fails."""
    pass


class DistributedTracingError(EnterpriseError):
    """Raised when distributed tracing fails."""
    pass
