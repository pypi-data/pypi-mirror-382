"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

XSystem Enterprise Features Package

Provides enterprise-grade features including:
- Schema registry integration (Confluent, AWS Glue)
- Distributed tracing (OpenTelemetry)
- Advanced authentication (OAuth2, JWT, SAML)
- Service mesh integration
- Enterprise monitoring and observability
"""

from .schema_registry import (
    ASchemaRegistry, ConfluentSchemaRegistry, AwsGlueSchemaRegistry,
    SchemaRegistryError, SchemaNotFoundError, SchemaValidationError
)
from .distributed_tracing import (
    TracingManager, OpenTelemetryTracer, JaegerTracer,
    TracingError, SpanContext, TraceContext
)
from .auth import (
    OAuth2Provider, JWTProvider, SAMLProvider,
    AuthenticationError, AuthorizationError, TokenExpiredError
)

__all__ = [
    # Schema Registry
    "ASchemaRegistry",
    "ConfluentSchemaRegistry", 
    "AwsGlueSchemaRegistry",
    "SchemaRegistryError",
    "SchemaNotFoundError",
    "SchemaValidationError",
    
    # Distributed Tracing
    "TracingManager",
    "OpenTelemetryTracer",
    "JaegerTracer",
    "TracingError",
    "SpanContext",
    "TraceContext",
    
    # Authentication
    "OAuth2Provider",
    "JWTProvider",
    "SAMLProvider",
    "AuthenticationError",
    "AuthorizationError", 
    "TokenExpiredError",
]
