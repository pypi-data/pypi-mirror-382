"""
CSC (Compressed Sparse Column) Edge Strategy Implementation

This module implements the CSC strategy for sparse graph representation
using compressed sparse column format for efficient column operations.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import defaultdict
import bisect
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class xCSCStrategy(aEdgeStrategy):
    """
    CSC (Compressed Sparse Column) edge strategy for sparse graphs.
    
    Optimized for column-wise operations and efficient sparse matrix
    computations with compressed storage format.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the CSC strategy."""
        super().__init__(EdgeMode.CSC, traits, **options)
        
        self.weighted = options.get('weighted', True)
        self.allow_duplicates = options.get('allow_duplicates', False)
        
        # CSC format: Compressed Sparse Column
        # col_ptr[j] to col_ptr[j+1] gives range in row_indices/values for column j
        self._col_ptr: List[int] = [0]  # Column pointers
        self._row_indices: List[int] = []  # Row indices
        self._values: List[float] = []  # Edge values/weights
        
        # Vertex management
        self._vertices: Set[str] = set()
        self._vertex_to_id: Dict[str, int] = {}
        self._id_to_vertex: Dict[int, str] = {}
        self._next_vertex_id = 0
        
        # Matrix dimensions
        self._num_rows = 0
        self._num_cols = 0
        self._nnz = 0  # Number of non-zeros
        
        # Quick access for compatibility
        self._edge_count = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the CSC strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.COMPRESSED | EdgeTrait.CACHE_FRIENDLY | EdgeTrait.COLUMNAR)
    
    def _get_or_create_vertex_id(self, vertex: str) -> int:
        """Get or create vertex ID."""
        if vertex not in self._vertex_to_id:
            vertex_id = self._next_vertex_id
            self._vertex_to_id[vertex] = vertex_id
            self._id_to_vertex[vertex_id] = vertex
            self._vertices.add(vertex)
            self._next_vertex_id += 1
            return vertex_id
        return self._vertex_to_id[vertex]
    
    def _expand_matrix(self, new_rows: int, new_cols: int) -> None:
        """Expand matrix dimensions if needed."""
        if new_rows > self._num_rows:
            self._num_rows = new_rows
        
        if new_cols > self._num_cols:
            # Add empty columns
            for _ in range(self._num_cols, new_cols):
                self._col_ptr.append(len(self._row_indices))
            self._num_cols = new_cols
    
    def _find_edge_in_column(self, col: int, row: int) -> int:
        """Find edge position in column, returns -1 if not found."""
        start = self._col_ptr[col]
        end = self._col_ptr[col + 1] if col + 1 < len(self._col_ptr) else len(self._row_indices)
        
        # Binary search in sorted row indices
        left, right = start, end - 1
        while left <= right:
            mid = (left + right) // 2
            if self._row_indices[mid] == row:
                return mid
            elif self._row_indices[mid] < row:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    
    def _insert_edge_in_column(self, col: int, row: int, value: float) -> None:
        """Insert edge in column maintaining sorted order."""
        start = self._col_ptr[col]
        end = self._col_ptr[col + 1] if col + 1 < len(self._col_ptr) else len(self._row_indices)
        
        # Find insertion position
        pos = bisect.bisect_left(self._row_indices, row, start, end)
        
        # Insert at position
        self._row_indices.insert(pos, row)
        self._values.insert(pos, value)
        
        # Update column pointers for columns after this one
        for i in range(col + 1, len(self._col_ptr)):
            self._col_ptr[i] += 1
        
        self._nnz += 1
    
    def _remove_edge_from_column(self, col: int, pos: int) -> None:
        """Remove edge from column at given position."""
        del self._row_indices[pos]
        del self._values[pos]
        
        # Update column pointers for columns after this one
        for i in range(col + 1, len(self._col_ptr)):
            self._col_ptr[i] -= 1
        
        self._nnz -= 1
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge to CSC matrix."""
        # In CSC: source = row, target = column
        row_id = self._get_or_create_vertex_id(source)
        col_id = self._get_or_create_vertex_id(target)
        
        weight = properties.get('weight', 1.0) if self.weighted else 1.0
        
        # Expand matrix if needed
        self._expand_matrix(row_id + 1, col_id + 1)
        
        # Check if edge exists
        pos = self._find_edge_in_column(col_id, row_id)
        
        if pos != -1:
            if not self.allow_duplicates:
                # Update existing edge
                self._values[pos] = weight
                return f"{source}->{target}"
            # else: allow duplicate, fall through to insert
        
        # Insert new edge
        self._insert_edge_in_column(col_id, row_id, weight)
        self._edge_count += 1
        
        return f"{source}->{target}"
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge from CSC matrix."""
        if source not in self._vertex_to_id or target not in self._vertex_to_id:
            return False
        
        row_id = self._vertex_to_id[source]
        col_id = self._vertex_to_id[target]
        
        if col_id >= self._num_cols:
            return False
        
        pos = self._find_edge_in_column(col_id, row_id)
        if pos != -1:
            self._remove_edge_from_column(col_id, pos)
            self._edge_count -= 1
            return True
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        if source not in self._vertex_to_id or target not in self._vertex_to_id:
            return False
        
        row_id = self._vertex_to_id[source]
        col_id = self._vertex_to_id[target]
        
        if col_id >= self._num_cols:
            return False
        
        return self._find_edge_in_column(col_id, row_id) != -1
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        if not self.has_edge(source, target):
            return None
        
        row_id = self._vertex_to_id[source]
        col_id = self._vertex_to_id[target]
        pos = self._find_edge_in_column(col_id, row_id)
        
        return {
            'source': source,
            'target': target,
            'weight': self._values[pos],
            'row_id': row_id,
            'col_id': col_id
        }
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of vertex."""
        if vertex not in self._vertex_to_id:
            return
        
        vertex_id = self._vertex_to_id[vertex]
        
        if direction in ['out', 'both']:
            # Outgoing: vertex is source (row), find all columns with this row
            for col in range(self._num_cols):
                if self._find_edge_in_column(col, vertex_id) != -1:
                    yield self._id_to_vertex[col]
        
        if direction in ['in', 'both']:
            # Incoming: vertex is target (column), get all rows in this column
            if vertex_id < self._num_cols:
                start = self._col_ptr[vertex_id]
                end = self._col_ptr[vertex_id + 1] if vertex_id + 1 < len(self._col_ptr) else len(self._row_indices)
                
                for i in range(start, end):
                    row_id = self._row_indices[i]
                    if row_id in self._id_to_vertex:
                        yield self._id_to_vertex[row_id]
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex."""
        return len(list(self.neighbors(vertex, direction)))
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for col in range(self._num_cols):
            start = self._col_ptr[col]
            end = self._col_ptr[col + 1] if col + 1 < len(self._col_ptr) else len(self._row_indices)
            
            target = self._id_to_vertex.get(col)
            if not target:
                continue
            
            for i in range(start, end):
                row = self._row_indices[i]
                source = self._id_to_vertex.get(row)
                if not source:
                    continue
                
                if data:
                    edge_data = {
                        'weight': self._values[i],
                        'row_id': row,
                        'col_id': col
                    }
                    yield (source, target, edge_data)
                else:
                    yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all data."""
        self._col_ptr = [0]
        self._row_indices.clear()
        self._values.clear()
        self._vertices.clear()
        self._vertex_to_id.clear()
        self._id_to_vertex.clear()
        
        self._num_rows = 0
        self._num_cols = 0
        self._nnz = 0
        self._edge_count = 0
        self._next_vertex_id = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex to graph."""
        self._get_or_create_vertex_id(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertex_to_id:
            return False
        
        vertex_id = self._vertex_to_id[vertex]
        
        # Remove all edges involving this vertex
        # This is expensive in CSC format - requires rebuilding
        edges_to_remove = []
        for source, target in self.edges():
            if source == vertex or target == vertex:
                edges_to_remove.append((source, target))
        
        for source, target in edges_to_remove:
            self.remove_edge(source, target)
        
        # Remove vertex
        del self._vertex_to_id[vertex]
        del self._id_to_vertex[vertex_id]
        self._vertices.remove(vertex)
        
        return True
    
    # ============================================================================
    # CSC SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_column(self, target: str) -> List[Tuple[str, float]]:
        """Get all incoming edges to target vertex (column in CSC)."""
        if target not in self._vertex_to_id:
            return []
        
        col_id = self._vertex_to_id[target]
        if col_id >= self._num_cols:
            return []
        
        result = []
        start = self._col_ptr[col_id]
        end = self._col_ptr[col_id + 1] if col_id + 1 < len(self._col_ptr) else len(self._row_indices)
        
        for i in range(start, end):
            row_id = self._row_indices[i]
            source = self._id_to_vertex.get(row_id)
            if source:
                result.append((source, self._values[i]))
        
        return result
    
    def matrix_vector_multiply(self, vector: Dict[str, float]) -> Dict[str, float]:
        """Multiply CSC matrix with vector (efficient column-wise)."""
        result = defaultdict(float)
        
        for col in range(self._num_cols):
            col_vertex = self._id_to_vertex.get(col)
            if not col_vertex or col_vertex not in vector:
                continue
            
            col_value = vector[col_vertex]
            start = self._col_ptr[col]
            end = self._col_ptr[col + 1] if col + 1 < len(self._col_ptr) else len(self._row_indices)
            
            for i in range(start, end):
                row_id = self._row_indices[i]
                row_vertex = self._id_to_vertex.get(row_id)
                if row_vertex:
                    result[row_vertex] += self._values[i] * col_value
        
        return dict(result)
    
    def get_sparsity(self) -> float:
        """Get sparsity ratio (fraction of zero entries)."""
        total_entries = self._num_rows * self._num_cols
        if total_entries == 0:
            return 0.0
        return 1.0 - (self._nnz / total_entries)
    
    def compress(self) -> None:
        """Compress storage by removing empty columns."""
        # Remove empty columns at the end
        while self._num_cols > 0 and self._col_ptr[self._num_cols - 1] == self._col_ptr[self._num_cols]:
            self._num_cols -= 1
            self._col_ptr.pop()
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get detailed memory usage."""
        return {
            'col_ptr_bytes': len(self._col_ptr) * 4,  # 4 bytes per int
            'row_indices_bytes': len(self._row_indices) * 4,
            'values_bytes': len(self._values) * 8,  # 8 bytes per float
            'vertex_mapping_bytes': len(self._vertices) * 50,  # Estimated
            'total_bytes': (len(self._col_ptr) + len(self._row_indices)) * 4 + len(self._values) * 8 + len(self._vertices) * 50
        }
    
    def export_matrix(self) -> Dict[str, Any]:
        """Export CSC matrix data."""
        return {
            'col_ptr': self._col_ptr.copy(),
            'row_indices': self._row_indices.copy(),
            'values': self._values.copy(),
            'vertex_to_id': self._vertex_to_id.copy(),
            'id_to_vertex': self._id_to_vertex.copy(),
            'dimensions': (self._num_rows, self._num_cols),
            'nnz': self._nnz
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive CSC statistics."""
        memory = self.get_memory_usage()
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'matrix_dimensions': (self._num_rows, self._num_cols),
            'nnz': self._nnz,
            'sparsity': self.get_sparsity(),
            'density': 1.0 - self.get_sparsity(),
            'avg_edges_per_column': self._nnz / max(1, self._num_cols),
            'compression_ratio': self._nnz / max(1, self._num_rows * self._num_cols),
            'memory_usage': memory['total_bytes'],
            'weighted': self.weighted,
            'allow_duplicates': self.allow_duplicates
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'CSC',
            'backend': 'Compressed Sparse Column matrix format',
            'weighted': self.weighted,
            'allow_duplicates': self.allow_duplicates,
            'complexity': {
                'add_edge': 'O(log k)',  # k = edges in column
                'remove_edge': 'O(log k)',
                'has_edge': 'O(log k)',
                'column_access': 'O(1)',
                'matrix_vector_mult': 'O(nnz)',
                'space': 'O(nnz + vertices)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        
        return {
            'vertices': stats['vertices'],
            'edges': stats['edges'],
            'matrix_size': f"{stats['matrix_dimensions'][0]}x{stats['matrix_dimensions'][1]}",
            'sparsity': f"{stats['sparsity'] * 100:.1f}%",
            'nnz': stats['nnz'],
            'avg_edges_per_col': f"{stats['avg_edges_per_column']:.1f}",
            'memory_usage': f"{stats['memory_usage']} bytes"
        }
