"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_discovery.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
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
    """Discovers dependencies from various project configuration sources."""
    
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
        """Initialize lazy discovery."""
        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.discovered_dependencies: Dict[str, DependencyInfo] = {}
        self._discovery_sources: List[str] = []
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).parent
        while current != current.parent:
            if (current / 'pyproject.toml').exists() or (current / 'setup.py').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def discover_all_dependencies(self) -> Dict[str, str]:
        """Discover all dependencies from all available sources."""
        self.discovered_dependencies.clear()
        self._discovery_sources.clear()
        
        # Try different discovery methods
        self._discover_from_pyproject_toml()
        self._discover_from_requirements_txt()
        self._discover_from_setup_py()
        self._discover_from_custom_config()
        
        # Add common mappings
        self._add_common_mappings()
        
        # Convert to simple dict format
        result = {}
        for import_name, dep_info in self.discovered_dependencies.items():
            result[import_name] = dep_info.package_name
        
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
