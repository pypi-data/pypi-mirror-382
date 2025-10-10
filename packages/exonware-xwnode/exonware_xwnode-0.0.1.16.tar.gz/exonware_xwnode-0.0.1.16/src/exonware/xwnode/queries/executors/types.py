#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/types.py

Executor Types and Enums

Module-specific types for query operation executors.
Imports shared types from root types.py per DEV_GUIDELINES.md.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 08-Oct-2025
"""

from enum import Enum, Flag, auto

# Import shared types from root
from ...types import QueryMode, QueryTrait

# Import node type from nodes module
from ...nodes.strategies.contracts import NodeType


class OperationType(Enum):
    """
    Operation category classification.
    
    Used to group the 50 operations by their primary purpose.
    """
    CORE = auto()           # SELECT, INSERT, UPDATE, DELETE, CREATE, DROP
    FILTERING = auto()      # WHERE, FILTER, BETWEEN, LIKE, IN, HAS
    AGGREGATION = auto()    # GROUP BY, HAVING, SUM, AVG, COUNT, MIN, MAX, DISTINCT
    ORDERING = auto()       # ORDER BY, LIMIT, OFFSET
    JOINING = auto()        # JOIN, UNION, WITH, OPTIONAL
    GRAPH = auto()          # MATCH, PATH, OUT, IN_TRAVERSE, RETURN
    PROJECTION = auto()     # PROJECT, EXTEND, CONSTRUCT
    SEARCH = auto()         # TERM, RANGE
    DATA_OPS = auto()       # LOAD, STORE, MERGE, ALTER, DESCRIBE
    CONTROL_FLOW = auto()   # FOREACH, LET, FOR
    WINDOW = auto()         # WINDOW, AGGREGATE
    ARRAY = auto()          # SLICING, INDEXING
    ADVANCED = auto()       # ASK, SUBSCRIBE, MUTATION, PIPE, OPTIONS, VALUES


class ExecutionStatus(Enum):
    """
    Execution status for operations.
    """
    PENDING = auto()        # Not yet started
    VALIDATING = auto()     # Validating action
    EXECUTING = auto()      # Currently executing
    COMPLETED = auto()      # Successfully completed
    FAILED = auto()         # Execution failed
    CANCELLED = auto()      # Execution cancelled


class OperationCapability(Flag):
    """
    Operation capability flags.
    
    Defines what capabilities an operation requires to execute.
    Moved from contracts.py per DEV_GUIDELINES.md (enums in types.py).
    """
    NONE = 0
    
    # Node type requirements
    REQUIRES_LINEAR = auto()
    REQUIRES_TREE = auto()
    REQUIRES_GRAPH = auto()
    REQUIRES_MATRIX = auto()
    
    # Trait requirements
    REQUIRES_ORDERED = auto()
    REQUIRES_INDEXED = auto()
    REQUIRES_HIERARCHICAL = auto()
    REQUIRES_WEIGHTED = auto()
    REQUIRES_SPATIAL = auto()
    
    # Special requirements
    REQUIRES_MUTABLE = auto()
    REQUIRES_TRANSACTIONAL = auto()


__all__ = [
    'OperationType',
    'ExecutionStatus',
    'OperationCapability',
    'NodeType',  # Re-export for convenience
    'QueryMode',  # Re-export from root
    'QueryTrait',  # Re-export from root
]
