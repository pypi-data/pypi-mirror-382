"""
PATRICIA Trie Node Strategy Implementation

This module implements the PATRICIA strategy (Practical Algorithm to
Retrieve Information Coded in Alphanumeric) for binary trie compression.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class PatriciaNode:
    """Node in the PATRICIA trie (compressed binary trie)."""
    
    def __init__(self, bit_position: int = -1, key: str = "", value: Any = None):
        self.bit_position = bit_position  # Which bit to test (-1 for leaves)
        self.key = key  # Full key (for leaves)
        self.value = value  # Value (for leaves)
        self.left: Optional['PatriciaNode'] = None   # 0 bit
        self.right: Optional['PatriciaNode'] = None  # 1 bit
        self.is_leaf = bit_position == -1
    
    def is_internal(self) -> bool:
        """Check if this is an internal node."""
        return not self.is_leaf


class PatriciaStrategy(ANodeTreeStrategy):
    """
    PATRICIA node strategy for compressed binary trie operations.
    
    Implements PATRICIA algorithm for efficient string storage and
    retrieval using compressed binary trie structure.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the PATRICIA strategy."""
        super().__init__(NodeMode.PATRICIA, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.use_bit_strings = options.get('use_bit_strings', False)  # Convert to binary
        
        # Core PATRICIA trie
        self._root: Optional[PatriciaNode] = None
        self._size = 0
        
        # Statistics
        self._total_nodes = 0
        self._max_depth = 0
        self._total_bits_saved = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the PATRICIA strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.COMPRESSED | NodeTrait.HIERARCHICAL)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _string_to_bits(self, s: str) -> str:
        """Convert string to binary representation."""
        if self.use_bit_strings:
            return s  # Assume it's already binary
        
        # Convert each character to 8-bit binary
        bits = ""
        for char in s:
            bits += format(ord(char), '08b')
        return bits
    
    def _get_bit(self, bit_string: str, position: int) -> int:
        """Get bit at position (0 or 1), returns 0 if position >= length."""
        if position >= len(bit_string):
            return 0
        return int(bit_string[position])
    
    def _find_first_differing_bit(self, key1: str, key2: str) -> int:
        """Find first bit position where two keys differ."""
        bits1 = self._string_to_bits(key1)
        bits2 = self._string_to_bits(key2)
        
        max_len = max(len(bits1), len(bits2))
        
        for i in range(max_len):
            bit1 = self._get_bit(bits1, i)
            bit2 = self._get_bit(bits2, i)
            if bit1 != bit2:
                return i
        
        return max_len  # Keys are identical up to the shorter length
    
    def _search_node(self, key: str) -> Optional[PatriciaNode]:
        """Search for node containing key."""
        if not self._root:
            return None
        
        normalized_key = self._normalize_key(key)
        bits = self._string_to_bits(normalized_key)
        current = self._root
        
        # Traverse down the trie
        while current and current.is_internal():
            bit = self._get_bit(bits, current.bit_position)
            if bit == 0:
                current = current.left
            else:
                current = current.right
        
        # Check if we found the correct key
        if current and current.key == normalized_key:
            return current
        
        return None
    
    def _insert_node(self, key: str, value: Any) -> None:
        """Insert key-value pair into PATRICIA trie."""
        normalized_key = self._normalize_key(key)
        
        if not self._root:
            # First insertion
            self._root = PatriciaNode(-1, normalized_key, value)
            self._size += 1
            self._total_nodes += 1
            return
        
        # Find where the new key should go
        bits = self._string_to_bits(normalized_key)
        current = self._root
        parent = None
        came_from_left = False
        
        # Traverse to find insertion point
        while current and current.is_internal():
            parent = current
            bit = self._get_bit(bits, current.bit_position)
            if bit == 0:
                current = current.left
                came_from_left = True
            else:
                current = current.right
                came_from_left = False
        
        # If key already exists, update value
        if current and current.key == normalized_key:
            current.value = value
            return
        
        # Find first differing bit
        existing_key = current.key if current else ""
        diff_bit = self._find_first_differing_bit(normalized_key, existing_key)
        
        # Create new leaf
        new_leaf = PatriciaNode(-1, normalized_key, value)
        self._total_nodes += 1
        self._size += 1
        
        if not current:
            # Edge case: empty position
            if parent:
                if came_from_left:
                    parent.left = new_leaf
                else:
                    parent.right = new_leaf
            return
        
        # Create new internal node
        new_internal = PatriciaNode(diff_bit)
        self._total_nodes += 1
        
        # Determine which child goes where
        new_bit = self._get_bit(bits, diff_bit)
        existing_bit = self._get_bit(self._string_to_bits(existing_key), diff_bit)
        
        if new_bit == 0:
            new_internal.left = new_leaf
            new_internal.right = current
        else:
            new_internal.left = current
            new_internal.right = new_leaf
        
        # Insert new internal node into tree
        if parent:
            if came_from_left:
                parent.left = new_internal
            else:
                parent.right = new_internal
        else:
            # New root
            self._root = new_internal
        
        # Update statistics
        self._total_bits_saved += 1  # Compression achieved
    
    def _collect_all_pairs(self, node: Optional[PatriciaNode]) -> List[Tuple[str, Any]]:
        """Collect all key-value pairs from subtree."""
        if not node:
            return []
        
        if node.is_leaf:
            return [(node.key, node.value)]
        
        result = []
        result.extend(self._collect_all_pairs(node.left))
        result.extend(self._collect_all_pairs(node.right))
        return result
    
    def _collect_with_prefix(self, node: Optional[PatriciaNode], prefix: str) -> List[Tuple[str, Any]]:
        """Collect all keys with given prefix."""
        if not node:
            return []
        
        if node.is_leaf:
            if node.key.startswith(prefix):
                return [(node.key, node.value)]
            return []
        
        # For internal nodes, we need to check both subtrees
        result = []
        result.extend(self._collect_with_prefix(node.left, prefix))
        result.extend(self._collect_with_prefix(node.right, prefix))
        return result
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add key-value pair to PATRICIA trie."""
        key_str = str(key)
        self._insert_node(key_str, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "trie_info":
            return {
                'size': self._size,
                'total_nodes': self._total_nodes,
                'max_depth': self._max_depth,
                'case_sensitive': self.case_sensitive,
                'use_bit_strings': self.use_bit_strings,
                'compression_ratio': self._total_bits_saved / max(1, self._total_nodes)
            }
        elif key_str == "all_keys":
            all_pairs = self._collect_all_pairs(self._root)
            return [key for key, _ in all_pairs]
        
        node = self._search_node(key_str)
        return node.value if node else default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        
        if key_str in ["trie_info", "all_keys"]:
            return True
        
        return self._search_node(key_str) is not None
    
    def remove(self, key: Any) -> bool:
        """Remove key from trie (simplified implementation)."""
        key_str = str(key)
        node = self._search_node(key_str)
        
        if node:
            # For simplicity, just mark as removed
            # Full implementation would require tree restructuring
            node.key = ""
            node.value = None
            self._size -= 1
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key from trie (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
        self._total_nodes = 0
        self._max_depth = 0
        self._total_bits_saved = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys in lexicographic order."""
        all_pairs = self._collect_all_pairs(self._root)
        valid_pairs = [(k, v) for k, v in all_pairs if k]  # Filter out removed keys
        for key, _ in sorted(valid_pairs):
            yield key
    
    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        all_pairs = self._collect_all_pairs(self._root)
        valid_pairs = [(k, v) for k, v in all_pairs if k]  # Filter out removed keys
        for _, value in sorted(valid_pairs):
            yield value
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        all_pairs = self._collect_all_pairs(self._root)
        valid_pairs = [(k, v) for k, v in all_pairs if k]  # Filter out removed keys
        for key, value in sorted(valid_pairs):
            yield (key, value)
    
    def __len__(self) -> int:
        """Get number of keys."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        all_pairs = self._collect_all_pairs(self._root)
        valid_pairs = [(k, v) for k, v in all_pairs if k]  # Filter out removed keys
        return dict(valid_pairs)
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict."""
        return True
    
    # ============================================================================
    # PATRICIA SPECIFIC OPERATIONS
    # ============================================================================
    
    def find_with_prefix(self, prefix: str) -> List[Tuple[str, Any]]:
        """Find all keys starting with given prefix."""
        normalized_prefix = self._normalize_key(prefix)
        return self._collect_with_prefix(self._root, normalized_prefix)
    
    def get_keys_with_prefix(self, prefix: str) -> List[str]:
        """Get keys starting with given prefix."""
        prefix_pairs = self.find_with_prefix(prefix)
        return [key for key, _ in prefix_pairs]
    
    def longest_common_prefix(self) -> str:
        """Find longest common prefix of all keys."""
        if self._size == 0:
            return ""
        
        all_keys = list(self.keys())
        if len(all_keys) == 1:
            return all_keys[0]
        
        # Find LCP using binary representation
        first_bits = self._string_to_bits(all_keys[0])
        lcp_bits = ""
        
        for i in range(len(first_bits)):
            bit = self._get_bit(first_bits, i)
            if all(self._get_bit(self._string_to_bits(key), i) == bit for key in all_keys):
                lcp_bits += str(bit)
            else:
                break
        
        # Convert back to string (simplified)
        if self.use_bit_strings:
            return lcp_bits
        
        # For character-based strings, find character boundaries
        char_boundary = len(lcp_bits) // 8 * 8
        if char_boundary > 0:
            char_bits = lcp_bits[:char_boundary]
            chars = ""
            for i in range(0, len(char_bits), 8):
                byte = char_bits[i:i+8]
                if len(byte) == 8:
                    chars += chr(int(byte, 2))
            return chars
        
        return ""
    
    def get_tree_depth(self) -> int:
        """Calculate maximum depth of the trie."""
        def _calculate_depth(node: Optional[PatriciaNode], depth: int = 0) -> int:
            if not node:
                return depth
            
            if node.is_leaf:
                return depth
            
            left_depth = _calculate_depth(node.left, depth + 1)
            right_depth = _calculate_depth(node.right, depth + 1)
            return max(left_depth, right_depth)
        
        return _calculate_depth(self._root)
    
    def get_compression_statistics(self) -> Dict[str, Any]:
        """Get detailed compression statistics."""
        def _analyze_tree(node: Optional[PatriciaNode]) -> Dict[str, int]:
            if not node:
                return {'internal_nodes': 0, 'leaf_nodes': 0, 'total_nodes': 0}
            
            if node.is_leaf:
                return {'internal_nodes': 0, 'leaf_nodes': 1, 'total_nodes': 1}
            
            left_stats = _analyze_tree(node.left)
            right_stats = _analyze_tree(node.right)
            
            return {
                'internal_nodes': 1 + left_stats['internal_nodes'] + right_stats['internal_nodes'],
                'leaf_nodes': left_stats['leaf_nodes'] + right_stats['leaf_nodes'],
                'total_nodes': 1 + left_stats['total_nodes'] + right_stats['total_nodes']
            }
        
        stats = _analyze_tree(self._root)
        
        # Calculate theoretical savings
        total_chars = sum(len(key) for key in self.keys())
        theoretical_bits = total_chars * 8  # Without compression
        
        return {
            'internal_nodes': stats['internal_nodes'],
            'leaf_nodes': stats['leaf_nodes'],
            'total_nodes': stats['total_nodes'],
            'theoretical_bits': theoretical_bits,
            'compression_achieved': self._total_bits_saved,
            'compression_ratio': self._total_bits_saved / max(1, theoretical_bits),
            'space_efficiency': stats['leaf_nodes'] / max(1, stats['total_nodes'])
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive PATRICIA statistics."""
        compression_stats = self.get_compression_statistics()
        
        return {
            'size': self._size,
            'total_nodes': self._total_nodes,
            'max_depth': self.get_tree_depth(),
            'case_sensitive': self.case_sensitive,
            'use_bit_strings': self.use_bit_strings,
            'compression_statistics': compression_stats,
            'compression_ratio': f"{compression_stats['compression_ratio']:.2%}",
            'space_efficiency': f"{compression_stats['space_efficiency']:.2%}"
        }
    
    def export_tree_structure(self) -> Dict[str, Any]:
        """Export tree structure for analysis."""
        def _export_node(node: Optional[PatriciaNode], node_id: int = 0) -> Tuple[Dict[str, Any], int]:
            if not node:
                return {}, node_id
            
            if node.is_leaf:
                return {
                    'id': node_id,
                    'type': 'leaf',
                    'key': node.key,
                    'value': str(node.value)
                }, node_id + 1
            
            left_data, next_id = _export_node(node.left, node_id + 1)
            right_data, final_id = _export_node(node.right, next_id)
            
            return {
                'id': node_id,
                'type': 'internal',
                'bit_position': node.bit_position,
                'left': left_data,
                'right': right_data
            }, final_id
        
        tree_data, _ = _export_node(self._root)
        return {
            'tree': tree_data,
            'statistics': self.get_statistics()
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'PATRICIA',
            'backend': 'Compressed binary trie (PATRICIA algorithm)',
            'case_sensitive': self.case_sensitive,
            'use_bit_strings': self.use_bit_strings,
            'complexity': {
                'insert': 'O(k)',  # k = key length in bits
                'search': 'O(k)',
                'delete': 'O(k)',
                'prefix_search': 'O(k + m)',  # m = number of matches
                'space': 'O(n)',  # n = number of internal nodes
                'compression': 'Binary path compression'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        comp_stats = stats['compression_statistics']
        
        return {
            'size': stats['size'],
            'total_nodes': stats['total_nodes'],
            'max_depth': stats['max_depth'],
            'compression_ratio': stats['compression_ratio'],
            'space_efficiency': stats['space_efficiency'],
            'internal_nodes': comp_stats['internal_nodes'],
            'memory_usage': f"{stats['total_nodes'] * 60} bytes (estimated)"
        }
