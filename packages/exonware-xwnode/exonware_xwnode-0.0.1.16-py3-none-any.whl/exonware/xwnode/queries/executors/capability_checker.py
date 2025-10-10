#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/capability_checker.py

Operation Capability Checker

This module provides capability checking for operations on different node types.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

from typing import Dict, List, Set

# Import NodeType from nodes module per DEV_GUIDELINES
from ...nodes.strategies.contracts import NodeType


# Operation-to-NodeType Compatibility Matrix
OPERATION_COMPATIBILITY = {
    # Core CRUD Operations (Universal)
    'SELECT': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'INSERT': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'UPDATE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'DELETE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'CREATE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'DROP': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Filtering Operations (Universal)
    'WHERE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'FILTER': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'LIKE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'IN': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'HAS': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Range Operations (Tree/Matrix)
    'BETWEEN': {NodeType.TREE, NodeType.MATRIX},
    'RANGE': {NodeType.TREE, NodeType.MATRIX},
    
    # Aggregation Operations (Universal)
    'GROUP': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'BY': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'HAVING': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'SUMMARIZE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'SUM': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'COUNT': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'AVG': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'MIN': {NodeType.LINEAR, NodeType.TREE, NodeType.MATRIX},  # Optimal on trees
    'MAX': {NodeType.LINEAR, NodeType.TREE, NodeType.MATRIX},  # Optimal on trees
    'DISTINCT': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Ordering Operations (Tree/Linear)
    'ORDER': {NodeType.TREE, NodeType.LINEAR},
    
    # Join Operations (Universal conceptually)
    'JOIN': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'UNION': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'WITH': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'OPTIONAL': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Graph Operations
    'MATCH': {NodeType.GRAPH, NodeType.TREE, NodeType.HYBRID},
    'PATH': {NodeType.GRAPH, NodeType.TREE, NodeType.HYBRID},
    'OUT': {NodeType.GRAPH, NodeType.TREE, NodeType.HYBRID},
    'IN_TRAVERSE': {NodeType.GRAPH, NodeType.TREE, NodeType.HYBRID},
    'RETURN': {NodeType.GRAPH, NodeType.TREE, NodeType.HYBRID},
    
    # Projection Operations (Universal)
    'PROJECT': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'EXTEND': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Array Operations (Linear/Matrix)
    'SLICING': {NodeType.LINEAR, NodeType.MATRIX},
    'INDEXING': {NodeType.LINEAR, NodeType.MATRIX, NodeType.TREE},
    
    # Search Operations (Universal)
    'TERM': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Data Operations (Universal)
    'LOAD': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'STORE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'MERGE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'ALTER': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Control Flow Operations (Universal)
    'FOREACH': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'LET': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'FOR': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Window Operations (Time-series, works on linear/tree)
    'WINDOW': {NodeType.LINEAR, NodeType.TREE},
    'AGGREGATE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Metadata Operations (Universal)
    'DESCRIBE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'CONSTRUCT': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'ASK': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    
    # Advanced Operations (Universal)
    'SUBSCRIBE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'SUBSCRIPTION': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'MUTATION': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'PIPE': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'OPTIONS': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
    'VALUES': {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID},
}


def check_operation_compatibility(operation: str, node_type: NodeType) -> bool:
    """
    Check if an operation is compatible with a node type.
    
    Args:
        operation: Operation name (e.g., "SELECT")
        node_type: Node type to check
        
    Returns:
        True if operation is compatible with node type
    """
    operation = operation.upper()
    
    # Check compatibility matrix
    if operation in OPERATION_COMPATIBILITY:
        return node_type in OPERATION_COMPATIBILITY[operation]
    
    # Unknown operation - assume universal (backward compatibility)
    return True


def get_supported_operations(node_type: NodeType) -> List[str]:
    """
    Get list of operations supported by a node type.
    
    Args:
        node_type: Node type to check
        
    Returns:
        List of supported operation names
    """
    supported = []
    
    for operation, compatible_types in OPERATION_COMPATIBILITY.items():
        if node_type in compatible_types:
            supported.append(operation)
    
    return supported


def get_universal_operations() -> List[str]:
    """
    Get list of universal operations (work on all node types).
    
    Returns:
        List of universal operation names
    """
    universal = []
    all_types = {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID}
    
    for operation, compatible_types in OPERATION_COMPATIBILITY.items():
        if compatible_types == all_types:
            universal.append(operation)
    
    return universal


def get_type_specific_operations(node_type: NodeType) -> List[str]:
    """
    Get operations that are specific to (or optimal for) a node type.
    
    Args:
        node_type: Node type to check
        
    Returns:
        List of type-specific operation names
    """
    specific = []
    all_types = {NodeType.LINEAR, NodeType.TREE, NodeType.GRAPH, NodeType.MATRIX, NodeType.HYBRID}
    
    for operation, compatible_types in OPERATION_COMPATIBILITY.items():
        # If node type supports it but not all types support it
        if node_type in compatible_types and compatible_types != all_types:
            specific.append(operation)
    
    return specific


# Global registry accessor
def get_global_registry() -> OperationRegistry:
    """Get the global operation registry instance."""
    return OperationRegistry()


__all__ = [
    'OperationRegistry',
    'get_operation_registry',
    'check_operation_compatibility',
    'get_supported_operations',
    'get_universal_operations',
    'get_type_specific_operations',
    'OPERATION_COMPATIBILITY',
]
