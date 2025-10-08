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
        self._discovery = get_lazy_discovery()
        self._package_import_mapping = {}
        self._import_package_mapping = {}
        self._refresh_mappings()
    
    def _refresh_mappings(self) -> None:
        """Refresh dependency mappings from project files."""
        # Get the dynamic mappings from lazy discovery
        self._package_import_mapping = self._discovery.get_package_import_mapping()
        self._import_package_mapping = self._discovery.get_import_package_mapping()
    
    def get_package_name(self, import_name: str) -> str:
        """
        Get package name from import name using dynamic discovery.
        
        Args:
            import_name: Name used in import statement
            
        Returns:
            Package name for installation
        """
        # Refresh mappings to ensure we have the latest
        self._refresh_mappings()
        return self._import_package_mapping.get(import_name, import_name)
    
    def get_import_names(self, package_name: str) -> list:
        """
        Get all possible import names for a package.
        
        Args:
            package_name: Package name (e.g., 'opencv-python')
            
        Returns:
            List of import names (e.g., ['opencv-python', 'cv2'])
        """
        self._refresh_mappings()
        return self._package_import_mapping.get(package_name, [package_name])
    
    def get_package_import_mapping(self) -> Dict[str, list]:
        """
        Get the complete package to import names mapping.
        
        Returns:
            Dict mapping package_name -> [import_names]
        """
        self._refresh_mappings()
        return self._package_import_mapping.copy()
    
    def get_import_package_mapping(self) -> Dict[str, str]:
        """
        Get the complete import to package name mapping.
        
        Returns:
            Dict mapping import_name -> package_name
        """
        self._refresh_mappings()
        return self._import_package_mapping.copy()


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
                    check=True
                )
                
                self._installed_packages.add(package_name)
                logger.info(f"Successfully installed: {package_name}")
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package_name}: {e.stderr}")
                self._failed_packages.add(package_name)
                return False
            except Exception as e:
                logger.error(f"Unexpected error installing {package_name}: {e}")
                self._failed_packages.add(package_name)
                return False
    
    def install_and_import(self, module_name: str, package_name: str = None) -> Tuple[Optional[ModuleType], bool]:
        """
        Install package and import module.
        
        Args:
            module_name: Name of the module to import
            package_name: Optional package name if different from module name
            
        Returns:
            Tuple of (module_object, success_flag)
        """
        if not self.is_enabled():
            return None, False
        
        # Get package name from dependency mapper if not provided
        if package_name is None:
            package_name = self._dependency_mapper.get_package_name(module_name)
        
        # Try to import first
        try:
            module = importlib.import_module(module_name)
            return module, True
        except ImportError:
            pass
        
        # Install package if import failed
        if self.install_package(package_name):
            try:
                module = importlib.import_module(module_name)
                return module, True
            except ImportError as e:
                logger.error(f"Still cannot import {module_name} after installing {package_name}: {e}")
                return None, False
        
        return None, False
    
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


def enable_lazy_install() -> None:
    """Enable lazy installation globally."""
    _lazy_installer.enable()


def disable_lazy_install() -> None:
    """Disable lazy installation globally."""
    _lazy_installer.disable()


def is_lazy_install_enabled() -> bool:
    """Check if lazy installation is enabled globally."""
    return _lazy_installer.is_enabled()


def install_missing_package(package_name: str) -> bool:
    """Install a missing package."""
    return _lazy_installer.install_package(package_name)


def install_and_import(module_name: str, package_name: str = None) -> Tuple[Optional[ModuleType], bool]:
    """Install package and import module."""
    return _lazy_installer.install_and_import(module_name, package_name)


def get_lazy_install_stats() -> Dict[str, Any]:
    """Get lazy installation statistics."""
    return _lazy_installer.get_stats()


def lazy_import_with_install(module_name: str, package_name: str = None) -> Tuple[Optional[ModuleType], bool]:
    """
    Lazy import with automatic installation.
    
    This function attempts to import a module, and if it fails due to ImportError,
    it automatically installs the corresponding package using pip before retrying.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional package name if different from module name
        
    Returns:
        Tuple of (module_object, success_flag)
    """
    return _lazy_installer.install_and_import(module_name, package_name)


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
