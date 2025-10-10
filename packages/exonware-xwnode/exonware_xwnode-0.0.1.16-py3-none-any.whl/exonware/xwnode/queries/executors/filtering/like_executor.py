#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/like_executor.py

LIKE Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

import re
from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType


class LikeExecutor(AUniversalOperationExecutor):
    """
    LIKE operation executor - Universal operation.
    
    Pattern matching using SQL LIKE syntax (% and _ wildcards).
    
    Capability: Universal
    Operation Type: FILTERING
    """
    
    OPERATION_NAME = "LIKE"
    OPERATION_TYPE = OperationType.FILTERING
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute LIKE operation."""
        params = action.params
        field = params.get('field')
        pattern = params.get('pattern', '')
        path = params.get('path', None)
        
        node = context.node
        result_data = self._execute_like(node, field, pattern, path, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'matched_count': len(result_data.get('items', []))}
        )
    
    def _execute_like(self, node: Any, field: str, pattern: str, path: str, context: ExecutionContext) -> Dict:
        """Execute LIKE pattern matching."""
        matched_items = []
        
        # Convert SQL LIKE pattern to regex
        # % = .* (any characters)
        # _ = . (single character)
        regex_pattern = pattern.replace('%', '.*').replace('_', '.')
        regex = re.compile(regex_pattern, re.IGNORECASE)
        
        # Get data
        if path:
            data = node.get(path, default=[])
        else:
            data = node.to_native()
        
        # Match pattern
        if isinstance(data, list):
            for item in data:
                value = item.get(field) if isinstance(item, dict) else str(item)
                if value and regex.match(str(value)):
                    matched_items.append(item)
        
        return {'items': matched_items, 'count': len(matched_items), 'pattern': pattern}

