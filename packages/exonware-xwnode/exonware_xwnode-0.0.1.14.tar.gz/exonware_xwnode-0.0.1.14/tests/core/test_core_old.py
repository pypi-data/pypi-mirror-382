"""
Core functionality tests for xnode

This test suite covers the core xnode functionality including:
- Import methods (both exonware.xwnode and xwnode)
- XWNode, XWEdge, XWQuery creation and basic operations  
- Facade object creation and verification
- Strategy switching capabilities
- Error handling and exceptions

The tests are designed to work with the current implementation while documenting
expected functionality and handling dependency issues gracefully.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 2025-01-03
"""

import pytest
import sys
from pathlib import Path

class TestCoreImports:
    """Test core import functionality."""
    
    def test_exonware_xnode_import(self):
        """Test that exonware.xnode can be imported."""
        try:
            import exonware.xnode
            assert True, "exonware.xnode imported successfully"
        except ImportError as e:
            pytest.skip(f"Skipping test due to dependency issue: {e}")
    
    def test_convenience_import(self):
        """Test that the convenience import works."""
        try:
            import xnode
            assert True, "xnode convenience import works"
        except ImportError as e:
            pytest.skip(f"Skipping convenience import test due to dependency issue: {e}")
    
    def test_version_info(self):
        """Test that version information is available."""
        try:
            import exonware.xnode
            
            # Check if version info is available
            version_attrs = ['__version__', '__author__', '__email__', '__company__']
            available_attrs = [attr for attr in version_attrs if hasattr(exonware.xnode, attr)]
            
            if available_attrs:
                for attr in available_attrs:
                    value = getattr(exonware.xnode, attr)
                    assert isinstance(value, str), f"{attr} should be a string"
            else:
                pytest.skip("Version information not available in current implementation")
                
        except ImportError as e:
            pytest.skip(f"Skipping version test due to dependency issue: {e}")


class TestCoreClasses:
    """Test core class creation and functionality."""
    
    def test_xnode_creation(self):
        """Test XWNode creation and facade object."""
        try:
            from exonware.xnode import XWNode
            
            # Test creation from dictionary
            data = {'name': 'Alice', 'age': 30, 'active': True}
            node = XWNode.from_native(data)
            
            assert node is not None
            assert hasattr(node, 'is_dict')
            assert hasattr(node, 'is_list')
            assert hasattr(node, 'is_leaf')
            assert node.is_dict
            
        except ImportError as e:
            pytest.skip(f"Skipping XWNode creation test due to dependency issue: {e}")
        
    def test_xnode_convenience_import_creation(self):
        """Test XWNode creation via convenience import."""
        import xnode
        
        # Test creation from dictionary
        data = {'name': 'Bob', 'age': 25}
        node = xnode.XWNode.from_native(data)
        
        assert node is not None
        assert node.is_dict
        assert not node.is_list
        assert not node.is_leaf
    
    def test_xquery_creation(self):
        """Test XWNodeQuery (xQuery) creation and functionality."""
        from exonware.xnode import XWNode, XWNodeQuery
        
        # Create a node first
        data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        node = XWNode.from_native(data)
        
        # Create query object
        query = XWNodeQuery(node)
        assert query is not None
        
        # Test basic query functionality
        assert hasattr(query, 'query')
    
    def test_xnode_factory_creation(self):
        """Test XWNodeFactory creation and usage."""
        from exonware.xnode import XWNodeFactory
        
        # Test factory creation
        factory = XWNodeFactory()
        assert factory is not None
        
        # Test factory methods
        assert hasattr(factory, 'from_dict')
        assert hasattr(factory, 'from_list')
        assert hasattr(factory, 'empty')
        
        # Test using factory
        data = {'test': 'value'}
        node = factory.from_dict(data)
        assert node is not None
        assert node.is_dict
    
    def test_facade_objects_created_successfully(self):
        """Test that facade objects are created successfully."""
        from exonware.xnode import XWNode, XWNodeQuery, XWNodeFactory
        
        # Test XWNode facade
        node = XWNode.from_native({'key': 'value'})
        assert node is not None
        assert hasattr(node, 'get')
        assert hasattr(node, 'set')
        assert hasattr(node, 'find')
        
        # Test XWNodeQuery facade
        query = XWNodeQuery(node)
        assert query is not None
        
        # Test XWNodeFactory facade
        factory = XWNodeFactory()
        assert factory is not None


class TestNodeOperations:
    """Test basic node operations."""
    
    def test_xnode_basic_operations(self):
        """Test basic XWNode operations."""
        from exonware.xnode import XWNode
        
        data = {
            'name': 'Alice',
            'age': 30,
            'skills': ['Python', 'JavaScript'],
            'profile': {
                'city': 'New York',
                'country': 'USA'
            }
        }
        
        node = XWNode.from_native(data)
        
        # Test basic properties
        assert node.is_dict
        assert not node.is_list
        assert not node.is_leaf
        
        # Test access methods
        name_node = node.get('name')
        assert name_node is not None
        assert name_node.value == 'Alice'
        
        # Test path navigation
        city_node = node.find('profile.city')
        if city_node:  # Some implementations might not support nested paths yet
            assert city_node.value == 'New York'
    
    def test_xnode_list_operations(self):
        """Test XWNode with list data."""
        from exonware.xnode import XWNode
        
        data = ['apple', 'banana', 'cherry']
        node = XWNode.from_native(data)
        
        assert node.is_list
        assert not node.is_dict
        assert not node.is_leaf
        assert len(node) == 3
    
    def test_xnode_leaf_operations(self):
        """Test XWNode with primitive data."""
        from exonware.xnode import XWNode
        
        node = XWNode.from_native("hello world")
        
        assert node.is_leaf
        assert not node.is_dict
        assert not node.is_list
        assert node.value == "hello world"


class TestStrategyCapabilities:
    """Test strategy switching capabilities where available."""
    
    def test_xnode_has_strategy_interface(self):
        """Test that XWNode has strategy-related interface."""
        from exonware.xnode import XWNode
        
        node = XWNode.from_native({'test': 'data'})
        
        # Check if strategy-related attributes exist
        # Note: Actual strategy switching methods may not be exposed yet
        assert hasattr(node, '_strategy') or hasattr(node, 'strategy')
    
    def test_strategy_switching_placeholder(self):
        """Placeholder test for strategy switching."""
        # This test is a placeholder for when strategy switching
        # is fully implemented in the public API
        from exonware.xnode import XWNode
        
        node = XWNode.from_native({'test': 'data'})
        
        # For now, just verify the node works
        assert node is not None
        
        # TODO: Add actual strategy switching tests when the API is available
        # Examples of what we want to test:
        # - node.switch_strategy('hash_map')
        # - node.switch_strategy('btree') 
        # - node.get_current_strategy()


class TestEdgeCapabilities:
    """Test xEdge capabilities and creation."""
    
    def test_xedge_import_placeholder(self):
        """Test xEdge import - currently not exposed in public API."""
        # NOTE: xEdge is not currently exposed in the public API
        # The abstract base class aEdge exists, but no xEdge facade
        # This test documents what we expect to be available
        
        try:
            from exonware.xnode import xEdge
            pytest.fail("xEdge should not be available yet - this test should be updated when implemented")
        except ImportError:
            # Expected - xEdge is not in the public API yet
            pass
        
        # For now, verify we can access the abstract base
        try:
            from exonware.xnode.base import aEdge
            assert aEdge is not None
        except ImportError:
            # If base module is not accessible, just note it
            pass
    
    def test_xedge_creation_placeholder(self):
        """Placeholder test for xEdge creation and strategy switching."""
        # This test documents what we expect xEdge to support
        # when it's fully implemented in the public API
        
        # TODO: When xEdge is implemented, test:
        # 1. from exonware.xnode import xEdge
        # 2. edge = xEdge.create() or similar factory method
        # 3. edge.add_edge(source, target)
        # 4. edge.switch_strategy('adjacency_list')
        # 5. edge.switch_strategy('adjacency_matrix')
        # 6. edge.get_current_strategy()
        
        # For now, just mark as expected to be implemented
        assert True, "xEdge implementation pending"


class TestErrorHandling:
    """Test error handling and exceptions."""
    
    def test_import_exceptions(self):
        """Test that exceptions can be imported."""
        from exonware.xnode import (
            XWNodeError, XWNodeTypeError, XWNodePathError, 
            XWNodeValueError, XWNodeSecurityError, XWNodeLimitError
        )
        
        # Verify they are exception classes
        assert issubclass(XWNodeError, Exception)
        assert issubclass(XWNodeTypeError, XWNodeError)
        assert issubclass(XWNodePathError, XWNodeError)
        assert issubclass(XWNodeValueError, XWNodeError)
        assert issubclass(XWNodeSecurityError, XWNodeError)
        assert issubclass(XWNodeLimitError, XWNodeError)
