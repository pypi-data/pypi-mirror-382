#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/core/create_executor.py

CREATE Executor

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
from ...nodes.strategies.contracts import NodeType


class CreateExecutor(AUniversalOperationExecutor):
    """
    CREATE operation executor - Universal operation.
    
    Creates new structures (collections, indices, schemas) in nodes.
    Works on all node types (LINEAR, TREE, GRAPH, MATRIX, HYBRID).
    
    Capability: Universal
    Operation Type: CORE
    """
    
    OPERATION_NAME = "CREATE"
    OPERATION_TYPE = OperationType.CORE
    SUPPORTED_NODE_TYPES = []  # Empty = Universal (all types)
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute CREATE operation."""
        # 1. Extract parameters
        params = action.params
        structure_type = params.get('type', 'collection')  # collection, index, schema
        name = params.get('name', 'new_structure')
        schema = params.get('schema', {})
        options = params.get('options', {})
        
        # 2. Get node strategy
        node = context.node
        
        # 3. Execute create
        result_data = self._execute_create(node, structure_type, name, schema, options, context)
        
        # 4. Return result
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={
                'structure_type': structure_type,
                'name': name,
                'created': result_data.get('created', False)
            }
        )
    
    def _execute_create(self, node: Any, structure_type: str, name: str, 
                       schema: Dict, options: Dict, context: ExecutionContext) -> Dict:
        """Actual CREATE logic."""
        try:
            # Create structure based on type
            if structure_type == 'collection':
                # Create a new collection/path
                node.set(name, {})
                created = True
            elif structure_type == 'index':
                # Create an index (simplified)
                index_path = f"_indices.{name}"
                node.set(index_path, {'type': 'index', 'fields': schema})
                created = True
            elif structure_type == 'schema':
                # Create a schema definition
                schema_path = f"_schemas.{name}"
                node.set(schema_path, schema)
                created = True
            else:
                created = False
            
            return {
                'created': created,
                'type': structure_type,
                'name': name,
                'path': name
            }
        except Exception as e:
            return {
                'created': False,
                'error': str(e)
            }

