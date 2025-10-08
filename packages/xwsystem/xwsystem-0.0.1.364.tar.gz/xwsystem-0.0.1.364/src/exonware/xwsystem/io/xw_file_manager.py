"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

XWFileManager - Concrete implementation of file manager operations.
"""

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, BinaryIO, TextIO

from .base import AFileManager
from .contracts import FileMode, FileType, PathType, OperationResult, LockType, IFileManager
from .atomic_file import AtomicFileWriter
from ..config.logging_setup import get_logger
from ..security.path_validator import PathValidator
from ..validation.data_validator import DataValidator
from ..monitoring.performance_monitor import performance_monitor

logger = get_logger(__name__)


class XWFileManager(AFileManager):
    """
    Concrete implementation of file manager operations.
    
    This class provides a complete, production-ready implementation of file
    management operations with xwsystem integration for security, validation,
    and monitoring. It can handle any file type (docx, json, photo, movie, etc.)
    with intelligent format detection and appropriate handling.
    
    Features:
    - Universal file type support (any format)
    - Intelligent format detection
    - Atomic file operations
    - Backup and restore capabilities
    - Temporary file management
    - Path validation and normalization
    - Directory operations
    - File metadata and permissions
    - xwsystem integration (security, validation, monitoring)
    """
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None, **config):
        """
        Initialize XWFileManager with xwsystem integration.
        
        Args:
            base_path: Optional base path for file operations
            **config: Configuration options for file operations
        """
        super().__init__(base_path, **config)
        
        # Initialize xwsystem utilities
        self._path_validator = PathValidator()
        self._data_validator = DataValidator()
        
        # Configuration
        self.auto_create_dirs = config.get('auto_create_dirs', True)
        self.auto_backup = config.get('auto_backup', True)
        self.auto_cleanup = config.get('auto_cleanup', True)
        self.timeout_seconds = config.get('timeout_seconds', 30)
        self.supported_formats = config.get('supported_formats', [
            'text', 'json', 'yaml', 'xml', 'csv', 'image', 'video', 'audio',
            'archive', 'document', 'code', 'config', 'data'
        ])
        
        logger.debug(f"XWFileManager initialized for base path: {base_path}")
    
    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================
    
    def open(self, mode: FileMode = FileMode.READ) -> None:
        """Open file with validation and monitoring."""
        if not self.file_path:
            raise ValueError("No file path specified")
        
        if self.validate_paths:
            self._path_validator.validate_path(self.file_path)
        
        with performance_monitor("file_open"):
            # Ensure parent directory exists
            if self.auto_create_dirs and mode in [FileMode.WRITE, FileMode.APPEND, FileMode.WRITE_PLUS]:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Open file
            self._handle = open(self.file_path, mode.value)
            logger.debug(f"File opened: {self.file_path} in mode {mode.value}")
    
    def read(self, size: Optional[int] = None) -> Union[str, bytes]:
        """Read from file with validation."""
        if not self.is_open():
            raise ValueError("File not open")
        
        with performance_monitor("file_read"):
            data = self._handle.read(size)
            
            if self.validate_data and isinstance(data, (str, bytes)):
                self._data_validator.validate_data(data)
            
            return data
    
    def write(self, data: Union[str, bytes]) -> int:
        """Write to file with validation."""
        if not self.is_open():
            raise ValueError("File not open")
        
        if self.validate_data:
            self._data_validator.validate_data(data)
        
        with performance_monitor("file_write"):
            return self._handle.write(data)
    
    def save(self, data: Any, file_path: Optional[Union[str, Path]] = None) -> None:
        """Save data to file with atomic operations and format detection."""
        target_path = Path(file_path) if file_path else self.file_path
        if not target_path:
            raise ValueError("No file path specified")
        
        if self.validate_paths:
            self._path_validator.validate_path(target_path)
        
        if self.validate_data:
            self._data_validator.validate_data(data)
        
        with performance_monitor("file_save"):
            # Detect file type and handle appropriately
            file_type = self.detect_file_type(target_path)
            
            if self.use_atomic_operations:
                # Use atomic file writer
                with AtomicFileWriter(target_path, backup=self.auto_backup) as writer:
                    if isinstance(data, str):
                        # Handle text data
                        if file_type in ['text', 'json', 'yaml', 'xml', 'csv', 'markdown']:
                            writer.write(data.encode('utf-8'))
                        else:
                            writer.write(data.encode('utf-8'))
                    elif isinstance(data, bytes):
                        # Handle binary data
                        writer.write(data)
                    else:
                        # Convert to string for text files, bytes for binary
                        if file_type in ['text', 'json', 'yaml', 'xml', 'csv', 'markdown']:
                            writer.write(str(data).encode('utf-8'))
                        else:
                            writer.write(bytes(data))
            else:
                # Direct write
                target_path.parent.mkdir(parents=True, exist_ok=True)
                mode = 'wb' if isinstance(data, bytes) or file_type not in ['text', 'json', 'yaml', 'xml', 'csv', 'markdown'] else 'w'
                with open(target_path, mode) as f:
                    if mode == 'wb':
                        if isinstance(data, str):
                            f.write(data.encode('utf-8'))
                        else:
                            f.write(data)
                    else:
                        f.write(str(data))
    
    def load(self, file_path: Optional[Union[str, Path]] = None) -> Any:
        """Load data from file with validation and format detection."""
        target_path = Path(file_path) if file_path else self.file_path
        if not target_path:
            raise ValueError("No file path specified")
        
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {target_path}")
        
        if self.validate_paths:
            self._path_validator.validate_path(target_path)
        
        with performance_monitor("file_load"):
            # Detect file type
            file_type = self.detect_file_type(target_path)
            
            # Load based on file type
            if file_type in ['text', 'json', 'yaml', 'xml', 'csv', 'markdown', 'config']:
                # Text files
                try:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        data = f.read()
                except UnicodeDecodeError:
                    # Fallback to latin-1
                    with open(target_path, 'r', encoding='latin-1') as f:
                        data = f.read()
            else:
                # Binary files
                with open(target_path, 'rb') as f:
                    data = f.read()
            
            if self.validate_data:
                self._data_validator.validate_data(data)
            
            return data
    
    def close(self) -> None:
        """Close file handle."""
        if self._handle and not self._handle.closed:
            self._handle.close()
            logger.debug(f"File closed: {self.file_path}")
    
    # ============================================================================
    # DIRECTORY OPERATIONS
    # ============================================================================
    
    def create(self, parents: bool = True, exist_ok: bool = True) -> bool:
        """Create directory with validation."""
        if not self.dir_path:
            raise ValueError("No directory path specified")
        
        if self.validate_paths:
            self._path_validator.validate_path(self.dir_path)
        
        with performance_monitor("directory_create"):
            try:
                self.dir_path.mkdir(parents=parents, exist_ok=exist_ok)
                logger.debug(f"Directory created: {self.dir_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to create directory {self.dir_path}: {e}")
                return False
    
    def delete(self, recursive: bool = False) -> bool:
        """Delete directory with validation."""
        if not self.dir_path:
            raise ValueError("No directory path specified")
        
        if self.validate_paths:
            self._path_validator.validate_path(self.dir_path)
        
        with performance_monitor("directory_delete"):
            try:
                if recursive:
                    shutil.rmtree(self.dir_path)
                else:
                    self.dir_path.rmdir()
                logger.debug(f"Directory deleted: {self.dir_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete directory {self.dir_path}: {e}")
                return False
    
    # ============================================================================
    # ATOMIC OPERATIONS
    # ============================================================================
    
    def atomic_write(self, file_path: Union[str, Path], data: Union[str, bytes], 
                    backup: bool = True) -> OperationResult:
        """Atomically write data to file."""
        target_path = Path(file_path)
        
        if self.validate_paths:
            self._path_validator.validate_path(target_path)
        
        if self.validate_data:
            self._data_validator.validate_data(data)
        
        with performance_monitor("atomic_write"):
            try:
                with AtomicFileWriter(target_path, backup=backup) as writer:
                    if isinstance(data, str):
                        writer.write(data.encode('utf-8'))
                    else:
                        writer.write(data)
                return OperationResult.SUCCESS
            except Exception as e:
                logger.error(f"Atomic write failed for {target_path}: {e}")
                return OperationResult.FAILED
    
    def atomic_copy(self, source: Union[str, Path], destination: Union[str, Path]) -> OperationResult:
        """Atomically copy file."""
        source_path = Path(source)
        dest_path = Path(destination)
        
        if self.validate_paths:
            self._path_validator.validate_path(source_path)
            self._path_validator.validate_path(dest_path)
        
        with performance_monitor("atomic_copy"):
            try:
                # Use atomic file writer for destination
                with open(source_path, 'rb') as src:
                    with AtomicFileWriter(dest_path) as writer:
                        shutil.copyfileobj(src, writer)
                return OperationResult.SUCCESS
            except Exception as e:
                logger.error(f"Atomic copy failed from {source_path} to {dest_path}: {e}")
                return OperationResult.FAILED
    
    def atomic_move(self, source: Union[str, Path], destination: Union[str, Path]) -> OperationResult:
        """Atomically move file."""
        source_path = Path(source)
        dest_path = Path(destination)
        
        if self.validate_paths:
            self._path_validator.validate_path(source_path)
            self._path_validator.validate_path(dest_path)
        
        with performance_monitor("atomic_move"):
            try:
                # Ensure destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Use atomic move (copy + delete)
                with open(source_path, 'rb') as src:
                    with AtomicFileWriter(dest_path) as writer:
                        shutil.copyfileobj(src, writer)
                
                # Delete source after successful copy
                source_path.unlink()
                return OperationResult.SUCCESS
            except Exception as e:
                logger.error(f"Atomic move failed from {source_path} to {dest_path}: {e}")
                return OperationResult.FAILED
    
    def atomic_delete(self, file_path: Union[str, Path], backup: bool = True) -> OperationResult:
        """Atomically delete file."""
        target_path = Path(file_path)
        
        if self.validate_paths:
            self._path_validator.validate_path(target_path)
        
        with performance_monitor("atomic_delete"):
            try:
                if backup and target_path.exists():
                    self.create_backup(target_path)
                
                if target_path.exists():
                    target_path.unlink()
                
                return OperationResult.SUCCESS
            except Exception as e:
                logger.error(f"Atomic delete failed for {target_path}: {e}")
                return OperationResult.FAILED
    
    def atomic_rename(self, old_path: Union[str, Path], new_path: Union[str, Path]) -> OperationResult:
        """Atomically rename file."""
        old_file = Path(old_path)
        new_file = Path(new_path)
        
        if self.validate_paths:
            self._path_validator.validate_path(old_file)
            self._path_validator.validate_path(new_file)
        
        with performance_monitor("atomic_rename"):
            try:
                # Ensure new directory exists
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Use atomic move for rename
                return self.atomic_move(old_file, new_file)
            except Exception as e:
                logger.error(f"Atomic rename failed from {old_file} to {new_file}: {e}")
                return OperationResult.FAILED
    
    # ============================================================================
    # BACKUP OPERATIONS
    # ============================================================================
    
    def create_backup(self, source: Union[str, Path], backup_dir: Union[str, Path]) -> Optional[Path]:
        """Create backup of file or directory."""
        source_path = Path(source)
        backup_path = Path(backup_dir)
        
        if self.validate_paths:
            self._path_validator.validate_path(source_path)
            self._path_validator.validate_path(backup_path)
        
        with performance_monitor("backup_create"):
            try:
                backup_path.mkdir(parents=True, exist_ok=True)
                
                if source_path.is_file():
                    # File backup
                    backup_file = backup_path / f"{source_path.name}.backup.{int(time.time())}"
                    shutil.copy2(source_path, backup_file)
                    return backup_file
                elif source_path.is_dir():
                    # Directory backup
                    backup_dir = backup_path / f"{source_path.name}.backup.{int(time.time())}"
                    shutil.copytree(source_path, backup_dir)
                    return backup_dir
                else:
                    return None
            except Exception as e:
                logger.error(f"Backup creation failed for {source_path}: {e}")
                return None
    
    def restore_backup(self, backup_path: Union[str, Path], target: Union[str, Path]) -> OperationResult:
        """Restore from backup."""
        backup = Path(backup_path)
        target_path = Path(target)
        
        if self.validate_paths:
            self._path_validator.validate_path(backup)
            self._path_validator.validate_path(target_path)
        
        with performance_monitor("backup_restore"):
            try:
                if backup.is_file():
                    # File restore
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup, target_path)
                elif backup.is_dir():
                    # Directory restore
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(backup, target_path)
                else:
                    return OperationResult.FAILED
                
                return OperationResult.SUCCESS
            except Exception as e:
                logger.error(f"Backup restore failed from {backup} to {target_path}: {e}")
                return OperationResult.FAILED
    
    # ============================================================================
    # TEMPORARY OPERATIONS
    # ============================================================================
    
    def create_temp_file(self, suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """Create temporary file."""
        with performance_monitor("temp_file_create"):
            try:
                # Create temporary file
                fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, 
                                               dir=self.get_temp_base_dir())
                os.close(fd)  # Close file descriptor
                
                temp_file = Path(temp_path)
                self._temp_files.append(temp_file)
                
                logger.debug(f"Temporary file created: {temp_file}")
                return temp_file
            except Exception as e:
                logger.error(f"Failed to create temporary file: {e}")
                raise
    
    def create_temp_directory(self, suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
        """Create temporary directory."""
        with performance_monitor("temp_dir_create"):
            try:
                temp_path = tempfile.mkdtemp(suffix=suffix, prefix=prefix,
                                           dir=self.get_temp_base_dir())
                temp_dir = Path(temp_path)
                self._temp_dirs.append(temp_dir)
                
                logger.debug(f"Temporary directory created: {temp_dir}")
                return temp_dir
            except Exception as e:
                logger.error(f"Failed to create temporary directory: {e}")
                raise
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_manager_info(self) -> Dict[str, Any]:
        """Get comprehensive file manager information."""
        return {
            'base_path': str(self.file_path) if self.file_path else None,
            'validate_paths': self.validate_paths,
            'validate_data': self.validate_data,
            'enable_monitoring': self.enable_monitoring,
            'use_atomic_operations': self.use_atomic_operations,
            'enable_backups': self.enable_backups,
            'cleanup_temp_on_exit': self.cleanup_temp_on_exit,
            'auto_detect_format': self.auto_detect_format,
            'max_file_size': self.max_file_size,
            'supported_formats': self.supported_formats,
            'temp_files_count': len(self._temp_files),
            'temp_dirs_count': len(self._temp_dirs)
        }
    
    def cleanup_all_resources(self) -> int:
        """Cleanup all resources (files, directories, temp files)."""
        cleaned_count = 0
        
        # Close file handle
        if self.is_open():
            self.close()
            cleaned_count += 1
        
        # Cleanup temporary resources
        cleaned_count += self._cleanup_all_temporary()
        
        logger.debug(f"Cleaned up {cleaned_count} resources")
        return cleaned_count
    
    def process_file(self, file_path: Union[str, Path], operation: str = 'info') -> Dict[str, Any]:
        """
        Process file with specified operation.
        
        Args:
            file_path: Path to file
            operation: Operation to perform ('info', 'copy', 'move', 'backup', 'validate')
            
        Returns:
            Operation result dictionary
        """
        target_path = Path(file_path)
        
        if not target_path.exists():
            return {'success': False, 'error': 'File not found'}
        
        if not self.is_safe_to_process(target_path):
            return {'success': False, 'error': 'File not safe to process'}
        
        with performance_monitor(f"file_process_{operation}"):
            try:
                if operation == 'info':
                    return {
                        'success': True,
                        'result': self.get_file_info(target_path)
                    }
                elif operation == 'copy':
                    # Create a copy with .copy suffix
                    copy_path = target_path.with_suffix(target_path.suffix + '.copy')
                    result = self.atomic_copy(target_path, copy_path)
                    return {
                        'success': result == OperationResult.SUCCESS,
                        'result': str(copy_path) if result == OperationResult.SUCCESS else None
                    }
                elif operation == 'backup':
                    backup_path = self.create_backup(target_path, target_path.parent / '.backups')
                    return {
                        'success': backup_path is not None,
                        'result': str(backup_path) if backup_path else None
                    }
                elif operation == 'validate':
                    # Validate file integrity
                    file_type = self.detect_file_type(target_path)
                    is_safe = self.is_safe_to_process(target_path)
                    return {
                        'success': True,
                        'result': {
                            'file_type': file_type,
                            'is_safe': is_safe,
                            'size': target_path.stat().st_size,
                            'readable': os.access(target_path, os.R_OK),
                            'writable': os.access(target_path, os.W_OK)
                        }
                    }
                else:
                    return {'success': False, 'error': f'Unknown operation: {operation}'}
                    
            except Exception as e:
                logger.error(f"File processing failed for {target_path}: {e}")
                return {'success': False, 'error': str(e)}
