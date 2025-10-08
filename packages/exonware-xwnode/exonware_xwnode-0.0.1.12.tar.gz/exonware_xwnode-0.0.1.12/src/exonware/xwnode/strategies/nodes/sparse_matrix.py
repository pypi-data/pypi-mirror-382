"""
Sparse Matrix Strategy Implementation

Implements a sparse matrix using coordinate format (COO) for memory efficiency.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

from typing import Any, Iterator, List, Optional, Dict, Union, Tuple
from .base import ANodeMatrixStrategy
from ...types import NodeMode, NodeTrait


class SparseMatrixStrategy(ANodeMatrixStrategy):
    """
    Sparse Matrix node strategy for memory-efficient matrix operations.
    
    Uses coordinate format (COO) to store only non-zero elements,
    providing excellent memory efficiency for sparse matrices.
    """
    
    def __init__(self):
        """Initialize an empty sparse matrix."""
        super().__init__()
        self._data: List[Tuple[int, int, Any]] = []  # (row, col, value)
        self._rows = 0
        self._cols = 0
        self._mode = NodeMode.SPARSE_MATRIX
        self._traits = {NodeTrait.SPARSE, NodeTrait.MEMORY_EFFICIENT, NodeTrait.MATRIX_OPS}
    
    def insert(self, key: str, value: Any) -> None:
        """Insert a value using key as coordinate (e.g., '1,2' for row 1, col 2)."""
        try:
            row, col = map(int, key.split(','))
            self.set_at_position(row, col, value)
        except ValueError:
            raise ValueError(f"Key must be in format 'row,col', got: {key}")
    
    def find(self, key: str) -> Optional[Any]:
        """Find a value using key as coordinate."""
        try:
            row, col = map(int, key.split(','))
            return self.get_at_position(row, col)
        except ValueError:
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a value using key as coordinate."""
        try:
            row, col = map(int, key.split(','))
            return self.set_at_position(row, col, 0) is not None
        except ValueError:
            return False
    
    def size(self) -> int:
        """Get the number of non-zero elements."""
        return len(self._data)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert sparse matrix to native dictionary format."""
        result = {}
        for row, col, value in self._data:
            result[f"{row},{col}"] = value
        return result
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load sparse matrix from native dictionary format."""
        self._data.clear()
        for key, value in data.items():
            try:
                row, col = map(int, key.split(','))
                if value != 0:  # Only store non-zero values
                    self._data.append((row, col, value))
                    self._rows = max(self._rows, row + 1)
                    self._cols = max(self._cols, col + 1)
            except ValueError:
                continue
    
    def get_dimensions(self) -> Tuple[int, int]:
        """Get matrix dimensions (rows, cols)."""
        return (self._rows, self._cols)
    
    def get_at_position(self, row: int, col: int) -> Any:
        """Get value at specific position."""
        for r, c, value in self._data:
            if r == row and c == col:
                return value
        return 0  # Default to 0 for sparse matrix
    
    def set_at_position(self, row: int, col: int, value: Any) -> None:
        """Set value at specific position."""
        # Remove existing entry if it exists
        self._data = [(r, c, v) for r, c, v in self._data if not (r == row and c == col)]
        
        # Add new entry if value is not zero
        if value != 0:
            self._data.append((row, col, value))
        
        # Update dimensions
        self._rows = max(self._rows, row + 1)
        self._cols = max(self._cols, col + 1)
    
    def get_row(self, row: int) -> List[Any]:
        """Get entire row as list."""
        result = [0] * self._cols
        for r, c, value in self._data:
            if r == row:
                result[c] = value
        return result
    
    def get_column(self, col: int) -> List[Any]:
        """Get entire column as list."""
        result = [0] * self._rows
        for r, c, value in self._data:
            if c == col:
                result[r] = value
        return result
    
    def transpose(self) -> 'SparseMatrixStrategy':
        """Return transposed matrix."""
        transposed = SparseMatrixStrategy()
        for row, col, value in self._data:
            transposed.set_at_position(col, row, value)
        return transposed
    
    def multiply(self, other: 'SparseMatrixStrategy') -> 'SparseMatrixStrategy':
        """Multiply with another sparse matrix."""
        result = SparseMatrixStrategy()
        other_dict = {}
        for r, c, v in other._data:
            other_dict[(r, c)] = v
        
        for r1, c1, v1 in self._data:
            for c2 in range(other._cols):
                if (c1, c2) in other_dict:
                    v2 = other_dict[(c1, c2)]
                    current = result.get_at_position(r1, c2)
                    result.set_at_position(r1, c2, current + v1 * v2)
        
        return result
    
    def add(self, other: 'SparseMatrixStrategy') -> 'SparseMatrixStrategy':
        """Add another sparse matrix."""
        result = SparseMatrixStrategy()
        
        # Add all elements from self
        for r, c, v in self._data:
            result.set_at_position(r, c, v)
        
        # Add all elements from other
        for r, c, v in other._data:
            current = result.get_at_position(r, c)
            result.set_at_position(r, c, current + v)
        
        return result
    
    def as_adjacency_matrix(self):
        """Convert to adjacency matrix format."""
        return self
    
    def as_incidence_matrix(self):
        """Convert to incidence matrix format."""
        return self
    
    def as_sparse_matrix(self):
        """Return self as sparse matrix."""
        return self
    
    def density(self) -> float:
        """Calculate matrix density (non-zero elements / total elements)."""
        total_elements = self._rows * self._cols
        if total_elements == 0:
            return 0.0
        return len(self._data) / total_elements
    
    def clear(self) -> None:
        """Clear all elements."""
        self._data.clear()
        self._rows = 0
        self._cols = 0
    
    def __iter__(self) -> Iterator[Tuple[int, int, Any]]:
        """Iterate through non-zero elements."""
        for row, col, value in self._data:
            yield (row, col, value)
    
    def __repr__(self) -> str:
        """String representation of the sparse matrix."""
        return f"SparseMatrixStrategy({self._rows}x{self._cols}, {len(self._data)} non-zero)"
    
    # Required abstract methods from base classes
    def as_adjacency_matrix(self):
        """Provide Adjacency Matrix behavioral view."""
        return self
    
    def as_incidence_matrix(self):
        """Provide Incidence Matrix behavioral view."""
        return self
    
    def as_sparse_matrix(self):
        """Provide Sparse Matrix behavioral view."""
        return self
