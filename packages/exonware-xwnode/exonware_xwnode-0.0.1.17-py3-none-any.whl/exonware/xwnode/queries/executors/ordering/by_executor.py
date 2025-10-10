#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/ordering/by_executor.py

BY Executor

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

class ByExecutor(AUniversalOperationExecutor):
    """
    BY operation executor.
    
    Modifier for ORDER/GROUP BY
    
    Capability: Universal
    Operation Type: ORDERING
    """
    
    OPERATION_NAME = "BY"
    OPERATION_TYPE = OperationType.ORDERING
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute BY operation."""
        params = action.params
        node = context.node
        
        result_data = self._execute_by(node, params, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'operation': self.OPERATION_NAME}
        )
    
    def _execute_by(self, node: Any, params: Dict, context: ExecutionContext) -> Dict:
        """Execute by logic."""
        # Implementation here
        return {'result': 'BY executed', 'params': params}
