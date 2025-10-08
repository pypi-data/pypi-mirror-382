"""
Adjacency Matrix Edge Strategy Implementation

This module implements the ADJ_MATRIX strategy for dense graph representation
with O(1) edge operations and efficient matrix-based algorithms.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, Union
from .base import AGraphEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class AdjMatrixStrategy(AGraphEdgeStrategy):
    """
    Adjacency Matrix edge strategy for dense graph representation.
    
    Provides O(1) edge operations and efficient matrix-based graph algorithms,
    ideal for dense graphs where most vertices are connected.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Adjacency Matrix strategy."""
        super().__init__(**options)
        self._mode = EdgeMode.ADJ_MATRIX
        self._traits = traits
        
        self.is_directed = options.get('directed', True)
        self.initial_capacity = options.get('initial_capacity', 100)
        self.allow_self_loops = options.get('self_loops', True)
        self.default_weight = options.get('default_weight', 1.0)
        
        # Core storage: 2D matrix of edge weights/properties
        self._matrix: List[List[Optional[Dict[str, Any]]]] = []
        self._capacity = 0
        
        # Vertex management
        self._vertex_to_index: Dict[str, int] = {}
        self._index_to_vertex: Dict[int, str] = {}
        self._vertex_count = 0
        self._edge_count = 0
        self._edge_id_counter = 0
        
        # Initialize matrix
        self._resize_matrix(self.initial_capacity)
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the adjacency matrix strategy."""
        return (EdgeTrait.DENSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.CACHE_FRIENDLY)
    
    # ============================================================================
    # MATRIX MANAGEMENT
    # ============================================================================
    
    def _resize_matrix(self, new_capacity: int) -> None:
        """Resize the adjacency matrix to new capacity."""
        old_capacity = self._capacity
        self._capacity = new_capacity
        
        # Create new matrix
        new_matrix = [[None for _ in range(self._capacity)] for _ in range(self._capacity)]
        
        # Copy existing data
        for i in range(min(old_capacity, self._capacity)):
            for j in range(min(old_capacity, self._capacity)):
                new_matrix[i][j] = self._matrix[i][j]
        
        self._matrix = new_matrix
    
    def _get_vertex_index(self, vertex: str) -> int:
        """Get or create index for vertex."""
        if vertex not in self._vertex_to_index:
            if self._vertex_count >= self._capacity:
                self._resize_matrix(self._capacity * 2)
            
            index = self._vertex_count
            self._vertex_to_index[vertex] = index
            self._index_to_vertex[index] = vertex
            self._vertex_count += 1
            return index
        
        return self._vertex_to_index[vertex]
    
    def _get_vertex_by_index(self, index: int) -> Optional[str]:
        """Get vertex by index."""
        return self._index_to_vertex.get(index)
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, from_node: Any, to_node: Any, **kwargs) -> None:
        """Add an edge between source and target vertices."""
        source = str(from_node)
        target = str(to_node)
        
        # Validation
        if not self.allow_self_loops and source == target:
            raise ValueError("Self loops not allowed")
        
        # Get vertex indices
        source_idx = self._get_vertex_index(source)
        target_idx = self._get_vertex_index(target)
        
        # Create edge data
        edge_data = {
            'weight': kwargs.get('weight', self.default_weight),
            'id': f"edge_{self._edge_id_counter}",
            **kwargs
        }
        self._edge_id_counter += 1
        
        # Add edge to matrix
        if self._matrix[source_idx][target_idx] is None:
            self._edge_count += 1
        
        self._matrix[source_idx][target_idx] = edge_data
        
        # Add reverse edge if undirected
        if not self.is_directed and source != target:
            if self._matrix[target_idx][source_idx] is None:
                self._edge_count += 1
            self._matrix[target_idx][source_idx] = edge_data
    
    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between vertices."""
        source = str(from_node)
        target = str(to_node)
        
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return False
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        removed = False
        
        # Remove edge from matrix
        if self._matrix[source_idx][target_idx] is not None:
            self._matrix[source_idx][target_idx] = None
            self._edge_count -= 1
            removed = True
        
        # Remove reverse edge if undirected
        if not self.is_directed and source != target:
            if self._matrix[target_idx][source_idx] is not None:
                self._matrix[target_idx][source_idx] = None
                self._edge_count -= 1
        
        return removed
    
    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists."""
        source = str(from_node)
        target = str(to_node)
        
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return False
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        return self._matrix[source_idx][target_idx] is not None
    
    def get_edge_count(self) -> int:
        """Get total number of edges."""
        return self._edge_count
    
    def get_vertex_count(self) -> int:
        """Get total number of vertices."""
        return self._vertex_count
    
    # ============================================================================
    # GRAPH EDGE STRATEGY METHODS
    # ============================================================================
    
    def get_neighbors(self, node: Any) -> List[Any]:
        """Get all neighboring nodes."""
        vertex = str(node)
        if vertex not in self._vertex_to_index:
            return []
        
        vertex_idx = self._vertex_to_index[vertex]
        neighbors = []
        
        for i in range(self._capacity):
            if self._matrix[vertex_idx][i] is not None:
                neighbor = self._index_to_vertex.get(i)
                if neighbor:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight."""
        source = str(from_node)
        target = str(to_node)
        
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return 0.0
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        edge_data = self._matrix[source_idx][target_idx]
        return edge_data.get('weight', self.default_weight) if edge_data else 0.0
    
    def set_edge_weight(self, from_node: Any, to_node: Any, weight: float) -> None:
        """Set edge weight."""
        source = str(from_node)
        target = str(to_node)
        
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            raise ValueError(f"Edge {source} -> {target} not found")
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        if self._matrix[source_idx][target_idx] is None:
            raise ValueError(f"Edge {source} -> {target} not found")
        
        self._matrix[source_idx][target_idx]['weight'] = weight
    
    def find_shortest_path(self, start: Any, end: Any) -> List[Any]:
        """Find shortest path between nodes."""
        # TODO: Implement Dijkstra's algorithm
        return []
    
    def find_all_paths(self, start: Any, end: Any) -> List[List[Any]]:
        """Find all paths between nodes."""
        # TODO: Implement DFS
        return []
    
    def get_connected_components(self) -> List[List[Any]]:
        """Get all connected components."""
        # TODO: Implement connected components
        return []
    
    def is_connected(self, start: Any, end: Any) -> bool:
        """Check if two nodes are connected."""
        # TODO: Implement connectivity check
        return False
    
    def get_degree(self, node: Any) -> int:
        """Get degree of node."""
        return len(self.get_neighbors(node))
    
    def is_cyclic(self) -> bool:
        """Check if graph contains cycles."""
        # TODO: Implement cycle detection
        return False
    
    # ============================================================================
    # MATRIX SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_matrix(self) -> List[List[Optional[float]]]:
        """Get the adjacency matrix as a 2D list."""
        matrix = []
        for i in range(self._vertex_count):
            row = []
            for j in range(self._vertex_count):
                edge_data = self._matrix[i][j]
                weight = edge_data.get('weight', self.default_weight) if edge_data else 0.0
                row.append(weight)
            matrix.append(row)
        return matrix
    
    def get_binary_matrix(self) -> List[List[int]]:
        """Get the binary adjacency matrix."""
        matrix = []
        for i in range(self._vertex_count):
            row = []
            for j in range(self._vertex_count):
                weight = 1 if self._matrix[i][j] is not None else 0
                row.append(weight)
            matrix.append(row)
        return matrix
    
    def set_matrix(self, matrix: List[List[Union[float, int, None]]], vertices: List[str]) -> None:
        """Set the adjacency matrix from a 2D list."""
        # Clear existing data
        self.clear()
        
        # Set vertices
        for vertex in vertices:
            self._get_vertex_index(vertex)
        
        # Set edges
        for i, row in enumerate(matrix):
            for j, weight in enumerate(row):
                if weight is not None and weight != 0:
                    source = self._index_to_vertex[i]
                    target = self._index_to_vertex[j]
                    self.add_edge(source, target, weight=float(weight))
    
    def matrix_multiply(self, other: 'xAdjMatrixStrategy') -> 'xAdjMatrixStrategy':
        """Multiply this matrix with another adjacency matrix."""
        # TODO: Implement matrix multiplication
        return self
    
    def transpose(self) -> 'xAdjMatrixStrategy':
        """Get the transpose of the adjacency matrix."""
        # TODO: Implement matrix transpose
        return self
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def edges(self) -> Iterator[tuple[Any, Any, Dict[str, Any]]]:
        """Get all edges in the graph."""
        for i in range(self._vertex_count):
            for j in range(self._vertex_count):
                if self._matrix[i][j] is not None:
                    source = self._index_to_vertex[i]
                    target = self._index_to_vertex[j]
                    yield (source, target, self._matrix[i][j])
    
    def vertices(self) -> Iterator[Any]:
        """Get all vertices in the graph."""
        return iter(self._vertex_to_index.keys())
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        self._matrix = [[None for _ in range(self._capacity)] for _ in range(self._capacity)]
        self._vertex_to_index.clear()
        self._index_to_vertex.clear()
        self._vertex_count = 0
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph."""
        self._get_vertex_index(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and all its incident edges."""
        if vertex not in self._vertex_to_index:
            return False
        
        vertex_idx = self._vertex_to_index[vertex]
        
        # Remove all edges incident to this vertex
        for i in range(self._capacity):
            if self._matrix[vertex_idx][i] is not None:
                self._matrix[vertex_idx][i] = None
                self._edge_count -= 1
            if self._matrix[i][vertex_idx] is not None:
                self._matrix[i][vertex_idx] = None
                self._edge_count -= 1
        
        # Remove vertex from mappings
        del self._vertex_to_index[vertex]
        del self._index_to_vertex[vertex_idx]
        self._vertex_count -= 1
        
        return True
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ADJ_MATRIX',
            'backend': '2D matrix',
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(1)',
                'has_edge': 'O(1)',
                'get_neighbors': 'O(V)',
                'space': 'O(V²)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'vertices': self._vertex_count,
            'edges': self._edge_count,
            'capacity': self._capacity,
            'directed': self.is_directed,
            'density': f"{(self._edge_count / max(1, self._vertex_count * (self._vertex_count - 1))) * 100:.1f}%"
        }
