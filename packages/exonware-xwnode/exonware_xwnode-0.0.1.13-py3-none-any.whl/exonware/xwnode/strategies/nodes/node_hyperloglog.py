"""
HyperLogLog Node Strategy Implementation

This module implements the HYPERLOGLOG strategy for probabilistic
cardinality estimation with logarithmic space complexity.
"""

from typing import Any, Iterator, List, Dict, Optional, Set
import hashlib
import math
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class xHyperLogLogStrategy(aNodeStrategy):
    """
    HyperLogLog node strategy for cardinality estimation.
    
    Provides memory-efficient approximate counting of distinct elements
    with configurable precision and excellent scalability.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the HyperLogLog strategy."""
        super().__init__(NodeMode.HYPERLOGLOG, traits, **options)
        
        # HyperLogLog parameters
        self.precision = options.get('precision', 12)  # b = 12 bits (4096 buckets)
        if not 4 <= self.precision <= 16:
            raise ValueError("Precision must be between 4 and 16")
        
        self.num_buckets = 2 ** self.precision
        self.alpha = self._calculate_alpha()
        
        # Core storage: buckets store maximum leading zeros + 1
        self._buckets: List[int] = [0] * self.num_buckets
        
        # Key-value mapping for compatibility
        self._values: Dict[str, Any] = {}
        self._items_added: Set[str] = set()
        self._size = 0
        
        # Performance tracking
        self._total_additions = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the HyperLogLog strategy."""
        return (NodeTrait.PROBABILISTIC | NodeTrait.COMPRESSED | NodeTrait.STREAMING)
    
    def _calculate_alpha(self) -> float:
        """Calculate alpha constant for bias correction."""
        m = self.num_buckets
        
        if m == 16:
            return 0.673
        elif m == 32:
            return 0.697
        elif m == 64:
            return 0.709
        else:
            return 0.7213 / (1.0 + 1.079 / m)
    
    def _hash_item(self, item: str) -> int:
        """Hash item to 32-bit integer."""
        hash_obj = hashlib.md5(item.encode())
        return int(hash_obj.hexdigest()[:8], 16)
    
    def _leading_zeros(self, num: int, max_bits: int = 32) -> int:
        """Count leading zeros in binary representation."""
        if num == 0:
            return max_bits
        
        zeros = 0
        mask = 1 << (max_bits - 1)
        
        while zeros < max_bits and (num & mask) == 0:
            zeros += 1
            mask >>= 1
        
        return zeros
    
    def _add_hash(self, hash_value: int) -> None:
        """Add hash value to HyperLogLog."""
        # Extract bucket index from first b bits
        bucket = hash_value & ((1 << self.precision) - 1)
        
        # Get remaining bits for leading zero count
        remaining = hash_value >> self.precision
        
        # Count leading zeros + 1
        leading_zeros = self._leading_zeros(remaining, 32 - self.precision) + 1
        
        # Update bucket with maximum value
        self._buckets[bucket] = max(self._buckets[bucket], leading_zeros)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add item to cardinality estimation."""
        item = str(key)
        
        # Add to HyperLogLog
        hash_value = self._hash_item(item)
        self._add_hash(hash_value)
        
        # Track for compatibility
        if item not in self._items_added:
            self._items_added.add(item)
            self._size += 1
        
        self._values[item] = value if value is not None else True
        self._total_additions += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value or cardinality estimate."""
        key_str = str(key)
        
        if key_str == "cardinality":
            return self.estimate_cardinality()
        elif key_str == "buckets":
            return self._buckets.copy()
        elif key_str == "statistics":
            return self.get_statistics()
        elif key_str == "raw_estimate":
            return self._raw_estimate()
        elif key_str in self._values:
            return self._values[key_str]
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if item might exist (probabilistic)."""
        key_str = str(key)
        
        if key_str in ["cardinality", "buckets", "statistics", "raw_estimate"]:
            return True
        
        return key_str in self._items_added
    
    def remove(self, key: Any) -> bool:
        """Remove item (not supported in HyperLogLog)."""
        # HyperLogLog doesn't support deletion
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove item (not supported in HyperLogLog)."""
        return False
    
    def clear(self) -> None:
        """Clear all data."""
        self._buckets = [0] * self.num_buckets
        self._values.clear()
        self._items_added.clear()
        self._size = 0
        self._total_additions = 0
    
    def keys(self) -> Iterator[str]:
        """Get all tracked items."""
        for item in self._items_added:
            yield item
        yield "cardinality"
        yield "buckets"
        yield "statistics"
        yield "raw_estimate"
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        for item in self._items_added:
            yield self._values.get(item, True)
        yield self.estimate_cardinality()
        yield self._buckets.copy()
        yield self.get_statistics()
        yield self._raw_estimate()
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all item-value pairs."""
        for item in self._items_added:
            yield (item, self._values.get(item, True))
        yield ("cardinality", self.estimate_cardinality())
        yield ("buckets", self._buckets.copy())
        yield ("statistics", self.get_statistics())
        yield ("raw_estimate", self._raw_estimate())
    
    def __len__(self) -> int:
        """Get number of unique items tracked."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        result = {}
        for item in self._items_added:
            result[item] = self._values.get(item, True)
        
        result.update({
            "cardinality": self.estimate_cardinality(),
            "buckets": self._buckets.copy(),
            "statistics": self.get_statistics(),
            "raw_estimate": self._raw_estimate()
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
    # HYPERLOGLOG SPECIFIC OPERATIONS
    # ============================================================================
    
    def add(self, item: str) -> None:
        """Add item to cardinality estimation."""
        self.put(item)
    
    def _raw_estimate(self) -> float:
        """Calculate raw cardinality estimate."""
        # Raw estimate: α_m * m² / Σ(2^(-M_j))
        sum_powers = sum(2.0 ** (-bucket) for bucket in self._buckets)
        return self.alpha * (self.num_buckets ** 2) / sum_powers
    
    def estimate_cardinality(self) -> int:
        """Estimate cardinality with bias correction."""
        raw_estimate = self._raw_estimate()
        
        # Apply bias correction for small/large values
        if raw_estimate <= 2.5 * self.num_buckets:
            # Small range correction
            zeros = self._buckets.count(0)
            if zeros != 0:
                return int(self.num_buckets * math.log(self.num_buckets / float(zeros)))
        
        if raw_estimate <= (1.0/30.0) * (2**32):
            # No correction needed
            return int(raw_estimate)
        else:
            # Large range correction
            return int(-1 * (2**32) * math.log(1 - raw_estimate / (2**32)))
    
    def merge(self, other: 'xHyperLogLogStrategy') -> 'xHyperLogLogStrategy':
        """Merge with another HyperLogLog."""
        if self.precision != other.precision:
            raise ValueError("Cannot merge HyperLogLogs with different precision")
        
        # Create new HyperLogLog
        merged = xHyperLogLogStrategy(
            traits=self._traits,
            precision=self.precision
        )
        
        # Merge buckets (take maximum)
        for i in range(self.num_buckets):
            merged._buckets[i] = max(self._buckets[i], other._buckets[i])
        
        # Merge tracked items
        merged._items_added = self._items_added | other._items_added
        merged._size = len(merged._items_added)
        merged._total_additions = self._total_additions + other._total_additions
        
        # Merge values
        merged._values.update(self._values)
        merged._values.update(other._values)
        
        return merged
    
    def union(self, other: 'xHyperLogLogStrategy') -> int:
        """Estimate cardinality of union with another HyperLogLog."""
        merged = self.merge(other)
        return merged.estimate_cardinality()
    
    def jaccard_similarity(self, other: 'xHyperLogLogStrategy') -> float:
        """Estimate Jaccard similarity with another HyperLogLog."""
        # |A ∩ B| / |A ∪ B| = (|A| + |B| - |A ∪ B|) / |A ∪ B|
        card_a = self.estimate_cardinality()
        card_b = other.estimate_cardinality()
        card_union = self.union(other)
        
        if card_union == 0:
            return 1.0 if card_a == 0 and card_b == 0 else 0.0
        
        card_intersection = card_a + card_b - card_union
        return max(0.0, card_intersection / card_union)
    
    def get_bucket_statistics(self) -> Dict[str, Any]:
        """Get statistics about bucket distribution."""
        non_zero = sum(1 for bucket in self._buckets if bucket > 0)
        max_bucket = max(self._buckets) if self._buckets else 0
        avg_bucket = sum(self._buckets) / len(self._buckets) if self._buckets else 0
        
        # Bucket value distribution
        bucket_dist = {}
        for value in self._buckets:
            bucket_dist[value] = bucket_dist.get(value, 0) + 1
        
        return {
            'total_buckets': self.num_buckets,
            'non_zero_buckets': non_zero,
            'zero_buckets': self.num_buckets - non_zero,
            'max_bucket_value': max_bucket,
            'avg_bucket_value': avg_bucket,
            'bucket_distribution': bucket_dist
        }
    
    def get_error_bounds(self) -> Dict[str, float]:
        """Get theoretical error bounds."""
        # Standard error: 1.04 / sqrt(m)
        standard_error = 1.04 / math.sqrt(self.num_buckets)
        
        estimate = self.estimate_cardinality()
        error_margin = estimate * standard_error
        
        return {
            'estimate': estimate,
            'standard_error': standard_error,
            'error_margin': error_margin,
            'lower_bound': max(0, estimate - 2 * error_margin),
            'upper_bound': estimate + 2 * error_margin,
            'confidence': 0.95  # 95% confidence interval
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive HyperLogLog statistics."""
        bucket_stats = self.get_bucket_statistics()
        error_bounds = self.get_error_bounds()
        
        return {
            'precision': self.precision,
            'num_buckets': self.num_buckets,
            'alpha': self.alpha,
            'estimated_cardinality': self.estimate_cardinality(),
            'raw_estimate': self._raw_estimate(),
            'items_tracked': self._size,
            'total_additions': self._total_additions,
            'bucket_stats': bucket_stats,
            'error_bounds': error_bounds,
            'memory_usage': self.num_buckets * 1  # 1 byte per bucket
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export HyperLogLog state."""
        return {
            'precision': self.precision,
            'buckets': self._buckets.copy(),
            'alpha': self.alpha,
            'num_buckets': self.num_buckets,
            'metadata': {
                'items_tracked': list(self._items_added),
                'total_additions': self._total_additions
            }
        }
    
    def import_state(self, state: Dict[str, Any]) -> None:
        """Import HyperLogLog state."""
        self.precision = state['precision']
        self.num_buckets = state['num_buckets']
        self.alpha = state['alpha']
        self._buckets = state['buckets'].copy()
        
        metadata = state['metadata']
        self._items_added = set(metadata['items_tracked'])
        self._total_additions = metadata['total_additions']
        self._size = len(self._items_added)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'HYPERLOGLOG',
            'backend': 'Probabilistic cardinality counter with bucket array',
            'precision': self.precision,
            'num_buckets': self.num_buckets,
            'alpha': self.alpha,
            'complexity': {
                'add': 'O(1)',
                'estimate': 'O(m)',  # m = num_buckets
                'merge': 'O(m)',
                'space': 'O(m)',
                'standard_error': f'1.04/√{self.num_buckets} ≈ {1.04/math.sqrt(self.num_buckets):.3f}'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        error_bounds = stats['error_bounds']
        
        return {
            'estimated_cardinality': stats['estimated_cardinality'],
            'items_tracked': stats['items_tracked'],
            'total_additions': stats['total_additions'],
            'precision_bits': self.precision,
            'standard_error': f"{error_bounds['standard_error']:.3f}",
            'error_margin': f"{error_bounds['error_margin']:.1f}",
            'memory_usage': f"{stats['memory_usage']} bytes"
        }
