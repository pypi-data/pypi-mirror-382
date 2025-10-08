"""
Union-Find Node Strategy Implementation

This module implements the UNION_FIND strategy for efficient set operations.
"""

from typing import Any, Iterator, Dict, List, Set
from .base import ANodeGraphStrategy
from ...types import NodeMode, NodeTrait


class UnionFind:
    """Union-Find data structure."""
    
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
        self.values: Dict[str, Any] = {}
    
    def make_set(self, x: str, value: Any = None) -> None:
        """Make a new set containing x."""
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.values[x] = value
    
    def find(self, x: str) -> str:
        """Find the root of the set containing x."""
        if x not in self.parent:
            return x
        
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x: str, y: str) -> bool:
        """Union the sets containing x and y."""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # Already in same set
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True
    
    def connected(self, x: str, y: str) -> bool:
        """Check if x and y are in the same set."""
        return self.find(x) == self.find(y)
    
    def get_set_members(self, x: str) -> Set[str]:
        """Get all members of the set containing x."""
        root = self.find(x)
        return {member for member in self.parent.keys() if self.find(member) == root}
    
    def get_all_sets(self) -> List[Set[str]]:
        """Get all disjoint sets."""
        roots = set(self.find(x) for x in self.parent.keys())
        return [self.get_set_members(root) for root in roots]
    
    def get_set_count(self) -> int:
        """Get the number of disjoint sets."""
        roots = set(self.find(x) for x in self.parent.keys())
        return len(roots)
    
    def get_set_size(self, x: str) -> int:
        """Get the size of the set containing x."""
        return len(self.get_set_members(x))


class xUnionFindStrategy(ANodeGraphStrategy):
    """
    Union-Find node strategy for efficient set operations.
    
    Optimized for union, find, and connected operations on disjoint sets.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the union-find strategy."""
        super().__init__(data=None, **options)
        self._mode = NodeMode.UNION_FIND
        self._traits = traits
        self._union_find = UnionFind()
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the union-find strategy."""
        return (NodeTrait.SET_OPERATIONS | NodeTrait.HIERARCHICAL)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """Store a key-value pair (creates a new set)."""
        str_key = str(key)
        if str_key not in self._union_find.parent:
            self._size += 1
        self._union_find.make_set(str_key, value)
    
    def find(self, key: Any) -> Any:
        """Find the root of the set containing key."""
        str_key = str(key)
        root = self._union_find.find(str_key)
        return self._union_find.values.get(root)
    
    def delete(self, key: Any) -> bool:
        """Delete a key (not supported in union-find)."""
        # Union-Find doesn't support deletion efficiently
        return False
    
    def size(self) -> int:
        """Get the number of elements."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if the structure is empty."""
        return self._size == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        return self._union_find.values.copy()
    
    # ============================================================================
    # GRAPH STRATEGY METHODS
    # ============================================================================
    
    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Add edge between nodes (union operation)."""
        str_from = str(from_node)
        str_to = str(to_node)
        
        # Make sure both nodes exist
        if str_from not in self._union_find.parent:
            self._union_find.make_set(str_from)
            self._size += 1
        if str_to not in self._union_find.parent:
            self._union_find.make_set(str_to)
            self._size += 1
        
        # Union the sets
        self._union_find.union(str_from, str_to)
    
    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes (not supported in union-find)."""
        # Union-Find doesn't support edge removal efficiently
        return False
    
    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists (connected operation)."""
        str_from = str(from_node)
        str_to = str(to_node)
        
        if str_from not in self._union_find.parent or str_to not in self._union_find.parent:
            return False
        
        return self._union_find.connected(str_from, str_to)
    
    def find_path(self, start: Any, end: Any) -> List[Any]:
        """Find path between nodes."""
        if self.has_edge(start, end):
            return [start, end]
        return []
    
    def get_neighbors(self, node: Any) -> List[Any]:
        """Get neighboring nodes (all nodes in same set)."""
        str_node = str(node)
        if str_node not in self._union_find.parent:
            return []
        
        members = self._union_find.get_set_members(str_node)
        return [member for member in members if member != str_node]
    
    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight (always 1.0 for union-find)."""
        return 1.0 if self.has_edge(from_node, to_node) else 0.0
    
    # ============================================================================
    # AUTO-3 Phase 3&4 methods
    # ============================================================================
    
    def as_union_find(self):
        """Provide Union-Find behavioral view."""
        return self
    
    def as_neural_graph(self):
        """Provide Neural Graph behavioral view."""
        # TODO: Implement Neural Graph view
        return self
    
    def as_flow_network(self):
        """Provide Flow Network behavioral view."""
        # TODO: Implement Flow Network view
        return self
    
    # ============================================================================
    # UNION-FIND SPECIFIC OPERATIONS
    # ============================================================================
    
    def make_set(self, element: str, value: Any = None) -> None:
        """Make a new set containing element."""
        if element not in self._union_find.parent:
            self._size += 1
        self._union_find.make_set(element, value)
    
    def find_root(self, element: str) -> str:
        """Find the root of the set containing element."""
        return self._union_find.find(element)
    
    def union_sets(self, element1: str, element2: str) -> bool:
        """Union the sets containing element1 and element2."""
        return self._union_find.union(element1, element2)
    
    def connected(self, element1: str, element2: str) -> bool:
        """Check if element1 and element2 are in the same set."""
        return self._union_find.connected(element1, element2)
    
    def get_set_members(self, element: str) -> Set[str]:
        """Get all members of the set containing element."""
        return self._union_find.get_set_members(element)
    
    def get_all_sets(self) -> List[Set[str]]:
        """Get all disjoint sets."""
        return self._union_find.get_all_sets()
    
    def get_set_count(self) -> int:
        """Get the number of disjoint sets."""
        return self._union_find.get_set_count()
    
    def get_set_size(self, element: str) -> int:
        """Get the size of the set containing element."""
        return self._union_find.get_set_size(element)
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Get all elements."""
        return iter(self._union_find.parent.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._union_find.values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all element-value pairs."""
        return iter(self._union_find.values.items())
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'UNION_FIND',
            'backend': 'Union-Find with path compression',
            'complexity': {
                'make_set': 'O(1)',
                'find': 'O(α(n))',
                'union': 'O(α(n))',
                'connected': 'O(α(n))'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'elements': self._size,
            'sets': self._union_find.get_set_count(),
            'memory_usage': f"{self._size * 32} bytes (estimated)"
        }
