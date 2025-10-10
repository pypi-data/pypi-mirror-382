#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/errors.py

Executor Error Classes

Module-specific errors for query operation executors.
Extends root error classes per DEV_GUIDELINES.md - no redundancy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

# Import and REUSE root error classes per DEV_GUIDELINES
from ...errors import (
    XWNodeError,
    XWNodeStrategyError,
    XWNodeUnsupportedCapabilityError,
    XWNodeValueError
)
from ...nodes.strategies.contracts import NodeType


class ExecutorError(XWNodeStrategyError):
    """
    Base error for executor operations.
    
    Extends XWNodeStrategyError from root - follows DEV_GUIDELINES principle:
    "Never reinvent the wheel - reuse code from xwsystem library or xnode"
    """
    pass


class OperationExecutionError(ExecutorError):
    """Raised when operation execution fails."""
    
    def __init__(self, operation: str, reason: str, context: dict = None):
        message = f"Operation '{operation}' execution failed: {reason}"
        super().__init__(message)
        self.operation = operation
        self.reason = reason
        self.add_context(**(context or {}))


class ValidationError(ExecutorError):
    """Raised when action validation fails."""
    
    def __init__(self, action_type: str, reason: str):
        message = f"Action validation failed for '{action_type}': {reason}"
        super().__init__(message)
        self.action_type = action_type
        self.reason = reason


# REUSE existing error from root, don't duplicate
# Alias for convenience in this module
UnsupportedOperationError = XWNodeUnsupportedCapabilityError


__all__ = [
    'ExecutorError',
    'OperationExecutionError',
    'ValidationError',
    'UnsupportedOperationError',  # Re-exported from root
]
