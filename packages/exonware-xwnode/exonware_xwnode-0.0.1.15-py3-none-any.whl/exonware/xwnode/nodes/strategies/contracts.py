#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/contracts.py

Node Strategy Contracts

This module defines contracts and enums for node strategies,
including the NodeType classification system for operation routing.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 08-Oct-2025
"""

from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Iterator


class NodeType(Enum):
    """
    Node strategy type classification.
    
    Used to determine which operations can be executed on a node.
    """
    LINEAR = auto()    # Array-like, sequential access (lists, stacks, queues)
    TREE = auto()      # Hierarchical, key-based ordering (maps, trees, tries)
    GRAPH = auto()     # Nodes with relationships (union-find, graphs)
    MATRIX = auto()    # 2D grid access (bitmaps, matrices)
    HYBRID = auto()    # Combination of multiple types


class INodeStrategy(ABC):
    """
    Base interface for all node strategies.
    
    All node strategies must implement this interface and declare their type
    and supported operations.
    """
    
    # Strategy type classification (must be set by each strategy)
    STRATEGY_TYPE: NodeType = NodeType.TREE  # Default
    
    # Supported operations (can be overridden by each strategy)
    SUPPORTED_OPERATIONS: List[str] = []  # Empty = supports all universal operations
    
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
    
    @abstractmethod
    def keys(self) -> Iterator[Any]:
        """Get iterator over keys."""
        pass
    
    @abstractmethod
    def values(self) -> Iterator[Any]:
        """Get iterator over values."""
        pass
    
    @abstractmethod
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get iterator over key-value pairs."""
        pass
    
    @classmethod
    def get_strategy_type(cls) -> NodeType:
        """Get the strategy type for this class."""
        return cls.STRATEGY_TYPE
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of explicitly supported operations."""
        return cls.SUPPORTED_OPERATIONS
    
    @classmethod
    def supports_operation(cls, operation: str) -> bool:
        """Check if this strategy supports a specific operation."""
        # Empty list means supports all universal operations
        if not cls.SUPPORTED_OPERATIONS:
            return True
        return operation in cls.SUPPORTED_OPERATIONS


__all__ = [
    'NodeType',
    'INodeStrategy',
]
