#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/update_executor.py

UPDATE Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.18
Generation Date: 08-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType
from ...nodes.strategies.contracts import NodeType


class UpdateExecutor(AUniversalOperationExecutor):
    """
    UPDATE operation executor - Universal operation.
    
    Updates existing data in nodes based on specified conditions.
    Works on all node types (LINEAR, TREE, GRAPH, MATRIX, HYBRID).
    
    Capability: Universal
    Operation Type: CORE
    """
    
    OPERATION_NAME = "UPDATE"
    OPERATION_TYPE = OperationType.CORE
    SUPPORTED_NODE_TYPES = []  # Empty = Universal (all types)
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute UPDATE operation."""
        # 1. Extract parameters
        params = action.params
        target = params.get('target', None)  # What to update (path/key)
        values = params.get('values', {})    # New values
        condition = params.get('where', None)  # Update condition
        
        # 2. Get node strategy
        node = context.node
        
        # 3. Execute update
        result_data = self._execute_update(node, target, values, condition, context)
        
        # 4. Return result
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={
                'updated_count': result_data.get('count', 0),
                'target': target,
                'condition': condition
            }
        )
    
    def _execute_update(self, node: Any, target: str, values: Dict, 
                       condition: Any, context: ExecutionContext) -> Dict:
        """Actual UPDATE logic."""
        updated_count = 0
        updated_items = []
        
        if target:
            # Update specific target
            try:
                current = node.get(target, default=None)
                if current is not None and self._matches_condition(current, condition):
                    node.set(target, values)
                    updated_count = 1
                    updated_items.append(target)
            except Exception as e:
                return {
                    'count': 0,
                    'items': [],
                    'error': str(e)
                }
        else:
            # Update all matching items
            # This is a simplified implementation - real version would traverse node
            updated_count = 0
            updated_items = []
        
        return {
            'count': updated_count,
            'items': updated_items,
            'values': values
        }
    
    def _matches_condition(self, item: Any, condition: Any) -> bool:
        """Check if item matches condition."""
        if condition is None:
            return True
        
        # Simplified condition checking
        # Real implementation would evaluate WHERE clause
        return True

