"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 18, 2025

Lazy import utilities - Defer heavy module imports until first access.
"""

import importlib
import sys
import threading
from typing import Any, Dict, Optional, Set
from types import ModuleType

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.utils.lazy_import")


class LazyImporter:
    """
    Lazy importer that defers heavy module imports until first access.
    """
    
    __slots__ = ('_enabled', '_lazy_modules', '_loaded_modules', '_lock', '_access_counts')
    
    def __init__(self):
        """Initialize lazy importer."""
        self._enabled = False
        self._lazy_modules: Dict[str, str] = {}  # module_name -> module_path
        self._loaded_modules: Dict[str, ModuleType] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def enable(self) -> None:
        """Enable lazy imports."""
        with self._lock:
            self._enabled = True
            logger.info("Lazy imports enabled")
    
    def disable(self) -> None:
        """Disable lazy imports."""
        with self._lock:
            self._enabled = False
            logger.info("Lazy imports disabled")
    
    def is_enabled(self) -> bool:
        """Check if lazy imports are enabled."""
        return self._enabled
    
    def register_lazy_module(self, module_name: str, module_path: str = None) -> None:
        """
        Register a module for lazy loading.
        
        Args:
            module_name: Name of the module to register
            module_path: Optional full module path (defaults to module_name)
        """
        with self._lock:
            if module_path is None:
                module_path = module_name
            
            self._lazy_modules[module_name] = module_path
            self._access_counts[module_name] = 0
            logger.debug(f"Registered lazy module: {module_name} -> {module_path}")
    
    def import_module(self, module_name: str, package_name: str = None) -> Any:
        """
        Import a module with lazy loading.
        
        Args:
            module_name: Name of the module to import
            package_name: Optional pip package name (for compatibility with lazy_install)
            
        Returns:
            Lazy-loaded module or actual module
        """
        with self._lock:
            if not self._enabled:
                # If lazy imports disabled, import normally
                return importlib.import_module(module_name)
            
            # Check if already loaded
            if module_name in self._loaded_modules:
                self._access_counts[module_name] += 1
                return self._loaded_modules[module_name]
            
            # Check if registered for lazy loading
            if module_name in self._lazy_modules:
                module_path = self._lazy_modules[module_name]
                
                try:
                    # Load the actual module
                    actual_module = importlib.import_module(module_path)
                    self._loaded_modules[module_name] = actual_module
                    self._access_counts[module_name] += 1
                    
                    logger.debug(f"Lazy loaded module: {module_name}")
                    return actual_module
                    
                except ImportError as e:
                    logger.error(f"Failed to lazy load {module_name}: {e}")
                    raise
            else:
                # Not registered for lazy loading, import normally
                return importlib.import_module(module_name)
    
    def preload_module(self, module_name: str) -> bool:
        """
        Preload a registered lazy module.
        
        Args:
            module_name: Name of the module to preload
            
        Returns:
            True if preloaded successfully, False otherwise
        """
        with self._lock:
            if module_name not in self._lazy_modules:
                logger.warning(f"Module {module_name} not registered for lazy loading")
                return False
            
            try:
                self.import_module(module_name)
                logger.info(f"Preloaded module: {module_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to preload {module_name}: {e}")
                return False
    
    def preload_frequently_used(self, threshold: int = 5) -> None:
        """
        Preload modules that are accessed frequently.
        
        Args:
            threshold: Minimum access count to trigger preloading
        """
        with self._lock:
            for module_name, count in self._access_counts.items():
                if count >= threshold and module_name not in self._loaded_modules:
                    self.preload_module(module_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lazy import statistics."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'registered_modules': list(self._lazy_modules.keys()),
                'loaded_modules': list(self._loaded_modules.keys()),
                'access_counts': self._access_counts.copy(),
                'total_registered': len(self._lazy_modules),
                'total_loaded': len(self._loaded_modules)
            }


# Global lazy importer instance
_lazy_importer = LazyImporter()

# Public API functions
def enable_lazy_imports() -> None:
    """Enable lazy imports."""
    _lazy_importer.enable()

def disable_lazy_imports() -> None:
    """Disable lazy imports."""
    _lazy_importer.disable()

def is_lazy_import_enabled() -> bool:
    """Check if lazy imports are enabled."""
    return _lazy_importer.is_enabled()

def lazy_import(module_name: str, package_name: str = None) -> Any:
    """
    Import a module with lazy loading.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional pip package name (for compatibility)
        
    Returns:
        Lazy-loaded module
    """
    return _lazy_importer.import_module(module_name, package_name)

def register_lazy_module(module_name: str, module_path: str = None) -> None:
    """
    Register a module for lazy loading.
    
    Args:
        module_name: Name of the module to register
        module_path: Optional full module path
    """
    _lazy_importer.register_lazy_module(module_name, module_path)

def preload_module(module_name: str) -> bool:
    """
    Preload a registered lazy module.
    
    Args:
        module_name: Name of the module to preload
        
    Returns:
        True if preloaded successfully, False otherwise
    """
    return _lazy_importer.preload_module(module_name)

def get_lazy_import_stats() -> Dict[str, Any]:
    """Get lazy import statistics."""
    return _lazy_importer.get_stats()
