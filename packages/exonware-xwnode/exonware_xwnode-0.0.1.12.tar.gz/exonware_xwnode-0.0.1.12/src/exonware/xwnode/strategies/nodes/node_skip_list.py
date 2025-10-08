#exonware\xnode\strategies\impls\node_skip_list.py
"""
Skip List Node Strategy Implementation

This module implements the SKIP_LIST strategy for probabilistic data structures
with O(log n) expected performance for search, insertion, and deletion.
"""

import random
from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class SkipListNode:
    """Node in the skip list."""
    
    def __init__(self, key: str, value: Any = None, level: int = 0):
        self.key = key
        self.value = value
        self.level = level
        self.forward: List[Optional['SkipListNode']] = [None] * (level + 1)
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, SkipListNode):
            return False
        return self.key == other.key and self.value == other.value


class SkipListStrategy(ANodeTreeStrategy):
    """
    Skip list node strategy for probabilistic data structures.
    
    Provides O(log n) expected performance for search, insertion, and deletion
    with simple implementation and good concurrent access properties.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the skip list strategy."""
        super().__init__(NodeMode.SKIP_LIST, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.max_level = options.get('max_level', 16)  # Maximum level for skip list
        self.probability = options.get('probability', 0.5)  # Probability for level promotion
        
        # Core skip list
        self._header = SkipListNode("", None, self.max_level)  # Header node
        self._level = 0  # Current maximum level
        self._size = 0
        
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_searches = 0
        self._max_level_reached = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the skip list strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _random_level(self) -> int:
        """Generate random level for new node."""
        level = 0
        while random.random() < self.probability and level < self.max_level:
            level += 1
        self._max_level_reached = max(self._max_level_reached, level)
        return level
    
    def _search_path(self, key: str) -> List[Optional[SkipListNode]]:
        """Find the path to the node with given key."""
        normalized_key = self._normalize_key(key)
        current = self._header
        path = [None] * (self._level + 1)
        
        # Start from highest level and work down
        for i in range(self._level, -1, -1):
            while (current.forward[i] is not None and 
                   self._normalize_key(current.forward[i].key) < normalized_key):
                current = current.forward[i]
            path[i] = current
        
        return path
    
    def _find_node(self, key: str) -> Optional[SkipListNode]:
        """Find node with given key."""
        normalized_key = self._normalize_key(key)
        current = self._header
        
        # Start from highest level and work down
        for i in range(self._level, -1, -1):
            while (current.forward[i] is not None and 
                   self._normalize_key(current.forward[i].key) < normalized_key):
                current = current.forward[i]
        
        # Check if we found the exact key
        current = current.forward[0]
        if current is not None and self._normalize_key(current.key) == normalized_key:
            return current
        
        return None
    
    def _insert_node(self, key: str, value: Any) -> bool:
        """Insert node with given key and value."""
        normalized_key = self._normalize_key(key)
        
        # Find the path to insertion point
        path = self._search_path(key)
        current = path[0].forward[0]
        
        # Check if key already exists
        if current is not None and self._normalize_key(current.key) == normalized_key:
            # Update existing node
            current.value = value
            return False
        
        # Create new node
        new_level = self._random_level()
        new_node = SkipListNode(key, value, new_level)
        
        # If new level is higher than current level, update header
        if new_level > self._level:
            for i in range(self._level + 1, new_level + 1):
                path.append(self._header)
            self._level = new_level
        
        # Insert node into skip list
        for i in range(new_level + 1):
            new_node.forward[i] = path[i].forward[i]
            path[i].forward[i] = new_node
        
        self._size += 1
        self._total_insertions += 1
        return True
    
    def _delete_node(self, key: str) -> bool:
        """Delete node with given key."""
        normalized_key = self._normalize_key(key)
        
        # Find the path to deletion point
        path = self._search_path(key)
        current = path[0].forward[0]
        
        # Check if key exists
        if current is None or self._normalize_key(current.key) != normalized_key:
            return False
        
        # Remove node from skip list
        for i in range(self._level + 1):
            if path[i].forward[i] != current:
                break
            path[i].forward[i] = current.forward[i]
        
        # Update level if necessary
        while (self._level > 0 and 
               self._header.forward[self._level] is None):
            self._level -= 1
        
        self._size -= 1
        self._total_deletions += 1
        return True
    
    def _inorder_traversal(self) -> Iterator[Tuple[str, Any]]:
        """In-order traversal of skip list."""
        current = self._header.forward[0]
        while current is not None:
            yield (current.key, current.value)
            current = current.forward[0]
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        self._insert_node(key, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
        self._total_searches += 1
        node = self._find_node(key)
        return node.value if node else default
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._delete_node(key)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._find_node(key) is not None
    
    def clear(self) -> None:
        """Clear all data."""
        self._header = SkipListNode("", None, self.max_level)
        self._level = 0
        self._size = 0
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if skip list is empty."""
        return self._size == 0
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Iterate over keys in sorted order."""
        for key, _ in self._inorder_traversal():
            yield key
    
    def values(self) -> Iterator[Any]:
        """Iterate over values in key order."""
        for _, value in self._inorder_traversal():
            yield value
    
    def items(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over key-value pairs in sorted order."""
        yield from self._inorder_traversal()
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        yield from self.keys()
    
    # ============================================================================
    # SKIP LIST SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min(self) -> Optional[Tuple[str, Any]]:
        """Get the minimum key-value pair."""
        if self._size == 0:
            return None
        
        current = self._header.forward[0]
        return (current.key, current.value) if current else None
    
    def get_max(self) -> Optional[Tuple[str, Any]]:
        """Get the maximum key-value pair."""
        if self._size == 0:
            return None
        
        current = self._header
        for i in range(self._level, -1, -1):
            while current.forward[i] is not None:
                current = current.forward[i]
        
        return (current.key, current.value) if current != self._header else None
    
    def range_query(self, start_key: str, end_key: str) -> Iterator[Tuple[str, Any]]:
        """Get all key-value pairs in range [start_key, end_key]."""
        if not isinstance(start_key, str) or not isinstance(end_key, str):
            return
        
        normalized_start = self._normalize_key(start_key)
        normalized_end = self._normalize_key(end_key)
        
        # Find starting position
        path = self._search_path(start_key)
        current = path[0].forward[0]
        
        # Iterate through range
        while (current is not None and 
               self._normalize_key(current.key) <= normalized_end):
            if self._normalize_key(current.key) >= normalized_start:
                yield (current.key, current.value)
            current = current.forward[0]
    
    def get_level(self) -> int:
        """Get current maximum level."""
        return self._level
    
    def get_max_level(self) -> int:
        """Get maximum level reached."""
        return self._max_level_reached
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'level': self._level,
            'max_level_reached': self._max_level_reached,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_searches': self._total_searches,
            'probability': self.probability,
            'max_level': self.max_level,
            'strategy': 'SKIP_LIST',
            'backend': 'Probabilistic skip list with O(log n) expected performance',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
