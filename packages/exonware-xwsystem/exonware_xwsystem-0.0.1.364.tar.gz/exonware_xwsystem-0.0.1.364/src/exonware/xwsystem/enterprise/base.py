#exonware/xsystem/enterprise/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Enterprise module base classes - abstract classes and data structures for enterprise functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .contracts import AuthType, SchemaType, TracingLevel
    from .schema_registry import SchemaInfo, CompatibilityLevel
    from .distributed_tracing import SpanContext, SpanKind


# Original base classes that were removed - RESTORED
@dataclass
class ATokenInfo:
    """Token information structure."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


@dataclass
class AUserInfo:
    """User information structure."""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = None
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.attributes is None:
            self.attributes = {}


class AAuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> ATokenInfo:
        """Authenticate user with credentials."""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> AUserInfo:
        """Validate authentication token."""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> ATokenInfo:
        """Refresh authentication token."""
        pass


# New abstract base classes for enterprise functionality
class AAuthenticationBase(ABC):
    """Abstract base class for authentication operations."""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate user with credentials."""
        pass
    
    @abstractmethod
    def authorize(self, user: str, resource: str, action: str) -> bool:
        """Authorize user for resource action."""
        pass
    
    @abstractmethod
    def get_token(self, user: str) -> Optional[str]:
        """Get authentication token for user."""
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        """Validate authentication token."""
        pass
    
    @abstractmethod
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh authentication token."""
        pass
    
    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """Revoke authentication token."""
        pass
    
    @abstractmethod
    def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from token."""
        pass


class ASchemaRegistryBase(ABC):
    """Abstract base class for schema registry operations."""
    
    def __init__(self, registry_url: str):
        """
        Initialize schema registry.
        
        Args:
            registry_url: Schema registry URL
        """
        self.registry_url = registry_url
        self._schemas: Dict[str, Any] = {}
    
    @abstractmethod
    def register_schema(self, subject: str, schema: Dict[str, Any], version: Optional[int] = None) -> int:
        """Register schema in registry."""
        pass
    
    @abstractmethod
    def get_schema(self, subject: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get schema from registry."""
        pass
    
    @abstractmethod
    def delete_schema(self, subject: str, version: Optional[int] = None) -> bool:
        """Delete schema from registry."""
        pass
    
    @abstractmethod
    def list_subjects(self) -> List[str]:
        """List all subjects."""
        pass
    
    @abstractmethod
    def get_versions(self, subject: str) -> List[int]:
        """Get schema versions for subject."""
        pass
    
    @abstractmethod
    def get_latest_version(self, subject: str) -> Optional[int]:
        """Get latest schema version for subject."""
        pass
    
    @abstractmethod
    def check_compatibility(self, subject: str, schema: Dict[str, Any], version: Optional[int] = None) -> bool:
        """Check schema compatibility."""
        pass


class ADistributedTracingBase(ABC):
    """Abstract base class for distributed tracing operations."""
    
    def __init__(self, service_name: str, tracing_level: str = "INFO"):
        """
        Initialize distributed tracing.
        
        Args:
            service_name: Service name for tracing
            tracing_level: Tracing level
        """
        self.service_name = service_name
        self.tracing_level = tracing_level
        self._spans: List[Any] = []
    
    @abstractmethod
    def start_span(self, operation_name: str, parent_span: Optional[Any] = None) -> Any:
        """Start new span."""
        pass
    
    @abstractmethod
    def finish_span(self, span: Any) -> None:
        """Finish span."""
        pass
    
    @abstractmethod
    def add_span_tag(self, span: Any, key: str, value: Any) -> None:
        """Add tag to span."""
        pass
    
    @abstractmethod
    def add_span_log(self, span: Any, message: str, **kwargs) -> None:
        """Add log to span."""
        pass
    
    @abstractmethod
    def inject_context(self, span: Any, headers: Dict[str, str]) -> None:
        """Inject trace context into headers."""
        pass
    
    @abstractmethod
    def extract_context(self, headers: Dict[str, str]) -> Optional[Any]:
        """Extract trace context from headers."""
        pass
    
    @abstractmethod
    def get_trace_id(self, span: Any) -> Optional[str]:
        """Get trace ID from span."""
        pass
    
    @abstractmethod
    def get_span_id(self, span: Any) -> Optional[str]:
        """Get span ID from span."""
        pass


class AEnterpriseManagerBase(ABC):
    """Abstract base class for enterprise management."""
    
    @abstractmethod
    def initialize_enterprise_features(self) -> None:
        """Initialize enterprise features."""
        pass
    
    @abstractmethod
    def shutdown_enterprise_features(self) -> None:
        """Shutdown enterprise features."""
        pass
    
    @abstractmethod
    def get_enterprise_status(self) -> Dict[str, Any]:
        """Get enterprise status."""
        pass
    
    @abstractmethod
    def configure_enterprise(self, config: Dict[str, Any]) -> None:
        """Configure enterprise settings."""
        pass
    
    @abstractmethod
    def validate_enterprise_license(self) -> bool:
        """Validate enterprise license."""
        pass
    
    @abstractmethod
    def get_enterprise_metrics(self) -> Dict[str, Any]:
        """Get enterprise metrics."""
        pass


class AComplianceBase(ABC):
    """Abstract base class for compliance management."""
    
    @abstractmethod
    def check_compliance(self, standard: str) -> bool:
        """Check compliance with standard."""
        pass
    
    @abstractmethod
    def get_compliance_report(self, standard: str) -> Dict[str, Any]:
        """Get compliance report."""
        pass
    
    @abstractmethod
    def audit_trail(self, operation: str, user: str, details: Dict[str, Any]) -> None:
        """Record audit trail."""
        pass
    
    @abstractmethod
    def get_audit_logs(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get audit logs."""
        pass
    
    @abstractmethod
    def encrypt_sensitive_data(self, data: Any) -> Any:
        """Encrypt sensitive data."""
        pass
    
    @abstractmethod
    def decrypt_sensitive_data(self, encrypted_data: Any) -> Any:
        """Decrypt sensitive data."""
        pass


# Additional missing classes that were imported by other files
class ASchemaRegistry(ABC):
    """Abstract base class for schema registry implementations."""
    
    @abstractmethod
    async def register_schema(self, subject: str, schema: str, schema_type: str = "AVRO") -> 'SchemaInfo':
        """Register a new schema version."""
        pass
    
    @abstractmethod
    async def get_schema(self, schema_id: int) -> 'SchemaInfo':
        """Get schema by ID."""
        pass
    
    @abstractmethod
    async def get_latest_schema(self, subject: str) -> 'SchemaInfo':
        """Get latest schema version for subject."""
        pass
    
    @abstractmethod
    async def get_schema_versions(self, subject: str) -> List[int]:
        """Get all versions for a subject."""
        pass
    
    @abstractmethod
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check if schema is compatible with latest version."""
        pass
    
    @abstractmethod
    async def set_compatibility(self, subject: str, level: 'CompatibilityLevel') -> None:
        """Set compatibility level for subject."""
        pass


class ATracingProvider(ABC):
    """Abstract base class for tracing providers."""
    
    @abstractmethod
    def start_span(
        self, 
        name: str, 
        kind: 'SpanKind' = None,
        parent: Optional['SpanContext'] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> 'SpanContext':
        """Start a new span."""
        pass
    
    @abstractmethod
    def finish_span(self, span: 'SpanContext', status: str = "OK", error: Optional[Exception] = None) -> None:
        """Finish a span."""
        pass
    
    @abstractmethod
    def add_span_attribute(self, span: 'SpanContext', key: str, value: Any) -> None:
        """Add attribute to span."""
        pass
    
    @abstractmethod
    def add_span_event(self, span: 'SpanContext', name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add event to span."""
        pass
