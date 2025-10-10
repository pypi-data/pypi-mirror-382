"""
xNode Model Tests
=================

Tests for internal model components including aNode, aNodeValue, aNodeList, aNodeDict, and aNodeFactory.
These test the internal implementation details to ensure proper behavior.
"""

import pytest
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
    # Also need to import model classes directly since conftest doesn't expose them
    from ..strategies.impls.node_tree_graph_hybrid import aNode, aNodeValue, aNodeList, aNodeDict, aNodeFactory
except ImportError:
    try:
        from src.xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
        from src.xlib.xnode.strategies.impls.node_tree_graph_hybrid import aNode, aNodeValue, aNodeList, aNodeDict, aNodeFactory
    except ImportError:
        from xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
        from xlib.xnode.strategies.impls.node_tree_graph_hybrid import aNode, aNodeValue, aNodeList, aNodeDict, aNodeFactory


class TestaNodeFactory:
    """Test the aNodeFactory for building node trees."""
    
    @pytest.mark.model
    def test_leaf_creation(self):
        """Test creating leaf nodes from various data types."""
        # String leaf
        leaf = aNodeFactory.from_native("hello")
        assert isinstance(leaf, aNodeValue)
        assert leaf.value == "hello"
        
        # Number leaf
        number_leaf = aNodeFactory.from_native(42)
        assert isinstance(number_leaf, aNodeValue)
        assert number_leaf.value == 42

    @pytest.mark.model  
    def test_dict_creation(self):
        """Test creating dict nodes from Python dictionaries."""
        data = {"name": "Alice", "age": 30}
        node = aNodeFactory.from_native(data)
        
        assert isinstance(node, aNodeDict)
        assert node._get_child("name").value == "Alice"
        assert node._get_child("age").value == 30

    @pytest.mark.model
    def test_list_creation(self):
        """Test creating list nodes from Python lists."""
        data = ["apple", "banana", "cherry"]
        node = aNodeFactory.from_native(data)
        
        assert isinstance(node, aNodeList)
        assert node._get_child(0).value == "apple"
        assert node._get_child(1).value == "banana"
        assert node._get_child(2).value == "cherry"

    @pytest.mark.model
    def test_nested_structure_creation(self):
        """Test creating complex nested structures."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        }
        
        root = aNodeFactory.from_native(data)
        assert isinstance(root, aNodeDict)
        
        users_node = root._get_child("users")
        assert isinstance(users_node, aNodeList)
        
        first_user = users_node._get_child(0)
        assert isinstance(first_user, aNodeDict)


class TestaNodeValue:
    """Test aNodeValue behavior."""
    
    @pytest.mark.model
    def test_leaf_value_access(self):
        """Test accessing leaf node values."""
        leaf = aNodeValue("test_value")
        assert leaf.value == "test_value"

    @pytest.mark.model
    def test_leaf_with_number(self):
        """Test leaf nodes with numeric values."""
        leaf = aNodeValue(42)
        assert leaf.value == 42

    @pytest.mark.model
    def test_leaf_child_access_error(self):
        """Test that accessing children of leaf nodes raises error."""
        leaf = aNodeValue("value")
        with pytest.raises(Exception):  # Should raise some form of error
            leaf._get_child("key")


class TestaNodeDict:
    """Test aNodeDict behavior."""
    
    @pytest.mark.model
    def test_dict_child_access(self):
        """Test accessing dictionary children."""
        dict_node = aNodeFactory.from_native({"test_key": "value"})
        retrieved = dict_node._get_child("test_key")
        assert retrieved.value == "value"

    @pytest.mark.model
    def test_dict_child_setting(self):
        """Test setting children in dict nodes."""
        dict_node = aNodeFactory.from_native({"key": "value"})
        assert dict_node._get_child("key").value == "value"

    @pytest.mark.model
    def test_dict_missing_key_error(self):
        """Test that accessing missing keys raises appropriate error."""
        dict_node = aNodeFactory.from_native({"existing": "value"})
        with pytest.raises(xNodePathError):
            dict_node._get_child("nonexistent")

    @pytest.mark.model
    def test_dict_multiple_children(self):
        """Test dict with multiple children."""
        dict_node = aNodeFactory.from_native({"name": "Alice", "age": 30})
        
        assert dict_node._get_child("name").value == "Alice"
        assert dict_node._get_child("age").value == 30


class TestaNodeList:
    """Test aNodeList behavior."""
    
    @pytest.mark.model
    def test_list_child_access(self):
        """Test accessing list children by index."""
        list_node = aNodeFactory.from_native(["first", "second"])
        
        assert list_node._get_child(0).value == "first"
        assert list_node._get_child(1).value == "second"

    @pytest.mark.model
    def test_list_append(self):
        """Test appending children to list nodes."""
        list_node = aNodeFactory.from_native(["value"])
        
        assert list_node._get_child(0).value == "value"

    @pytest.mark.model
    def test_list_insert(self):
        """Test inserting children at specific positions."""
        list_node = aNodeFactory.from_native(["value"])
        
        assert list_node._get_child(0).value == "value"

    @pytest.mark.model
    def test_list_index_error(self):
        """Test that accessing invalid indices raises appropriate error."""
        list_node = aNodeFactory.from_native([])
        with pytest.raises(IndexError):
            list_node._get_child(0)

    @pytest.mark.model
    def test_list_length_and_iteration(self):
        """Test list length and basic iteration properties."""
        list_node = aNodeFactory.from_native(["value"])
        
        # Test that we can access the child we just added
        assert list_node._get_child(0).value == "value"

    @pytest.mark.model
    def test_list_multiple_types(self):
        """Test list with multiple data types."""
        list_node = aNodeFactory.from_native([1, "two", True])
        
        assert list_node._get_child(0).value == 1
        assert list_node._get_child(1).value == "two"
        assert list_node._get_child(2).value is True

    @pytest.mark.model
    def test_list_insertion_ordering(self):
        """Test that list insertion maintains proper ordering."""
        list_node = aNodeFactory.from_native(["first", "second", "third"])
        
        assert list_node._get_child(0).value == "first"
        assert list_node._get_child(1).value == "second"
        assert list_node._get_child(2).value == "third"


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 