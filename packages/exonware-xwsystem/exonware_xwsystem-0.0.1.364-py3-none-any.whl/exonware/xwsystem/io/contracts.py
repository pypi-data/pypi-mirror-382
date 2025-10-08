"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

IO module contracts - interfaces and enums for input/output operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, BinaryIO, TextIO
from pathlib import Path

# Import enums from types module
from .types import (
    FileMode,
    FileType,
    PathType,
    OperationResult,
    LockType
)


# ============================================================================
# FILE INTERFACES
# ============================================================================

class IFile(ABC):
    """
    Interface for file operations with both static and instance methods.
    
    Provides comprehensive file operations including:
    - File I/O operations (read, write, save, load)
    - File metadata operations (size, permissions, timestamps)
    - File validation and safety checks
    - Static utility methods for file operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    def open(self, mode: FileMode = FileMode.READ) -> None:
        """Open file with specified mode."""
        pass
    
    @abstractmethod
    def read(self, size: Optional[int] = None) -> Union[str, bytes]:
        """Read from file."""
        pass
    
    @abstractmethod
    def write(self, data: Union[str, bytes]) -> int:
        """Write to file."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close file."""
        pass
    
    @abstractmethod
    def save(self, data: Any, **kwargs) -> bool:
        """Save data to file."""
        pass
    
    @abstractmethod
    def load(self, **kwargs) -> Any:
        """Load data from file."""
        pass
    
    @abstractmethod
    def save_as(self, path: Union[str, Path], data: Any, **kwargs) -> bool:
        """Save data to specific path."""
        pass
    
    @abstractmethod
    def to_file(self, path: Union[str, Path], **kwargs) -> bool:
        """Write current object to file."""
        pass
    
    @abstractmethod
    def from_file(self, path: Union[str, Path], **kwargs) -> 'IFile':
        """Load object from file."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def exists(path: Union[str, Path]) -> bool:
        """Check if file exists."""
        pass
    
    @staticmethod
    @abstractmethod
    def size(path: Union[str, Path]) -> int:
        """Get file size."""
        pass
    
    @staticmethod
    @abstractmethod
    def delete(path: Union[str, Path]) -> bool:
        """Delete file."""
        pass
    
    @staticmethod
    @abstractmethod
    def copy(source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy file."""
        pass
    
    @staticmethod
    @abstractmethod
    def move(source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Move file."""
        pass
    
    @staticmethod
    @abstractmethod
    def rename(old_path: Union[str, Path], new_path: Union[str, Path]) -> bool:
        """Rename file."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_modified_time(path: Union[str, Path]) -> float:
        """Get file modification time."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_created_time(path: Union[str, Path]) -> float:
        """Get file creation time."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_permissions(path: Union[str, Path]) -> int:
        """Get file permissions."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_readable(path: Union[str, Path]) -> bool:
        """Check if file is readable."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_writable(path: Union[str, Path]) -> bool:
        """Check if file is writable."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_executable(path: Union[str, Path]) -> bool:
        """Check if file is executable."""
        pass
    
    @staticmethod
    @abstractmethod
    def read_text(path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read file as text."""
        pass
    
    @staticmethod
    @abstractmethod
    def read_bytes(path: Union[str, Path]) -> bytes:
        """Read file as bytes."""
        pass
    
    @staticmethod
    @abstractmethod
    def write_text(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """Write text to file."""
        pass
    
    @staticmethod
    @abstractmethod
    def write_bytes(path: Union[str, Path], content: bytes) -> bool:
        """Write bytes to file."""
        pass
    
    @staticmethod
    @abstractmethod
    def safe_read_text(path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
        """Safely read text file, returning None on error."""
        pass
    
    @staticmethod
    @abstractmethod
    def safe_read_bytes(path: Union[str, Path]) -> Optional[bytes]:
        """Safely read binary file, returning None on error."""
        pass
    
    @staticmethod
    @abstractmethod
    def safe_write_text(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """Safely write text to file."""
        pass
    
    @staticmethod
    @abstractmethod
    def safe_write_bytes(path: Union[str, Path], content: bytes) -> bool:
        """Safely write bytes to file."""
        pass


# ============================================================================
# FOLDER INTERFACES
# ============================================================================

class IFolder(ABC):
    """
    Interface for folder/directory operations with both static and instance methods.
    
    Provides comprehensive directory operations including:
    - Directory I/O operations (create, delete, list, walk)
    - Directory metadata operations (size, permissions, contents)
    - Directory validation and safety checks
    - Static utility methods for directory operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    def create(self, parents: bool = True, exist_ok: bool = True) -> bool:
        """Create directory."""
        pass
    
    @abstractmethod
    def delete(self, recursive: bool = False) -> bool:
        """Delete directory."""
        pass
    
    @abstractmethod
    def list_files(self, pattern: Optional[str] = None, recursive: bool = False) -> List[Path]:
        """List files in directory."""
        pass
    
    @abstractmethod
    def list_directories(self, recursive: bool = False) -> List[Path]:
        """List subdirectories."""
        pass
    
    @abstractmethod
    def walk(self) -> List[tuple[Path, List[str], List[str]]]:
        """Walk directory tree."""
        pass
    
    @abstractmethod
    def get_size(self) -> int:
        """Get directory size."""
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Check if directory is empty."""
        pass
    
    @abstractmethod
    def copy_to(self, destination: Union[str, Path]) -> bool:
        """Copy directory to destination."""
        pass
    
    @abstractmethod
    def move_to(self, destination: Union[str, Path]) -> bool:
        """Move directory to destination."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def exists(path: Union[str, Path]) -> bool:
        """Check if directory exists."""
        pass
    
    @staticmethod
    @abstractmethod
    def create_dir(path: Union[str, Path], parents: bool = True, exist_ok: bool = True) -> bool:
        """Create directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def delete_dir(path: Union[str, Path], recursive: bool = False) -> bool:
        """Delete directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def list_files_static(path: Union[str, Path], pattern: Optional[str] = None, recursive: bool = False) -> List[Path]:
        """List files in directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def list_directories_static(path: Union[str, Path], recursive: bool = False) -> List[Path]:
        """List subdirectories."""
        pass
    
    @staticmethod
    @abstractmethod
    def walk_static(path: Union[str, Path]) -> List[tuple[Path, List[str], List[str]]]:
        """Walk directory tree."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_size_static(path: Union[str, Path]) -> int:
        """Get directory size."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_empty_static(path: Union[str, Path]) -> bool:
        """Check if directory is empty."""
        pass
    
    @staticmethod
    @abstractmethod
    def copy_dir(source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def move_dir(source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Move directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_permissions(path: Union[str, Path]) -> int:
        """Get directory permissions."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_readable(path: Union[str, Path]) -> bool:
        """Check if directory is readable."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_writable(path: Union[str, Path]) -> bool:
        """Check if directory is writable."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_executable(path: Union[str, Path]) -> bool:
        """Check if directory is executable."""
        pass


# ============================================================================
# PATH INTERFACES
# ============================================================================

class IPath(ABC):
    """
    Interface for path operations with both static and instance methods.
    
    Provides comprehensive path operations including:
    - Path manipulation (resolve, normalize, join, split)
    - Path validation and safety checks
    - Static utility methods for path operations
    """
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def normalize(path: Union[str, Path]) -> Path:
        """Normalize path."""
        pass
    
    @staticmethod
    @abstractmethod
    def resolve(path: Union[str, Path]) -> Path:
        """Resolve path."""
        pass
    
    @staticmethod
    @abstractmethod
    def absolute(path: Union[str, Path]) -> Path:
        """Get absolute path."""
        pass
    
    @staticmethod
    @abstractmethod
    def relative(path: Union[str, Path], start: Optional[Union[str, Path]] = None) -> Path:
        """Get relative path."""
        pass
    
    @staticmethod
    @abstractmethod
    def join(*paths: Union[str, Path]) -> Path:
        """Join paths."""
        pass
    
    @staticmethod
    @abstractmethod
    def split(path: Union[str, Path]) -> tuple[Path, str]:
        """Split path into directory and filename."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_extension(path: Union[str, Path]) -> str:
        """Get file extension."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_stem(path: Union[str, Path]) -> str:
        """Get file stem (name without extension)."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_name(path: Union[str, Path]) -> str:
        """Get file/directory name."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_parent(path: Union[str, Path]) -> Path:
        """Get parent directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_absolute(path: Union[str, Path]) -> bool:
        """Check if path is absolute."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_relative(path: Union[str, Path]) -> bool:
        """Check if path is relative."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_parts(path: Union[str, Path]) -> tuple:
        """Get path parts."""
        pass
    
    @staticmethod
    @abstractmethod
    def match(path: Union[str, Path], pattern: str) -> bool:
        """Check if path matches pattern."""
        pass
    
    @staticmethod
    @abstractmethod
    def with_suffix(path: Union[str, Path], suffix: str) -> Path:
        """Get path with new suffix."""
        pass
    
    @staticmethod
    @abstractmethod
    def with_name(path: Union[str, Path], name: str) -> Path:
        """Get path with new name."""
        pass


# ============================================================================
# STREAM INTERFACES
# ============================================================================

class IStream(ABC):
    """
    Interface for stream operations with both static and instance methods.
    
    Provides comprehensive stream operations including:
    - Stream I/O operations (read, write, seek, tell)
    - Stream validation and safety checks
    - Static utility methods for stream operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    def read(self, size: Optional[int] = None) -> Union[str, bytes]:
        """Read from stream."""
        pass
    
    @abstractmethod
    def write(self, data: Union[str, bytes]) -> int:
        """Write to stream."""
        pass
    
    @abstractmethod
    def seek(self, position: int, whence: int = 0) -> int:
        """Seek stream position."""
        pass
    
    @abstractmethod
    def tell(self) -> int:
        """Get current stream position."""
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """Flush stream buffer."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close stream."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def open_file(path: Union[str, Path], mode: str = 'r', encoding: Optional[str] = None) -> Union[TextIO, BinaryIO]:
        """Open file as stream."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_closed(stream: Union[TextIO, BinaryIO]) -> bool:
        """Check if stream is closed."""
        pass
    
    @staticmethod
    @abstractmethod
    def readable(stream: Union[TextIO, BinaryIO]) -> bool:
        """Check if stream is readable."""
        pass
    
    @staticmethod
    @abstractmethod
    def writable(stream: Union[TextIO, BinaryIO]) -> bool:
        """Check if stream is writable."""
        pass
    
    @staticmethod
    @abstractmethod
    def seekable(stream: Union[TextIO, BinaryIO]) -> bool:
        """Check if stream is seekable."""
        pass


# ============================================================================
# ASYNC I/O INTERFACES
# ============================================================================

class IAsyncIO(ABC):
    """
    Interface for async I/O operations with both static and instance methods.
    
    Provides comprehensive async I/O operations including:
    - Async file operations (aread, awrite, aseek, atell)
    - Async stream operations
    - Static utility methods for async operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    async def aread(self, size: Optional[int] = None) -> Union[str, bytes]:
        """Async read operation."""
        pass
    
    @abstractmethod
    async def awrite(self, data: Union[str, bytes]) -> int:
        """Async write operation."""
        pass
    
    @abstractmethod
    async def aseek(self, position: int, whence: int = 0) -> int:
        """Async seek operation."""
        pass
    
    @abstractmethod
    async def atell(self) -> int:
        """Async tell operation."""
        pass
    
    @abstractmethod
    async def aflush(self) -> None:
        """Async flush operation."""
        pass
    
    @abstractmethod
    async def aclose(self) -> None:
        """Async close operation."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    async def aopen_file(path: Union[str, Path], mode: str = 'r', encoding: Optional[str] = None) -> Any:
        """Async open file."""
        pass
    
    @staticmethod
    @abstractmethod
    async def aread_text(path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Async read text file."""
        pass
    
    @staticmethod
    @abstractmethod
    async def aread_bytes(path: Union[str, Path]) -> bytes:
        """Async read binary file."""
        pass
    
    @staticmethod
    @abstractmethod
    async def awrite_text(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """Async write text to file."""
        pass
    
    @staticmethod
    @abstractmethod
    async def awrite_bytes(path: Union[str, Path], content: bytes) -> bool:
        """Async write bytes to file."""
        pass


# ============================================================================
# ATOMIC OPERATIONS INTERFACES
# ============================================================================

class IAtomicOperations(ABC):
    """
    Interface for atomic operations with both static and instance methods.
    
    Provides comprehensive atomic operations including:
    - Atomic file operations (atomic write, copy, move, delete)
    - Backup and restore operations
    - Static utility methods for atomic operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    def atomic_write(self, file_path: Union[str, Path], data: Union[str, bytes], 
                    backup: bool = True) -> OperationResult:
        """Atomically write data to file."""
        pass
    
    @abstractmethod
    def atomic_copy(self, source: Union[str, Path], destination: Union[str, Path]) -> OperationResult:
        """Atomically copy file."""
        pass
    
    @abstractmethod
    def atomic_move(self, source: Union[str, Path], destination: Union[str, Path]) -> OperationResult:
        """Atomically move file."""
        pass
    
    @abstractmethod
    def atomic_delete(self, file_path: Union[str, Path], backup: bool = True) -> OperationResult:
        """Atomically delete file."""
        pass
    
    @abstractmethod
    def atomic_rename(self, old_path: Union[str, Path], new_path: Union[str, Path]) -> OperationResult:
        """Atomically rename file."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def atomic_write_static(file_path: Union[str, Path], data: Union[str, bytes], 
                           backup: bool = True) -> OperationResult:
        """Atomically write data to file."""
        pass
    
    @staticmethod
    @abstractmethod
    def atomic_copy_static(source: Union[str, Path], destination: Union[str, Path]) -> OperationResult:
        """Atomically copy file."""
        pass
    
    @staticmethod
    @abstractmethod
    def atomic_move_static(source: Union[str, Path], destination: Union[str, Path]) -> OperationResult:
        """Atomically move file."""
        pass
    
    @staticmethod
    @abstractmethod
    def atomic_delete_static(file_path: Union[str, Path], backup: bool = True) -> OperationResult:
        """Atomically delete file."""
        pass
    
    @staticmethod
    @abstractmethod
    def atomic_rename_static(old_path: Union[str, Path], new_path: Union[str, Path]) -> OperationResult:
        """Atomically rename file."""
        pass


# ============================================================================
# BACKUP OPERATIONS INTERFACES
# ============================================================================

class IBackupOperations(ABC):
    """
    Interface for backup operations with both static and instance methods.
    
    Provides comprehensive backup operations including:
    - Backup creation and restoration
    - Backup management and cleanup
    - Static utility methods for backup operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    def create_backup(self, source: Union[str, Path], backup_dir: Union[str, Path]) -> Optional[Path]:
        """Create backup of file or directory."""
        pass
    
    @abstractmethod
    def restore_backup(self, backup_path: Union[str, Path], target: Union[str, Path]) -> OperationResult:
        """Restore from backup."""
        pass
    
    @abstractmethod
    def list_backups(self, backup_dir: Union[str, Path]) -> List[Path]:
        """List available backups."""
        pass
    
    @abstractmethod
    def cleanup_backups(self, backup_dir: Union[str, Path], max_age_days: int = 30) -> int:
        """Cleanup old backups."""
        pass
    
    @abstractmethod
    def verify_backup(self, backup_path: Union[str, Path]) -> bool:
        """Verify backup integrity."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def create_backup_static(source: Union[str, Path], backup_dir: Union[str, Path]) -> Optional[Path]:
        """Create backup of file or directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def restore_backup_static(backup_path: Union[str, Path], target: Union[str, Path]) -> OperationResult:
        """Restore from backup."""
        pass
    
    @staticmethod
    @abstractmethod
    def list_backups_static(backup_dir: Union[str, Path]) -> List[Path]:
        """List available backups."""
        pass
    
    @staticmethod
    @abstractmethod
    def cleanup_backups_static(backup_dir: Union[str, Path], max_age_days: int = 30) -> int:
        """Cleanup old backups."""
        pass
    
    @staticmethod
    @abstractmethod
    def verify_backup_static(backup_path: Union[str, Path]) -> bool:
        """Verify backup integrity."""
        pass


# ============================================================================
# TEMPORARY OPERATIONS INTERFACES
# ============================================================================

class ITemporaryOperations(ABC):
    """
    Interface for temporary operations with both static and instance methods.
    
    Provides comprehensive temporary operations including:
    - Temporary file and directory creation
    - Temporary resource cleanup
    - Static utility methods for temporary operations
    """
    
    # ============================================================================
    # INSTANCE METHODS
    # ============================================================================
    
    @abstractmethod
    def create_temp_file(self, suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """Create temporary file."""
        pass
    
    @abstractmethod
    def create_temp_directory(self, suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """Create temporary directory."""
        pass
    
    @abstractmethod
    def cleanup_temp(self, path: Union[str, Path]) -> bool:
        """Cleanup temporary file or directory."""
        pass
    
    @abstractmethod
    def cleanup_all_temp(self) -> int:
        """Cleanup all temporary files and directories."""
        pass
    
    # ============================================================================
    # STATIC METHODS
    # ============================================================================
    
    @staticmethod
    @abstractmethod
    def create_temp_file_static(suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """Create temporary file."""
        pass
    
    @staticmethod
    @abstractmethod
    def create_temp_directory_static(suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """Create temporary directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def cleanup_temp_static(path: Union[str, Path]) -> bool:
        """Cleanup temporary file or directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def get_temp_base_dir() -> Path:
        """Get temporary base directory."""
        pass
    
    @staticmethod
    @abstractmethod
    def is_temp(path: Union[str, Path]) -> bool:
        """Check if path is temporary."""
        pass


# ============================================================================
# UNIFIED I/O INTERFACE
# ============================================================================

class IUnifiedIO(IFile, IFolder, IPath, IStream, IAsyncIO, IAtomicOperations, IBackupOperations, ITemporaryOperations):
    """
    Unified I/O interface combining all existing I/O capabilities.
    
    This is the unified interface for all input/output operations across XWSystem.
    It combines all existing I/O interfaces into a single, comprehensive interface
    that provides complete I/O functionality for any data source.
    
    Features:
    - File operations (read, write, save, load)
    - Directory operations (create, delete, list, walk)
    - Path operations (resolve, normalize, join, split)
    - Stream operations (open, read, write, seek)
    - Async operations (async read/write, async streams)
    - Atomic operations (atomic write, copy, move, delete)
    - Backup operations (create, restore, list, cleanup)
    - Temporary operations (create temp files/dirs, cleanup)
    
    This interface follows the xwsystem pattern of combining existing interfaces
    rather than creating new abstractions, maximizing code reuse and maintaining
    backward compatibility.
    """
    pass


# ============================================================================
# FILE MANAGER INTERFACE
# ============================================================================

class IFileManager(IFile, IFolder, IPath, IAtomicOperations, IBackupOperations, ITemporaryOperations):
    """
    File Manager interface for comprehensive file operations.
    
    This interface combines file, directory, path, atomic, backup, and temporary
    operations to provide a complete file management solution. It's designed
    to handle any file type (docx, json, photo, movie, etc.) with intelligent
    format detection and appropriate handling.
    
    Features:
    - Universal file type support (any format)
    - Intelligent format detection
    - Atomic file operations
    - Backup and restore capabilities
    - Temporary file management
    - Path validation and normalization
    - Directory operations
    - File metadata and permissions
    
    This interface is specifically designed for file management tasks where
    you need to handle various file types without knowing the specific format
    in advance.
    """
    pass