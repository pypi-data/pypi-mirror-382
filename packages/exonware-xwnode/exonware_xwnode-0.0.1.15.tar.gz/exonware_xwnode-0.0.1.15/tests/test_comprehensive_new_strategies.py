#!/usr/bin/env python3
"""
Comprehensive New Strategies Test

Test all the newly added strategies organized by type.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

print("🚀 Comprehensive New Strategies Test")
print("=" * 50)

def test_linear_strategies():
    """Test all Linear strategies."""
    print("\n📋 Testing Linear Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.array_list import ArrayListStrategy
        from exonware.xwnode.strategies.nodes.linked_list import LinkedListStrategy
        from exonware.xwnode.strategies.nodes.stack import StackStrategy
        from exonware.xwnode.strategies.nodes.queue import QueueStrategy
        from exonware.xwnode.strategies.nodes.priority_queue import PriorityQueueStrategy
        from exonware.xwnode.strategies.nodes.deque import DequeStrategy
        
        # Test ArrayList
        print("   Testing ArrayListStrategy...")
        array_list = ArrayListStrategy()
        array_list.insert("item1", "value1")
        array_list.insert("item2", "value2")
        assert array_list.find("item1") == "value1"
        assert array_list.size() == 2
        print("   ✅ ArrayListStrategy works")
        
        # Test LinkedList
        print("   Testing LinkedListStrategy...")
        linked_list = LinkedListStrategy()
        linked_list.insert("item1", "value1")
        linked_list.insert("item2", "value2")
        assert linked_list.find("item1") == "value1"
        assert linked_list.size() == 2
        print("   ✅ LinkedListStrategy works")
        
        # Test Stack
        print("   Testing StackStrategy...")
        stack = StackStrategy()
        stack.push("value1")
        stack.push("value2")
        assert stack.peek() == "value2"
        assert stack.pop() == "value2"
        assert stack.size() == 1
        print("   ✅ StackStrategy works")
        
        # Test Queue
        print("   Testing QueueStrategy...")
        queue = QueueStrategy()
        queue.enqueue("value1")
        queue.enqueue("value2")
        assert queue.front() == "value1"
        assert queue.dequeue() == "value1"
        assert queue.size() == 1
        print("   ✅ QueueStrategy works")
        
        # Test PriorityQueue
        print("   Testing PriorityQueueStrategy...")
        pq = PriorityQueueStrategy()
        pq.insert_with_priority("item1", "value1", 1.0)
        pq.insert_with_priority("item2", "value2", 0.5)
        min_item = pq.extract_min()
        assert min_item[0] == "item2"  # Lower priority should come first
        print("   ✅ PriorityQueueStrategy works")
        
        # Test Deque
        print("   Testing DequeStrategy...")
        deque = DequeStrategy()
        deque.append("value1")
        deque.appendleft("value2")
        assert deque.peek_left() == "value2"
        assert deque.peek_right() == "value1"
        assert deque.size() == 2
        print("   ✅ DequeStrategy works")
        
        print("   ✅ All Linear strategies work correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Linear strategies test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_matrix_strategies():
    """Test all Matrix strategies."""
    print("\n🔢 Testing Matrix Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.node_bitmap import BitmapStrategy
        from exonware.xwnode.strategies.nodes.node_roaring_bitmap import RoaringBitmapStrategy
        from exonware.xwnode.strategies.nodes.node_bitset_dynamic import BitsetDynamicStrategy
        from exonware.xwnode.strategies.nodes.sparse_matrix import SparseMatrixStrategy
        
        # Test Bitmap
        print("   Testing BitmapStrategy...")
        bitmap = BitmapStrategy()
        bitmap.set_at_position(0, 0, True)
        bitmap.set_at_position(1, 1, True)
        assert bitmap.get_at_position(0, 0) == True
        assert bitmap.get_dimensions() == (2, 2)
        print("   ✅ BitmapStrategy works")
        
        # Test RoaringBitmap
        print("   Testing RoaringBitmapStrategy...")
        roaring = RoaringBitmapStrategy()
        roaring.set_at_position(0, 0, True)
        roaring.set_at_position(1, 1, True)
        assert roaring.get_at_position(0, 0) == True
        assert roaring.get_dimensions() == (2, 2)
        print("   ✅ RoaringBitmapStrategy works")
        
        # Test BitsetDynamic
        print("   Testing BitsetDynamicStrategy...")
        bitset = BitsetDynamicStrategy()
        bitset.set_at_position(0, 0, True)
        bitset.set_at_position(1, 1, True)
        assert bitset.get_at_position(0, 0) == True
        assert bitset.get_dimensions() == (2, 2)
        print("   ✅ BitsetDynamicStrategy works")
        
        # Test SparseMatrix
        print("   Testing SparseMatrixStrategy...")
        sparse = SparseMatrixStrategy()
        sparse.set_at_position(0, 0, 5)
        sparse.set_at_position(1, 1, 10)
        assert sparse.get_at_position(0, 0) == 5
        assert sparse.get_dimensions() == (2, 2)
        assert sparse.density() < 1.0  # Should be sparse
        print("   ✅ SparseMatrixStrategy works")
        
        print("   ✅ All Matrix strategies work correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Matrix strategies test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_strategies():
    """Test all Graph strategies."""
    print("\n🕸️ Testing Graph Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.node_union_find import UnionFindStrategy
        from exonware.xwnode.strategies.nodes.adjacency_list import AdjacencyListStrategy
        
        # Test UnionFind
        print("   Testing UnionFindStrategy...")
        uf = UnionFindStrategy()
        uf.insert("node1", "data1")
        uf.insert("node2", "data2")
        uf.union("node1", "node2")
        assert uf.find("node1") == uf.find("node2")
        print("   ✅ UnionFindStrategy works")
        
        # Test AdjacencyList
        print("   Testing AdjacencyListStrategy...")
        adj_list = AdjacencyListStrategy()
        adj_list.insert("A", "nodeA")
        adj_list.insert("B", "nodeB")
        adj_list.add_edge("A", "B", 1.5)
        assert adj_list.has_edge("A", "B") == True
        assert adj_list.get_edge_weight("A", "B") == 1.5
        assert "B" in adj_list.get_neighbors("A")
        print("   ✅ AdjacencyListStrategy works")
        
        print("   ✅ All Graph strategies work correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Graph strategies test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tree_strategies():
    """Test all Tree strategies."""
    print("\n🌳 Testing Tree Strategies...")
    
    try:
        from exonware.xwnode.strategies.nodes.node_avl_tree import AVLTreeStrategy
        from exonware.xwnode.strategies.nodes.node_trie import TrieStrategy
        from exonware.xwnode.strategies.nodes.node_heap import HeapStrategy
        
        # Test AVLTree
        print("   Testing AVLTreeStrategy...")
        avl = AVLTreeStrategy()
        avl.insert("key1", "value1")
        avl.insert("key2", "value2")
        assert avl.find("key1") == "value1"
        assert avl.size() == 2
        print("   ✅ AVLTreeStrategy works")
        
        # Test Trie
        print("   Testing TrieStrategy...")
        trie = TrieStrategy()
        trie.insert("hello", "world")
        trie.insert("help", "me")
        assert trie.find("hello") == "world"
        assert trie.find("help") == "me"
        print("   ✅ TrieStrategy works")
        
        # Test Heap
        print("   Testing HeapStrategy...")
        heap = HeapStrategy()
        heap.insert("key1", 10)
        heap.insert("key2", 5)
        heap.insert("key3", 15)
        min_key = heap.get_min()
        max_key = heap.get_max()
        assert min_key is not None
        assert max_key is not None
        print("   ✅ HeapStrategy works")
        
        print("   ✅ All Tree strategies work correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Tree strategies test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_organization():
    """Test that strategies are properly organized by type."""
    print("\n📊 Testing Strategy Organization...")
    
    try:
        from exonware.xwnode.strategies.nodes.base import (
            ANodeStrategy, ANodeLinearStrategy, ANodeMatrixStrategy,
            ANodeGraphStrategy, ANodeTreeStrategy
        )
        
        # Test Linear strategies
        from exonware.xwnode.strategies.nodes.stack import StackStrategy
        from exonware.xwnode.strategies.nodes.queue import QueueStrategy
        from exonware.xwnode.strategies.nodes.priority_queue import PriorityQueueStrategy
        from exonware.xwnode.strategies.nodes.deque import DequeStrategy
        
        assert issubclass(StackStrategy, ANodeLinearStrategy)
        assert issubclass(QueueStrategy, ANodeLinearStrategy)
        assert issubclass(PriorityQueueStrategy, ANodeLinearStrategy)
        assert issubclass(DequeStrategy, ANodeLinearStrategy)
        print("   ✅ Linear strategies properly inherit from ANodeLinearStrategy")
        
        # Test Matrix strategies
        from exonware.xwnode.strategies.nodes.sparse_matrix import SparseMatrixStrategy
        
        assert issubclass(SparseMatrixStrategy, ANodeMatrixStrategy)
        print("   ✅ Matrix strategies properly inherit from ANodeMatrixStrategy")
        
        # Test Graph strategies
        from exonware.xwnode.strategies.nodes.adjacency_list import AdjacencyListStrategy
        
        assert issubclass(AdjacencyListStrategy, ANodeGraphStrategy)
        print("   ✅ Graph strategies properly inherit from ANodeGraphStrategy")
        
        # Test Tree strategies
        from exonware.xwnode.strategies.nodes.node_avl_tree import AVLTreeStrategy
        from exonware.xwnode.strategies.nodes.node_trie import TrieStrategy
        
        assert issubclass(AVLTreeStrategy, ANodeTreeStrategy)
        assert issubclass(TrieStrategy, ANodeTreeStrategy)
        print("   ✅ Tree strategies properly inherit from ANodeTreeStrategy")
        
        print("   ✅ All strategies are properly organized by type!")
        return True
        
    except Exception as e:
        print(f"   ❌ Strategy organization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_world_scenarios():
    """Test strategies with real-world scenarios."""
    print("\n🌍 Testing Real-World Scenarios...")
    
    try:
        # Scenario 1: Web Browser History (Stack)
        print("   Testing Web Browser History (Stack)...")
        history = StackStrategy()
        history.push("google.com")
        history.push("github.com")
        history.push("stackoverflow.com")
        assert history.peek() == "stackoverflow.com"
        history.pop()  # Go back
        assert history.peek() == "github.com"
        print("   ✅ Web browser history works with Stack")
        
        # Scenario 2: Task Queue (Priority Queue)
        print("   Testing Task Queue (Priority Queue)...")
        task_queue = PriorityQueueStrategy()
        task_queue.insert_with_priority("urgent", "Fix critical bug", 1.0)
        task_queue.insert_with_priority("normal", "Update documentation", 5.0)
        task_queue.insert_with_priority("low", "Clean up code", 10.0)
        
        urgent_task = task_queue.extract_min()
        assert urgent_task[0] == "urgent"
        print("   ✅ Task queue works with Priority Queue")
        
        # Scenario 3: Social Network (Adjacency List)
        print("   Testing Social Network (Adjacency List)...")
        social_network = AdjacencyListStrategy()
        social_network.insert("Alice", {"name": "Alice", "age": 25})
        social_network.insert("Bob", {"name": "Bob", "age": 30})
        social_network.insert("Charlie", {"name": "Charlie", "age": 28})
        
        social_network.add_edge("Alice", "Bob", 0.8)  # Friendship strength
        social_network.add_edge("Bob", "Charlie", 0.6)
        
        alice_friends = social_network.get_neighbors("Alice")
        assert "Bob" in alice_friends
        print("   ✅ Social network works with Adjacency List")
        
        # Scenario 4: Sparse Data Matrix (Sparse Matrix)
        print("   Testing Sparse Data Matrix (Sparse Matrix)...")
        data_matrix = SparseMatrixStrategy()
        data_matrix.set_at_position(0, 0, 100)  # User 0, Item 0, Rating 100
        data_matrix.set_at_position(0, 5, 85)   # User 0, Item 5, Rating 85
        data_matrix.set_at_position(1, 0, 90)   # User 1, Item 0, Rating 90
        
        assert data_matrix.get_at_position(0, 0) == 100
        assert data_matrix.density() < 0.1  # Should be very sparse
        print("   ✅ Sparse data matrix works with Sparse Matrix")
        
        print("   ✅ All real-world scenarios work correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Real-world scenarios test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all comprehensive new strategy tests."""
    print("Starting comprehensive new strategy testing...")
    
    results = []
    
    # Test each strategy type
    results.append(test_linear_strategies())
    results.append(test_matrix_strategies())
    results.append(test_graph_strategies())
    results.append(test_tree_strategies())
    
    # Test organization
    results.append(test_strategy_organization())
    
    # Test real-world scenarios
    results.append(test_real_world_scenarios())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎉 COMPREHENSIVE NEW STRATEGIES TESTS COMPLETED!")
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📋 New Strategies Tested:")
        print("   📋 Linear: Stack, Queue, PriorityQueue, Deque")
        print("   🔢 Matrix: SparseMatrix")
        print("   🕸️ Graph: AdjacencyList")
        print("   🌳 Tree: AVLTree, Trie, Heap (existing)")
        print("   📊 Organization: All strategies properly categorized")
        print("   🌍 Real-world: Browser history, task queue, social network, sparse data")
        
        print("\n✨ All new XWNode strategies are working comprehensively!")
        
        return True
    else:
        print(f"\n❌ {total - passed} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
