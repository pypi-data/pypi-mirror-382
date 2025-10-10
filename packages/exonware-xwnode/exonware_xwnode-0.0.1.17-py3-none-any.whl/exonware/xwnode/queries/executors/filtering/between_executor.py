#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/between_executor.py

BETWEEN Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.17
Generation Date: 08-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType
from ...nodes.strategies.contracts import NodeType


class BetweenExecutor(AOperationExecutor):
    """
    BETWEEN operation executor - Tree/Matrix operation.
    
    Checks if values are within a range (inclusive).
    Optimized for TREE and MATRIX node types.
    
    Capability: Tree/Matrix only
    Operation Type: FILTERING
    """
    
    OPERATION_NAME = "BETWEEN"
    OPERATION_TYPE = OperationType.FILTERING
    SUPPORTED_NODE_TYPES = [NodeType.TREE, NodeType.MATRIX, NodeType.HYBRID]
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute BETWEEN operation."""
        params = action.params
        field = params.get('field')
        min_value = params.get('min')
        max_value = params.get('max')
        path = params.get('path', None)
        
        node = context.node
        result_data = self._execute_between(node, field, min_value, max_value, path, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'matched_count': len(result_data.get('items', []))}
        )
    
    def _execute_between(self, node: Any, field: str, min_val: Any, max_val: Any, 
                        path: str, context: ExecutionContext) -> Dict:
        """Execute BETWEEN range check."""
        matched_items = []
        
        # Get data
        if path:
            data = node.get(path, default=[])
        else:
            data = node.to_native()
        
        # Check range
        if isinstance(data, list):
            for item in data:
                value = item.get(field) if isinstance(item, dict) else item
                try:
                    if min_val <= value <= max_val:
                        matched_items.append(item)
                except (TypeError, ValueError):
                    pass
        
        return {
            'items': matched_items,
            'count': len(matched_items),
            'range': {'min': min_val, 'max': max_val}
        }

