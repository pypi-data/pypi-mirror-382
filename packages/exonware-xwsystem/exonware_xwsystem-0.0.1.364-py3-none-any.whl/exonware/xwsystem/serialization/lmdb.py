#exonware\xsystem\serialization\lmdb.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: January 02, 2025

LMDB serializer for memory-mapped database operations.
"""

import json
import pickle
from typing import Any, Dict, Iterator, Optional, Union
from pathlib import Path

# Explicit imports - no try/except blocks per DEV_GUIDELINES.md
import lmdb

from .base import ASerialization
from .errors import SerializationError


class LmdbError(SerializationError):
    """LMDB specific serialization errors."""
    pass


class LmdbSerializer(ASerialization):
    """
    LMDB serializer for memory-mapped database operations.
    
    Provides very fast reads through memory mapping and ACID transactions.
    Optimized for high-performance key-value operations.
    """
    
    def __init__(self, map_size: int = 1024**3, max_dbs: int = 0):
        """
        Initialize LMDB serializer.
        
        Args:
            map_size: Maximum size of memory map in bytes (default: 1GB)
            max_dbs: Maximum number of named databases (0 = unlimited)
        """
        super().__init__()
        self.map_size = map_size
        self.max_dbs = max_dbs
        self._env = None
        self._db = None
        
    def _get_env(self, db_path: Union[str, Path]) -> Any:
        """Get LMDB environment."""
        if self._env is not None:
            return self._env
            
        db_path = Path(db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        self._env = lmdb.open(
            str(db_path),
            map_size=self.map_size,
            max_dbs=self.max_dbs
        )
        return self._env
    
    def _get_db(self, db_path: Union[str, Path], db_name: Optional[str] = None) -> Any:
        """Get LMDB database handle."""
        env = self._get_env(db_path)
        
        if db_name:
            return env.open_db(db_name.encode('utf-8'))
        return None
    
    def dumps(self, data: Any, **kwargs) -> bytes:
        """Serialize data to bytes for LMDB storage."""
        try:
            # Use JSON for simple types, pickle for complex objects
            if isinstance(data, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(data).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            raise LmdbError(f"Serialization failed: {e}")
    
    def loads(self, data: bytes, **kwargs) -> Any:
        """Deserialize bytes from LMDB storage."""
        try:
            # Try JSON first, fallback to pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        except Exception as e:
            raise LmdbError(f"Deserialization failed: {e}")
    
    def put(self, key: str, value: Any, db_path: Union[str, Path], db_name: Optional[str] = None) -> None:
        """Store key-value pair in LMDB with transaction."""
        try:
            env = self._get_env(db_path)
            db = self._get_db(db_path, db_name)
            
            with env.begin(write=True) as txn:
                serialized_value = self.dumps(value)
                txn.put(key.encode('utf-8'), serialized_value, db=db)
        except Exception as e:
            raise LmdbError(f"Put operation failed: {e}")
    
    def get(self, key: str, db_path: Union[str, Path], db_name: Optional[str] = None, default: Any = None) -> Any:
        """Retrieve value by key from LMDB with transaction."""
        try:
            env = self._get_env(db_path)
            db = self._get_db(db_path, db_name)
            
            with env.begin() as txn:
                serialized_value = txn.get(key.encode('utf-8'), db=db)
                if serialized_value is None:
                    return default
                return self.loads(serialized_value)
        except Exception as e:
            raise LmdbError(f"Get operation failed: {e}")
    
    def delete(self, key: str, db_path: Union[str, Path], db_name: Optional[str] = None) -> bool:
        """Delete key-value pair from LMDB with transaction."""
        try:
            env = self._get_env(db_path)
            db = self._get_db(db_path, db_name)
            
            with env.begin(write=True) as txn:
                return txn.delete(key.encode('utf-8'), db=db)
        except Exception as e:
            raise LmdbError(f"Delete operation failed: {e}")
    
    def keys(self, db_path: Union[str, Path], db_name: Optional[str] = None, prefix: str = "") -> Iterator[str]:
        """Iterate over keys in LMDB."""
        try:
            env = self._get_env(db_path)
            db = self._get_db(db_path, db_name)
            
            with env.begin() as txn:
                cursor = txn.cursor(db=db)
                cursor.first()
                
                for key_bytes, _ in cursor:
                    key = key_bytes.decode('utf-8')
                    if not prefix or key.startswith(prefix):
                        yield key
        except Exception as e:
            raise LmdbError(f"Keys iteration failed: {e}")
    
    def items(self, db_path: Union[str, Path], db_name: Optional[str] = None, prefix: str = "") -> Iterator[tuple]:
        """Iterate over key-value pairs in LMDB."""
        try:
            env = self._get_env(db_path)
            db = self._get_db(db_path, db_name)
            
            with env.begin() as txn:
                cursor = txn.cursor(db=db)
                cursor.first()
                
                for key_bytes, value_bytes in cursor:
                    key = key_bytes.decode('utf-8')
                    if not prefix or key.startswith(prefix):
                        value = self.loads(value_bytes)
                        yield (key, value)
        except Exception as e:
            raise LmdbError(f"Items iteration failed: {e}")
    
    def close(self) -> None:
        """Close LMDB environment."""
        if self._env is not None:
            try:
                self._env.close()
                self._env = None
                self._db = None
            except Exception as e:
                raise LmdbError(f"Close operation failed: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
