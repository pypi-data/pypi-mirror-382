"""
Adjacency List Edge Strategy Implementation

This module implements the ADJ_LIST strategy for sparse graph representation
with efficient edge addition and neighbor queries.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple
from collections import defaultdict
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class xAdjListStrategy(aEdgeStrategy):
    """
    Adjacency List edge strategy for sparse graph representation.
    
    Provides O(1) edge addition and O(degree) neighbor queries,
    ideal for sparse graphs where most vertices have few connections.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Adjacency List strategy."""
        super().__init__(EdgeMode.ADJ_LIST, traits, **options)
        
        self.is_directed = options.get('directed', True)
        self.allow_self_loops = options.get('self_loops', True)
        self.allow_multi_edges = options.get('multi_edges', False)
        
        # Core storage: vertex -> list of (neighbor, edge_data)
        self._outgoing: Dict[str, List[Tuple[str, Dict[str, Any]]]] = defaultdict(list)
        self._incoming: Dict[str, List[Tuple[str, Dict[str, Any]]]] = defaultdict(list) if self.is_directed else None
        
        # Vertex set for fast membership testing
        self._vertices: Set[str] = set()
        
        # Edge properties storage
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the adjacency list strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.MULTI)
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add an edge between source and target vertices."""
        # Validate self-loops
        if source == target and not self.allow_self_loops:
            raise ValueError(f"Self-loops not allowed: {source} -> {target}")
        
        # Check for existing edge if multi-edges not allowed
        if not self.allow_multi_edges and self.has_edge(source, target):
            raise ValueError(f"Multi-edges not allowed: {source} -> {target}")
        
        # Generate edge ID
        edge_id = f"edge_{self._edge_id_counter}"
        self._edge_id_counter += 1
        
        # Create edge data
        edge_data = {
            'id': edge_id,
            'source': source,
            'target': target,
            'properties': properties.copy()
        }
        
        # Add vertices to vertex set
        self._vertices.add(source)
        self._vertices.add(target)
        
        # Add to outgoing adjacency list
        self._outgoing[source].append((target, edge_data))
        
        # Add to incoming adjacency list (if directed)
        if self.is_directed and self._incoming is not None:
            self._incoming[target].append((source, edge_data))
        elif not self.is_directed:
            # For undirected graphs, add reverse edge (unless it's a self-loop)
            if source != target:
                self._outgoing[target].append((source, edge_data))
        
        self._edge_count += 1
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge(s) between source and target."""
        if source not in self._outgoing:
            return False
        
        removed = False
        
        # Remove from outgoing list
        original_length = len(self._outgoing[source])
        if edge_id:
            # Remove specific edge by ID
            self._outgoing[source] = [
                (neighbor, data) for neighbor, data in self._outgoing[source]
                if not (neighbor == target and data['id'] == edge_id)
            ]
        else:
            # Remove all edges to target
            self._outgoing[source] = [
                (neighbor, data) for neighbor, data in self._outgoing[source]
                if neighbor != target
            ]
        
        removed = len(self._outgoing[source]) < original_length
        
        if removed:
            self._edge_count -= (original_length - len(self._outgoing[source]))
        
        # Remove from incoming list (if directed)
        if self.is_directed and self._incoming is not None and target in self._incoming:
            if edge_id:
                self._incoming[target] = [
                    (neighbor, data) for neighbor, data in self._incoming[target]
                    if not (neighbor == source and data['id'] == edge_id)
                ]
            else:
                self._incoming[target] = [
                    (neighbor, data) for neighbor, data in self._incoming[target]
                    if neighbor != source
                ]
        elif not self.is_directed and source != target:
            # For undirected graphs, remove reverse edge
            if target in self._outgoing:
                if edge_id:
                    self._outgoing[target] = [
                        (neighbor, data) for neighbor, data in self._outgoing[target]
                        if not (neighbor == source and data['id'] == edge_id)
                    ]
                else:
                    self._outgoing[target] = [
                        (neighbor, data) for neighbor, data in self._outgoing[target]
                        if neighbor != source
                    ]
        
        return removed
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        if source not in self._outgoing:
            return False
        
        return any(neighbor == target for neighbor, _ in self._outgoing[source])
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data between source and target."""
        if source not in self._outgoing:
            return None
        
        for neighbor, data in self._outgoing[source]:
            if neighbor == target:
                return data
        
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of a vertex."""
        if direction == 'out':
            if vertex in self._outgoing:
                for neighbor, _ in self._outgoing[vertex]:
                    yield neighbor
        elif direction == 'in':
            if self.is_directed and self._incoming is not None and vertex in self._incoming:
                for neighbor, _ in self._incoming[vertex]:
                    yield neighbor
            elif not self.is_directed:
                # For undirected graphs, incoming = outgoing
                if vertex in self._outgoing:
                    for neighbor, _ in self._outgoing[vertex]:
                        yield neighbor
        elif direction == 'both':
            # Get all neighbors (both in and out)
            seen = set()
            for neighbor in self.neighbors(vertex, 'out'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    yield neighbor
            for neighbor in self.neighbors(vertex, 'in'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    yield neighbor
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of a vertex."""
        if direction == 'out':
            return len(self._outgoing.get(vertex, []))
        elif direction == 'in':
            if self.is_directed and self._incoming is not None:
                return len(self._incoming.get(vertex, []))
            elif not self.is_directed:
                return len(self._outgoing.get(vertex, []))
            else:
                return 0
        elif direction == 'both':
            out_degree = self.degree(vertex, 'out')
            in_degree = self.degree(vertex, 'in')
            # For undirected graphs, avoid double counting
            return out_degree if not self.is_directed else out_degree + in_degree
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges in the graph."""
        seen_edges = set()
        
        for source, adj_list in self._outgoing.items():
            for target, edge_data in adj_list:
                edge_key = (source, target, edge_data['id'])
                
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    
                    if data:
                        yield (source, target, edge_data)
                    else:
                        yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices in the graph."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get the number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        self._outgoing.clear()
        if self._incoming is not None:
            self._incoming.clear()
        self._vertices.clear()
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph."""
        self._vertices.add(vertex)
        # Initialize adjacency lists if not present
        if vertex not in self._outgoing:
            self._outgoing[vertex] = []
        if self.is_directed and self._incoming is not None and vertex not in self._incoming:
            self._incoming[vertex] = []
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Remove all outgoing edges
        edges_removed = len(self._outgoing.get(vertex, []))
        self._edge_count -= edges_removed
        
        # Remove all incoming edges
        for source in list(self._outgoing.keys()):
            if source != vertex:
                original_length = len(self._outgoing[source])
                self._outgoing[source] = [
                    (neighbor, data) for neighbor, data in self._outgoing[source]
                    if neighbor != vertex
                ]
                self._edge_count -= (original_length - len(self._outgoing[source]))
        
        # Clean up adjacency lists
        if vertex in self._outgoing:
            del self._outgoing[vertex]
        if self._incoming is not None and vertex in self._incoming:
            del self._incoming[vertex]
        
        # Remove from vertex set
        self._vertices.remove(vertex)
        
        return True
    
    # ============================================================================
    # ADVANCED OPERATIONS
    # ============================================================================
    
    def get_subgraph(self, vertices: Set[str]) -> 'xAdjListStrategy':
        """Extract subgraph containing only specified vertices."""
        subgraph = xAdjListStrategy(
            traits=self._traits,
            directed=self.is_directed,
            self_loops=self.allow_self_loops,
            multi_edges=self.allow_multi_edges
        )
        
        # Add vertices
        for vertex in vertices:
            if vertex in self._vertices:
                subgraph.add_vertex(vertex)
        
        # Add edges
        for source, target, edge_data in self.edges(data=True):
            if source in vertices and target in vertices:
                subgraph.add_edge(source, target, **edge_data['properties'])
        
        return subgraph
    
    def get_edge_list(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Get all edges as a list."""
        return list(self.edges(data=True))
    
    def get_adjacency_dict(self) -> Dict[str, List[str]]:
        """Get adjacency representation as a dictionary."""
        return {
            vertex: [neighbor for neighbor, _ in adj_list]
            for vertex, adj_list in self._outgoing.items()
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'adjacency_list',
            'backend': 'Python defaultdict + lists',
            'directed': self.is_directed,
            'multi_edges': self.allow_multi_edges,
            'self_loops': self.allow_self_loops,
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(degree)',
                'has_edge': 'O(degree)',
                'neighbors': 'O(degree)',
                'space': 'O(V + E)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        avg_degree = self._edge_count / max(1, len(self._vertices)) if self._vertices else 0
        density = self._edge_count / max(1, len(self._vertices) * (len(self._vertices) - 1)) if len(self._vertices) > 1 else 0
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'average_degree': round(avg_degree, 2),
            'density': round(density, 4),
            'memory_usage': f"{len(self._vertices) * 48 + self._edge_count * 32} bytes (estimated)",
            'sparsity': f"{(1 - density) * 100:.1f}%"
        }
