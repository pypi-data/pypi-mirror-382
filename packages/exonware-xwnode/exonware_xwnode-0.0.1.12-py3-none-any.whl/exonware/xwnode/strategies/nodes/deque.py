"""
Deque Strategy Implementation

Implements a double-ended queue using Python's deque for efficient operations at both ends.

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


class DequeStrategy(ANodeLinearStrategy):
    """
    Deque (Double-ended queue) node strategy for efficient operations at both ends.
    
    Provides O(1) operations for adding/removing elements at both front and back,
    ideal for sliding window algorithms and breadth-first search.
    """
    
    def __init__(self):
        """Initialize an empty deque."""
        super().__init__()
        self._deque: deque = deque()
        self._mode = NodeMode.DEQUE
        self._traits = {NodeTrait.DOUBLE_ENDED, NodeTrait.FAST_INSERT, NodeTrait.FAST_DELETE}
    
    def insert(self, key: str, value: Any) -> None:
        """Insert an item (defaults to back)."""
        self._deque.append((key, value))
    
    def find(self, key: str) -> Optional[Any]:
        """Find an item in the deque (O(n) operation)."""
        for k, v in self._deque:
            if k == key:
                return v
        return None
    
    def delete(self, key: str) -> bool:
        """Remove an item from the deque."""
        for i, (k, v) in enumerate(self._deque):
            if k == key:
                del self._deque[i]
                return True
        return False
    
    def size(self) -> int:
        """Get the number of items in the deque."""
        return len(self._deque)
    
    def is_empty(self) -> bool:
        """Check if the deque is empty."""
        return len(self._deque) == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert deque to native dictionary format."""
        return dict(self._deque)
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load deque from native dictionary format."""
        self._deque = deque(data.items())
    
    def append(self, value: Any) -> None:
        """Add an item to the right end."""
        key = f"item_{len(self._deque)}"
        self._deque.append((key, value))
    
    def appendleft(self, value: Any) -> None:
        """Add an item to the left end."""
        key = f"item_{len(self._deque)}"
        self._deque.appendleft((key, value))
    
    def pop(self) -> Optional[Any]:
        """Remove and return an item from the right end."""
        if self.is_empty():
            return None
        key, value = self._deque.pop()
        return value
    
    def popleft(self) -> Optional[Any]:
        """Remove and return an item from the left end."""
        if self.is_empty():
            return None
        key, value = self._deque.popleft()
        return value
    
    def peek_right(self) -> Optional[Any]:
        """Peek at the rightmost item without removing it."""
        if self.is_empty():
            return None
        key, value = self._deque[-1]
        return value
    
    def peek_left(self) -> Optional[Any]:
        """Peek at the leftmost item without removing it."""
        if self.is_empty():
            return None
        key, value = self._deque[0]
        return value
    
    def rotate(self, n: int = 1) -> None:
        """Rotate the deque n steps to the right (positive) or left (negative)."""
        self._deque.rotate(n)
    
    def reverse(self) -> None:
        """Reverse the deque in place."""
        self._deque.reverse()
    
    def clear(self) -> None:
        """Clear all items from the deque."""
        self._deque.clear()
    
    def get_at_index(self, index: int) -> Optional[Any]:
        """Get item at specific index."""
        if 0 <= index < len(self._deque):
            key, value = self._deque[index]
            return value
        return None
    
    def set_at_index(self, index: int, value: Any) -> bool:
        """Set item at specific index."""
        if 0 <= index < len(self._deque):
            key, old_value = self._deque[index]
            self._deque[index] = (key, value)
            return True
        return False
    
    def push_front(self, value: Any) -> None:
        """Push to front (left end)."""
        self.appendleft(value)
    
    def push_back(self, value: Any) -> None:
        """Push to back (right end)."""
        self.append(value)
    
    def remove(self, value: Any) -> bool:
        """Remove the first occurrence of a value."""
        for i, (key, v) in enumerate(self._deque):
            if v == value:
                del self._deque[i]
                return True
        return False
    
    def count(self, value: Any) -> int:
        """Count occurrences of a value."""
        count = 0
        for key, v in self._deque:
            if v == value:
                count += 1
        return count
    
    def extend(self, values: list) -> None:
        """Extend the deque with values from the right."""
        for value in values:
            self.append(value)
    
    def extendleft(self, values: list) -> None:
        """Extend the deque with values from the left."""
        for value in reversed(values):
            self.appendleft(value)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through deque items (left to right)."""
        for key, value in self._deque:
            yield value
    
    def __repr__(self) -> str:
        """String representation of the deque."""
        return f"DequeStrategy(size={len(self._deque)}, left={self.peek_left()}, right={self.peek_right()})"
    
    # Required abstract methods from base classes
    def pop_front(self) -> Any:
        """Remove element from front (same as popleft for deque)."""
        return self.popleft()
    
    def pop_back(self) -> Any:
        """Remove element from back (same as pop for deque)."""
        return self.pop()
    
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        return self
    
    def as_stack(self):
        """Provide Stack behavioral view."""
        return self
    
    def as_queue(self):
        """Provide Queue behavioral view."""
        return self
    
    def as_deque(self):
        """Provide Deque behavioral view."""
        return self
