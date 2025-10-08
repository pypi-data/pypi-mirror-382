"""
Array List Node Strategy Implementation

This module implements the ARRAY_LIST strategy for sequential data
with fast indexed access.
"""

from typing import Any, Iterator, List, Union, Dict
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class xArrayListStrategy(aNodeStrategy):
    """
    Array List node strategy for sequential data with O(1) indexed access.
    
    Uses Python's built-in list for optimal performance with indexed operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the array list strategy."""
        super().__init__(NodeMode.ARRAY_LIST, traits, **options)
        self._data: List[Any] = []
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the array list strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a value at index (key must be numeric)."""
        try:
            index = int(key)
        except (ValueError, TypeError):
            raise TypeError(f"Array list requires numeric indices, got {type(key).__name__}")
        
        # Extend list if necessary
        while len(self._data) <= index:
            self._data.append(None)
            
        if self._data[index] is None:
            self._size += 1
        self._data[index] = value
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by index."""
        try:
            index = int(key)
            if 0 <= index < len(self._data):
                value = self._data[index]
                return value if value is not None else default
            return default
        except (ValueError, TypeError):
            return default
    
    def has(self, key: Any) -> bool:
        """Check if index exists and has a value."""
        try:
            index = int(key)
            return 0 <= index < len(self._data) and self._data[index] is not None
        except (ValueError, TypeError):
            return False
    
    def remove(self, key: Any) -> bool:
        """Remove value at index."""
        try:
            index = int(key)
            if 0 <= index < len(self._data) and self._data[index] is not None:
                self._data[index] = None
                self._size -= 1
                return True
            return False
        except (ValueError, TypeError):
            return False
    
    def delete(self, key: Any) -> bool:
        """Remove value at index (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all valid indices as strings."""
        return (str(i) for i, value in enumerate(self._data) if value is not None)
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return (value for value in self._data if value is not None)
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all index-value pairs."""
        return ((str(i), value) for i, value in enumerate(self._data) if value is not None)
    
    def __len__(self) -> int:
        """Get the number of non-None items."""
        return self._size
    
    def to_native(self) -> List[Any]:
        """Convert to native Python list."""
        # Return only non-None values in order
        return [value for value in self._data if value is not None]
    
    @property
    def is_list(self) -> bool:
        """This is always a list strategy."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This is never a dict strategy."""
        return False
    
    # ============================================================================
    # ARRAY-SPECIFIC OPERATIONS
    # ============================================================================
    
    def append(self, value: Any) -> None:
        """Append a value to the end."""
        self._data.append(value)
        self._size += 1
    
    def insert(self, index: int, value: Any) -> None:
        """Insert a value at the specified index."""
        self._data.insert(index, value)
        self._size += 1
    
    def pop(self, index: int = -1) -> Any:
        """Remove and return value at index."""
        if not self._data:
            raise IndexError("pop from empty list")
        value = self._data.pop(index)
        if value is not None:
            self._size -= 1
        return value
    
    def extend(self, values: List[Any]) -> None:
        """Extend with multiple values."""
        self._data.extend(values)
        self._size += len(values)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ARRAY_LIST',
            'backend': 'Python list',
            'complexity': {
                'get': 'O(1)',
                'put': 'O(1) amortized',
                'append': 'O(1) amortized',
                'insert': 'O(n)',
                'pop': 'O(1) end, O(n) middle'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': self._size,
            'capacity': len(self._data),
            'memory_usage': f"{len(self._data) * 8} bytes (estimated)",
            'utilization': f"{(self._size / max(1, len(self._data))) * 100:.1f}%"
        }
