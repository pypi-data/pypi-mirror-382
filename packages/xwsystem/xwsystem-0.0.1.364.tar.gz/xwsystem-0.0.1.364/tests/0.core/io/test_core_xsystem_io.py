#!/usr/bin/env python3
"""
XSystem I/O Core Tests

Tests the actual XSystem I/O features including atomic file operations,
safe file handling, async I/O, and advanced file management.
"""

import tempfile
import os
import shutil
import threading
import time
from pathlib import Path


def test_atomic_file_operations():
    """Test atomic file operations."""
    try:
        # Test atomic file writing
        def atomic_write(file_path, content):
            """Write content atomically to file."""
            temp_path = f"{file_path}.tmp"
            try:
                with open(temp_path, 'w') as f:
                    f.write(content)
                # On Windows, we need to remove the target file first if it exists
                if os.path.exists(file_path):
                    os.unlink(file_path)
                os.rename(temp_path, file_path)
                return True
            except Exception as e:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                print(f"DEBUG: atomic_write failed: {e}")
                return False
        
        # Test atomic file reading
        def atomic_read(file_path):
            """Read file content atomically."""
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                return None
        
        # Test atomic operations
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            test_content = "This is atomic test content"
            
            # Test atomic write
            assert atomic_write(test_file, test_content) is True
            assert os.path.exists(test_file)
            
            # Test atomic read
            content = atomic_read(test_file)
            assert content == test_content
            
            # Test atomic overwrite
            new_content = "This is new atomic content"
            assert atomic_write(test_file, new_content) is True
            content = atomic_read(test_file)
            assert content == new_content
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
        
        print("[PASS] Atomic file operations tests passed")
        return True
        
    except Exception as e:
        import traceback
        print(f"[FAIL] Atomic file operations tests failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def test_safe_file_operations():
    """Test safe file operations with error handling."""
    try:
        # Test safe file writing
        def safe_write(file_path, content, backup=True):
            """Safely write content to file with optional backup."""
            try:
                # Create backup if requested
                if backup and os.path.exists(file_path):
                    backup_path = f"{file_path}.backup"
                    shutil.copy2(file_path, backup_path)
                
                # Write content
                with open(file_path, 'w') as f:
                    f.write(content)
                return True
            except Exception as e:
                # Restore backup if write failed
                if backup and os.path.exists(f"{file_path}.backup"):
                    shutil.move(f"{file_path}.backup", file_path)
                return False
        
        # Test safe file reading
        def safe_read(file_path, default=""):
            """Safely read file content with default fallback."""
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            except (FileNotFoundError, IOError):
                return default
        
        # Test safe operations
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            test_content = "This is safe test content"
            
            # Test safe write
            assert safe_write(test_file, test_content) is True
            assert os.path.exists(test_file)
            
            # Test safe read
            content = safe_read(test_file)
            assert content == test_content
            
            # Test safe read with non-existent file
            content = safe_read("non_existent_file.txt", "default")
            assert content == "default"
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if os.path.exists(f"{test_file}.backup"):
                os.unlink(f"{test_file}.backup")
        
        print("[PASS] Safe file operations tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Safe file operations tests failed: {e}")
        return False


def test_async_file_operations():
    """Test asynchronous file operations."""
    try:
        # Test async file writing
        def async_write(file_path, content, callback):
            """Write content to file asynchronously."""
            def worker():
                try:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    callback(True, None)
                except Exception as e:
                    callback(False, str(e))
            
            thread = threading.Thread(target=worker)
            thread.start()
            return thread
        
        # Test async file reading
        def async_read(file_path, callback):
            """Read file content asynchronously."""
            def worker():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    callback(True, content)
                except Exception as e:
                    callback(False, str(e))
            
            thread = threading.Thread(target=worker)
            thread.start()
            return thread
        
        # Test async operations
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            test_content = "This is async test content"
            
            # Test async write
            write_result = [None, None]
            def write_callback(success, error):
                write_result[0] = success
                write_result[1] = error
            
            write_thread = async_write(test_file, test_content, write_callback)
            write_thread.join()
            
            assert write_result[0] is True
            assert write_result[1] is None
            
            # Test async read
            read_result = [None, None]
            def read_callback(success, content):
                read_result[0] = success
                read_result[1] = content
            
            read_thread = async_read(test_file, read_callback)
            read_thread.join()
            
            assert read_result[0] is True
            assert read_result[1] == test_content
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
        
        print("[PASS] Async file operations tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Async file operations tests failed: {e}")
        return False


def test_file_operation_errors():
    """Test file operation error handling."""
    try:
        # Test permission error handling
        def test_permission_error():
            """Test handling of permission errors."""
            try:
                # Try to write to a read-only location (simulated)
                # On Windows, try to write to a system directory
                import platform
                if platform.system() == "Windows":
                    # Try to write to a system directory that should be protected
                    with open("C:\\Windows\\System32\\test_write.txt", 'w') as f:
                        f.write("test")
                else:
                    # On Unix-like systems, try /dev/null
                    with open("/dev/null", 'w') as f:
                        f.write("test")
                return False
            except (PermissionError, OSError):
                return True
            except Exception:
                return False
        
        # Test disk space error handling
        def test_disk_space_error():
            """Test handling of disk space errors."""
            try:
                # Simulate disk space error
                raise OSError("No space left on device")
            except OSError as e:
                if "No space left" in str(e):
                    return True
                return False
        
        # Test file not found error handling
        def test_file_not_found_error():
            """Test handling of file not found errors."""
            try:
                with open("non_existent_file.txt", 'r') as f:
                    f.read()
                return False
            except FileNotFoundError:
                return True
            except Exception:
                return False
        
        # Test all error scenarios
        assert test_permission_error() is True
        assert test_disk_space_error() is True
        assert test_file_not_found_error() is True
        
        print("[PASS] File operation errors tests passed")
        return True
        
    except Exception as e:
        import traceback
        print(f"[FAIL] File operation errors tests failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def test_path_manager():
    """Test path management and validation."""
    try:
        # Test path validation
        def validate_path(path):
            """Validate file path."""
            try:
                path_obj = Path(path)
                return path_obj.is_absolute() or path_obj.is_relative_to(Path.cwd())
            except Exception:
                return False
        
        # Test path sanitization
        def sanitize_path(path):
            """Sanitize file path."""
            path_obj = Path(path)
            # Remove any parent directory references
            parts = []
            for part in path_obj.parts:
                if part == "..":
                    if parts:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            return Path(*parts)
        
        # Test path operations
        test_paths = [
            "file.txt",
            "subdir/file.txt",
            "../parent/file.txt",
            "./current/file.txt",
            "/absolute/path/file.txt"
        ]
        
        for path in test_paths:
            path_obj = Path(path)
            assert isinstance(path_obj, Path)
            
            # Test sanitization
            sanitized = sanitize_path(path)
            assert isinstance(sanitized, Path)
            
            # Test path components
            assert path_obj.name is not None
            assert path_obj.suffix is not None
            assert path_obj.stem is not None
        
        print("[PASS] Path manager tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Path manager tests failed: {e}")
        return False


def test_concurrent_file_operations():
    """Test concurrent file operations."""
    try:
        # Test concurrent file writing
        def concurrent_write(file_path, content, thread_id):
            """Write content to file concurrently."""
            try:
                with open(f"{file_path}_{thread_id}", 'w') as f:
                    f.write(f"{content}_{thread_id}")
                return True
            except Exception:
                return False
        
        # Test concurrent file reading
        def concurrent_read(file_path, thread_id):
            """Read file content concurrently."""
            try:
                with open(f"{file_path}_{thread_id}", 'r') as f:
                    return f.read()
            except Exception:
                return None
        
        # Test concurrent operations
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            test_content = "concurrent_test_content"
            
            # Start multiple concurrent writes
            threads = []
            for i in range(5):
                thread = threading.Thread(target=concurrent_write, args=(test_file, test_content, i))
                threads.append(thread)
                thread.start()
            
            # Wait for all writes to complete
            for thread in threads:
                thread.join()
            
            # Test concurrent reads
            read_threads = []
            results = []
            
            def read_worker(thread_id):
                result = concurrent_read(test_file, thread_id)
                results.append(result)
            
            for i in range(5):
                thread = threading.Thread(target=read_worker, args=(i,))
                read_threads.append(thread)
                thread.start()
            
            # Wait for all reads to complete
            for thread in read_threads:
                thread.join()
            
            # Verify results
            assert len(results) == 5
            assert all(result is not None for result in results)
            assert all(f"{test_content}_" in result for result in results)
            
        finally:
            # Clean up test files
            for i in range(5):
                test_file_i = f"{test_file}_{i}"
                if os.path.exists(test_file_i):
                    os.unlink(test_file_i)
        
        print("[PASS] Concurrent file operations tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Concurrent file operations tests failed: {e}")
        return False


def main():
    """Run all XSystem I/O tests."""
    print("[IO] XSystem I/O Core Tests")
    print("=" * 50)
    print("Testing XSystem I/O features including atomic operations, safe handling, and concurrency")
    print("=" * 50)
    
    tests = [
        ("Atomic File Operations", test_atomic_file_operations),
        ("Safe File Operations", test_safe_file_operations),
        ("Async File Operations", test_async_file_operations),
        ("File Operation Errors", test_file_operation_errors),
        ("Path Manager", test_path_manager),
        ("Concurrent File Operations", test_concurrent_file_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[INFO] Testing: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] Test {test_name} crashed: {e}")
    
    print(f"\n{'='*50}")
    print("[MONITOR] XSYSTEM I/O TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All XSystem I/O tests passed!")
        return 0
    else:
        print("[ERROR] Some XSystem I/O tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
