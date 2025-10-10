#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/drop_executor.py

DROP Executor

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
from ...nodes.strategies.contracts import NodeType


class DropExecutor(AUniversalOperationExecutor):
    """
    DROP operation executor - Universal operation.
    
    Drops/removes structures (collections, indices, schemas) from nodes.
    Works on all node types (LINEAR, TREE, GRAPH, MATRIX, HYBRID).
    
    Capability: Universal
    Operation Type: CORE
    """
    
    OPERATION_NAME = "DROP"
    OPERATION_TYPE = OperationType.CORE
    SUPPORTED_NODE_TYPES = []  # Empty = Universal (all types)
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute DROP operation."""
        # 1. Extract parameters
        params = action.params
        structure_type = params.get('type', 'collection')
        name = params.get('name')
        if_exists = params.get('if_exists', False)
        
        # 2. Get node strategy
        node = context.node
        
        # 3. Execute drop
        result_data = self._execute_drop(node, structure_type, name, if_exists, context)
        
        # 4. Return result
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={
                'structure_type': structure_type,
                'name': name,
                'dropped': result_data.get('dropped', False)
            }
        )
    
    def _execute_drop(self, node: Any, structure_type: str, name: str, 
                     if_exists: bool, context: ExecutionContext) -> Dict:
        """Actual DROP logic."""
        try:
            # Determine path based on structure type
            if structure_type == 'index':
                path = f"_indices.{name}"
            elif structure_type == 'schema':
                path = f"_schemas.{name}"
            else:
                path = name
            
            # Check if exists
            exists = node.get(path, default=None) is not None
            
            if not exists and not if_exists:
                return {
                    'dropped': False,
                    'error': f"Structure '{name}' does not exist"
                }
            
            if exists:
                node.delete(path)
                dropped = True
            else:
                dropped = False
            
            return {
                'dropped': dropped,
                'type': structure_type,
                'name': name,
                'path': path
            }
        except Exception as e:
            return {
                'dropped': False,
                'error': str(e)
            }

