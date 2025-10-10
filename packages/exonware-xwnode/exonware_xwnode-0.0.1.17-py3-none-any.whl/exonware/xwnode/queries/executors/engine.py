#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/engine.py

Query Execution Engine

This module provides the main execution engine that orchestrates operation execution
with capability checking and routing.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.17
Generation Date: 08-Oct-2025
"""

from typing import Any, List, Dict, Optional
from .contracts import Action, ExecutionContext, ExecutionResult, NodeType
from .registry import get_operation_registry, OperationRegistry
from .capability_checker import check_operation_compatibility
from .base import UnsupportedOperationError
from ...base import XWNodeBase


class ExecutionEngine:
    """
    Main query execution engine.
    
    Orchestrates execution of XWQuery operations on nodes with:
    - Capability-aware routing
    - Operation composition
    - Error handling
    - Performance monitoring
    """
    
    def __init__(self, registry: Optional[OperationRegistry] = None):
        """
        Initialize execution engine.
        
        Args:
            registry: Operation registry (uses global if not provided)
        """
        self._registry = registry or get_operation_registry()
        self._execution_history: List[Dict] = []
    
    def execute(self, query: str, node: Any, **kwargs) -> ExecutionResult:
        """
        Execute a query string on a node.
        
        Args:
            query: XWQuery script string
            node: Target node to execute on
            **kwargs: Additional execution options
            
        Returns:
            ExecutionResult with data
        """
        # Parse query to actions tree
        from ..strategies.xwquery import XWQueryScriptStrategy
        
        script_strategy = XWQueryScriptStrategy()
        parsed = script_strategy.parse_script(query)
        actions_tree = parsed.get_actions_tree()
        
        # Create execution context
        context = ExecutionContext(
            node=node,
            variables=kwargs.get('variables', {}),
            options=kwargs
        )
        
        # Execute actions tree
        return self.execute_actions_tree(actions_tree, context)
    
    def execute_actions_tree(self, actions_tree: XWNodeBase, context: ExecutionContext) -> ExecutionResult:
        """
        Execute an actions tree.
        
        Args:
            actions_tree: Parsed actions tree
            context: Execution context
            
        Returns:
            Combined execution result
        """
        tree_data = actions_tree.to_native()
        statements = tree_data.get('root', {}).get('statements', [])
        
        results = []
        
        for statement in statements:
            # Create action from statement
            action = Action(
                type=statement.get('type', 'UNKNOWN'),
                params=statement.get('params', {}),
                id=statement.get('id', ''),
                line_number=statement.get('line_number', 0)
            )
            
            # Execute action
            result = self.execute_action(action, context)
            results.append(result)
            
            # Store result for later actions
            if action.id:
                context.set_result(action.id, result.data)
        
        # Combine results
        return self._combine_results(results)
    
    def execute_action(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """
        Execute a single action.
        
        Args:
            action: Action to execute
            context: Execution context
            
        Returns:
            ExecutionResult
        """
        # Get executor for this operation
        executor = self._registry.get(action.type)
        
        if not executor:
            return ExecutionResult(
                data=None,
                success=False,
                error=f"No executor registered for operation: {action.type}"
            )
        
        # Check capability before execution
        try:
            node_type = self._get_node_type(context.node)
            
            if not executor.can_execute_on(node_type):
                return ExecutionResult(
                    data=None,
                    success=False,
                    error=f"Operation {action.type} not supported on {node_type.name} nodes"
                )
            
            # Execute
            result = executor.execute(action, context)
            
            # Record execution
            self._record_execution(action, result)
            
            return result
            
        except UnsupportedOperationError as e:
            return ExecutionResult(
                data=None,
                success=False,
                error=str(e)
            )
        except Exception as e:
            return ExecutionResult(
                data=None,
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def _get_node_type(self, node: Any) -> NodeType:
        """Get node's strategy type."""
        if hasattr(node, '_strategy') and hasattr(node._strategy, 'STRATEGY_TYPE'):
            return node._strategy.STRATEGY_TYPE
        elif hasattr(node, 'STRATEGY_TYPE'):
            return node.STRATEGY_TYPE
        return NodeType.TREE  # Default
    
    def _combine_results(self, results: List[ExecutionResult]) -> ExecutionResult:
        """Combine multiple execution results."""
        if not results:
            return ExecutionResult(data=[])
        
        if len(results) == 1:
            return results[0]
        
        # Combine data from all results
        combined_data = []
        total_affected = 0
        total_time = 0.0
        all_success = True
        
        for result in results:
            if result.data:
                if isinstance(result.data, list):
                    combined_data.extend(result.data)
                else:
                    combined_data.append(result.data)
            total_affected += result.affected_count
            total_time += result.execution_time
            all_success = all_success and result.success
        
        return ExecutionResult(
            data=combined_data,
            affected_count=total_affected,
            execution_time=total_time,
            success=all_success
        )
    
    def _record_execution(self, action: Action, result: ExecutionResult) -> None:
        """Record execution in history."""
        self._execution_history.append({
            'action': action.type,
            'success': result.success,
            'affected_count': result.affected_count,
            'execution_time': result.execution_time
        })
    
    def get_execution_history(self) -> List[Dict]:
        """Get execution history."""
        return self._execution_history.copy()
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()


__all__ = ['ExecutionEngine']
