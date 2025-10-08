"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_install.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: 27-Jan-2025

Lazy Installation System for xwsystem

This module provides automatic installation of missing packages when import
failures occur. It integrates with the lazy discovery system to automatically
discover package names from project configuration files.

The system is designed to be package-agnostic and reusable across all
exonware libraries by using dynamic discovery rather than hardcoded mappings.

Features:
- Per-package isolation (xwsystem vs xwnode won't interfere)
- Interactive mode with user prompts
- Auto-detection of [lazy] extra from pip installation
- Performance optimized with caching

Design Philosophy:
The lazy system is smart enough to work automatically with standard Python imports.
You DON'T need to use xwimport() in your code - just use normal try/except imports.
The xwimport() function is available for special cases but is NOT recommended for
general use. Keep your code clean and simple with standard imports.
"""

import subprocess
import sys
import importlib
import threading
import json
import os
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from types import ModuleType

from ..config.logging_setup import get_logger
from .lazy_discovery import discover_dependencies, get_lazy_discovery

logger = get_logger("xsystem.utils.lazy_install")


# =============================================================================
# ENVIRONMENT DETECTION UTILITIES
# =============================================================================

def _is_externally_managed() -> bool:
    """
    Check if Python environment is externally managed (PEP 668).
    
    Returns:
        True if environment has EXTERNALLY-MANAGED marker file
    """
    marker_file = Path(sys.prefix) / "EXTERNALLY-MANAGED"
    return marker_file.exists()


def _check_pip_audit_available() -> bool:
    """Check if pip-audit is available for vulnerability scanning."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'pip-audit' in result.stdout
    except Exception:
        return False


# =============================================================================
# LAZY INSTALLATION MODES
# =============================================================================

class LazyInstallMode(Enum):
    """Lazy installation modes."""
    AUTO = "auto"           # Automatically install without asking
    INTERACTIVE = "interactive"  # Ask user before installing
    WARN = "warn"           # Log warning but don't install (for monitoring)
    DISABLED = "disabled"   # Don't install anything
    DRY_RUN = "dry_run"    # Show what would be installed but don't install


class DependencyMapper:
    """
    Maps import names to package names using dynamic discovery.
    Optimized with caching to avoid repeated file I/O.
    """
    
    __slots__ = ('_discovery', '_package_import_mapping', '_import_package_mapping', '_cached', '_lock')
    
    def __init__(self):
        """Initialize dependency mapper."""
        self._discovery = get_lazy_discovery()
        self._package_import_mapping = {}
        self._import_package_mapping = {}
        self._cached = False
        self._lock = threading.RLock()
        # Don't auto-refresh on init - lazy load on first use
    
    def _ensure_mappings_cached(self) -> None:
        """Ensure mappings are cached (lazy initialization)."""
        if self._cached:
            return
        
        with self._lock:
            # Double-check pattern
            if self._cached:
                return
            
            # Get the dynamic mappings from lazy discovery (one-time operation)
            self._package_import_mapping = self._discovery.get_package_import_mapping()
            self._import_package_mapping = self._discovery.get_import_package_mapping()
            self._cached = True
    
    def get_package_name(self, import_name: str) -> str:
        """
        Get package name from import name using dynamic discovery.
        
        Args:
            import_name: Name used in import statement
            
        Returns:
            Package name for installation
        """
        # Lazy load mappings on first use (cached afterward)
        self._ensure_mappings_cached()
        return self._import_package_mapping.get(import_name, import_name)
    
    def get_import_names(self, package_name: str) -> list:
        """
        Get all possible import names for a package.
        
        Args:
            package_name: Package name (e.g., 'opencv-python')
            
        Returns:
            List of import names (e.g., ['opencv-python', 'cv2'])
        """
        self._ensure_mappings_cached()
        return self._package_import_mapping.get(package_name, [package_name])
    
    def get_package_import_mapping(self) -> Dict[str, list]:
        """
        Get the complete package to import names mapping.
        
        Returns:
            Dict mapping package_name -> [import_names]
        """
        self._ensure_mappings_cached()
        return self._package_import_mapping.copy()
    
    def get_import_package_mapping(self) -> Dict[str, str]:
        """
        Get the complete import to package name mapping.
        
        Returns:
            Dict mapping import_name -> package_name
        """
        self._ensure_mappings_cached()
        return self._import_package_mapping.copy()


# =============================================================================
# SECURITY & POLICY CONFIGURATION
# =============================================================================

class LazyInstallPolicy:
    """
    Security and policy configuration for lazy installation.
    Per-package allow/deny lists, index URLs, and security settings.
    """
    __slots__ = ()
    
    # Allow/Deny lists per package
    _allow_lists: Dict[str, Set[str]] = {}
    _deny_lists: Dict[str, Set[str]] = {}
    
    # Index URL configuration per package
    _index_urls: Dict[str, str] = {}
    _extra_index_urls: Dict[str, List[str]] = {}
    _trusted_hosts: Dict[str, List[str]] = {}
    
    # Security settings
    _require_hashes: Dict[str, bool] = {}
    _verify_ssl: Dict[str, bool] = {}
    
    # Lockfile paths per package
    _lockfile_paths: Dict[str, str] = {}
    
    _lock = threading.RLock()
    
    @classmethod
    def set_allow_list(cls, package_name: str, allowed_packages: List[str]) -> None:
        """Set allow list for a package (only these can be installed)."""
        with cls._lock:
            cls._allow_lists[package_name] = set(allowed_packages)
            logger.info(f"Set allow list for {package_name}: {len(allowed_packages)} packages")
    
    @classmethod
    def set_deny_list(cls, package_name: str, denied_packages: List[str]) -> None:
        """Set deny list for a package (these cannot be installed)."""
        with cls._lock:
            cls._deny_lists[package_name] = set(denied_packages)
            logger.info(f"Set deny list for {package_name}: {len(denied_packages)} packages")
    
    @classmethod
    def add_to_allow_list(cls, package_name: str, allowed_package: str) -> None:
        """Add single package to allow list."""
        with cls._lock:
            if package_name not in cls._allow_lists:
                cls._allow_lists[package_name] = set()
            cls._allow_lists[package_name].add(allowed_package)
    
    @classmethod
    def add_to_deny_list(cls, package_name: str, denied_package: str) -> None:
        """Add single package to deny list."""
        with cls._lock:
            if package_name not in cls._deny_lists:
                cls._deny_lists[package_name] = set()
            cls._deny_lists[package_name].add(denied_package)
    
    @classmethod
    def is_package_allowed(cls, installer_package: str, target_package: str) -> Tuple[bool, str]:
        """
        Check if target_package can be installed by installer_package.
        Returns: (allowed: bool, reason: str)
        """
        with cls._lock:
            # Check deny list first
            if installer_package in cls._deny_lists:
                if target_package in cls._deny_lists[installer_package]:
                    return False, f"Package '{target_package}' is in deny list"
            
            # Check allow list (if exists, package MUST be in it)
            if installer_package in cls._allow_lists:
                if target_package not in cls._allow_lists[installer_package]:
                    return False, f"Package '{target_package}' not in allow list"
            
            return True, "OK"
    
    @classmethod
    def set_index_url(cls, package_name: str, index_url: str) -> None:
        """Set PyPI index URL for a package."""
        with cls._lock:
            cls._index_urls[package_name] = index_url
            logger.info(f"Set index URL for {package_name}: {index_url}")
    
    @classmethod
    def set_extra_index_urls(cls, package_name: str, urls: List[str]) -> None:
        """Set extra index URLs for a package."""
        with cls._lock:
            cls._extra_index_urls[package_name] = urls
            logger.info(f"Set {len(urls)} extra index URLs for {package_name}")
    
    @classmethod
    def add_trusted_host(cls, package_name: str, host: str) -> None:
        """Add trusted host for a package."""
        with cls._lock:
            if package_name not in cls._trusted_hosts:
                cls._trusted_hosts[package_name] = []
            cls._trusted_hosts[package_name].append(host)
    
    @classmethod
    def get_pip_args(cls, package_name: str) -> List[str]:
        """Get pip install arguments for a package based on policy."""
        args = []
        
        with cls._lock:
            # Add index URL
            if package_name in cls._index_urls:
                args.extend(['--index-url', cls._index_urls[package_name]])
            
            # Add extra index URLs
            if package_name in cls._extra_index_urls:
                for url in cls._extra_index_urls[package_name]:
                    args.extend(['--extra-index-url', url])
            
            # Add trusted hosts
            if package_name in cls._trusted_hosts:
                for host in cls._trusted_hosts[package_name]:
                    args.extend(['--trusted-host', host])
            
            # Add hash requirement if enabled
            if cls._require_hashes.get(package_name, False):
                args.append('--require-hashes')
            
            # Add SSL verification setting
            if not cls._verify_ssl.get(package_name, True):
                args.append('--no-verify-ssl')
        
        return args
    
    @classmethod
    def set_lockfile_path(cls, package_name: str, path: str) -> None:
        """Set lockfile path for a package."""
        with cls._lock:
            cls._lockfile_paths[package_name] = path
    
    @classmethod
    def get_lockfile_path(cls, package_name: str) -> Optional[str]:
        """Get lockfile path for a package."""
        with cls._lock:
            return cls._lockfile_paths.get(package_name)


# =============================================================================
# PER-PACKAGE LAZY INSTALLER REGISTRY
# =============================================================================

class LazyInstallerRegistry:
    """Registry to manage separate lazy installer instances per package."""
    _instances: Dict[str, 'LazyInstaller'] = {}
    _lock = threading.RLock()
    
    @classmethod
    def get_instance(cls, package_name: str = 'default') -> 'LazyInstaller':
        """Get or create a lazy installer instance for a package."""
        with cls._lock:
            if package_name not in cls._instances:
                cls._instances[package_name] = LazyInstaller(package_name)
            return cls._instances[package_name]
    
    @classmethod
    def get_all_instances(cls) -> Dict[str, 'LazyInstaller']:
        """Get all lazy installer instances."""
        with cls._lock:
            return cls._instances.copy()


# =============================================================================
# LAZY INSTALLER - Per-Package Isolated
# =============================================================================

class LazyInstaller:
    """
    Lazy installer that automatically installs missing packages on import failure.
    Each instance is isolated per package to prevent interference.
    """
    
    __slots__ = (
        '_package_name', '_enabled', '_installed_packages', '_failed_packages', 
        '_lock', '_dependency_mapper', '_mode', '_auto_approve_all'
    )
    
    def __init__(self, package_name: str = 'default'):
        """Initialize lazy installer for a specific package."""
        self._package_name = package_name
        self._enabled = False  # Default to disabled until explicitly enabled
        self._installed_packages: Set[str] = set()
        self._failed_packages: Set[str] = set()
        self._lock = threading.RLock()
        self._dependency_mapper = DependencyMapper()
        self._mode = LazyInstallMode.AUTO
        self._auto_approve_all = False
    
    def get_package_name(self) -> str:
        """Get the package name this installer is for."""
        return self._package_name
    
    def set_mode(self, mode: LazyInstallMode) -> None:
        """
        Set the lazy installation mode.
        
        Args:
            mode: Installation mode (AUTO, INTERACTIVE, DISABLED, DRY_RUN)
        """
        with self._lock:
            self._mode = mode
            logger.info(f"Lazy installation mode for {self._package_name} set to: {mode.value}")
    
    def get_mode(self) -> LazyInstallMode:
        """Get the current installation mode."""
        return self._mode
    
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
    
    def _ask_user_permission(self, package_name: str, module_name: str) -> bool:
        """
        Ask user for permission to install a package.
        
        Args:
            package_name: Name of the package to install
            module_name: Name of the module being imported
            
        Returns:
            True if user approves, False otherwise
        """
        # If user already approved all, return True
        if self._auto_approve_all:
            return True
        
        print(f"\n{'='*60}")
        print(f"Lazy Installation Active - {self._package_name}")
        print(f"{'='*60}")
        print(f"Package: {package_name}")
        print(f"Module:  {module_name}")
        print(f"{'='*60}")
        print(f"\nThe module '{module_name}' is not installed.")
        print(f"Would you like to install '{package_name}'?")
        print(f"\nOptions:")
        print(f"  [Y] Yes - Install this package")
        print(f"  [N] No  - Skip this package")
        print(f"  [A] All - Install this and all future packages without asking")
        print(f"  [Q] Quit - Cancel and raise ImportError")
        print(f"{'='*60}")
        
        while True:
            try:
                choice = input("Your choice [Y/N/A/Q]: ").strip().upper()
                
                if choice in ('Y', 'YES', ''):
                    return True
                elif choice in ('N', 'NO'):
                    return False
                elif choice in ('A', 'ALL'):
                    self._auto_approve_all = True
                    return True
                elif choice in ('Q', 'QUIT'):
                    raise KeyboardInterrupt("User cancelled installation")
                else:
                    print(f"Invalid choice '{choice}'. Please enter Y, N, A, or Q.")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Installation cancelled by user")
                return False
    
    def install_package(self, package_name: str, module_name: str = None) -> bool:
        """
        Install a package using pip.
        
        Args:
            package_name: Name of the package to install
            module_name: Name of the module being imported (for interactive mode)
            
        Returns:
            True if installation successful, False otherwise
        """
        with self._lock:
            # Check if already installed or failed
            if package_name in self._installed_packages:
                return True
            
            if package_name in self._failed_packages:
                return False
            
            # Handle different modes
            if self._mode == LazyInstallMode.DISABLED:
                logger.info(f"Lazy installation disabled for {self._package_name}, skipping {package_name}")
                return False
            
            if self._mode == LazyInstallMode.WARN:
                logger.warning(f"[WARN] Package '{package_name}' is missing but WARN mode is active - not installing")
                print(f"[WARN] ({self._package_name}): Package '{package_name}' is missing (not installed in WARN mode)")
                return False
            
            if self._mode == LazyInstallMode.DRY_RUN:
                print(f"[DRY RUN] ({self._package_name}): Would install package '{package_name}'")
                return False
            
            if self._mode == LazyInstallMode.INTERACTIVE:
                # Ask user for permission
                if not self._ask_user_permission(package_name, module_name or package_name):
                    logger.info(f"User declined installation of {package_name}")
                    self._failed_packages.add(package_name)
                    return False
            
            # =================================================================
            # SECURITY CHECKS (PEP 668, Allow/Deny Lists)
            # =================================================================
            
            # Check PEP 668: Externally-managed environment
            if _is_externally_managed():
                logger.error(f"Cannot install {package_name}: Environment is externally managed (PEP 668)")
                print(f"\n[ERROR] This Python environment is externally managed (PEP 668)")
                print(f"Package '{package_name}' cannot be installed in this environment.")
                print(f"\nSuggested solutions:")
                print(f"  1. Create a virtual environment:")
                print(f"     python -m venv .venv")
                print(f"     .venv\\Scripts\\activate  # Windows")
                print(f"     source .venv/bin/activate  # Linux/macOS")
                print(f"  2. Use pipx for isolated installs:")
                print(f"     pipx install {package_name}")
                print(f"  3. Override with --break-system-packages (NOT RECOMMENDED)\n")
                self._failed_packages.add(package_name)
                return False
            
            # Check allow/deny lists
            allowed, reason = LazyInstallPolicy.is_package_allowed(self._package_name, package_name)
            if not allowed:
                logger.error(f"Cannot install {package_name}: {reason}")
                print(f"\n[SECURITY] Package '{package_name}' blocked: {reason}\n")
                self._failed_packages.add(package_name)
                return False
            
            # =================================================================
            # PROCEED WITH INSTALLATION (AUTO or user approved)
            # =================================================================
            
            try:
                logger.info(f"Installing package: {package_name}")
                print(f"\n[INSTALL] Installing {package_name}...")
                
                # Build pip install command with policy arguments
                pip_args = [sys.executable, '-m', 'pip', 'install']
                
                # Add policy-based arguments (index URLs, trusted hosts, etc.)
                policy_args = LazyInstallPolicy.get_pip_args(self._package_name)
                if policy_args:
                    pip_args.extend(policy_args)
                    logger.debug(f"Using policy args: {policy_args}")
                
                # Add package name
                pip_args.append(package_name)
                
                # Run pip install
                result = subprocess.run(
                    pip_args,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self._installed_packages.add(package_name)
                print(f"[OK] Successfully installed: {package_name}\n")
                logger.info(f"Successfully installed: {package_name}")
                
                # Run vulnerability audit if pip-audit is available
                if _check_pip_audit_available():
                    self._run_vulnerability_audit(package_name)
                
                # Update lockfile if configured
                self._update_lockfile(package_name)
                
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package_name}: {e.stderr}")
                print(f"[FAIL] Failed to install {package_name}\n")
                self._failed_packages.add(package_name)
                return False
            except Exception as e:
                logger.error(f"Unexpected error installing {package_name}: {e}")
                print(f"[ERROR] Unexpected error: {e}\n")
                self._failed_packages.add(package_name)
                return False
    
    def _run_vulnerability_audit(self, package_name: str) -> None:
        """
        Run vulnerability audit on installed package using pip-audit.
        Only runs if pip-audit is installed.
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip_audit', '-r', '-', '--format', 'json'],
                input=package_name,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Vulnerability audit passed for {package_name}")
            else:
                # Parse JSON output for vulnerabilities
                try:
                    audit_data = json.loads(result.stdout)
                    if audit_data.get('vulnerabilities'):
                        logger.warning(f"[SECURITY] Vulnerabilities found in {package_name}: {audit_data}")
                        print(f"[SECURITY WARNING] Package '{package_name}' has known vulnerabilities")
                        print(f"Run 'pip-audit' for details")
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse audit results for {package_name}")
        except subprocess.TimeoutExpired:
            logger.warning(f"Vulnerability audit timed out for {package_name}")
        except Exception as e:
            logger.debug(f"Vulnerability audit skipped for {package_name}: {e}")
    
    def _update_lockfile(self, package_name: str) -> None:
        """Update lockfile with newly installed package."""
        lockfile_path = LazyInstallPolicy.get_lockfile_path(self._package_name)
        if not lockfile_path:
            return  # No lockfile configured
        
        try:
            # Get installed version
            version = self._get_installed_version(package_name)
            if not version:
                return
            
            # Load existing lockfile or create new
            lockfile_path = Path(lockfile_path)
            if lockfile_path.exists():
                with open(lockfile_path, 'r', encoding='utf-8') as f:
                    lockdata = json.load(f)
            else:
                lockdata = {
                    "metadata": {
                        "generated_by": f"xwsystem-lazy-{self._package_name}",
                        "version": "1.0"
                    },
                    "packages": {}
                }
            
            # Add/update package entry
            lockdata["packages"][package_name] = {
                "version": version,
                "installed_at": datetime.now().isoformat(),
                "installer": self._package_name
            }
            
            # Write lockfile
            lockfile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(lockfile_path, 'w', encoding='utf-8') as f:
                json.dump(lockdata, f, indent=2)
            
            logger.info(f"Updated lockfile: {lockfile_path}")
        except Exception as e:
            logger.warning(f"Failed to update lockfile: {e}")
    
    def _get_installed_version(self, package_name: str) -> Optional[str]:
        """Get installed version of a package."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
        except Exception as e:
            logger.debug(f"Could not get version for {package_name}: {e}")
        return None
    
    def generate_sbom(self) -> Dict:
        """
        Generate Software Bill of Materials (SBOM) for installed packages.
        
        Returns:
            Dict containing SBOM data in SPDX-like format
        """
        sbom = {
            "metadata": {
                "format": "xwsystem-sbom",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "installer_package": self._package_name
            },
            "packages": []
        }
        
        for pkg in self._installed_packages:
            version = self._get_installed_version(pkg)
            sbom["packages"].append({
                "name": pkg,
                "version": version or "unknown",
                "installed_by": self._package_name,
                "source": "pypi"  # Could be enhanced to detect actual source
            })
        
        return sbom
    
    def export_sbom(self, output_path: str) -> bool:
        """
        Export SBOM to file.
        
        Args:
            output_path: Path to write SBOM file
            
        Returns:
            True if successful
        """
        try:
            sbom = self.generate_sbom()
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sbom, f, indent=2)
            
            logger.info(f"Exported SBOM to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export SBOM: {e}")
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
        
        # Install package if import failed (pass module_name for interactive prompt)
        if self.install_package(package_name, module_name):
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


# =============================================================================
# PUBLIC API - Per-Package Functions
# =============================================================================

def enable_lazy_install(package_name: str = 'default') -> None:
    """Enable lazy installation for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    installer.enable()


def disable_lazy_install(package_name: str = 'default') -> None:
    """Disable lazy installation for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    installer.disable()


def is_lazy_install_enabled(package_name: str = 'default') -> bool:
    """Check if lazy installation is enabled for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    return installer.is_enabled()


def set_lazy_install_mode(package_name: str, mode: LazyInstallMode) -> None:
    """Set the lazy installation mode for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    installer.set_mode(mode)


def get_lazy_install_mode(package_name: str = 'default') -> LazyInstallMode:
    """Get the lazy installation mode for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    return installer.get_mode()


def install_missing_package(package_name: str, installer_package: str = 'default') -> bool:
    """
    Install a missing package.
    
    Args:
        package_name: Name of the package to install
        installer_package: Which package's lazy installer to use
        
    Returns:
        True if installation successful, False otherwise
    """
    installer = LazyInstallerRegistry.get_instance(installer_package)
    return installer.install_package(package_name)


def install_and_import(
    module_name: str, 
    package_name: str = None,
    installer_package: str = 'default'
) -> Tuple[Optional[ModuleType], bool]:
    """
    Install package and import module.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional package name if different from module name
        installer_package: Which package's lazy installer to use
        
    Returns:
        Tuple of (module_object, success_flag)
    """
    installer = LazyInstallerRegistry.get_instance(installer_package)
    return installer.install_and_import(module_name, package_name)


def get_lazy_install_stats(package_name: str = 'default') -> Dict[str, Any]:
    """Get lazy installation statistics for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    return installer.get_stats()


def get_all_lazy_install_stats() -> Dict[str, Dict[str, Any]]:
    """Get lazy installation statistics for all packages."""
    all_instances = LazyInstallerRegistry.get_all_instances()
    return {name: inst.get_stats() for name, inst in all_instances.items()}


def lazy_import_with_install(
    module_name: str, 
    package_name: str = None,
    installer_package: str = 'default'
) -> Tuple[Optional[ModuleType], bool]:
    """
    Lazy import with automatic installation.
    
    This function attempts to import a module, and if it fails due to ImportError,
    it automatically installs the corresponding package using pip before retrying.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional package name if different from module name
        installer_package: Which package's lazy installer to use (e.g., 'xwsystem', 'xwnode')
        
    Returns:
        Tuple of (module_object, success_flag)
    """
    installer = LazyInstallerRegistry.get_instance(installer_package)
    return installer.install_and_import(module_name, package_name)


def xwimport(
    module_name: str, 
    package_name: str = None,
    installer_package: str = 'default'
) -> Any:
    """
    Simple lazy import with automatic installation.
    
    This function either returns the imported module or raises an ImportError.
    No availability checking - it either works or fails.
    
    Args:
        module_name: Name of the module to import
        package_name: Optional package name if different from module name
        installer_package: Which package's lazy installer to use
        
    Returns:
        The imported module object
        
    Raises:
        ImportError: If module cannot be imported even after installation attempt
    """
    module, available = lazy_import_with_install(module_name, package_name, installer_package)
    if not available:
        raise ImportError(f"Module {module_name} is not available and could not be installed")
    return module


# =============================================================================
# PUBLIC API - Security & Policy Configuration
# =============================================================================

def set_package_allow_list(package_name: str, allowed_packages: List[str]) -> None:
    """
    Set allow list for a package (only these packages can be installed).
    
    Args:
        package_name: Installer package name (e.g., 'xwsystem')
        allowed_packages: List of package names that are allowed
    """
    LazyInstallPolicy.set_allow_list(package_name, allowed_packages)


def set_package_deny_list(package_name: str, denied_packages: List[str]) -> None:
    """
    Set deny list for a package (these packages cannot be installed).
    
    Args:
        package_name: Installer package name (e.g., 'xwsystem')
        denied_packages: List of package names that are blocked
    """
    LazyInstallPolicy.set_deny_list(package_name, denied_packages)


def add_to_package_allow_list(package_name: str, allowed_package: str) -> None:
    """Add single package to allow list."""
    LazyInstallPolicy.add_to_allow_list(package_name, allowed_package)


def add_to_package_deny_list(package_name: str, denied_package: str) -> None:
    """Add single package to deny list."""
    LazyInstallPolicy.add_to_deny_list(package_name, denied_package)


def set_package_index_url(package_name: str, index_url: str) -> None:
    """
    Set PyPI index URL for a package.
    
    Args:
        package_name: Installer package name (e.g., 'xwsystem')
        index_url: PyPI index URL (e.g., 'https://pypi.org/simple')
    """
    LazyInstallPolicy.set_index_url(package_name, index_url)


def set_package_extra_index_urls(package_name: str, urls: List[str]) -> None:
    """Set extra index URLs for a package."""
    LazyInstallPolicy.set_extra_index_urls(package_name, urls)


def add_package_trusted_host(package_name: str, host: str) -> None:
    """Add trusted host for a package."""
    LazyInstallPolicy.add_trusted_host(package_name, host)


def set_package_lockfile(package_name: str, lockfile_path: str) -> None:
    """
    Set lockfile path for a package to track installed dependencies.
    
    Args:
        package_name: Installer package name
        lockfile_path: Path to lockfile (JSON format)
    """
    LazyInstallPolicy.set_lockfile_path(package_name, lockfile_path)


def generate_package_sbom(package_name: str = 'default', output_path: str = None) -> Dict:
    """
    Generate Software Bill of Materials (SBOM) for installed packages.
    
    Args:
        package_name: Installer package name
        output_path: Optional path to export SBOM file
        
    Returns:
        Dict containing SBOM data
    """
    installer = LazyInstallerRegistry.get_instance(package_name)
    sbom = installer.generate_sbom()
    
    if output_path:
        installer.export_sbom(output_path)
    
    return sbom


def check_externally_managed_environment() -> bool:
    """
    Check if current Python environment is externally managed (PEP 668).
    
    Returns:
        True if environment is externally managed
    """
    return _is_externally_managed()
