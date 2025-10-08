#!/usr/bin/env python3
"""
Single test runner for xSystem - consolidates all test execution.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: January 02, 2025
"""

import sys
import subprocess
from pathlib import Path


def run_tests_with_pytest(test_path: str, marker: str = None, category: str = None):
    """Run tests using pytest with appropriate configuration."""
    
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    
    # Configure pytest arguments
    pytest_args = [
        str(test_dir / test_path),
        "-v",                    # Verbose output
        "--tb=short",           # Short traceback format
        "-x",                   # Stop on first failure
        "--strict-markers",     # Treat unknown markers as errors
    ]
    
    # Add marker if specified
    if marker:
        pytest_args.extend(["-m", marker])
    
    # Add coverage if available
    try:
        import coverage
        pytest_args.extend([
            "--cov=exonware.xwsystem",
            "--cov-report=term-missing"
        ])
    except ImportError:
        pass
    
    # Run tests using subprocess to avoid import issues
    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        # pytest not installed, try to install it
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode


def run_core_tests():
    """Run all core tests."""
    print("🚀 Running CORE tests...")
    print("=" * 50)
    return run_tests_with_pytest("core", "xwsystem_core")


def run_unit_tests():
    """Run all unit tests."""
    print("🚀 Running UNIT tests...")
    print("=" * 50)
    return run_tests_with_pytest("unit", "xwsystem_unit")


def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Running INTEGRATION tests...")
    print("=" * 50)
    return run_tests_with_pytest("integration", "xwsystem_integration")


def run_performance_tests():
    """Run all performance tests."""
    print("🚀 Running PERFORMANCE tests...")
    print("=" * 50)
    return run_tests_with_pytest("performance", "xwsystem_performance")


def run_specific_unit_category(category: str):
    """Run specific unit test category."""
    
    test_dir = Path(__file__).parent / "unit" / category
    
    if not test_dir.exists():
        print(f"❌ Test category '{category}' not found")
        print("Available unit categories:")
        unit_dir = Path(__file__).parent / "unit"
        for item in unit_dir.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                print(f"  - {item.name}")
        return 1
    
    print(f"🚀 Running unit category: {category}")
    print("=" * 50)
    
    pytest_args = [
        str(test_dir),
        "-v",
        "--tb=short",
        "-x",
        "--strict-markers",
        "-m", f"xwsystem_{category}",
    ]
    
    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print("Installing pytest...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode


def run_all_tests():
    """Run all tests (core, unit, integration, performance) in sequence."""
    
    test_categories = [
        ('core', run_core_tests),
        ('unit', run_unit_tests),
        ('integration', run_integration_tests),
        ('performance', run_performance_tests)
    ]
    results = {}
    
    print("🚀 xSystem Test Suite")
    print("=" * 50)
    
    for category, test_func in test_categories:
        print(f"\n📁 Running {category.upper()} tests...")
        print("-" * 30)
        
        try:
            result = test_func()
            results[category] = result
            if result == 0:
                print(f"✅ {category.upper()} tests PASSED")
            else:
                print(f"❌ {category.upper()} tests FAILED")
        except Exception as e:
            print(f"❌ Error running {category} tests: {e}")
            results[category] = 1
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    all_passed = True
    for category, result in results.items():
        status = "✅ PASSED" if result == 0 else "❌ FAILED"
        print(f"{category.upper():<15}: {status}")
        if result != 0:
            all_passed = False
    
    print(f"\nOverall: {'🎉 ALL TESTS PASSED' if all_passed else '💥 SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


def run_with_pytest(category: str = None, marker: str = None):
    """Run tests using pytest directly."""
    
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    if category:
        cmd.extend([f"tests/{category}/"])
    
    if marker:
        cmd.extend(["-m", marker])
    
    print(f"🚀 Running pytest: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return 1


def show_help():
    """Show help information."""
    print("""
🚀 xSystem Test Runner (Single Runner)

Usage:
  python runner.py [command] [options]

Commands:
  all                    Run all tests (default)
  core                   Run core tests only
  unit                   Run unit tests only
  integration            Run integration tests only
  performance            Run performance tests only
  pytest [category]      Run tests using pytest directly
  unit-category <name>   Run specific unit test category

Examples:
  python runner.py                    # Run all tests
  python runner.py core              # Run core tests only
  python runner.py pytest unit       # Run unit tests with pytest
  python runner.py pytest -m xwsystem_security  # Run security tests
  python runner.py unit-category security_tests  # Run security unit tests

Available Unit Categories:
  - config_tests
  - io_tests
  - patterns_tests
  - performance_tests
  - security_tests
  - serialization_tests
  - structures_tests
  - threading_tests

Markers:
  -m xwsystem_core         Core functionality tests
  -m xwsystem_unit         Unit tests
  -m xwsystem_integration  Integration tests
  -m xwsystem_security     Security tests
  -m xwsystem_serialization Serialization tests
  -m xwsystem_performance  Performance tests
""")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help" or command == "--help" or command == "-h":
            show_help()
            exit_code = 0
        elif command == "pytest":
            category = sys.argv[2] if len(sys.argv) > 2 else None
            marker = None
            if len(sys.argv) > 3 and sys.argv[2] == "-m":
                marker = sys.argv[3]
                category = None
            exit_code = run_with_pytest(category, marker)
        elif command == "unit-category" and len(sys.argv) > 2:
            # Run specific unit category
            exit_code = run_specific_unit_category(sys.argv[2])
        elif command == "core":
            exit_code = run_core_tests()
        elif command == "unit":
            exit_code = run_unit_tests()
        elif command == "integration":
            exit_code = run_integration_tests()
        elif command == "performance":
            exit_code = run_performance_tests()
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            exit_code = 1
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
