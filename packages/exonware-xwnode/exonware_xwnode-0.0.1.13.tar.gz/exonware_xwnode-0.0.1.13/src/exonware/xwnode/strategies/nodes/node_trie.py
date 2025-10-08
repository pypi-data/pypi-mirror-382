"""
Trie Node Strategy Implementation

This module implements the TRIE strategy for efficient string prefix operations.
"""

from typing import Any, Iterator, Dict, List, Optional
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait
from ..utils import (
    TrieNode,
    safe_to_native_conversion,
    create_basic_metrics,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class TrieStrategy(ANodeTreeStrategy):
    """
    Trie node strategy for efficient string prefix operations.
    
    Optimized for prefix matching, autocomplete, and string searching.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the trie strategy."""
        super().__init__(NodeMode.TRIE, traits, **options)
        self._root = TrieNode()
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the trie strategy."""
        return (NodeTrait.ORDERED | NodeTrait.HIERARCHICAL | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair (key should be string-like)."""
        word = str(key)
        node = self._root
        
        # Traverse/create path
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Mark end and store value
        if not node.is_end_word:
            update_size_tracker(self._size_tracker, 1)
        node.is_end_word = True
        node.value = value
        record_access(self._access_tracker, 'put_count')
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        word = str(key)
        node = self._find_node(word)
        record_access(self._access_tracker, 'get_count')
        if node and node.is_end_word:
            return node.value
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        word = str(key)
        node = self._find_node(word)
        return node is not None and node.is_end_word
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair."""
        word = str(key)
        result = self._remove_recursive(self._root, word, 0)
        if result:
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
        return result
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = TrieNode()
        self._size_tracker['size'] = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        return iter(self._collect_words())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        words = self._collect_words()
        for word in words:
            node = self._find_node(word)
            if node:
                yield node.value
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        words = self._collect_words()
        for word in words:
            node = self._find_node(word)
            if node:
                yield (word, node.value)
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self._size_tracker['size']
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        result = {}
        for word in self._collect_words():
            node = self._find_node(word)
            if node:
                result[word] = safe_to_native_conversion(node.value)
        return result
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict with string keys."""
        return True
    
    # ============================================================================
    # TRIE-SPECIFIC OPERATIONS
    # ============================================================================
    
    def starts_with(self, prefix: str) -> List[str]:
        """Get all keys that start with the given prefix."""
        node = self._find_node(prefix)
        if not node:
            return []
        
        words = []
        self._collect_words_from_node(node, prefix, words)
        return words
    
    def longest_common_prefix(self) -> str:
        """Find the longest common prefix of all stored keys."""
        if not self._root.children:
            return ""
        
        prefix = ""
        node = self._root
        
        while len(node.children) == 1 and not node.is_end_word:
            char = next(iter(node.children.keys()))
            prefix += char
            node = node.children[char]
        
        return prefix
    
    def get_all_prefixes(self, word: str) -> List[str]:
        """Get all prefixes of the given word that exist in the trie."""
        prefixes = []
        node = self._root
        
        for i, char in enumerate(word):
            if char not in node.children:
                break
            node = node.children[char]
            if node.is_end_word:
                prefixes.append(word[:i+1])
        
        return prefixes
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _find_node(self, word: str) -> Optional[TrieNode]:
        """Find the node corresponding to the given word."""
        node = self._root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def _remove_recursive(self, node: TrieNode, word: str, index: int) -> bool:
        """Recursively remove a word from the trie."""
        if index == len(word):
            if node.is_end_word:
                node.is_end_word = False
                node.value = None
                return True
            return False
        
        char = word[index]
        if char not in node.children:
            return False
        
        child = node.children[char]
        should_delete_child = self._remove_recursive(child, word, index + 1)
        
        if should_delete_child and not child.is_end_word and not child.children:
            del node.children[char]
        
        return should_delete_child
    
    def _collect_words(self) -> List[str]:
        """Collect all words stored in the trie."""
        words = []
        self._collect_words_from_node(self._root, "", words)
        return words
    
    def _collect_words_from_node(self, node: TrieNode, prefix: str, words: List[str]) -> None:
        """Collect all words from a given node."""
        if node.is_end_word:
            words.append(prefix)
        
        for char, child in node.children.items():
            self._collect_words_from_node(child, prefix + char, words)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return create_basic_backend_info(
            'TRIE',
            'TrieNode tree',
            complexity={
                'get': 'O(m) where m is key length',
                'put': 'O(m) where m is key length',
                'has': 'O(m) where m is key length',
                'starts_with': 'O(m + k) where m is prefix length, k is number of matches'
            }
        )
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        base_metrics = create_basic_metrics('TRIE', self._size_tracker['size'])
        access_metrics = get_access_metrics(self._access_tracker)
        base_metrics.update(access_metrics)
        return base_metrics
