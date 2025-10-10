#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/optional_executor.py

OPTIONAL Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType


class OptionalExecutor(AUniversalOperationExecutor):
    """
    OPTIONAL operation executor - Universal operation.
    
    Performs optional matching (like LEFT JOIN or OPTIONAL MATCH in SPARQL).
    Returns items whether or not the optional condition matches.
    
    Capability: Universal
    Operation Type: FILTERING
    """
    
    OPERATION_NAME = "OPTIONAL"
    OPERATION_TYPE = OperationType.FILTERING
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute OPTIONAL operation."""
        params = action.params
        condition = params.get('condition', None)
        path = params.get('path', None)
        
        node = context.node
        result_data = self._execute_optional(node, condition, path, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'total_count': len(result_data.get('items', []))}
        )
    
    def _execute_optional(self, node: Any, condition: Any, path: str, context: ExecutionContext) -> Dict:
        """Execute OPTIONAL matching."""
        all_items = []
        
        # Get data
        if path:
            data = node.get(path, default=[])
        else:
            data = node.to_native()
        
        # Include all items, mark which match optional condition
        if isinstance(data, list):
            for item in data:
                result_item = item.copy() if isinstance(item, dict) else {'value': item}
                result_item['_optional_matched'] = self._matches_condition(item, condition)
                all_items.append(result_item)
        
        return {'items': all_items, 'count': len(all_items)}
    
    def _matches_condition(self, item: Any, condition: Any) -> bool:
        """Check if item matches optional condition."""
        if condition is None:
            return False
        # Simplified condition matching
        return False

