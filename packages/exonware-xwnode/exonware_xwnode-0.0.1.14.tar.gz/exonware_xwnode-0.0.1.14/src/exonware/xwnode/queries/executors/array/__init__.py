"""Array operation executors."""

from .slicing_executor import SlicingExecutor
from .indexing_executor import IndexingExecutor

__all__ = [
    'SlicingExecutor',
    'IndexingExecutor',
]
