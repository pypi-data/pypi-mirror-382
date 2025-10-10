"""
xNode Core Functionality Tests
==============================

Comprehensive unit tests for core xNode functionality including:
- Factory methods (from_native)
- Property access and type checking
- Container operations (iteration, length, keys, items)
- Bracket notation access
- String representations
- Error conditions
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add src to Python path for direct imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Dynamic import handling for different test environments
try:
    from conftest import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
except ImportError:
    try:
        from src.xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
    except ImportError:
        from xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError


class TestxNodeFactoryMethods:
    """Test xNode factory methods for creating nodes from different sources."""
    
    @pytest.mark.core
    def test_from_native_dict(self, simple_dict_data):
        """Test creating xNode from Python dictionary."""
        node = xNode.from_native(simple_dict_data)
        
        assert node.is_dict
        assert not node.is_list
        assert not node.is_leaf
        assert node['name'].value == 'Alice'
        assert node['age'].value == 30
        assert node['active'].value is True

    @pytest.mark.core
    def test_from_native_list(self, simple_list_data):
        """Test creating xNode from Python list."""
        node = xNode.from_native(simple_list_data)
        
        assert node.is_list
        assert not node.is_dict
        assert not node.is_leaf
        assert node[0].value == 'apple'
        assert node[1].value == 'banana'
        assert node[2].value == 'cherry'

    @pytest.mark.core
    def test_from_native_string_primitive(self):
        """Test creating xNode from string primitive."""
        test_value = "hello world"
        node = xNode.from_native(test_value)
        
        assert node.is_leaf
        assert not node.is_dict
        assert not node.is_list
        assert node.value == test_value

    @pytest.mark.core
    def test_from_native_number_primitive(self):
        """Test creating xNode from number primitive."""
        test_value = 42
        node = xNode.from_native(test_value)
        
        assert node.is_leaf
        assert node.value == test_value

    @pytest.mark.core
    def test_from_native_boolean_primitive(self):
        """Test creating xNode from boolean primitive."""
        test_value = True
        node = xNode.from_native(test_value)
        
        assert node.is_leaf
        assert node.value is True

    @pytest.mark.core
    def test_from_native_none_value(self):
        """Test creating xNode from None value."""
        node = xNode.from_native(None)
        
        assert node.is_leaf
        assert node.value is None

    @pytest.mark.core
    def test_from_native_nested_structure(self, nested_data):
        """Test creating xNode from complex nested structure."""
        node = xNode.from_native(nested_data)
        
        assert node.is_dict
        assert node['users'].is_list
        assert node['users'][0].is_dict
        assert node['users'][0]['name'].value == 'Alice'
        assert node['metadata']['version'].value == 1.0




class TestxNodeProperties:
    """Test xNode properties and type checking methods."""
    
    @pytest.mark.core
    def test_is_leaf_property(self, leaf_node):
        """Test is_leaf property for leaf nodes."""
        assert leaf_node.is_leaf is True
        assert leaf_node.is_list is False
        assert leaf_node.is_dict is False
    
    @pytest.mark.core
    def test_is_list_property(self, list_node):
        """Test is_list property for list nodes."""
        assert list_node.is_list is True
        assert list_node.is_leaf is False
        assert list_node.is_dict is False
    
    @pytest.mark.core
    def test_is_dict_property(self, simple_node):
        """Test is_dict property for dict nodes."""
        assert simple_node.is_dict is True
        assert simple_node.is_leaf is False
        assert simple_node.is_list is False
    
    @pytest.mark.core
    def test_type_property_leaf(self, leaf_node):
        """Test type property for leaf nodes."""
        assert leaf_node.type == 'value'
    
    @pytest.mark.core
    def test_type_property_list(self, list_node):
        """Test type property for list nodes."""
        assert list_node.type == 'list'
    
    @pytest.mark.core
    def test_type_property_dict(self, simple_node):
        """Test type property for dict nodes."""
        assert simple_node.type == 'dict'
    
    @pytest.mark.core
    def test_value_property_preserves_data(self, mixed_type_data):
        """Test that value property works correctly for container vs leaf nodes."""
        node = xNode.from_native(mixed_type_data)
        
        # Container nodes (dict/list) have value=None, access data via to_native()
        assert node.value is None  # Dict node has no direct value
        
        # Access the actual data via to_native()
        data = node.to_native()
        assert data == mixed_type_data
        assert data['string'] == 'hello'
        assert data['integer'] == 42
        assert data['float'] == 3.14
        assert data['boolean'] is True
        assert data['null'] is None
        assert data['list'] == [1, 2, 3]
        assert data['dict'] == {'nested': 'value'}
        
        # Leaf nodes have direct values
        string_node = node['string']
        assert string_node.value == 'hello'


class TestxNodeContainerOperations:
    """Test container operations for dict and list nodes."""
    
    @pytest.mark.core
    def test_len_dict_node(self, simple_node):
        """Test len() operation on dict nodes."""
        assert len(simple_node) == 3  # name, age, active
    
    @pytest.mark.core
    def test_len_list_node(self, list_node):
        """Test len() operation on list nodes."""
        assert len(list_node) == 3  # 'apple', 'banana', 'cherry'
    
    @pytest.mark.core
    def test_len_leaf_node_returns_zero(self, leaf_node):
        """Test that len() on leaf nodes returns 0."""
        assert len(leaf_node) == 0
    
    @pytest.mark.core
    def test_iter_dict_node(self, simple_node):
        """Test iteration over dict node values."""
        values = list(simple_node)
        assert len(values) == 3
        
        # All items should be xNode instances
        for value in values:
            assert isinstance(value, xNode)
    
    @pytest.mark.core
    def test_iter_list_node(self, list_node):
        """Test iteration over list node elements."""
        elements = list(list_node)
        assert len(elements) == 3
        
        # All items should be xNode instances
        for element in elements:
            assert isinstance(element, xNode)
        
        # Check actual values
        assert elements[0].value == 'apple'
        assert elements[1].value == 'banana'
        assert elements[2].value == 'cherry'
    
    @pytest.mark.core
    def test_iter_leaf_node_returns_empty(self, leaf_node):
        """Test that iteration on leaf nodes returns empty list."""
        assert list(leaf_node) == []
    
    @pytest.mark.core
    def test_keys_dict_node(self, simple_node):
        """Test keys() method on dict nodes."""
        keys = list(simple_node.keys())
        expected_keys = ['name', 'age', 'active']
        
        assert len(keys) == 3
        for key in expected_keys:
            assert key in keys
    
    @pytest.mark.core
    def test_keys_list_node_returns_empty(self, list_node):
        """Test that keys() on list nodes returns empty iterator."""
        assert list(list_node.keys()) == []
    
    @pytest.mark.core
    def test_keys_leaf_node_returns_empty(self, leaf_node):
        """Test that keys() on leaf nodes returns empty iterator."""
        assert list(leaf_node.keys()) == []
    
    @pytest.mark.core
    def test_items_dict_node(self, simple_node):
        """Test items() method on dict nodes."""
        items = list(simple_node.items())
        assert len(items) == 3
        
        # Check structure: each item should be (key, xNode)
        for key, node in items:
            assert isinstance(key, str)
            assert isinstance(node, xNode)
        
        # Check specific items
        items_dict = dict(items)
        assert 'name' in items_dict
        assert 'age' in items_dict
        assert 'active' in items_dict
        assert items_dict['name'].value == 'Alice'
        assert items_dict['age'].value == 30
        assert items_dict['active'].value is True
    
    @pytest.mark.core
    def test_items_list_node_returns_empty(self, list_node):
        """Test that items() on list nodes returns empty iterator."""
        assert list(list_node.items()) == []


class TestxNodeBracketAccess:
    """Test bracket notation access for container nodes."""
    
    @pytest.mark.core
    def test_getitem_dict_string_key(self, simple_node):
        """Test bracket access with string key on dict node."""
        name_node = simple_node['name']
        
        assert isinstance(name_node, xNode)
        assert name_node.is_leaf
        assert name_node.value == 'Alice'
    
    @pytest.mark.core
    def test_getitem_list_integer_index(self, list_node):
        """Test bracket access with integer index on list node."""
        first_element = list_node[0]
        
        assert isinstance(first_element, xNode)
        assert first_element.is_leaf
        assert first_element.value == 'apple'
    
    @pytest.mark.core
    def test_getitem_dict_nonexistent_key_raises_error(self, simple_node):
        """Test that accessing nonexistent key raises appropriate error."""
        with pytest.raises(KeyError):
            simple_node['nonexistent']
    
    @pytest.mark.core
    def test_getitem_list_out_of_bounds_raises_error(self, list_node):
        """Test that accessing out-of-bounds index raises appropriate error."""
        with pytest.raises(KeyError):
            list_node[10]
    
    @pytest.mark.core
    def test_getitem_leaf_node_raises_error(self, leaf_node):
        """Test that bracket access on leaf nodes raises appropriate error."""
        with pytest.raises(KeyError):
            leaf_node['key']


class TestxNodeConversions:
    """Test xNode conversion methods."""
    
    @pytest.mark.core
    def test_to_native_dict_node(self, simple_dict_data):
        """Test to_native() method on dict node."""
        node = xNode.from_native(simple_dict_data)
        result = node.to_native()
        
        assert result == simple_dict_data
        assert isinstance(result, dict)
    
    @pytest.mark.core
    def test_to_native_list_node(self, simple_list_data):
        """Test to_native() method on list node."""
        node = xNode.from_native(simple_list_data)
        result = node.to_native()
        
        assert result == simple_list_data
        assert isinstance(result, list)
    
    @pytest.mark.core
    def test_to_native_leaf_node(self, leaf_node):
        """Test to_native() method on leaf node."""
        result = leaf_node.to_native()
        
        assert result == "simple string value"
        assert isinstance(result, str)
    



class TestxNodeStringRepresentations:
    """Test xNode string representation methods."""
    
    @pytest.mark.core
    def test_repr_leaf_node(self, leaf_node):
        """Test __repr__ for leaf nodes."""
        repr_str = repr(leaf_node)
        assert repr_str.startswith('xNode(type=value')
        assert 'simple string value' in repr_str
    
    @pytest.mark.core
    def test_repr_dict_node(self, simple_node):
        """Test __repr__ for dict nodes."""
        repr_str = repr(simple_node)
        assert repr_str.startswith('xNode(type=dict')
        assert '3 items' in repr_str
    
    @pytest.mark.core
    def test_repr_list_node(self, list_node):
        """Test __repr__ for list nodes."""
        repr_str = repr(list_node)
        assert repr_str.startswith('xNode(type=list')
        assert '3 items' in repr_str
    
    @pytest.mark.core
    def test_str_representation(self, simple_node):
        """Test __str__ method - uses visualize format."""
        str_repr = str(simple_node)
        assert 'name:' in str_repr or 'Alice' in str_repr  # Should contain the data in some format
    
    @pytest.mark.core
    def test_repr_long_value_truncation(self):
        """Test that very long values are not truncated in repr."""
        long_string = 'x' * 100
        node = xNode.from_native(long_string)
        repr_str = repr(node)
        assert '...' not in repr_str


class TestxNodeEmptyContainers:
    """Test xNode behavior with empty containers."""
    
    @pytest.mark.core
    def test_empty_dict_node(self, empty_dict_node):
        """Test empty dictionary node behavior."""
        assert empty_dict_node.is_dict
        assert len(empty_dict_node) == 0
        assert list(empty_dict_node.keys()) == []
        assert list(empty_dict_node.items()) == []
        assert list(empty_dict_node) == []
    
    @pytest.mark.core
    def test_empty_list_node(self, empty_list_node):
        """Test empty list node behavior."""
        assert empty_list_node.is_list
        assert len(empty_list_node) == 0
        assert list(empty_list_node) == []


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 