"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

Schema Registry Integration for Enterprise Serialization

Provides integration with enterprise schema registries for:
- Schema evolution and compatibility checking
- Centralized schema management
- Version control for data schemas
- Cross-service schema sharing
"""

import json
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from .base import ASchemaRegistry
from .errors import SchemaRegistryError, SchemaNotFoundError, SchemaValidationError
from .types import CompatibilityLevel

import requests
import boto3

from ..config.logging_setup import get_logger

logger = get_logger("xwsystem.enterprise.schema_registry")


@dataclass
class SchemaInfo:
    """Schema information from registry."""
    id: int
    version: int
    subject: str
    schema: str
    schema_type: str = "AVRO"
    compatibility: Optional[CompatibilityLevel] = None


    
    @abstractmethod
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check if schema is compatible with latest version."""
        pass
    
    @abstractmethod
    async def set_compatibility(self, subject: str, level: CompatibilityLevel) -> None:
        """Set compatibility level for subject."""
        pass


class ConfluentSchemaRegistry(ASchemaRegistry):
    """Confluent Schema Registry implementation."""
    
    def __init__(
        self,
        url: str,
        auth: Optional[tuple] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ):
        """
        Initialize Confluent Schema Registry client.
        
        Args:
            url: Schema registry URL
            auth: Optional (username, password) tuple
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
        """
        # requests is now required
        
        self.url = url.rstrip('/')
        self.auth = auth
        self.headers = headers or {}
        self.timeout = timeout
        
        # Set default headers
        self.headers.setdefault('Content-Type', 'application/vnd.schemaregistry.v1+json')
    
    async def register_schema(self, subject: str, schema: str, schema_type: str = "AVRO") -> SchemaInfo:
        """Register a new schema version."""
        import asyncio
        
        def _register():
            url = f"{self.url}/subjects/{subject}/versions"
            data = {
                "schema": json.dumps(json.loads(schema)) if schema_type == "AVRO" else schema,
                "schemaType": schema_type
            }
            
            response = requests.post(
                url, 
                json=data, 
                auth=self.auth, 
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 409:
                # Schema already exists, get existing info
                return self._get_existing_schema(subject, schema)
            elif response.status_code != 200:
                raise SchemaRegistryError(f"Failed to register schema: {response.text}")
            
            result = response.json()
            return SchemaInfo(
                id=result['id'],
                version=result.get('version', 1),
                subject=subject,
                schema=schema,
                schema_type=schema_type
            )
        
        return await asyncio.to_thread(_register)
    
    async def get_schema(self, schema_id: int) -> SchemaInfo:
        """Get schema by ID."""
        import asyncio
        
        def _get():
            url = f"{self.url}/schemas/ids/{schema_id}"
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise SchemaNotFoundError(f"Schema ID {schema_id} not found")
            elif response.status_code != 200:
                raise SchemaRegistryError(f"Failed to get schema: {response.text}")
            
            result = response.json()
            return SchemaInfo(
                id=schema_id,
                version=1,  # Version not provided by ID endpoint
                subject="",  # Subject not provided by ID endpoint
                schema=result['schema'],
                schema_type=result.get('schemaType', 'AVRO')
            )
        
        return await asyncio.to_thread(_get)
    
    async def get_latest_schema(self, subject: str) -> SchemaInfo:
        """Get latest schema version for subject."""
        import asyncio
        
        def _get():
            url = f"{self.url}/subjects/{subject}/versions/latest"
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise SchemaNotFoundError(f"Subject {subject} not found")
            elif response.status_code != 200:
                raise SchemaRegistryError(f"Failed to get schema: {response.text}")
            
            result = response.json()
            return SchemaInfo(
                id=result['id'],
                version=result['version'],
                subject=result['subject'],
                schema=result['schema'],
                schema_type=result.get('schemaType', 'AVRO')
            )
        
        return await asyncio.to_thread(_get)
    
    async def get_schema_versions(self, subject: str) -> List[int]:
        """Get all versions for a subject."""
        import asyncio
        
        def _get():
            url = f"{self.url}/subjects/{subject}/versions"
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                return []
            elif response.status_code != 200:
                raise SchemaRegistryError(f"Failed to get versions: {response.text}")
            
            return response.json()
        
        return await asyncio.to_thread(_get)
    
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check if schema is compatible with latest version."""
        import asyncio
        
        def _check():
            url = f"{self.url}/compatibility/subjects/{subject}/versions/latest"
            data = {"schema": json.dumps(json.loads(schema))}
            
            response = requests.post(
                url,
                json=data,
                auth=self.auth,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return False
            
            result = response.json()
            return result.get('is_compatible', False)
        
        return await asyncio.to_thread(_check)
    
    async def set_compatibility(self, subject: str, level: CompatibilityLevel) -> None:
        """Set compatibility level for subject."""
        import asyncio
        
        def _set():
            url = f"{self.url}/config/{subject}"
            data = {"compatibility": level.value}
            
            response = requests.put(
                url,
                json=data,
                auth=self.auth,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise SchemaRegistryError(f"Failed to set compatibility: {response.text}")
        
        await asyncio.to_thread(_set)
    
    def _get_existing_schema(self, subject: str, schema: str) -> SchemaInfo:
        """Get existing schema info when registration returns 409."""
        # This is a simplified implementation
        # In practice, you'd need to check all versions to find the matching one
        url = f"{self.url}/subjects/{subject}/versions/latest"
        response = requests.get(url, auth=self.auth, headers=self.headers, timeout=self.timeout)
        
        if response.status_code == 200:
            result = response.json()
            return SchemaInfo(
                id=result['id'],
                version=result['version'],
                subject=result['subject'],
                schema=result['schema'],
                schema_type=result.get('schemaType', 'AVRO')
            )
        
        raise SchemaRegistryError("Could not retrieve existing schema")


class AwsGlueSchemaRegistry(ASchemaRegistry):
    """AWS Glue Schema Registry implementation."""
    
    def __init__(
        self,
        registry_name: str,
        region_name: str = 'us-east-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize AWS Glue Schema Registry client.
        
        Args:
            registry_name: Name of the schema registry
            region_name: AWS region name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
        """
        # boto3 is now required
        
        self.registry_name = registry_name
        self.client = boto3.client(
            'glue',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    
    async def register_schema(self, subject: str, schema: str, schema_type: str = "AVRO") -> SchemaInfo:
        """Register a new schema version."""
        import asyncio
        
        def _register():
            try:
                response = self.client.register_schema_version(
                    SchemaId={
                        'RegistryName': self.registry_name,
                        'SchemaName': subject
                    },
                    SchemaDefinition=schema
                )
                
                return SchemaInfo(
                    id=hash(response['SchemaVersionId']),  # AWS uses UUID, convert to int
                    version=response['VersionNumber'],
                    subject=subject,
                    schema=schema,
                    schema_type=schema_type
                )
                
            except self.client.exceptions.EntityNotFoundException:
                # Schema doesn't exist, create it first
                self.client.create_schema(
                    RegistryId={'RegistryName': self.registry_name},
                    SchemaName=subject,
                    DataFormat=schema_type,
                    SchemaDefinition=schema
                )
                
                # Now register the version
                response = self.client.register_schema_version(
                    SchemaId={
                        'RegistryName': self.registry_name,
                        'SchemaName': subject
                    },
                    SchemaDefinition=schema
                )
                
                return SchemaInfo(
                    id=hash(response['SchemaVersionId']),
                    version=response['VersionNumber'],
                    subject=subject,
                    schema=schema,
                    schema_type=schema_type
                )
        
        return await asyncio.to_thread(_register)
    
    async def get_schema(self, schema_id: int) -> SchemaInfo:
        """Get schema by ID (not directly supported by AWS Glue)."""
        raise SchemaRegistryError("AWS Glue Schema Registry does not support lookup by numeric ID")
    
    async def get_latest_schema(self, subject: str) -> SchemaInfo:
        """Get latest schema version for subject."""
        import asyncio
        
        def _get():
            try:
                response = self.client.get_schema_version(
                    SchemaId={
                        'RegistryName': self.registry_name,
                        'SchemaName': subject
                    },
                    SchemaVersionNumber={'LatestVersion': True}
                )
                
                return SchemaInfo(
                    id=hash(response['SchemaVersionId']),
                    version=response['VersionNumber'],
                    subject=subject,
                    schema=response['SchemaDefinition'],
                    schema_type=response['DataFormat']
                )
                
            except self.client.exceptions.EntityNotFoundException:
                raise SchemaNotFoundError(f"Subject {subject} not found")
        
        return await asyncio.to_thread(_get)
    
    async def get_schema_versions(self, subject: str) -> List[int]:
        """Get all versions for a subject."""
        import asyncio
        
        def _get():
            try:
                response = self.client.list_schema_versions(
                    SchemaId={
                        'RegistryName': self.registry_name,
                        'SchemaName': subject
                    }
                )
                
                return [v['VersionNumber'] for v in response['SchemaVersions']]
                
            except self.client.exceptions.EntityNotFoundException:
                return []
        
        return await asyncio.to_thread(_get)
    
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check if schema is compatible with latest version."""
        import asyncio
        
        def _check():
            try:
                response = self.client.check_schema_version_validity(
                    SchemaId={
                        'RegistryName': self.registry_name,
                        'SchemaName': subject
                    },
                    SchemaDefinition=schema
                )
                
                return response['Valid']
                
            except Exception:
                return False
        
        return await asyncio.to_thread(_check)
    
    async def set_compatibility(self, subject: str, level: CompatibilityLevel) -> None:
        """Set compatibility level for subject (not directly supported by AWS Glue)."""
        logger.warning("AWS Glue Schema Registry does not support setting compatibility levels")


class SchemaRegistry:
    """Main schema registry class for backward compatibility."""
    
    def __init__(self, registry_type: str = "confluent", **kwargs):
        """Initialize schema registry.
        
        Args:
            registry_type: Type of registry ('confluent', 'aws_glue')
            **kwargs: Registry-specific configuration
        """
        self.registry_type = registry_type
        self._registry = None
        
        if registry_type == "confluent":
            self._registry = ConfluentSchemaRegistry(**kwargs)
        elif registry_type == "aws_glue":
            self._registry = AWSGlueSchemaRegistry(**kwargs)
        else:
            raise ValueError(f"Unsupported registry type: {registry_type}")
    
    async def register_schema(self, subject: str, schema: str, schema_type: str = "JSON") -> int:
        """Register a schema."""
        return await self._registry.register_schema(subject, schema, schema_type)
    
    async def get_schema(self, subject: str, version: Optional[int] = None) -> Optional[str]:
        """Get a schema."""
        return await self._registry.get_schema(subject, version)
    
    async def get_schema_by_id(self, schema_id: int) -> Optional[str]:
        """Get schema by ID."""
        return await self._registry.get_schema_by_id(schema_id)
    
    async def list_subjects(self) -> List[str]:
        """List all subjects."""
        return await self._registry.list_subjects()
    
    async def get_versions(self, subject: str) -> List[int]:
        """Get all versions for a subject."""
        return await self._registry.get_versions(subject)
    
    async def check_compatibility(self, subject: str, schema: str) -> bool:
        """Check schema compatibility."""
        return await self._registry.check_compatibility(subject, schema)
    
    async def set_compatibility(self, subject: str, level: CompatibilityLevel) -> None:
        """Set compatibility level."""
        await self._registry.set_compatibility(subject, level)