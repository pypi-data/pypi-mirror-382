"""
Shared utilities for XWNode strategies.

This module provides common functionality that can be used by multiple strategies
without creating cross-dependencies between strategies.
"""

import threading
from typing import Any, Dict, List, Optional, Iterator, Tuple, Union
from collections import OrderedDict
import weakref
import time

# Use xSystem logging
from exonware.xwsystem import get_logger

logger = get_logger('xnode.strategies.utils')


# ============================================================================
# PATH PARSING UTILITIES
# ============================================================================

class PathParser:
    """Thread-safe path parser with caching for use by multiple strategies."""
    
    def __init__(self, max_cache_size: int = 1024):
        self._cache = OrderedDict()
        self._max_cache_size = max_cache_size
        self._lock = threading.RLock()
    
    def parse(self, path: str) -> List[str]:
        """Parse a path string into parts."""
        with self._lock:
            if path in self._cache:
                return self._cache[path]
            
            parts = self._parse_path(path)
            
            # Cache the result
            if len(self._cache) >= self._max_cache_size:
                self._cache.popitem(last=False)
            self._cache[path] = parts
            
            return parts
    
    def _parse_path(self, path: str) -> List[str]:
        """Internal path parsing logic."""
        if not path:
            return []
        
        # Simple dot-separated path parsing
        return [part for part in path.split('.') if part]


# ============================================================================
# ADVANCED DATA STRUCTURES (Shared implementations)
# ============================================================================

class TrieNode:
    """Internal node for Trie structure - shared across strategies."""
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_word: bool = False
        self.value: Any = None
    
    def __repr__(self):
        return f"TrieNode(children={len(self.children)}, is_end={self.is_end_word})"


class UnionFind:
    """Union-Find (Disjoint Set) data structure - shared across strategies."""
    
    def __init__(self):
        self._parent: Dict[Any, Any] = {}
        self._rank: Dict[Any, int] = {}
        self._sets_count = 0
    
    def make_set(self, x: Any) -> None:
        """Create new set with element x. O(1)"""
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
            self._sets_count += 1
    
    def find(self, x: Any) -> Any:
        """Find root of set containing x with path compression. α(n) ≈ O(1)"""
        if x not in self._parent:
            raise ValueError(f"Element {x} not found in union-find structure")
        
        # Path compression
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        
        return self._parent[x]
    
    def union(self, x: Any, y: Any) -> None:
        """Union sets containing x and y by rank. α(n) ≈ O(1)"""
        # Ensure both elements exist
        self.make_set(x)
        self.make_set(y)
        
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return  # Already in same set
        
        # Union by rank
        if self._rank[root_x] < self._rank[root_y]:
            root_x, root_y = root_y, root_x
        
        self._parent[root_y] = root_x
        if self._rank[root_x] == self._rank[root_y]:
            self._rank[root_x] += 1
        
        self._sets_count -= 1
    
    def connected(self, x: Any, y: Any) -> bool:
        """Check if x and y are in same set. α(n) ≈ O(1)"""
        try:
            return self.find(x) == self.find(y)
        except ValueError:
            return False
    
    def size(self) -> int:
        """Get number of elements. O(1)"""
        return len(self._parent)
    
    def sets_count(self) -> int:
        """Get number of disjoint sets. O(1)"""
        return self._sets_count


class MinHeap:
    """Min-heap implementation for priority queue operations - shared across strategies."""
    
    def __init__(self):
        self._heap: List[Tuple[float, Any]] = []
        self._size = 0
    
    def push(self, value: Any, priority: float = 0.0) -> None:
        """Push item with priority. O(log n)"""
        self._heap.append((priority, value))
        self._size += 1
        self._heapify_up(self._size - 1)
    
    def pop_min(self) -> Any:
        """Pop minimum priority item. O(log n)"""
        if self._size == 0:
            raise IndexError("Heap is empty")
        
        min_val = self._heap[0][1]
        self._heap[0] = self._heap[self._size - 1]
        self._heap.pop()
        self._size -= 1
        
        if self._size > 0:
            self._heapify_down(0)
        
        return min_val
    
    def peek_min(self) -> Any:
        """Peek at minimum without removing. O(1)"""
        if self._size == 0:
            raise IndexError("Heap is empty")
        return self._heap[0][1]
    
    def _heapify_up(self, index: int) -> None:
        """Move element up to maintain heap property."""
        parent = (index - 1) // 2
        if parent >= 0 and self._heap[index][0] < self._heap[parent][0]:
            self._heap[index], self._heap[parent] = self._heap[parent], self._heap[index]
            self._heapify_up(parent)
    
    def _heapify_down(self, index: int) -> None:
        """Move element down to maintain heap property."""
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < self._size and self._heap[left][0] < self._heap[smallest][0]:
            smallest = left
        
        if right < self._size and self._heap[right][0] < self._heap[smallest][0]:
            smallest = right
        
        if smallest != index:
            self._heap[index], self._heap[smallest] = self._heap[smallest], self._heap[index]
            self._heapify_down(smallest)
    
    def size(self) -> int:
        """Get heap size. O(1)"""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if heap is empty. O(1)"""
        return self._size == 0


# ============================================================================
# COMMON UTILITY FUNCTIONS
# ============================================================================

def recursive_to_native(obj: Any) -> Any:
    """
    Recursively convert objects to native Python types.
    
    This is a shared utility for converting complex objects (including XWNode objects)
    to native Python types for serialization and comparison.
    """
    if hasattr(obj, 'to_native'):
        # This is an XWNode, recursively convert it
        return recursive_to_native(obj.to_native())
    elif isinstance(obj, dict):
        return {k: recursive_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_to_native(item) for item in obj]
    else:
        return obj


def is_sequential_numeric_keys(data: Dict[str, Any]) -> bool:
    """
    Check if dictionary keys are sequential numeric indices (for list detection).
    
    This is useful for determining if a dict represents a list structure.
    """
    if not data:
        return False
    
    keys = list(data.keys())
    try:
        indices = [int(k) for k in keys]
        return indices == list(range(len(indices)))
    except ValueError:
        return False


def calculate_structural_hash(data: Dict[str, Any]) -> int:
    """
    Calculate a structural hash based on keys only (not values).
    
    This is useful for fast equality checking when values don't matter.
    """
    return hash(tuple(sorted(data.keys())))


def validate_traits(supported_traits, requested_traits, strategy_name: str) -> None:
    """
    Validate that requested traits are supported by a strategy.
    
    Args:
        supported_traits: Traits supported by the strategy
        requested_traits: Traits requested by the user
        strategy_name: Name of the strategy for error messages
    """
    unsupported = requested_traits & ~supported_traits
    if unsupported != 0:
        unsupported_names = [trait.name for trait in unsupported]
        raise ValueError(f"Strategy {strategy_name} does not support traits: {unsupported_names}")


# ============================================================================
# PERFORMANCE MONITORING UTILITIES
# ============================================================================

class PerformanceTracker:
    """Shared performance tracking utilities for strategies."""
    
    def __init__(self):
        self._access_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._operation_times: Dict[str, List[float]] = {}
        self._lock = threading.RLock()
    
    def record_access(self) -> None:
        """Record a data access operation."""
        with self._lock:
            self._access_count += 1
    
    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        with self._lock:
            self._cache_hits += 1
    
    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        with self._lock:
            self._cache_misses += 1
    
    def record_operation_time(self, operation: str, time_taken: float) -> None:
        """Record the time taken for an operation."""
        with self._lock:
            if operation not in self._operation_times:
                self._operation_times[operation] = []
            self._operation_times[operation].append(time_taken)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._lock:
            metrics = {
                'access_count': self._access_count,
                'cache_hits': self._cache_hits,
                'cache_misses': self._cache_misses,
            }
            
            # Calculate cache hit rate
            total_cache_ops = self._cache_hits + self._cache_misses
            if total_cache_ops > 0:
                metrics['cache_hit_rate'] = self._cache_hits / total_cache_ops
            else:
                metrics['cache_hit_rate'] = 0.0
            
            # Calculate average operation times
            for operation, times in self._operation_times.items():
                if times:
                    metrics[f'{operation}_avg_time'] = sum(times) / len(times)
                    metrics[f'{operation}_min_time'] = min(times)
                    metrics[f'{operation}_max_time'] = max(times)
            
            return metrics
    
    def reset(self) -> None:
        """Reset all performance counters."""
        with self._lock:
            self._access_count = 0
            self._cache_hits = 0
            self._cache_misses = 0
            self._operation_times.clear()


# ============================================================================
# OBJECT POOLING UTILITIES
# ============================================================================

class ObjectPool:
    """Generic object pool for strategies that need pooling."""
    
    def __init__(self, max_size: int = 100):
        self._pool: List[Any] = []
        self._max_size = max_size
        self._lock = threading.RLock()
        self._stats = {
            'created': 0,
            'reused': 0,
            'pooled': 0
        }
    
    def get_object(self, factory_func, *args, **kwargs) -> Any:
        """
        Get an object from the pool or create a new one.
        
        Args:
            factory_func: Function to create new objects
            *args, **kwargs: Arguments for factory function
            
        Returns:
            Object from pool or newly created
        """
        with self._lock:
            if self._pool:
                # Reuse existing object
                obj = self._pool.pop()
                self._stats['reused'] += 1
                logger.debug(f"♻️ Reused object from pool")
                return obj
            else:
                # Create new object
                obj = factory_func(*args, **kwargs)
                self._stats['created'] += 1
                logger.debug(f"🆕 Created new object")
                return obj
    
    def return_object(self, obj: Any, reset_func=None) -> None:
        """
        Return an object to the pool for reuse.
        
        Args:
            obj: Object to return to pool
            reset_func: Optional function to reset object state
        """
        with self._lock:
            if len(self._pool) < self._max_size:
                if reset_func:
                    reset_func(obj)
                self._pool.append(obj)
                self._stats['pooled'] += 1
                logger.debug(f"🔄 Returned object to pool")
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats['pool_size'] = len(self._pool)
            return stats
    
    @property
    def efficiency(self) -> float:
        """Get pool efficiency (reuse rate)."""
        total = self._stats['created'] + self._stats['reused']
        return self._stats['reused'] / total if total > 0 else 0.0
    
    def clear(self) -> None:
        """Clear all pooled objects."""
        with self._lock:
            self._pool.clear()
            logger.info("🧹 Cleared object pool")


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_path_parser(max_cache_size: int = 1024) -> PathParser:
    """Create a path parser instance."""
    return PathParser(max_cache_size)


def create_performance_tracker() -> PerformanceTracker:
    """Create a performance tracker instance."""
    return PerformanceTracker()


def create_object_pool(max_size: int = 100) -> ObjectPool:
    """Create an object pool instance."""
    return ObjectPool(max_size)


def create_basic_metrics(strategy_name: str, size: int, **additional_metrics) -> Dict[str, Any]:
    """Create basic metrics dictionary for strategies."""
    metrics = {
        'strategy': strategy_name,
        'size': size,
        'memory_usage': f"{size * 64} bytes (estimated)",
        'timestamp': time.time()
    }
    metrics.update(additional_metrics)
    return metrics


def create_basic_backend_info(strategy_name: str, backend_type: str, **additional_info) -> Dict[str, Any]:
    """Create basic backend info dictionary for strategies."""
    info = {
        'strategy': strategy_name,
        'backend': backend_type,
        'complexity': {
            'get': 'O(1) average',
            'put': 'O(1) average',
            'has': 'O(1) average',
            'remove': 'O(1) average'
        }
    }
    info.update(additional_info)
    return info


def is_list_like(keys: List[str]) -> bool:
    """Check if keys represent a list-like structure."""
    if not keys:
        return False
    
    # Check if all keys are numeric and consecutive starting from 0
    try:
        numeric_keys = [int(key) for key in keys]
        return numeric_keys == list(range(len(numeric_keys)))
    except (ValueError, TypeError):
        return False


def safe_to_native_conversion(data: Any) -> Any:
    """Safely convert data to native Python types, handling XWNode objects."""
    if hasattr(data, 'to_native'):
        # This is an XWNode, recursively convert it
        return safe_to_native_conversion(data.to_native())
    elif isinstance(data, dict):
        return {k: safe_to_native_conversion(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [safe_to_native_conversion(item) for item in data]
    elif isinstance(data, (set, frozenset)):
        return {safe_to_native_conversion(item) for item in data}
    else:
        return data


def create_strategy_logger(strategy_name: str):
    """Create a logger for a specific strategy."""
    return get_logger(f"xnode.strategy.{strategy_name}")


def validate_strategy_options(options: Dict[str, Any], allowed_options: List[str]) -> Dict[str, Any]:
    """Validate strategy options and return only allowed ones."""
    return {k: v for k, v in options.items() if k in allowed_options}


def create_size_tracker() -> Dict[str, int]:
    """Create a size tracking dictionary."""
    return {'size': 0}


def update_size_tracker(tracker: Dict[str, int], delta: int) -> None:
    """Update size tracker with delta change."""
    tracker['size'] = max(0, tracker['size'] + delta)


def create_access_tracker() -> Dict[str, int]:
    """Create an access tracking dictionary."""
    return {
        'get_count': 0,
        'put_count': 0,
        'delete_count': 0,
        'access_count': 0
    }


def record_access(tracker: Dict[str, int], operation: str) -> None:
    """Record an access operation."""
    if operation in tracker:
        tracker[operation] += 1
    tracker['access_count'] += 1


def get_access_metrics(tracker: Dict[str, int]) -> Dict[str, Any]:
    """Get access metrics from tracker."""
    return {
        'total_accesses': tracker['access_count'],
        'get_operations': tracker['get_count'],
        'put_operations': tracker['put_count'],
        'delete_operations': tracker['delete_count']
    }
