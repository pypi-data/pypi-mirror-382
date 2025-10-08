#exonware\xsystem\serialization\zarr.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: January 02, 2025

Zarr serializer for chunked compressed arrays.
"""

import json
import numpy as np
from typing import Any, Dict, Optional, Union
from pathlib import Path

# Explicit imports - no try/except blocks per DEV_GUIDELINES.md
import zarr

from .base import ASerialization
from .errors import SerializationError


class ZarrError(SerializationError):
    """Zarr specific serialization errors."""
    pass


class ZarrSerializer(ASerialization):
    """
    Zarr serializer for chunked compressed arrays.
    
    Optimized for cloud-friendly storage with chunked, compressed arrays.
    Similar to HDF5 but more cloud-native and efficient.
    """
    
    def __init__(self, compression: str = "gzip", compression_level: int = 1, chunk_size: int = 1024):
        """
        Initialize Zarr serializer.
        
        Args:
            compression: Compression algorithm ("gzip", "blosc", "lz4", "zstd", None)
            compression_level: Compression level (1-9 for gzip, 1-6 for others)
            chunk_size: Default chunk size for arrays
        """
        super().__init__()
        self.compression = compression
        self.compression_level = compression_level
        self.chunk_size = chunk_size
        
    def dumps(self, data: Any, **kwargs) -> bytes:
        """Serialize data to Zarr format."""
        import io
        
        # Create in-memory Zarr array
        if isinstance(data, np.ndarray):
            # Direct numpy array
            z = zarr.array(data, compression=self.compression, 
                          compression_opts=self.compression_level)
        elif isinstance(data, (list, tuple)):
            # Convert to numpy array
            arr = np.array(data)
            z = zarr.array(arr, compression=self.compression,
                          compression_opts=self.compression_level)
        else:
            # Convert to JSON and store as string
            json_str = json.dumps(data)
            z = zarr.array([json_str], dtype='U', compression=self.compression,
                          compression_opts=self.compression_level)
        
        # Store in memory buffer
        buffer = io.BytesIO()
        zarr.save(buffer, z)
        return buffer.getvalue()
    
    def loads(self, data: bytes, **kwargs) -> Any:
        """Deserialize data from Zarr format."""
        import io
        
        # Load from memory buffer
        buffer = io.BytesIO(data)
        z = zarr.load(buffer)
        
        # Convert back to original format
        if hasattr(z, 'shape') and len(z.shape) == 1 and z.dtype.kind == 'U':
            # JSON string
            return json.loads(z[0])
        else:
            # Numpy array
            return np.array(z)
    
    def save_array(self, data: np.ndarray, path: Union[str, Path], 
                   chunk_size: Optional[int] = None) -> None:
        """Save numpy array to Zarr format on disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        chunk_size = chunk_size or self.chunk_size
        z = zarr.open_array(
            str(path), 
            mode='w',
            shape=data.shape,
            dtype=data.dtype,
            chunks=chunk_size,
            compression=self.compression,
            compression_opts=self.compression_level
        )
        z[:] = data
    
    def load_array(self, path: Union[str, Path]) -> np.ndarray:
        """Load numpy array from Zarr format on disk."""
        z = zarr.open_array(str(path), mode='r')
        return np.array(z)
    
    def save_group(self, data: Dict[str, Any], path: Union[str, Path]) -> None:
        """Save dictionary as Zarr group."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        z = zarr.open_group(str(path), mode='w')
        
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                z[key] = value
            elif isinstance(value, (list, tuple)):
                z[key] = np.array(value)
            else:
                # Store as JSON string
                json_str = json.dumps(value)
                z[key] = np.array([json_str], dtype='U')
    
    def load_group(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load Zarr group as dictionary."""
        z = zarr.open_group(str(path), mode='r')
        result = {}
        
        for key in z.keys():
            value = z[key]
            if hasattr(value, 'dtype') and value.dtype.kind == 'U' and len(value.shape) == 1:
                # JSON string
                result[key] = json.loads(value[0])
            else:
                # Numpy array
                result[key] = np.array(value)
                
        return result
