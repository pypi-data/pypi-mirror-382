"""
DATA_INTERCHANGE_OPTIMIZED Node Strategy Implementation

Ultra-lightweight strategy specifically optimized for data interchange patterns:
- Copy-on-write semantics for data interchange
- Object pooling support for factory patterns  
- Structural hash caching for fast equality checks
- Minimal metadata overhead
- Zero graph features for maximum performance
- __slots__ optimization for memory efficiency
"""

import weakref
from typing import Any, Iterator, Dict, List, Optional
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError

# Import shared utilities
from ..utils import (
    recursive_to_native, is_sequential_numeric_keys, 
    calculate_structural_hash, create_performance_tracker
)


class DataInterchangeOptimizedStrategy(aNodeStrategy):
    """
    Ultra-lightweight node strategy optimized for data interchange patterns.
    
    This strategy provides maximum performance for data interchange patterns:
    - O(1) hash map operations using Python dict
    - COW semantics with lazy copying
    - Structural hash caching for fast equality
    - Object pooling support
    - Minimal memory overhead with __slots__
    - Zero graph/edge overhead
    """
    
    __slots__ = (
        '_data', '_size', '_hash_cache', '_frozen', '_cow_enabled',
        '_pool_ref', '_creation_time', '_access_count', 'mode', 'traits', 'options'
    )
    
    def __init__(self, traits: NodeTrait = NodeTrait.INDEXED, **options):
        """Initialize the xData-optimized strategy."""
        # Initialize parent without calling super() to avoid dict overhead
        self.mode = NodeMode.HASH_MAP  # Using HASH_MAP as base mode
        self.traits = traits
        self.options = options
        
        # Core data storage (ultra-efficient)
        self._data: Dict[str, Any] = {}
        self._size = 0
        
        # COW optimization flags
        self._hash_cache: Optional[int] = None
        self._frozen = False  # True after first copy
        self._cow_enabled = options.get('enable_cow', True)
        
        # Object pooling support
        self._pool_ref: Optional[weakref.ref] = None
        
        # Performance tracking (minimal overhead)
        self._creation_time = options.get('creation_time', 0)
        self._performance_tracker = create_performance_tracker()
        
        self._validate_traits()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the xData-optimized strategy."""
        return NodeTrait.INDEXED  # Only essential traits for maximum performance
    
    # ============================================================================
    # ULTRA-OPTIMIZED CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair with COW optimization."""
        self._ensure_mutable()
        
        str_key = str(key)
        if str_key not in self._data:
            self._size += 1
        
        self._data[str_key] = value
        self._invalidate_cache()
        self._performance_tracker.record_access()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key (zero-overhead success path)."""
        self._performance_tracker.record_access()
        return self._data.get(str(key), default)
    
    def has(self, key: Any) -> bool:
        """Check if key exists (optimized)."""
        return str(key) in self._data
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair with COW."""
        self._ensure_mutable()
        
        str_key = str(key)
        if str_key in self._data:
            del self._data[str_key]
            self._size -= 1
            self._invalidate_cache()
            return True
        return False
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair (alias for delete)."""
        return self.delete(key)
    
    def clear(self) -> None:
        """Clear all data with COW."""
        self._ensure_mutable()
        self._data.clear()
        self._size = 0
        self._invalidate_cache()
    
    def keys(self) -> Iterator[str]:
        """Get all keys (zero-copy iterator)."""
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values (zero-copy iterator)."""
        return iter(self._data.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs (zero-copy iterator)."""
        return iter(self._data.items())
    
    def __len__(self) -> int:
        """Get the number of items (zero overhead)."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary (optimized for xData)."""
        # Return a copy with all nested XWNode objects converted to native types
        return {k: recursive_to_native(v) for k, v in self._data.items()}
    
    # ============================================================================
    # COPY-ON-WRITE OPTIMIZATIONS (xData Specific)
    # ============================================================================
    
    def _ensure_mutable(self) -> None:
        """Ensure this instance is mutable (COW implementation)."""
        if not self._cow_enabled:
            return
            
        if self._frozen:
            # Create a new data dict (copy-on-write)
            self._data = dict(self._data)
            self._frozen = False
            self._invalidate_cache()
    
    def freeze(self) -> None:
        """Freeze this instance for COW (called after first copy)."""
        if self._cow_enabled:
            self._frozen = True
    
    def copy(self) -> 'DataInterchangeOptimizedStrategy':
        """Create a COW copy of this strategy."""
        if self._cow_enabled:
            self.freeze()
        
        # Create new instance sharing data until mutation
        new_instance = DataInterchangeOptimizedStrategy(self.traits, **self.options)
        new_instance._data = self._data  # Shared until mutation
        new_instance._size = self._size
        new_instance._hash_cache = self._hash_cache
        new_instance._frozen = False  # New instance can be mutated
        
        return new_instance
    
    # ============================================================================
    # STRUCTURAL HASH CACHING (xData Performance)
    # ============================================================================
    
    def _invalidate_cache(self) -> None:
        """Invalidate cached hash (minimal overhead)."""
        self._hash_cache = None
    
    def structural_hash(self) -> int:
        """Get structural hash with caching (xData equality optimization)."""
        if self._hash_cache is None:
            # Compute hash based on structure, not values
            # This is optimized for xData's equality checking
            self._hash_cache = calculate_structural_hash(self._data)
        
        return self._hash_cache
    
    def fast_equals(self, other: 'DataInterchangeOptimizedStrategy') -> bool:
        """Fast equality check using structural hashes."""
        if not isinstance(other, DataInterchangeOptimizedStrategy):
            return False
        
        # Quick size check
        if self._size != other._size:
            return False
        
        # Structural hash comparison (much faster than deep comparison)
        return self.structural_hash() == other.structural_hash()
    
    # ============================================================================
    # OBJECT POOLING SUPPORT (Factory Pattern)
    # ============================================================================
    
    def set_pool_reference(self, pool_ref: weakref.ref) -> None:
        """Set reference to object pool for cleanup."""
        self._pool_ref = pool_ref
    
    def return_to_pool(self) -> None:
        """Return this instance to object pool if available."""
        if self._pool_ref is not None:
            pool = self._pool_ref()
            if pool is not None:
                # Reset state for reuse
                self._data.clear()
                self._size = 0
                self._invalidate_cache()
                self._frozen = False
                self._performance_tracker.reset()
                pool.return_instance(self)
    
    def __del__(self):
        """Destructor with object pool support."""
        self.return_to_pool()
    
    # ============================================================================
    # XDATA-SPECIFIC OPTIMIZATIONS
    # ============================================================================
    
    @property
    def is_list(self) -> bool:
        """Check if this represents a list (optimized for xData)."""
        return is_sequential_numeric_keys(self._data)
    
    @property
    def is_dict(self) -> bool:
        """Check if this represents a dict (optimized for xData)."""
        return not self.is_list
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (xData pattern)."""
        return len(self._data) == 1 and "value" in self._data
    
    # ============================================================================
    # PERFORMANCE MONITORING (Minimal Overhead)
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'DATA_INTERCHANGE_OPTIMIZED',
            'backend': 'Optimized Python dict with COW',
            'complexity': {
                'get': 'O(1)',
                'put': 'O(1)',
                'has': 'O(1)', 
                'delete': 'O(1)'
            },
            'features': [
                'copy_on_write',
                'structural_hashing',
                'object_pooling',
                'slots_optimization'
            ]
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        metrics = self._performance_tracker.get_metrics()
        metrics.update({
            'size': self._size,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'is_frozen': self._frozen,
            'hash_cached': self._hash_cache is not None,
            'cow_enabled': self._cow_enabled,
            'creation_time': self._creation_time
        })
        return metrics
    
    def get_xdata_stats(self) -> Dict[str, Any]:
        """Get xData-specific performance statistics."""
        return {
            'strategy': 'DATA_INTERCHANGE_OPTIMIZED',
            'cow_active': self._cow_enabled,
            'frozen_state': self._frozen,
            'cache_efficiency': 'cached' if self._hash_cache else 'not_cached',
            'memory_footprint': 'minimal',
            'graph_overhead': 'zero',
            'pooling_support': self._pool_ref is not None,
            'access_pattern': f"{self._performance_tracker.get_metrics()['access_count']} operations"
        }
    
    # ============================================================================
    # DISABLED FEATURES (Maximum Performance)
    # ============================================================================
    
    def get_ordered(self, start: Any = None, end: Any = None) -> List[tuple[Any, Any]]:
        """Ordered operations not supported in DATA_INTERCHANGE_OPTIMIZED."""
        raise XWNodeUnsupportedCapabilityError(
            'ordered_operations', 
            'DATA_INTERCHANGE_OPTIMIZED',
            ['fast_lookup', 'copy_on_write', 'structural_hashing']
        ).suggest("Use preset='ANALYTICS' for ordered operations")
    
    def get_with_prefix(self, prefix: str) -> List[tuple[Any, Any]]:
        """Prefix operations not optimized in DATA_INTERCHANGE_OPTIMIZED."""
        raise XWNodeUnsupportedCapabilityError(
            'prefix_operations',
            'DATA_INTERCHANGE_OPTIMIZED', 
            ['fast_lookup', 'copy_on_write']
        ).suggest("Use preset='SEARCH_ENGINE' for prefix operations")
    
    def get_priority(self) -> Optional[tuple[Any, Any]]:
        """Priority operations not supported in DATA_INTERCHANGE_OPTIMIZED."""
        raise XWNodeUnsupportedCapabilityError(
            'priority_operations',
            'DATA_INTERCHANGE_OPTIMIZED',
            ['fast_lookup', 'copy_on_write']
        ).suggest("Use preset='ANALYTICS' with heap structure for priorities")
    
    # ============================================================================
    # STRING REPRESENTATION (Optimized)
    # ============================================================================
    
    def __str__(self) -> str:
        """Optimized string representation."""
        return f"DataInterchangeOptimized(size={self._size}, cow={self._cow_enabled})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"DataInterchangeOptimizedStrategy(size={self._size}, "
                f"frozen={self._frozen}, cow={self._cow_enabled}, "
                f"cached={self._hash_cache is not None})")


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_data_interchange_optimized_strategy(**options) -> DataInterchangeOptimizedStrategy:
    """
    Factory function for creating data interchange optimized strategy instances.
    
    This function provides the recommended way to create DATA_INTERCHANGE_OPTIMIZED
    strategy instances with proper configuration for data interchange usage.
    """
    # Set data interchange specific optimizations
    data_interchange_options = {
        'enable_cow': True,
        'enable_pooling': True,
        'enable_hash_caching': True,
        'minimal_metadata': True,
        'slots_optimization': True,
        'fast_creation': True,
        'lazy_loading': False,  # Eager loading for predictability
        'memory_profile': 'ultra_minimal'
    }
    
    # Merge with user options
    data_interchange_options.update(options)
    
    return DataInterchangeOptimizedStrategy(NodeTrait.INDEXED, **data_interchange_options)
