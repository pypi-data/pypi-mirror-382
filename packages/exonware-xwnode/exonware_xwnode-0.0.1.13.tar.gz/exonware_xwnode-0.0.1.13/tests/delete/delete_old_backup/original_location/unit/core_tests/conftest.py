"""
Core tests specific configuration and fixtures.
"""

import pytest
from pathlib import Path
import sys

# Import parent conftest fixtures
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import *  # Import all parent fixtures

# Additional core-specific fixtures
@pytest.fixture
def mixed_type_data():
    """Data with mixed types for comprehensive testing."""
    return {
        'string': 'hello',
        'integer': 42,
        'float': 3.14,
        'boolean': True,
        'null': None,
        'list': [1, 2, 3],
        'dict': {'nested': 'value'}
    }


@pytest.fixture
def json_test_data():
    """Valid JSON string for testing JSON parsing."""
    return '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], "meta": {"count": 2}}'


@pytest.fixture  
def invalid_json_data():
    """Invalid JSON string for error testing."""
    return '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], "meta": {"count": 2}'  # Missing closing brace 