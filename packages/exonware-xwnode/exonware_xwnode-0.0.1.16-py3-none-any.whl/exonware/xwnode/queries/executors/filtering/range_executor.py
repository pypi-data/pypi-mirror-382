#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/range_executor.py

RANGE Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType
from ...nodes.strategies.contracts import NodeType


class RangeExecutor(AOperationExecutor):
    """
    RANGE operation executor - Tree/Matrix operation.
    
    Performs range queries on ordered data structures.
    Optimized for TREE and MATRIX node types with efficient range scanning.
    
    Capability: Tree/Matrix only
    Operation Type: FILTERING
    """
    
    OPERATION_NAME = "RANGE"
    OPERATION_TYPE = OperationType.FILTERING
    SUPPORTED_NODE_TYPES = [NodeType.TREE, NodeType.MATRIX, NodeType.HYBRID]
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute RANGE operation."""
        params = action.params
        start = params.get('start')
        end = params.get('end')
        inclusive = params.get('inclusive', True)
        path = params.get('path', None)
        
        node = context.node
        result_data = self._execute_range(node, start, end, inclusive, path, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'item_count': len(result_data.get('items', []))}
        )
    
    def _execute_range(self, node: Any, start: Any, end: Any, inclusive: bool,
                      path: str, context: ExecutionContext) -> Dict:
        """Execute RANGE query."""
        range_items = []
        
        # Get data
        if path:
            data = node.get(path, default={})
        else:
            data = node.to_native()
        
        # Range query (simplified - would use tree traversal in real impl)
        if isinstance(data, dict):
            for key, value in sorted(data.items()):
                if inclusive:
                    if start <= key <= end:
                        range_items.append({key: value})
                else:
                    if start < key < end:
                        range_items.append({key: value})
        
        return {
            'items': range_items,
            'count': len(range_items),
            'range': {'start': start, 'end': end, 'inclusive': inclusive}
        }

