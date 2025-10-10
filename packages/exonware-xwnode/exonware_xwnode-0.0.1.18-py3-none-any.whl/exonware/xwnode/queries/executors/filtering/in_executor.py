#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/in_executor.py

IN Executor

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


class InExecutor(AUniversalOperationExecutor):
    """
    IN operation executor - Universal operation.
    
    Checks if a value is in a specified set.
    
    Capability: Universal
    Operation Type: FILTERING
    """
    
    OPERATION_NAME = "IN"
    OPERATION_TYPE = OperationType.FILTERING
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute IN operation."""
        params = action.params
        field = params.get('field')
        values = params.get('values', [])
        path = params.get('path', None)
        
        node = context.node
        result_data = self._execute_in(node, field, values, path, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'matched_count': len(result_data.get('items', []))}
        )
    
    def _execute_in(self, node: Any, field: str, values: List, path: str, context: ExecutionContext) -> Dict:
        """Execute IN membership check."""
        matched_items = []
        values_set = set(values) if values else set()
        
        # Get data
        if path:
            data = node.get(path, default=[])
        else:
            data = node.to_native()
        
        # Check membership
        if isinstance(data, list):
            for item in data:
                value = item.get(field) if isinstance(item, dict) else item
                if value in values_set:
                    matched_items.append(item)
        
        return {'items': matched_items, 'count': len(matched_items), 'values': values}

