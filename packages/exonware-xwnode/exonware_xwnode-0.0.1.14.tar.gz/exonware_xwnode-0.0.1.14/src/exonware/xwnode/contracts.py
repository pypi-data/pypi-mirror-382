#!/usr/bin/env python3
"""
Contract interfaces for XWNode Strategy Pattern.

This module defines the contracts that all node and edge strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional, Dict, List, Union, Callable
from enum import Enum, Flag

# Import all enums from types.py to avoid circular references
from .types import (
    NodeMode, EdgeMode, NodeTrait, EdgeTrait, QueryMode, QueryTrait
)


class iNodeStrategy(ABC):
    """
    Abstract interface for node strategies.
    
    All node strategies must implement this interface to ensure
    compatibility with the XWNode facade.
    """
    
    @abstractmethod
    def create_from_data(self, data: Any) -> 'iNodeStrategy':
        """Create a new strategy instance from data."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['iNodeStrategy']:
        """Get a child node by path."""
        pass
    
    @abstractmethod
    def put(self, path: str, value: Any) -> 'iNodeStrategy':
        """Set a value at path."""
        pass
    
    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete a node at path."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        pass
    
    @abstractmethod
    def keys(self) -> Iterator[str]:
        """Get keys (for dict-like nodes)."""
        pass
    
    @abstractmethod
    def values(self) -> Iterator['iNodeStrategy']:
        """Get values (for dict-like nodes)."""
        pass
    
    @abstractmethod
    def items(self) -> Iterator[tuple[str, 'iNodeStrategy']]:
        """Get items (for dict-like nodes)."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator['iNodeStrategy']:
        """Iterate over children."""
        pass
    
    @abstractmethod
    def __getitem__(self, key: Union[str, int]) -> 'iNodeStrategy':
        """Get child by key or index."""
        pass
    
    @abstractmethod
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        pass
    
    @abstractmethod
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        pass
    
    # Type checking properties
    @property
    @abstractmethod
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        pass
    
    @property
    @abstractmethod
    def is_list(self) -> bool:
        """Check if this is a list node."""
        pass
    
    @property
    @abstractmethod
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        pass
    
    @property
    @abstractmethod
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        pass
    
    @property
    @abstractmethod
    def is_object(self) -> bool:
        """Check if this is an object node."""
        pass
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Get the type of this node."""
        pass
    
    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the value of this node."""
        pass
    
    # Optional properties with default implementations
    @property
    def uri(self) -> Optional[str]:
        """Get URI (for reference/object nodes)."""
        return None
    
    @property
    def reference_type(self) -> Optional[str]:
        """Get reference type (for reference nodes)."""
        return None
    
    @property
    def object_type(self) -> Optional[str]:
        """Get object type (for object nodes)."""
        return None
    
    @property
    def mime_type(self) -> Optional[str]:
        """Get MIME type (for object nodes)."""
        return None
    
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata (for reference/object nodes)."""
        return None
    
    # Strategy information
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass
    
    @property
    @abstractmethod
    def supported_traits(self) -> List[NodeTrait]:
        """Get supported traits for this strategy."""
        pass


class iEdgeStrategy(ABC):
    """
    Abstract interface for edge strategies.
    
    All edge strategies must implement this interface to ensure
    compatibility with the XWNode graph operations, including advanced
    features like edge types, weights, properties, and graph algorithms.
    """
    
    @abstractmethod
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with advanced properties."""
        pass
    
    @abstractmethod
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove an edge between source and target."""
        pass
    
    @abstractmethod
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> List[str]:
        """Get neighbors of a node with optional filtering."""
        pass
    
    @abstractmethod
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        """Get all edges with metadata."""
        pass
    
    @abstractmethod
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get edge data/properties."""
        pass
    
    @abstractmethod
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> List[str]:
        """Find shortest path between nodes."""
        pass
    
    @abstractmethod
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> List[List[str]]:
        """Find cycles in the graph."""
        pass
    
    @abstractmethod
    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: Optional[str] = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        pass
    
    @abstractmethod
    def is_connected(self, source: str, target: str, edge_type: Optional[str] = None) -> bool:
        """Check if nodes are connected."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get number of edges."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over edges with full metadata."""
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass
    
    @property
    @abstractmethod
    def supported_traits(self) -> List[EdgeTrait]:
        """Get supported traits for this strategy."""
        pass


class iEdge(ABC):
    """
    Abstract interface for edge facade.
    
    This defines the public interface for edge operations with advanced features
    including edge types, weights, properties, and graph algorithms.
    """
    
    @abstractmethod
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with advanced properties."""
        pass
    
    @abstractmethod
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove an edge between source and target."""
        pass
    
    @abstractmethod
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> List[str]:
        """Get neighbors of a node with optional filtering."""
        pass
    
    @abstractmethod
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        """Get all edges with metadata."""
        pass
    
    @abstractmethod
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get edge data/properties."""
        pass
    
    @abstractmethod
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> List[str]:
        """Find shortest path between nodes."""
        pass
    
    @abstractmethod
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> List[List[str]]:
        """Find cycles in the graph."""
        pass
    
    @abstractmethod
    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: Optional[str] = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        pass
    
    @abstractmethod
    def is_connected(self, source: str, target: str, edge_type: Optional[str] = None) -> bool:
        """Check if nodes are connected."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get number of edges."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over edges with full metadata."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def copy(self) -> 'iEdge':
        """Create a deep copy."""
        pass


class iNodeFacade(ABC):
    """
    Abstract interface for the XWNode facade.
    
    This defines the public interface that XWNode must implement.
    """
    
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['iNodeFacade']:
        """Get a node by path."""
        pass
    
    @abstractmethod
    def set(self, path: str, value: Any, in_place: bool = True) -> 'iNodeFacade':
        """Set a value at path."""
        pass
    
    @abstractmethod
    def delete(self, path: str, in_place: bool = True) -> 'iNodeFacade':
        """Delete a node at path."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        pass
    
    @abstractmethod
    def find(self, path: str, in_place: bool = False) -> Optional['iNodeFacade']:
        """Find a node by path."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    @abstractmethod
    def copy(self) -> 'iNodeFacade':
        """Create a deep copy."""
        pass
    
    @abstractmethod
    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        pass
    
    @abstractmethod
    def flatten(self, separator: str = ".") -> Dict[str, Any]:
        """Flatten to dictionary."""
        pass
    
    @abstractmethod
    def merge(self, other: 'iNodeFacade', strategy: str = "replace") -> 'iNodeFacade':
        """Merge with another node."""
        pass
    
    @abstractmethod
    def diff(self, other: 'iNodeFacade') -> Dict[str, Any]:
        """Get differences with another node."""
        pass
    
    @abstractmethod
    def transform(self, transformer: callable) -> 'iNodeFacade':
        """Transform using a function."""
        pass
    
    @abstractmethod
    def select(self, *paths: str) -> Dict[str, 'iNodeFacade']:
        """Select multiple paths."""
        pass
    
    # Container methods
    @abstractmethod
    def __len__(self) -> int:
        """Get length."""
        pass
    
    @abstractmethod
    def __iter__(self) -> Iterator['iNodeFacade']:
        """Iterate over children."""
        pass
    
    @abstractmethod
    def __getitem__(self, key: Union[str, int]) -> 'iNodeFacade':
        """Get child by key or index."""
        pass
    
    @abstractmethod
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        pass
    
    @abstractmethod
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        pass
    
    # Type checking properties
    @property
    @abstractmethod
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        pass
    
    @property
    @abstractmethod
    def is_list(self) -> bool:
        """Check if this is a list node."""
        pass
    
    @property
    @abstractmethod
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        pass
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Get the type of this node."""
        pass
    
    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the value of this node."""
        pass

# ============================================================================
# QUERY INTERFACES
# ============================================================================

# QueryMode and QueryTrait are now imported from types.py


class IQueryStrategy(ABC):
    """
    Abstract interface for query strategies.
    
    All query strategies must implement this interface to ensure
    compatibility with the XWQuery facade and automatic query detection.
    """
    
    @abstractmethod
    def execute(self, query_string: str, context: Dict[str, Any] = None) -> 'iQueryResult':
        """Execute a query and return results."""
        pass
    
    @abstractmethod
    def validate_query(self, query_string: str) -> bool:
        """Validate if the query string is valid for this strategy."""
        pass
    
    @abstractmethod
    def get_query_plan(self, query_string: str) -> Dict[str, Any]:
        """Get the execution plan for a query."""
        pass
    
    @abstractmethod
    def get_mode(self) -> QueryMode:
        """Get the query mode this strategy handles."""
        pass
    
    @abstractmethod
    def get_traits(self) -> QueryTrait:
        """Get the traits/capabilities this strategy supports."""
        pass
    
    @abstractmethod
    def can_handle(self, query_string: str) -> bool:
        """Check if this strategy can handle the given query string."""
        pass
    
    @abstractmethod
    def get_supported_operations(self) -> List[str]:
        """Get list of supported query operations."""
        pass
    
    @abstractmethod
    def estimate_complexity(self, query_string: str) -> Dict[str, Any]:
        """Estimate query complexity and resource requirements."""
        pass


# ============================================================================
# QUERY ERROR CLASSES
# ============================================================================

class XWQueryError(Exception):
    """Base exception for all query-related errors."""
    
    def __init__(self, message: str, query_string: str = None, cause: Exception = None):
        super().__init__(message)
        self.query_string = query_string
        self.cause = cause
    
    def __str__(self):
        base_msg = super().__str__()
        if self.query_string:
            return f"{base_msg} (Query: {self.query_string[:100]}...)"
        return base_msg


class XWQueryValidationError(XWQueryError):
    """Raised when query validation fails."""
    pass


class XWQueryExecutionError(XWQueryError):
    """Raised when query execution fails."""
    pass


class XWQueryParseError(XWQueryError):
    """Raised when query parsing fails."""
    pass


class XWQueryTimeoutError(XWQueryError):
    """Raised when query execution times out."""
    pass


class XWQueryNotSupportedError(XWQueryError):
    """Raised when a query operation is not supported."""
    pass


class XWQueryStrategyNotFoundError(XWQueryError):
    """Raised when no suitable query strategy is found."""
    pass


class XWQueryContextError(XWQueryError):
    """Raised when query context is invalid or missing."""
    pass

class iQueryResult(ABC):
    """Interface for query results."""
    
    @property
    @abstractmethod
    def nodes(self) -> List['iNodeFacade']:
        """Get result nodes."""
        pass
    
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Get result metadata."""
        pass
    
    @abstractmethod
    def first(self) -> Optional['iNodeFacade']:
        """Get first result."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get result count."""
        pass
    
    @abstractmethod
    def filter(self, predicate: Callable[['iNodeFacade'], bool]) -> 'iQueryResult':
        """Filter results."""
        pass
    
    @abstractmethod
    def limit(self, limit: int) -> 'iQueryResult':
        """Limit results."""
        pass
    
    @abstractmethod
    def offset(self, offset: int) -> 'iQueryResult':
        """Offset results."""
        pass


class iQueryEngine(ABC):
    """Interface for query engines."""
    
    @abstractmethod
    def execute_query(self, query_string: str, context: Dict[str, Any]) -> iQueryResult:
        """Execute query and return results."""
        pass
    
    @abstractmethod
    def parse_query(self, query_string: str) -> Dict[str, Any]:
        """Parse query string into structured format."""
        pass
    
    @abstractmethod
    def validate_query(self, query_string: str) -> bool:
        """Validate query string."""
        pass


class iQuery(ABC):
    """Interface for query capabilities."""
    
    @abstractmethod
    def query(self, query_string: str, query_type: str = "hybrid", **kwargs) -> iQueryResult:
        """Execute a query."""
        pass
    
    @abstractmethod
    def find_nodes(self, predicate: Callable[['iNodeFacade'], bool], max_results: Optional[int] = None) -> iQueryResult:
        """Find nodes matching predicate."""
        pass
    
    @abstractmethod
    def find_by_path(self, path_pattern: str) -> iQueryResult:
        """Find nodes by path pattern."""
        pass
    
    @abstractmethod
    def find_by_value(self, value: Any, exact_match: bool = True) -> iQueryResult:
        """Find nodes by value."""
        pass
    
    @abstractmethod
    def count_nodes(self, predicate: Optional[Callable[['iNodeFacade'], bool]] = None) -> int:
        """Count nodes matching predicate."""
        pass
    
    @abstractmethod
    def select(self, selector: str, **kwargs) -> List['iNodeFacade']:
        """Select nodes using a selector expression."""
        pass
    
    @abstractmethod
    def filter(self, condition: str, **kwargs) -> List['iNodeFacade']:
        """Filter nodes based on a condition."""
        pass
    
    @abstractmethod
    def where(self, condition: str) -> List['iNodeFacade']:
        """Filter nodes using a where condition."""
        pass
    
    @abstractmethod
    def sort(self, key: str = None, reverse: bool = False) -> List['iNodeFacade']:
        """Sort nodes by a key."""
        pass
    
    @abstractmethod
    def limit(self, count: int) -> List['iNodeFacade']:
        """Limit the number of results."""
        pass
    
    @abstractmethod
    def skip(self, count: int) -> List['iNodeFacade']:
        """Skip a number of results."""
        pass
    
    @abstractmethod
    def first(self) -> Optional['iNodeFacade']:
        """Get the first result."""
        pass
    
    @abstractmethod
    def last(self) -> Optional['iNodeFacade']:
        """Get the last result."""
        pass
    
    @abstractmethod
    def group_by(self, key: str) -> Dict[str, List['iNodeFacade']]:
        """Group nodes by a key."""
        pass
    
    @abstractmethod
    def distinct(self, key: str = None) -> List['iNodeFacade']:
        """Get distinct values."""
        pass
    
    @abstractmethod
    def clear_query_cache(self):
        """Clear the query cache."""
        pass
    
    @abstractmethod
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query execution statistics."""
        pass
