#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/aggregation/count_executor.py

COUNT Operation Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult


class CountExecutor(AUniversalOperationExecutor):
    """COUNT operation executor - Universal aggregation."""
    
    OPERATION_NAME = "COUNT"
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute COUNT operation."""
        # Count items in node
        count = 0
        
        if hasattr(context.node, '__len__'):
            count = len(context.node)
        elif hasattr(context.node, 'size'):
            count = context.node.size()
        elif hasattr(context.node, '_strategy') and hasattr(context.node._strategy, 'size'):
            count = context.node._strategy.size()
        
        return ExecutionResult(data={'count': count}, affected_count=count)


__all__ = ['CountExecutor']
