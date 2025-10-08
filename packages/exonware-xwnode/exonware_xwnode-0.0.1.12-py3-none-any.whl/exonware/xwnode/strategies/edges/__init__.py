"""
Edge Strategies Package

This package contains all edge strategy implementations organized by type:
- Linear edges (sequential connections)
- Tree edges (hierarchical connections)  
- Graph edges (network connections)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from .base import AEdgeStrategy, ALinearEdgeStrategy, ATreeEdgeStrategy, AGraphEdgeStrategy

# Graph edge strategies
from .adj_list import AdjListStrategy
from .adj_matrix import AdjMatrixStrategy

__all__ = [
    # Base classes
    'AEdgeStrategy',
    'ALinearEdgeStrategy',
    'ATreeEdgeStrategy', 
    'AGraphEdgeStrategy',
    
    # Graph edge strategies
    'AdjListStrategy',
    'AdjMatrixStrategy'
]
