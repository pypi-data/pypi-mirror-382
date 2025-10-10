"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/__init__.py

Query Operation Executors

This package implements the execution layer for 50 XWQuery Script operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.18
Generation Date: 08-Oct-2025
"""

from .contracts import (
    IOperationExecutor,
    Action,
    ExecutionContext,
    ExecutionResult
)
from .types import OperationCapability, OperationType, ExecutionStatus
from .errors import ExecutorError, OperationExecutionError, ValidationError, UnsupportedOperationError
from .base import AOperationExecutor
from .registry import OperationRegistry, get_operation_registry, register_operation

__all__ = [
    # Contracts
    'IOperationExecutor',
    'Action',
    'ExecutionContext',
    'ExecutionResult',
    # Types
    'OperationCapability',
    'OperationType',
    'ExecutionStatus',
    # Errors
    'ExecutorError',
    'OperationExecutionError',
    'ValidationError',
    'UnsupportedOperationError',
    # Base
    'AOperationExecutor',
    # Registry
    'OperationRegistry',
    'get_operation_registry',
    'register_operation',
]
