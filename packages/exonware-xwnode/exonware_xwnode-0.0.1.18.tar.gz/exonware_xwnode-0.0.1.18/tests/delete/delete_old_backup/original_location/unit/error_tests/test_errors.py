"""
xNode Error Handling Tests
==========================

Comprehensive tests for xNode error handling including:
- xNodePathError scenarios
- xNodeTypeError conditions
- xNodeValueError handling
- Edge cases and boundary conditions
- Exception inheritance and behavior

Following pytest best practices and established test patterns.
"""

import pytest
import json
from pathlib import Path
import sys

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
    from src.xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
    

class TestxNodeErrorHierarchy:
    """Test the xNode exception hierarchy and inheritance."""
    
    @pytest.mark.errors
    def test_exception_inheritance(self):
        """Test that all xNode exceptions inherit from xNodeError."""
        assert issubclass(xNodeTypeError, xNodeError)
        assert issubclass(xNodePathError, xNodeError)
        assert issubclass(xNodeValueError, xNodeError)
        
        # Test standard exception inheritance
        assert issubclass(xNodeTypeError, TypeError)
        assert issubclass(xNodePathError, KeyError)
        assert issubclass(xNodeValueError, ValueError)
    
    @pytest.mark.errors
    def test_exception_instantiation(self):
        """Test that exceptions can be instantiated properly."""
        base_error = xNodeError("Base error message")
        assert str(base_error) == "Base error message"
        
        type_error = xNodeTypeError("Type error message")
        # Note: isolated module loading may add quotes around the message
        assert str(type_error) in ["Type error message", "'Type error message'"]
        
        path_error = xNodePathError("Path error message")
        # Note: isolated module loading may add quotes around the message
        assert str(path_error) in ["Path error message", "'Path error message'"]
        
        value_error = xNodeValueError("Value error message")
        # Note: isolated module loading may add quotes around the message
        assert str(value_error) in ["Value error message", "'Value error message'"]


class TestxNodePathErrorScenarios:
    """Test scenarios that should raise xNodePathError."""
    
    @pytest.mark.errors
    def test_nonexistent_key_access(self, simple_node):
        """Test accessing nonexistent keys raises xNodePathError."""
        with pytest.raises(xNodePathError) as exc_info:
            simple_node['nonexistent_key']
        
        assert "Key not found: 'nonexistent_key'" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_out_of_bounds_list_access(self, list_node):
        """Test accessing out-of-bounds list indices raises xNodePathError."""
        with pytest.raises(xNodePathError) as exc_info:
            list_node[100]
        
        assert "List index out of range: 100" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_negative_index_out_of_bounds(self, list_node):
        """Test accessing negative out-of-bounds indices raises xNodePathError."""
        with pytest.raises(xNodePathError) as exc_info:
            list_node[-10]  # Only 5 elements, so -10 is out of bounds
        
        assert "List index out of range: -10" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_invalid_path_navigation(self, nested_node):
        """Test invalid path navigation raises xNodePathError."""
        with pytest.raises(xNodePathError) as exc_info:
            nested_node.find('nonexistent.deep.path')
        
        # Note: isolated module loading may affect string formatting in error messages
        error_msg = str(exc_info.value)
        assert "Cannot resolve path" in error_msg and "nonexistent.deep.path" in error_msg
    
    @pytest.mark.errors
    def test_path_navigation_through_leaf(self, nested_node):
        """Test path navigation through leaf nodes raises xNodePathError."""
        with pytest.raises(xNodePathError) as exc_info:
            nested_node.find('users.0.name.invalid.path')
        
        assert "Cannot resolve path" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_array_access_with_string_on_list(self, list_node):
        """Test accessing list with non-numeric string raises xNodePathError."""
        with pytest.raises(xNodePathError) as exc_info:
            list_node.find('invalid_string_index')
        
        assert "Cannot resolve path" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_complex_invalid_path(self, nested_node):
        """Test complex invalid path scenarios."""
        # Mix of valid and invalid path components
        with pytest.raises(xNodePathError):
            nested_node.find('users.0.invalid.name')
        
        with pytest.raises(xNodePathError):
            nested_node.find('users.10.name')  # Invalid index
        
        with pytest.raises(xNodePathError):
            nested_node.find('metadata.tags.10')  # Index out of bounds


class TestxNodeTypeErrorScenarios:
    """Test scenarios that should raise xNodeTypeError."""
    
    @pytest.mark.errors
    def test_child_access_on_leaf_node(self, leaf_node):
        """Test that accessing children of leaf nodes raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            leaf_node['any_key']
        
        assert "Cannot access children of a leaf node" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_len_on_leaf_node(self, leaf_node):
        """Test that len() on leaf nodes raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            len(leaf_node)
        
        assert "Leaf nodes have no length" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_iteration_on_leaf_node(self, leaf_node):
        """Test that iteration on leaf nodes raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            list(leaf_node)
        
        assert "Cannot iterate over a leaf node" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_keys_on_non_dict_node(self, list_node, leaf_node):
        """Test that keys() on non-dict nodes raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            list(list_node.keys())
        
        assert "Only dict nodes have keys" in str(exc_info.value)
        
        with pytest.raises(xNodeTypeError) as exc_info:
            list(leaf_node.keys())
        
        assert "Only dict nodes have keys" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_items_on_non_dict_node(self, list_node, leaf_node):
        """Test that items() on non-dict nodes raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            list(list_node.items())
        
        assert "Only dict nodes have items" in str(exc_info.value)
        
        with pytest.raises(xNodeTypeError) as exc_info:
            list(leaf_node.items())
        
        assert "Only dict nodes have items" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_string_index_on_list_node(self, list_node):
        """Test that string indices on lists raise appropriate type errors."""
        with pytest.raises(xNodeTypeError) as exc_info:
            list_node._node._get_child('string_index')  # Access internal method
        
        assert "List indices must be integers" in str(exc_info.value)


class TestJSONParsingErrors:
    """Test JSON parsing error scenarios."""
    
    @pytest.mark.errors
    def test_invalid_json_syntax(self):
        """Test that invalid JSON syntax raises json.JSONDecodeError."""
        invalid_json = '{"key": "value"'  # Missing closing brace
        
        with pytest.raises(json.JSONDecodeError):
            xNode.from_json(invalid_json)
    
    @pytest.mark.errors
    def test_malformed_json_array(self):
        """Test malformed JSON array raises json.JSONDecodeError."""
        invalid_json = '[1, 2, 3'  # Missing closing bracket
        
        with pytest.raises(json.JSONDecodeError):
            xNode.from_json(invalid_json)
    
    @pytest.mark.errors
    def test_invalid_json_values(self):
        """Test invalid JSON values raise json.JSONDecodeError."""
        # Unquoted strings are invalid in JSON
        invalid_json = '{key: "value"}'
        
        with pytest.raises(json.JSONDecodeError):
            xNode.from_json(invalid_json)
    
    @pytest.mark.errors
    def test_empty_json_string(self):
        """Test empty JSON string raises json.JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            xNode.from_json('')
    
    @pytest.mark.errors
    def test_none_json_input(self):
        """Test None input to from_json raises appropriate error."""
        with pytest.raises((TypeError, AttributeError)):
            xNode.from_json(None)


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""
    
    @pytest.mark.errors
    def test_very_deep_invalid_navigation(self):
        """Test very deep invalid navigation paths."""
        node = xNode.from_native({'a': {'b': {'c': 'value'}}})
        
        # Valid path
        assert node.find('a.b.c').value == 'value'
        
        # Invalid continuation
        with pytest.raises(xNodePathError):
            node.find('a.b.c.d.e.f.g.h.i.j')
    
    @pytest.mark.errors
    def test_mixed_valid_invalid_paths(self, nested_node):
        """Test paths that start valid but become invalid."""
        # Start with valid path, then go invalid
        with pytest.raises(xNodePathError):
            nested_node.find('users.0.name.invalid.continuation')
        
        with pytest.raises(xNodePathError):
            nested_node.find('metadata.version.more.levels')
    
    @pytest.mark.errors
    def test_edge_case_indices(self, list_node):
        """Test edge case index values."""
        # Test maximum integer (should be out of bounds)
        with pytest.raises(xNodePathError):
            list_node[2**31]
        
        # Test very negative number
        with pytest.raises(xNodePathError):
            list_node[-1000]
    
    @pytest.mark.errors
    def test_empty_containers_navigation(self, empty_dict_node, empty_list_node):
        """Test navigation on empty containers."""
        # Empty dict access
        with pytest.raises(xNodePathError):
            empty_dict_node['any_key']
        
        # Empty list access
        with pytest.raises(xNodePathError):
            empty_list_node[0]
        
        # Path navigation on empty containers
        with pytest.raises(xNodePathError):
            empty_dict_node.find('any.path')
        
        with pytest.raises(xNodePathError):
            empty_list_node.find('0.path')


class TestErrorMessages:
    """Test that error messages are informative and helpful."""
    
    @pytest.mark.errors
    def test_path_error_contains_full_path(self, nested_node):
        """Test that path errors contain the full attempted path."""
        invalid_path = 'users.0.nonexistent.deep.path'
        
        with pytest.raises(xNodePathError) as exc_info:
            nested_node.find(invalid_path)
        
        # Error message should contain the full path
        assert invalid_path in str(exc_info.value)
    
    @pytest.mark.errors
    def test_key_error_contains_key_name(self, simple_node):
        """Test that key errors contain the specific key name."""
        missing_key = 'definitely_not_there'
        
        with pytest.raises(xNodePathError) as exc_info:
            simple_node[missing_key]
        
        assert missing_key in str(exc_info.value)
    
    @pytest.mark.errors
    def test_index_error_contains_index_value(self, list_node):
        """Test that index errors contain the specific index value."""
        invalid_index = 999
        
        with pytest.raises(xNodePathError) as exc_info:
            list_node[invalid_index]
        
        assert str(invalid_index) in str(exc_info.value)
    
    @pytest.mark.errors
    def test_type_error_describes_operation(self, leaf_node):
        """Test that type errors describe the invalid operation."""
        with pytest.raises(xNodeTypeError) as exc_info:
            len(leaf_node)
        
        assert "Leaf nodes have no length" in str(exc_info.value)
        
        with pytest.raises(xNodeTypeError) as exc_info:
            list(leaf_node)
        
        assert "Cannot iterate over a leaf node" in str(exc_info.value)


class TestErrorRecovery:
    """Test error recovery and graceful handling."""
    
    @pytest.mark.errors
    def test_get_method_error_recovery(self, nested_node):
        """Test that get() method gracefully handles errors."""
        # Should return None instead of raising exception
        result = nested_node.get('nonexistent.path')
        assert result is None
        
        # Should return default instead of raising exception
        default_value = 'fallback'
        result = nested_node.get('nonexistent.path', default_value)
        assert result.value == default_value
    
    @pytest.mark.errors
    def test_get_method_with_type_errors(self, leaf_node):
        """Test get() method with operations that would cause type errors."""
        # Should return None instead of raising xNodeTypeError
        result = leaf_node.get('some.path')
        assert result is None
        
        # Should return default instead of raising xNodeTypeError
        result = leaf_node.get('some.path', 'default')
        assert result.value == 'default'
    
    @pytest.mark.errors
    def test_partial_path_success(self, nested_node):
        """Test that partial paths can succeed even if deeper paths fail."""
        # This should work
        users = nested_node.find('users')
        assert users.is_list
        
        first_user = nested_node.find('users.0')
        assert first_user.is_dict
        
        # But this should fail
        with pytest.raises(xNodePathError):
            nested_node.find('users.0.nonexistent')


class TestConcurrentErrorHandling:
    """Test error handling in concurrent scenarios (if applicable)."""
    
    @pytest.mark.errors
    def test_multiple_error_scenarios(self, nested_node):
        """Test multiple different error scenarios on the same node."""
        # Multiple different types of errors should not interfere
        
        with pytest.raises(xNodePathError):
            nested_node.find('nonexistent1')
        
        with pytest.raises(xNodePathError):
            nested_node.find('nonexistent2.path')
        
        with pytest.raises(xNodePathError):
            nested_node['missing_key']
        
        # Node should still be functional after errors
        assert nested_node.find('users.0.name').value == 'Alice'
    
    @pytest.mark.errors
    def test_error_state_isolation(self, nested_node, leaf_node):
        """Test that errors on one node don't affect other nodes."""
        # Error on leaf node
        with pytest.raises(xNodeTypeError):
            len(leaf_node)
        
        # nested_node should still work fine
        assert len(nested_node) == 2  # users and metadata
        
        # Error on nested_node
        with pytest.raises(xNodePathError):
            nested_node['nonexistent']
        
        # leaf_node should still work fine
        assert leaf_node.value == "simple string value"


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 
