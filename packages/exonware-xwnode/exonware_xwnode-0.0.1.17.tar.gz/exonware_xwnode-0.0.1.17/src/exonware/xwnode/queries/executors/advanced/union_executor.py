#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/advanced/union_executor.py

UNION Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.17
Generation Date: 09-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType

class UnionExecutor(AUniversalOperationExecutor):
    """
    UNION operation executor.
    
    Unions data from multiple sources
    
    Capability: Universal
    Operation Type: JOINING
    """
    
    OPERATION_NAME = "UNION"
    OPERATION_TYPE = OperationType.JOINING
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute UNION operation."""
        params = action.params
        node = context.node
        
        result_data = self._execute_union(node, params, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'operation': self.OPERATION_NAME}
        )
    
    def _execute_union(self, node: Any, params: Dict, context: ExecutionContext) -> Dict:
        """Execute union logic."""
        # Implementation here
        return {'result': 'UNION executed', 'params': params}
