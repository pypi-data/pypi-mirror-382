#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/contracts.py

Operation Executor Contracts

This module defines the interfaces and data structures for query operation execution.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 08-Oct-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Import shared types per DEV_GUIDELINES.md
from ...nodes.strategies.contracts import NodeType
from .types import OperationCapability


@dataclass
class Action:
    """
    Represents a single query action to be executed.
    
    Actions are parsed from XWQuery Script and contain all information
    needed to execute a specific operation.
    """
    type: str                        # e.g., "SELECT", "INSERT", "WHERE"
    params: Dict[str, Any]           # Operation parameters
    id: str = ""                     # Unique action ID
    line_number: int = 0             # Source line number
    children: List['Action'] = field(default_factory=list)  # Nested actions
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


@dataclass
class ExecutionContext:
    """
    Execution context for operation execution.
    
    Contains all state needed during execution including the target node,
    variables, transaction state, and configuration.
    """
    node: Any                        # Target XWNode to execute on
    variables: Dict[str, Any] = field(default_factory=dict)  # Query variables
    transaction: Optional[Any] = None  # Transaction object (if in transaction)
    cache: Optional[Dict[str, Any]] = None  # Result cache
    parent_results: Dict[str, Any] = field(default_factory=dict)  # Results from parent actions
    options: Dict[str, Any] = field(default_factory=dict)  # Execution options
    
    def set_result(self, action_id: str, result: Any) -> None:
        """Store result for later use by other actions."""
        self.parent_results[action_id] = result
    
    def get_result(self, action_id: str) -> Optional[Any]:
        """Get result from previous action."""
        return self.parent_results.get(action_id)


@dataclass
class ExecutionResult:
    """
    Result of operation execution.
    
    Contains the data returned by the operation along with metadata
    about the execution.
    """
    data: Any                        # Result data
    affected_count: int = 0          # Number of items affected
    execution_time: float = 0.0      # Execution time in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    success: bool = True             # Whether execution succeeded
    error: Optional[str] = None      # Error message if failed


class IOperationExecutor(ABC):
    """
    Interface for operation executors.
    
    All operation executors must implement this interface to be compatible
    with the execution engine.
    """
    
    # Operation name (e.g., "SELECT", "INSERT")
    OPERATION_NAME: str = ""
    
    # Supported node types (empty = all types)
    SUPPORTED_NODE_TYPES: List[NodeType] = []
    
    # Required capabilities
    REQUIRED_CAPABILITIES: OperationCapability = OperationCapability.NONE
    
    @abstractmethod
    def execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """
        Execute the operation.
        
        Args:
            action: The action to execute
            context: Execution context with node and state
            
        Returns:
            ExecutionResult with data and metadata
            
        Raises:
            UnsupportedOperationError: If operation cannot execute on node type
            ExecutionError: If execution fails
        """
        pass
    
    @abstractmethod
    def validate(self, action: Action, context: ExecutionContext) -> bool:
        """
        Validate that the action can be executed.
        
        Args:
            action: The action to validate
            context: Execution context
            
        Returns:
            True if action is valid and can be executed
        """
        pass
    
    def can_execute_on(self, node_type: NodeType) -> bool:
        """
        Check if this executor can operate on the given node type.
        
        Args:
            node_type: The node type to check
            
        Returns:
            True if this executor supports the node type
        """
        # Empty list means supports all types
        if not self.SUPPORTED_NODE_TYPES:
            return True
        return node_type in self.SUPPORTED_NODE_TYPES
    
    def estimate_cost(self, action: Action, context: ExecutionContext) -> int:
        """
        Estimate execution cost (optional).
        
        Args:
            action: The action to estimate
            context: Execution context
            
        Returns:
            Estimated cost (arbitrary units)
        """
        return 100  # Default cost


__all__ = [
    'IOperationExecutor',
    'Action',
    'ExecutionContext',
    'ExecutionResult',
    'OperationCapability',
    'NodeType',
]
