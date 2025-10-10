#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/values_executor.py

VALUES Executor

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


class ValuesExecutor(AUniversalOperationExecutor):
    """
    VALUES operation executor - Universal operation.
    
    Handles VALUES clause (inline data/constants).
    Used in SQL and SPARQL for providing inline value lists.
    
    Capability: Universal
    Operation Type: DATA_OPS
    """
    
    OPERATION_NAME = "VALUES"
    OPERATION_TYPE = OperationType.DATA_OPS
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute VALUES operation."""
        params = action.params
        values = params.get('values', [])
        columns = params.get('columns', [])
        
        result_data = self._execute_values(values, columns, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'row_count': len(result_data.get('rows', []))}
        )
    
    def _execute_values(self, values: List, columns: List, context: ExecutionContext) -> Dict:
        """Execute VALUES inline data."""
        rows = []
        
        # Convert values to rows with column names
        if columns:
            for value_row in values:
                if isinstance(value_row, list):
                    row = dict(zip(columns, value_row))
                    rows.append(row)
                elif isinstance(value_row, dict):
                    rows.append(value_row)
        else:
            # No columns specified, use values as-is
            rows = values if isinstance(values, list) else [values]
        
        return {
            'rows': rows,
            'count': len(rows),
            'columns': columns
        }

