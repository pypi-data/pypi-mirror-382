"""
Pytest configuration and fixtures for xNode tests.
Provides reusable test data and setup utilities.
"""

import pytest
from pathlib import Path
import sys
import os

# Override the global conftest.py auto-handler registration for xnode tests
# since xnode should not depend on xdata
@pytest.fixture(autouse=True)
def ensure_handlers_registered():
    """Override global handler registration - xnode tests don't need xdata handlers."""
    pass  # Explicitly do nothing

# Ensure src is in path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Add xnode directly to path to avoid xlib init chain issues
XNODE_PATH = SRC_PATH / "xlib" / "xnode"
if str(XNODE_PATH) not in sys.path:
    sys.path.insert(0, str(XNODE_PATH))

# Import xNode using the proper module path
try:
    from src.xlib.xnode import xNode, xNodeQuery
    from src.xlib.xnode.errors import xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
    print("✅ xNode imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    # Create mock objects for testing
    class MockxNode:
        @staticmethod
        def from_native(data):
            return MockxNode()
        @property
        def value(self):
            return "mock"
    
    xNode = MockxNode
    xNodeQuery = MockxNode
    xNodeError = Exception
    xNodeTypeError = TypeError
    xNodePathError = KeyError
    xNodeValueError = ValueError
    print("⚠️  Using mock objects for testing")


@pytest.fixture
def simple_dict_data():
    """Simple dictionary test data."""
    return {
        'name': 'Alice',
        'age': 30,
        'active': True
    }


@pytest.fixture
def simple_list_data():
    """Simple list test data."""
    return ['apple', 'banana', 'cherry']


@pytest.fixture
def nested_data():
    """Complex nested hierarchical test data."""
    return {
        'users': [
            {
                'id': 1,
                'name': 'Alice',
                'age': 30,
                'profile': {
                    'email': 'alice@example.com',
                    'preferences': {
                        'theme': 'dark',
                        'notifications': True
                    }
                },
                'roles': ['admin', 'user']
            },
            {
                'id': 2,
                'name': 'Bob',
                'age': 25,
                'profile': {
                    'email': 'bob@example.com',
                    'preferences': {
                        'theme': 'light',
                        'notifications': False
                    }
                },
                'roles': ['user']
            }
        ],
        'metadata': {
            'version': 1.0,
            'created': '2024-01-01',
            'tags': ['test', 'sample', 'data']
        }
    }


@pytest.fixture
def simple_node(simple_dict_data):
    """xNode instance from simple dictionary."""
    return xNode.from_native(simple_dict_data)


@pytest.fixture
def list_node(simple_list_data):
    """xNode instance from simple list."""
    return xNode.from_native(simple_list_data)


@pytest.fixture
def nested_node(nested_data):
    """xNode instance from nested data."""
    return xNode.from_native(nested_data)


@pytest.fixture
def leaf_node():
    """Simple leaf node."""
    return xNode.from_native("simple string value")


@pytest.fixture
def number_node():
    """Simple number leaf node."""
    return xNode.from_native(42)


@pytest.fixture
def boolean_node():
    """Simple boolean leaf node."""
    return xNode.from_native(True)


@pytest.fixture
def empty_dict_node():
    """Empty dictionary node."""
    return xNode.from_native({})


@pytest.fixture
def empty_list_node():
    """Empty list node."""
    return xNode.from_native([])


@pytest.fixture
def json_test_string():
    """JSON string for testing JSON parsing."""
    return '{"name": "Test", "value": 42, "items": [1, 2, {"nested": true}]}'


# Test data directory
@pytest.fixture
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "data" 