#exonware\xwsystem\serialization\yaml.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

Enhanced YAML serialization with security, validation and performance optimizations.
"""

import sys
import hashlib
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional, Union, TextIO, BinaryIO, Iterator, Iterable, Callable, Set
from io import StringIO

from .base import ASerialization
from .contracts import SerializationCapability, SerializationFormat, FormatDetectionError, ValidationError
from .errors import SerializationError
from ..config.logging_setup import get_logger

logger = get_logger("xwsystem.serialization.yaml")

# Import YAML libraries - lazy installation system will handle missing dependencies
import yaml
from yaml import SafeLoader, SafeDumper
import ruamel.yaml
import msgspec
import xxhash


class YamlError(SerializationError):
    """YAML-specific serialization error."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "YAML", original_error)


class YamlSerializer(ASerialization):
    """
    Enhanced YAML serializer with security validation, custom encoders,
    and performance optimizations for production use.
    
    Supports all audit features:
    - Partial access via key paths
    - Streaming via chunked processing
    - Typed decoding
    - Patching via key updates
    - Schema validation
    - Canonical serialization
    - Checksums and verification
    """
    
    __slots__ = ('default_flow_style', 'sort_keys', 'width', 'indent', 'canonical', 'type_adapters', 'target_version', 'use_ruamel')

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        default_flow_style: Optional[bool] = None,
        sort_keys: bool = False,
        width: Optional[int] = None,
        indent: int = 2,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        canonical: bool = False,
        use_ruamel: bool = True,
    ) -> None:
        """
        Initialize YAML serializer with security and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            default_flow_style: Whether to use flow style for collections
            sort_keys: Whether to sort dictionary keys
            width: Maximum line width
            indent: Indentation level
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
            canonical: Whether to use canonical serialization
            use_ruamel: Whether to use ruamel.yaml for performance (if available)
        """
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path
        )
        
        self.default_flow_style = default_flow_style
        self.sort_keys = sort_keys or canonical
        self.width = width
        self.indent = indent
        self.canonical = canonical
        self.use_ruamel = use_ruamel  # Lazy install handles ruamel availability
        self.type_adapters: Dict[type, tuple[Callable, Callable]] = {}
        self.target_version = "1.0"
        
        # Register default type adapters
        self._register_default_adapters()

    # =============================================================================
    # PROPERTIES
    # =============================================================================

    @property
    def format_name(self) -> str:
        """Get the serialization format name."""
        return "YAML"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions for this format."""
        return [".yaml", ".yml"]

    @property
    def mime_type(self) -> str:
        """Get the MIME type for this serialization format."""
        return "application/x-yaml"

    @property
    def is_binary_format(self) -> bool:
        """Whether this is a binary format."""
        return False

    @property
    def supports_streaming(self) -> bool:
        """Whether streaming is supported."""
        return True

    def capabilities(self) -> Set[SerializationCapability]:
        """Get set of capabilities supported by this format."""
        caps = {SerializationCapability.STREAMING}
        
        if self.canonical or self.sort_keys:
            caps.add(SerializationCapability.CANONICAL)
        
        return caps

    # =============================================================================
    # FORMAT DETECTION
    # =============================================================================

    def sniff_format(self, src: Union[str, bytes, Path, TextIO, BinaryIO]) -> SerializationFormat:
        """Auto-detect format from data source."""
        try:
            if isinstance(src, str):
                # Check if it's a file path or YAML string
                if len(src) > 260 or '\n' in src or src.strip().startswith('-') or ':' in src:
                    # Likely YAML string
                    content = src[:1024]
                else:
                    # Likely file path
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read(1024)
            elif isinstance(src, Path):
                with open(src, 'r', encoding='utf-8') as f:
                    content = f.read(1024)
            elif isinstance(src, bytes):
                content = src[:1024].decode('utf-8', errors='ignore')
            elif hasattr(src, 'read'):
                content = src.read(1024)
                if hasattr(src, 'seek'):
                    src.seek(0)
            else:
                raise FormatDetectionError("Unsupported source type")
            
            # Try to parse as YAML
            # Lazy install handles library availability
            if self.use_ruamel:
                yaml_obj = ruamel.yaml.YAML()
                yaml_obj.load(content)
            else:
                yaml.safe_load(content)
            
            return SerializationFormat.YAML
        except Exception as e:
            raise FormatDetectionError(f"Failed to detect YAML format: {e}")

    # =============================================================================
    # CORE SERIALIZATION METHODS
    # =============================================================================

    def dumps_text(self, data: Any) -> str:
        """Serialize data to text string."""
        try:
            if self.validate_input and self._data_validator:
                self._data_validator.validate_data_structure(data)
            
            if self.use_ruamel:
                yaml_obj = ruamel.yaml.YAML()
                yaml_obj.default_flow_style = self.default_flow_style
                yaml_obj.width = self.width
                yaml_obj.indent = self.indent
                
                string_stream = StringIO()
                yaml_obj.dump(data, string_stream)
                return string_stream.getvalue()
            else:
                return yaml.dump(
                    data,
                    default_flow_style=self.default_flow_style,
                    sort_keys=self.sort_keys,
                    width=self.width,
                    indent=self.indent,
                    Dumper=SafeDumper
                )
        except Exception as e:
            raise YamlError(f"YAML serialization failed: {e}", e)

    def dumps_binary(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        try:
            if self.validate_input and self._data_validator:
                self._data_validator.validate_data_structure(data)
            
            text = self.dumps_text(data)
            return text.encode('utf-8')
        except Exception as e:
            raise YamlError(f"YAML serialization failed: {e}", e)

    def loads_text(self, data: str) -> Any:
        """Deserialize from text string."""
        try:
            # Lazy install handles library availability
            if self.use_ruamel:
                yaml_obj = ruamel.yaml.YAML()
                return yaml_obj.load(data)
            else:
                return yaml.safe_load(data)
        except Exception as e:
            raise YamlError(f"YAML deserialization failed: {e}", e)

    def loads_bytes(self, data: bytes) -> Any:
        """Deserialize from bytes."""
        try:
            text = data.decode('utf-8')
            return self.loads_text(text)
        except Exception as e:
            raise YamlError(f"YAML deserialization failed: {e}", e)

    # =============================================================================
    # TYPED DECODING
    # =============================================================================

    def loads_typed(self, data: Union[str, bytes], type_: type) -> Any:
        """Deserialize data to specific type."""
        try:
            # First deserialize to dict
            if isinstance(data, str):
                obj = self.loads_text(data)
            else:
                obj = self.loads_bytes(data)
            
            # Convert to target type
            if hasattr(type_, '__annotations__'):  # dataclass
                import dataclasses
                if dataclasses.is_dataclass(type_):
                    return type_(**obj)
            
            # For other types, try direct conversion
            if isinstance(obj, dict) and hasattr(type_, '__init__'):
                return type_(**obj)
            elif isinstance(obj, (list, tuple)) and hasattr(type_, '__init__'):
                return type_(*obj)
            else:
                return type_(obj)
                
        except Exception as e:
            raise ValidationError(f"Failed to convert to type {type_.__name__}: {e}")

    # =============================================================================
    # PATH-BASED ACCESS (Partial Access)
    # =============================================================================

    def get_at(self, data: Union[str, bytes], path: str) -> Any:
        """Get value at specific path using dot notation."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse YAML
            obj = self.loads_text(data)
            
            # Navigate using dot notation
            keys = path.split('.')
            current = obj
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                elif isinstance(current, list) and key.isdigit():
                    index = int(key)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    return None
            
            return current
        except Exception as e:
            raise SerializationError(f"Failed to get value at path '{path}': {e}")

    def set_at(self, data: Union[str, bytes], path: str, value: Any) -> Union[str, bytes]:
        """Set value at specific path using dot notation."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse YAML
            obj = self.loads_text(data)
            
            # Navigate and set using dot notation
            keys = path.split('.')
            current = obj
            
            for key in keys[:-1]:
                if isinstance(current, dict):
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                elif isinstance(current, list) and key.isdigit():
                    index = int(key)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return data  # Can't set in non-existent list index
                else:
                    return data  # Can't navigate further
            
            # Set the final value
            if isinstance(current, dict):
                current[keys[-1]] = value
            elif isinstance(current, list) and keys[-1].isdigit():
                index = int(keys[-1])
                if 0 <= index < len(current):
                    current[index] = value
            
            # Serialize back
            result = self.dumps_text(obj)
            return result.encode('utf-8') if isinstance(data, bytes) else result
        except Exception as e:
            raise SerializationError(f"Failed to set value at path '{path}': {e}")

    def iter_path(self, data: Union[str, bytes], path: str) -> Iterator[Any]:
        """Iterate over values matching path expression."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse YAML
            obj = self.loads_text(data)
            
            # Simple path matching (YAML doesn't have complex path expressions)
            if path == '*':
                # Return all values
                def _iter_dict(d):
                    for v in d.values():
                        if isinstance(v, dict):
                            yield from _iter_dict(v)
                        else:
                            yield v
                yield from _iter_dict(obj)
            else:
                # Single path
                value = self.get_at(data, path)
                if value is not None:
                    yield value
        except Exception as e:
            raise SerializationError(f"Failed to iterate path '{path}': {e}")

    # =============================================================================
    # PATCHING
    # =============================================================================

    def apply_patch(self, data: Union[str, bytes], patch: Any, rfc: str = "6902") -> Union[str, bytes]:
        """Apply patch to serialized data."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse YAML
            obj = self.loads_text(data)
            
            # Apply patch operations (simplified for YAML)
            if isinstance(patch, list):
                for op in patch:
                    if op.get('op') == 'replace' and 'path' in op:
                        path = op['path']
                        value = op.get('value', '')
                        # Set value at path
                        self.set_at(data, path, value)
                    elif op.get('op') == 'add' and 'path' in op:
                        path = op['path']
                        value = op.get('value', '')
                        # Add value at path
                        self.set_at(data, path, value)
                    elif op.get('op') == 'remove' and 'path' in op:
                        path = op['path']
                        # Remove value at path (simplified)
                        keys = path.split('.')
                        current = obj
                        for key in keys[:-1]:
                            current = current[key]
                        if keys[-1] in current:
                            del current[keys[-1]]
            
            # Serialize back
            result = self.dumps_text(obj)
            return result.encode('utf-8') if isinstance(data, bytes) else result
        except Exception as e:
            raise SerializationError(f"Failed to apply patch: {e}")

    # =============================================================================
    # SCHEMA VALIDATION
    # =============================================================================

    def validate_schema(self, data: Union[str, bytes], schema: Any, dialect: str = "yaml") -> bool:
        """Validate data against schema."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse YAML
            obj = self.loads_text(data)
            
            if dialect == "yaml":
                # Simple YAML validation - check required keys
                if isinstance(schema, dict):
                    for key, expected_type in schema.items():
                        if key not in obj:
                            return False
                        if not isinstance(obj[key], expected_type):
                            return False
                return True
            else:
                raise SerializationError(f"Unsupported schema dialect: {dialect}")
        except Exception as e:
            raise ValidationError(f"Schema validation failed: {e}")

    # =============================================================================
    # CANONICAL SERIALIZATION
    # =============================================================================

    def canonicalize(self, data: Any) -> Union[str, bytes]:
        """Create canonical representation of data."""
        try:
            # Use sorted keys and consistent formatting
            canonical = self.dumps_text(data)
            return canonical.encode('utf-8') if self.is_binary_format else canonical
        except Exception as e:
            raise SerializationError(f"Canonicalization failed: {e}")

    def hash_stable(self, data: Any, algorithm: str = "sha256") -> str:
        """Generate stable hash of data using canonical representation."""
        try:
            canonical = self.canonicalize(data)
            if isinstance(canonical, str):
                canonical = canonical.encode('utf-8')
            
            if algorithm == "sha256":
                return hashlib.sha256(canonical).hexdigest()
            elif algorithm == "xxh3":
                return xxhash.xxh3_64(canonical).hexdigest()
            else:
                return hashlib.new(algorithm, canonical).hexdigest()
        except Exception as e:
            raise SerializationError(f"Hash generation failed: {e}")

    # =============================================================================
    # CHECKSUMS
    # =============================================================================

    def checksum(self, data: Any, algorithm: str = "sha256") -> str:
        """Calculate checksum of serialized data."""
        try:
            serialized = self.dumps(data)
            if isinstance(serialized, str):
                serialized = serialized.encode('utf-8')
            
            if algorithm == "sha256":
                return hashlib.sha256(serialized).hexdigest()
            elif algorithm == "xxh3":
                return xxhash.xxh3_64(serialized).hexdigest()
            else:
                return hashlib.new(algorithm, serialized).hexdigest()
        except Exception as e:
            raise SerializationError(f"Checksum calculation failed: {e}")

    def verify_checksum(self, data: Union[str, bytes], expected_checksum: str, algorithm: str = "sha256") -> bool:
        """Verify checksum of serialized data."""
        try:
            calculated = self.checksum(data, algorithm)
            return calculated == expected_checksum
        except Exception as e:
            raise SerializationError(f"Checksum verification failed: {e}")

    # =============================================================================
    # SYNC STREAMING
    # =============================================================================

    def iter_serialize(self, data: Any, chunk_size: int = 8192) -> Iterator[Union[str, bytes]]:
        """Stream serialize data in chunks synchronously."""
        try:
            serialized = self.dumps(data)
            if isinstance(serialized, str):
                serialized = serialized.encode('utf-8')
            
            for i in range(0, len(serialized), chunk_size):
                yield serialized[i:i + chunk_size]
        except Exception as e:
            raise SerializationError(f"Stream serialization failed: {e}")

    def iter_deserialize(self, src: Union[TextIO, BinaryIO, Iterable[Union[str, bytes]]]) -> Any:
        """Stream deserialize data from chunks synchronously."""
        try:
            if hasattr(src, 'read'):
                # File-like object
                content = src.read()
                if isinstance(content, bytes):
                    return self.loads_bytes(content)
                else:
                    return self.loads_text(content)
            else:
                # Iterable of chunks
                chunks = []
                for chunk in src:
                    chunks.append(chunk)
                
                if chunks and isinstance(chunks[0], bytes):
                    return self.loads_bytes(b''.join(chunks))
                else:
                    return self.loads_text(''.join(chunks))
        except Exception as e:
            raise SerializationError(f"Stream deserialization failed: {e}")

    # =============================================================================
    # BATCH STREAMING (Not applicable to YAML)
    # =============================================================================

    def serialize_ndjson(self, rows: Iterable[Any]) -> Iterator[str]:
        """Serialize iterable to YAML (not NDJSON)."""
        # YAML doesn't have NDJSON equivalent, but we can create multiple YAML documents
        try:
            for i, row in enumerate(rows):
                yaml_doc = self.dumps_text(row)
                yield f"--- # Document {i}\n{yaml_doc}\n"
        except Exception as e:
            raise SerializationError(f"YAML batch serialization failed: {e}")

    def deserialize_ndjson(self, lines: Iterable[str]) -> Iterator[Any]:
        """Deserialize YAML documents from lines."""
        try:
            current_doc = []
            for line in lines:
                line = line.strip()
                if line.startswith('--- # Document'):
                    # Start of new document
                    if current_doc:
                        yield self.loads_text('\n'.join(current_doc))
                        current_doc = []
                elif line:
                    current_doc.append(line)
            
            # Process last document
            if current_doc:
                yield self.loads_text('\n'.join(current_doc))
        except Exception as e:
            raise SerializationError(f"YAML batch deserialization failed: {e}")

    # =============================================================================
    # TYPE ADAPTERS
    # =============================================================================

    def register_type_adapter(self, typ: type, to_fn: Callable[[Any], Any], from_fn: Callable[[Any], Any]) -> None:
        """Register custom type adapter for serialization."""
        self.type_adapters[typ] = (to_fn, from_fn)

    def unregister_type_adapter(self, typ: type) -> bool:
        """Unregister type adapter."""
        if typ in self.type_adapters:
            del self.type_adapters[typ]
            return True
        return False

    def _register_default_adapters(self) -> None:
        """Register default type adapters."""
        # Decimal
        self.register_type_adapter(
            Decimal,
            lambda x: str(x),
            lambda x: Decimal(x)
        )
        
        # Path
        self.register_type_adapter(
            Path,
            lambda x: str(x),
            lambda x: Path(x)
        )

    # =============================================================================
    # VERSIONING
    # =============================================================================

    def format_version(self) -> str:
        """Get current format version."""
        return self.target_version

    def set_target_version(self, version: str) -> None:
        """Set target format version for serialization."""
        self.target_version = version

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _custom_encoder(self, obj: Any) -> Any:
        """Custom encoder for non-standard types."""
        # Check type adapters first
        for typ, (to_fn, _) in self.type_adapters.items():
            if isinstance(obj, typ):
                return to_fn(obj)
        
        # Default handling
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        
        raise TypeError(f"Object of type {type(obj).__name__} is not YAML serializable")

    def _custom_decoder(self, obj: Any) -> Any:
        """Custom decoder for non-standard types."""
        # Check type adapters
        for typ, (_, from_fn) in self.type_adapters.items():
            try:
                return from_fn(obj)
            except (TypeError, ValueError):
                continue
        
        return obj
