#exonware/xwsystem/enterprise/contracts.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Enterprise module contracts and interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

# Import enums from types module
from .types import (
    AuthType,
    SchemaType,
    TracingLevel,
    CompatibilityLevel,
    SpanKind,
    OAuth2GrantType
)

if TYPE_CHECKING:
    from .base import ATokenInfo, AUserInfo
    from .schema_registry import SchemaInfo
    from .distributed_tracing import SpanContext


class IAuthProvider(ABC):
    """Interface for authentication providers."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> 'ATokenInfo':
        """Authenticate user with credentials."""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> 'AUserInfo':
        """Validate authentication token."""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> 'ATokenInfo':
        """Refresh authentication token."""
        pass


class ISchemaRegistry(ABC):
    """Interface for schema registry implementations."""
    
    @abstractmethod
    async def register_schema(self, subject: str, schema: str, schema_type: str = "AVRO") -> 'SchemaInfo':
        """Register a new schema version."""
        pass
    
    @abstractmethod
    async def get_schema(self, subject: str, version: Optional[int] = None) -> 'SchemaInfo':
        """Get schema by subject and version."""
        pass
    
    @abstractmethod
    async def get_schema_by_id(self, schema_id: int) -> 'SchemaInfo':
        """Get schema by ID."""
        pass
    
    @abstractmethod
    async def get_versions(self, subject: str) -> List[int]:
        """Get all versions for a subject."""
        pass
    
    @abstractmethod
    async def set_compatibility(self, subject: str, level: 'CompatibilityLevel') -> None:
        """Set compatibility level for subject."""
        pass


class ITracingProvider(ABC):
    """Interface for tracing providers."""
    
    @abstractmethod
    def start_span(
        self, 
        name: str, 
        parent: Optional['SpanContext'] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> 'SpanContext':
        """Start a new span."""
        pass
    
    @abstractmethod
    def end_span(self, span: 'SpanContext') -> None:
        """End a span."""
        pass
    
    @abstractmethod
    def add_event(self, span: 'SpanContext', name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to a span."""
        pass
    
    @abstractmethod
    def add_attribute(self, span: 'SpanContext', key: str, value: Any) -> None:
        """Add an attribute to a span."""
        pass
