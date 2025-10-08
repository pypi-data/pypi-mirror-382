"""
LSM Tree Node Strategy Implementation

This module implements the LSM_TREE strategy for write-heavy workloads
with eventual consistency and compaction.
"""

from typing import Any, Iterator, Dict, List, Optional, Tuple
import time
import threading
from collections import defaultdict
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class MemTable:
    """In-memory table for LSM tree."""
    
    def __init__(self, max_size: int = 1000):
        self.data: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self.max_size = max_size
        self.size = 0
    
    def put(self, key: str, value: Any) -> bool:
        """Put value, returns True if table is now full."""
        self.data[key] = (value, time.time())
        if key not in self.data:
            self.size += 1
        return self.size >= self.max_size
    
    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        """Get value and timestamp."""
        return self.data.get(key)
    
    def has(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.data
    
    def remove(self, key: str) -> bool:
        """Remove key (tombstone)."""
        if key in self.data:
            self.data[key] = (None, time.time())  # Tombstone
            return True
        return False
    
    def items(self) -> Iterator[Tuple[str, Tuple[Any, float]]]:
        """Get all items."""
        return iter(self.data.items())
    
    def clear(self) -> None:
        """Clear all data."""
        self.data.clear()
        self.size = 0


class SSTable:
    """Sorted String Table for LSM tree."""
    
    def __init__(self, level: int, data: Dict[str, Tuple[Any, float]]):
        self.level = level
        self.data = dict(sorted(data.items()))  # Keep sorted
        self.creation_time = time.time()
        self.size = len(data)
    
    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        """Get value and timestamp."""
        return self.data.get(key)
    
    def has(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.data
    
    def items(self) -> Iterator[Tuple[str, Tuple[Any, float]]]:
        """Get all items in sorted order."""
        return iter(self.data.items())
    
    def keys(self) -> Iterator[str]:
        """Get all keys in sorted order."""
        return iter(self.data.keys())
    
    def range_query(self, start_key: str, end_key: str) -> List[Tuple[str, Any, float]]:
        """Query range [start_key, end_key]."""
        result = []
        for key, (value, timestamp) in self.data.items():
            if start_key <= key <= end_key and value is not None:  # Skip tombstones
                result.append((key, value, timestamp))
        return result


class LSMTreeStrategy(ANodeTreeStrategy):
    """
    LSM Tree node strategy for write-heavy workloads.
    
    Provides excellent write performance with eventual read consistency
    through in-memory memtables and sorted disk-based SSTables.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the LSM Tree strategy."""
        super().__init__(NodeMode.LSM_TREE, traits, **options)
        
        self.memtable_size = options.get('memtable_size', 1000)
        self.max_levels = options.get('max_levels', 7)
        self.level_multiplier = options.get('level_multiplier', 10)
        
        # Storage components
        self.memtable = MemTable(self.memtable_size)
        self.immutable_memtables: List[MemTable] = []
        self.sstables: Dict[int, List[SSTable]] = defaultdict(list)
        self._values: Dict[str, Any] = {}  # Direct key-value cache for fast access
        
        # Compaction control
        self._compaction_lock = threading.RLock()
        self._background_compaction = options.get('background_compaction', False)
        self._last_compaction = time.time()
        
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the LSM tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.STREAMING | NodeTrait.PERSISTENT)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a value (optimized for writes)."""
        key_str = str(key)
        
        # Always write to active memtable first
        was_new_key = key_str not in self._values
        
        if self.memtable.put(key_str, value):
            # Memtable is full, flush to L0
            self._flush_memtable()
        
        # Update our direct storage too for consistency
        self._values[key_str] = value
        
        if was_new_key:
            self._size += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value (may involve multiple lookups)."""
        key_str = str(key)
        
        # 1. Check active memtable first
        result = self.memtable.get(key_str)
        if result is not None:
            value, timestamp = result
            return value if value is not None else default
        
        # 2. Check immutable memtables (newest first)
        for memtable in reversed(self.immutable_memtables):
            result = memtable.get(key_str)
            if result is not None:
                value, timestamp = result
                return value if value is not None else default
        
        # 3. Check SSTables from L0 down (newest first within each level)
        for level in range(self.max_levels):
            for sstable in reversed(self.sstables[level]):
                result = sstable.get(key_str)
                if result is not None:
                    value, timestamp = result
                    return value if value is not None else default
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists (may involve multiple lookups)."""
        return str(key) in self._values
    
    def remove(self, key: Any) -> bool:
        """Remove value by key (writes tombstone)."""
        key_str = str(key)
        
        if not self.has(key_str):
            return False
        
        # Write tombstone to memtable
        if self.memtable.put(key_str, None):  # None = tombstone
            self._flush_memtable()
        
        # Remove from direct cache
        del self._values[key_str]
        self._size -= 1
        return True
    
    def delete(self, key: Any) -> bool:
        """Remove value by key (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        with self._compaction_lock:
            self.memtable.clear()
            self.immutable_memtables.clear()
            self.sstables.clear()
            self._values.clear()
            self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys (merged from all levels)."""
        seen_keys = set()
        
        # Active memtable
        for key, (value, _) in self.memtable.items():
            if value is not None and key not in seen_keys:
                seen_keys.add(key)
                yield key
        
        # Immutable memtables
        for memtable in reversed(self.immutable_memtables):
            for key, (value, _) in memtable.items():
                if value is not None and key not in seen_keys:
                    seen_keys.add(key)
                    yield key
        
        # SSTables
        for level in range(self.max_levels):
            for sstable in reversed(self.sstables[level]):
                for key in sstable.keys():
                    if key not in seen_keys:
                        value, _ = sstable.get(key)
                        if value is not None:
                            seen_keys.add(key)
                            yield key
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        for key in self.keys():
            yield self.get(key)
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        for key in self.keys():
            yield (key, self.get(key))
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self.items())
    
    @property
    def is_list(self) -> bool:
        """This is not primarily a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This is a dict-like strategy."""
        return True
    
    # ============================================================================
    # LSM TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def _flush_memtable(self) -> None:
        """Flush active memtable to L0."""
        if self.memtable.size == 0:
            return
        
        with self._compaction_lock:
            # Move active memtable to immutable
            self.immutable_memtables.append(self.memtable)
            self.memtable = MemTable(self.memtable_size)
            
            # Create L0 SSTable from oldest immutable memtable
            if self.immutable_memtables:
                old_memtable = self.immutable_memtables.pop(0)
                sstable = SSTable(0, old_memtable.data)
                self.sstables[0].append(sstable)
                
                # Trigger compaction if needed
                self._maybe_compact()
    
    def _maybe_compact(self) -> None:
        """Check if compaction is needed and trigger it."""
        # Simple compaction strategy: compact when level has too many SSTables
        for level in range(self.max_levels - 1):
            max_sstables = self.level_multiplier ** level
            if len(self.sstables[level]) > max_sstables:
                self._compact_level(level)
                break
    
    def _compact_level(self, level: int) -> None:
        """Compact SSTables from level to level+1."""
        if level >= self.max_levels - 1:
            return
        
        # Simple compaction: merge all SSTables in level
        merged_data = {}
        
        for sstable in self.sstables[level]:
            for key, (value, timestamp) in sstable.items():
                if key not in merged_data or timestamp > merged_data[key][1]:
                    merged_data[key] = (value, timestamp)
        
        # Remove tombstones and create new SSTable
        clean_data = {k: v for k, v in merged_data.items() if v[0] is not None}
        
        if clean_data:
            new_sstable = SSTable(level + 1, clean_data)
            self.sstables[level + 1].append(new_sstable)
        
        # Clear the compacted level
        self.sstables[level].clear()
        
        self._last_compaction = time.time()
    
    def force_compaction(self) -> None:
        """Force full compaction of all levels."""
        with self._compaction_lock:
            # Flush any pending memtables first
            if self.memtable.size > 0:
                self._flush_memtable()
            
            # Compact each level
            for level in range(self.max_levels - 1):
                if self.sstables[level]:
                    self._compact_level(level)
    
    def range_query(self, start_key: str, end_key: str) -> List[Tuple[str, Any]]:
        """Efficient range query across all levels."""
        result_map = {}
        
        # Query all levels and merge results (newest wins)
        for level in range(self.max_levels):
            for sstable in self.sstables[level]:
                for key, value, timestamp in sstable.range_query(start_key, end_key):
                    if key not in result_map or timestamp > result_map[key][1]:
                        result_map[key] = (value, timestamp)
        
        # Return sorted results (excluding tombstones)
        return [(k, v) for k, (v, _) in sorted(result_map.items()) if v is not None]
    
    def get_level_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get statistics for each level."""
        stats = {}
        for level in range(self.max_levels):
            sstables = self.sstables[level]
            stats[level] = {
                'sstable_count': len(sstables),
                'total_keys': sum(sstable.size for sstable in sstables),
                'oldest_sstable': min((ss.creation_time for ss in sstables), default=0),
                'newest_sstable': max((ss.creation_time for ss in sstables), default=0)
            }
        return stats
    
    def compact_if_needed(self) -> bool:
        """Check and perform compaction if needed."""
        # Compaction heuristics
        total_sstables = sum(len(tables) for tables in self.sstables.values())
        time_since_last = time.time() - self._last_compaction
        
        if total_sstables > 50 or time_since_last > 300:  # 5 minutes
            self.force_compaction()
            return True
        return False
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'LSM_TREE',
            'backend': 'Memtables + SSTables',
            'memtable_size': self.memtable_size,
            'max_levels': self.max_levels,
            'complexity': {
                'write': 'O(1) amortized',
                'read': 'O(log n) worst case',
                'range_query': 'O(log n + k)',
                'compaction': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        total_sstables = sum(len(tables) for tables in self.sstables.values())
        memtable_utilization = self.memtable.size / self.memtable_size * 100
        
        return {
            'size': self._size,
            'active_memtable_size': self.memtable.size,
            'immutable_memtables': len(self.immutable_memtables),
            'total_sstables': total_sstables,
            'memtable_utilization': f"{memtable_utilization:.1f}%",
            'last_compaction': self._last_compaction,
            'memory_usage': f"{(self.memtable.size + total_sstables * 500) * 24} bytes (estimated)"
        }
