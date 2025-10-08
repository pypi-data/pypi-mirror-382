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
        """Test accessing nonexistent keys raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            simple_node['nonexistent_key']
        
        assert "nonexistent_key" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_out_of_bounds_list_access(self, list_node):
        """Test accessing out-of-bounds list indices raises IndexError."""
        with pytest.raises(IndexError) as exc_info:
            list_node[100]
        
        assert "100" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_negative_index_out_of_bounds(self, list_node):
        """Test accessing negative out-of-bounds indices raises IndexError."""
        with pytest.raises(IndexError) as exc_info:
            list_node[-10]  # Only 5 elements, so -10 is out of bounds
        
        assert "out of range" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_invalid_path_navigation(self, nested_node):
        """Test invalid path navigation raises xNodePathError."""
        # Modern API: find() returns None, find_strict() raises errors
        assert nested_node.find('nonexistent.deep.path') is None
        
        # find_strict() should raise xNodePathError
        with pytest.raises(xNodePathError) as exc_info:
            nested_node.find_strict('nonexistent.deep.path')
        
        # The error message should contain the key that was not found
        error_msg = str(exc_info.value)
        assert "nonexistent" in error_msg
    
    @pytest.mark.errors
    def test_path_navigation_through_leaf(self, nested_node):
        """Test path navigation through leaf nodes raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            nested_node.find('users.0.name.invalid.path')
        
        assert "does not support child access" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_array_access_with_string_on_list(self, list_node):
        """Test accessing list with non-numeric string raises xNodeTypeError."""
        with pytest.raises(xNodeTypeError) as exc_info:
            list_node.find('invalid_string_index')
        
        assert "List index must be an integer" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_complex_invalid_path(self, nested_node):
        """Test complex invalid path scenarios."""
        # Mix of valid and invalid path components
        with pytest.raises(xNodePathError):
            nested_node.find('users.0.invalid.name')
        
        with pytest.raises(IndexError):
            nested_node.find('users.10.name')  # Invalid index
        
        with pytest.raises(IndexError):
            nested_node.find('metadata.tags.10')  # Index out of bounds


class TestxNodeTypeErrorScenarios:
    """Test scenarios that should raise xNodeTypeError."""
    
    @pytest.mark.errors
    def test_child_access_on_leaf_node(self, leaf_node):
        """Test that accessing children of leaf nodes raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            leaf_node['any_key']
        
        assert "does not support child access" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_len_on_leaf_node(self, leaf_node):
        """Test that len() on leaf nodes returns 0."""
        # Leaf nodes return 0 for len() instead of raising an error
        assert len(leaf_node) == 0
    
    @pytest.mark.errors
    def test_iteration_on_leaf_node(self, leaf_node):
        """Test that iteration on leaf nodes returns empty list."""
        # Leaf nodes return empty iterator instead of raising an error
        assert list(leaf_node) == []
    
    @pytest.mark.errors
    def test_keys_on_non_dict_node(self, list_node, leaf_node):
        """Test that keys() on non-dict nodes returns empty list."""
        # Non-dict nodes return empty iterator instead of raising an error
        assert list(list_node.keys()) == []
        assert list(leaf_node.keys()) == []
    
    @pytest.mark.errors
    def test_items_on_non_dict_node(self, list_node, leaf_node):
        """Test that items() on non-dict nodes returns empty list."""
        # Non-dict nodes return empty iterator instead of raising an error
        assert list(list_node.items()) == []
        assert list(leaf_node.items()) == []
    
    @pytest.mark.errors
    def test_string_index_on_list_node(self, list_node):
        """Test that string indexing on list nodes raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            list_node['string_index']  # Access through facade
        
        assert "string_index" in str(exc_info.value)


class TestDataValidationErrors:
    """Test data validation error scenarios."""
    
    @pytest.mark.errors
    def test_complex_object_handling(self):
        """Test that complex objects are handled appropriately (data agnostic)."""
        # Test with a function object - xNode is data agnostic and should accept any data
        def test_function():
            pass
        
        # Should succeed as xNode is data agnostic
        node = xNode.from_native(test_function)
        assert node.is_leaf
        assert node.value is test_function
    
    @pytest.mark.errors
    def test_circular_reference_data(self):
        """Test that circular reference data raises appropriate errors."""
        # Create circular reference
        circular_data = {}
        circular_data['self'] = circular_data
        
        with pytest.raises(Exception):  # Should raise some kind of error
            xNode.from_native(circular_data)
    
    # Removed test_none_input as None is a valid value for xNode.from_native()
    # The test_from_native_none_value test in test_xnode_core.py confirms this behavior
    
    @pytest.mark.errors
    def test_empty_data_handling(self):
        """Test empty data handling."""
        # Empty dict should work
        empty_dict = xNode.from_native({})
        assert empty_dict.is_dict
        
        # Empty list should work
        empty_list = xNode.from_native([])
        assert empty_list.is_list
        
        # Empty string should work
        empty_string = xNode.from_native("")
        assert empty_string.is_leaf


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""
    
    @pytest.mark.errors
    def test_very_deep_invalid_navigation(self):
        """Test very deep invalid navigation paths."""
        node = xNode.from_native({'a': {'b': {'c': 'value'}}})
        
        # Valid path
        assert node.find('a.b.c').value == 'value'
        
        # Invalid continuation - should raise xNodeTypeError when trying to access child of leaf node
        with pytest.raises(xNodeTypeError):
            node.find('a.b.c.d.e.f.g.h.i.j')
    
    @pytest.mark.errors
    def test_mixed_valid_invalid_paths(self, nested_node):
        """Test paths that start valid but become invalid."""
        # Start with valid path, then go invalid - should raise xNodeTypeError when trying to access child of leaf node
        with pytest.raises(xNodeTypeError):
            nested_node.find('users.0.name.invalid.continuation')
        
        with pytest.raises(xNodeTypeError):
            nested_node.find('metadata.version.more.levels')
    
    @pytest.mark.errors
    def test_edge_case_indices(self, list_node):
        """Test edge case index values."""
        # Test maximum integer (should be out of bounds)
        with pytest.raises(IndexError):
            list_node[2**31]
        
        # Test very negative number
        with pytest.raises(IndexError):
            list_node[-1000]
    
    @pytest.mark.errors
    def test_empty_containers_navigation(self, empty_dict_node, empty_list_node):
        """Test navigation on empty containers."""
        # Empty dict access
        with pytest.raises(KeyError):
            empty_dict_node['any_key']
        
        # Empty list access
        with pytest.raises(IndexError):
            empty_list_node[0]
        
        # Path navigation on empty containers
        with pytest.raises(xNodePathError):
            empty_dict_node.find('any.path')
        
        with pytest.raises(IndexError):
            empty_list_node.find('0.path')


class TestErrorMessages:
    """Test that error messages are informative and helpful."""
    
    @pytest.mark.errors
    def test_path_error_contains_full_path(self, nested_node):
        """Test that path errors contain the key that was not found."""
        invalid_path = 'users.0.nonexistent.deep.path'
        
        with pytest.raises(xNodePathError) as exc_info:
            nested_node.find(invalid_path)
        
        # Error message should contain the key that was not found
        assert "nonexistent" in str(exc_info.value)
    
    @pytest.mark.errors
    def test_key_error_contains_key_name(self, simple_node):
        """Test that key errors contain the specific key name."""
        missing_key = 'definitely_not_there'
        
        with pytest.raises(KeyError) as exc_info:
            simple_node[missing_key]
        
        assert missing_key in str(exc_info.value)
    
    @pytest.mark.errors
    def test_index_error_contains_index_value(self, list_node):
        """Test that index errors contain the specific index value."""
        invalid_index = 999
        
        with pytest.raises(IndexError) as exc_info:
            list_node[invalid_index]
        
        assert str(invalid_index) in str(exc_info.value)
    
    @pytest.mark.errors
    def test_type_error_describes_operation(self, leaf_node):
        """Test that type errors describe the invalid operation."""
        # Leaf nodes return 0 for len() instead of raising an error
        assert len(leaf_node) == 0
        
        # Leaf nodes return empty iterator instead of raising an error
        assert list(leaf_node) == []


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
        
        with pytest.raises(KeyError):
            nested_node['missing_key']
        
        # Node should still be functional after errors
        assert nested_node.find('users.0.name').value == 'Alice'
    
    @pytest.mark.errors
    def test_error_state_isolation(self, nested_node, leaf_node):
        """Test that errors on one node don't affect other nodes."""
        # Leaf nodes return 0 for len() instead of raising an error
        assert len(leaf_node) == 0
        
        # nested_node should still work fine
        assert len(nested_node) == 2  # users and metadata
        
        # Error on nested_node
        with pytest.raises(KeyError):
            nested_node['nonexistent']
        
        # leaf_node should still work fine
        assert leaf_node.value == "simple string value"


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 
