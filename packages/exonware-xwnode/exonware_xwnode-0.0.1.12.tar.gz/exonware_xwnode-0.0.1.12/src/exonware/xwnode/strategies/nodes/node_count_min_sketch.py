"""
Count-Min Sketch Node Strategy Implementation

This module implements the COUNT_MIN_SKETCH strategy for probabilistic
frequency estimation in data streams with bounded error guarantees.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
import hashlib
import math
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class xCountMinSketchStrategy(aNodeStrategy):
    """
    Count-Min Sketch node strategy for streaming frequency estimation.
    
    Provides memory-efficient approximate frequency counting with 
    probabilistic error bounds and no false negatives.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Count-Min Sketch strategy."""
        super().__init__(NodeMode.COUNT_MIN_SKETCH, traits, **options)
        
        # Sketch parameters
        self.epsilon = options.get('epsilon', 0.01)  # Error bound (1%)
        self.delta = options.get('delta', 0.01)     # Confidence (99%)
        
        # Calculate dimensions
        self.width = self._calculate_width()
        self.depth = self._calculate_depth()
        
        # Core sketch matrix
        self._sketch: List[List[int]] = [[0 for _ in range(self.width)] for _ in range(self.depth)]
        
        # Hash functions (using different seeds)
        self._hash_seeds = self._generate_hash_seeds()
        
        # Key-value mapping for compatibility
        self._values: Dict[str, Any] = {}
        self._total_count = 0
        self._unique_items = set()
        self._size = 0
        
        # Heavy hitters tracking
        self.track_heavy_hitters = options.get('track_heavy_hitters', True)
        self.heavy_hitter_threshold = options.get('heavy_hitter_threshold', 0.01)  # 1% of total
        self._heavy_hitters: Dict[str, int] = {}
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the count-min sketch strategy."""
        return (NodeTrait.PROBABILISTIC | NodeTrait.COMPRESSED | NodeTrait.STREAMING)
    
    def _calculate_width(self) -> int:
        """Calculate sketch width based on error bound."""
        # width = ceil(e / epsilon)
        e = math.e
        return max(1, int(math.ceil(e / self.epsilon)))
    
    def _calculate_depth(self) -> int:
        """Calculate sketch depth based on confidence."""
        # depth = ceil(ln(1/delta))
        return max(1, int(math.ceil(math.log(1.0 / self.delta))))
    
    def _generate_hash_seeds(self) -> List[int]:
        """Generate seeds for hash functions."""
        seeds = []
        for i in range(self.depth):
            # Use different primes as seeds
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
            seed = primes[i % len(primes)] * (i + 1) * 1000 + i
            seeds.append(seed)
        return seeds
    
    def _hash_item(self, item: str, seed: int) -> int:
        """Hash item to bucket using given seed."""
        hash_obj = hashlib.md5(f"{item}{seed}".encode())
        hash_value = int(hash_obj.hexdigest(), 16)
        return hash_value % self.width
    
    def _update_heavy_hitters(self, item: str, estimated_count: int) -> None:
        """Update heavy hitters tracking."""
        if not self.track_heavy_hitters:
            return
        
        threshold = self._total_count * self.heavy_hitter_threshold
        
        if estimated_count >= threshold:
            self._heavy_hitters[item] = estimated_count
        else:
            # Remove from heavy hitters if below threshold
            self._heavy_hitters.pop(item, None)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add item to count-min sketch."""
        item = str(key)
        count = 1
        
        # If value is a number, treat it as count
        if isinstance(value, (int, float)) and value > 0:
            count = int(value)
        
        # Update sketch
        for i in range(self.depth):
            bucket = self._hash_item(item, self._hash_seeds[i])
            self._sketch[i][bucket] += count
        
        # Update tracking
        self._total_count += count
        self._unique_items.add(item)
        
        # Store value
        self._values[item] = value if value is not None else count
        
        if item not in self._values or self._size == 0:
            self._size += 1
        
        # Update heavy hitters
        estimated_count = self.estimate_count(item)
        self._update_heavy_hitters(item, estimated_count)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get estimated count or stored value."""
        item = str(key)
        
        if key == "total_count":
            return self._total_count
        elif key == "unique_items":
            return len(self._unique_items)
        elif key == "heavy_hitters":
            return dict(self._heavy_hitters)
        elif key == "sketch_info":
            return {
                'width': self.width,
                'depth': self.depth,
                'epsilon': self.epsilon,
                'delta': self.delta,
                'total_count': self._total_count
            }
        elif key == "estimated_count":
            # Return function to estimate any item
            return lambda x: self.estimate_count(x)
        elif item in self._values:
            return self._values[item]
        else:
            # Return estimated count
            return self.estimate_count(item)
    
    def has(self, key: Any) -> bool:
        """Check if item might exist (probabilistic)."""
        item = str(key)
        
        if key in ["total_count", "unique_items", "heavy_hitters", "sketch_info", "estimated_count"]:
            return True
        
        # Item exists if estimated count > 0
        return self.estimate_count(item) > 0
    
    def remove(self, key: Any) -> bool:
        """Remove item (limited support - decrements count)."""
        item = str(key)
        
        if item in self._values:
            # Decrement count in sketch
            for i in range(self.depth):
                bucket = self._hash_item(item, self._hash_seeds[i])
                if self._sketch[i][bucket] > 0:
                    self._sketch[i][bucket] -= 1
            
            self._total_count = max(0, self._total_count - 1)
            
            # Remove from values if count becomes 0
            if self.estimate_count(item) == 0:
                del self._values[item]
                self._unique_items.discard(item)
                self._size -= 1
                self._heavy_hitters.pop(item, None)
            
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove item (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._sketch = [[0 for _ in range(self.width)] for _ in range(self.depth)]
        self._values.clear()
        self._unique_items.clear()
        self._heavy_hitters.clear()
        self._total_count = 0
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all tracked items."""
        for item in self._unique_items:
            yield item
        yield "total_count"
        yield "unique_items"
        yield "heavy_hitters"
        yield "sketch_info"
        yield "estimated_count"
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        for item in self._unique_items:
            yield self.estimate_count(item)
        yield self._total_count
        yield len(self._unique_items)
        yield dict(self._heavy_hitters)
        yield self.get("sketch_info")
        yield self.get("estimated_count")
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all item-count pairs."""
        for item in self._unique_items:
            yield (item, self.estimate_count(item))
        yield ("total_count", self._total_count)
        yield ("unique_items", len(self._unique_items))
        yield ("heavy_hitters", dict(self._heavy_hitters))
        yield ("sketch_info", self.get("sketch_info"))
        yield ("estimated_count", self.get("estimated_count"))
    
    def __len__(self) -> int:
        """Get number of unique items tracked."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        result = {}
        for item in self._unique_items:
            result[item] = self.estimate_count(item)
        
        result.update({
            "total_count": self._total_count,
            "unique_items": len(self._unique_items),
            "heavy_hitters": dict(self._heavy_hitters),
            "sketch_info": self.get("sketch_info")
        })
        
        return result
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict with probabilistic semantics."""
        return True
    
    # ============================================================================
    # COUNT-MIN SKETCH SPECIFIC OPERATIONS
    # ============================================================================
    
    def estimate_count(self, item: str) -> int:
        """Estimate count of item."""
        if not item:
            return 0
        
        min_count = float('inf')
        
        for i in range(self.depth):
            bucket = self._hash_item(item, self._hash_seeds[i])
            count = self._sketch[i][bucket]
            min_count = min(min_count, count)
        
        return int(min_count) if min_count != float('inf') else 0
    
    def increment(self, item: str, count: int = 1) -> None:
        """Increment count for item."""
        self.put(item, count)
    
    def get_frequent_items(self, threshold: Optional[int] = None) -> List[Tuple[str, int]]:
        """Get items above frequency threshold."""
        if threshold is None:
            threshold = max(1, int(self._total_count * self.heavy_hitter_threshold))
        
        frequent = []
        for item in self._unique_items:
            count = self.estimate_count(item)
            if count >= threshold:
                frequent.append((item, count))
        
        # Sort by frequency (descending)
        frequent.sort(key=lambda x: x[1], reverse=True)
        return frequent
    
    def get_top_k(self, k: int) -> List[Tuple[str, int]]:
        """Get top-k most frequent items."""
        all_items = [(item, self.estimate_count(item)) for item in self._unique_items]
        all_items.sort(key=lambda x: x[1], reverse=True)
        return all_items[:k]
    
    def merge(self, other: 'xCountMinSketchStrategy') -> 'xCountMinSketchStrategy':
        """Merge with another Count-Min Sketch."""
        if (self.width != other.width or self.depth != other.depth or
            self._hash_seeds != other._hash_seeds):
            raise ValueError("Cannot merge sketches with different parameters")
        
        # Create new sketch
        merged = xCountMinSketchStrategy(
            traits=self._traits,
            epsilon=self.epsilon,
            delta=self.delta,
            track_heavy_hitters=self.track_heavy_hitters,
            heavy_hitter_threshold=self.heavy_hitter_threshold
        )
        
        # Merge sketch matrices
        for i in range(self.depth):
            for j in range(self.width):
                merged._sketch[i][j] = self._sketch[i][j] + other._sketch[i][j]
        
        # Merge metadata
        merged._total_count = self._total_count + other._total_count
        merged._unique_items = self._unique_items | other._unique_items
        merged._size = len(merged._unique_items)
        
        # Merge values (prefer this sketch's values)
        merged._values.update(other._values)
        merged._values.update(self._values)
        
        # Recompute heavy hitters
        for item in merged._unique_items:
            count = merged.estimate_count(item)
            merged._update_heavy_hitters(item, count)
        
        return merged
    
    def get_error_bounds(self, item: str) -> Tuple[int, int, float]:
        """Get error bounds for item count estimate."""
        estimate = self.estimate_count(item)
        
        # Error bound: estimate <= true_count <= estimate + epsilon * total_count
        max_error = int(self.epsilon * self._total_count)
        confidence = 1.0 - self.delta
        
        return estimate, estimate + max_error, confidence
    
    def point_query(self, item: str) -> Dict[str, Any]:
        """Comprehensive point query with error analysis."""
        estimate = self.estimate_count(item)
        lower_bound, upper_bound, confidence = self.get_error_bounds(item)
        
        return {
            'item': item,
            'estimated_count': estimate,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence': confidence,
            'relative_frequency': estimate / max(1, self._total_count),
            'is_heavy_hitter': item in self._heavy_hitters
        }
    
    def range_query(self, items: List[str]) -> int:
        """Estimate total count for a range of items."""
        # Simple sum - can lead to overestimation due to hash collisions
        return sum(self.estimate_count(item) for item in items)
    
    def get_sketch_statistics(self) -> Dict[str, Any]:
        """Get comprehensive sketch statistics."""
        # Calculate sketch density
        total_cells = self.width * self.depth
        non_zero_cells = sum(1 for i in range(self.depth) for j in range(self.width) 
                           if self._sketch[i][j] > 0)
        density = non_zero_cells / total_cells if total_cells > 0 else 0
        
        # Calculate hash distribution
        max_bucket_count = max(max(row) for row in self._sketch) if self._sketch else 0
        avg_bucket_count = self._total_count / total_cells if total_cells > 0 else 0
        
        return {
            'width': self.width,
            'depth': self.depth,
            'total_cells': total_cells,
            'non_zero_cells': non_zero_cells,
            'density': density,
            'total_count': self._total_count,
            'unique_items': len(self._unique_items),
            'heavy_hitters': len(self._heavy_hitters),
            'max_bucket_count': max_bucket_count,
            'avg_bucket_count': avg_bucket_count,
            'theoretical_error_bound': self.epsilon,
            'theoretical_confidence': 1.0 - self.delta,
            'memory_usage': total_cells * 4  # 4 bytes per int
        }
    
    def export_sketch(self) -> Dict[str, Any]:
        """Export sketch for analysis or persistence."""
        return {
            'sketch_matrix': [row.copy() for row in self._sketch],
            'parameters': {
                'width': self.width,
                'depth': self.depth,
                'epsilon': self.epsilon,
                'delta': self.delta,
                'hash_seeds': self._hash_seeds.copy()
            },
            'metadata': {
                'total_count': self._total_count,
                'unique_items': list(self._unique_items),
                'heavy_hitters': dict(self._heavy_hitters)
            }
        }
    
    def import_sketch(self, sketch_data: Dict[str, Any]) -> None:
        """Import sketch from exported data."""
        self._sketch = [row.copy() for row in sketch_data['sketch_matrix']]
        
        params = sketch_data['parameters']
        self.width = params['width']
        self.depth = params['depth']
        self.epsilon = params['epsilon']
        self.delta = params['delta']
        self._hash_seeds = params['hash_seeds'].copy()
        
        metadata = sketch_data['metadata']
        self._total_count = metadata['total_count']
        self._unique_items = set(metadata['unique_items'])
        self._heavy_hitters = metadata['heavy_hitters'].copy()
        self._size = len(self._unique_items)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'COUNT_MIN_SKETCH',
            'backend': 'Probabilistic frequency counter with hash matrix',
            'width': self.width,
            'depth': self.depth,
            'epsilon': self.epsilon,
            'delta': self.delta,
            'track_heavy_hitters': self.track_heavy_hitters,
            'complexity': {
                'update': 'O(d)',  # d = depth
                'query': 'O(d)',
                'space': 'O(w * d)',  # w = width, d = depth
                'merge': 'O(w * d)',
                'error_bound': f'ε * ||f||₁ with probability ≥ {1.0 - self.delta}'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_sketch_statistics()
        
        return {
            'total_count': stats['total_count'],
            'unique_items': stats['unique_items'],
            'sketch_density': f"{stats['density'] * 100:.1f}%",
            'heavy_hitters': stats['heavy_hitters'],
            'error_bound': f"{self.epsilon * 100:.2f}%",
            'confidence': f"{(1.0 - self.delta) * 100:.1f}%",
            'memory_usage': f"{stats['memory_usage']} bytes"
        }
