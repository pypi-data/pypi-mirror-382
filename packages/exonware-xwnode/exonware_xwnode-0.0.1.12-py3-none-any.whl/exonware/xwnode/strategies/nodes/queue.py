"""
Queue Strategy Implementation

Implements a FIFO (First In, First Out) data structure using Python's deque.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

from typing import Any, Iterator, Optional, Dict, Union
from collections import deque
from .base import ANodeLinearStrategy
from ...types import NodeMode, NodeTrait


class QueueStrategy(ANodeLinearStrategy):
    """
    Queue node strategy for FIFO (First In, First Out) operations.
    
    Provides O(1) enqueue and dequeue operations with efficient memory usage
    for queue-based algorithms and breadth-first search.
    """
    
    def __init__(self):
        """Initialize an empty queue."""
        super().__init__()
        self._queue: deque = deque()
        self._mode = NodeMode.QUEUE
        self._traits = {NodeTrait.FIFO, NodeTrait.FAST_INSERT, NodeTrait.FAST_DELETE}
    
    def insert(self, key: str, value: Any) -> None:
        """Enqueue an item into the queue."""
        self._queue.append((key, value))
        self._record_access("enqueue")
    
    def find(self, key: str) -> Optional[Any]:
        """Find an item in the queue (O(n) operation)."""
        for k, v in self._queue:
            if k == key:
                self._record_access("find")
                return v
        return None
    
    def delete(self, key: str) -> bool:
        """Remove an item from the queue."""
        for i, (k, v) in enumerate(self._queue):
            if k == key:
                del self._queue[i]
                self._record_access("delete")
                return True
        return False
    
    def size(self) -> int:
        """Get the number of items in the queue."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert queue to native dictionary format."""
        return dict(self._queue)
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load queue from native dictionary format."""
        self._queue = deque(data.items())
    
    def enqueue(self, value: Any) -> None:
        """Enqueue a value into the queue."""
        key = f"item_{len(self._queue)}"
        self.insert(key, value)
    
    def dequeue(self) -> Optional[Any]:
        """Dequeue and return the front item from the queue."""
        if self.is_empty():
            return None
        key, value = self._queue.popleft()
        self._record_access("dequeue")
        return value
    
    def front(self) -> Optional[Any]:
        """Get the front item without removing it."""
        if self.is_empty():
            return None
        key, value = self._queue[0]
        self._record_access("front")
        return value
    
    def back(self) -> Optional[Any]:
        """Get the back item without removing it."""
        if self.is_empty():
            return None
        key, value = self._queue[-1]
        self._record_access("back")
        return value
    
    def clear(self) -> None:
        """Clear all items from the queue."""
        self._queue.clear()
        self._record_access("clear")
    
    def get_at_index(self, index: int) -> Optional[Any]:
        """Get item at specific index (0 = front of queue)."""
        if 0 <= index < len(self._queue):
            key, value = self._queue[index]
            self._record_access("get_at_index")
            return value
        return None
    
    def push_front(self, value: Any) -> None:
        """Push to front of queue."""
        self._queue.appendleft((f"item_{len(self._queue)}", value))
        self._record_access("push_front")
    
    def push_back(self, value: Any) -> None:
        """Push to back of queue."""
        self.enqueue(value)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through queue items (front to back)."""
        for key, value in self._queue:
            yield value
    
    def __repr__(self) -> str:
        """String representation of the queue."""
        return f"QueueStrategy(size={len(self._queue)}, front={self.front()})"
    
    # Required abstract methods from base classes
    def pop_front(self) -> Any:
        """Remove element from front (same as dequeue for queue)."""
        return self.dequeue()
    
    def pop_back(self) -> Any:
        """Remove element from back (not applicable for queue)."""
        raise NotImplementedError("Queue doesn't support pop_back")
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index (not recommended for queue)."""
        if 0 <= index < len(self._queue):
            key, old_value = self._queue[index]
            self._queue[index] = (key, value)
    
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        return self
    
    def as_stack(self):
        """Provide Stack behavioral view (not recommended)."""
        raise NotImplementedError("Queue cannot behave as Stack")
    
    def as_queue(self):
        """Provide Queue behavioral view."""
        return self
    
    def as_deque(self):
        """Provide Deque behavioral view."""
        return self
