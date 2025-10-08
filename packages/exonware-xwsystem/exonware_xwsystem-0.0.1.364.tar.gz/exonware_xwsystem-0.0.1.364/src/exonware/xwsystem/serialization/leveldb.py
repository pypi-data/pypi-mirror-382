#exonware\xsystem\serialization\leveldb.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: January 02, 2025

LevelDB/RocksDB serializer for key-value store operations.
"""

import json
import pickle
from typing import Any, Dict, Iterator, Optional, Union
from pathlib import Path

# Import leveldb libraries - lazy installation system will handle missing dependencies
import rocksdb
import plyvel

from .base import ASerialization
from .errors import SerializationError


class LevelDbError(SerializationError):
    """LevelDB/RocksDB specific serialization errors."""
    pass


class LevelDbSerializer(ASerialization):
    """
    LevelDB/RocksDB serializer for key-value store operations.
    
    Supports both LevelDB and RocksDB backends with automatic detection.
    Optimized for fast partial access and high-throughput operations.
    """
    
    def __init__(self, backend: str = "auto", compression: bool = True):
        """
        Initialize LevelDB/RocksDB serializer.
        
        Args:
            backend: "leveldb", "rocksdb", or "auto" for automatic detection
            compression: Enable compression for better storage efficiency
            
        Raises:
            LevelDbError: If neither rocksdb nor plyvel is available
        """
        # Lazy installation system will handle missing backends automatically
        
        super().__init__()
        self.backend = backend
        self.compression = compression
        self._db = None
        self._db_type = None
        
    def _get_db(self, db_path: Union[str, Path]) -> Any:
        """Get database instance with automatic backend detection."""
        if self._db is not None:
            return self._db
            
        db_path = Path(db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Use RocksDB first (more features), fallback to LevelDB
        if self.backend in ("auto", "rocksdb"):
            self._db = rocksdb.DB(str(db_path), rocksdb.Options(create_if_missing=True))
            self._db_type = "rocksdb"
            return self._db
        
        if self.backend in ("auto", "leveldb"):
            self._db = plyvel.DB(str(db_path), create_if_missing=True)
            self._db_type = "leveldb"
            return self._db
        
        raise LevelDbError("Invalid backend specified")
    
    def dumps(self, data: Any, **kwargs) -> bytes:
        """Serialize data to bytes for key-value storage."""
        try:
            # Use JSON for simple types, pickle for complex objects
            if isinstance(data, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(data).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            raise LevelDbError(f"Serialization failed: {e}")
    
    def loads(self, data: bytes, **kwargs) -> Any:
        """Deserialize bytes from key-value storage."""
        try:
            # Try JSON first, fallback to pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        except Exception as e:
            raise LevelDbError(f"Deserialization failed: {e}")
    
    def put(self, key: str, value: Any, db_path: Union[str, Path]) -> None:
        """Store key-value pair in database."""
        try:
            db = self._get_db(db_path)
            serialized_value = self.dumps(value)
            db.put(key.encode('utf-8'), serialized_value)
        except Exception as e:
            raise LevelDbError(f"Put operation failed: {e}")
    
    def get(self, key: str, db_path: Union[str, Path], default: Any = None) -> Any:
        """Retrieve value by key from database."""
        try:
            db = self._get_db(db_path)
            serialized_value = db.get(key.encode('utf-8'))
            if serialized_value is None:
                return default
            return self.loads(serialized_value)
        except Exception as e:
            raise LevelDbError(f"Get operation failed: {e}")
    
    def delete(self, key: str, db_path: Union[str, Path]) -> bool:
        """Delete key-value pair from database."""
        try:
            db = self._get_db(db_path)
            db.delete(key.encode('utf-8'))
            return True
        except Exception as e:
            raise LevelDbError(f"Delete operation failed: {e}")
    
    def keys(self, db_path: Union[str, Path], prefix: str = "") -> Iterator[str]:
        """Iterate over keys in database."""
        try:
            db = self._get_db(db_path)
            prefix_bytes = prefix.encode('utf-8') if prefix else None
            
            for key_bytes, _ in db:
                key = key_bytes.decode('utf-8')
                if not prefix or key.startswith(prefix):
                    yield key
        except Exception as e:
            raise LevelDbError(f"Keys iteration failed: {e}")
    
    def items(self, db_path: Union[str, Path], prefix: str = "") -> Iterator[tuple]:
        """Iterate over key-value pairs in database."""
        try:
            db = self._get_db(db_path)
            prefix_bytes = prefix.encode('utf-8') if prefix else None
            
            for key_bytes, value_bytes in db:
                key = key_bytes.decode('utf-8')
                if not prefix or key.startswith(prefix):
                    value = self.loads(value_bytes)
                    yield (key, value)
        except Exception as e:
            raise LevelDbError(f"Items iteration failed: {e}")
    
    def close(self) -> None:
        """Close database connection."""
        if self._db is not None:
            try:
                if self._db_type == "rocksdb":
                    self._db.close()
                elif self._db_type == "leveldb":
                    self._db.close()
                self._db = None
                self._db_type = None
            except Exception as e:
                raise LevelDbError(f"Close operation failed: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
