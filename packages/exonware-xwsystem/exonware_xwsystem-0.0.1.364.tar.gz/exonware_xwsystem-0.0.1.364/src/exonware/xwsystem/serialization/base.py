#exonware/xwsystem/serialization/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Abstract classes for XWSystem serialization.
"""

import sys
import ast
import types
import logging
import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncIterator, BinaryIO, Dict, List, Optional, TextIO, Union, Set, Iterator, Iterable, Callable

from .contracts import ISerialization, SerializationCapability, SerializationFormat, FormatDetectionError, ValidationError as ContractValidationError
from .errors import SerializationError
from ..config.logging_setup import get_logger
from ..io.atomic_file import AtomicFileWriter, safe_read_text, safe_read_bytes, safe_write_text, safe_write_bytes
from ..security.path_validator import PathValidator, PathSecurityError
from ..validation.data_validator import DataValidator, ValidationError
from ..monitoring.performance_validator import performance_monitor

logger = get_logger("xwsystem.serialization.abstracts")




class ASerialization(ISerialization, ABC):
    """
    Abstract base class providing common serialization functionality 
    with XWSystem integration for security, validation, and file operations.
    
    🔄 ASYNC INTEGRATION:
       All serializers automatically inherit async capabilities through the unified
       ISerialization interface. Default async implementations delegate to sync
       methods via asyncio.to_thread(). Override async methods for performance
       when there's a real benefit (file I/O, streaming, network operations).
    
    🚨 IMPLEMENTATION REMINDER FOR ALL SERIALIZERS:
       DO NOT HARDCODE SERIALIZATION LOGIC - USE OFFICIAL LIBRARIES!
       
       Examples of CORRECT implementations:
       ✅ JSON: json.dumps() / json.loads()
       ✅ YAML: yaml.dump() / yaml.safe_load()  
       ✅ TOML: tomli_w.dumps() / tomllib.loads()
       ✅ XML: defusedxml.etree.tostring() / defusedxml.etree.fromstring()
       ✅ BSON: bson.encode() / bson.decode()
       ✅ Pickle: pickle.dumps() / pickle.loads()
       ✅ Marshal: marshal.dumps() / marshal.loads()
       ✅ CSV: csv.writer() / csv.reader()
       
       NEVER write custom parsers/writers for established formats!
    """

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        text_encoding: str = 'utf-8',
        base64_encoding: str = 'ascii',
        allow_unsafe: bool = False,
        enable_sandboxing: bool = True,
        trusted_types: Optional[Set[type]] = None,
    ) -> None:
        """
        Initialize abstract serialization with XWSystem utilities.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation (None for no restriction)
            text_encoding: Text encoding for file operations
            base64_encoding: Base64 encoding for binary data
            allow_unsafe: Whether to allow unsafe operations
            enable_sandboxing: Whether to enable sandboxing
            trusted_types: Set of trusted types for deserialization
        """
        self.validate_input = validate_input
        self.max_depth = max_depth
        self.max_size_mb = max_size_mb
        self.use_atomic_writes = use_atomic_writes
        self.validate_paths = validate_paths
        self.text_encoding = text_encoding
        self.base64_encoding = base64_encoding
        self.allow_unsafe = allow_unsafe
        self.enable_sandboxing = enable_sandboxing
        self.trusted_types = trusted_types or set()
        
        # Initialize XWSystem utilities
        self._path_validator = PathValidator(base_path) if validate_paths else None
        self._data_validator = DataValidator(
            max_dict_depth=max_depth,
            max_path_length=max_size_mb * 1024 * 1024 if max_size_mb else None,
            max_path_depth=max_depth,
            max_resolution_depth=max_depth
        ) if validate_input else None
        
        logger.debug(f"ASerialization initialized for {self.format_name}")

    # =============================================================================
    # PROPERTIES (Must be implemented by subclasses)
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
    # CORE SERIALIZATION METHODS (Must be implemented by subclasses)
    # =============================================================================

    @abstractmethod
    def dumps_text(self, data: Any) -> str:
        """Serialize data to text string."""
        pass

    @abstractmethod
    def dumps_binary(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        pass

    @abstractmethod
    def loads_text(self, data: str) -> Any:
        """Deserialize from text string."""
        pass

    @abstractmethod
    def loads_bytes(self, data: bytes) -> Any:
        """Deserialize from bytes."""
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
    def apply_patch(self, data: Union[str, bytes], patch: Any, rfc: str = "6902") -> Union[str, bytes]:
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
    def validate_schema(self, data: Union[str, bytes], schema: Any, dialect: str = "jsonschema") -> bool:
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
    # IMPLEMENTED METHODS (Common functionality)
    # =============================================================================

    def dumps(self, data: Any) -> Union[str, bytes]:
        """Serialize data to string or bytes based on format type."""
        if self.validate_input and self._data_validator:
            self._data_validator.validate_data_structure(data)
        
        if self.is_binary_format:
            return self.dumps_binary(data)
        else:
            return self.dumps_text(data)

    def loads(self, data: Union[str, bytes]) -> Any:
        """Deserialize from string or bytes."""
        if isinstance(data, str):
            return self.loads_text(data)
        elif isinstance(data, bytes):
            return self.loads_bytes(data)
        else:
            raise SerializationError(f"Invalid data type: {type(data)}")

    def dump(self, data: Any, fp: Union[TextIO, BinaryIO]) -> None:
        """Serialize data to file-like object."""
        if self.is_binary_format:
            if hasattr(fp, 'write') and hasattr(fp, 'mode') and 'b' in fp.mode:
                self.dump_binary(data, fp)
            else:
                # Convert binary to base64 for text file
                binary_data = self.dumps_binary(data)
                base64_data = base64.b64encode(binary_data).decode(self.base64_encoding)
                fp.write(base64_data)
        else:
            if hasattr(fp, 'write') and hasattr(fp, 'mode') and 'b' not in fp.mode:
                self.dump_text(data, fp)
            else:
                # Convert text to bytes for binary file
                text_data = self.dumps_text(data)
                fp.write(text_data.encode(self.text_encoding))

    def dump_text(self, data: Any, fp: TextIO) -> None:
        """Serialize data to text file-like object."""
        text_data = self.dumps_text(data)
        fp.write(text_data)

    def dump_binary(self, data: Any, fp: BinaryIO) -> None:
        """Serialize data to binary file-like object."""
        binary_data = self.dumps_binary(data)
        fp.write(binary_data)

    def load(self, fp: Union[TextIO, BinaryIO]) -> Any:
        """Deserialize from file-like object."""
        if self.is_binary_format:
            if hasattr(fp, 'read') and hasattr(fp, 'mode') and 'b' in fp.mode:
                return self.load_binary(fp)
            else:
                # Read base64 from text file
                base64_data = fp.read()
                binary_data = base64.b64decode(base64_data.encode(self.base64_encoding))
                return self.loads_bytes(binary_data)
        else:
            if hasattr(fp, 'read') and hasattr(fp, 'mode') and 'b' not in fp.mode:
                return self.load_text(fp)
            else:
                # Read text from binary file
                text_data = fp.read().decode(self.text_encoding)
                return self.loads_text(text_data)

    def load_text(self, fp: TextIO) -> Any:
        """Deserialize from text file-like object."""
        text_data = fp.read()
        return self.loads_text(text_data)

    def load_binary(self, fp: BinaryIO) -> Any:
        """Deserialize from binary file-like object."""
        binary_data = fp.read()
        return self.loads_bytes(binary_data)

    def save_file(self, data: Any, file_path: Union[str, Path]) -> None:
        """Save data to file using XWSystem atomic operations."""
        file_path = Path(file_path)
        
        if self.validate_paths and self._path_validator:
            self._path_validator.validate_write_path(file_path)
        
        if self.use_atomic_writes:
            if self.is_binary_format:
                binary_data = self.dumps_binary(data)
                safe_write_bytes(file_path, binary_data)
            else:
                text_data = self.dumps_text(data)
                safe_write_text(file_path, text_data, encoding=self.text_encoding)
        else:
            # Direct write (not recommended for production)
            with open(file_path, 'wb' if self.is_binary_format else 'w', 
                     encoding=None if self.is_binary_format else self.text_encoding) as f:
                self.dump(data, f)

    def load_file(self, file_path: Union[str, Path]) -> Any:
        """Load data from file using XWSystem safe operations."""
        file_path = Path(file_path)
        
        if self.validate_paths and self._path_validator:
            self._path_validator.validate_read_path(file_path)
        
        if self.is_binary_format:
            binary_data = safe_read_bytes(file_path)
            return self.loads_bytes(binary_data)
        else:
            text_data = safe_read_text(file_path, encoding=self.text_encoding)
            return self.loads_text(text_data)

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

    def validate_data(self, data: Any) -> bool:
        """Validate data for serialization compatibility."""
        if self._data_validator:
            try:
                self._data_validator.validate(data)
                return True
            except ValidationError:
                return False
        return True

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information for this serialization format."""
        return {
            'format_name': self.format_name,
            'file_extensions': self.file_extensions,
            'mime_type': self.mime_type,
            'is_binary_format': self.is_binary_format,
            'supports_streaming': self.supports_streaming,
            'text_encoding': self.text_encoding,
            'base64_encoding': self.base64_encoding,
            'max_depth': self.max_depth,
            'max_size_mb': self.max_size_mb,
            'validate_input': self.validate_input,
            'validate_paths': self.validate_paths,
            'use_atomic_writes': self.use_atomic_writes,
            'allow_unsafe': self.allow_unsafe,
            'enable_sandboxing': self.enable_sandboxing
        }

    def estimate_size(self, data: Any) -> int:
        """Estimate serialized size in bytes."""
        try:
            serialized = self.dumps(data)
            return len(serialized) if isinstance(serialized, bytes) else len(serialized.encode(self.text_encoding))
        except Exception:
            # Fallback estimation
            return len(str(data).encode(self.text_encoding))

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

    def configure(self, **options: Any) -> None:
        """Configure serialization options."""
        for key, value in options.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration option: {key}")

    def reset_configuration(self) -> None:
        """Reset configuration to defaults."""
        # Reset to default values
        self.validate_input = True
        self.max_depth = 100
        self.max_size_mb = 10.0
        self.use_atomic_writes = True
        self.validate_paths = True
        self.text_encoding = 'utf-8'
        self.base64_encoding = 'ascii'
        self.allow_unsafe = False
        self.enable_sandboxing = True
        self.trusted_types = set()

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            'validate_input': self.validate_input,
            'max_depth': self.max_depth,
            'max_size_mb': self.max_size_mb,
            'use_atomic_writes': self.use_atomic_writes,
            'validate_paths': self.validate_paths,
            'text_encoding': self.text_encoding,
            'base64_encoding': self.base64_encoding,
            'allow_unsafe': self.allow_unsafe,
            'enable_sandboxing': self.enable_sandboxing,
            'trusted_types': list(self.trusted_types)
        }

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
    # ASYNC METHODS (Default implementations using asyncio.to_thread)
    # =============================================================================

    async def dumps_async(self, data: Any) -> Union[str, bytes]:
        """Serialize data asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.dumps, data)

    async def dumps_text_async(self, data: Any) -> str:
        """Serialize data to text asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.dumps_text, data)

    async def dumps_binary_async(self, data: Any) -> bytes:
        """Serialize data to bytes asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.dumps_binary, data)

    async def loads_async(self, data: Union[str, bytes]) -> Any:
        """Deserialize data asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.loads, data)

    async def loads_text_async(self, data: str) -> Any:
        """Deserialize from text asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.loads_text, data)

    async def loads_bytes_async(self, data: bytes) -> Any:
        """Deserialize from bytes asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.loads_bytes, data)

    async def save_file_async(self, data: Any, file_path: Union[str, Path]) -> None:
        """Save data to file asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.save_file, data, file_path)

    async def load_file_async(self, file_path: Union[str, Path]) -> Any:
        """Load data from file asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.load_file, file_path)

    async def stream_serialize(self, data: Any, chunk_size: int = 8192) -> AsyncIterator[Union[str, bytes]]:
        """Stream serialize data in chunks asynchronously."""
        serialized = await self.dumps_async(data)
        if isinstance(serialized, bytes):
            for i in range(0, len(serialized), chunk_size):
                yield serialized[i:i + chunk_size]
        else:
            encoded = serialized.encode(self.text_encoding)
            for i in range(0, len(encoded), chunk_size):
                yield encoded[i:i + chunk_size].decode(self.text_encoding)

    async def stream_deserialize(self, data_stream: AsyncIterator[Union[str, bytes]]) -> Any:
        """Stream deserialize data from chunks asynchronously."""
        chunks = []
        async for chunk in data_stream:
            chunks.append(chunk)
        
        if self.is_binary_format:
            return await self.loads_bytes_async(b''.join(chunks))
        else:
            return await self.loads_text_async(''.join(chunks))

    async def serialize_batch(self, data_list: List[Any]) -> List[Union[str, bytes]]:
        """Serialize multiple objects in batch asynchronously."""
        import asyncio
        tasks = [self.dumps_async(data) for data in data_list]
        return await asyncio.gather(*tasks)

    async def deserialize_batch(self, data_list: List[Union[str, bytes]]) -> List[Any]:
        """Deserialize multiple objects in batch asynchronously."""
        import asyncio
        tasks = [self.loads_async(data) for data in data_list]
        return await asyncio.gather(*tasks)

    async def save_batch_files(self, data_dict: Dict[Union[str, Path], Any]) -> None:
        """Save multiple files in batch asynchronously."""
        import asyncio
        tasks = [self.save_file_async(data, path) for path, data in data_dict.items()]
        await asyncio.gather(*tasks)

    async def load_batch_files(self, file_paths: List[Union[str, Path]]) -> Dict[Union[str, Path], Any]:
        """Load multiple files in batch asynchronously."""
        import asyncio
        tasks = [self.load_file_async(path) for path in file_paths]
        results = await asyncio.gather(*tasks)
        return dict(zip(file_paths, results))

    async def validate_data_async(self, data: Any) -> bool:
        """Validate data asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.validate_data, data)

    async def estimate_size_async(self, data: Any) -> int:
        """Estimate size asynchronously."""
        import asyncio
        return await asyncio.to_thread(self.estimate_size, data)
