"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: October 07, 2025

Lazy Import Hook System

This module provides a custom import hook that intercepts ImportError exceptions
and automatically installs missing packages when lazy mode is enabled.

Performance Optimized:
- Zero overhead for successful imports (no hooks in import path)
- Only activates when ImportError occurs
- Cached results prevent repeated installations
- Thread-safe implementation

Design:
- Uses sys.excepthook to catch ImportError at top level
- Completely passive until import fails
- No performance impact on normal imports
"""

import sys
import threading
from typing import Any, Optional, Dict

from ..config.logging_setup import get_logger

logger = get_logger("xwsystem.utils.lazy_import_hook")

# Global state
_hook_installed = False
_hook_lock = threading.RLock()
_original_excepthook = None


class LazyImportHook:
    """
    Import hook that intercepts ImportError and auto-installs packages.
    
    Performance optimized:
    - Zero overhead for successful imports
    - Only triggers on ImportError
    - Cached package installations
    """
    
    __slots__ = ('_enabled', '_package_name')
    
    def __init__(self, package_name: str = 'default'):
        """Initialize import hook for specific package."""
        self._enabled = False
        self._package_name = package_name
    
    def enable(self) -> None:
        """Enable the import hook."""
        self._enabled = True
        logger.debug(f"Import hook enabled for {self._package_name}")
    
    def disable(self) -> None:
        """Disable the import hook."""
        self._enabled = False
        logger.debug(f"Import hook disabled for {self._package_name}")
    
    def is_enabled(self) -> bool:
        """Check if hook is enabled."""
        return self._enabled
    
    def handle_import_error(self, module_name: str) -> Optional[Any]:
        """
        Handle ImportError by attempting to install and re-import.
        
        Args:
            module_name: Name of the module that failed to import
            
        Returns:
            Imported module if successful, None otherwise
        """
        if not self._enabled:
            return None
        
        try:
            from .lazy_install import lazy_import_with_install
            module, success = lazy_import_with_install(
                module_name, 
                installer_package=self._package_name
            )
            return module if success else None
        except:
            return None


# =============================================================================
# PERFORMANT IMPORT HOOK - Only activates on ImportError
# =============================================================================

class LazyMetaPathFinder:
    """
    Custom meta path finder that intercepts failed imports.
    
    Performance optimized:
    - Returns None immediately for successful imports (zero overhead)
    - Only tries lazy install when import would fail anyway
    - Cached results prevent repeated installations
    """
    
    __slots__ = ('_package_name', '_enabled')
    
    def __init__(self, package_name: str = 'default'):
        """Initialize meta path finder."""
        self._package_name = package_name
        self._enabled = True
    
    def find_module(self, fullname: str, path: Optional[str] = None):
        """
        Find module - returns None to let standard import continue.
        
        This is called for EVERY import, so must be ultra-fast.
        We return None immediately to avoid overhead.
        """
        # Return None immediately - let standard import proceed
        # We only intervene in find_spec() when import fails
        return None
    
    def find_spec(self, fullname: str, path: Optional[str] = None, target=None):
        """
        Find module spec - only called if standard import fails.
        
        This is our interception point - called when import would fail anyway.
        Zero overhead for successful imports!
        """
        if not self._enabled:
            return None
        
        # Only handle top-level packages, not sub-modules
        # e.g., handle "fastavro" but not "fastavro.schema"
        # This prevents trying to install "capnp.lib.types" as a package
        if '.' in fullname:
            # This is a sub-module - don't try to install
            return None
        
        # Try lazy installation
        try:
            from .lazy_install import is_lazy_install_enabled, lazy_import_with_install
            
            # Check if lazy install is enabled for this package
            if not is_lazy_install_enabled(self._package_name):
                return None
            
            # Attempt lazy install and import
            module, success = lazy_import_with_install(
                fullname,
                installer_package=self._package_name
            )
            
            if success and module:
                # Successfully installed and imported
                # Return a spec that points to the now-available module
                import importlib.util
                return importlib.util.find_spec(fullname)
            
        except Exception as e:
            logger.debug(f"Lazy import hook failed for {fullname}: {e}")
        
        # Let import fail normally
        return None


# Registry of installed hooks per package
_installed_hooks: Dict[str, LazyMetaPathFinder] = {}


def install_import_hook(package_name: str = 'default') -> None:
    """
    Install performant import hook for automatic lazy installation.
    
    Performance characteristics:
    - Zero overhead for successful imports
    - Only activates when ImportError would occur anyway
    - Thread-safe installation
    """
    global _installed_hooks
    
    with _hook_lock:
        # Don't install duplicate hooks
        if package_name in _installed_hooks:
            logger.debug(f"Import hook already installed for {package_name}")
            return
        
        # Create and install the hook
        hook = LazyMetaPathFinder(package_name)
        sys.meta_path.append(hook)
        _installed_hooks[package_name] = hook
        
        logger.info(f"✅ Lazy import hook installed for {package_name}")


def uninstall_import_hook(package_name: str = 'default') -> None:
    """Uninstall import hook for a package."""
    global _installed_hooks
    
    with _hook_lock:
        if package_name in _installed_hooks:
            hook = _installed_hooks[package_name]
            try:
                sys.meta_path.remove(hook)
            except ValueError:
                pass  # Already removed
            del _installed_hooks[package_name]
            logger.info(f"Lazy import hook uninstalled for {package_name}")


def is_import_hook_installed(package_name: str = 'default') -> bool:
    """Check if import hook is installed for a package."""
    return package_name in _installed_hooks

