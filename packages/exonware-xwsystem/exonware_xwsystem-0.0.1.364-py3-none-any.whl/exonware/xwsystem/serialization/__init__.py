"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

XSystem Serialization Package

Provides comprehensive serialization utilities for 30 formats following the production library principle.

🚨 CRITICAL PRINCIPLE: NO HARDCODED SERIALIZATION LOGIC
   All serializers use established, well-tested libraries only!

📊 FORMAT BREAKDOWN:

TEXT FORMATS (8):
1. JSON        - Built-in json library
2. YAML        - PyYAML library 
3. TOML        - Built-in tomllib + tomli-w
4. XML         - dicttoxml + xmltodict libraries
5. CSV         - Built-in csv library
6. ConfigParser- Built-in configparser module
7. FormData    - Built-in urllib.parse
8. Multipart   - Built-in email.mime modules

BINARY FORMATS (9):
9.  BSON       - pymongo.bson library
10. MessagePack- msgpack library
11. CBOR       - cbor2 library
12. Pickle     - Built-in pickle module
13. Marshal    - Built-in marshal module
14. SQLite3    - Built-in sqlite3 module
15. DBM        - Built-in dbm module
16. Shelve     - Built-in shelve module
17. Plistlib   - Built-in plistlib module

SCHEMA-BASED FORMATS (7):
18. Apache Avro      - fastavro library
19. Protocol Buffers - google.protobuf library
20. Apache Thrift    - thrift library
21. Apache Parquet   - pyarrow library
22. Apache ORC       - pyorc library
23. Cap'n Proto      - pycapnp library
24. FlatBuffers      - flatbuffers library

KEY-VALUE STORES (3):
25. LevelDB/RocksDB  - plyvel/python-rocksdb libraries
26. LMDB            - lmdb library
27. Zarr            - zarr library

SCIENTIFIC & ANALYTICS (3):
28. HDF5            - h5py library
29. Feather/Arrow   - pyarrow library
30. GraphDB         - neo4j/pydgraph libraries

✅ BENEFITS:
- ONE import gets 30 serialization formats
- Production-grade reliability (no custom parsers)
- Consistent API across all formats (sync AND async)
- Security validation & atomic file operations
- Schema-based formats for enterprise applications
- Unified async support with automatic fallbacks
- Streaming and batch operations built-in
- Minimizes dependencies in consuming projects

🔄 ASYNC SUPPORT:
Every serializer automatically supports async operations:
- serializer.dumps_async() - async serialization
- serializer.loads_async() - async deserialization  
- serializer.save_file_async() - async file I/O with aiofiles
- serializer.load_file_async() - async file loading
- serializer.serialize_batch() - concurrent batch operations
- serializer.stream_serialize() - async streaming support
"""

from .contracts import ISerialization
from .base import ASerialization, SerializationError

# Core 12 formats (established external + built-in libraries)
from .json import JsonSerializer, JsonError
from .yaml import YamlSerializer, YamlError
from .toml import TomlSerializer, TomlError
from .xml import XmlSerializer, XmlError
from .bson import BsonSerializer, BsonError
from .msgpack import MsgPackSerializer
from .cbor import CborSerializer, CborError
from .csv import CsvSerializer, CsvError
from .pickle import PickleSerializer, PickleError
from .marshal import MarshalSerializer, MarshalError
from .formdata import FormDataSerializer, FormDataError
from .multipart import MultipartSerializer, MultipartError

# Built-in Python modules (5 additional formats)
from .configparser import ConfigParserSerializer, ConfigParserError
from .sqlite3 import Sqlite3Serializer, Sqlite3Error
from .dbm import DbmSerializer, DbmError
from .shelve import ShelveSerializer, ShelveError
from .plistlib import PlistlibSerializer, PlistlibError

# Schema-based formats (6 core + 1 optional = 7 enterprise formats)
from .avro import AvroSerializer, AvroError
from .protobuf import ProtobufSerializer, ProtobufError
from .thrift import ThriftSerializer, ThriftError
from .parquet import ParquetSerializer, ParquetError
from .orc import OrcSerializer, OrcError
from .capnproto import CapnProtoSerializer, CapnProtoError
from .flatbuffers import FlatBuffersSerializer, FlatBuffersError

# Key-value stores (3 additional formats) - lazy installation handles missing deps
from .leveldb import LevelDbSerializer, LevelDbError
from .lmdb import LmdbSerializer, LmdbError
from .zarr import ZarrSerializer, ZarrError

# Scientific & analytics (3 additional formats)
from .hdf5 import Hdf5Serializer, Hdf5Error
from .feather import FeatherSerializer, FeatherError
from .graphdb import GraphDbSerializer, GraphDbError

# Auto-detection and format intelligence
from .format_detector import FormatDetector, detect_format, get_format_suggestions, is_binary_format
from .auto_serializer import (
    AutoSerializer, auto_serialize, auto_deserialize, 
    auto_save_file, auto_load_file
)

# XWSerialization - Self-transforming intelligent serializer
from .xw_serializer import (
    XWSerializer, create_xw_serializer,
    dumps, loads, save_file, load_file
)

# Flyweight pattern for memory optimization
from .flyweight import (
    get_serializer, get_flyweight_stats, clear_serializer_cache, 
    get_cache_info, create_serializer, SerializerPool
)

__all__ = [
    # Interface and base class
    "ISerialization",
    "ASerialization", 
    "SerializationError",
    # Core 12 formats
    "JsonSerializer", "JsonError", 
    "YamlSerializer", "YamlError",
    "TomlSerializer", "TomlError",
    "XmlSerializer", "XmlError",
    "BsonSerializer", "BsonError",
    "MsgPackSerializer",
    "CborSerializer", "CborError",
    "CsvSerializer", "CsvError",
    "PickleSerializer", "PickleError",
    "MarshalSerializer", "MarshalError",
    "FormDataSerializer", "FormDataError",
    "MultipartSerializer", "MultipartError",
    # Built-in Python modules (5 additional formats)
    "ConfigParserSerializer", "ConfigParserError",
    "Sqlite3Serializer", "Sqlite3Error",
    "DbmSerializer", "DbmError",
    "ShelveSerializer", "ShelveError",
    "PlistlibSerializer", "PlistlibError",
    # Schema-based formats (7 enterprise formats)
    "AvroSerializer", "AvroError",
    "ProtobufSerializer", "ProtobufError",
    "ThriftSerializer", "ThriftError",
    "ParquetSerializer", "ParquetError",
    "OrcSerializer", "OrcError",
    "CapnProtoSerializer", "CapnProtoError",
    "FlatBuffersSerializer", "FlatBuffersError",
    
    # Key-value stores (3 additional formats)
    "LevelDbSerializer", "LevelDbError",
    "LmdbSerializer", "LmdbError", 
    "ZarrSerializer", "ZarrError",
    
    # Scientific & analytics (3 additional formats)
    "Hdf5Serializer", "Hdf5Error",
    "FeatherSerializer", "FeatherError",
    "GraphDbSerializer", "GraphDbError",
    
    # Auto-detection and intelligence
    "FormatDetector", "detect_format", "get_format_suggestions", "is_binary_format",
    "AutoSerializer", "auto_serialize", "auto_deserialize", 
    "auto_save_file", "auto_load_file",
    
    # XWSerialization - Self-transforming intelligent serializer
    "XWSerializer", "create_xw_serializer",
    "dumps", "loads", "save_file", "load_file",
    
    # Flyweight optimization
    "get_serializer", "get_flyweight_stats", "clear_serializer_cache", 
    "get_cache_info", "create_serializer", "SerializerPool",
]
