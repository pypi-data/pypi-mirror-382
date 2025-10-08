"""
Dynamic Bitset Node Strategy Implementation

This module implements the BITSET_DYNAMIC strategy for dynamic bitset
operations with automatic resizing and bit manipulation capabilities.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple, Union
from .base import ANodeMatrixStrategy
from ...types import NodeMode, NodeTrait


class BitsetDynamicStrategy(ANodeMatrixStrategy):
    """
    Dynamic Bitset node strategy for bit manipulation operations.
    
    Provides efficient set operations, bit manipulation, and automatic
    resizing for large-scale boolean data processing.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Dynamic Bitset strategy."""
        super().__init__(NodeMode.BITSET_DYNAMIC, traits, **options)
        
        self.initial_capacity = options.get('initial_capacity', 64)
        self.growth_factor = options.get('growth_factor', 2.0)
        self.auto_trim = options.get('auto_trim', True)
        
        # Core dynamic bitset
        self._bits: List[int] = [0] * ((self.initial_capacity + 63) // 64)  # 64-bit chunks
        self._capacity = len(self._bits) * 64
        self._size = 0  # Number of set bits
        self._highest_bit = -1  # Highest set bit index
        
        # Statistics
        self._total_operations = 0
        self._resize_count = 0
        self._trim_count = 0
        self._bit_flips = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the dynamic bitset strategy."""
        return (NodeTrait.INDEXED | NodeTrait.COMPRESSED)
    
    def _ensure_capacity(self, bit_index: int) -> None:
        """Ensure bitset can accommodate the given bit index."""
        required_capacity = bit_index + 1
        
        if required_capacity > self._capacity:
            # Calculate new capacity
            new_capacity = self._capacity
            while new_capacity < required_capacity:
                new_capacity = int(new_capacity * self.growth_factor)
            
            # Extend bits array
            old_chunks = len(self._bits)
            new_chunks = (new_capacity + 63) // 64
            self._bits.extend([0] * (new_chunks - old_chunks))
            self._capacity = new_chunks * 64
            self._resize_count += 1
    
    def _trim_if_needed(self) -> None:
        """Trim unused capacity if auto_trim is enabled."""
        if not self.auto_trim or self._highest_bit == -1:
            return
        
        required_chunks = (self._highest_bit // 64) + 1
        current_chunks = len(self._bits)
        
        # Trim if we have more than 2x the required chunks
        if current_chunks > required_chunks * 2:
            self._bits = self._bits[:required_chunks]
            self._capacity = len(self._bits) * 64
            self._trim_count += 1
    
    def _update_highest_bit(self) -> None:
        """Update the highest set bit index."""
        self._highest_bit = -1
        for i in range(len(self._bits) - 1, -1, -1):
            if self._bits[i] != 0:
                # Find highest bit in this chunk
                chunk = self._bits[i]
                bit_pos = i * 64
                while chunk > 0:
                    if chunk & 1:
                        self._highest_bit = bit_pos
                    chunk >>= 1
                    bit_pos += 1
                break
    
    def _set_bit(self, bit_index: int, value: bool) -> bool:
        """Set bit at index to value. Returns True if bit changed."""
        self._ensure_capacity(bit_index)
        
        chunk_index = bit_index // 64
        bit_position = bit_index % 64
        mask = 1 << bit_position
        
        old_value = bool(self._bits[chunk_index] & mask)
        
        if value:
            if not old_value:
                self._bits[chunk_index] |= mask
                self._size += 1
                self._highest_bit = max(self._highest_bit, bit_index)
                self._bit_flips += 1
                return True
        else:
            if old_value:
                self._bits[chunk_index] &= ~mask
                self._size -= 1
                if bit_index == self._highest_bit:
                    self._update_highest_bit()
                self._bit_flips += 1
                return True
        
        return False
    
    def _get_bit(self, bit_index: int) -> bool:
        """Get bit value at index."""
        if bit_index < 0 or bit_index >= self._capacity:
            return False
        
        chunk_index = bit_index // 64
        if chunk_index >= len(self._bits):
            return False
        
        bit_position = bit_index % 64
        mask = 1 << bit_position
        return bool(self._bits[chunk_index] & mask)
    
    def _find_next_set_bit(self, start_index: int = 0) -> int:
        """Find next set bit starting from start_index."""
        for i in range(start_index, self._highest_bit + 1):
            if self._get_bit(i):
                return i
        return -1
    
    def _find_next_clear_bit(self, start_index: int = 0) -> int:
        """Find next clear bit starting from start_index."""
        i = start_index
        while i <= self._highest_bit + 64:  # Search a bit beyond current range
            if not self._get_bit(i):
                return i
            i += 1
        return i
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Set bit at key index."""
        self._total_operations += 1
        
        if isinstance(key, str) and key.isdigit():
            bit_index = int(key)
        elif isinstance(key, int):
            bit_index = key
        else:
            bit_index = hash(str(key)) % (2**20)  # Limit to reasonable range
        
        # Interpret value as boolean
        if value is None:
            bit_value = True  # Default to setting the bit
        elif isinstance(value, bool):
            bit_value = value
        elif isinstance(value, (int, float)):
            bit_value = bool(value)
        else:
            bit_value = bool(value)
        
        self._set_bit(abs(bit_index), bit_value)
        self._trim_if_needed()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get bit value at key index."""
        key_str = str(key)
        
        if key_str == "bitset_info":
            return {
                'size': self._size,
                'capacity': self._capacity,
                'highest_bit': self._highest_bit,
                'total_operations': self._total_operations,
                'resize_count': self._resize_count,
                'bit_flips': self._bit_flips,
                'utilization': self._size / max(1, self._capacity) * 100
            }
        elif key_str == "bit_count":
            return self._size
        elif key_str == "all_set_bits":
            return self.get_set_bits()
        elif key_str == "bit_pattern":
            return self.to_bit_string()
        
        if key_str.isdigit():
            bit_index = int(key_str)
            return self._get_bit(bit_index)
        elif isinstance(key, int):
            return self._get_bit(key)
        else:
            bit_index = hash(str(key)) % (2**20)
            return self._get_bit(abs(bit_index))
    
    def has(self, key: Any) -> bool:
        """Check if bit at key index is set."""
        key_str = str(key)
        
        if key_str in ["bitset_info", "bit_count", "all_set_bits", "bit_pattern"]:
            return True
        
        if key_str.isdigit():
            bit_index = int(key_str)
            return self._get_bit(bit_index)
        elif isinstance(key, int):
            return self._get_bit(key)
        else:
            bit_index = hash(str(key)) % (2**20)
            return self._get_bit(abs(bit_index))
    
    def remove(self, key: Any) -> bool:
        """Clear bit at key index."""
        if isinstance(key, str) and key.isdigit():
            bit_index = int(key)
        elif isinstance(key, int):
            bit_index = key
        else:
            bit_index = hash(str(key)) % (2**20)
        
        return self._set_bit(abs(bit_index), False)
    
    def delete(self, key: Any) -> bool:
        """Clear bit at key index (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all bits."""
        self._bits = [0] * ((self.initial_capacity + 63) // 64)
        self._capacity = len(self._bits) * 64
        self._size = 0
        self._highest_bit = -1
        self._total_operations = 0
        self._resize_count = 0
        self._trim_count = 0
        self._bit_flips = 0
    
    def keys(self) -> Iterator[str]:
        """Get all set bit indices as strings."""
        for i in range(self._highest_bit + 1):
            if self._get_bit(i):
                yield str(i)
    
    def values(self) -> Iterator[Any]:
        """Get all set bit values (always True)."""
        for i in range(self._highest_bit + 1):
            if self._get_bit(i):
                yield True
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all set bit indices and values."""
        for i in range(self._highest_bit + 1):
            if self._get_bit(i):
                yield (str(i), True)
    
    def __len__(self) -> int:
        """Get number of set bits."""
        return self._size
    
    def to_native(self) -> Dict[str, bool]:
        """Convert to native Python dict of set bits."""
        return {str(i): True for i in range(self._highest_bit + 1) if self._get_bit(i)}
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for indexed access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict."""
        return True
    
    # ============================================================================
    # BITSET SPECIFIC OPERATIONS
    # ============================================================================
    
    def set_bit(self, index: int, value: bool = True) -> None:
        """Set specific bit to value."""
        self._set_bit(abs(index), value)
        self._trim_if_needed()
    
    def clear_bit(self, index: int) -> None:
        """Clear specific bit."""
        self._set_bit(abs(index), False)
        self._trim_if_needed()
    
    def flip_bit(self, index: int) -> None:
        """Flip specific bit."""
        current_value = self._get_bit(abs(index))
        self._set_bit(abs(index), not current_value)
        self._trim_if_needed()
    
    def get_set_bits(self) -> List[int]:
        """Get list of all set bit indices."""
        result = []
        for i in range(self._highest_bit + 1):
            if self._get_bit(i):
                result.append(i)
        return result
    
    def get_clear_bits(self, max_index: Optional[int] = None) -> List[int]:
        """Get list of clear bit indices up to max_index."""
        if max_index is None:
            max_index = self._highest_bit + 10  # Some reasonable limit
        
        result = []
        for i in range(min(max_index + 1, self._capacity)):
            if not self._get_bit(i):
                result.append(i)
        return result
    
    def count_bits(self, start: int = 0, end: Optional[int] = None) -> int:
        """Count set bits in range [start, end)."""
        if end is None:
            end = self._highest_bit + 1
        
        count = 0
        for i in range(start, min(end, self._highest_bit + 1)):
            if self._get_bit(i):
                count += 1
        return count
    
    def find_first_set(self) -> int:
        """Find index of first set bit (-1 if none)."""
        return self._find_next_set_bit(0)
    
    def find_last_set(self) -> int:
        """Find index of last set bit (-1 if none)."""
        return self._highest_bit if self._size > 0 else -1
    
    def find_next_set(self, start: int) -> int:
        """Find next set bit after start index."""
        return self._find_next_set_bit(start + 1)
    
    def find_next_clear(self, start: int) -> int:
        """Find next clear bit after start index."""
        return self._find_next_clear_bit(start)
    
    def set_range(self, start: int, end: int, value: bool = True) -> None:
        """Set range of bits [start, end) to value."""
        for i in range(start, end):
            self._set_bit(i, value)
        self._trim_if_needed()
    
    def flip_range(self, start: int, end: int) -> None:
        """Flip range of bits [start, end)."""
        for i in range(start, end):
            current = self._get_bit(i)
            self._set_bit(i, not current)
        self._trim_if_needed()
    
    def logical_and(self, other: 'xBitsetDynamicStrategy') -> 'xBitsetDynamicStrategy':
        """Perform logical AND with another bitset."""
        result = xBitsetDynamicStrategy()
        max_index = max(self._highest_bit, other._highest_bit)
        
        for i in range(max_index + 1):
            if self._get_bit(i) and other._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def logical_or(self, other: 'xBitsetDynamicStrategy') -> 'xBitsetDynamicStrategy':
        """Perform logical OR with another bitset."""
        result = xBitsetDynamicStrategy()
        max_index = max(self._highest_bit, other._highest_bit)
        
        for i in range(max_index + 1):
            if self._get_bit(i) or other._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def logical_xor(self, other: 'xBitsetDynamicStrategy') -> 'xBitsetDynamicStrategy':
        """Perform logical XOR with another bitset."""
        result = xBitsetDynamicStrategy()
        max_index = max(self._highest_bit, other._highest_bit)
        
        for i in range(max_index + 1):
            if self._get_bit(i) != other._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def logical_not(self, max_index: Optional[int] = None) -> 'xBitsetDynamicStrategy':
        """Perform logical NOT (up to max_index)."""
        if max_index is None:
            max_index = self._highest_bit + 64  # Reasonable extension
        
        result = xBitsetDynamicStrategy()
        for i in range(max_index + 1):
            if not self._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def is_subset_of(self, other: 'xBitsetDynamicStrategy') -> bool:
        """Check if this bitset is a subset of another."""
        for i in range(self._highest_bit + 1):
            if self._get_bit(i) and not other._get_bit(i):
                return False
        return True
    
    def is_superset_of(self, other: 'xBitsetDynamicStrategy') -> bool:
        """Check if this bitset is a superset of another."""
        return other.is_subset_of(self)
    
    def intersects(self, other: 'xBitsetDynamicStrategy') -> bool:
        """Check if this bitset intersects with another."""
        max_index = min(self._highest_bit, other._highest_bit)
        for i in range(max_index + 1):
            if self._get_bit(i) and other._get_bit(i):
                return True
        return False
    
    def to_bit_string(self, max_length: int = 64) -> str:
        """Convert to binary string representation."""
        if self._highest_bit == -1:
            return "0"
        
        length = min(self._highest_bit + 1, max_length)
        bits = []
        for i in range(length - 1, -1, -1):  # MSB first
            bits.append('1' if self._get_bit(i) else '0')
        
        result = ''.join(bits)
        if length < self._highest_bit + 1:
            result = "..." + result  # Indicate truncation
        
        return result
    
    def from_bit_string(self, bit_string: str) -> None:
        """Load from binary string representation."""
        self.clear()
        
        # Remove any truncation indicator
        if bit_string.startswith("..."):
            bit_string = bit_string[3:]
        
        for i, bit_char in enumerate(reversed(bit_string)):
            if bit_char == '1':
                self._set_bit(i, True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bitset statistics."""
        chunks_used = (self._highest_bit // 64) + 1 if self._highest_bit >= 0 else 0
        
        return {
            'size': self._size,
            'capacity': self._capacity,
            'highest_bit': self._highest_bit,
            'chunks_allocated': len(self._bits),
            'chunks_used': chunks_used,
            'utilization': self._size / max(1, self._capacity) * 100,
            'density': self._size / max(1, self._highest_bit + 1) * 100 if self._highest_bit >= 0 else 0,
            'total_operations': self._total_operations,
            'resize_count': self._resize_count,
            'trim_count': self._trim_count,
            'bit_flips': self._bit_flips,
            'memory_efficiency': chunks_used / max(1, len(self._bits)) * 100
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'BITSET_DYNAMIC',
            'backend': 'Dynamic bitset with 64-bit chunks',
            'initial_capacity': self.initial_capacity,
            'growth_factor': self.growth_factor,
            'auto_trim': self.auto_trim,
            'complexity': {
                'set_bit': 'O(1) amortized',
                'get_bit': 'O(1)',
                'clear_bit': 'O(1)',
                'flip_bit': 'O(1)',
                'find_next': 'O(n)',  # n = bit range
                'logical_ops': 'O(max(m,n))',  # m,n = highest bits
                'space': 'O(capacity/64)',
                'resize': 'O(old_capacity) when triggered'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        
        return {
            'size': stats['size'],
            'capacity': stats['capacity'],
            'highest_bit': stats['highest_bit'],
            'utilization': f"{stats['utilization']:.1f}%",
            'density': f"{stats['density']:.1f}%",
            'total_operations': stats['total_operations'],
            'bit_flips': stats['bit_flips'],
            'memory_usage': f"{len(self._bits) * 8} bytes"
        }
