#!/usr/bin/env python3
"""
Unit tests for advanced operations in TreeGraphHybridStrategy.

This module tests the new advanced data structure operations:
- Union-Find (disjoint sets)
- Trie (prefix tree)
- MinHeap (priority queue)
"""

import pytest
from src.xlib.xnode.strategies.impls.node_tree_graph_hybrid import TreeGraphHybridStrategy
from src.xlib.xnode.strategies.types import NodeTrait


class TestAdvancedOperations:
    """Test advanced data structure operations."""
    
    def test_union_find_basic_operations(self):
        """Test basic Union-Find operations."""
        strategy = TreeGraphHybridStrategy()
        
        # Test make_set
        strategy.union_find_make_set(1)
        strategy.union_find_make_set(2)
        strategy.union_find_make_set(3)
        
        assert strategy.union_find_size() == 3
        assert strategy.union_find_sets_count() == 3
        
        # Test find
        assert strategy.union_find_find(1) == 1
        assert strategy.union_find_find(2) == 2
        assert strategy.union_find_find(3) == 3
    
    def test_union_find_union_operations(self):
        """Test Union-Find union operations."""
        strategy = TreeGraphHybridStrategy()
        
        # Create sets
        strategy.union_find_make_set(1)
        strategy.union_find_make_set(2)
        strategy.union_find_make_set(3)
        strategy.union_find_make_set(4)
        
        # Test union
        strategy.union_find_union(1, 2)
        assert strategy.union_find_sets_count() == 3
        assert strategy.union_find_connected(1, 2) == True
        assert strategy.union_find_connected(1, 3) == False
        
        strategy.union_find_union(2, 3)
        assert strategy.union_find_sets_count() == 2
        assert strategy.union_find_connected(1, 3) == True
        assert strategy.union_find_connected(1, 4) == False
        
        strategy.union_find_union(1, 4)
        assert strategy.union_find_sets_count() == 1
        assert strategy.union_find_connected(1, 4) == True
        assert strategy.union_find_connected(2, 4) == True
    
    def test_union_find_error_handling(self):
        """Test Union-Find error handling."""
        strategy = TreeGraphHybridStrategy()
        
        # Test find on non-existent element
        with pytest.raises(ValueError):
            strategy.union_find_find(1)
        
        # Test connected on non-existent elements
        assert strategy.union_find_connected(1, 2) == False
    
    def test_trie_basic_operations(self):
        """Test basic Trie operations."""
        strategy = TreeGraphHybridStrategy()
        
        # Test insert and contains
        strategy.trie_insert("hello", "greeting")
        strategy.trie_insert("world", "planet")
        strategy.trie_insert("help", "assist")
        
        assert strategy.trie_contains("hello") == True
        assert strategy.trie_contains("world") == True
        assert strategy.trie_contains("help") == True
        assert strategy.trie_contains("missing") == False
    
    def test_trie_get_operations(self):
        """Test Trie get operations."""
        strategy = TreeGraphHybridStrategy()
        
        strategy.trie_insert("hello", "greeting")
        strategy.trie_insert("world", "planet")
        strategy.trie_insert("help", "assist")
        
        assert strategy.trie_get("hello") == "greeting"
        assert strategy.trie_get("world") == "planet"
        assert strategy.trie_get("help") == "assist"
        
        # Test get on non-existent word
        with pytest.raises(ValueError):
            strategy.trie_get("missing")
    
    def test_trie_prefix_search(self):
        """Test Trie prefix search operations."""
        strategy = TreeGraphHybridStrategy()
        
        strategy.trie_insert("hello", "greeting")
        strategy.trie_insert("world", "planet")
        strategy.trie_insert("help", "assist")
        strategy.trie_insert("hero", "protagonist")
        strategy.trie_insert("apple", "fruit")
        
        # Test prefix search
        words_with_he = strategy.trie_starts_with("he")
        assert "hello" in words_with_he
        assert "help" in words_with_he
        assert "hero" in words_with_he
        assert len(words_with_he) == 3
        
        words_with_hel = strategy.trie_starts_with("hel")
        assert "hello" in words_with_hel
        assert "help" in words_with_hel
        assert len(words_with_hel) == 2
        
        # Test non-existent prefix
        empty_result = strategy.trie_starts_with("xyz")
        assert len(empty_result) == 0
    
    def test_trie_error_handling(self):
        """Test Trie error handling."""
        strategy = TreeGraphHybridStrategy()
        
        # Test insert with non-string word
        with pytest.raises(ValueError):
            strategy.trie_insert(123, "value")
        
        # Test get with non-string word
        with pytest.raises(ValueError):
            strategy.trie_get(123)
    
    def test_heap_basic_operations(self):
        """Test basic MinHeap operations."""
        strategy = TreeGraphHybridStrategy()
        
        # Test push and size
        strategy.heap_push("task1", 3.0)
        strategy.heap_push("task2", 1.0)
        strategy.heap_push("task3", 2.0)
        
        assert strategy.heap_size() == 3
        assert strategy.heap_is_empty() == False
    
    def test_heap_pop_operations(self):
        """Test MinHeap pop operations."""
        strategy = TreeGraphHybridStrategy()
        
        strategy.heap_push("task1", 3.0)
        strategy.heap_push("task2", 1.0)
        strategy.heap_push("task3", 2.0)
        strategy.heap_push("task4", 0.5)
        
        # Test pop order (should be by priority)
        assert strategy.heap_pop_min() == "task4"  # priority 0.5
        assert strategy.heap_pop_min() == "task2"  # priority 1.0
        assert strategy.heap_pop_min() == "task3"  # priority 2.0
        assert strategy.heap_pop_min() == "task1"  # priority 3.0
        
        assert strategy.heap_is_empty() == True
    
    def test_heap_peek_operations(self):
        """Test MinHeap peek operations."""
        strategy = TreeGraphHybridStrategy()
        
        strategy.heap_push("task1", 3.0)
        strategy.heap_push("task2", 1.0)
        
        # Test peek without removing
        assert strategy.heap_peek_min() == "task2"  # priority 1.0
        assert strategy.heap_size() == 2  # Size unchanged
        
        # Pop and verify
        assert strategy.heap_pop_min() == "task2"
        assert strategy.heap_peek_min() == "task1"
    
    def test_heap_error_handling(self):
        """Test MinHeap error handling."""
        strategy = TreeGraphHybridStrategy()
        
        # Test pop on empty heap
        with pytest.raises(IndexError):
            strategy.heap_pop_min()
        
        # Test peek on empty heap
        with pytest.raises(IndexError):
            strategy.heap_peek_min()
    
    def test_advanced_traits_support(self):
        """Test that the strategy supports advanced traits."""
        strategy = TreeGraphHybridStrategy()
        traits = strategy.get_supported_traits()
        
        # Check that new traits are supported
        assert NodeTrait.GRAPH in traits
        assert NodeTrait.UNION_FIND in traits
        assert NodeTrait.PREFIX_TREE in traits
        assert NodeTrait.HEAP_OPERATIONS in traits
        assert NodeTrait.STATE_MACHINE in traits
        
        # Check that original traits are still supported
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.HIERARCHICAL in traits
        assert NodeTrait.INDEXED in traits
    
    def test_backend_info_advanced_features(self):
        """Test that backend info includes advanced features."""
        strategy = TreeGraphHybridStrategy()
        info = strategy.backend_info()
        
        # Check that advanced features are listed
        assert "union_find" in info["features"]
        assert "trie_operations" in info["features"]
        assert "priority_queue" in info["features"]
        assert "advanced_traits" in info["features"]
        
        # Check that complexity info includes advanced operations
        assert "union_find" in info["complexity"]
        assert "trie" in info["complexity"]
        assert "heap" in info["complexity"]
    
    def test_persistence_across_operations(self):
        """Test that advanced operations persist data correctly."""
        strategy = TreeGraphHybridStrategy()
        
        # Add data to all structures
        strategy.union_find_make_set(1)
        strategy.union_find_union(1, 2)
        
        strategy.trie_insert("hello", "greeting")
        strategy.trie_insert("world", "planet")
        
        strategy.heap_push("task1", 1.0)
        strategy.heap_push("task2", 2.0)
        
        # Convert to native and back
        native_data = strategy.to_native()
        new_strategy = TreeGraphHybridStrategy()
        new_strategy.create_from_data(native_data)
        
        # Verify data persisted
        assert new_strategy.union_find_connected(1, 2) == True
        assert new_strategy.trie_contains("hello") == True
        assert new_strategy.trie_get("hello") == "greeting"
        assert new_strategy.heap_size() == 2
        assert new_strategy.heap_pop_min() == "task1"
