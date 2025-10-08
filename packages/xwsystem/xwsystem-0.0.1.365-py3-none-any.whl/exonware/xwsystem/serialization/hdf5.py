#exonware\xsystem\serialization\hdf5.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: January 02, 2025

HDF5 serializer for hierarchical tree with partial fast access.
"""

import json
import numpy as np
from typing import Any, Dict, Optional, Union
from pathlib import Path

# Explicit imports - no try/except blocks per DEV_GUIDELINES.md
import h5py

from .base import ASerialization
from .errors import SerializationError


class Hdf5Error(SerializationError):
    """HDF5 specific serialization errors."""
    pass


class Hdf5Serializer(ASerialization):
    """
    HDF5 serializer for hierarchical tree with partial fast access.
    
    Optimized for scientific data with hierarchical structure and fast partial access.
    Supports datasets, groups, and attributes with compression.
    """
    
    def __init__(self, compression: str = "gzip", compression_level: int = 6):
        """
        Initialize HDF5 serializer.
        
        Args:
            compression: Compression algorithm ("gzip", "lzf", "szip", None)
            compression_level: Compression level (1-9 for gzip)
        """
        super().__init__()
        self.compression = compression
        self.compression_level = compression_level
        
    def dumps(self, data: Any, **kwargs) -> bytes:
        """Serialize data to HDF5 format in memory."""
        import io
        
        # Create in-memory HDF5 file
        buffer = io.BytesIO()
        
        with h5py.File(buffer, 'w') as f:
            self._write_data(f, data, '/')
        
        return buffer.getvalue()
    
    def loads(self, data: bytes, **kwargs) -> Any:
        """Deserialize data from HDF5 format in memory."""
        import io
        
        buffer = io.BytesIO(data)
        
        with h5py.File(buffer, 'r') as f:
            return self._read_data(f, '/')
    
    def _write_data(self, group: Any, data: Any, path: str) -> None:
        """Write data to HDF5 group."""
        if isinstance(data, dict):
            # Create group for dictionary
            for key, value in data.items():
                new_path = f"{path}/{key}" if path != '/' else f"/{key}"
                if isinstance(value, dict):
                    # Create subgroup
                    subgroup = group.create_group(key)
                    self._write_data(subgroup, value, new_path)
                elif isinstance(value, (list, tuple, np.ndarray)):
                    # Create dataset
                    arr = np.array(value)
                    group.create_dataset(key, data=arr, compression=self.compression,
                                       compression_opts=self.compression_level)
                else:
                    # Store as attribute
                    group.attrs[key] = value
        elif isinstance(data, (list, tuple, np.ndarray)):
            # Direct array
            arr = np.array(data)
            group.create_dataset('data', data=arr, compression=self.compression,
                               compression_opts=self.compression_level)
        else:
            # Scalar value
            group.attrs['value'] = data
    
    def _read_data(self, group: Any, path: str) -> Any:
        """Read data from HDF5 group."""
        if len(group.keys()) == 0 and len(group.attrs) > 0:
            # Leaf node with attributes only
            if len(group.attrs) == 1 and 'value' in group.attrs:
                return group.attrs['value']
            else:
                return dict(group.attrs)
        
        result = {}
        
        # Read datasets
        for key in group.keys():
            dataset = group[key]
            if isinstance(dataset, h5py.Dataset):
                result[key] = np.array(dataset)
            elif isinstance(dataset, h5py.Group):
                result[key] = self._read_data(dataset, f"{path}/{key}")
        
        # Read attributes
        for key, value in group.attrs.items():
            result[key] = value
        
        # If only one dataset named 'data', return it directly
        if len(result) == 1 and 'data' in result:
            return result['data']
        
        return result
    
    def save_file(self, data: Any, file_path: Union[str, Path], **kwargs) -> None:
        """Save data to HDF5 file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with h5py.File(str(file_path), 'w') as f:
            self._write_data(f, data, '/')
    
    def load_file(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load data from HDF5 file."""
        with h5py.File(str(file_path), 'r') as f:
            return self._read_data(f, '/')
    
    def partial_read(self, file_path: Union[str, Path], dataset_path: str, 
                    start: Optional[int] = None, stop: Optional[int] = None) -> Any:
        """Read partial data from HDF5 dataset for fast access."""
        with h5py.File(str(file_path), 'r') as f:
            dataset = f[dataset_path]
            if start is not None or stop is not None:
                return dataset[start:stop]
            return np.array(dataset)
