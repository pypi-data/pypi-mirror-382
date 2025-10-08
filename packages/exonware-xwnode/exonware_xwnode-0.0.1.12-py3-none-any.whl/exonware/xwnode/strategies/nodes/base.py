#!/usr/bin/env python3
"""
Node Strategy Base Classes

This module defines the abstract base classes for all node strategy implementations:
- ANodeStrategy: Base strategy for all node implementations
- ANodeLinearStrategy: Phase 1 - Linear data structure capabilities
- ANodeTreeStrategy: Phase 2 - Tree data structure capabilities  
- ANodeGraphStrategy: Phase 3&4 - Graph data structure capabilities

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Iterator

from ...contracts import iNodeStrategy
from ...errors import XWNodeTypeError, XWNodeValueError


class ANodeStrategy(ABC):
    """Base strategy for all node implementations."""
    
    def __init__(self, data: Any = None, **options):
        """Initialize node strategy."""
        self._data = data
        self._options = options
        self._mode = options.get('mode', 'AUTO')
        self._traits = options.get('traits', None)
    
    @abstractmethod
    def insert(self, key: Any, value: Any) -> None:
        """Insert key-value pair."""
        pass
    
    @abstractmethod
    def find(self, key: Any) -> Optional[Any]:
        """Find value by key."""
        pass
    
    @abstractmethod
    def delete(self, key: Any) -> bool:
        """Delete by key."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get size of structure."""
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Check if structure is empty."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    def get_mode(self) -> str:
        """Get strategy mode."""
        return self._mode
    
    def get_traits(self):
        """Get strategy traits."""
        return self._traits


class ANodeLinearStrategy(ANodeStrategy):
    """Phase 1: Linear data structure capabilities."""
    
    def push_front(self, value: Any) -> None:
        """Add element to front."""
        raise NotImplementedError("Subclasses must implement push_front")
    
    def push_back(self, value: Any) -> None:
        """Add element to back."""
        raise NotImplementedError("Subclasses must implement push_back")
    
    def pop_front(self) -> Any:
        """Remove element from front."""
        raise NotImplementedError("Subclasses must implement pop_front")
    
    def pop_back(self) -> Any:
        """Remove element from back."""
        raise NotImplementedError("Subclasses must implement pop_back")
    
    def get_at_index(self, index: int) -> Any:
        """Get element at index."""
        raise NotImplementedError("Subclasses must implement get_at_index")
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index."""
        raise NotImplementedError("Subclasses must implement set_at_index")
    
    # AUTO-3 Phase 1 methods
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        raise NotImplementedError("Subclasses must implement as_linked_list")
    
    def as_stack(self):
        """Provide Stack behavioral view."""
        raise NotImplementedError("Subclasses must implement as_stack")
    
    def as_queue(self):
        """Provide Queue behavioral view."""
        raise NotImplementedError("Subclasses must implement as_queue")
    
    def as_deque(self):
        """Provide Deque behavioral view."""
        raise NotImplementedError("Subclasses must implement as_deque")


class ANodeGraphStrategy(ANodeStrategy):
    """Phase 3&4: Graph data structure capabilities."""
    
    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Add edge between nodes."""
        raise NotImplementedError("Subclasses must implement add_edge")
    
    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes."""
        raise NotImplementedError("Subclasses must implement remove_edge")
    
    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists."""
        raise NotImplementedError("Subclasses must implement has_edge")
    
    def find_path(self, start: Any, end: Any) -> List[Any]:
        """Find path between nodes."""
        raise NotImplementedError("Subclasses must implement find_path")
    
    def get_neighbors(self, node: Any) -> List[Any]:
        """Get neighboring nodes."""
        raise NotImplementedError("Subclasses must implement get_neighbors")
    
    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight."""
        raise NotImplementedError("Subclasses must implement get_edge_weight")
    
    # AUTO-3 Phase 3&4 methods
    def as_union_find(self):
        """Provide Union-Find behavioral view."""
        raise NotImplementedError("Subclasses must implement as_union_find")
    
    def as_neural_graph(self):
        """Provide Neural Graph behavioral view."""
        raise NotImplementedError("Subclasses must implement as_neural_graph")
    
    def as_flow_network(self):
        """Provide Flow Network behavioral view."""
        raise NotImplementedError("Subclasses must implement as_flow_network")


class ANodeMatrixStrategy(ANodeStrategy):
    """Matrix-based data structure capabilities."""
    
    def get_dimensions(self) -> tuple:
        """Get matrix dimensions (rows, cols)."""
        raise NotImplementedError("Subclasses must implement get_dimensions")
    
    def get_at_position(self, row: int, col: int) -> Any:
        """Get element at matrix position."""
        raise NotImplementedError("Subclasses must implement get_at_position")
    
    def set_at_position(self, row: int, col: int, value: Any) -> None:
        """Set element at matrix position."""
        raise NotImplementedError("Subclasses must implement set_at_position")
    
    def get_row(self, row: int) -> List[Any]:
        """Get entire row."""
        raise NotImplementedError("Subclasses must implement get_row")
    
    def get_column(self, col: int) -> List[Any]:
        """Get entire column."""
        raise NotImplementedError("Subclasses must implement get_column")
    
    def transpose(self) -> 'ANodeMatrixStrategy':
        """Transpose the matrix."""
        raise NotImplementedError("Subclasses must implement transpose")
    
    def multiply(self, other: 'ANodeMatrixStrategy') -> 'ANodeMatrixStrategy':
        """Matrix multiplication."""
        raise NotImplementedError("Subclasses must implement multiply")
    
    def add(self, other: 'ANodeMatrixStrategy') -> 'ANodeMatrixStrategy':
        """Matrix addition."""
        raise NotImplementedError("Subclasses must implement add")
    
    # Matrix-specific behavioral views
    def as_adjacency_matrix(self):
        """Provide Adjacency Matrix behavioral view."""
        raise NotImplementedError("Subclasses must implement as_adjacency_matrix")
    
    def as_incidence_matrix(self):
        """Provide Incidence Matrix behavioral view."""
        raise NotImplementedError("Subclasses must implement as_incidence_matrix")
    
    def as_sparse_matrix(self):
        """Provide Sparse Matrix behavioral view."""
        raise NotImplementedError("Subclasses must implement as_sparse_matrix")


class ANodeTreeStrategy(ANodeGraphStrategy):
    """Phase 2: Tree data structure capabilities."""
    
    def insert(self, key: Any, value: Any) -> None:
        """Insert with tree ordering."""
        raise NotImplementedError("Subclasses must implement insert")
    
    def find(self, key: Any) -> Optional[Any]:
        """Find with tree traversal."""
        raise NotImplementedError("Subclasses must implement find")
    
    def delete(self, key: Any) -> bool:
        """Delete with tree restructuring."""
        raise NotImplementedError("Subclasses must implement delete")
    
    def traverse(self, order: str = 'inorder') -> List[Any]:
        """Traverse tree in specified order."""
        raise NotImplementedError("Subclasses must implement traverse")
    
    def get_min(self) -> Any:
        """Get minimum key."""
        raise NotImplementedError("Subclasses must implement get_min")
    
    def get_max(self) -> Any:
        """Get maximum key."""
        raise NotImplementedError("Subclasses must implement get_max")
    
    # AUTO-3 Phase 2 methods
    def as_trie(self):
        """Provide Trie behavioral view."""
        raise NotImplementedError("Subclasses must implement as_trie")
    
    def as_heap(self):
        """Provide Heap behavioral view."""
        raise NotImplementedError("Subclasses must implement as_heap")
    
    def as_skip_list(self):
        """Provide SkipList behavioral view."""
        raise NotImplementedError("Subclasses must implement as_skip_list")
