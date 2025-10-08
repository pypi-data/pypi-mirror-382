#exonware\xnode\strategies\impls\edge_tree_graph_basic.py
"""
Tree-Graph Basic Edge Strategy Implementation

This module implements the TREE_GRAPH_BASIC strategy for basic edge storage
in tree+graph hybrid structures, providing minimal graph capabilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Iterator
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class xTreeGraphBasicStrategy(aEdgeStrategy):
    """
    Basic edge strategy for tree+graph hybrid structures.
    
    Provides minimal graph capabilities optimized for tree navigation
    with basic edge storage and traversal support.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the tree-graph basic strategy."""
        super().__init__(EdgeMode.TREE_GRAPH_BASIC, traits, **options)
        
        # Basic edge storage - simple adjacency representation
        self._edges: Dict[str, Set[str]] = {}  # source -> {targets}
        self._reverse_edges: Dict[str, Set[str]] = {}  # target -> {sources}
        self._edge_count = 0
        
        # Statistics
        self._total_additions = 0
        self._total_removals = 0
        self._max_degree = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the tree-graph basic strategy."""
        return (EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.MULTI)
    
    def _update_degree_stats(self, node: str) -> None:
        """Update degree statistics."""
        degree = len(self._edges.get(node, set()))
        self._max_degree = max(self._max_degree, degree)
    
    def _add_edge_internal(self, source: str, target: str, weight: float = 1.0, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Internal method to add edge."""
        if source not in self._edges:
            self._edges[source] = set()
        if target not in self._reverse_edges:
            self._reverse_edges[target] = set()
        
        # Check if edge already exists
        if target in self._edges[source]:
            return False  # Edge already exists
        
        # Add edge
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)
        self._edge_count += 1
        self._total_additions += 1
        
        # Update statistics
        self._update_degree_stats(source)
        
        return True
    
    def _remove_edge_internal(self, source: str, target: str) -> bool:
        """Internal method to remove edge."""
        if source not in self._edges or target not in self._edges[source]:
            return False
        
        # Remove edge
        self._edges[source].remove(target)
        self._reverse_edges[target].remove(source)
        self._edge_count -= 1
        self._total_removals += 1
        
        # Clean up empty sets
        if not self._edges[source]:
            del self._edges[source]
        if not self._reverse_edges[target]:
            del self._reverse_edges[target]
        
        return True
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, weight: float = 1.0, 
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add an edge between source and target nodes."""
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Source and target must be strings")
        
        return self._add_edge_internal(source, target, weight, metadata)
    
    def remove_edge(self, source: str, target: str) -> bool:
        """Remove an edge between source and target nodes."""
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("Source and target must be strings")
        
        return self._remove_edge_internal(source, target)
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if an edge exists between source and target nodes."""
        if not isinstance(source, str) or not isinstance(target, str):
            return False
        
        return source in self._edges and target in self._edges[source]
    
    def get_neighbors(self, node: str) -> List[str]:
        """Get all neighbors of a node."""
        if not isinstance(node, str):
            return []
        
        return list(self._edges.get(node, set()))
    
    def get_incoming(self, node: str) -> List[str]:
        """Get all incoming neighbors of a node."""
        if not isinstance(node, str):
            return []
        
        return list(self._reverse_edges.get(node, set()))
    
    def get_outgoing(self, node: str) -> List[str]:
        """Get all outgoing neighbors of a node."""
        if not isinstance(node, str):
            return []
        
        return list(self._edges.get(node, set()))
    
    def get_degree(self, node: str) -> int:
        """Get the degree (number of neighbors) of a node."""
        if not isinstance(node, str):
            return 0
        
        return len(self._edges.get(node, set()))
    
    def get_in_degree(self, node: str) -> int:
        """Get the in-degree of a node."""
        if not isinstance(node, str):
            return 0
        
        return len(self._reverse_edges.get(node, set()))
    
    def get_out_degree(self, node: str) -> int:
        """Get the out-degree of a node."""
        if not isinstance(node, str):
            return 0
        
        return len(self._edges.get(node, set()))
    
    def clear(self) -> None:
        """Clear all edges."""
        self._edges.clear()
        self._reverse_edges.clear()
        self._edge_count = 0
    
    def size(self) -> int:
        """Get the number of edges."""
        return self._edge_count
    
    def is_empty(self) -> bool:
        """Check if there are no edges."""
        return self._edge_count == 0
    
    def get_nodes(self) -> Set[str]:
        """Get all nodes that have edges."""
        nodes = set()
        nodes.update(self._edges.keys())
        nodes.update(self._reverse_edges.keys())
        return nodes
    
    def get_edge_count(self) -> int:
        """Get the total number of edges."""
        return self._edge_count
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def edges(self) -> Iterator[Tuple[str, str]]:
        """Iterate over all edges as (source, target) pairs."""
        for source, targets in self._edges.items():
            for target in targets:
                yield (source, target)
    
    def nodes(self) -> Iterator[str]:
        """Iterate over all nodes."""
        yield from self.get_nodes()
    
    def __iter__(self) -> Iterator[Tuple[str, str]]:
        """Iterate over all edges."""
        yield from self.edges()
    
    # ============================================================================
    # TREE-GRAPH BASIC SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_children(self, node: str) -> List[str]:
        """Get children of a node (for tree-like navigation)."""
        return self.get_outgoing(node)
    
    def get_parents(self, node: str) -> List[str]:
        """Get parents of a node (for tree-like navigation)."""
        return self.get_incoming(node)
    
    def is_leaf(self, node: str) -> bool:
        """Check if a node is a leaf (no outgoing edges)."""
        return self.get_out_degree(node) == 0
    
    def is_root(self, node: str) -> bool:
        """Check if a node is a root (no incoming edges)."""
        return self.get_in_degree(node) == 0
    
    def get_roots(self) -> List[str]:
        """Get all root nodes (nodes with no incoming edges)."""
        all_nodes = self.get_nodes()
        return [node for node in all_nodes if self.is_root(node)]
    
    def get_leaves(self) -> List[str]:
        """Get all leaf nodes (nodes with no outgoing edges)."""
        all_nodes = self.get_nodes()
        return [node for node in all_nodes if self.is_leaf(node)]
    
    def get_path(self, source: str, target: str) -> Optional[List[str]]:
        """Get a simple path from source to target using BFS."""
        if source == target:
            return [source]
        
        if source not in self._edges:
            return None
        
        # Simple BFS for path finding
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self._edges.get(current, set()):
                if neighbor == target:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def is_connected(self, source: str, target: str) -> bool:
        """Check if two nodes are connected."""
        return self.get_path(source, target) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        nodes = self.get_nodes()
        return {
            'edge_count': self._edge_count,
            'node_count': len(nodes),
            'max_degree': self._max_degree,
            'total_additions': self._total_additions,
            'total_removals': self._total_removals,
            'roots': len(self.get_roots()),
            'leaves': len(self.get_leaves()),
            'strategy': 'TREE_GRAPH_BASIC',
            'backend': 'Simple adjacency sets with reverse indexing',
            'traits': [trait.name for trait in EdgeTrait if self.has_trait(trait)]
        }
