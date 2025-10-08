#!/usr/bin/env python3
"""
Edge Strategy Base Classes

This module defines the abstract base classes for all edge strategy implementations:
- AEdgeStrategy: Base strategy for all edge implementations
- ALinearEdgeStrategy: Linear edge capabilities (sequential connections)
- ATreeEdgeStrategy: Tree edge capabilities (hierarchical connections)
- AGraphEdgeStrategy: Graph edge capabilities (network connections)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Tuple

from ...contracts import iEdgeStrategy
from ...errors import XWNodeTypeError, XWNodeValueError


class AEdgeStrategy(ABC):
    """Base strategy for all edge implementations."""
    
    def __init__(self, **options):
        """Initialize edge strategy."""
        self._options = options
        self._mode = options.get('mode', 'AUTO')
        self._traits = options.get('traits', None)
    
    @abstractmethod
    def add_edge(self, from_node: Any, to_node: Any, **kwargs) -> None:
        """Add edge between nodes."""
        pass
    
    @abstractmethod
    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes."""
        pass
    
    @abstractmethod
    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists."""
        pass
    
    @abstractmethod
    def get_edge_count(self) -> int:
        """Get total number of edges."""
        pass
    
    @abstractmethod
    def get_vertex_count(self) -> int:
        """Get total number of vertices."""
        pass
    
    def get_mode(self) -> str:
        """Get strategy mode."""
        return self._mode
    
    def get_traits(self):
        """Get strategy traits."""
        return self._traits


class ALinearEdgeStrategy(AEdgeStrategy):
    """Linear edge capabilities (sequential connections)."""
    
    def get_next(self, node: Any) -> Optional[Any]:
        """Get next node in sequence."""
        raise NotImplementedError("Subclasses must implement get_next")
    
    def get_previous(self, node: Any) -> Optional[Any]:
        """Get previous node in sequence."""
        raise NotImplementedError("Subclasses must implement get_previous")
    
    def get_first(self) -> Optional[Any]:
        """Get first node in sequence."""
        raise NotImplementedError("Subclasses must implement get_first")
    
    def get_last(self) -> Optional[Any]:
        """Get last node in sequence."""
        raise NotImplementedError("Subclasses must implement get_last")
    
    def insert_after(self, node: Any, new_node: Any) -> None:
        """Insert new node after specified node."""
        raise NotImplementedError("Subclasses must implement insert_after")
    
    def insert_before(self, node: Any, new_node: Any) -> None:
        """Insert new node before specified node."""
        raise NotImplementedError("Subclasses must implement insert_before")


class ATreeEdgeStrategy(AEdgeStrategy):
    """Tree edge capabilities (hierarchical connections)."""
    
    def get_parent(self, node: Any) -> Optional[Any]:
        """Get parent node."""
        raise NotImplementedError("Subclasses must implement get_parent")
    
    def get_children(self, node: Any) -> List[Any]:
        """Get child nodes."""
        raise NotImplementedError("Subclasses must implement get_children")
    
    def get_siblings(self, node: Any) -> List[Any]:
        """Get sibling nodes."""
        raise NotImplementedError("Subclasses must implement get_siblings")
    
    def get_root(self) -> Optional[Any]:
        """Get root node."""
        raise NotImplementedError("Subclasses must implement get_root")
    
    def get_leaves(self) -> List[Any]:
        """Get leaf nodes."""
        raise NotImplementedError("Subclasses must implement get_leaves")
    
    def get_depth(self, node: Any) -> int:
        """Get depth of node."""
        raise NotImplementedError("Subclasses must implement get_depth")
    
    def get_height(self) -> int:
        """Get height of tree."""
        raise NotImplementedError("Subclasses must implement get_height")
    
    def is_ancestor(self, ancestor: Any, descendant: Any) -> bool:
        """Check if one node is ancestor of another."""
        raise NotImplementedError("Subclasses must implement is_ancestor")


class AGraphEdgeStrategy(AEdgeStrategy):
    """Graph edge capabilities (network connections)."""
    
    def get_neighbors(self, node: Any) -> List[Any]:
        """Get all neighboring nodes."""
        raise NotImplementedError("Subclasses must implement get_neighbors")
    
    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight."""
        raise NotImplementedError("Subclasses must implement get_edge_weight")
    
    def set_edge_weight(self, from_node: Any, to_node: Any, weight: float) -> None:
        """Set edge weight."""
        raise NotImplementedError("Subclasses must implement set_edge_weight")
    
    def find_shortest_path(self, start: Any, end: Any) -> List[Any]:
        """Find shortest path between nodes."""
        raise NotImplementedError("Subclasses must implement find_shortest_path")
    
    def find_all_paths(self, start: Any, end: Any) -> List[List[Any]]:
        """Find all paths between nodes."""
        raise NotImplementedError("Subclasses must implement find_all_paths")
    
    def get_connected_components(self) -> List[List[Any]]:
        """Get all connected components."""
        raise NotImplementedError("Subclasses must implement get_connected_components")
    
    def is_connected(self, start: Any, end: Any) -> bool:
        """Check if two nodes are connected."""
        raise NotImplementedError("Subclasses must implement is_connected")
    
    def get_degree(self, node: Any) -> int:
        """Get degree of node."""
        raise NotImplementedError("Subclasses must implement get_degree")
    
    def is_cyclic(self) -> bool:
        """Check if graph contains cycles."""
        raise NotImplementedError("Subclasses must implement is_cyclic")
