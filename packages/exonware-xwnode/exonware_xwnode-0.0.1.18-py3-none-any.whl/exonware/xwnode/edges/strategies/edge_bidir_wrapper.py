"""
Bidirectional Wrapper Edge Strategy Implementation

This module implements the BIDIR_WRAPPER strategy for efficient
undirected graph operations using dual directed edges.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import defaultdict
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class xBidirWrapperStrategy(aEdgeStrategy):
    """
    Bidirectional Wrapper edge strategy for undirected graphs.
    
    Efficiently represents undirected edges using pairs of directed edges
    with automatic synchronization and optimized undirected operations.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Bidirectional Wrapper strategy."""
        super().__init__(EdgeMode.BIDIR_WRAPPER, traits, **options)
        
        self.auto_sync = options.get('auto_sync', True)
        self.weighted = options.get('weighted', True)
        self.allow_self_loops = options.get('allow_self_loops', True)
        
        # Core storage: directed adjacency lists for both directions
        self._outgoing: Dict[str, Dict[str, float]] = defaultdict(dict)  # source -> {target: weight}
        self._incoming: Dict[str, Dict[str, float]] = defaultdict(dict)  # target -> {source: weight}
        
        # Undirected edge tracking
        self._undirected_edges: Set[Tuple[str, str]] = set()  # Canonical edge pairs (min, max)
        self._vertices: Set[str] = set()
        
        # Performance tracking
        self._edge_count = 0
        self._sync_operations = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the bidirectional wrapper strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.CACHE_FRIENDLY)
    
    def _canonical_edge(self, source: str, target: str) -> Tuple[str, str]:
        """Get canonical representation of undirected edge."""
        return (min(source, target), max(source, target))
    
    def _add_directed_edge(self, source: str, target: str, weight: float) -> None:
        """Add directed edge to internal structures."""
        self._outgoing[source][target] = weight
        self._incoming[target][source] = weight
        self._vertices.add(source)
        self._vertices.add(target)
    
    def _remove_directed_edge(self, source: str, target: str) -> bool:
        """Remove directed edge from internal structures."""
        if target in self._outgoing.get(source, {}):
            del self._outgoing[source][target]
            del self._incoming[target][source]
            return True
        return False
    
    def _sync_undirected_edge(self, source: str, target: str, weight: float) -> None:
        """Synchronize both directions of an undirected edge."""
        if self.auto_sync:
            self._add_directed_edge(source, target, weight)
            if source != target:  # Avoid double self-loops
                self._add_directed_edge(target, source, weight)
            self._sync_operations += 1
    
    def _unsync_undirected_edge(self, source: str, target: str) -> bool:
        """Remove both directions of an undirected edge."""
        removed = False
        if self._remove_directed_edge(source, target):
            removed = True
        if source != target and self._remove_directed_edge(target, source):
            removed = True
        
        if removed:
            self._sync_operations += 1
        
        return removed
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add undirected edge (creates two directed edges)."""
        weight = properties.get('weight', 1.0) if self.weighted else 1.0
        
        if not self.allow_self_loops and source == target:
            raise ValueError("Self-loops not allowed")
        
        canonical = self._canonical_edge(source, target)
        
        # Check if undirected edge already exists
        if canonical in self._undirected_edges:
            # Update existing edge
            self._sync_undirected_edge(source, target, weight)
        else:
            # Add new undirected edge
            self._sync_undirected_edge(source, target, weight)
            self._undirected_edges.add(canonical)
            self._edge_count += 1
        
        return f"{canonical[0]}<->{canonical[1]}"
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove undirected edge (removes both directed edges)."""
        canonical = self._canonical_edge(source, target)
        
        if canonical in self._undirected_edges:
            # Remove undirected edge
            if self._unsync_undirected_edge(source, target):
                self._undirected_edges.remove(canonical)
                self._edge_count -= 1
                return True
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if undirected edge exists."""
        canonical = self._canonical_edge(source, target)
        return canonical in self._undirected_edges
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        if not self.has_edge(source, target):
            return None
        
        # Get weight from one direction (they should be synchronized)
        weight = self._outgoing.get(source, {}).get(target, 1.0)
        canonical = self._canonical_edge(source, target)
        
        return {
            'source': source,
            'target': target,
            'canonical': canonical,
            'weight': weight,
            'undirected': True,
            'self_loop': source == target
        }
    
    def neighbors(self, vertex: str, direction: str = 'both') -> Iterator[str]:
        """Get neighbors of vertex."""
        if direction in ['out', 'both']:
            for neighbor in self._outgoing.get(vertex, {}):
                yield neighbor
        
        if direction in ['in', 'both'] and direction != 'out':
            # For undirected graphs, incoming and outgoing are the same
            # But avoid duplicates when direction is 'both'
            for neighbor in self._incoming.get(vertex, {}):
                if direction == 'in' or neighbor not in self._outgoing.get(vertex, {}):
                    yield neighbor
    
    def degree(self, vertex: str, direction: str = 'both') -> int:
        """Get degree of vertex."""
        if direction == 'out':
            return len(self._outgoing.get(vertex, {}))
        elif direction == 'in':
            return len(self._incoming.get(vertex, {}))
        else:  # both - for undirected graphs, this is just the degree
            # Use set to avoid counting self-loops twice
            neighbors = set()
            neighbors.update(self._outgoing.get(vertex, {}))
            neighbors.update(self._incoming.get(vertex, {}))
            return len(neighbors)
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all undirected edges (returns each edge once)."""
        for canonical in self._undirected_edges:
            source, target = canonical
            
            if data:
                edge_data = self.get_edge_data(source, target)
                yield (source, target, edge_data)
            else:
                yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get number of undirected edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all data."""
        self._outgoing.clear()
        self._incoming.clear()
        self._undirected_edges.clear()
        self._vertices.clear()
        self._edge_count = 0
        self._sync_operations = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex to graph."""
        self._vertices.add(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Remove all edges involving this vertex
        edges_to_remove = []
        for source, target in self.edges():
            if source == vertex or target == vertex:
                edges_to_remove.append((source, target))
        
        for source, target in edges_to_remove:
            self.remove_edge(source, target)
        
        # Remove vertex
        self._vertices.discard(vertex)
        self._outgoing.pop(vertex, None)
        self._incoming.pop(vertex, None)
        
        return True
    
    # ============================================================================
    # UNDIRECTED GRAPH SPECIFIC OPERATIONS
    # ============================================================================
    
    def add_undirected_edge(self, vertex1: str, vertex2: str, weight: float = 1.0) -> str:
        """Add undirected edge explicitly."""
        return self.add_edge(vertex1, vertex2, weight=weight)
    
    def get_undirected_degree(self, vertex: str) -> int:
        """Get undirected degree (number of incident edges)."""
        return self.degree(vertex, 'both')
    
    def get_all_neighbors(self, vertex: str) -> Set[str]:
        """Get all neighbors in undirected graph."""
        neighbors = set()
        neighbors.update(self._outgoing.get(vertex, {}))
        neighbors.update(self._incoming.get(vertex, {}))
        return neighbors
    
    def is_connected_to(self, vertex1: str, vertex2: str) -> bool:
        """Check if two vertices are connected."""
        return self.has_edge(vertex1, vertex2)
    
    def get_edge_weight(self, vertex1: str, vertex2: str) -> Optional[float]:
        """Get weight of undirected edge."""
        if not self.has_edge(vertex1, vertex2):
            return None
        
        # Return weight from either direction (should be same)
        return self._outgoing.get(vertex1, {}).get(vertex2) or \
               self._outgoing.get(vertex2, {}).get(vertex1)
    
    def set_edge_weight(self, vertex1: str, vertex2: str, weight: float) -> bool:
        """Set weight of undirected edge."""
        if not self.has_edge(vertex1, vertex2):
            return False
        
        # Update both directions
        self._sync_undirected_edge(vertex1, vertex2, weight)
        return True
    
    def get_connected_components(self) -> List[Set[str]]:
        """Find connected components using DFS."""
        visited = set()
        components = []
        
        for vertex in self._vertices:
            if vertex not in visited:
                component = set()
                stack = [vertex]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        
                        # Add all unvisited neighbors
                        for neighbor in self.get_all_neighbors(current):
                            if neighbor not in visited:
                                stack.append(neighbor)
                
                if component:
                    components.append(component)
        
        return components
    
    def is_connected(self) -> bool:
        """Check if graph is connected."""
        components = self.get_connected_components()
        return len(components) <= 1
    
    def spanning_tree_edges(self) -> List[Tuple[str, str, float]]:
        """Get edges of a minimum spanning tree using Kruskal's algorithm."""
        # Get all edges with weights
        edges = []
        for source, target in self.edges():
            weight = self.get_edge_weight(source, target)
            edges.append((weight, source, target))
        
        # Sort by weight
        edges.sort()
        
        # Union-Find for cycle detection
        parent = {}
        rank = {}
        
        def find(x):
            if x not in parent:
                parent[x] = x
                rank[x] = 0
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return False
            if rank[px] < rank[py]:
                px, py = py, px
            parent[py] = px
            if rank[px] == rank[py]:
                rank[px] += 1
            return True
        
        # Build MST
        mst_edges = []
        for weight, source, target in edges:
            if union(source, target):
                mst_edges.append((source, target, weight))
        
        return mst_edges
    
    def validate_synchronization(self) -> Dict[str, Any]:
        """Validate that all undirected edges are properly synchronized."""
        issues = []
        
        for canonical in self._undirected_edges:
            source, target = canonical
            
            # Check forward direction
            forward_weight = self._outgoing.get(source, {}).get(target)
            if forward_weight is None:
                issues.append(f"Missing forward edge: {source} -> {target}")
                continue
            
            # Check backward direction (skip for self-loops)
            if source != target:
                backward_weight = self._outgoing.get(target, {}).get(source)
                if backward_weight is None:
                    issues.append(f"Missing backward edge: {target} -> {source}")
                elif abs(forward_weight - backward_weight) > 1e-9:
                    issues.append(f"Weight mismatch: {source}<->{target} ({forward_weight} != {backward_weight})")
        
        return {
            'synchronized': len(issues) == 0,
            'issues': issues,
            'sync_operations': self._sync_operations,
            'undirected_edges': len(self._undirected_edges),
            'directed_edges': sum(len(adj) for adj in self._outgoing.values())
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bidirectional wrapper statistics."""
        sync_status = self.validate_synchronization()
        components = self.get_connected_components()
        
        # Calculate clustering coefficient
        total_clustering = 0
        vertices_with_neighbors = 0
        
        for vertex in self._vertices:
            neighbors = self.get_all_neighbors(vertex)
            degree = len(neighbors)
            
            if degree >= 2:
                # Count triangles
                triangles = 0
                for n1 in neighbors:
                    for n2 in neighbors:
                        if n1 < n2 and self.has_edge(n1, n2):
                            triangles += 1
                
                # Clustering coefficient for this vertex
                possible_edges = degree * (degree - 1) / 2
                clustering = triangles / possible_edges if possible_edges > 0 else 0
                total_clustering += clustering
                vertices_with_neighbors += 1
        
        avg_clustering = total_clustering / vertices_with_neighbors if vertices_with_neighbors > 0 else 0
        
        return {
            'vertices': len(self._vertices),
            'undirected_edges': self._edge_count,
            'directed_edges_stored': sum(len(adj) for adj in self._outgoing.values()),
            'connected_components': len(components),
            'largest_component': max(len(comp) for comp in components) if components else 0,
            'is_connected': len(components) <= 1,
            'avg_degree': (2 * self._edge_count) / max(1, len(self._vertices)),
            'avg_clustering_coefficient': avg_clustering,
            'sync_status': sync_status,
            'weighted': self.weighted,
            'allow_self_loops': self.allow_self_loops,
            'auto_sync': self.auto_sync
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'BIDIR_WRAPPER',
            'backend': 'Dual directed adjacency lists for undirected graphs',
            'auto_sync': self.auto_sync,
            'weighted': self.weighted,
            'allow_self_loops': self.allow_self_loops,
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(1)',
                'has_edge': 'O(1)',
                'neighbors': 'O(degree)',
                'connected_components': 'O(V + E)',
                'space': 'O(2E + V)'  # Double storage for undirected edges
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        sync_status = stats['sync_status']
        
        return {
            'vertices': stats['vertices'],
            'undirected_edges': stats['undirected_edges'],
            'directed_edges_stored': stats['directed_edges_stored'],
            'connected_components': stats['connected_components'],
            'avg_degree': f"{stats['avg_degree']:.1f}",
            'clustering_coeff': f"{stats['avg_clustering_coefficient']:.3f}",
            'synchronized': sync_status['synchronized'],
            'memory_usage': f"{stats['directed_edges_stored'] * 16 + len(self._vertices) * 50} bytes (estimated)"
        }
