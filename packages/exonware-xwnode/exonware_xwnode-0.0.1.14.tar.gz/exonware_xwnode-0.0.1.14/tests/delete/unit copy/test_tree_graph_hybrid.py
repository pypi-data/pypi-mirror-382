#!/usr/bin/env python3
"""
Test for the unified Tree Graph Hybrid Strategy.

This test verifies that the new unified strategy works correctly
and maintains all the functionality of the original aNode model.
"""

import pytest
from src.xlib.xnode.strategies.impls.node_tree_graph_hybrid import TreeGraphHybridStrategy
from src.xlib.xnode.strategies.types import NodeMode, NodeTrait


class TestTreeGraphHybridStrategy:
    """Test the unified tree graph hybrid strategy."""
    
    def test_strategy_initialization(self):
        """Test that the strategy initializes correctly."""
        strategy = TreeGraphHybridStrategy()
        assert strategy.mode == NodeMode.TREE_GRAPH_HYBRID
        assert strategy.traits == NodeTrait.NONE
    
    def test_create_from_simple_data(self):
        """Test creating strategy from simple data."""
        data = {"name": "John", "age": 30}
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(data)
        
        assert strategy.get("name") == "John"
        assert strategy.get("age") == 30
        assert strategy.has("name") is True
        assert strategy.has("nonexistent") is False
    
    def test_create_from_nested_data(self):
        """Test creating strategy from nested data."""
        data = {
            "user": {
                "profile": {
                    "name": "John",
                    "age": 30
                },
                "settings": {
                    "theme": "dark"
                }
            }
        }
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(data)
        
        assert strategy.get("user.profile.name") == "John"
        assert strategy.get("user.profile.age") == 30
        assert strategy.get("user.settings.theme") == "dark"
    
    def test_create_from_list_data(self):
        """Test creating strategy from list data."""
        data = ["apple", "banana", "cherry"]
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(data)
        
        assert strategy.get("0") == "apple"
        assert strategy.get("1") == "banana"
        assert strategy.get("2") == "cherry"
        assert len(strategy) == 3
    
    def test_put_and_get_operations(self):
        """Test put and get operations."""
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data({})
        
        # Test direct key assignment
        strategy.put("name", "John")
        strategy.put("age", 30)
        
        assert strategy.get("name") == "John"
        assert strategy.get("age") == 30
        
        # Test nested path assignment
        strategy.put("user.profile.name", "Jane")
        strategy.put("user.profile.age", 25)
        
        assert strategy.get("user.profile.name") == "Jane"
        assert strategy.get("user.profile.age") == 25
    
    def test_keys_values_items(self):
        """Test keys, values, and items methods."""
        data = {"a": 1, "b": 2, "c": 3}
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(data)
        
        keys = list(strategy.keys())
        values = list(strategy.values())
        items = list(strategy.items())
        
        assert set(keys) == {"a", "b", "c"}
        assert set(values) == {1, 2, 3}
        assert set(items) == {("a", 1), ("b", 2), ("c", 3)}
    
    def test_to_native_conversion(self):
        """Test conversion back to native Python objects."""
        original_data = {
            "user": {
                "name": "John",
                "hobbies": ["reading", "gaming"]
            }
        }
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(original_data)
        
        converted_data = strategy.to_native()
        assert converted_data == original_data
    
    def test_supported_traits(self):
        """Test that the strategy supports the correct traits."""
        strategy = TreeGraphHybridStrategy()
        supported = strategy.get_supported_traits()
        
        assert NodeTrait.ORDERED in supported
        assert NodeTrait.HIERARCHICAL in supported
        assert NodeTrait.INDEXED in supported
    
    def test_backend_info(self):
        """Test that backend info is provided correctly."""
        strategy = TreeGraphHybridStrategy()
        info = strategy.backend_info()
        
        assert info["strategy"] == "TREE_GRAPH_HYBRID"
        assert info["backend"] == "aNode tree with lazy loading and advanced data structures"
        assert "lazy_loading" in info["features"]
        assert "tree_navigation" in info["features"]
    
    def test_metrics(self):
        """Test that metrics are tracked correctly."""
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data({"a": 1, "b": 2})
        
        # Access some data to generate metrics
        strategy.get("a")
        strategy.get("b")
        strategy.get("nonexistent")
        
        metrics = strategy.metrics()
        assert metrics["size"] == 2
        assert metrics["access_count"] >= 3
        assert metrics["has_root"] is True
    
    def test_large_data_handling(self):
        """Test that the strategy can handle large datasets efficiently."""
        # Create a large dataset
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(large_data)
        
        # Test access to various keys
        assert strategy.get("key_0") == "value_0"
        assert strategy.get("key_500") == "value_500"
        assert strategy.get("key_999") == "value_999"
        assert len(strategy) == 1000
    
    def test_circular_reference_handling(self):
        """Test that circular references are handled gracefully."""
        # Create a circular reference
        data = {"a": 1}
        data["self"] = data  # Circular reference
        
        strategy = TreeGraphHybridStrategy()
        strategy.create_from_data(data)
        
        # Should not crash and should handle the circular reference
        assert strategy.get("a") == 1
        # The circular reference should be handled by the factory


if __name__ == "__main__":
    pytest.main([__file__])
