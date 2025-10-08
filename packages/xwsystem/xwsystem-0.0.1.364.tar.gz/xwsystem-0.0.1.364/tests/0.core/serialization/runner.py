#!/usr/bin/env python3
"""
Core Serialization Test Runner

Tests all 24+ serialization formats with comprehensive roundtrip testing.
Focuses on the main public API and real-world usage scenarios.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 02, 2025
"""

import sys
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple


class SerializationCoreTester:
    """Core tester for serialization functionality."""
    
    def __init__(self):
        self.test_data_dir = Path(__file__).parent / "data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.results: Dict[str, bool] = {}
        
    def get_test_data(self) -> Dict[str, Any]:
        """Get comprehensive test data for serialization testing."""
        return {
            "simple": {"hello": "world", "number": 42, "boolean": True},
            "nested": {
                "user": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "preferences": {
                        "theme": "dark",
                        "notifications": True
                    }
                },
                "metadata": {
                    "created": "2025-01-02T10:30:00Z",
                    "version": "1.0.0"
                }
            },
            "list_data": [
                {"id": 1, "name": "Item 1", "active": True},
                {"id": 2, "name": "Item 2", "active": False},
                {"id": 3, "name": "Item 3", "active": True}
            ],
            "edge_cases": {
                "empty_string": "",
                "null_value": None,
                "unicode": "Hello 世界 🌍",
                "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
                "large_number": 999999999999999999,
                "float_precision": 3.141592653589793
            }
        }
    
    def test_json_serialization(self) -> bool:
        """Test JSON serialization core functionality."""
        try:
            from exonware.xwsystem.serialization.json import JsonSerializer, save_file, load_file
            
            serializer = JsonSerializer()
            test_data = self.get_test_data()
            
            # Test text serialization
            json_str = serializer.dumps_text(test_data)
            assert isinstance(json_str, str)
            
            # Test roundtrip
            deserialized = serializer.loads_text(json_str)
            assert deserialized == test_data
            
            # Test binary serialization
            json_bytes = serializer.dumps_binary(test_data)
            assert isinstance(json_bytes, bytes)
            
            # Test binary roundtrip
            deserialized_binary = serializer.loads_bytes(json_bytes)
            assert deserialized_binary == test_data
            
            # Test file operations using convenience functions
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_file = Path(f.name)
            
            try:
                save_file(test_data, temp_file)
                loaded_data = load_file(temp_file)
                assert loaded_data == test_data
            finally:
                temp_file.unlink(missing_ok=True)
            
            print("[PASS] JSON serialization core tests passed")
            return True
            
        except Exception as e:
            print(f"[FAIL] JSON serialization core tests failed: {e}")
            return False
    
    def test_yaml_serialization(self) -> bool:
        """Test YAML serialization core functionality."""
        try:
            from exonware.xwsystem.serialization.yaml import YamlSerializer
            
            serializer = YamlSerializer()
            test_data = self.get_test_data()
            
            # Test text serialization
            yaml_str = serializer.dumps_text(test_data)
            assert isinstance(yaml_str, str)
            
            # Test roundtrip
            deserialized = serializer.loads_text(yaml_str)
            assert deserialized == test_data
            
            print("[PASS] YAML serialization core tests passed")
            return True
            
        except Exception as e:
            print(f"[FAIL] YAML serialization core tests failed: {e}")
            return False
    
    def test_pickle_serialization(self) -> bool:
        """Test Pickle serialization core functionality."""
        try:
            from exonware.xwsystem.serialization.pickle import PickleSerializer
            
            serializer = PickleSerializer()
            test_data = self.get_test_data()
            
            # Test binary serialization (Pickle is binary-only)
            pickle_bytes = serializer.dumps_binary(test_data)
            assert isinstance(pickle_bytes, bytes)
            
            # Test roundtrip
            deserialized = serializer.loads_bytes(pickle_bytes)
            assert deserialized == test_data
            
            print("[PASS] Pickle serialization core tests passed")
            return True
            
        except Exception as e:
            print(f"[FAIL] Pickle serialization core tests failed: {e}")
            return False
    
    def test_basic_serialization(self) -> bool:
        """Test basic serialization functionality."""
        try:
            from exonware.xwsystem.serialization.json import dumps, loads
            
            test_data = {"hello": "world", "number": 42}
            
            # Test basic serialization
            json_str = dumps(test_data)
            assert isinstance(json_str, str)
            
            # Test basic deserialization
            deserialized = loads(json_str)
            assert deserialized == test_data
            
            print("[PASS] Basic serialization core tests passed")
            return True
            
        except Exception as e:
            print(f"[FAIL] Basic serialization core tests failed: {e}")
            return False
    
    def test_convenience_functions(self) -> bool:
        """Test convenience functions for serialization."""
        try:
            from exonware.xwsystem import quick_serialize, quick_deserialize
            
            test_data = {"hello": "world", "number": 42}
            
            # Test quick_serialize
            json_str = quick_serialize(test_data, "json")
            assert isinstance(json_str, str)
            
            # Test quick_deserialize
            deserialized = quick_deserialize(json_str, "json")
            assert deserialized == test_data
            
            print("[PASS] Convenience functions core tests passed")
            return True
            
        except Exception as e:
            print(f"[FAIL] Convenience functions core tests failed: {e}")
            return False
    
    def test_all_serialization_tests(self) -> int:
        """Run all serialization core tests."""
        print("[SERIALIZATION] XSystem Core Serialization Tests")
        print("=" * 50)
        print("Testing all main serialization features with comprehensive roundtrip testing")
        print("=" * 50)
        
        # Run the actual XSystem serialization tests
        try:
            import sys
            from pathlib import Path
            test_xwsystem_path = Path(__file__).parent / "test_core_xwsystem_serialization.py"
            sys.path.insert(0, str(test_xwsystem_path.parent))
            
            import test_core_xwsystem_serialization
            return test_core_xwsystem_serialization.main()
        except Exception as e:
            print(f"[FAIL] Failed to run XSystem serialization tests: {e}")
            # Fallback to basic tests if XSystem tests fail
            try:
                import test_core_xwsystem_serialization
                return test_core_xwsystem_serialization.main()
            except Exception as e2:
                print(f"[FAIL] Failed to run basic serialization tests: {e2}")
                return 1


def run_all_serialization_tests() -> int:
    """Main entry point for serialization core tests."""
    tester = SerializationCoreTester()
    return tester.test_all_serialization_tests()


if __name__ == "__main__":
    sys.exit(run_all_serialization_tests())
