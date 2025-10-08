"""
Priority Queue Strategy Implementation

Implements a priority queue using Python's heapq for efficient priority-based operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

from typing import Any, Iterator, Optional, Dict, Union, Tuple
import heapq
from .base import ANodeLinearStrategy
from ...types import NodeMode, NodeTrait


class PriorityQueueStrategy(ANodeLinearStrategy):
    """
    Priority Queue node strategy for priority-based operations.
    
    Uses a binary heap for efficient insertion and extraction of
    highest priority elements, ideal for algorithms like Dijkstra's.
    """
    
    def __init__(self):
        """Initialize an empty priority queue."""
        super().__init__()
        self._heap: List[Tuple[float, int, str, Any]] = []  # (priority, counter, key, value)
        self._counter = 0  # For stable sorting
        self._mode = NodeMode.PRIORITY_QUEUE
        self._traits = {NodeTrait.PRIORITY, NodeTrait.FAST_INSERT, NodeTrait.FAST_DELETE}
    
    def insert(self, key: str, value: Any) -> None:
        """Insert an item with default priority (0)."""
        self.insert_with_priority(key, value, 0.0)
    
    def find(self, key: str) -> Optional[Any]:
        """Find an item in the priority queue (O(n) operation)."""
        for priority, counter, k, v in self._heap:
            if k == key:
                return v
        return None
    
    def delete(self, key: str) -> bool:
        """Remove an item from the priority queue."""
        for i, (priority, counter, k, v) in enumerate(self._heap):
            if k == key:
                self._heap.pop(i)
                heapq.heapify(self._heap)  # Re-heapify after removal
                return True
        return False
    
    def size(self) -> int:
        """Get the number of items in the priority queue."""
        return len(self._heap)
    
    def is_empty(self) -> bool:
        """Check if the priority queue is empty."""
        return len(self._heap) == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert priority queue to native dictionary format."""
        result = {}
        for priority, counter, key, value in self._heap:
            result[key] = value
        return result
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load priority queue from native dictionary format."""
        self._heap.clear()
        for key, value in data.items():
            self.insert(key, value)
    
    def insert_with_priority(self, key: str, value: Any, priority: float) -> None:
        """Insert an item with specific priority."""
        heapq.heappush(self._heap, (priority, self._counter, key, value))
        self._counter += 1
    
    def extract_min(self) -> Optional[Tuple[str, Any, float]]:
        """Extract item with minimum priority."""
        if self.is_empty():
            return None
        
        priority, counter, key, value = heapq.heappop(self._heap)
        return (key, value, priority)
    
    def extract_max(self) -> Optional[Tuple[str, Any, float]]:
        """Extract item with maximum priority."""
        if self.is_empty():
            return None
        
        # Convert to max-heap by negating priorities
        max_heap = [(-priority, counter, key, value) for priority, counter, key, value in self._heap]
        heapq.heapify(max_heap)
        
        neg_priority, counter, key, value = heapq.heappop(max_heap)
        priority = -neg_priority
        
        # Remove from original heap
        for i, (p, c, k, v) in enumerate(self._heap):
            if k == key and c == counter:
                self._heap.pop(i)
                break
        
        return (key, value, priority)
    
    def peek_min(self) -> Optional[Tuple[str, Any, float]]:
        """Peek at item with minimum priority without removing it."""
        if self.is_empty():
            return None
        
        priority, counter, key, value = self._heap[0]
        return (key, value, priority)
    
    def peek_max(self) -> Optional[Tuple[str, Any, float]]:
        """Peek at item with maximum priority without removing it."""
        if self.is_empty():
            return None
        
        max_item = None
        for priority, counter, key, value in self._heap:
            if max_item is None or priority > max_item[2]:
                max_item = (key, value, priority)
        
        return max_item
    
    def update_priority(self, key: str, new_priority: float) -> bool:
        """Update the priority of an existing item."""
        for i, (priority, counter, k, v) in enumerate(self._heap):
            if k == key:
                self._heap[i] = (new_priority, counter, k, v)
                heapq.heapify(self._heap)  # Re-heapify after update
                return True
        return False
    
    def get_priority(self, key: str) -> Optional[float]:
        """Get the priority of an item."""
        for priority, counter, k, v in self._heap:
            if k == key:
                return priority
        return None
    
    def clear(self) -> None:
        """Clear all items from the priority queue."""
        self._heap.clear()
        self._counter = 0
    
    def get_at_index(self, index: int) -> Optional[Any]:
        """Get item at specific index (not recommended for priority queue)."""
        if 0 <= index < len(self._heap):
            priority, counter, key, value = self._heap[index]
            return value
        return None
    
    def push_front(self, value: Any) -> None:
        """Push to front with high priority."""
        key = f"item_{len(self._heap)}"
        self.insert_with_priority(key, value, float('inf'))
    
    def push_back(self, value: Any) -> None:
        """Push to back with low priority."""
        key = f"item_{len(self._heap)}"
        self.insert_with_priority(key, value, float('-inf'))
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through items (order not guaranteed)."""
        for priority, counter, key, value in self._heap:
            yield value
    
    def __repr__(self) -> str:
        """String representation of the priority queue."""
        min_item = self.peek_min()
        max_item = self.peek_max()
        return f"PriorityQueueStrategy(size={len(self._heap)}, min={min_item[2] if min_item else None}, max={max_item[2] if max_item else None})"
    
    # Required abstract methods from base classes
    def pop_front(self) -> Any:
        """Remove element from front (same as extract_min for priority queue)."""
        result = self.extract_min()
        return result[1] if result else None
    
    def pop_back(self) -> Any:
        """Remove element from back (same as extract_max for priority queue)."""
        result = self.extract_max()
        return result[1] if result else None
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index (not recommended for priority queue)."""
        if 0 <= index < len(self._heap):
            priority, counter, key, old_value = self._heap[index]
            self._heap[index] = (priority, counter, key, value)
    
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        return self
    
    def as_stack(self):
        """Provide Stack behavioral view (not recommended)."""
        raise NotImplementedError("PriorityQueue cannot behave as Stack")
    
    def as_queue(self):
        """Provide Queue behavioral view (not recommended)."""
        raise NotImplementedError("PriorityQueue cannot behave as Queue")
    
    def as_deque(self):
        """Provide Deque behavioral view (not recommended)."""
        raise NotImplementedError("PriorityQueue cannot behave as Deque")
