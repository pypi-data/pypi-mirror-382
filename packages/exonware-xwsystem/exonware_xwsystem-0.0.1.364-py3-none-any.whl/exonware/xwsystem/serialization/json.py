#exonware\xwsystem\serialization\json.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Enhanced JSON serialization with security, validation and performance optimizations.
"""

import json
import sys
import hashlib
import base64
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TextIO, BinaryIO, Iterator, Iterable, Callable, Set
from io import StringIO, BytesIO

from .base import ASerialization
from .contracts import SerializationCapability, SerializationFormat, FormatDetectionError, ValidationError
from .errors import SerializationError, JsonError
from ..config.logging_setup import get_logger

logger = get_logger("xwsystem.serialization.json")

# Import JSON libraries - lazy installation system will handle missing dependencies
import orjson
import ijson
import jsonpointer
import jsonpatch
import jsonschema
import msgspec
import xxhash


class JsonSerializer(ASerialization):
    """
    Enhanced JSON serializer with security validation, custom encoders,
    and performance optimizations for production use.
    
    Supports all audit features:
    - Partial access via JSON Pointer
    - Streaming via ijson
    - Typed decoding
    - Patching via JSON Patch
    - Schema validation
    - Canonical serialization
    - Checksums and verification
    """
    
    __slots__ = ('indent', 'sort_keys', 'ensure_ascii', 'canonical', 'type_adapters', 'target_version')

    def __init__(
        self,
        validate_input: bool = True,
        max_depth: int = 100,
        max_size_mb: float = 10.0,
        indent: Optional[int] = None,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        use_atomic_writes: bool = True,
        validate_paths: bool = True,
        base_path: Optional[Union[str, Path]] = None,
        canonical: bool = False,
        use_orjson: bool = True,
    ) -> None:
        """
        Initialize JSON serializer with security and performance options.

        Args:
            validate_input: Whether to validate input data for security
            max_depth: Maximum nesting depth allowed
            max_size_mb: Maximum data size in MB
            indent: JSON indentation (None for compact)
            sort_keys: Whether to sort dictionary keys
            ensure_ascii: Whether to escape non-ASCII characters
            use_atomic_writes: Whether to use atomic file operations
            validate_paths: Whether to validate file paths for security
            base_path: Base path for path validation
            canonical: Whether to use canonical serialization
            use_orjson: Whether to use orjson for performance (if available)
        """
        super().__init__(
            validate_input=validate_input,
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            use_atomic_writes=use_atomic_writes,
            validate_paths=validate_paths,
            base_path=base_path
        )
        
        self.indent = indent
        self.sort_keys = sort_keys or canonical
        self.ensure_ascii = ensure_ascii
        self.canonical = canonical
        self.use_orjson = use_orjson  # Lazy install handles orjson availability
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
        return "JSON"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions for this format."""
        return [".json", ".jsonl", ".ndjson"]

    @property
    def mime_type(self) -> str:
        """Get the MIME type for this serialization format."""
        return "application/json"

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
        
        # Lazy install handles dependencies automatically
        caps.add(SerializationCapability.PARTIAL_ACCESS)
        caps.add(SerializationCapability.TYPED_DECODE)
        
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
                # Check if it's a file path or JSON string
                if len(src) > 260 or '\n' in src or src.startswith('{') or src.startswith('['):
                    # Likely JSON string
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
            
            # Try to parse as JSON
            json.loads(content)
            return SerializationFormat.JSON
        except Exception as e:
            raise FormatDetectionError(f"Failed to detect JSON format: {e}")

    # =============================================================================
    # CORE SERIALIZATION METHODS
    # =============================================================================

    def dumps_text(self, data: Any) -> str:
        """Serialize data to text string."""
        try:
            if self.validate_input and self._data_validator:
                self._data_validator.validate_data_structure(data)
            
            if self.use_orjson:
                return orjson.dumps(data, option=orjson.OPT_SORT_KEYS if self.sort_keys else 0).decode('utf-8')
            else:
                return json.dumps(
                    data,
                    indent=self.indent,
                    sort_keys=self.sort_keys,
                    ensure_ascii=self.ensure_ascii,
                    default=self._custom_encoder
                )
        except Exception as e:
            raise JsonError(f"JSON serialization failed: {e}", e)

    def dumps_binary(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        try:
            if self.validate_input and self._data_validator:
                self._data_validator.validate_data_structure(data)
            
            if self.use_orjson:
                return orjson.dumps(data, option=orjson.OPT_SORT_KEYS if self.sort_keys else 0)
            else:
                text = json.dumps(
                    data,
                    indent=self.indent,
                    sort_keys=self.sort_keys,
                    ensure_ascii=self.ensure_ascii,
                    default=self._custom_encoder
                )
                return text.encode('utf-8')
        except Exception as e:
            raise JsonError(f"JSON serialization failed: {e}", e)

    def loads_text(self, data: str) -> Any:
        """Deserialize from text string."""
        try:
            if self.use_orjson:
                return orjson.loads(data.encode('utf-8'))
            else:
                return json.loads(data, object_hook=self._custom_decoder)
        except Exception as e:
            raise JsonError(f"JSON deserialization failed: {e}", e)

    def loads_bytes(self, data: bytes) -> Any:
        """Deserialize from bytes."""
        try:
            if self.use_orjson:
                return orjson.loads(data)
            else:
                text = data.decode('utf-8')
                return json.loads(text, object_hook=self._custom_decoder)
        except Exception as e:
            raise JsonError(f"JSON deserialization failed: {e}", e)

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
        """Get value at specific path using JSON Pointer or dot notation."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse JSON
            obj = json.loads(data)
            
            # Convert dot notation to JSON Pointer format
            if not path.startswith('/'):
                json_pointer = '/' + path.replace('.', '/')
            else:
                json_pointer = path
            
            # Use JSON Pointer - lazy install handles jsonpointer availability
            return jsonpointer.resolve_pointer(obj, json_pointer)
        except Exception as e:
            raise SerializationError(f"Failed to get value at path '{path}': {e}")

    def set_at(self, data: Union[str, bytes], path: str, value: Any) -> Union[str, bytes]:
        """Set value at specific path using JSON Pointer or dot notation."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse JSON
            obj = json.loads(data)
            
            # Convert dot notation to JSON Pointer format
            if not path.startswith('/'):
                json_pointer = '/' + path.replace('.', '/')
            else:
                json_pointer = path
            
            # Use JSON Pointer - lazy install handles jsonpointer availability
            jsonpointer.set_pointer(obj, json_pointer, value)
            
            # Serialize back
            result = json.dumps(obj, sort_keys=self.sort_keys, ensure_ascii=self.ensure_ascii)
            return result.encode('utf-8') if isinstance(data, bytes) else result
        except Exception as e:
            raise SerializationError(f"Failed to set value at path '{path}': {e}")

    def iter_path(self, data: Union[str, bytes], path: str) -> Iterator[Any]:
        """Iterate over values matching path expression."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse JSON
            obj = json.loads(data)
            
            # Use ijson for streaming path access - lazy install handles ijson availability
            for item in ijson.items(StringIO(data), path):
                yield item
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
            
            # Parse JSON
            obj = json.loads(data)
            
            # Convert dot notation paths to JSON Pointer format for jsonpatch
            # Lazy install handles jsonpatch availability
            if isinstance(patch, list):
                converted_patch = []
                for op in patch:
                    converted_op = op.copy()
                    if 'path' in converted_op and not converted_op['path'].startswith('/'):
                        # Convert dot notation to JSON Pointer
                        converted_op['path'] = '/' + converted_op['path'].replace('.', '/')
                    converted_patch.append(converted_op)
                patch = converted_patch
            
            if rfc == "6902":
                # JSON Patch
                patched = jsonpatch.apply_patch(obj, patch)
            elif rfc == "7386":
                # JSON Merge Patch
                patched = jsonpatch.merge_patch(obj, patch)
            else:
                raise SerializationError(f"Unsupported RFC: {rfc}")
            
            # Serialize back
            result = json.dumps(patched, sort_keys=self.sort_keys, ensure_ascii=self.ensure_ascii)
            return result.encode('utf-8') if isinstance(data, bytes) else result
        except Exception as e:
            raise SerializationError(f"Failed to apply patch: {e}")

    # =============================================================================
    # SCHEMA VALIDATION
    # =============================================================================

    def validate_schema(self, data: Union[str, bytes], schema: Any, dialect: str = "jsonschema") -> bool:
        """Validate data against schema."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Parse JSON
            obj = json.loads(data)
            
            # Lazy install handles jsonschema availability
            if dialect == "jsonschema":
                jsonschema.validate(obj, schema)
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
            canonical = json.dumps(
                data,
                sort_keys=True,
                separators=(',', ':'),
                ensure_ascii=True,
                default=self._custom_encoder
            )
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
    # BATCH STREAMING (NDJSON)
    # =============================================================================

    def serialize_ndjson(self, rows: Iterable[Any]) -> Iterator[str]:
        """Serialize iterable to newline-delimited JSON."""
        try:
            for row in rows:
                yield self.dumps_text(row) + '\n'
        except Exception as e:
            raise SerializationError(f"NDJSON serialization failed: {e}")

    def deserialize_ndjson(self, lines: Iterable[str]) -> Iterator[Any]:
        """Deserialize newline-delimited JSON."""
        try:
            for line in lines:
                line = line.strip()
                if line:
                    yield self.loads_text(line)
        except Exception as e:
            raise SerializationError(f"NDJSON deserialization failed: {e}")

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
        
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def _custom_decoder(self, obj: Any) -> Any:
        """Custom decoder for non-standard types."""
        # Check type adapters
        for typ, (_, from_fn) in self.type_adapters.items():
            try:
                return from_fn(obj)
            except (TypeError, ValueError):
                continue
        
        return obj