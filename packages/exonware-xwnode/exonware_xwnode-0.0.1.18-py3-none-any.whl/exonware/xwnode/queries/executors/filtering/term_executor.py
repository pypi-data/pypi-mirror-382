#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/filtering/term_executor.py

TERM Executor

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


class TermExecutor(AUniversalOperationExecutor):
    """
    TERM operation executor - Universal operation.
    
    Performs term-based search/matching (exact term match).
    Used in search engines and text indexing.
    
    Capability: Universal
    Operation Type: SEARCH
    """
    
    OPERATION_NAME = "TERM"
    OPERATION_TYPE = OperationType.SEARCH
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute TERM operation."""
        params = action.params
        field = params.get('field')
        term = params.get('term', '')
        path = params.get('path', None)
        case_sensitive = params.get('case_sensitive', False)
        
        node = context.node
        result_data = self._execute_term(node, field, term, path, case_sensitive, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'matched_count': len(result_data.get('items', []))}
        )
    
    def _execute_term(self, node: Any, field: str, term: str, path: str, 
                     case_sensitive: bool, context: ExecutionContext) -> Dict:
        """Execute TERM search."""
        matched_items = []
        
        # Get data
        if path:
            data = node.get(path, default=[])
        else:
            data = node.to_native()
        
        # Normalize term if case-insensitive
        search_term = term if case_sensitive else term.lower()
        
        # Search for term
        if isinstance(data, list):
            for item in data:
                value = item.get(field) if isinstance(item, dict) else str(item)
                if value:
                    compare_value = str(value) if case_sensitive else str(value).lower()
                    if search_term in compare_value:
                        matched_items.append(item)
        
        return {'items': matched_items, 'count': len(matched_items), 'term': term}

