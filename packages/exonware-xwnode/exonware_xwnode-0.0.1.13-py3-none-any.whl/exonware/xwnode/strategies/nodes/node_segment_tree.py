"""
Segment Tree Node Strategy Implementation

This module implements the SEGMENT_TREE strategy for range queries
and updates with O(log n) complexity.
"""

from typing import Any, Iterator, List, Optional, Callable, Dict, Union
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class SegmentTreeStrategy(ANodeTreeStrategy):
    """
    Segment Tree node strategy for efficient range queries and updates.
    
    Provides O(log n) range queries and updates for associative operations
    like sum, min, max, etc.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Segment Tree strategy."""
        super().__init__(NodeMode.SEGMENT_TREE, traits, **options)
        
        self._size = options.get('initial_size', 0)
        self._operation = options.get('operation', 'sum')  # sum, min, max, etc.
        self._identity = self._get_identity(self._operation)
        self._combiner = self._get_combiner(self._operation)
        
        # Internal tree representation (0-indexed, 1-based tree)
        self._tree: List[Any] = [self._identity] * (4 * max(1, self._size))
        self._values: Dict[str, Any] = {}  # Key-value storage for compatibility
        self._indices: Dict[str, int] = {}  # Map keys to tree indices
        self._reverse_indices: Dict[int, str] = {}  # Map indices to keys
        self._next_index = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the segment tree strategy."""
        return (NodeTrait.INDEXED | NodeTrait.HIERARCHICAL | NodeTrait.STREAMING)
    
    def _get_identity(self, operation: str) -> Any:
        """Get identity element for the operation."""
        identities = {
            'sum': 0,
            'min': float('inf'),
            'max': float('-inf'),
            'product': 1,
            'gcd': 0,
            'lcm': 1,
            'xor': 0,
            'and': True,
            'or': False
        }
        return identities.get(operation, 0)
    
    def _get_combiner(self, operation: str) -> Callable[[Any, Any], Any]:
        """Get combiner function for the operation."""
        import math
        
        combiners = {
            'sum': lambda a, b: a + b,
            'min': lambda a, b: min(a, b),
            'max': lambda a, b: max(a, b),
            'product': lambda a, b: a * b,
            'gcd': lambda a, b: math.gcd(int(a), int(b)),
            'lcm': lambda a, b: abs(int(a) * int(b)) // math.gcd(int(a), int(b)),
            'xor': lambda a, b: a ^ b,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b
        }
        return combiners.get(operation, lambda a, b: a + b)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a value at the given key."""
        key_str = str(key)
        
        # Convert value to numeric if possible
        try:
            numeric_value = float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            numeric_value = 0.0
        
        if key_str in self._indices:
            # Update existing
            idx = self._indices[key_str]
            self._update_point(idx, numeric_value)
        else:
            # Add new
            if self._next_index >= len(self._tree) // 4:
                self._resize_tree()
            
            idx = self._next_index
            self._indices[key_str] = idx
            self._reverse_indices[idx] = key_str
            self._next_index += 1
            self._update_point(idx, numeric_value)
        
        self._values[key_str] = value
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        key_str = str(key)
        return self._values.get(key_str, default)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return str(key) in self._values
    
    def remove(self, key: Any) -> bool:
        """Remove value by key."""
        key_str = str(key)
        if key_str not in self._indices:
            return False
        
        idx = self._indices[key_str]
        self._update_point(idx, self._identity)
        
        del self._indices[key_str]
        del self._reverse_indices[idx]
        del self._values[key_str]
        
        return True
    
    def delete(self, key: Any) -> bool:
        """Remove value by key (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._tree = [self._identity] * (4 * max(1, self._size))
        self._values.clear()
        self._indices.clear()
        self._reverse_indices.clear()
        self._next_index = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        return iter(self._values.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        return iter(self._values.items())
    
    def __len__(self) -> int:
        """Get the number of items."""
        return len(self._values)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self._values)
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This can behave like a dict."""
        return True
    
    # ============================================================================
    # SEGMENT TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def _resize_tree(self) -> None:
        """Resize the internal tree when needed."""
        old_size = len(self._tree)
        new_size = old_size * 2
        self._tree.extend([self._identity] * (new_size - old_size))
    
    def _update_point(self, idx: int, value: Any) -> None:
        """Update a single point in the segment tree."""
        # Convert to 1-based indexing for tree
        tree_idx = idx + len(self._tree) // 4
        
        # Ensure tree is large enough
        while tree_idx >= len(self._tree):
            self._resize_tree()
            tree_idx = idx + len(self._tree) // 4
        
        # Update leaf
        self._tree[tree_idx] = value
        
        # Update ancestors
        while tree_idx > 1:
            tree_idx //= 2
            left_child = self._tree[tree_idx * 2] if tree_idx * 2 < len(self._tree) else self._identity
            right_child = self._tree[tree_idx * 2 + 1] if tree_idx * 2 + 1 < len(self._tree) else self._identity
            self._tree[tree_idx] = self._combiner(left_child, right_child)
    
    def range_query(self, left: int, right: int) -> Any:
        """Query range [left, right] inclusive."""
        return self._range_query_recursive(1, 0, len(self._tree) // 4 - 1, left, right)
    
    def _range_query_recursive(self, node: int, start: int, end: int, 
                              query_left: int, query_right: int) -> Any:
        """Recursive range query implementation."""
        if query_right < start or query_left > end:
            return self._identity
        
        if query_left <= start and end <= query_right:
            return self._tree[node] if node < len(self._tree) else self._identity
        
        mid = (start + end) // 2
        left_result = self._range_query_recursive(2 * node, start, mid, query_left, query_right)
        right_result = self._range_query_recursive(2 * node + 1, mid + 1, end, query_left, query_right)
        
        return self._combiner(left_result, right_result)
    
    def range_update(self, left: int, right: int, value: Any) -> None:
        """Update range [left, right] with value (point updates)."""
        for i in range(left, right + 1):
            if i in self._reverse_indices:
                key = self._reverse_indices[i]
                self.put(key, value)
    
    def prefix_query(self, index: int) -> Any:
        """Query prefix [0, index]."""
        return self.range_query(0, index)
    
    def suffix_query(self, index: int) -> Any:
        """Query suffix [index, size-1]."""
        return self.range_query(index, len(self._values) - 1)
    
    def find_first_greater(self, value: Any) -> Optional[int]:
        """Find first index where tree value > given value."""
        for i in range(len(self._values)):
            if i in self._reverse_indices:
                key = self._reverse_indices[i]
                if key in self._values:
                    try:
                        if float(self._values[key]) > float(value):
                            return i
                    except (ValueError, TypeError):
                        continue
        return None
    
    def get_operation_info(self) -> Dict[str, Any]:
        """Get information about the current operation."""
        return {
            'operation': self._operation,
            'identity': self._identity,
            'total_result': self.range_query(0, max(0, len(self._values) - 1))
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'SEGMENT_TREE',
            'backend': 'Array-based segment tree',
            'operation': self._operation,
            'complexity': {
                'point_update': 'O(log n)',
                'range_query': 'O(log n)',
                'range_update': 'O(n log n)',
                'build': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        tree_height = 0
        if len(self._values) > 0:
            import math
            tree_height = math.ceil(math.log2(len(self._values)))
        
        return {
            'size': len(self._values),
            'tree_size': len(self._tree),
            'tree_height': tree_height,
            'operation': self._operation,
            'memory_usage': f"{len(self._tree) * 8 + len(self._values) * 24} bytes (estimated)",
            'utilization': f"{len(self._values) / max(1, len(self._tree) // 4) * 100:.1f}%"
        }
