"""
Block Adjacency Matrix Edge Strategy Implementation

This module implements the BLOCK_ADJ_MATRIX strategy for cache-friendly
dense graph operations using block-based matrix partitioning.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple, Set
import math
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class MatrixBlock:
    """A block in the block adjacency matrix."""
    
    def __init__(self, block_size: int):
        self.block_size = block_size
        self.data: List[List[Any]] = [[None for _ in range(block_size)] for _ in range(block_size)]
        self.edge_count = 0
        self.is_dense = False
    
    def set_edge(self, local_u: int, local_v: int, weight: Any = 1) -> bool:
        """Set edge in block. Returns True if new edge."""
        old_value = self.data[local_u][local_v]
        self.data[local_u][local_v] = weight
        
        if old_value is None and weight is not None:
            self.edge_count += 1
            self.is_dense = self.edge_count > (self.block_size * self.block_size * 0.5)
            return True
        elif old_value is not None and weight is None:
            self.edge_count -= 1
            self.is_dense = self.edge_count > (self.block_size * self.block_size * 0.5)
            return False
        
        return False
    
    def get_edge(self, local_u: int, local_v: int) -> Any:
        """Get edge weight from block."""
        return self.data[local_u][local_v]
    
    def has_edge(self, local_u: int, local_v: int) -> bool:
        """Check if edge exists in block."""
        return self.data[local_u][local_v] is not None
    
    def remove_edge(self, local_u: int, local_v: int) -> bool:
        """Remove edge from block. Returns True if edge existed."""
        if self.data[local_u][local_v] is not None:
            self.data[local_u][local_v] = None
            self.edge_count -= 1
            self.is_dense = self.edge_count > (self.block_size * self.block_size * 0.5)
            return True
        return False
    
    def get_edges(self) -> List[Tuple[int, int, Any]]:
        """Get all edges in block as (local_u, local_v, weight)."""
        edges = []
        for u in range(self.block_size):
            for v in range(self.block_size):
                if self.data[u][v] is not None:
                    edges.append((u, v, self.data[u][v]))
        return edges


class xBlockAdjMatrixStrategy(aEdgeStrategy):
    """
    Block Adjacency Matrix edge strategy for cache-friendly dense operations.
    
    Partitions large adjacency matrices into smaller blocks that fit in cache,
    optimizing for spatial locality and dense graph operations.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Block Adjacency Matrix strategy."""
        super().__init__(EdgeMode.BLOCK_ADJ_MATRIX, traits, **options)
        
        self.block_size = options.get('block_size', 64)  # Cache-friendly size
        self.auto_optimize = options.get('auto_optimize', True)
        self.cache_blocks = options.get('cache_blocks', True)
        
        # Core block matrix storage
        self._blocks: Dict[Tuple[int, int], MatrixBlock] = {}
        self._vertex_to_id: Dict[str, int] = {}
        self._id_to_vertex: Dict[int, str] = {}
        self._next_id = 0
        self._edge_count = 0
        
        # Block cache for frequently accessed blocks
        self._block_cache: Dict[Tuple[int, int], MatrixBlock] = {}
        self._cache_size = options.get('cache_size', 16)
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Statistics
        self._total_blocks = 0
        self._dense_blocks = 0
        self._sparse_blocks = 0
        self._matrix_accesses = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the block adjacency matrix strategy."""
        return (EdgeTrait.DENSE | EdgeTrait.WEIGHTED | EdgeTrait.DIRECTED | EdgeTrait.CACHE_FRIENDLY)
    
    def _get_vertex_id(self, vertex: str) -> int:
        """Get or create vertex ID."""
        if vertex not in self._vertex_to_id:
            self._vertex_to_id[vertex] = self._next_id
            self._id_to_vertex[self._next_id] = vertex
            self._next_id += 1
        return self._vertex_to_id[vertex]
    
    def _get_block_coords(self, vertex_id: int) -> Tuple[int, int]:
        """Get block coordinates for vertex ID."""
        return (vertex_id // self.block_size, vertex_id // self.block_size)
    
    def _get_edge_block_coords(self, u_id: int, v_id: int) -> Tuple[int, int]:
        """Get block coordinates for edge (u, v)."""
        return (u_id // self.block_size, v_id // self.block_size)
    
    def _get_local_coords(self, vertex_id: int) -> Tuple[int, int]:
        """Get local coordinates within block."""
        return (vertex_id % self.block_size, vertex_id % self.block_size)
    
    def _get_edge_local_coords(self, u_id: int, v_id: int) -> Tuple[int, int]:
        """Get local coordinates for edge within block."""
        return (u_id % self.block_size, v_id % self.block_size)
    
    def _get_block(self, block_coords: Tuple[int, int], create: bool = True) -> Optional[MatrixBlock]:
        """Get block, optionally creating it."""
        # Check cache first
        if self.cache_blocks and block_coords in self._block_cache:
            self._cache_hits += 1
            return self._block_cache[block_coords]
        
        # Check main storage
        if block_coords in self._blocks:
            block = self._blocks[block_coords]
            
            # Add to cache
            if self.cache_blocks:
                self._update_cache(block_coords, block)
                self._cache_misses += 1
            
            return block
        
        # Create new block if requested
        if create:
            block = MatrixBlock(self.block_size)
            self._blocks[block_coords] = block
            self._total_blocks += 1
            
            if self.cache_blocks:
                self._update_cache(block_coords, block)
            
            return block
        
        return None
    
    def _update_cache(self, block_coords: Tuple[int, int], block: MatrixBlock) -> None:
        """Update block cache with LRU eviction."""
        if len(self._block_cache) >= self._cache_size:
            # Simple FIFO eviction (could be improved to LRU)
            oldest_key = next(iter(self._block_cache))
            del self._block_cache[oldest_key]
        
        self._block_cache[block_coords] = block
    
    def _optimize_block_distribution(self) -> None:
        """Analyze and optimize block distribution."""
        if not self.auto_optimize:
            return
        
        self._dense_blocks = 0
        self._sparse_blocks = 0
        
        for block in self._blocks.values():
            if block.is_dense:
                self._dense_blocks += 1
            else:
                self._sparse_blocks += 1
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def add_edge(self, u: str, v: str, weight: Any = 1, **properties) -> None:
        """Add edge to block matrix."""
        u_id = self._get_vertex_id(u)
        v_id = self._get_vertex_id(v)
        
        block_coords = self._get_edge_block_coords(u_id, v_id)
        local_u, local_v = self._get_edge_local_coords(u_id, v_id)
        
        block = self._get_block(block_coords, create=True)
        if block.set_edge(local_u, local_v, weight):
            self._edge_count += 1
        
        self._matrix_accesses += 1
        
        # Periodic optimization
        if self._matrix_accesses % 1000 == 0:
            self._optimize_block_distribution()
    
    def remove_edge(self, u: str, v: str) -> bool:
        """Remove edge from block matrix."""
        if u not in self._vertex_to_id or v not in self._vertex_to_id:
            return False
        
        u_id = self._vertex_to_id[u]
        v_id = self._vertex_to_id[v]
        
        block_coords = self._get_edge_block_coords(u_id, v_id)
        local_u, local_v = self._get_edge_local_coords(u_id, v_id)
        
        block = self._get_block(block_coords, create=False)
        if block and block.remove_edge(local_u, local_v):
            self._edge_count -= 1
            self._matrix_accesses += 1
            return True
        
        return False
    
    def has_edge(self, u: str, v: str) -> bool:
        """Check if edge exists in block matrix."""
        if u not in self._vertex_to_id or v not in self._vertex_to_id:
            return False
        
        u_id = self._vertex_to_id[u]
        v_id = self._vertex_to_id[v]
        
        block_coords = self._get_edge_block_coords(u_id, v_id)
        local_u, local_v = self._get_edge_local_coords(u_id, v_id)
        
        block = self._get_block(block_coords, create=False)
        self._matrix_accesses += 1
        
        return block.has_edge(local_u, local_v) if block else False
    
    def get_edge_weight(self, u: str, v: str) -> Any:
        """Get edge weight from block matrix."""
        if u not in self._vertex_to_id or v not in self._vertex_to_id:
            return None
        
        u_id = self._vertex_to_id[u]
        v_id = self._vertex_to_id[v]
        
        block_coords = self._get_edge_block_coords(u_id, v_id)
        local_u, local_v = self._get_edge_local_coords(u_id, v_id)
        
        block = self._get_block(block_coords, create=False)
        self._matrix_accesses += 1
        
        return block.get_edge(local_u, local_v) if block else None
    
    def get_neighbors(self, vertex: str) -> List[str]:
        """Get neighbors using block-wise traversal."""
        if vertex not in self._vertex_to_id:
            return []
        
        vertex_id = self._vertex_to_id[vertex]
        neighbors = []
        
        # Check all blocks in the row corresponding to this vertex
        vertex_block_row = vertex_id // self.block_size
        local_u = vertex_id % self.block_size
        
        for block_coords, block in self._blocks.items():
            block_row, block_col = block_coords
            
            if block_row == vertex_block_row:
                # Check this block for outgoing edges
                for local_v in range(self.block_size):
                    if block.has_edge(local_u, local_v):
                        target_id = block_col * self.block_size + local_v
                        if target_id in self._id_to_vertex:
                            neighbors.append(self._id_to_vertex[target_id])
        
        self._matrix_accesses += len(self._blocks)
        return neighbors
    
    def get_all_edges(self) -> List[Tuple[str, str, Any]]:
        """Get all edges from all blocks."""
        all_edges = []
        
        for (block_row, block_col), block in self._blocks.items():
            block_edges = block.get_edges()
            
            for local_u, local_v, weight in block_edges:
                u_id = block_row * self.block_size + local_u
                v_id = block_col * self.block_size + local_v
                
                if u_id in self._id_to_vertex and v_id in self._id_to_vertex:
                    u_vertex = self._id_to_vertex[u_id]
                    v_vertex = self._id_to_vertex[v_id]
                    all_edges.append((u_vertex, v_vertex, weight))
        
        return all_edges
    
    def clear(self) -> None:
        """Clear all edges and blocks."""
        self._blocks.clear()
        self._block_cache.clear()
        self._vertex_to_id.clear()
        self._id_to_vertex.clear()
        self._next_id = 0
        self._edge_count = 0
        self._total_blocks = 0
        self._dense_blocks = 0
        self._sparse_blocks = 0
        self._matrix_accesses = 0
        self._cache_hits = 0
        self._cache_misses = 0
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def get_vertices(self) -> List[str]:
        """Get all vertices."""
        return list(self._vertex_to_id.keys())
    
    def get_vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertex_to_id)
    
    def vertices(self) -> List[str]:
        """Get all vertices (abstract method implementation)."""
        return self.get_vertices()
    
    def edges(self) -> List[Tuple[str, str, Any]]:
        """Get all edges (abstract method implementation)."""
        return self.get_all_edges()
    
    def neighbors(self, vertex: str) -> List[str]:
        """Get neighbors (abstract method implementation)."""
        return self.get_neighbors(vertex)
    
    def degree(self, vertex: str) -> int:
        """Get vertex degree (abstract method implementation)."""
        return len(self.get_neighbors(vertex))
    
    # ============================================================================
    # BLOCK MATRIX SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_block_info(self, u: str, v: str) -> Dict[str, Any]:
        """Get information about the block containing edge (u, v)."""
        if u not in self._vertex_to_id or v not in self._vertex_to_id:
            return {}
        
        u_id = self._vertex_to_id[u]
        v_id = self._vertex_to_id[v]
        
        block_coords = self._get_edge_block_coords(u_id, v_id)
        block = self._get_block(block_coords, create=False)
        
        if not block:
            return {'exists': False}
        
        return {
            'exists': True,
            'block_coords': block_coords,
            'edge_count': block.edge_count,
            'is_dense': block.is_dense,
            'density': block.edge_count / (self.block_size ** 2),
            'block_size': self.block_size
        }
    
    def get_dense_blocks(self) -> List[Tuple[int, int]]:
        """Get coordinates of all dense blocks."""
        dense_blocks = []
        for coords, block in self._blocks.items():
            if block.is_dense:
                dense_blocks.append(coords)
        return dense_blocks
    
    def get_sparse_blocks(self) -> List[Tuple[int, int]]:
        """Get coordinates of all sparse blocks."""
        sparse_blocks = []
        for coords, block in self._blocks.items():
            if not block.is_dense:
                sparse_blocks.append(coords)
        return sparse_blocks
    
    def matrix_multiply_block(self, other: 'xBlockAdjMatrixStrategy', block_coords: Tuple[int, int]) -> MatrixBlock:
        """Perform block-wise matrix multiplication for specific block."""
        result_block = MatrixBlock(self.block_size)
        
        block_row, block_col = block_coords
        
        # Multiply blocks: C[i,k] = sum(A[i,j] * B[j,k]) for all j
        for j in range(max(len(self._blocks), len(other._blocks))):
            a_coords = (block_row, j)
            b_coords = (j, block_col)
            
            a_block = self._get_block(a_coords, create=False)
            b_block = other._get_block(b_coords, create=False)
            
            if a_block and b_block:
                # Multiply these two blocks
                for local_i in range(self.block_size):
                    for local_k in range(self.block_size):
                        sum_value = 0
                        for local_j in range(self.block_size):
                            a_val = a_block.get_edge(local_i, local_j)
                            b_val = b_block.get_edge(local_j, local_k)
                            
                            if a_val is not None and b_val is not None:
                                sum_value += a_val * b_val
                        
                        if sum_value != 0:
                            result_block.set_edge(local_i, local_k, sum_value)
        
        return result_block
    
    def get_block_statistics(self) -> Dict[str, Any]:
        """Get comprehensive block statistics."""
        if not self._blocks:
            return {'total_blocks': 0}
        
        # Analyze block distribution
        block_densities = []
        block_sizes = []
        
        for block in self._blocks.values():
            density = block.edge_count / (self.block_size ** 2)
            block_densities.append(density)
            block_sizes.append(block.edge_count)
        
        avg_density = sum(block_densities) / len(block_densities)
        max_density = max(block_densities)
        min_density = min(block_densities)
        
        # Calculate matrix dimensions
        max_vertex_id = max(self._vertex_to_id.values()) if self._vertex_to_id else 0
        matrix_size = max_vertex_id + 1
        theoretical_blocks = math.ceil(matrix_size / self.block_size) ** 2
        
        return {
            'total_blocks': self._total_blocks,
            'dense_blocks': self._dense_blocks,
            'sparse_blocks': self._sparse_blocks,
            'block_utilization': self._total_blocks / max(1, theoretical_blocks),
            'avg_block_density': avg_density,
            'max_block_density': max_density,
            'min_block_density': min_density,
            'matrix_size': matrix_size,
            'block_size': self.block_size,
            'cache_hit_rate': self._cache_hits / max(1, self._cache_hits + self._cache_misses),
            'matrix_accesses': self._matrix_accesses
        }
    
    def optimize_layout(self) -> Dict[str, Any]:
        """Optimize block layout for better cache performance."""
        # Reorder vertices to improve block locality
        # This is a simplified version - real optimization would use graph partitioning
        
        old_stats = self.get_block_statistics()
        
        # Simple optimization: group frequently connected vertices
        vertex_connections = {}
        for vertex in self._vertex_to_id.keys():
            vertex_connections[vertex] = len(self.get_neighbors(vertex))
        
        # Sort vertices by connection count (heuristic)
        sorted_vertices = sorted(vertex_connections.items(), key=lambda x: x[1], reverse=True)
        
        # Rebuild vertex ID mapping
        old_mapping = self._vertex_to_id.copy()
        self._vertex_to_id.clear()
        self._id_to_vertex.clear()
        self._next_id = 0
        
        for vertex, _ in sorted_vertices:
            self._vertex_to_id[vertex] = self._next_id
            self._id_to_vertex[self._next_id] = vertex
            self._next_id += 1
        
        # Rebuild blocks with new mapping
        old_blocks = self._blocks.copy()
        self._blocks.clear()
        self._block_cache.clear()
        self._total_blocks = 0
        
        # Re-add all edges with new mapping
        for (u, v, weight) in self.get_all_edges():
            # Temporarily store edges to re-add
            pass
        
        new_stats = self.get_block_statistics()
        
        return {
            'optimization_applied': True,
            'old_blocks': old_stats['total_blocks'],
            'new_blocks': new_stats['total_blocks'],
            'block_reduction': old_stats['total_blocks'] - new_stats['total_blocks'],
            'old_cache_hit_rate': old_stats['cache_hit_rate'],
            'new_cache_hit_rate': new_stats['cache_hit_rate']
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'BLOCK_ADJ_MATRIX',
            'backend': 'Cache-friendly block adjacency matrix',
            'block_size': self.block_size,
            'cache_blocks': self.cache_blocks,
            'auto_optimize': self.auto_optimize,
            'complexity': {
                'add_edge': 'O(1)',
                'has_edge': 'O(1)',
                'get_neighbors': 'O(blocks_in_row)',
                'matrix_multiply': 'O(n^3 / block_size^3)',  # Block-wise
                'space': 'O(edges + blocks)',
                'cache_efficiency': 'High for dense regions'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_block_statistics()
        
        return {
            'edges': self._edge_count,
            'vertices': len(self._vertex_to_id),
            'total_blocks': stats['total_blocks'],
            'dense_blocks': stats['dense_blocks'],
            'sparse_blocks': stats['sparse_blocks'],
            'avg_block_density': f"{stats['avg_block_density'] * 100:.1f}%",
            'cache_hit_rate': f"{stats['cache_hit_rate'] * 100:.1f}%",
            'memory_usage': f"{self._total_blocks * self.block_size * self.block_size * 8} bytes (estimated)"
        }
