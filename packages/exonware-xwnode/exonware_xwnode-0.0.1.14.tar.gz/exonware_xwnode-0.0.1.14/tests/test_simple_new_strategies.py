#!/usr/bin/env python3
"""
Simple New Strategies Test

Test the newly added strategies with minimal imports.

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

print("🚀 Simple New Strategies Test")
print("=" * 40)

def test_stack():
    """Test Stack strategy."""
    print("\n📋 Testing Stack Strategy...")
    
    try:
        from exonware.xwnode.strategies.nodes.stack import StackStrategy
        
        stack = StackStrategy()
        stack.push("value1")
        stack.push("value2")
        
        assert stack.peek() == "value2"
        assert stack.pop() == "value2"
        assert stack.size() == 1
        
        print("   ✅ StackStrategy works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ StackStrategy failed: {e}")
        return False

def test_queue():
    """Test Queue strategy."""
    print("\n📋 Testing Queue Strategy...")
    
    try:
        from exonware.xwnode.strategies.nodes.queue import QueueStrategy
        
        queue = QueueStrategy()
        queue.enqueue("value1")
        queue.enqueue("value2")
        
        assert queue.front() == "value1"
        assert queue.dequeue() == "value1"
        assert queue.size() == 1
        
        print("   ✅ QueueStrategy works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ QueueStrategy failed: {e}")
        return False

def test_priority_queue():
    """Test Priority Queue strategy."""
    print("\n📋 Testing Priority Queue Strategy...")
    
    try:
        from exonware.xwnode.strategies.nodes.priority_queue import PriorityQueueStrategy
        
        pq = PriorityQueueStrategy()
        pq.insert_with_priority("item1", "value1", 1.0)
        pq.insert_with_priority("item2", "value2", 0.5)
        
        min_item = pq.extract_min()
        assert min_item[0] == "item2"  # Lower priority should come first
        
        print("   ✅ PriorityQueueStrategy works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ PriorityQueueStrategy failed: {e}")
        return False

def test_deque():
    """Test Deque strategy."""
    print("\n📋 Testing Deque Strategy...")
    
    try:
        from exonware.xwnode.strategies.nodes.deque import DequeStrategy
        
        deque = DequeStrategy()
        deque.append("value1")
        deque.appendleft("value2")
        
        assert deque.peek_left() == "value2"
        assert deque.peek_right() == "value1"
        assert deque.size() == 2
        
        print("   ✅ DequeStrategy works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ DequeStrategy failed: {e}")
        return False

def test_sparse_matrix():
    """Test Sparse Matrix strategy."""
    print("\n🔢 Testing Sparse Matrix Strategy...")
    
    try:
        from exonware.xwnode.strategies.nodes.sparse_matrix import SparseMatrixStrategy
        
        sparse = SparseMatrixStrategy()
        sparse.set_at_position(0, 0, 5)
        sparse.set_at_position(1, 1, 10)
        
        assert sparse.get_at_position(0, 0) == 5
        assert sparse.get_dimensions() == (2, 2)
        assert sparse.density() < 1.0  # Should be sparse
        
        print("   ✅ SparseMatrixStrategy works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ SparseMatrixStrategy failed: {e}")
        return False

def test_adjacency_list():
    """Test Adjacency List strategy."""
    print("\n🕸️ Testing Adjacency List Strategy...")
    
    try:
        from exonware.xwnode.strategies.nodes.adjacency_list import AdjacencyListStrategy
        
        adj_list = AdjacencyListStrategy()
        adj_list.insert("A", "nodeA")
        adj_list.insert("B", "nodeB")
        adj_list.add_edge("A", "B", 1.5)
        
        assert adj_list.has_edge("A", "B") == True
        assert adj_list.get_edge_weight("A", "B") == 1.5
        assert "B" in adj_list.get_neighbors("A")
        
        print("   ✅ AdjacencyListStrategy works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ AdjacencyListStrategy failed: {e}")
        return False

def main():
    """Run all simple new strategy tests."""
    print("Starting simple new strategy testing...")
    
    results = []
    
    # Test each new strategy
    results.append(test_stack())
    results.append(test_queue())
    results.append(test_priority_queue())
    results.append(test_deque())
    results.append(test_sparse_matrix())
    results.append(test_adjacency_list())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎉 SIMPLE NEW STRATEGIES TESTS COMPLETED!")
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📋 New Strategies Tested:")
        print("   📋 Linear: Stack, Queue, PriorityQueue, Deque")
        print("   🔢 Matrix: SparseMatrix")
        print("   🕸️ Graph: AdjacencyList")
        
        print("\n✨ All new XWNode strategies are working!")
        
        return True
    else:
        print(f"\n❌ {total - passed} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
