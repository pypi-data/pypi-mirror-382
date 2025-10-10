#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/has_executor.py

HAS Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 08-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType


class HasExecutor(AUniversalOperationExecutor):
    """
    HAS operation executor - Universal operation.
    
    Checks if a property/field exists in data.
    
    Capability: Universal
    Operation Type: FILTERING
    """
    
    OPERATION_NAME = "HAS"
    OPERATION_TYPE = OperationType.FILTERING
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute HAS operation."""
        params = action.params
        property_name = params.get('property')
        path = params.get('path', None)
        
        node = context.node
        result_data = self._execute_has(node, property_name, path, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'matched_count': len(result_data.get('items', []))}
        )
    
    def _execute_has(self, node: Any, property_name: str, path: str, context: ExecutionContext) -> Dict:
        """Execute HAS property check."""
        matched_items = []
        
        # Get data
        if path:
            data = node.get(path, default=[])
        else:
            data = node.to_native()
        
        # Check property existence
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and property_name in item:
                    matched_items.append(item)
        elif isinstance(data, dict):
            if property_name in data:
                matched_items.append(data)
        
        return {'items': matched_items, 'count': len(matched_items), 'property': property_name}

