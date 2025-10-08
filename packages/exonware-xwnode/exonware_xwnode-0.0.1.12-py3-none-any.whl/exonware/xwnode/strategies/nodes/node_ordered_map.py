"""
Ordered Map Node Strategy Implementation

This module implements the ORDERED_MAP strategy for sorted key-value
operations with efficient range queries and ordered iteration.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
import bisect
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class OrderedMapStrategy(ANodeTreeStrategy):
    """
    Ordered Map node strategy for sorted key-value operations.
    
    Maintains keys in sorted order for efficient range queries,
    ordered iteration, and logarithmic search operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Ordered Map strategy."""
        super().__init__(NodeMode.ORDERED_MAP, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.allow_duplicates = options.get('allow_duplicates', False)
        
        # Core storage: parallel sorted arrays
        self._keys: List[str] = []
        self._values: List[Any] = []
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the ordered map strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _find_key_position(self, key: str) -> int:
        """Find position where key should be inserted (or exists)."""
        normalized_key = self._normalize_key(key)
        return bisect.bisect_left(self._keys, normalized_key)
    
    def _insert_at_position(self, position: int, key: str, value: Any) -> None:
        """Insert key-value pair at specific position."""
        normalized_key = self._normalize_key(key)
        self._keys.insert(position, normalized_key)
        self._values.insert(position, value)
        self._size += 1
    
    def _remove_at_position(self, position: int) -> Any:
        """Remove key-value pair at specific position."""
        if 0 <= position < self._size:
            self._keys.pop(position)
            value = self._values.pop(position)
            self._size -= 1
            return value
        return None
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add/update key-value pair in sorted order."""
        key_str = str(key)
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        
        # Check if key already exists
        if (position < self._size and 
            self._keys[position] == normalized_key):
            if not self.allow_duplicates:
                # Update existing key
                self._values[position] = value
                return
        
        # Insert new key-value pair
        self._insert_at_position(position, key_str, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "sorted_keys":
            return self._keys.copy()
        elif key_str == "sorted_values":
            return self._values.copy()
        elif key_str == "map_info":
            return {
                'size': self._size,
                'case_sensitive': self.case_sensitive,
                'allow_duplicates': self.allow_duplicates,
                'first_key': self.first_key(),
                'last_key': self.last_key()
            }
        elif key_str.isdigit():
            # Numeric access by index
            index = int(key_str)
            if 0 <= index < self._size:
                return self._values[index]
            return default
        
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        
        if (position < self._size and 
            self._keys[position] == normalized_key):
            return self._values[position]
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        
        if key_str in ["sorted_keys", "sorted_values", "map_info"]:
            return True
        elif key_str.isdigit():
            index = int(key_str)
            return 0 <= index < self._size
        
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        
        return (position < self._size and 
                self._keys[position] == normalized_key)
    
    def remove(self, key: Any) -> bool:
        """Remove key from map."""
        key_str = str(key)
        
        if key_str.isdigit():
            # Remove by index
            index = int(key_str)
            if 0 <= index < self._size:
                self._remove_at_position(index)
                return True
            return False
        
        normalized_key = self._normalize_key(key_str)
        position = self._find_key_position(key_str)
        
        if (position < self._size and 
            self._keys[position] == normalized_key):
            self._remove_at_position(position)
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key from map (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._keys.clear()
        self._values.clear()
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys in sorted order."""
        for key in self._keys:
            yield key
    
    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        for value in self._values:
            yield value
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        for key, value in zip(self._keys, self._values):
            yield (key, value)
    
    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict (preserves insertion order in Python 3.7+)."""
        return dict(zip(self._keys, self._values))
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for indexed access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This is a dict-like structure."""
        return True
    
    # ============================================================================
    # ORDERED MAP SPECIFIC OPERATIONS
    # ============================================================================
    
    def first_key(self) -> Optional[str]:
        """Get first (smallest) key."""
        return self._keys[0] if self._size > 0 else None
    
    def last_key(self) -> Optional[str]:
        """Get last (largest) key."""
        return self._keys[-1] if self._size > 0 else None
    
    def first_value(self) -> Any:
        """Get value of first key."""
        return self._values[0] if self._size > 0 else None
    
    def last_value(self) -> Any:
        """Get value of last key."""
        return self._values[-1] if self._size > 0 else None
    
    def get_range(self, start_key: str, end_key: str, inclusive: bool = True) -> List[Tuple[str, Any]]:
        """Get key-value pairs in range [start_key, end_key]."""
        start_norm = self._normalize_key(start_key)
        end_norm = self._normalize_key(end_key)
        
        result = []
        for key, value in zip(self._keys, self._values):
            if inclusive:
                if start_norm <= key <= end_norm:
                    result.append((key, value))
            else:
                if start_norm < key < end_norm:
                    result.append((key, value))
        
        return result
    
    def get_keys_range(self, start_key: str, end_key: str, inclusive: bool = True) -> List[str]:
        """Get keys in range."""
        range_items = self.get_range(start_key, end_key, inclusive)
        return [key for key, _ in range_items]
    
    def get_values_range(self, start_key: str, end_key: str, inclusive: bool = True) -> List[Any]:
        """Get values in key range."""
        range_items = self.get_range(start_key, end_key, inclusive)
        return [value for _, value in range_items]
    
    def lower_bound(self, key: str) -> Optional[str]:
        """Find first key >= given key."""
        normalized_key = self._normalize_key(key)
        position = bisect.bisect_left(self._keys, normalized_key)
        
        return self._keys[position] if position < self._size else None
    
    def upper_bound(self, key: str) -> Optional[str]:
        """Find first key > given key."""
        normalized_key = self._normalize_key(key)
        position = bisect.bisect_right(self._keys, normalized_key)
        
        return self._keys[position] if position < self._size else None
    
    def floor(self, key: str) -> Optional[str]:
        """Find largest key <= given key."""
        normalized_key = self._normalize_key(key)
        position = bisect.bisect_right(self._keys, normalized_key) - 1
        
        return self._keys[position] if position >= 0 else None
    
    def ceiling(self, key: str) -> Optional[str]:
        """Find smallest key >= given key."""
        return self.lower_bound(key)
    
    def get_at_index(self, index: int) -> Optional[Tuple[str, Any]]:
        """Get key-value pair at specific index."""
        if 0 <= index < self._size:
            return (self._keys[index], self._values[index])
        return None
    
    def index_of(self, key: str) -> int:
        """Get index of key (-1 if not found)."""
        normalized_key = self._normalize_key(key)
        position = self._find_key_position(key)
        
        if (position < self._size and 
            self._keys[position] == normalized_key):
            return position
        
        return -1
    
    def pop_first(self) -> Optional[Tuple[str, Any]]:
        """Remove and return first key-value pair."""
        if self._size > 0:
            key = self._keys[0]
            value = self._remove_at_position(0)
            return (key, value)
        return None
    
    def pop_last(self) -> Optional[Tuple[str, Any]]:
        """Remove and return last key-value pair."""
        if self._size > 0:
            key = self._keys[-1]
            value = self._remove_at_position(self._size - 1)
            return (key, value)
        return None
    
    def reverse_keys(self) -> Iterator[str]:
        """Get keys in reverse order."""
        for i in range(self._size - 1, -1, -1):
            yield self._keys[i]
    
    def reverse_values(self) -> Iterator[Any]:
        """Get values in reverse key order."""
        for i in range(self._size - 1, -1, -1):
            yield self._values[i]
    
    def reverse_items(self) -> Iterator[Tuple[str, Any]]:
        """Get key-value pairs in reverse order."""
        for i in range(self._size - 1, -1, -1):
            yield (self._keys[i], self._values[i])
    
    def find_prefix_keys(self, prefix: str) -> List[str]:
        """Find all keys starting with given prefix."""
        normalized_prefix = self._normalize_key(prefix)
        result = []
        
        for key in self._keys:
            if key.startswith(normalized_prefix):
                result.append(key)
            elif key > normalized_prefix and not key.startswith(normalized_prefix):
                break  # Keys are sorted, no more matches possible
        
        return result
    
    def count_range(self, start_key: str, end_key: str, inclusive: bool = True) -> int:
        """Count keys in range."""
        return len(self.get_keys_range(start_key, end_key, inclusive))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ordered map statistics."""
        if self._size == 0:
            return {'size': 0, 'first_key': None, 'last_key': None}
        
        # Calculate key length statistics
        key_lengths = [len(key) for key in self._keys]
        avg_key_length = sum(key_lengths) / len(key_lengths)
        min_key_length = min(key_lengths)
        max_key_length = max(key_lengths)
        
        return {
            'size': self._size,
            'first_key': self.first_key(),
            'last_key': self.last_key(),
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates,
            'avg_key_length': avg_key_length,
            'min_key_length': min_key_length,
            'max_key_length': max_key_length,
            'memory_usage': self._size * 50  # Estimated
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ORDERED_MAP',
            'backend': 'Parallel sorted arrays with binary search',
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates,
            'complexity': {
                'put': 'O(n)',  # Due to array insertion
                'get': 'O(log n)',  # Binary search
                'remove': 'O(n)',  # Due to array removal
                'range_query': 'O(log n + k)',  # k = result size
                'iteration': 'O(n)',
                'space': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        
        return {
            'size': stats['size'],
            'first_key': str(stats['first_key']) if stats['first_key'] else 'None',
            'last_key': str(stats['last_key']) if stats['last_key'] else 'None',
            'avg_key_length': f"{stats['avg_key_length']:.1f}" if stats.get('avg_key_length') else '0',
            'case_sensitive': stats['case_sensitive'],
            'memory_usage': f"{stats['memory_usage']} bytes (estimated)"
        }
