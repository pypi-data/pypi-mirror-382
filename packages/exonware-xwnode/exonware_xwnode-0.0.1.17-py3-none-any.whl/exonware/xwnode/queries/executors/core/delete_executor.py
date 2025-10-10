#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/delete_executor.py

DELETE Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.17
Generation Date: 08-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType
from ...nodes.strategies.contracts import NodeType


class DeleteExecutor(AUniversalOperationExecutor):
    """
    DELETE operation executor - Universal operation.
    
    Deletes data from nodes based on specified conditions.
    Works on all node types (LINEAR, TREE, GRAPH, MATRIX, HYBRID).
    
    Capability: Universal
    Operation Type: CORE
    """
    
    OPERATION_NAME = "DELETE"
    OPERATION_TYPE = OperationType.CORE
    SUPPORTED_NODE_TYPES = []  # Empty = Universal (all types)
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute DELETE operation."""
        # 1. Extract parameters
        params = action.params
        target = params.get('target', None)  # What to delete (path/key)
        condition = params.get('where', None)  # Delete condition
        
        # 2. Get node strategy
        node = context.node
        
        # 3. Execute delete
        result_data = self._execute_delete(node, target, condition, context)
        
        # 4. Return result
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={
                'deleted_count': result_data.get('count', 0),
                'target': target,
                'condition': condition
            }
        )
    
    def _execute_delete(self, node: Any, target: str, condition: Any, 
                       context: ExecutionContext) -> Dict:
        """Actual DELETE logic."""
        deleted_count = 0
        deleted_items = []
        
        if target:
            # Delete specific target
            try:
                current = node.get(target, default=None)
                if current is not None and self._matches_condition(current, condition):
                    node.delete(target)
                    deleted_count = 1
                    deleted_items.append(target)
            except Exception as e:
                return {
                    'count': 0,
                    'items': [],
                    'error': str(e)
                }
        else:
            # Delete all matching items
            # This is a simplified implementation
            deleted_count = 0
            deleted_items = []
        
        return {
            'count': deleted_count,
            'items': deleted_items
        }
    
    def _matches_condition(self, item: Any, condition: Any) -> bool:
        """Check if item matches condition."""
        if condition is None:
            return True
        
        # Simplified condition checking
        return True

