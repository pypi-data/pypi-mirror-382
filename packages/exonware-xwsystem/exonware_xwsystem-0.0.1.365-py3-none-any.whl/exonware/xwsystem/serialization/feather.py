#exonware\xsystem\serialization\feather.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: January 02, 2025

Feather/Arrow serializer for columnar zero-copy fast I/O.
"""

import json
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, Union
from pathlib import Path

# Explicit imports - no try/except blocks per DEV_GUIDELINES.md
import pyarrow as pa
import pyarrow.feather as feather

from .base import ASerialization
from .errors import SerializationError


class FeatherError(SerializationError):
    """Feather/Arrow specific serialization errors."""
    pass


class FeatherSerializer(ASerialization):
    """
    Feather/Arrow serializer for columnar zero-copy fast I/O.
    
    Optimized for fast columnar data storage with zero-copy memory mapping.
    Supports pandas DataFrames and Arrow tables with compression.
    """
    
    def __init__(self, compression: str = "lz4", compression_level: int = 1):
        """
        Initialize Feather serializer.
        
        Args:
            compression: Compression algorithm ("lz4", "zstd", "uncompressed")
            compression_level: Compression level (1-22 for zstd, 1-9 for lz4)
        """
        super().__init__()
        self.compression = compression
        self.compression_level = compression_level
        
    def dumps(self, data: Any, **kwargs) -> bytes:
        """Serialize data to Feather format in memory."""
        import io
        
        # Convert to Arrow table
        if isinstance(data, pd.DataFrame):
            table = pa.Table.from_pandas(data)
        elif isinstance(data, dict):
            # Convert dict to DataFrame then to Arrow
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df)
        elif isinstance(data, (list, tuple)):
            # Convert list to DataFrame then to Arrow
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df)
        else:
            # Try to convert to DataFrame
            df = pd.DataFrame([data])
            table = pa.Table.from_pandas(df)
        
        # Write to memory buffer
        buffer = io.BytesIO()
        feather.write_feather(table, buffer, compression=self.compression,
                            compression_level=self.compression_level)
        return buffer.getvalue()
    
    def loads(self, data: bytes, **kwargs) -> Any:
        """Deserialize data from Feather format in memory."""
        import io
        
        buffer = io.BytesIO(data)
        table = feather.read_table(buffer)
        
        # Convert to pandas DataFrame
        return table.to_pandas()
    
    def save_file(self, data: Any, file_path: Union[str, Path], **kwargs) -> None:
        """Save data to Feather file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to Arrow table
        if isinstance(data, pd.DataFrame):
            table = pa.Table.from_pandas(data)
        elif isinstance(data, dict):
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df)
        elif isinstance(data, (list, tuple)):
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df)
        else:
            df = pd.DataFrame([data])
            table = pa.Table.from_pandas(df)
        
        feather.write_feather(table, str(file_path), compression=self.compression,
                            compression_level=self.compression_level)
    
    def load_file(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load data from Feather file."""
        table = feather.read_table(str(file_path))
        return table.to_pandas()
    
    def load_arrow_table(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load data as Arrow table for zero-copy operations."""
        return feather.read_table(str(file_path))
    
    def save_arrow_table(self, table: Any, file_path: Union[str, Path], **kwargs) -> None:
        """Save Arrow table to Feather file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        feather.write_feather(table, str(file_path), compression=self.compression,
                            compression_level=self.compression_level)
    
    def memory_map(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Memory map Feather file for zero-copy access."""
        # Memory map the file
        source = pa.memory_map(str(file_path))
        table = feather.read_table(source)
        return table
