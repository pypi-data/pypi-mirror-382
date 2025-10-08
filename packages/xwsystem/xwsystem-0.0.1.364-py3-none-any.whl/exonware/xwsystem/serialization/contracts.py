#!/usr/bin/env python3
#exonware\xwsystem\serialization\contracts.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Serialization interfaces for XWSystem.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncIterator, BinaryIO, Dict, List, Optional, TextIO, Union, Protocol, Iterator, Iterable, Callable, Literal
from typing_extensions import runtime_checkable
from dataclasses import dataclass

# Import enums from types module
from .types import (
    SerializationFormat,
    SerializationMode,
    SerializationType,
    SerializationCapability
)


# ============================================================================
# SERIALIZATION ERRORS
# ============================================================================

class SerializationError(Exception):
    """Base exception for serialization errors."""
    
    def __init__(self, message: str, format_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.format_name = format_name
        self.original_error = original_error


class FormatDetectionError(SerializationError):
    """Error when format detection fails."""
    pass


class ValidationError(SerializationError):
    """Error when validation fails."""
    pass


# ============================================================================
# SERIALIZATION RESULT
# ============================================================================

@dataclass
class SerializationResult:
    """Result of serialization operation with metadata."""
    payload: Union[str, bytes]
    bytes_written: int
    duration_ms: float
    meta: Dict[str, Any]


# ============================================================================
# CORE SERIALIZATION INTERFACE
# ============================================================================

class ISerialization(ABC):
    """
    Unified interface defining the contract for all serialization implementations.
    
    This interface ensures consistent API across different serialization formats
    with proper support for both text and binary formats, sync and async operations.
    
    🚨 CRITICAL IMPLEMENTATION PRINCIPLE:
       NEVER HARDCODE SERIALIZATION/DESERIALIZATION LOGIC!
       
       Always use official, well-tested libraries:
       - Built-in modules (json, pickle, marshal, csv, etc.)
       - Established third-party libraries (PyYAML, tomli-w, etc.)
       
       Hardcoding is dangerous because:
       1. Incomplete specification implementation
       2. Missing edge cases and security vulnerabilities  
       3. Performance issues
       4. Maintenance burden
       5. Compatibility problems
       
       If an official library doesn't exist, use the most established
       community library, not custom implementations.
    
    🔄 ASYNC INTEGRATION:
       This interface includes both sync and async methods. The ASerialization
       base class provides default async implementations that delegate to sync
       methods via asyncio.to_thread(). Individual serializers can override
       async methods when there's a performance benefit.
    """

    # =============================================================================
    # PROPERTIES
    # =============================================================================

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get the serialization format name (e.g., 'JSON', 'YAML')."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Get supported file extensions for this format."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """Get the MIME type for this serialization format."""
        pass

    @property
    @abstractmethod
    def is_binary_format(self) -> bool:
        """Whether this is a binary or text-based format."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this format supports streaming serialization."""
        pass

    @abstractmethod
    def capabilities(self) -> set[SerializationCapability]:
        """Get set of capabilities supported by this format."""
        pass

    # =============================================================================
    # FORMAT DETECTION
    # =============================================================================

    @abstractmethod
    def sniff_format(self, src: Union[str, bytes, Path, TextIO, BinaryIO]) -> SerializationFormat:
        """
        Auto-detect format from data source.
        
        Args:
            src: Data source (string, bytes, file path, or file-like object)
            
        Returns:
            Detected serialization format
            
        Raises:
            FormatDetectionError: If format cannot be detected
        """
        pass

    # =============================================================================
    # CORE SERIALIZATION METHODS
    # =============================================================================

    @abstractmethod
    def dumps(self, data: Any) -> Union[str, bytes]:
        """
        Serialize data to string or bytes based on format type.
        
        Automatically delegates to dumps_text() or dumps_binary() based on 
        is_binary_format property.

        Args:
            data: Data to serialize

        Returns:
            Serialized string for text formats, bytes for binary formats

        Raises:
            SerializationError: If serialization fails
        """
        pass

    @abstractmethod
    def dumps_text(self, data: Any) -> str:
        """
        Serialize data to text string.
        
        Should only be implemented by text-based formats.

        Args:
            data: Data to serialize

        Returns:
            Serialized text string

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on binary format
        """
        pass
        
    @abstractmethod
    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to bytes.
        
        Should only be implemented by binary formats.

        Args:
            data: Data to serialize

        Returns:
            Serialized bytes

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on text format
        """
        pass

    @abstractmethod
    def loads(self, data: Union[str, bytes]) -> Any:
        """
        Deserialize from string or bytes.
        
        Automatically handles both text and binary data based on input type
        and format capabilities.

        Args:
            data: String or bytes to deserialize

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    def loads_text(self, data: str) -> Any:
        """
        Deserialize from text string.
        
        Should be implemented by all formats (binary formats may convert
        from base64 or other text encoding).

        Args:
            data: Text string to deserialize

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass
        
    @abstractmethod
    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize from bytes.
        
        Should only be implemented by binary formats.

        Args:
            data: Bytes to deserialize

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    # =============================================================================
    # TYPED DECODING
    # =============================================================================

    @abstractmethod
    def loads_typed(self, data: Union[str, bytes], type_: type) -> Any:
        """
        Deserialize data to specific type (dataclass, TypedDict, pydantic, etc.).
        
        Args:
            data: Serialized data
            type_: Target type for deserialization
            
        Returns:
            Deserialized object of specified type
            
        Raises:
            SerializationError: If deserialization fails
            ValidationError: If data doesn't match target type
        """
        pass

    # =============================================================================
    # PATH-BASED ACCESS (Partial Access)
    # =============================================================================

    @abstractmethod
    def get_at(self, data: Union[str, bytes], path: str) -> Any:
        """
        Get value at specific path without full deserialization.
        
        Supports JSON Pointer (RFC 6901), XPath for XML, etc.
        
        Args:
            data: Serialized data
            path: Path expression (JSON Pointer, XPath, etc.)
            
        Returns:
            Value at specified path
            
        Raises:
            SerializationError: If path access fails
            ValidationError: If path is invalid
        """
        pass

    @abstractmethod
    def set_at(self, data: Union[str, bytes], path: str, value: Any) -> Union[str, bytes]:
        """
        Set value at specific path without full deserialization.
        
        Args:
            data: Serialized data
            path: Path expression
            value: New value to set
            
        Returns:
            Modified serialized data
            
        Raises:
            SerializationError: If path modification fails
        """
        pass

    @abstractmethod
    def iter_path(self, data: Union[str, bytes], path: str) -> Iterator[Any]:
        """
        Iterate over values matching path expression.
        
        Args:
            data: Serialized data
            path: Path expression for iteration
            
        Yields:
            Matching values
            
        Raises:
            SerializationError: If iteration fails
        """
        pass

    # =============================================================================
    # PATCHING
    # =============================================================================

    @abstractmethod
    def apply_patch(self, data: Union[str, bytes], patch: Any, rfc: Literal["6902", "7386"] = "6902") -> Union[str, bytes]:
        """
        Apply patch to serialized data.
        
        Args:
            data: Serialized data
            patch: Patch data (JSON Patch RFC 6902 or JSON Merge Patch RFC 7386)
            rfc: Patch format specification
            
        Returns:
            Patched serialized data
            
        Raises:
            SerializationError: If patch application fails
        """
        pass

    # =============================================================================
    # SCHEMA VALIDATION
    # =============================================================================

    @abstractmethod
    def validate_schema(self, data: Union[str, bytes], schema: Any, dialect: Literal["jsonschema", "avro", "protobuf", "xsd"] = "jsonschema") -> bool:
        """
        Validate data against schema.
        
        Args:
            data: Serialized data to validate
            schema: Schema definition
            dialect: Schema dialect/format
            
        Returns:
            True if data matches schema
            
        Raises:
            ValidationError: If validation fails
        """
        pass

    # =============================================================================
    # CANONICAL SERIALIZATION
    # =============================================================================

    @abstractmethod
    def canonicalize(self, data: Any) -> Union[str, bytes]:
        """
        Create canonical representation of data.
        
        Ensures deterministic output (key order, float formatting, etc.).
        
        Args:
            data: Data to canonicalize
            
        Returns:
            Canonical serialized representation
            
        Raises:
            SerializationError: If canonicalization fails
        """
        pass

    @abstractmethod
    def hash_stable(self, data: Any, algorithm: str = "sha256") -> str:
        """
        Generate stable hash of data using canonical representation.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, xxh3, etc.)
            
        Returns:
            Stable hash string
        """
        pass

    # =============================================================================
    # CHECKSUMS
    # =============================================================================

    @abstractmethod
    def checksum(self, data: Any, algorithm: str = "sha256") -> str:
        """
        Calculate checksum of serialized data.
        
        Args:
            data: Data to checksum
            algorithm: Checksum algorithm (sha256, xxh3, crc32, etc.)
            
        Returns:
            Checksum string
        """
        pass

    @abstractmethod
    def verify_checksum(self, data: Union[str, bytes], expected_checksum: str, algorithm: str = "sha256") -> bool:
        """
        Verify checksum of serialized data.
        
        Args:
            data: Serialized data
            expected_checksum: Expected checksum value
            algorithm: Checksum algorithm
            
        Returns:
            True if checksum matches
        """
        pass

    # =============================================================================
    # FILE-LIKE OBJECT METHODS
    # =============================================================================

    @abstractmethod
    def dump(self, data: Any, fp: Union[TextIO, BinaryIO]) -> None:
        """
        Serialize data to file-like object.
        
        Automatically chooses text or binary mode based on format type.

        Args:
            data: Data to serialize
            fp: File-like object to write to (text or binary)

        Raises:
            SerializationError: If serialization fails
        """
        pass
        
    @abstractmethod
    def dump_text(self, data: Any, fp: TextIO) -> None:
        """
        Serialize data to text file-like object.

        Args:
            data: Data to serialize
            fp: Text file-like object to write to

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on binary-only format
        """
        pass
        
    @abstractmethod  
    def dump_binary(self, data: Any, fp: BinaryIO) -> None:
        """
        Serialize data to binary file-like object.

        Args:
            data: Data to serialize
            fp: Binary file-like object to write to

        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    @abstractmethod
    def load(self, fp: Union[TextIO, BinaryIO]) -> Any:
        """
        Deserialize from file-like object.
        
        Automatically handles text or binary file-like objects.

        Args:
            fp: File-like object to read from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    def load_text(self, fp: TextIO) -> Any:
        """
        Deserialize from text file-like object.

        Args:
            fp: Text file-like object to read from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
        """
        pass
        
    @abstractmethod
    def load_binary(self, fp: BinaryIO) -> Any:
        """
        Deserialize from binary file-like object.

        Args:
            fp: Binary file-like object to read from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If deserialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    # =============================================================================
    # FILE PATH METHODS
    # =============================================================================

    @abstractmethod
    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to file.
        
        Automatically handles text/binary mode based on format type.

        Args:
            data: Data to serialize
            file_path: Path to save file

        Raises:
            SerializationError: If saving fails
        """
        pass
        
    @abstractmethod  
    def load_file(self, file_path: Union[str, Path]) -> Any:
        """
        Load data from file.
        
        Automatically handles text/binary mode based on format type.

        Args:
            file_path: Path to load from

        Returns:
            Deserialized Python object

        Raises:
            SerializationError: If loading fails
        """
        pass

    # =============================================================================
    # SYNC STREAMING
    # =============================================================================

    @abstractmethod
    def iter_serialize(self, data: Any, chunk_size: int = 8192) -> Iterator[Union[str, bytes]]:
        """
        Stream serialize data in chunks synchronously.
        
        Args:
            data: Data to serialize
            chunk_size: Size of each chunk
            
        Yields:
            Serialized chunks
        """
        pass

    @abstractmethod
    def iter_deserialize(self, src: Union[TextIO, BinaryIO, Iterable[Union[str, bytes]]]) -> Any:
        """
        Stream deserialize data from chunks synchronously.
        
        Args:
            src: Source of data chunks
            
        Returns:
            Deserialized Python object
        """
        pass

    # =============================================================================
    # BATCH STREAMING (NDJSON)
    # =============================================================================

    @abstractmethod
    def serialize_ndjson(self, rows: Iterable[Any]) -> Iterator[str]:
        """
        Serialize iterable to newline-delimited JSON.
        
        Args:
            rows: Iterable of objects to serialize
            
        Yields:
            JSON lines
        """
        pass

    @abstractmethod
    def deserialize_ndjson(self, lines: Iterable[str]) -> Iterator[Any]:
        """
        Deserialize newline-delimited JSON.
        
        Args:
            lines: Iterable of JSON lines
            
        Yields:
            Deserialized objects
        """
        pass

    # =============================================================================
    # VALIDATION AND UTILITY METHODS
    # =============================================================================

    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """
        Validate data for serialization compatibility.

        Args:
            data: Data to validate

        Returns:
            True if data can be serialized

        Raises:
            SerializationError: If validation fails
        """
        pass

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information for this serialization format.

        Returns:
            Dictionary with schema information including:
            - supported_types: List of supported Python types
            - format_version: Version of the format specification
            - capabilities: Dict of format capabilities
        """
        pass

    @abstractmethod
    def estimate_size(self, data: Any) -> int:
        """
        Estimate serialized size in bytes.

        Args:
            data: Data to estimate

        Returns:
            Estimated size in bytes
        """
        pass

    # =============================================================================
    # TYPE ADAPTERS
    # =============================================================================

    @abstractmethod
    def register_type_adapter(self, typ: type, to_fn: Callable[[Any], Any], from_fn: Callable[[Any], Any]) -> None:
        """
        Register custom type adapter for serialization.
        
        Args:
            typ: Type to register adapter for
            to_fn: Function to convert type to serializable form
            from_fn: Function to convert from serialized form to type
        """
        pass

    @abstractmethod
    def unregister_type_adapter(self, typ: type) -> bool:
        """
        Unregister type adapter.
        
        Args:
            typ: Type to unregister
            
        Returns:
            True if adapter was removed
        """
        pass

    # =============================================================================
    # CONFIGURATION METHODS
    # =============================================================================

    @abstractmethod
    def configure(self, **options: Any) -> None:
        """
        Configure serialization options.
        
        Supported options:
        - compression: "gzip", "zstd", "lz4", None
        - compression_level: int (1-9)
        - safe_mode: bool (enable security limits)
        - canonical: bool (enable canonical output)
        - tracing: bool (enable performance tracing)
        - workers: int (parallel processing workers)
        - thread_safe: bool (enable thread safety)

        Args:
            **options: Configuration options specific to format
        """
        pass

    @abstractmethod
    def reset_configuration(self) -> None:
        """Reset configuration to defaults."""
        pass

    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Current configuration dictionary
        """
        pass

    # =============================================================================
    # VERSIONING
    # =============================================================================

    @abstractmethod
    def format_version(self) -> str:
        """
        Get current format version.
        
        Returns:
            Format version string
        """
        pass

    @abstractmethod
    def set_target_version(self, version: str) -> None:
        """
        Set target format version for serialization.
        
        Args:
            version: Target version string
        """
        pass

    # =============================================================================
    # CONTEXT MANAGER
    # =============================================================================

    def __enter__(self):
        """Enter context manager for resource management."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, cleaning up resources."""
        pass

    # =============================================================================
    # ASYNC SERIALIZATION METHODS
    # =============================================================================

    @abstractmethod
    async def dumps_async(self, data: Any) -> Union[str, bytes]:
        """
        Serialize data to string or bytes asynchronously.
        
        Args:
            data: Data to serialize
            
        Returns:
            Serialized string for text formats, bytes for binary formats
            
        Raises:
            SerializationError: If serialization fails
        """
        pass

    @abstractmethod
    async def dumps_text_async(self, data: Any) -> str:
        """
        Serialize data to text string asynchronously.
        
        Args:
            data: Data to serialize
            
        Returns:
            Serialized text string
            
        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on binary format
        """
        pass

    @abstractmethod
    async def dumps_binary_async(self, data: Any) -> bytes:
        """
        Serialize data to bytes asynchronously.
        
        Args:
            data: Data to serialize
            
        Returns:
            Serialized bytes
            
        Raises:
            SerializationError: If serialization fails
            NotImplementedError: If called on text format
        """
        pass

    @abstractmethod
    async def loads_async(self, data: Union[str, bytes]) -> Any:
        """
        Deserialize from string or bytes asynchronously.
        
        Args:
            data: String or bytes to deserialize
            
        Returns:
            Deserialized Python object
            
        Raises:
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    async def loads_text_async(self, data: str) -> Any:
        """
        Deserialize from text string asynchronously.
        
        Args:
            data: Text string to deserialize
            
        Returns:
            Deserialized Python object
            
        Raises:
            SerializationError: If deserialization fails
        """
        pass

    @abstractmethod
    async def loads_bytes_async(self, data: bytes) -> Any:
        """
        Deserialize from bytes asynchronously.
        
        Args:
            data: Bytes to deserialize
            
        Returns:
            Deserialized Python object
            
        Raises:
            SerializationError: If deserialization fails
            NotImplementedError: If called on text-only format
        """
        pass

    # =============================================================================
    # ASYNC FILE OPERATIONS
    # =============================================================================

    @abstractmethod
    async def save_file_async(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Save data to file asynchronously.
        
        Args:
            data: Data to serialize
            file_path: Path to save file
            
        Raises:
            SerializationError: If saving fails
        """
        pass

    @abstractmethod
    async def load_file_async(self, file_path: Union[str, Path]) -> Any:
        """
        Load data from file asynchronously.
        
        Args:
            file_path: Path to load from
            
        Returns:
            Deserialized Python object
            
        Raises:
            SerializationError: If loading fails
        """
        pass

    # =============================================================================
    # ASYNC STREAMING METHODS
    # =============================================================================

    @abstractmethod
    async def stream_serialize(self, data: Any, chunk_size: int = 8192) -> AsyncIterator[Union[str, bytes]]:
        """
        Stream serialize data in chunks asynchronously.
        
        Args:
            data: Data to serialize
            chunk_size: Size of each chunk
            
        Yields:
            Serialized chunks
            
        Raises:
            SerializationError: If serialization fails
        """
        pass

    @abstractmethod
    async def stream_deserialize(self, data_stream: AsyncIterator[Union[str, bytes]]) -> Any:
        """
        Stream deserialize data from chunks asynchronously.
        
        Args:
            data_stream: Async iterator of data chunks
            
        Returns:
            Deserialized Python object
            
        Raises:
            SerializationError: If deserialization fails
        """
        pass

    # =============================================================================
    # ASYNC BATCH OPERATIONS
    # =============================================================================

    @abstractmethod
    async def serialize_batch(self, data_list: List[Any]) -> List[Union[str, bytes]]:
        """
        Serialize multiple objects in batch asynchronously.
        
        Args:
            data_list: List of objects to serialize
            
        Returns:
            List of serialized data
            
        Raises:
            SerializationError: If any serialization fails
        """
        pass

    @abstractmethod
    async def deserialize_batch(self, data_list: List[Union[str, bytes]]) -> List[Any]:
        """
        Deserialize multiple objects in batch asynchronously.
        
        Args:
            data_list: List of serialized data
            
        Returns:
            List of deserialized objects
            
        Raises:
            SerializationError: If any deserialization fails
        """
        pass

    @abstractmethod
    async def save_batch_files(self, data_dict: Dict[Union[str, Path], Any]) -> None:
        """
        Save multiple files in batch asynchronously.
        
        Args:
            data_dict: Dictionary mapping file paths to data
            
        Raises:
            SerializationError: If any save fails
        """
        pass

    @abstractmethod
    async def load_batch_files(self, file_paths: List[Union[str, Path]]) -> Dict[Union[str, Path], Any]:
        """
        Load multiple files in batch asynchronously.
        
        Args:
            file_paths: List of file paths to load
            
        Returns:
            Dictionary mapping file paths to loaded data
            
        Raises:
            SerializationError: If any load fails
        """
        pass

    # =============================================================================
    # ASYNC VALIDATION METHODS
    # =============================================================================

    @abstractmethod
    async def validate_data_async(self, data: Any) -> bool:
        """
        Validate data for serialization compatibility asynchronously.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data can be serialized
            
        Raises:
            SerializationError: If validation fails
        """
        pass

    @abstractmethod
    async def estimate_size_async(self, data: Any) -> int:
        """
        Estimate serialized size in bytes asynchronously.
        
        Args:
            data: Data to estimate
            
        Returns:
            Estimated size in bytes
        """
        pass


# ============================================================================
# SERIALIZABLE OBJECT INTERFACE
# ============================================================================

class ISerializable(ABC):
    """
    Interface for objects that can be serialized/deserialized.
    
    Enforces consistent serialization across XWSystem.
    """
    
    @abstractmethod
    def serialize(self, format: SerializationFormat = SerializationFormat.NATIVE) -> Union[str, bytes]:
        """
        Serialize object to string or bytes.
        
        Args:
            format: Serialization format
            
        Returns:
            Serialized data
        """
        pass
    
    @abstractmethod
    def deserialize(self, data: Union[str, bytes], format: SerializationFormat = SerializationFormat.NATIVE) -> 'ISerializable':
        """
        Deserialize from string or bytes.
        
        Args:
            data: Serialized data
            format: Serialization format
            
        Returns:
            New instance created from serialized data
        """
        pass
    
    @abstractmethod
    def to_string(self, format: SerializationFormat = SerializationFormat.JSON) -> str:
        """
        Convert to string representation.
        
        Args:
            format: String format
            
        Returns:
            String representation
        """
        pass
    
    @abstractmethod
    def from_string(self, data: str, format: SerializationFormat = SerializationFormat.JSON) -> 'ISerializable':
        """
        Create from string representation.
        
        Args:
            data: String data
            format: String format
            
        Returns:
            New instance created from string
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[SerializationFormat]:
        """
        Get list of supported serialization formats.
        
        Returns:
            List of supported formats
        """
        pass
    
    @abstractmethod
    def is_serializable(self, format: SerializationFormat) -> bool:
        """
        Check if object can be serialized in given format.
        
        Args:
            format: Format to check
            
        Returns:
            True if serializable
        """
        pass


# ============================================================================
# SERIALIZATION MANAGER INTERFACES
# ============================================================================

class ISerializationManager(ABC):
    """
    Interface for serialization management.
    
    Enforces consistent serialization management across XWSystem.
    """
    
    @abstractmethod
    def register_serializer(self, format: SerializationFormat, serializer: Any) -> None:
        """
        Register serializer for format.
        
        Args:
            format: Serialization format
            serializer: Serializer instance
        """
        pass
    
    @abstractmethod
    def unregister_serializer(self, format: SerializationFormat) -> bool:
        """
        Unregister serializer for format.
        
        Args:
            format: Serialization format
            
        Returns:
            True if unregistered
        """
        pass
    
    @abstractmethod
    def get_serializer(self, format: SerializationFormat) -> Optional[Any]:
        """
        Get serializer for format.
        
        Args:
            format: Serialization format
            
        Returns:
            Serializer instance or None
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[SerializationFormat]:
        """
        Get list of supported formats.
        
        Returns:
            List of supported formats
        """
        pass
    
    @abstractmethod
    def is_format_supported(self, format: SerializationFormat) -> bool:
        """
        Check if format is supported.
        
        Args:
            format: Format to check
            
        Returns:
            True if supported
        """
        pass


# ============================================================================
# SERIALIZATION VALIDATION INTERFACES
# ============================================================================

class ISerializationValidator(ABC):
    """
    Interface for serialization validation.
    
    Enforces consistent serialization validation across XWSystem.
    """
    
    @abstractmethod
    def validate_serializable(self, obj: Any, format: SerializationFormat) -> bool:
        """
        Validate if object is serializable in format.
        
        Args:
            obj: Object to validate
            format: Serialization format
            
        Returns:
            True if serializable
        """
        pass
    
    @abstractmethod
    def validate_serialized_data(self, data: Union[str, bytes], format: SerializationFormat) -> bool:
        """
        Validate serialized data format.
        
        Args:
            data: Serialized data
            format: Serialization format
            
        Returns:
            True if valid
        """
        pass
    
    @abstractmethod
    def get_validation_errors(self, obj: Any, format: SerializationFormat) -> List[str]:
        """
        Get validation errors for object.
        
        Args:
            obj: Object to validate
            format: Serialization format
            
        Returns:
            List of validation errors
        """
        pass


# ============================================================================
# SERIALIZATION PROTOCOLS
# ============================================================================

@runtime_checkable
class Serializable(Protocol):
    """Protocol for objects that can be serialized."""
    
    def dumps(self, data: Any, **kwargs: Any) -> Union[str, bytes]:
        """Serialize data to string or bytes."""
        ...
    
    def loads(self, data: Union[str, bytes], **kwargs: Any) -> Any:
        """Deserialize data from string or bytes."""
        ...


@runtime_checkable
class AsyncSerializable(Protocol):
    """Protocol for objects that support async serialization."""
    
    async def dumps_async(self, data: Any, **kwargs: Any) -> Union[str, bytes]:
        """Asynchronously serialize data to string or bytes."""
        ...
    
    async def loads_async(self, data: Union[str, bytes], **kwargs: Any) -> Any:
        """Asynchronously deserialize data from string or bytes."""
        ...
