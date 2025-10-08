"""
#exonware/xwnode/src/exonware/xwnode/errors.py

A+ Best Practice Error Handling for xwnode Library.

This module implements zero-overhead error handling with rich context,
actionable suggestions, and performance optimization for critical paths.
"""

import time
import difflib
from typing import Any, Dict, List, Optional, Union
from exonware.xwsystem import get_logger

logger = get_logger(__name__)


# ============================================================================
# A+ BASE ERROR SYSTEM
# ============================================================================

class XWNodeError(Exception):
    """
    Base exception with rich context and zero overhead in success path.
    
    This error system follows modern Python best practices:
    - Zero overhead when no errors occur
    - Rich context only created on failure path
    - Chainable methods for fluent error building
    - Performance-optimized with __slots__
    """
    
    __slots__ = ('message', 'error_code', 'context', 'suggestions', 'timestamp', 'cause')
    
    def __init__(self, message: str, *, 
                 error_code: str = None,
                 context: Dict[str, Any] = None,
                 suggestions: List[str] = None,
                 cause: Exception = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.suggestions = suggestions or []
        self.timestamp = time.time()
        self.cause = cause
    
    def add_context(self, **kwargs) -> 'XWNodeError':
        """Add context information (chainable)."""
        self.context.update(kwargs)
        return self
    
    def suggest(self, suggestion: str) -> 'XWNodeError':
        """Add actionable suggestion (chainable)."""
        self.suggestions.append(suggestion)
        return self
    
    def __str__(self) -> str:
        """Rich string representation with context and suggestions."""
        result = [self.message]
        
        if self.context:
            context_str = ', '.join(f"{k}={v}" for k, v in self.context.items())
            result.append(f"Context: {context_str}")
        
        if self.suggestions:
            suggestions_str = '; '.join(self.suggestions)
            result.append(f"Suggestions: {suggestions_str}")
            
        return " | ".join(result)


# ============================================================================
# PATH NAVIGATION ERRORS (Most Common)
# ============================================================================

class XWNodePathError(XWNodeError, KeyError):
    """
    Path navigation errors with AI-like suggestions.
    
    This is the most common error type, so it's heavily optimized
    with smart suggestion generation and fuzzy matching.
    """
    
    __slots__ = ('path', 'segment', 'reason', 'node_type', 'available_keys')
    
    def __init__(self, path: str, segment: str = None, reason: str = "not_found", 
                 node_type: str = None, available_keys: List[str] = None):
        self.path = path
        self.segment = segment or path
        self.reason = reason  # "not_found", "type_mismatch", "out_of_bounds"
        self.node_type = node_type
        self.available_keys = available_keys or []
        
        # Generate helpful message
        message = f"Path navigation failed: '{path}'"
        if segment and segment != path:
            message += f" at segment '{segment}'"
        message += f" ({reason})"
        
        context = {
            'path': path,
            'segment': segment,
            'reason': reason,
            'node_type': node_type
        }
        
        suggestions = self._generate_smart_suggestions()
        
        super().__init__(message, 
                        error_code=f"PATH_{reason.upper()}", 
                        context=context,
                        suggestions=suggestions)
    
    def _generate_smart_suggestions(self) -> List[str]:
        """Generate AI-like suggestions based on error context."""
        suggestions = []
        
        if self.reason == "not_found" and self.available_keys:
            # Fuzzy matching for typos (performance: only on error path)
            close_matches = difflib.get_close_matches(
                self.segment, self.available_keys, n=3, cutoff=0.6
            )
            if close_matches:
                suggestions.append(f"Did you mean: {', '.join(close_matches)}?")
            
            # Show available options (truncated for readability)
            if len(self.available_keys) <= 5:
                suggestions.append(f"Available: {', '.join(self.available_keys)}")
            else:
                preview = ', '.join(self.available_keys[:5])
                suggestions.append(f"Available: {preview}... ({len(self.available_keys)} total)")
        
        elif self.reason == "type_mismatch":
            suggestions.append("Cannot access children of leaf nodes")
            if self.node_type:
                suggestions.append(f"Node type is '{self.node_type}' (not a container)")
        
        elif self.reason == "out_of_bounds":
            suggestions.append("Check list bounds before accessing by index")
            if self.available_keys:
                suggestions.append(f"Valid range: 0-{len(self.available_keys)-1}")
        
        return suggestions


class XWNodeTypeError(XWNodeError, TypeError):
    """Enhanced type errors with operation context."""
    
    __slots__ = ('attempted_operation', 'actual_type', 'expected_types')
    
    def __init__(self, message: str, *,
                 attempted_operation: str = None,
                 actual_type: str = None,
                 expected_types: List[str] = None):
        self.attempted_operation = attempted_operation
        self.actual_type = actual_type
        self.expected_types = expected_types or []
        
        context = {
            'operation': attempted_operation,
            'actual_type': actual_type,
            'expected_types': expected_types
        }
        
        suggestions = []
        if expected_types:
            suggestions.append(f"Expected types: {', '.join(expected_types)}")
        if attempted_operation:
            suggestions.append(f"Check node type before {attempted_operation}")
        
        super().__init__(message, 
                        error_code="TYPE_MISMATCH",
                        context=context,
                        suggestions=suggestions)


class XWNodeValueError(XWNodeError, ValueError):
    """Enhanced value errors with validation context."""
    
    __slots__ = ('invalid_value', 'constraints', 'validation_rules')
    
    def __init__(self, message: str, *,
                 invalid_value: Any = None,
                 constraints: Dict[str, Any] = None,
                 validation_rules: List[str] = None):
        self.invalid_value = invalid_value
        self.constraints = constraints or {}
        self.validation_rules = validation_rules or []
        
        context = {
            'invalid_value': invalid_value,
            'constraints': constraints
        }
        
        suggestions = []
        if validation_rules:
            suggestions.extend(validation_rules)
        if constraints:
            for rule, value in constraints.items():
                suggestions.append(f"Value must satisfy {rule}: {value}")
        
        super().__init__(message,
                        error_code="INVALID_VALUE", 
                        context=context,
                        suggestions=suggestions)


# ============================================================================
# PERFORMANCE-OPTIMIZED ERROR FACTORY
# ============================================================================

class ErrorFactory:
    """
    Zero-overhead error creation for critical paths.
    
    This factory provides fast paths for common error scenarios,
    avoiding expensive operations in hot code paths.
    """
    
    @staticmethod
    def path_not_found(path: str, segment: str = None, available_keys: List[str] = None) -> XWNodePathError:
        """Fast path for common 'not found' errors."""
        return XWNodePathError(path, segment, "not_found", available_keys=available_keys)
    
    @staticmethod
    def type_mismatch(path: str, segment: str, node_type: str) -> XWNodePathError:
        """Fast path for type mismatch errors."""
        return XWNodePathError(path, segment, "type_mismatch", node_type=node_type)
    
    @staticmethod
    def index_out_of_bounds(path: str, index: int, length: int) -> XWNodePathError:
        """Fast path for index errors."""
        return XWNodePathError(path, str(index), "out_of_bounds").add_context(
            index=index, length=length
        ).suggest(f"Valid range: 0-{length-1}")
    
    @staticmethod
    def operation_not_supported(operation: str, node_type: str, supported_ops: List[str] = None) -> XWNodeTypeError:
        """Fast path for unsupported operation errors."""
        message = f"Operation '{operation}' not supported on {node_type}"
        error = XWNodeTypeError(
            message,
            attempted_operation=operation,
            actual_type=node_type
        )
        if supported_ops:
            error.suggest(f"Supported operations: {', '.join(supported_ops)}")
        return error
    
    @staticmethod
    def invalid_preset(preset_name: str, available_presets: List[str]) -> XWNodeValueError:
        """Fast path for invalid preset errors."""
        close_matches = difflib.get_close_matches(preset_name, available_presets, n=3, cutoff=0.6)
        error = XWNodeValueError(
            f"Unknown preset '{preset_name}'",
            invalid_value=preset_name,
            constraints={'available_presets': available_presets}
        )
        if close_matches:
            error.suggest(f"Did you mean: {', '.join(close_matches)}?")
        error.suggest(f"Available presets: {', '.join(available_presets)}")
        return error


# ============================================================================
# STRATEGY SYSTEM ERRORS (A+ Enhanced)
# ============================================================================

class XWNodeStrategyError(XWNodeError):
    """Base exception for strategy-related errors."""
    pass


class XWNodeUnsupportedCapabilityError(XWNodeStrategyError):
    """Raised when a strategy doesn't support a requested capability."""
    
    __slots__ = ('capability', 'strategy', 'available_capabilities')
    
    def __init__(self, capability: str, strategy: str, available_capabilities: List[str] = None):
        self.capability = capability
        self.strategy = strategy
        self.available_capabilities = available_capabilities or []
        
        message = f"Strategy '{strategy}' does not support capability '{capability}'"
        
        context = {
            'capability': capability,
            'strategy': strategy,
            'available_capabilities': available_capabilities
        }
        
        suggestions = []
        if available_capabilities:
            suggestions.append(f"Available capabilities: {', '.join(available_capabilities)}")
            
            # Suggest alternative strategies
            if capability == 'graph_operations':
                suggestions.append("Use preset='SOCIAL_GRAPH' or 'TREE_GRAPH_MIX' for graph features")
            elif capability == 'spatial_operations':
                suggestions.append("Use preset='SPATIAL_MAP' for spatial features")
        
        super().__init__(message,
                        error_code="UNSUPPORTED_CAPABILITY",
                        context=context,
                        suggestions=suggestions)


class XWNodePresetError(XWNodeStrategyError):
    """Raised when preset operations fail."""
    
    __slots__ = ('preset_name', 'operation', 'reason')
    
    def __init__(self, preset_name: str, operation: str, reason: str = None):
        self.preset_name = preset_name
        self.operation = operation
        self.reason = reason
        
        message = f"Preset '{preset_name}' {operation} failed"
        if reason:
            message += f": {reason}"
        
        context = {
            'preset_name': preset_name,
            'operation': operation,
            'reason': reason
        }
        
        # Import here to avoid circular imports
        try:
            from .types import list_presets
            available = list_presets()
            suggestions = [f"Available presets: {', '.join(available)}"]
        except ImportError:
            suggestions = ["Check preset name spelling"]
        
        super().__init__(message,
                        error_code="PRESET_ERROR",
                        context=context,
                        suggestions=suggestions)


# ============================================================================
# SECURITY ERRORS (A+ Enhanced)
# ============================================================================

class XWNodeSecurityError(XWNodeError):
    """Base exception for security-related errors."""
    pass


class XWNodeLimitError(XWNodeSecurityError):
    """Raised when resource limits are exceeded."""
    
    __slots__ = ('resource', 'limit', 'actual_value')
    
    def __init__(self, resource: str, limit: Union[int, str], actual_value: Union[int, str] = None):
        self.resource = resource
        self.limit = limit
        self.actual_value = actual_value
        
        message = f"Resource limit exceeded for {resource}: limit={limit}"
        if actual_value is not None:
            message += f", actual={actual_value}"
        
        context = {
            'resource': resource,
            'limit': limit,
            'actual_value': actual_value
        }
        
        suggestions = [
            f"Increase {resource} limit in configuration",
            "Consider using a more efficient strategy",
            "Break operation into smaller chunks"
        ]
        
        super().__init__(message,
                        error_code="RESOURCE_LIMIT",
                        context=context,
                        suggestions=suggestions)


class XWNodePathSecurityError(XWNodeSecurityError):
    """Raised for path-related security violations."""
    
    __slots__ = ('path', 'violation_type', 'security_policy')
    
    def __init__(self, path: str, violation_type: str, security_policy: str = None):
        self.path = path
        self.violation_type = violation_type
        self.security_policy = security_policy
        
        message = f"Path security violation: {violation_type} in '{path}'"
        if security_policy:
            message += f" (policy: {security_policy})"
        
        context = {
            'path': path,
            'violation_type': violation_type,
            'security_policy': security_policy
        }
        
        suggestions = [
            "Check path for invalid characters or patterns",
            "Use only trusted data sources",
            "Sanitize user input before path operations"
        ]
        
        super().__init__(message,
                        error_code="PATH_SECURITY",
                        context=context,
                        suggestions=suggestions)


# ============================================================================
# PERFORMANCE OPTIMIZATION HELPERS
# ============================================================================

def safe_path_access(get_child_func, path: str, segment: str, node=None):
    """
    Optimized wrapper for path access with minimal error overhead.
    
    This function encapsulates the zero-overhead error handling pattern:
    - Fast path when operation succeeds
    - Rich error context only on failure
    """
    try:
        # Fast path - no error overhead when successful
        return get_child_func(segment)
    except KeyError:
        # Only create rich error on failure path
        available = []
        if node and hasattr(node, 'keys'):
            available = list(node.keys())
        raise ErrorFactory.path_not_found(path, segment, available)
    except IndexError:
        # Index out of bounds
        length = len(node) if node and hasattr(node, '__len__') else 0
        try:
            index = int(segment)
            raise ErrorFactory.index_out_of_bounds(path, index, length)
        except ValueError:
            # Non-numeric index on list
            raise ErrorFactory.type_mismatch(path, segment, "list")
    except TypeError:
        # Type mismatch - trying to access child of leaf
        node_type = type(node).__name__ if node else "unknown"
        raise ErrorFactory.type_mismatch(path, segment, node_type)


# ============================================================================
# LEGACY COMPATIBILITY (Backwards compatibility)
# ============================================================================

# Keep old error names for backwards compatibility
XWNodeValidationError = XWNodeValueError
XWNodeSerializationError = XWNodeError
XWNodePerformanceError = XWNodeError  
XWNodeConfigurationError = XWNodeError

# Strategy errors (maintained for compatibility)
XWNodeIllegalMigrationError = XWNodeStrategyError
XWNodeStrategyNotFoundError = XWNodeStrategyError
XWNodeStrategyInitializationError = XWNodeStrategyError
XWNodeConcurrencyError = XWNodeStrategyError


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core error system
    'XWNodeError',
    'XWNodePathError', 
    'XWNodeTypeError',
    'XWNodeValueError',
    
    # Security errors
    'XWNodeSecurityError',
    'XWNodeLimitError',
    'XWNodePathSecurityError',
    
    # Strategy errors
    'XWNodeStrategyError',
    'XWNodeUnsupportedCapabilityError',
    'XWNodePresetError',
    
    # Performance helpers
    'ErrorFactory',
    'safe_path_access',
    
    # Legacy compatibility
    'XWNodeValidationError',
    'XWNodeSerializationError', 
    'XWNodePerformanceError',
    'XWNodeConfigurationError',
    'XWNodeIllegalMigrationError',
    'XWNodeStrategyNotFoundError',
    'XWNodeStrategyInitializationError',
    'XWNodeConcurrencyError'
]
