"""
Core Tests for XSystem

This package contains comprehensive core tests that verify the main functionality
of XSystem's core features. These tests focus on:

1. Serialization - All 24+ formats with roundtrip testing
2. Security - Crypto, hashing, path validation
3. HTTP - Client operations, retry logic, async support
4. I/O - Atomic file operations, async operations
5. Monitoring - Performance monitoring, memory monitoring, circuit breakers
6. Threading - Thread-safe operations, async primitives
7. Caching - LRU, LFU, TTL caches
8. Validation - Data validation, declarative models

Each core feature is tested individually with real data and comprehensive
roundtrip testing to ensure production readiness.
"""

from exonware.xwsystem.version import __version__