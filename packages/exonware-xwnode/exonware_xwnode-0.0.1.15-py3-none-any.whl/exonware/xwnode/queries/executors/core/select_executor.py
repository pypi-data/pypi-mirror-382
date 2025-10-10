#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/select_executor.py

SELECT Operation Executor

Implements SELECT operation execution on all node types.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 08-Oct-2025
"""

from typing import Any, List, Dict, Optional
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationCapability
from ...nodes.strategies.contracts import NodeType


class SelectExecutor(AUniversalOperationExecutor):
    """
    SELECT operation executor - Universal operation.
    
    Works on all node types (LINEAR, TREE, GRAPH, MATRIX).
    Retrieves and projects data from nodes.
    """
    
    OPERATION_NAME = "SELECT"
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """
        Execute SELECT operation.
        
        Supports:
        - Column projection
        - Star (*) selection
        - Expressions and aliases
        - Adapts to different node types
        """
        # Extract parameters
        columns = action.params.get('columns', ['*'])
        source = action.params.get('from', context.node)
        
        # Get node type
        node_type = self._get_node_type(context.node)
        
        # Route to appropriate handler based on node type
        if node_type == NodeType.LINEAR:
            data = self._select_from_linear(source, columns, context)
        elif node_type == NodeType.TREE:
            data = self._select_from_tree(source, columns, context)
        elif node_type == NodeType.GRAPH:
            data = self._select_from_graph(source, columns, context)
        elif node_type == NodeType.MATRIX:
            data = self._select_from_matrix(source, columns, context)
        else:  # HYBRID
            data = self._select_from_tree(source, columns, context)  # Default to tree
        
        return ExecutionResult(
            data=data,
            affected_count=len(data) if isinstance(data, list) else 1
        )
    
    def _get_node_type(self, node: Any) -> NodeType:
        """Get node's strategy type."""
        if hasattr(node, '_strategy') and hasattr(node._strategy, 'STRATEGY_TYPE'):
            return node._strategy.STRATEGY_TYPE
        elif hasattr(node, 'STRATEGY_TYPE'):
            return node.STRATEGY_TYPE
        return NodeType.TREE  # Default
    
    def _select_from_linear(self, source: Any, columns: List[str], context: ExecutionContext) -> List[Dict]:
        """Select from linear node (list-like)."""
        results = []
        
        # Iterate through linear structure
        if hasattr(source, 'items'):
            for key, value in source.items():
                if columns == ['*']:
                    results.append({'key': key, 'value': value})
                else:
                    row = self._project_columns(value, columns)
                    results.append(row)
        
        return results
    
    def _select_from_tree(self, source: Any, columns: List[str], context: ExecutionContext) -> List[Dict]:
        """Select from tree node (key-value map)."""
        results = []
        
        # Iterate through tree structure
        if hasattr(source, 'items'):
            for key, value in source.items():
                if columns == ['*']:
                    results.append({'key': key, 'value': value})
                else:
                    row = self._project_columns(value, columns)
                    if row:
                        results.append(row)
        
        return results
    
    def _select_from_graph(self, source: Any, columns: List[str], context: ExecutionContext) -> List[Dict]:
        """Select from graph node."""
        # For graphs, return nodes
        results = []
        
        if hasattr(source, 'items'):
            for key, value in source.items():
                if columns == ['*']:
                    results.append({'node_id': key, 'node_data': value})
                else:
                    row = self._project_columns(value, columns)
                    if row:
                        row['node_id'] = key
                        results.append(row)
        
        return results
    
    def _select_from_matrix(self, source: Any, columns: List[str], context: ExecutionContext) -> List[Dict]:
        """Select from matrix node."""
        results = []
        
        # Iterate through matrix
        if hasattr(source, 'items'):
            for key, value in source.items():
                if columns == ['*']:
                    results.append({'position': key, 'value': value})
                else:
                    row = self._project_columns(value, columns)
                    if row:
                        results.append(row)
        
        return results
    
    def _project_columns(self, value: Any, columns: List[str]) -> Optional[Dict]:
        """Project specific columns from a value."""
        if not isinstance(value, dict):
            return {'value': value}
        
        projected = {}
        for col in columns:
            if col in value:
                projected[col] = value[col]
        
        return projected if projected else None


__all__ = ['SelectExecutor']
