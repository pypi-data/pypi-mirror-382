"""
xNode Integration Tests
=======================

Integration tests for real-world usage scenarios including:
- Complex hierarchical data operations
- Large data structure navigation
- Performance with deep nesting
- Real-world configuration handling
- JSON round-trip scenarios

Following pytest best practices and established test patterns.
"""

import pytest
import json
from pathlib import Path
import sys
import time

# Setup path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Import from conftest.py which sets up the proper imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from conftest import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
except ImportError:
    from src.xlib.xNode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
except ImportError:
    from xlib.xNode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.mark.integration
    def test_configuration_management(self, real_world_config):
        """Test managing complex configuration data."""
        config = xNode.from_native(real_world_config)
        
        # Access database configuration
        db_host = config.find('database.host')
        assert db_host.value == 'localhost'
        
        db_port = config.find('database.port')
        assert db_port.value == 5432
        
        # Access nested credentials
        username = config.find('database.credentials.username')
        assert username.value == 'admin'
        
        # Access array elements
        read_pool = config.find('database.pools.0.name')
        assert read_pool.value == 'read'
        
        # Access API endpoints
        first_endpoint = config.find('api.endpoints.0.path')
        assert first_endpoint.value == '/users'
        
        # Verify structure integrity
        assert config.is_dict
        assert config['database'].is_dict
        assert config['api']['endpoints'].is_list
    
    @pytest.mark.integration
    def test_json_roundtrip_complex_data(self, nested_data):
        """Test JSON round-trip with complex nested data."""
        # Create node from Python data
        original_node = xNode.from_native(nested_data)
        
        # Convert to JSON
        json_str = original_node.to_json()
        
        # Parse back from JSON
        roundtrip_node = xNode.from_json(json_str)
        
        # Verify data integrity
        assert original_node.value == roundtrip_node.value
        
        # Test specific nested access
        assert original_node.find('users.0.name').value == roundtrip_node.find('users.0.name').value
        assert original_node.find('metadata.version').value == roundtrip_node.find('metadata.version').value
    
    @pytest.mark.integration
    def test_data_exploration_workflow(self, nested_data):
        """Test typical data exploration workflow."""
        data = xNode.from_native(nested_data)
        
        # 1. Explore structure
        assert data.is_dict
        keys = list(data.keys())
        assert 'users' in keys
        assert 'metadata' in keys
        
        # 2. Examine users array
        users = data['users']
        assert users.is_list
        assert len(users) == 2
        
        # 3. Examine individual user
        first_user = users[0]
        assert first_user.is_dict
        user_keys = list(first_user.keys())
        assert 'name' in user_keys
        assert 'profile' in user_keys
        
        # 4. Deep exploration
        preferences = first_user['profile']['preferences']
        assert preferences.is_dict
        assert preferences['theme'].value == 'dark'
        
        # 5. Navigate using paths
        email = data.find('users.0.profile.email')
        assert email.value == 'alice@example.com'


class TestLargeDataStructures:
    """Test behavior with large data structures."""
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_large_array_navigation(self):
        """Test navigation in large arrays."""
        # Create large array
        large_array = [{'id': i, 'value': f'item_{i}'} for i in range(1000)]
        node = xNode.from_native(large_array)
        
        # Test access to various elements
        first_item = node.find('0.id')
        assert first_item.value == 0
        
        middle_item = node.find('500.value')
        assert middle_item.value == 'item_500'
        
        last_item = node.find('999.id')
        assert last_item.value == 999
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_deep_nesting_performance(self):
        """Test performance with deeply nested structures."""
        # Create deeply nested structure
        deep_data = {}
        current = deep_data
        
        for i in range(100):
            current[f'level_{i}'] = {}
            current = current[f'level_{i}']
        current['final_value'] = 'reached_the_end'
        
        # Measure navigation time
        node = xNode.from_native(deep_data)
        start_time = time.time()
        
        # Build path
        path_parts = [f'level_{i}' for i in range(100)] + ['final_value']
        deep_path = '.'.join(path_parts)
        
        result = node.find(deep_path)
        end_time = time.time()
        
        assert result.value == 'reached_the_end'
        # Should complete in reasonable time (< 1 second)
        assert (end_time - start_time) < 1.0
    
    @pytest.mark.integration
    @pytest.mark.performance 
    def test_wide_structure_performance(self):
        """Test performance with wide structures."""
        # Create wide structure
        wide_data = {}
        for i in range(10000):
            wide_data[f'key_{i:04d}'] = f'value_{i}'
        
        node = xNode.from_native(wide_data)
        
        # Test random access
        start_time = time.time()
        
        # Access various keys
        for i in [0, 1000, 5000, 9999]:
            key = f'key_{i:04d}'
            result = node[key]
            assert result.value == f'value_{i}'
        
        end_time = time.time()
        
        # Should complete quickly (< 0.1 seconds)
        assert (end_time - start_time) < 0.1


class TestComplexNavigationPatterns:
    """Test complex navigation patterns."""
    
    @pytest.mark.integration
    def test_mixed_access_patterns(self, complex_navigation_data):
        """Test mixing different access patterns in single workflow."""
        node = xNode.from_native(complex_navigation_data)
        
        # Pattern 1: Bracket notation chain
        backend_team = node['company']['departments'][0]['teams'][0]
        assert backend_team['name'].value == 'Backend'
        
        # Pattern 2: Mixed bracket and path notation
        alice_role = node['company']['departments'][0].find('teams.0.members.0.role')
        assert alice_role.value == 'lead'
        
        # Pattern 3: Path notation with arrays
        api_limit = node.find('config.features.api_limits.requests_per_minute')
        assert api_limit.value == 1000
        
        # Pattern 4: get() with defaults
        nonexistent = node.get('company.departments.0.teams.0.budget', 'not_set')
        assert nonexistent.value == 'not_set'
    
    @pytest.mark.integration
    def test_iterative_exploration(self, complex_navigation_data):
        """Test iterative data exploration patterns."""
        node = xNode.from_native(complex_navigation_data)
        
        # Explore all departments
        departments = node['company']['departments']
        dept_names = []
        
        for dept in departments:
            dept_names.append(dept['name'].value)
        
        assert 'Engineering' in dept_names
        assert 'Sales' in dept_names
        
        # Explore teams in first department
        engineering_teams = departments[0]['teams']
        team_names = []
        
        for team in engineering_teams:
            team_names.append(team['name'].value)
        
        assert 'Backend' in team_names
        assert 'Frontend' in team_names
        
        # Count total members across all teams
        total_members = 0
        for dept in departments:
            for team in dept['teams']:
                total_members += len(team['members'])
        
        assert total_members == 6  # 4 in Engineering + 2 in Sales


class TestErrorRecoveryInComplexScenarios:
    """Test error recovery in complex scenarios."""
    
    @pytest.mark.integration
    def test_partial_failure_recovery(self, nested_data):
        """Test recovery from partial failures in complex operations."""
        node = xNode.from_native(nested_data)
        
        # Some operations succeed
        valid_results = []
        valid_results.append(node.get('users.0.name', 'default'))
        valid_results.append(node.get('metadata.version', 'default'))
        
        # Some operations fail gracefully
        invalid_results = []
        invalid_results.append(node.get('users.0.nonexistent', 'default'))
        invalid_results.append(node.get('completely.invalid.path', 'default'))
        
        # Verify successful operations worked
        assert valid_results[0].value == 'Alice'
        assert valid_results[1].value == '1.0'
        
        # Verify failed operations returned defaults
        assert invalid_results[0].value == 'default'
        assert invalid_results[1].value == 'default'
        
        # Original node should still be functional
        assert node.find('users.1.name').value == 'Bob'
    
    @pytest.mark.integration
    def test_mixed_success_failure_workflow(self, real_world_config):
        """Test workflows with mixed success and failure scenarios."""
        config = xNode.from_native(real_world_config)
        
        # Build a configuration reader that handles missing values
        def get_config_value(path, default=None):
            return config.get(path, default)
        
        # Read various configuration values (some exist, some don't)
        db_host = get_config_value('database.host', 'localhost')
        db_timeout = get_config_value('database.timeout', 30)  # Doesn't exist
        api_port = get_config_value('api.port', 8080)  # Doesn't exist
        rate_limit = get_config_value('api.rate_limits.requests_per_minute', 100)
        
        # Verify results
        assert db_host.value == 'localhost'  # Existed
        assert db_timeout.value == 30  # Default used
        assert api_port.value == 8080  # Default used
        assert rate_limit.value == 1000  # Existed


class TestDataTransformation:
    """Test data transformation scenarios."""
    
    @pytest.mark.integration
    def test_data_extraction_and_transformation(self, nested_data):
        """Test extracting and transforming data."""
        node = xNode.from_native(nested_data)
        
        # Extract user information
        users_data = []
        users = node['users']
        
        for user in users:
            user_info = {
                'name': user['name'].value,
                'age': user['age'].value,
                'email': user['profile']['email'].value,
                'theme': user['profile']['preferences']['theme'].value
            }
            users_data.append(user_info)
        
        # Verify transformation
        assert len(users_data) == 2
        assert users_data[0]['name'] == 'Alice'
        assert users_data[0]['theme'] == 'dark'
        assert users_data[1]['name'] == 'Bob'
        assert users_data[1]['theme'] == 'light'
    
    @pytest.mark.integration
    def test_configuration_validation(self, real_world_config):
        """Test configuration validation patterns."""
        config = xNode.from_native(real_world_config)
        
        # Validate required configuration exists
        required_paths = [
            'database.host',
            'database.port',
            'database.credentials.username',
            'api.rate_limits.requests_per_minute'
        ]
        
        missing_configs = []
        for path in required_paths:
            if config.get(path) is None:
                missing_configs.append(path)
        
        # Should have no missing required configs
        assert len(missing_configs) == 0
        
        # Validate configuration values
        assert isinstance(config.find('database.port').value, int)
        assert config.find('database.port').value > 0
        assert config.find('api.rate_limits.requests_per_minute').value > 0


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 
