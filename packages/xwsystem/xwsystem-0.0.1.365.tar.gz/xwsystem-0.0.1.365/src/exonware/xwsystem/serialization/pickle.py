#exonware\xsystem\serialization\pickle.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

Python Pickle Serializer Implementation

Provides Python pickle serialization with protocol version control,
security considerations, and integration with XSystem utilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pickle
import pickletools
import io
from pathlib import Path

from .contracts import ISerialization
from .base import ASerialization

class SecureUnpickler(pickle.Unpickler):
    """
    Secure unpickler that restricts what classes can be loaded.
    """
    
    def __init__(self, file, *, allowed_classes=None, blocked_classes=None):
        super().__init__(file)
        self.allowed_classes = allowed_classes or set()
        self.blocked_classes = blocked_classes or set()
    
    def find_class(self, module, name):
        """
        Override find_class to restrict class loading.
        """
        full_name = f"{module}.{name}"
        
        # Check blocked classes first
        if self.blocked_classes and full_name in self.blocked_classes:
            raise pickle.UnpicklingError(f"Blocked class: {full_name}")
        
        # If allowed_classes is specified, only allow those
        if self.allowed_classes and full_name not in self.allowed_classes:
            raise pickle.UnpicklingError(f"Class not in allowed list: {full_name}")
        
        # Additional security checks for dangerous modules
        dangerous_modules = {
            'subprocess', 'os', 'sys', 'importlib', '__builtin__', 'builtins'
        }
        
        if module in dangerous_modules:
            raise pickle.UnpicklingError(f"Dangerous module blocked: {module}")
        
        return super().find_class(module, name)


class PickleSerializer(ASerialization):
    """
    Python Pickle serializer with security considerations.
    
    Features:
    - Multiple pickle protocol versions
    - Security warnings for untrusted data
    - Compression support
    - Python object serialization
    - Binary format
    - Security validation
    - Atomic file operations
    
    WARNING: Pickle can execute arbitrary code during deserialization.
    Only use with trusted data sources.
    """
    
    def __init__(
        self,
        protocol: int = pickle.HIGHEST_PROTOCOL,
        fix_imports: bool = True,
        buffer_callback: Optional[Any] = None,
        validate_input: bool = True,
        validate_paths: bool = True,
        use_atomic_writes: bool = True,
        max_depth: int = 1000,
        max_size_mb: int = 100,
        allow_unsafe: bool = False,
        allowed_classes: Optional[Set[str]] = None,
        blocked_classes: Optional[Set[str]] = None
    ) -> None:
        """
        Initialize Pickle serializer with enhanced security.
        
        Args:
            protocol: Pickle protocol version (0-5)
            fix_imports: Fix Python 2/3 import compatibility
            buffer_callback: Buffer callback for protocol 5
            validate_input: Enable input data validation
            validate_paths: Enable path security validation
            use_atomic_writes: Use atomic file operations
            max_depth: Maximum nesting depth
            max_size_mb: Maximum data size in MB
            allow_unsafe: Allow potentially unsafe operations
            allowed_classes: Set of allowed class names for deserialization
            blocked_classes: Set of blocked class names for deserialization
        """
        super().__init__(
            validate_input=validate_input,
            validate_paths=validate_paths,
            use_atomic_writes=use_atomic_writes,
            max_depth=max_depth,
            max_size_mb=max_size_mb
        )
        
        self._protocol = protocol
        self._fix_imports = fix_imports
        self._buffer_callback = buffer_callback
        self._allow_unsafe = allow_unsafe
        self._allowed_classes = allowed_classes or set()
        self._blocked_classes = blocked_classes or {
            # Dangerous classes that should be blocked by default
            'subprocess.Popen', 'os.system', '__builtin__.eval', '__builtin__.exec',
            'builtins.eval', 'builtins.exec', 'builtins.compile',
            'importlib.import_module', '__import__'
        }
        
        if not allow_unsafe:
            import warnings
            warnings.warn(
                "⚠️  SECURITY WARNING: Pickle can execute arbitrary code during deserialization. "
                "Only use with trusted data sources. Consider using JSON, MessagePack, or CBOR "
                "for untrusted data. Set allow_unsafe=True to suppress this warning.",
                UserWarning,
                stacklevel=2
            )
    
    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "Pickle"
    
    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return [".pkl", ".pickle", ".p"]
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type."""
        return "application/x-pickle"
    
    @property
    def is_binary_format(self) -> bool:
        """Check if this is a binary format."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def dumps(self, data: Any) -> str:
        """
        Serialize data to pickle and return as base64-encoded string.
        
        Args:
            data: Data to serialize
            
        Returns:
            Base64-encoded pickle string
            
        Raises:
            ValueError: If data validation fails
            pickle.PicklingError: If data cannot be pickled
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            if self._protocol >= 5 and self._buffer_callback:
                result = pickle.dumps(
                    data,
                    protocol=self._protocol,
                    fix_imports=self._fix_imports,
                    buffer_callback=self._buffer_callback
                )
            else:
                result = pickle.dumps(
                    data,
                    protocol=self._protocol,
                    fix_imports=self._fix_imports
                )
            
            # Encode to base64 string for string interface
            import base64
            return base64.b64encode(result).decode('ascii')
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def dumps_binary(self, data: Any) -> bytes:
        """
        Serialize data to pickle bytes directly.
        
        Args:
            data: Data to serialize
            
        Returns:
            Pickle bytes
            
        Raises:
            ValueError: If data validation fails
            pickle.PicklingError: If data cannot be pickled
        """
        if self.validate_input:
            self._validate_data_security(data)
        
        try:
            if self._protocol >= 5 and self._buffer_callback:
                result = pickle.dumps(
                    data,
                    protocol=self._protocol,
                    fix_imports=self._fix_imports,
                    buffer_callback=self._buffer_callback
                )
            else:
                result = pickle.dumps(
                    data,
                    protocol=self._protocol,
                    fix_imports=self._fix_imports
                )
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("serialization", e)
    
    def loads(self, data: Union[bytes, str]) -> Any:
        """Deserialize pickle data."""
        # Convert string to bytes if needed
        if isinstance(data, str):
            import base64
            pickle_bytes = base64.b64decode(data.encode('ascii'))
        else:
            pickle_bytes = data
            
        # Delegate to loads_bytes for actual processing
        return self.loads_bytes(pickle_bytes)
    
    def loads_bytes(self, data: bytes) -> Any:
        """
        Deserialize pickle bytes with enhanced security.
        
        Args:
            data: Pickle bytes to deserialize
            
        Returns:
            Deserialized data
            
        Raises:
            ValueError: If data validation fails
            pickle.UnpicklingError: If security validation fails
            
        WARNING: This can execute arbitrary code. Only use with trusted data.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError(f"Expected bytes or bytearray, got {type(data)}")
        
        if not self._allow_unsafe:
            # Additional security warning
            import warnings
            warnings.warn(
                "⚠️  SECURITY: Unpickling can execute arbitrary code. "
                "Only proceed if you trust the data source.",
                UserWarning,
                stacklevel=2
            )
        
        try:
            # Use secure unpickler if security constraints are specified
            if self._allowed_classes or self._blocked_classes:
                buffer = io.BytesIO(data)
                unpickler = SecureUnpickler(
                    buffer,
                    allowed_classes=self._allowed_classes,
                    blocked_classes=self._blocked_classes
                )
                result = unpickler.load()
            else:
                result = pickle.loads(
                    data,
                    fix_imports=self._fix_imports,
                    encoding="ASCII",
                    errors="strict"
                )
            
            if self.validate_input:
                self._validate_data_security(result)
            
            return result
            
        except Exception as e:
            self._handle_serialization_error("deserialization", e)
    
    # 🎯 OPTIMIZATION: save_file and load_file inherited from base class!
    # Base class automatically handles binary format based on is_binary_format flag
    
    def dump_stream(self, data_stream, file_path: Union[str, Path]) -> None:
        """
        Dump multiple objects to pickle file.
        
        Args:
            data_stream: Iterable of objects to pickle
            file_path: Path to save the file
        """
        file_path = Path(file_path)
        
        if self.validate_paths:
            self._path_validator.validate_path(str(file_path))
        
        if self.use_atomic_writes:
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
            try:
                with open(temp_path, 'wb') as f:
                    pickler = pickle.Pickler(f, protocol=self._protocol)
                    for item in data_stream:
                        if self.validate_input:
                            self._validate_data_security(item)
                        pickler.dump(item)
                temp_path.replace(file_path)
            except Exception:
                if temp_path.exists():
                    temp_path.unlink()
                raise
        else:
            with open(file_path, 'wb') as f:
                pickler = pickle.Pickler(f, protocol=self._protocol)
                for item in data_stream:
                    if self.validate_input:
                        self._validate_data_security(item)
                    pickler.dump(item)
    
    def load_stream(self, file_path: Union[str, Path]):
        """
        Load multiple objects from pickle file.
        
        Args:
            file_path: Path to the file
            
        Yields:
            Loaded objects
        """
        file_path = Path(file_path)
        
        if self.validate_paths:
            self._path_validator.validate_path(str(file_path))
        
        try:
            with open(file_path, 'rb') as f:
                unpickler = pickle.Unpickler(f)
                while True:
                    try:
                        item = unpickler.load()
                        if self.validate_input:
                            self._validate_data_security(item)
                        yield item
                    except EOFError:
                        break
        except FileNotFoundError:
            raise FileNotFoundError(f"Pickle file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to load pickle stream {file_path}: {e}") from e
    
    def optimize(self, data: bytes) -> bytes:
        """
        Optimize pickle data using pickletools.
        
        Args:
            data: Pickle bytes to optimize
            
        Returns:
            Optimized pickle bytes
        """
        output = io.BytesIO()
        pickletools.optimize(io.BytesIO(data), output)
        return output.getvalue()
    
    def disassemble(self, data: bytes) -> str:
        """
        Disassemble pickle data for debugging.
        
        Args:
            data: Pickle bytes to disassemble
            
        Returns:
            Human-readable disassembly
        """
        output = io.StringIO()
        pickletools.dis(io.BytesIO(data), output)
        return output.getvalue()
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get Pickle format schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            "format": "Pickle",
            "version": f"Protocol {self._protocol}",
            "description": "Python native object serialization",
            "features": {
                "binary": True,
                "python_specific": True,
                "arbitrary_objects": True,
                "streaming": True,
                "compression": False,
                "security_risk": True
            },
            "supported_types": [
                "All Python objects (with __reduce__ or picklable)"
            ],
            "protocol": self._protocol,
            "fix_imports": self._fix_imports,
            "allow_unsafe": self._allow_unsafe,
            "file_extensions": list(self.file_extensions),
            "mime_type": self.mime_type,
            "security_warning": "Can execute arbitrary code during deserialization"
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current serializer configuration.
        
        Returns:
            Configuration dictionary
        """
        config = super().get_config()
        config.update({
            "protocol": self._protocol,
            "fix_imports": self._fix_imports,
            "allow_unsafe": self._allow_unsafe
        })
        return config


# Module-level convenience functions for consistent API
def dumps(data: Any, **kwargs: Any) -> str:
    """Serialize data to Pickle string (base64-encoded) with default settings."""
    serializer = PickleSerializer(**kwargs)
    return serializer.dumps(data)


def loads(s: str, **kwargs: Any) -> Any:
    """Deserialize Pickle string with default settings."""
    serializer = PickleSerializer(**kwargs)
    return serializer.loads(s)


def dumps_bytes(data: Any, **kwargs: Any) -> bytes:
    """Serialize data to Pickle bytes with default settings."""
    serializer = PickleSerializer(**kwargs)
    return serializer.dumps_binary(data)


def loads_bytes(data: bytes, **kwargs: Any) -> Any:
    """Deserialize Pickle bytes with default settings."""
    serializer = PickleSerializer(**kwargs)
    return serializer.loads_bytes(data)


def load_file(file_path: Union[str, Path], **kwargs: Any) -> Any:
    """Load Pickle from file with default settings."""
    serializer = PickleSerializer(**kwargs)
    return serializer.load_file(file_path)


def save_file(data: Any, file_path: Union[str, Path], **kwargs: Any) -> None:
    """Save data to Pickle file with default settings."""
    serializer = PickleSerializer(**kwargs)
    return serializer.save_file(data, file_path)


# Error classes for consistency with other serializers
class PickleError(Exception):
    """Base exception for Pickle serialization errors."""
    pass
