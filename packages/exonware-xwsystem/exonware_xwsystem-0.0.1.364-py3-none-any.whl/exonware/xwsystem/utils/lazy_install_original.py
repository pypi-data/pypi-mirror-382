"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_install.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: 27-Jan-2025

Lazy Installation System for xwsystem

This module provides automatic installation of missing packages when import
failures occur. It integrates with the lazy discovery system to automatically
discover package names from project configuration files.

The system is designed to be package-agnostic and reusable across all
exonware libraries by using dynamic discovery rather than hardcoded mappings.
"""

import subprocess
import sys
import importlib
import threading
from typing import Any, Dict, Optional, Set, Tuple
from types import ModuleType

from ..config.logging_setup import get_logger
from .lazy_discovery import discover_dependencies, get_lazy_discovery

logger = get_logger("xsystem.utils.lazy_install")


class DependencyMapper:
    """Maps import names to package names using dynamic discovery."""
    
    def __init__(self):
        """Initialize dependency mapper."""
        self._dependencies = {}
        self._discovery = get_lazy_discovery()
        self._refresh_dependencies()
    
    def _refresh_dependencies(self) -> None:
        """Refresh dependency mappings from project files."""
        self._dependencies = discover_dependencies()
    
    def get_package_name(self, import_name: str) -> str:
        """
        Get package name from import name using dynamic discovery.
        
        Args:
            import_name: Name used in import statement
            
        Returns:
            Package name for installation
        """
        # Refresh dependencies to ensure we have the latest
        self._refresh_dependencies()
        return self._dependencies.get(import_name, import_name)


class LazyInstaller:
    """
    Lazy installer that automatically installs missing packages on import failure.
    """
    
    __slots__ = ('_enabled', '_installed_packages', '_failed_packages', '_lock', '_dependency_mapper')
    
    def __init__(self):
        """Initialize lazy installer."""
        self._enabled = True  # Default enabled, can be controlled via environment
        self._installed_packages: Set[str] = set()
        self._failed_packages: Set[str] = set()
        self._lock = threading.RLock()
        self._dependency_mapper = DependencyMapper()
    
    def enable(self) -> None:
        """Enable lazy installation."""
        with self._lock:
            self._enabled = True
            logger.info("Lazy installation enabled")
    
    def disable(self) -> None:
        """Disable lazy installation."""
        with self._lock:
            self._enabled = False
            logger.info("Lazy installation disabled")
    
    def is_enabled(self) -> bool:
        """Check if lazy installation is enabled."""
        return self._enabled
    
    def install_package(self, package_name: str) -> bool:
        """
        Install a package using pip.
        
        Args:
            package_name: Name of the package to install
            
        Returns:
            True if installation successful, False otherwise
        """
        with self._lock:
            if package_name in self._installed_packages:
                return True
            
            if package_name in self._failed_packages:
                return False
            
            try:
                logger.info(f"Installing package: {package_name}")
                
                # Run pip install
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package_name],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self._installed_packages.add(package_name)
                    logger.info(f"Successfully installed: {package_name}")
                    return True
                else:
                    logger.error(f"Failed to install {package_name}: {result.stderr}")
                    self._failed_packages.add(package_name)
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout installing {package_name}")
                self._failed_packages.add(package_name)
                return False
            except Exception as e:
                logger.error(f"Error installing {package_name}: {e}")
                self._failed_packages.add(package_name)
                return False
    
    def install_and_import(self, module_name: str, package_name: str = None) -> Any:
        """
        Install package if missing and import module.
        
        Args:
            module_name: Name of the module to import
            package_name: Optional pip package name if different from module name
            
        Returns:
            Imported module
            
        Raises:
            ImportError: If module cannot be imported even after installation
        """
        if not self._enabled:
            raise ImportError(f"Lazy installation is disabled. Cannot install {module_name}")
        
        # Try to import first
        try:
            return importlib.import_module(module_name)
        except ImportError:
            pass
        
        # Get package name
        if package_name is None:
            package_name = self._dependency_mapper.get_package_name(module_name)
        
        # Install package
        if not self.install_package(package_name):
            raise ImportError(f"Failed to install package {package_name} for module {module_name}")
        
        # Try to import again
        try:
            return importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Module {module_name} not available even after installing {package_name}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get installation statistics."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'installed_packages': list(self._installed_packages),
                'failed_packages': list(self._failed_packages),
                'total_installed': len(self._installed_packages),
                'total_failed': len(self._failed_packages)
            }


# Global lazy installer instance
_lazy_installer = LazyInstaller()

# Public API functions
def enable_lazy_install() -> None:
    """Enable lazy installation."""
    _lazy_installer.enable()

def disable_lazy_install() -> None:
    """Disable lazy installation."""
    _lazy_installer.disable()

def is_lazy_install_enabled() -> bool:
    """Check if lazy installation is enabled."""
    return _lazy_installer.is_enabled()

def install_missing_package(package_name: str) -> bool:
    """
    Install a missing package.
    
    Args:
        package_name: Name of the package to install
        
    Returns:
        True if installation successful, False otherwise
    """
    return _lazy_installer.install_package(package_name)

def install_and_import(module_name: str, package_name: str = None) -> Any:
    """
    Install package if missing and import module.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional pip package name if different from module name
        
    Returns:
        Imported module
    """
    return _lazy_installer.install_and_import(module_name, package_name)

def get_lazy_install_stats() -> Dict[str, Any]:
    """Get lazy installation statistics."""
    return _lazy_installer.get_stats()


def lazy_import_with_install(module_name: str, package_name: str = None) -> Tuple[Any, bool]:
    """
    Universal lazy import with automatic installation.
    
    This is the main function that should be used in xwsystem modules.
    It attempts to import a module, and if it fails due to ImportError,
    it automatically installs the corresponding package using pip before retrying.
    
    Args:
        module_name: Name of the module to import (e.g., 'msgpack', 'requests')
        package_name: Optional package name if different from module name
        
    Returns:
        Tuple of (module, available) where:
        - module: The imported module object or None if import failed
        - available: Boolean indicating if the module is available
        
    Example:
        msgpack, MSGPACK_AVAILABLE = lazy_import_with_install("msgpack")
        if MSGPACK_AVAILABLE:
            data = msgpack.packb({"key": "value"})
    """
    try:
        # Try to import the module first
        module = importlib.import_module(module_name)
        return module, True
    except ImportError:
        # Import failed, check if lazy install is enabled
        if not _lazy_installer.is_enabled():
            logger.debug(f"Lazy install disabled, skipping auto-install for {module_name}")
            return None, False
        
        # Get package name if not provided
        if package_name is None:
            package_name = _lazy_installer._dependency_mapper.get_package_name(module_name)
        
        logger.info(f"Module {module_name} not found, attempting to install {package_name}")
        
        # Try to install the package
        if _lazy_installer.install_package(package_name):
            try:
                # Retry import after installation
                module = importlib.import_module(module_name)
                logger.info(f"Successfully imported {module_name} after installation")
                return module, True
            except ImportError as e:
                logger.error(f"Failed to import {module_name} even after installing {package_name}: {e}")
                return None, False
        else:
            logger.error(f"Failed to install package {package_name} for module {module_name}")
            return None, False

def xwimport(module_name: str, package_name: str = None) -> Any:
    """
    Simple lazy import with automatic installation.
    
    This function either returns the imported module or raises an ImportError.
    No availability checking - it either works or fails.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional package name if different from module name
        
    Returns:
        The imported module object
        
    Raises:
        ImportError: If module cannot be imported even after installation attempt
    """
    module, available = lazy_import_with_install(module_name, package_name)
    if not available:
        raise ImportError(f"Module {module_name} is not available and could not be installed")
    return module
