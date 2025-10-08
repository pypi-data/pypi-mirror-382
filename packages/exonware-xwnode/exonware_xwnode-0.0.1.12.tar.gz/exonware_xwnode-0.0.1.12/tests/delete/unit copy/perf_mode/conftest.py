"""
Performance Mode Test Configuration
==================================

Shared fixtures and configuration for performance mode tests.
"""

import pytest
import sys
import os
import gc
import time
from pathlib import Path
from contextlib import contextmanager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

# Import test configuration
try:
    from .test_config import *
except ImportError:
    # Default values if config file doesn't exist
    TEST_USERS_COUNT = 2000
    TEST_DEEP_NESTING_LEVELS = 15
    TEST_WIDE_STRUCTURE_KEYS = 3000
    TEST_LARGE_DATA_ITEMS = 5000
    BENCHMARK_COMPREHENSIVE_OPS = 50
    BENCHMARK_MEMORY_OPS = 100
    BENCHMARK_SPEED_OPS = 150
    BENCHMARK_ADAPTIVE_OPS = 200
    BENCHMARK_LEARNING_OPS = 200

from src.xlib.xwnode import xwnode
from src.xlib.xwsystem.config import PerformanceMode
from src.xlib.xwnode.config import reset_performance_manager, set_performance_mode


@pytest.fixture(autouse=True)
def isolate_performance_tests():
    """Automatically isolate each test with proper state management."""
    # Setup: Reset before test
    reset_performance_manager()
    gc.collect()
    
    yield  # Run test
    
    # Teardown: Clean up after test
    reset_performance_manager()
    set_performance_mode(PerformanceMode.DEFAULT)
    gc.collect()
    time.sleep(0.01)  # Brief pause for cleanup


@pytest.fixture
def clean_performance_manager():
    """Provide a clean performance manager for each test."""
    reset_performance_manager()
    yield
    reset_performance_manager()


@contextmanager
def timeout_context(seconds):
    """Context manager for operation timeouts (Windows compatible)."""
    import platform
    
    if platform.system() == "Windows":
        # Windows doesn't support SIGALRM, use threading instead
        import threading
        
        timeout_occurred = [False]
        
        def timeout_handler():
            timeout_occurred[0] = True
        
        timer = threading.Timer(seconds, timeout_handler)
        timer.start()
        
        try:
            yield
            if timeout_occurred[0]:
                raise TimeoutError(f"Operation exceeded {seconds} seconds")
        finally:
            timer.cancel()
    else:
        # Unix systems support SIGALRM
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Operation exceeded {seconds} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


@pytest.fixture(scope="module")
def test_data():
    """Create test data for performance testing (cached per module)."""
    return {
        'users': [
            {'id': i, 'name': f'User{i}', 'email': f'user{i}@example.com', 'active': i % 2 == 0}
            for i in range(TEST_USERS_COUNT)  # Controlled by runner configuration
        ],
        'settings': {
            'theme': 'dark',
            'language': 'en',
            'notifications': True,
            'privacy': {'share_data': False, 'analytics': True}
        },
        'metadata': {
            'version': '1.0.0',
            'created': '2024-01-01',
            'tags': ['test', 'performance', 'comparison']
        }
    }


@pytest.fixture(scope="module")
def deep_nested_data():
    """Create deeply nested test data (cached per module)."""
    def create_nested(level, max_level=TEST_DEEP_NESTING_LEVELS):  # Controlled by runner configuration
        if level >= max_level:
            return f'value_at_level_{level}'
        return {
            f'level_{level}': create_nested(level + 1, max_level),
            f'list_{level}': [create_nested(level + 1, max_level) for _ in range(5)],
            f'data_{level}': {'nested': create_nested(level + 1, max_level)}
        }
    return create_nested(0)


@pytest.fixture(scope="module")
def wide_structure_data():
    """Create wide structure test data (cached per module)."""
    return {
        f'key_{i}': {
            'id': i,
            'name': f'Item{i}',
            'value': i * 1.5,
            'active': i % 3 == 0,
            'metadata': {'created': f'2024-{i%12+1:02d}-01', 'priority': i % 5}
        }
        for i in range(TEST_WIDE_STRUCTURE_KEYS)  # Controlled by runner configuration
    }


@pytest.fixture
def small_data():
    """Create small test data."""
    return {'key': 'value', 'number': 42, 'active': True}


@pytest.fixture(scope="module")
def large_data():
    """Create large test data (cached per module)."""
    return {
        'items': [{'id': i, 'data': f'item_{i}', 'nested': {'value': i * 2}} for i in range(TEST_LARGE_DATA_ITEMS)],  # Controlled by runner configuration
        'config': {'setting1': True, 'setting2': False, 'setting3': 'test'},
        'metadata': {'version': '2.0.0', 'created': '2024-01-01'}
    }


@pytest.fixture
def all_performance_modes():
    """Get all available performance modes."""
    return [
        PerformanceMode.AUTO,
        PerformanceMode.DEFAULT,
        PerformanceMode.FAST,
        PerformanceMode.OPTIMIZED,
        PerformanceMode.ADAPTIVE,
        PerformanceMode.MANUAL
    ]
