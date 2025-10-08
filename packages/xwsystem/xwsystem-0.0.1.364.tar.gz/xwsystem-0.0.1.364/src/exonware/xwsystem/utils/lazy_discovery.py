"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_discovery.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: 27-Jan-2025

Lazy Discovery System for xwsystem

This module provides package-agnostic discovery of dependencies from project
configuration files. It automatically discovers what packages are needed
from pyproject.toml, requirements.txt, and other config files.

The system is designed to be completely package-agnostic and reusable across
all exonware libraries (xwnode, xwdata, xwentity, etc.) by automatically
discovering dependencies from project configuration files rather than using
hardcoded package mappings.
"""

import os
import re
import json
import toml
import sys
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.utils.lazy_discovery")

@dataclass
class DependencyInfo:
    """Information about a discovered dependency."""
    import_name: str
    package_name: str
    version: Optional[str] = None
    source: str = "unknown"
    category: str = "general"

class LazyDiscovery:
    """
    Discovers dependencies from various project configuration sources.
    Optimized with caching and file modification time checks.
    """
    
    __slots__ = ('project_root', 'discovered_dependencies', '_discovery_sources', 
                 '_cached_dependencies', '_file_mtimes', '_cache_valid')
    
    # Common import name to package name mappings (package-agnostic)
    COMMON_MAPPINGS = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'Pillow': 'Pillow',
        'yaml': 'PyYAML',
        'sklearn': 'scikit-learn',
        'bs4': 'beautifulsoup4',
        'dateutil': 'python-dateutil',
        'requests_oauthlib': 'requests-oauthlib',
        'google': 'google-api-python-client',
        'jwt': 'PyJWT',
        'crypto': 'pycrypto',
        'Crypto': 'pycrypto',
        'MySQLdb': 'mysqlclient',
        'psycopg2': 'psycopg2-binary',
        'lxml': 'lxml',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pytest': 'pytest',
        'black': 'black',
        'isort': 'isort',
        'mypy': 'mypy',
        'psutil': 'psutil',
        'colorama': 'colorama',
        'pytz': 'pytz',
        'aiofiles': 'aiofiles',
        'watchdog': 'watchdog',
        'wand': 'Wand',
        'exifread': 'ExifRead',
        'piexif': 'piexif',
        'rawpy': 'rawpy',
        'imageio': 'imageio',
        'scipy': 'scipy',
        'scikit-image': 'scikit-image',
        'opencv-python': 'opencv-python',
        'opencv-contrib-python': 'opencv-contrib-python',
    }
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize lazy discovery with caching."""
        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.discovered_dependencies: Dict[str, DependencyInfo] = {}
        self._discovery_sources: List[str] = []
        # Performance optimization: cache results and file modification times
        self._cached_dependencies: Dict[str, str] = {}
        self._file_mtimes: Dict[str, float] = {}
        self._cache_valid = False
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).parent
        while current != current.parent:
            if (current / 'pyproject.toml').exists() or (current / 'setup.py').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _is_cache_valid(self) -> bool:
        """Check if cached dependencies are still valid."""
        if not self._cache_valid or not self._cached_dependencies:
            return False
        
        # Check if config files have been modified
        config_files = [
            self.project_root / 'pyproject.toml',
            self.project_root / 'requirements.txt',
            self.project_root / 'setup.py',
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    current_mtime = config_file.stat().st_mtime
                    cached_mtime = self._file_mtimes.get(str(config_file), 0)
                    if current_mtime > cached_mtime:
                        return False  # File was modified
                except:
                    return False  # Error checking - invalidate cache
        
        return True
    
    def discover_all_dependencies(self) -> Dict[str, str]:
        """
        Discover all dependencies from all available sources.
        Optimized with caching - only re-parses if files changed.
        """
        # Return cached result if still valid
        if self._is_cache_valid():
            return self._cached_dependencies.copy()
        
        # Cache invalid - rediscover
        self.discovered_dependencies.clear()
        self._discovery_sources.clear()
        
        # Try different discovery methods
        self._discover_from_pyproject_toml()
        self._discover_from_requirements_txt()
        self._discover_from_setup_py()
        self._discover_from_custom_config()
        
        # Add common mappings
        self._add_common_mappings()
        
        # Convert to simple dict format and cache
        result = {}
        for import_name, dep_info in self.discovered_dependencies.items():
            result[import_name] = dep_info.package_name
        
        # Update cache
        self._cached_dependencies = result.copy()
        self._cache_valid = True
        
        # Update file modification times
        config_files = [
            self.project_root / 'pyproject.toml',
            self.project_root / 'requirements.txt',
            self.project_root / 'setup.py',
        ]
        for config_file in config_files:
            if config_file.exists():
                try:
                    self._file_mtimes[str(config_file)] = config_file.stat().st_mtime
                except:
                    pass
        
        return result
    
    def _discover_from_pyproject_toml(self) -> None:
        """Discover dependencies from pyproject.toml."""
        pyproject_path = self.project_root / 'pyproject.toml'
        if not pyproject_path.exists():
            return
        
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            # Check dependencies
            dependencies = []
            if 'project' in data and 'dependencies' in data['project']:
                dependencies.extend(data['project']['dependencies'])
            
            # Check optional dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group_name, group_deps in data['project']['optional-dependencies'].items():
                    dependencies.extend(group_deps)
            
            # Check build-system dependencies
            if 'build-system' in data and 'requires' in data['build-system']:
                dependencies.extend(data['build-system']['requires'])
            
            for dep in dependencies:
                self._parse_dependency_string(dep, 'pyproject.toml')
            
            self._discovery_sources.append('pyproject.toml')
            
        except Exception as e:
            logger.warning(f"Could not parse pyproject.toml: {e}")
    
    def _discover_from_requirements_txt(self) -> None:
        """Discover dependencies from requirements.txt."""
        requirements_path = self.project_root / 'requirements.txt'
        if not requirements_path.exists():
            return
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self._parse_dependency_string(line, 'requirements.txt')
            
            self._discovery_sources.append('requirements.txt')
            
        except Exception as e:
            logger.warning(f"Could not parse requirements.txt: {e}")
    
    def _discover_from_setup_py(self) -> None:
        """Discover dependencies from setup.py."""
        setup_path = self.project_root / 'setup.py'
        if not setup_path.exists():
            return
        
        try:
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract install_requires
            install_requires_match = re.search(
                r'install_requires\s*=\s*\[(.*?)\]', 
                content, 
                re.DOTALL
            )
            if install_requires_match:
                deps_str = install_requires_match.group(1)
                # Simple parsing - could be improved
                deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
                for dep in deps:
                    self._parse_dependency_string(dep, 'setup.py')
            
            self._discovery_sources.append('setup.py')
            
        except Exception as e:
            logger.warning(f"Could not parse setup.py: {e}")
    
    def _discover_from_custom_config(self) -> None:
        """Discover dependencies from custom configuration files."""
        # Look for dependency-mappings.json or similar
        config_files = [
            'dependency-mappings.json',
            'lazy-dependencies.json',
            'dependencies.json'
        ]
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        for import_name, package_name in data.items():
                            self.discovered_dependencies[import_name] = DependencyInfo(
                                import_name=import_name,
                                package_name=package_name,
                                source=config_file,
                                category='custom'
                            )
                    
                    self._discovery_sources.append(config_file)
                    
                except Exception as e:
                    logger.warning(f"Could not parse {config_file}: {e}")
    
    def _parse_dependency_string(self, dep_str: str, source: str) -> None:
        """Parse a dependency string and extract dependency information."""
        # Remove version constraints and extras
        dep_str = re.sub(r'[>=<!=~]+.*', '', dep_str)
        dep_str = re.sub(r'\[.*\]', '', dep_str)
        dep_str = dep_str.strip()
        
        if not dep_str:
            return
        
        # Determine import name and package name
        import_name = dep_str
        package_name = dep_str
        
        # Check if it's a common mapping
        if dep_str in self.COMMON_MAPPINGS:
            package_name = self.COMMON_MAPPINGS[dep_str]
        elif dep_str in self.COMMON_MAPPINGS.values():
            # Find the import name for this package
            for imp_name, pkg_name in self.COMMON_MAPPINGS.items():
                if pkg_name == dep_str:
                    import_name = imp_name
                    break
        
        # Store the dependency info
        self.discovered_dependencies[import_name] = DependencyInfo(
            import_name=import_name,
            package_name=package_name,
            source=source,
            category='discovered'
        )
    
    def _add_common_mappings(self) -> None:
        """Add common mappings that might not be in dependency files."""
        for import_name, package_name in self.COMMON_MAPPINGS.items():
            if import_name not in self.discovered_dependencies:
                self.discovered_dependencies[import_name] = DependencyInfo(
                    import_name=import_name,
                    package_name=package_name,
                    source='common_mappings',
                    category='common'
                )
    
    def get_discovery_sources(self) -> List[str]:
        """Get list of sources used for discovery."""
        return self._discovery_sources.copy()
    
    def get_dependency_info(self, import_name: str) -> Optional[DependencyInfo]:
        """Get detailed information about a dependency."""
        return self.discovered_dependencies.get(import_name)
    
    def add_custom_mapping(self, import_name: str, package_name: str, category: str = 'custom') -> None:
        """Add a custom dependency mapping."""
        self.discovered_dependencies[import_name] = DependencyInfo(
            import_name=import_name,
            package_name=package_name,
            source='custom',
            category=category
        )
    
    def get_package_import_mapping(self) -> Dict[str, List[str]]:
        """
        Get mapping of package names to their possible import names.
        
        Returns:
            Dict mapping package_name -> [package_name, import_name1, import_name2, ...]
            
        Example:
            {
                "fastavro": ["fastavro", "fastavro"],
                "opencv-python": ["opencv-python", "cv2"],
                "Pillow": ["Pillow", "PIL"],
                "PyYAML": ["PyYAML", "yaml"]
            }
        """
        # First, discover all dependencies
        self.discover_all_dependencies()
        
        # Create reverse mapping: package_name -> [import_names]
        package_to_imports = {}
        
        for import_name, dep_info in self.discovered_dependencies.items():
            package_name = dep_info.package_name
            
            if package_name not in package_to_imports:
                package_to_imports[package_name] = [package_name]  # Always include package name itself
            
            # Add import name if different from package name
            if import_name != package_name:
                if import_name not in package_to_imports[package_name]:
                    package_to_imports[package_name].append(import_name)
        
        return package_to_imports
    
    def get_import_package_mapping(self) -> Dict[str, str]:
        """
        Get mapping of import names to package names (reverse of above).
        
        Returns:
            Dict mapping import_name -> package_name
            
        Example:
            {
                "fastavro": "fastavro",
                "cv2": "opencv-python", 
                "PIL": "Pillow",
                "yaml": "PyYAML"
            }
        """
        # First, discover all dependencies
        self.discover_all_dependencies()
        
        # Create simple mapping: import_name -> package_name
        return {import_name: dep_info.package_name for import_name, dep_info in self.discovered_dependencies.items()}
    
    def get_package_for_import(self, import_name: str) -> Optional[str]:
        """
        Get the package name for a given import name.
        
        Args:
            import_name: The import name (e.g., 'cv2', 'PIL')
            
        Returns:
            Package name (e.g., 'opencv-python', 'Pillow') or None if not found
        """
        mapping = self.get_import_package_mapping()
        return mapping.get(import_name)
    
    def get_imports_for_package(self, package_name: str) -> List[str]:
        """
        Get all possible import names for a given package.
        
        Args:
            package_name: The package name (e.g., 'opencv-python')
            
        Returns:
            List of import names (e.g., ['opencv-python', 'cv2'])
        """
        mapping = self.get_package_import_mapping()
        return mapping.get(package_name, [package_name])
    
    def export_to_json(self, file_path: str) -> None:
        """Export discovered dependencies to JSON file."""
        data = {
            'dependencies': {name: info.package_name for name, info in self.discovered_dependencies.items()},
            'sources': self.get_discovery_sources(),
            'total_count': len(self.discovered_dependencies)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# Global discovery instance
_discovery = None

def get_lazy_discovery(project_root: Optional[str] = None) -> LazyDiscovery:
    """Get the global lazy discovery instance."""
    global _discovery
    if _discovery is None:
        _discovery = LazyDiscovery(project_root)
    return _discovery

def discover_dependencies(project_root: Optional[str] = None) -> Dict[str, str]:
    """Discover all dependencies for the current project."""
    discovery = get_lazy_discovery(project_root)
    return discovery.discover_all_dependencies()

def export_dependency_mappings(file_path: str, project_root: Optional[str] = None) -> None:
    """Export discovered dependency mappings to a JSON file."""
    discovery = get_lazy_discovery(project_root)
    discovery.export_to_json(file_path)


# =============================================================================
# SIMPLE CONFIGURATION API - Auto-Detection of [lazy] Extra
# =============================================================================

# Performance optimization: Cache detection results per package
_lazy_detection_cache: Dict[str, bool] = {}
_lazy_detection_lock = threading.RLock()

# Performance optimization: Module-level constant for mode enum conversion
_MODE_ENUM_MAP = None  # Lazy initialized to avoid circular import

def _detect_lazy_installation(package_name: str) -> bool:
    """
    Detect if the package was installed with [lazy] extra.
    Optimized with per-package caching to avoid repeated detection.
    
    Args:
        package_name: Package name to check
        
    Returns:
        True if [lazy] extra was installed, False otherwise
    """
    import os
    
    # Check cache first (performance optimization)
    with _lazy_detection_lock:
        if package_name in _lazy_detection_cache:
            return _lazy_detection_cache[package_name]
    
    # Method 1: Check via pkg_resources (most reliable)
    try:
        import pkg_resources
        
        # Try both package name formats
        package_names_to_try = [
            f"exonware-{package_name}",
            package_name,
            f"exonware.{package_name}"
        ]
        
        for pkg_name in package_names_to_try:
            try:
                dist = pkg_resources.get_distribution(pkg_name)
                # Check if 'lazy' is in the installed extras
                if hasattr(dist, 'extras'):
                    if 'lazy' in dist.extras:
                        logger.info(f"✅ Detected [lazy] extra for {package_name}")
                        # Cache the result
                        with _lazy_detection_lock:
                            _lazy_detection_cache[package_name] = True
                        return True
                        
            except pkg_resources.DistributionNotFound:
                continue
                
    except ImportError:
        logger.debug("pkg_resources not available, trying alternative methods")
    
    # Method 2: Check via importlib.metadata (Python 3.8+)
    try:
        if sys.version_info >= (3, 8):
            from importlib import metadata
            
            package_names_to_try = [
                f"exonware-{package_name}",
                package_name,
            ]
            
            for pkg_name in package_names_to_try:
                try:
                    dist = metadata.distribution(pkg_name)
                    # Check if lazy dependencies are installed
                    if dist.requires:
                        for req in dist.requires:
                            if 'extra == "lazy"' in req or 'extra == \'lazy\'' in req:
                                # Check if these dependencies are actually installed
                                dep_name = req.split(';')[0].strip().split('[')[0].strip()
                                try:
                                    metadata.distribution(dep_name)
                                    logger.info(f"✅ Detected [lazy] dependencies for {package_name}")
                                    # Cache the result
                                    with _lazy_detection_lock:
                                        _lazy_detection_cache[package_name] = True
                                    return True
                                except:
                                    pass
                except Exception:
                    continue
    except Exception as e:
        logger.debug(f"importlib.metadata check failed: {e}")
    
    # Method 3: Check environment variable (fallback)
    env_var = f"{package_name.upper()}_LAZY_INSTALL"
    env_value = os.environ.get(env_var, '').lower()
    if env_value in ('true', '1', 'yes', 'on'):
        logger.info(f"✅ Detected lazy via environment variable {env_var}")
        # Cache the result
        with _lazy_detection_lock:
            _lazy_detection_cache[package_name] = True
        return True
    
    # Method 4: Check if lazy-specific dependencies are installed
    lazy_indicators = {
        'importlib-metadata': False,
        'pkg-resources': False,
    }
    
    for indicator in lazy_indicators:
        try:
            __import__(indicator.replace('-', '_'))
            lazy_indicators[indicator] = True
        except ImportError:
            pass
    
    # If some lazy indicators are present, assume lazy installation
    if any(lazy_indicators.values()):
        logger.info(f"✅ Detected lazy indicators for {package_name}")
        # Cache the result
        with _lazy_detection_lock:
            _lazy_detection_cache[package_name] = True
        return True
    
    # Default: lazy installation is NOT enabled
    result = False
    logger.info(f"❌ No [lazy] extra detected for {package_name}")
    
    # Cache the result for future calls (performance optimization)
    with _lazy_detection_lock:
        _lazy_detection_cache[package_name] = result
    
    return result


class LazyInstallConfig:
    """Global configuration for lazy installation per package."""
    _configs: Dict[str, bool] = {}
    _modes: Dict[str, str] = {}
    _initialized: Dict[str, bool] = {}
    
    @classmethod
    def set(cls, package_name: str, enabled: bool, mode: str = "auto") -> None:
        """
        Enable or disable lazy installation for a specific package.
        Optimized: initialization is deferred until actually needed.
        """
        package_key = package_name.lower()
        
        # Fast path: just set the config, don't initialize yet
        # Initialization happens lazily when first import fails
        cls._configs[package_key] = enabled
        cls._modes[package_key] = mode
        
        # Only initialize if explicitly enabled (skip for disabled packages)
        if enabled and not cls._initialized.get(package_key):
            # Lazy initialization - defer actual setup
            cls._initialize_package(package_key, enabled, mode)
    
    @classmethod
    def _get_mode_enum_map(cls):
        """Get mode enum mapping (lazy initialized to avoid circular import)."""
        global _MODE_ENUM_MAP
        if _MODE_ENUM_MAP is None:
            from .lazy_install import LazyInstallMode
            _MODE_ENUM_MAP = {
                "auto": LazyInstallMode.AUTO,
                "interactive": LazyInstallMode.INTERACTIVE,
                "warn": LazyInstallMode.WARN,
                "disabled": LazyInstallMode.DISABLED,
                "dry_run": LazyInstallMode.DRY_RUN,
            }
        return _MODE_ENUM_MAP
    
    @classmethod
    def _initialize_package(cls, package_key: str, enabled: bool, mode: str) -> None:
        """Initialize lazy installation for a specific package."""
        if enabled:
            try:
                from .lazy_install import (
                    enable_lazy_install, 
                    set_lazy_install_mode,
                )
                from .lazy_import_hook import install_import_hook
                
                # Enable for THIS specific package only
                enable_lazy_install(package_key)
                
                # Set the mode for THIS specific package (use cached enum map)
                mode_enum = cls._get_mode_enum_map().get(mode.lower(), cls._get_mode_enum_map()["auto"])
                
                set_lazy_install_mode(package_key, mode_enum)
                
                # Install import hook for automatic interception (performance optimized)
                install_import_hook(package_key)
                
                cls._initialized[package_key] = True
                logger.info(f"✅ Lazy installation initialized for {package_key} (mode: {mode})")
            except ImportError as e:
                logger.warning(f"⚠️ Could not enable lazy install for {package_key}: {e}")
        else:
            try:
                from .lazy_install import disable_lazy_install
                disable_lazy_install(package_key)
                cls._initialized[package_key] = True
                logger.info(f"❌ Lazy installation disabled for {package_key}")
            except ImportError:
                pass
    
    @classmethod
    def is_enabled(cls, package_name: str) -> bool:
        """Check if lazy installation is enabled for a package."""
        return cls._configs.get(package_name.lower(), False)
    
    @classmethod
    def get_mode(cls, package_name: str) -> str:
        """Get the lazy installation mode for a package."""
        return cls._modes.get(package_name.lower(), "auto")


def config_package_lazy_install_enabled(
    package_name: str, 
    enabled: bool = None,  # None = auto-detect from pip installation
    mode: str = "auto"
) -> None:
    """
    Simple one-line configuration for package lazy installation.
    
    Args:
        package_name: Package name (e.g., "xwsystem", "xwnode", "xwdata")
        enabled: True to enable, False to disable, None to auto-detect from pip installation
        mode: Installation mode - "auto", "interactive", "disabled", "dry_run"
              - "auto": Automatically install without asking (default)
              - "interactive": Ask user before installing each package
              - "disabled": Don't install anything
              - "dry_run": Show what would be installed but don't install
    
    Examples:
        # Auto-detect from installation (if user did 'pip install lib[lazy]')
        config_package_lazy_install_enabled("xwsystem")
        
        # Force enable regardless of installation
        config_package_lazy_install_enabled("xwnode", True, "interactive")
        
        # Force disable
        config_package_lazy_install_enabled("xwdata", False)
    """
    # Auto-detect if enabled is None
    if enabled is None:
        enabled = _detect_lazy_installation(package_name)
    
    LazyInstallConfig.set(package_name, enabled, mode)