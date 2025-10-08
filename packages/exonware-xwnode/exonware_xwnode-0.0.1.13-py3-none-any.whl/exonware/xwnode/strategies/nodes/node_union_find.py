"""
Union-Find Node Strategy Implementation

This module implements the UNION_FIND strategy for efficient set operations.
"""

from typing import Any, Iterator, Dict, List, Set
from .base import ANodeGraphStrategy
from ...types import NodeMode, NodeTrait
from ..utils import (
    UnionFind,
    safe_to_native_conversion,
    create_basic_metrics,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class UnionFindStrategy(ANodeGraphStrategy):
    """
    Union-Find node strategy for efficient set operations.
    
    Optimized for union, find, and connected operations on disjoint sets.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the union-find strategy."""
        super().__init__(NodeMode.UNION_FIND, traits, **options)
        self._union_find = UnionFind()
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the union-find strategy."""
        return (NodeTrait.SET_OPERATIONS | NodeTrait.HIERARCHICAL)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair (creates a new set)."""
        str_key = str(key)
        if str_key not in self._union_find.parent:
            update_size_tracker(self._size_tracker, 1)
        self._union_find.make_set(str_key, value)
        record_access(self._access_tracker, 'put_count')
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        str_key = str(key)
        record_access(self._access_tracker, 'get_count')
        return self._union_find.values.get(str_key, default)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return str(key) in self._union_find.parent
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair."""
        str_key = str(key)
        if str_key in self._union_find.parent:
            # Remove from all data structures
            del self._union_find.parent[str_key]
            if str_key in self._union_find.rank:
                del self._union_find.rank[str_key]
            if str_key in self._union_find.values:
                del self._union_find.values[str_key]
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            return True
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._union_find = UnionFind()
        self._size_tracker['size'] = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        return iter(self._union_find.parent.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._union_find.values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        return iter(self._union_find.values.items())
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self._size_tracker['size']
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict with set structure info."""
        result = {}
        for key in self._union_find.parent.keys():
            result[key] = {
                'value': safe_to_native_conversion(self._union_find.values.get(key)),
                'root': self._union_find.find(key),
                'set_id': self._union_find.find(key)
            }
        return result
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict but with set semantics."""
        return True
    
    # ============================================================================
    # UNION-FIND SPECIFIC OPERATIONS
    # ============================================================================
    
    def make_set(self, element: str, value: Any = None) -> None:
        """Create a new set containing only the given element."""
        if element not in self._union_find.parent:
            update_size_tracker(self._size_tracker, 1)
        self._union_find.make_set(element, value)
    
    def find(self, element: str) -> str:
        """Find the root of the set containing element (with path compression)."""
        return self._union_find.find(element)
    
    def union(self, element1: str, element2: str) -> bool:
        """Union the sets containing element1 and element2."""
        return self._union_find.union(element1, element2)
    
    def connected(self, element1: str, element2: str) -> bool:
        """Check if two elements are in the same set."""
        return self._union_find.connected(element1, element2)
    
    def get_set_members(self, element: str) -> Set[str]:
        """Get all members of the set containing the given element."""
        return self._union_find.get_set_members(element)
    
    def get_all_sets(self) -> List[Set[str]]:
        """Get all disjoint sets."""
        return self._union_find.get_all_sets()
    
    def get_set_count(self) -> int:
        """Get the number of disjoint sets."""
        return self._union_find.get_set_count()
    
    def get_set_size(self, element: str) -> int:
        """Get the size of the set containing the given element."""
        return self._union_find.get_set_size(element)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return create_basic_backend_info(
            'UNION_FIND',
            'UnionFind with path compression and union by rank',
            complexity={
                'find': 'O(α(n)) amortized where α is inverse Ackermann',
                'union': 'O(α(n)) amortized where α is inverse Ackermann',
                'connected': 'O(α(n)) amortized where α is inverse Ackermann'
            }
        )
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        base_metrics = create_basic_metrics('UNION_FIND', self._size_tracker['size'])
        access_metrics = get_access_metrics(self._access_tracker)
        base_metrics.update(access_metrics)
        base_metrics.update({
            'set_count': self._union_find.get_set_count(),
            'avg_set_size': self._size_tracker['size'] / max(1, self._union_find.get_set_count())
        })
        return base_metrics
