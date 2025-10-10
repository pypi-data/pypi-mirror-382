#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/insert_executor.py

INSERT Operation Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 08-Oct-2025
"""

from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult


class InsertExecutor(AUniversalOperationExecutor):
    """INSERT operation executor - Universal operation."""
    
    OPERATION_NAME = "INSERT"
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute INSERT operation on node."""
        key = action.params.get('key')
        value = action.params.get('value')
        
        # Insert into node using strategy
        if hasattr(context.node, 'insert'):
            context.node.insert(key, value)
        elif hasattr(context.node, 'put'):
            context.node.put(key, value)
        elif hasattr(context.node, '_strategy'):
            context.node._strategy.insert(key, value)
        
        return ExecutionResult(data={'inserted': key}, affected_count=1)


__all__ = ['InsertExecutor']
