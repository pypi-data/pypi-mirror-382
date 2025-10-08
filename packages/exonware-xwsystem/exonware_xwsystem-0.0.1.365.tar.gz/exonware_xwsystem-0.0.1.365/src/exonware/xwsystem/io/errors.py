#exonware/xwsystem/io/errors.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

IO module errors - exception classes for input/output functionality.
"""


class IOError(Exception):
    """Base exception for IO errors."""
    pass


class FileNotFoundError(IOError):
    """Raised when file is not found."""
    pass


class FilePermissionError(IOError):
    """Raised when file permission is denied."""
    pass


class FileLockError(IOError):
    """Raised when file lock operation fails."""
    pass


class FileReadError(IOError):
    """Raised when file read operation fails."""
    pass


class FileWriteError(IOError):
    """Raised when file write operation fails."""
    pass


class FileDeleteError(IOError):
    """Raised when file delete operation fails."""
    pass


class FileCopyError(IOError):
    """Raised when file copy operation fails."""
    pass


class FileMoveError(IOError):
    """Raised when file move operation fails."""
    pass


class DirectoryError(IOError):
    """Raised when directory operation fails."""
    pass


class DirectoryNotFoundError(DirectoryError):
    """Raised when directory is not found."""
    pass


class DirectoryCreateError(DirectoryError):
    """Raised when directory creation fails."""
    pass


class DirectoryDeleteError(DirectoryError):
    """Raised when directory deletion fails."""
    pass


class PathError(IOError):
    """Raised when path operation fails."""
    pass


class PathValidationError(PathError):
    """Raised when path validation fails."""
    pass


class PathResolutionError(PathError):
    """Raised when path resolution fails."""
    pass


class StreamError(IOError):
    """Raised when stream operation fails."""
    pass


class StreamOpenError(StreamError):
    """Raised when stream opening fails."""
    pass


class StreamCloseError(StreamError):
    """Raised when stream closing fails."""
    pass


class StreamReadError(StreamError):
    """Raised when stream read fails."""
    pass


class StreamWriteError(StreamError):
    """Raised when stream write fails."""
    pass


class AtomicOperationError(IOError):
    """Raised when atomic operation fails."""
    pass


class BackupError(IOError):
    """Raised when backup operation fails."""
    pass


class TemporaryFileError(IOError):
    """Raised when temporary file operation fails."""
    pass
