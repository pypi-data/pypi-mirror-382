"""
Integration tests specific configuration and fixtures.
"""

import pytest
from pathlib import Path
import sys

# Import parent conftest fixtures
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import *  # Import all parent fixtures

# Additional integration-specific fixtures
@pytest.fixture
def real_world_config():
    """Real-world configuration-like data."""
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret"
            },
            "pools": [
                {"name": "read", "max_connections": 10},
                {"name": "write", "max_connections": 5}
            ]
        },
        "api": {
            "endpoints": [
                {
                    "path": "/users",
                    "methods": ["GET", "POST"],
                    "auth_required": True
                },
                {
                    "path": "/health",
                    "methods": ["GET"],
                    "auth_required": False
                }
            ],
            "rate_limits": {
                "requests_per_minute": 1000,
                "burst_allowance": 100
            }
        }
    }


@pytest.fixture
def complex_navigation_data():
    """Complex data structure for navigation testing."""
    return {
        'company': {
            'name': 'TechCorp',
            'departments': [
                {
                    'name': 'Engineering',
                    'teams': [
                        {
                            'name': 'Backend',
                            'members': [
                                {'name': 'Alice', 'role': 'lead'},
                                {'name': 'Bob', 'role': 'developer'}
                            ]
                        },
                        {
                            'name': 'Frontend', 
                            'members': [
                                {'name': 'Charlie', 'role': 'lead'},
                                {'name': 'Diana', 'role': 'developer'}
                            ]
                        }
                    ]
                },
                {
                    'name': 'Sales',
                    'teams': [
                        {
                            'name': 'Enterprise',
                            'members': [
                                {'name': 'Eve', 'role': 'manager'},
                                {'name': 'Frank', 'role': 'rep'}
                            ]
                        }
                    ]
                }
            ]
        },
        'config': {
            'version': '2.1.0',
            'features': {
                'auth': True,
                'analytics': False,
                'api_limits': {
                    'requests_per_minute': 1000,
                    'max_payload_size': '10MB'
                }
            }
        }
    }