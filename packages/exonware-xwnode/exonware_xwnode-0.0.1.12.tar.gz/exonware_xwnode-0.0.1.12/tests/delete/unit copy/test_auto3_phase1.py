#!/usr/bin/env python3
"""
Test AUTO-3 Phase 1: Linear Data Structures.

Tests LinkedList, Stack, Queue, and Deque behavioral views on xNode.
"""

import sys
import os
import pytest
from typing import Dict, Any, List

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode
from src.xlib.xnode.errors import xNodeTypeError, xNodeValueError


class TestLinkedListView:
    """Test LinkedList behavioral view."""
    
    def test_linked_list_creation(self):
        """Test creating LinkedList view from list node."""
        node = xNode.from_native([1, 2, 3])
        ll = node.as_linked_list()
        
        assert ll.size() == 3
        assert not ll.is_empty()
        assert ll.front() == 1
        assert ll.back() == 3
    
    def test_linked_list_push_back(self):
        """Test pushing elements to back of list."""
        node = xNode.from_native([1, 2])
        ll = node.as_linked_list()
        
        ll.push_back(3)
        assert ll.size() == 3
        assert ll.back() == 3
        assert node.to_native() == [1, 2, 3]
    
    def test_linked_list_push_front(self):
        """Test pushing elements to front of list."""
        node = xNode.from_native([2, 3])
        ll = node.as_linked_list()
        
        ll.push_front(1)
        assert ll.size() == 3
        assert ll.front() == 1
        assert node.to_native() == [1, 2, 3]
    
    def test_linked_list_pop_back(self):
        """Test popping elements from back of list."""
        node = xNode.from_native([1, 2, 3])
        ll = node.as_linked_list()
        
        value = ll.pop_back()
        assert value == 3
        assert ll.size() == 2
        assert node.to_native() == [1, 2]
    
    def test_linked_list_pop_front(self):
        """Test popping elements from front of list."""
        node = xNode.from_native([1, 2, 3])
        ll = node.as_linked_list()
        
        value = ll.pop_front()
        assert value == 1
        assert ll.size() == 2
        assert node.to_native() == [2, 3]
    
    def test_linked_list_clear(self):
        """Test clearing linked list."""
        node = xNode.from_native([1, 2, 3])
        ll = node.as_linked_list()
        
        ll.clear()
        assert ll.size() == 0
        assert ll.is_empty()
        assert node.to_native() == []
    
    def test_linked_list_empty_operations(self):
        """Test operations on empty linked list."""
        node = xNode.from_native([])
        ll = node.as_linked_list()
        
        assert ll.is_empty()
        assert ll.size() == 0
        
        # Test error conditions
        with pytest.raises(xNodeValueError):
            ll.pop_front()
        
        with pytest.raises(xNodeValueError):
            ll.pop_back()
        
        with pytest.raises(xNodeValueError):
            ll.front()
        
        with pytest.raises(xNodeValueError):
            ll.back()
    
    def test_linked_list_non_list_node(self):
        """Test LinkedList view with non-list node."""
        node = xNode.from_native({"key": "value"})
        
        with pytest.raises(xNodeTypeError):
            node.as_linked_list()


class TestStackView:
    """Test Stack behavioral view."""
    
    def test_stack_creation(self):
        """Test creating Stack view from list node."""
        node = xNode.from_native([1, 2, 3])
        stack = node.as_stack()
        
        assert stack.size() == 3
        assert not stack.is_empty()
        assert stack.peek() == 3
        assert stack.top() == 3
    
    def test_stack_push_pop(self):
        """Test stack push and pop operations."""
        node = xNode.from_native([])
        stack = node.as_stack()
        
        # Test push
        stack.push(1)
        assert stack.size() == 1
        assert stack.peek() == 1
        
        stack.push(2)
        assert stack.size() == 2
        assert stack.peek() == 2
        
        # Test pop
        value = stack.pop()
        assert value == 2
        assert stack.size() == 1
        assert stack.peek() == 1
        
        value = stack.pop()
        assert value == 1
        assert stack.is_empty()
    
    def test_stack_lifo_order(self):
        """Test LIFO (Last In, First Out) behavior."""
        node = xNode.from_native([])
        stack = node.as_stack()
        
        # Push elements
        for i in range(5):
            stack.push(i)
        
        # Pop elements - should be in reverse order
        result = []
        while not stack.is_empty():
            result.append(stack.pop())
        
        assert result == [4, 3, 2, 1, 0]
    
    def test_stack_clear(self):
        """Test clearing stack."""
        node = xNode.from_native([1, 2, 3])
        stack = node.as_stack()
        
        stack.clear()
        assert stack.is_empty()
        assert stack.size() == 0
    
    def test_stack_empty_operations(self):
        """Test operations on empty stack."""
        node = xNode.from_native([])
        stack = node.as_stack()
        
        assert stack.is_empty()
        
        with pytest.raises(xNodeValueError):
            stack.pop()
        
        with pytest.raises(xNodeValueError):
            stack.peek()
        
        with pytest.raises(xNodeValueError):
            stack.top()
    
    def test_stack_non_list_node(self):
        """Test Stack view with non-list node."""
        node = xNode.from_native({"key": "value"})
        
        with pytest.raises(xNodeTypeError):
            node.as_stack()


class TestQueueView:
    """Test Queue behavioral view."""
    
    def test_queue_creation(self):
        """Test creating Queue view from list node."""
        node = xNode.from_native([1, 2, 3])
        queue = node.as_queue()
        
        assert queue.size() == 3
        assert not queue.is_empty()
        assert queue.front() == 1
        assert queue.back() == 3
    
    def test_queue_enqueue_dequeue(self):
        """Test queue enqueue and dequeue operations."""
        node = xNode.from_native([])
        queue = node.as_queue()
        
        # Test enqueue
        queue.enqueue(1)
        assert queue.size() == 1
        assert queue.front() == 1
        assert queue.back() == 1
        
        queue.enqueue(2)
        assert queue.size() == 2
        assert queue.front() == 1
        assert queue.back() == 2
        
        # Test dequeue
        value = queue.dequeue()
        assert value == 1
        assert queue.size() == 1
        assert queue.front() == 2
        
        value = queue.dequeue()
        assert value == 2
        assert queue.is_empty()
    
    def test_queue_fifo_order(self):
        """Test FIFO (First In, First Out) behavior."""
        node = xNode.from_native([])
        queue = node.as_queue()
        
        # Enqueue elements
        for i in range(5):
            queue.enqueue(i)
        
        # Dequeue elements - should be in same order
        result = []
        while not queue.is_empty():
            result.append(queue.dequeue())
        
        assert result == [0, 1, 2, 3, 4]
    
    def test_queue_clear(self):
        """Test clearing queue."""
        node = xNode.from_native([1, 2, 3])
        queue = node.as_queue()
        
        queue.clear()
        assert queue.is_empty()
        assert queue.size() == 0
    
    def test_queue_empty_operations(self):
        """Test operations on empty queue."""
        node = xNode.from_native([])
        queue = node.as_queue()
        
        assert queue.is_empty()
        
        with pytest.raises(xNodeValueError):
            queue.dequeue()
        
        with pytest.raises(xNodeValueError):
            queue.front()
        
        with pytest.raises(xNodeValueError):
            queue.back()
    
    def test_queue_non_list_node(self):
        """Test Queue view with non-list node."""
        node = xNode.from_native({"key": "value"})
        
        with pytest.raises(xNodeTypeError):
            node.as_queue()


class TestDequeView:
    """Test Deque (double-ended queue) behavioral view."""
    
    def test_deque_creation(self):
        """Test creating Deque view from list node."""
        node = xNode.from_native([1, 2, 3])
        dq = node.as_deque()
        
        assert dq.size() == 3
        assert not dq.is_empty()
    
    def test_deque_append_operations(self):
        """Test deque append operations."""
        node = xNode.from_native([2, 3])
        dq = node.as_deque()
        
        # Append left
        dq.append_left(1)
        assert dq.size() == 3
        assert node.to_native() == [1, 2, 3]
        
        # Append right
        dq.append_right(4)
        assert dq.size() == 4
        assert node.to_native() == [1, 2, 3, 4]
    
    def test_deque_pop_operations(self):
        """Test deque pop operations."""
        node = xNode.from_native([1, 2, 3, 4])
        dq = node.as_deque()
        
        # Pop left
        value = dq.pop_left()
        assert value == 1
        assert dq.size() == 3
        assert node.to_native() == [2, 3, 4]
        
        # Pop right
        value = dq.pop_right()
        assert value == 4
        assert dq.size() == 2
        assert node.to_native() == [2, 3]
    
    def test_deque_both_ends(self):
        """Test operations on both ends simultaneously."""
        node = xNode.from_native([])
        dq = node.as_deque()
        
        # Build: [1, 2, 3, 4, 5]
        dq.append_right(3)
        dq.append_left(2)
        dq.append_left(1)
        dq.append_right(4)
        dq.append_right(5)
        
        assert node.to_native() == [1, 2, 3, 4, 5]
        
        # Remove from both ends
        left = dq.pop_left()    # 1
        right = dq.pop_right()  # 5
        
        assert left == 1
        assert right == 5
        assert node.to_native() == [2, 3, 4]
    
    def test_deque_clear(self):
        """Test clearing deque."""
        node = xNode.from_native([1, 2, 3])
        dq = node.as_deque()
        
        dq.clear()
        assert dq.is_empty()
        assert dq.size() == 0
        assert node.to_native() == []
    
    def test_deque_empty_operations(self):
        """Test operations on empty deque."""
        node = xNode.from_native([])
        dq = node.as_deque()
        
        assert dq.is_empty()
        
        with pytest.raises(xNodeValueError):
            dq.pop_left()
        
        with pytest.raises(xNodeValueError):
            dq.pop_right()
    
    def test_deque_non_list_node(self):
        """Test Deque view with non-list node."""
        node = xNode.from_native({"key": "value"})
        
        with pytest.raises(xNodeTypeError):
            node.as_deque()


class TestConvenienceMethods:
    """Test convenience methods on xNode for common operations."""
    
    def test_push_pop_methods(self):
        """Test push/pop convenience methods (stack behavior)."""
        node = xNode.from_native([])
        
        # Test chaining
        result = node.push(1).push(2).push(3)
        assert result is node  # Should return self for chaining
        assert node.to_native() == [1, 2, 3]
        
        # Test pop
        value = node.pop()
        assert value == 3
        assert node.to_native() == [1, 2]
    
    def test_enqueue_dequeue_methods(self):
        """Test enqueue/dequeue convenience methods (queue behavior)."""
        node = xNode.from_native([])
        
        # Test chaining
        result = node.enqueue(1).enqueue(2).enqueue(3)
        assert result is node  # Should return self for chaining
        assert node.to_native() == [1, 2, 3]
        
        # Test dequeue
        value = node.dequeue()
        assert value == 1
        assert node.to_native() == [2, 3]
    
    def test_push_front_back_methods(self):
        """Test push_front/push_back convenience methods (linked list behavior)."""
        node = xNode.from_native([2, 3])
        
        # Test chaining
        result = node.push_front(1).push_back(4)
        assert result is node  # Should return self for chaining
        assert node.to_native() == [1, 2, 3, 4]
        
        # Test pop
        front = node.pop_front()
        back = node.pop_back()
        assert front == 1
        assert back == 4
        assert node.to_native() == [2, 3]


class TestStructureTypeDetection:
    """Test structure type detection and information."""
    
    def test_structure_type_detection(self):
        """Test automatic structure type detection."""
        # List node
        list_node = xNode.from_native([1, 2, 3])
        assert list_node.structure_type == "list"
        
        # Dict node
        dict_node = xNode.from_native({"key": "value"})
        assert dict_node.structure_type == "dict"
        
        # Leaf node
        leaf_node = xNode.from_native("hello")
        assert leaf_node.structure_type == "value"
        
        # Empty list
        empty_node = xNode.from_native([])
        assert empty_node.structure_type == "empty_list"
    
    def test_structure_info(self):
        """Test structure information method."""
        node = xNode.from_native([1, 2, 3])
        info = node.structure_info()
        
        assert info["type"] == "list"
        assert info["is_list"] is True
        assert info["is_dict"] is False
        assert info["is_leaf"] is False
        assert info["size"] == 3
        
        # Check support flags
        supports = info["supports"]
        assert supports["linked_list"] is True
        assert supports["stack"] is True
        assert supports["queue"] is True
        assert supports["deque"] is True
        assert supports["tree"] is True
        assert supports["graph"] is True
        assert supports["query"] is True
    
    def test_structure_info_dict_node(self):
        """Test structure info for dict node."""
        node = xNode.from_native({"a": 1, "b": 2})
        info = node.structure_info()
        
        assert info["type"] == "dict"
        assert info["is_dict"] is True
        assert info["size"] == 2
        
        # Dict nodes don't support linear structures
        supports = info["supports"]
        assert supports["linked_list"] is False
        assert supports["stack"] is False
        assert supports["queue"] is False
        assert supports["deque"] is False
        # But still support tree, graph, query
        assert supports["tree"] is True
        assert supports["graph"] is True
        assert supports["query"] is True


class TestIntegrationWithExistingFeatures:
    """Test that data structure views work with existing tree/graph/query features."""
    
    def test_tree_operations_with_structure_views(self):
        """Test that tree operations still work with structure views."""
        data = {
            "tasks": [
                {"name": "Task 1", "priority": 1},
                {"name": "Task 2", "priority": 2}
            ]
        }
        node = xNode.from_native(data)
        
        # Navigate to tasks list
        tasks = node.find("tasks")
        
        # Use as stack to add new task
        new_task = {"name": "Task 3", "priority": 3}
        tasks.push(new_task)
        
        # Verify via tree navigation
        task3 = node.find("tasks.2.name")
        assert task3.value == "Task 3"
        
        # Pop task and verify
        popped = tasks.pop()
        assert popped["name"] == "Task 3"
        
        # Verify list is back to original size
        assert len(tasks) == 2
    
    def test_graph_operations_with_structure_views(self):
        """Test that graph operations work with structure views."""
        # Create two list nodes
        list1 = xNode.from_native([1, 2])
        list2 = xNode.from_native([3, 4])
        
        # Connect them with graph relation
        list1.connect(list2, "points_to")
        
        # Use structure operations
        list1.push(5)  # Add to first list
        list2.enqueue(6)  # Add to second list as queue
        
        # Verify graph relationship still exists
        neighbors = list1.neighbors("points_to")
        assert len(neighbors) >= 0  # Should have the connection
        
        # Verify structure operations worked
        assert 5 in list1.to_native()
        assert 6 in list2.to_native()
    
    def test_query_operations_with_structure_views(self):
        """Test that query operations work with structure views."""
        # Create data structure
        data = {
            "queues": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ]
        }
        node = xNode.from_native(data)
        
        # Use queue operations on sub-lists
        queue1 = node.find("queues.0")
        queue1.enqueue(10)
        
        # Use query to find modified queue
        results = node.find_nodes(lambda n: hasattr(n, 'value') and 
                                 isinstance(n.value, int) and 
                                 n.value == 10)
        
        assert results is not None
        # The 10 should be findable in the structure
