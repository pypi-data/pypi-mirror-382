#!/usr/bin/env python3
"""
Test XWNode Strategy Inheritance Hierarchy

Test that all strategies inherit from the correct abstract base classes.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
sys.path.insert(0, str(src_path))

print("🚀 Testing XWNode Strategy Inheritance Hierarchy")
print("=" * 50)

def test_inheritance_hierarchy():
    """Test that all strategies inherit from the correct base classes."""
    print("\n📋 Testing Inheritance Hierarchy...")
    
    try:
        # Import abstract base classes
        from exonware.xwnode.strategies.nodes.base import (
            ANodeStrategy,
            ANodeLinearStrategy,
            ANodeMatrixStrategy,
            ANodeGraphStrategy,
            ANodeTreeStrategy
        )
        
        print("   ✅ Abstract base classes imported successfully")
        
        # Test that ANodeTreeStrategy inherits from ANodeGraphStrategy
        assert issubclass(ANodeTreeStrategy, ANodeGraphStrategy), "ANodeTreeStrategy should inherit from ANodeGraphStrategy"
        print("   ✅ ANodeTreeStrategy inherits from ANodeGraphStrategy")
        
        # Test that all base classes inherit from ANodeStrategy
        assert issubclass(ANodeLinearStrategy, ANodeStrategy), "ANodeLinearStrategy should inherit from ANodeStrategy"
        assert issubclass(ANodeMatrixStrategy, ANodeStrategy), "ANodeMatrixStrategy should inherit from ANodeStrategy"
        assert issubclass(ANodeGraphStrategy, ANodeStrategy), "ANodeGraphStrategy should inherit from ANodeStrategy"
        print("   ✅ All base classes inherit from ANodeStrategy")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Inheritance hierarchy test failed: {e}")
        return False

def test_linear_strategies():
    """Test that linear strategies inherit from ANodeLinearStrategy."""
    print("\n📋 Testing Linear Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.base import ANodeLinearStrategy
        from exonware.xwnode.strategies.nodes.array_list import ArrayListStrategy
        from exonware.xwnode.strategies.nodes.linked_list import LinkedListStrategy
        
        # Test inheritance
        assert issubclass(XWArrayListStrategy, ANodeLinearStrategy), "XWArrayListStrategy should inherit from ANodeLinearStrategy"
        assert issubclass(XWLinkedListStrategy, ANodeLinearStrategy), "XWLinkedListStrategy should inherit from ANodeLinearStrategy"
        
        print("   ✅ XWArrayListStrategy inherits from ANodeLinearStrategy")
        print("   ✅ XWLinkedListStrategy inherits from ANodeLinearStrategy")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Linear strategies test failed: {e}")
        return False

def test_matrix_strategies():
    """Test that matrix strategies inherit from ANodeMatrixStrategy."""
    print("\n🔢 Testing Matrix Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.base import ANodeMatrixStrategy
        from exonware.xwnode.strategies.nodes.node_bitmap import BitmapStrategy
        from exonware.xwnode.strategies.nodes.node_roaring_bitmap import RoaringBitmapStrategy
        from exonware.xwnode.strategies.nodes.node_bitset_dynamic import BitsetDynamicStrategy
        
        # Test inheritance
        assert issubclass(BitmapStrategy, ANodeMatrixStrategy), "BitmapStrategy should inherit from ANodeMatrixStrategy"
        assert issubclass(RoaringBitmapStrategy, ANodeMatrixStrategy), "RoaringBitmapStrategy should inherit from ANodeMatrixStrategy"
        assert issubclass(BitsetDynamicStrategy, ANodeMatrixStrategy), "BitsetDynamicStrategy should inherit from ANodeMatrixStrategy"
        
        print("   ✅ BitmapStrategy inherits from ANodeMatrixStrategy")
        print("   ✅ RoaringBitmapStrategy inherits from ANodeMatrixStrategy")
        print("   ✅ BitsetDynamicStrategy inherits from ANodeMatrixStrategy")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Matrix strategies test failed: {e}")
        return False

def test_graph_strategies():
    """Test that graph strategies inherit from ANodeGraphStrategy."""
    print("\n🕸️ Testing Graph Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.base import ANodeGraphStrategy
        from exonware.xwnode.strategies.nodes.node_union_find import UnionFindStrategy
        
        # Test inheritance
        assert issubclass(UnionFindStrategy, ANodeGraphStrategy), "UnionFindStrategy should inherit from ANodeGraphStrategy"
        
        print("   ✅ UnionFindStrategy inherits from ANodeGraphStrategy")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Graph strategies test failed: {e}")
        return False

def test_tree_strategies():
    """Test that tree strategies inherit from ANodeTreeStrategy."""
    print("\n🌳 Testing Tree Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.base import ANodeTreeStrategy
        from exonware.xwnode.strategies.nodes.node_avl_tree import AVLTreeStrategy
        from exonware.xwnode.strategies.nodes.node_red_black_tree import RedBlackTreeStrategy
        from exonware.xwnode.strategies.nodes.node_b_plus_tree import BPlusTreeStrategy
        from exonware.xwnode.strategies.nodes.node_trie import TrieStrategy
        from exonware.xwnode.strategies.nodes.node_heap import HeapStrategy
        from exonware.xwnode.strategies.nodes.node_btree import BTreeStrategy
        from exonware.xwnode.strategies.nodes.node_splay_tree import SplayTreeStrategy
        from exonware.xwnode.strategies.nodes.node_treap import TreapStrategy
        from exonware.xwnode.strategies.nodes.node_skip_list import SkipListStrategy
        from exonware.xwnode.strategies.nodes.node_patricia import PatriciaStrategy
        from exonware.xwnode.strategies.nodes.node_radix_trie import RadixTrieStrategy
        from exonware.xwnode.strategies.nodes.node_segment_tree import SegmentTreeStrategy
        from exonware.xwnode.strategies.nodes.node_fenwick_tree import FenwickTreeStrategy
        from exonware.xwnode.strategies.nodes.node_cow_tree import COWTreeStrategy
        from exonware.xwnode.strategies.nodes.node_persistent_tree import PersistentTreeStrategy
        from exonware.xwnode.strategies.nodes.node_lsm_tree import LSMTreeStrategy
        from exonware.xwnode.strategies.nodes.node_ordered_map_balanced import OrderedMapBalancedStrategy
        from exonware.xwnode.strategies.nodes.node_ordered_map import OrderedMapStrategy
        from exonware.xwnode.strategies.nodes.node_set_tree import SetTreeStrategy
        from exonware.xwnode.strategies.nodes.node_aho_corasick import AhoCorasickStrategy
        from exonware.xwnode.strategies.nodes.node_suffix_array import SuffixArrayStrategy
        
        # Test inheritance
        tree_strategies = [
            AVLTreeStrategy, RedBlackTreeStrategy, BPlusTreeStrategy,
            TrieStrategy, HeapStrategy, BTreeStrategy, SplayTreeStrategy,
            TreapStrategy, SkipListStrategy, PatriciaStrategy,
            RadixTrieStrategy, SegmentTreeStrategy, FenwickTreeStrategy,
            COWTreeStrategy, PersistentTreeStrategy, LSMTreeStrategy,
            OrderedMapBalancedStrategy, OrderedMapStrategy, SetTreeStrategy,
            AhoCorasickStrategy, SuffixArrayStrategy
        ]
        
        for strategy in tree_strategies:
            assert issubclass(strategy, ANodeTreeStrategy), f"{strategy.__name__} should inherit from ANodeTreeStrategy"
            print(f"   ✅ {strategy.__name__} inherits from ANodeTreeStrategy")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Tree strategies test failed: {e}")
        return False

def test_strategy_creation():
    """Test that strategies can be created and basic methods work."""
    print("\n🔧 Testing Strategy Creation...")
    
    try:
        from exonware.xwnode.strategies.nodes.array_list import ArrayListStrategy
        from exonware.xwnode.strategies.nodes.linked_list import LinkedListStrategy
        from exonware.xwnode.strategies.nodes.hash_map import HashMapStrategy
        
        # Test creating strategies
        array_strategy = ArrayListStrategy()
        linked_strategy = LinkedListStrategy()
        hash_strategy = HashMapStrategy()
        
        print("   ✅ ArrayListStrategy created successfully")
        print("   ✅ LinkedListStrategy created successfully")
        print("   ✅ HashMapStrategy created successfully")
        
        # Test basic operations
        array_strategy.insert("key1", "value1")
        linked_strategy.insert("key1", "value1")
        hash_strategy.insert("key1", "value1")
        
        assert array_strategy.find("key1") == "value1"
        assert linked_strategy.find("key1") == "value1"
        assert hash_strategy.find("key1") == "value1"
        
        print("   ✅ Basic operations work on all strategies")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Strategy creation test failed: {e}")
        return False

def main():
    """Run all inheritance hierarchy tests."""
    print("Starting inheritance hierarchy testing...")
    
    results = []
    
    # Test all components
    results.append(test_inheritance_hierarchy())
    results.append(test_linear_strategies())
    results.append(test_matrix_strategies())
    results.append(test_graph_strategies())
    results.append(test_tree_strategies())
    results.append(test_strategy_creation())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎉 INHERITANCE HIERARCHY TESTS COMPLETED!")
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📋 Inheritance Hierarchy Verified:")
        print("   ✅ ANodeTreeStrategy inherits from ANodeGraphStrategy")
        print("   ✅ All base classes inherit from ANodeStrategy")
        print("   ✅ Linear strategies inherit from ANodeLinearStrategy")
        print("   ✅ Matrix strategies inherit from ANodeMatrixStrategy")
        print("   ✅ Graph strategies inherit from ANodeGraphStrategy")
        print("   ✅ Tree strategies inherit from ANodeTreeStrategy")
        print("   ✅ All strategies can be created and work correctly")
        
        print("\n🔧 Strategy Types Verified:")
        print("   📋 Linear: XWArrayListStrategy, XWLinkedListStrategy")
        print("   🔢 Matrix: XWBitmapStrategy, XWRoaringBitmapStrategy, XWBitsetDynamicStrategy")
        print("   🕸️ Graph: XWUnionFindStrategy")
        print("   🌳 Tree: 21+ tree strategies (AVL, Red-Black, B+, Trie, Heap, etc.)")
        
        print("\n✨ XWNode Strategy Inheritance Hierarchy is Correct!")
        print("\n🎯 Inheritance Chain:")
        print("   ANodeStrategy (base)")
        print("   ├── ANodeLinearStrategy")
        print("   ├── ANodeMatrixStrategy")
        print("   ├── ANodeGraphStrategy")
        print("   └── ANodeTreeStrategy (inherits from ANodeGraphStrategy)")
        
        return True
    else:
        print(f"\n❌ {total - passed} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
