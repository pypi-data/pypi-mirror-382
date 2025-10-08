#exonware\xnode\strategies\impls\node_treap.py
"""
Treap Node Strategy Implementation

This module implements the TREAP strategy for randomized balanced trees
combining binary search tree and heap properties.
"""

import random
from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class TreapNode:
    """Node in the treap."""
    
    def __init__(self, key: str, value: Any = None, priority: int = None):
        self.key = key
        self.value = value
        self.priority = priority if priority is not None else random.randint(1, 1000000)
        self.left: Optional['TreapNode'] = None
        self.right: Optional['TreapNode'] = None
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value, self.priority))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, TreapNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.priority == other.priority)


class TreapStrategy(ANodeTreeStrategy):
    """
    Treap node strategy for randomized balanced trees.
    
    Combines binary search tree and heap properties with randomized
    priorities for self-balancing behavior.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the treap strategy."""
        super().__init__(NodeMode.TREAP, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.priority_range = options.get('priority_range', (1, 1000000))
        
        # Core treap
        self._root: Optional[TreapNode] = None
        self._size = 0
        
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_rotations = 0
        self._max_height = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the treap strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _get_height(self, node: Optional[TreapNode]) -> int:
        """Get height of node."""
        if not node:
            return 0
        
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)
    
    def _rotate_right(self, node: TreapNode) -> TreapNode:
        """Right rotation around node."""
        left_child = node.left
        if not left_child:
            return node
        
        # Perform rotation
        node.left = left_child.right
        left_child.right = node
        
        self._total_rotations += 1
        return left_child
    
    def _rotate_left(self, node: TreapNode) -> TreapNode:
        """Left rotation around node."""
        right_child = node.right
        if not right_child:
            return node
        
        # Perform rotation
        node.right = right_child.left
        right_child.left = node
        
        self._total_rotations += 1
        return right_child
    
    def _balance_treap(self, node: TreapNode) -> TreapNode:
        """Balance treap using heap property."""
        # Rotate right if left child has higher priority
        if node.left and node.left.priority > node.priority:
            return self._rotate_right(node)
        
        # Rotate left if right child has higher priority
        if node.right and node.right.priority > node.priority:
            return self._rotate_left(node)
        
        return node
    
    def _insert_node(self, node: Optional[TreapNode], key: str, value: Any, priority: int = None) -> Tuple[TreapNode, bool]:
        """Insert node with given key and value."""
        if not node:
            new_node = TreapNode(key, value, priority)
            return new_node, True
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            node.left, inserted = self._insert_node(node.left, key, value, priority)
        elif normalized_key > node_key:
            node.right, inserted = self._insert_node(node.right, key, value, priority)
        else:
            # Key already exists, update value
            node.value = value
            return node, False
        
        if not inserted:
            return node, False
        
        # Balance treap using heap property
        balanced_node = self._balance_treap(node)
        return balanced_node, True
    
    def _find_node(self, node: Optional[TreapNode], key: str) -> Optional[TreapNode]:
        """Find node with given key."""
        if not node:
            return None
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            return self._find_node(node.left, key)
        elif normalized_key > node_key:
            return self._find_node(node.right, key)
        else:
            return node
    
    def _find_min(self, node: TreapNode) -> TreapNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _find_max(self, node: TreapNode) -> TreapNode:
        """Find maximum node in subtree."""
        while node.right:
            node = node.right
        return node
    
    def _delete_node(self, node: Optional[TreapNode], key: str) -> Tuple[Optional[TreapNode], bool]:
        """Delete node with given key."""
        if not node:
            return None, False
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            node.left, deleted = self._delete_node(node.left, key)
        elif normalized_key > node_key:
            node.right, deleted = self._delete_node(node.right, key)
        else:
            # Found node to delete
            if not node.left:
                return node.right, True
            elif not node.right:
                return node.left, True
            else:
                # Node has both children, rotate to leaf
                if node.left.priority > node.right.priority:
                    node = self._rotate_right(node)
                    node.right, _ = self._delete_node(node.right, key)
                else:
                    node = self._rotate_left(node)
                    node.left, _ = self._delete_node(node.left, key)
                deleted = True
        
        if not deleted:
            return node, False
        
        return node, True
    
    def _inorder_traversal(self, node: Optional[TreapNode]) -> Iterator[Tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        # Generate random priority
        priority = random.randint(self.priority_range[0], self.priority_range[1])
        self._root, inserted = self._insert_node(self._root, key, value, priority)
        if inserted:
            self._size += 1
            self._total_insertions += 1
            self._max_height = max(self._max_height, self._get_height(self._root))
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
        node = self._find_node(self._root, key)
        return node.value if node else default
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        self._root, deleted = self._delete_node(self._root, key)
        if deleted:
            self._size -= 1
            self._total_deletions += 1
        return deleted
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._find_node(self._root, key) is not None
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self._root is None
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Iterate over keys in sorted order."""
        for key, _ in self._inorder_traversal(self._root):
            yield key
    
    def values(self) -> Iterator[Any]:
        """Iterate over values in key order."""
        for _, value in self._inorder_traversal(self._root):
            yield value
    
    def items(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over key-value pairs in sorted order."""
        yield from self._inorder_traversal(self._root)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        yield from self.keys()
    
    # ============================================================================
    # TREAP SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min(self) -> Optional[Tuple[str, Any]]:
        """Get the minimum key-value pair."""
        if not self._root:
            return None
        
        min_node = self._find_min(self._root)
        return (min_node.key, min_node.value)
    
    def get_max(self) -> Optional[Tuple[str, Any]]:
        """Get the maximum key-value pair."""
        if not self._root:
            return None
        
        max_node = self._find_max(self._root)
        return (max_node.key, max_node.value)
    
    def get_height(self) -> int:
        """Get the height of the tree."""
        return self._get_height(self._root)
    
    def get_priority(self, key: str) -> Optional[int]:
        """Get priority of node with given key."""
        node = self._find_node(self._root, key)
        return node.priority if node else None
    
    def set_priority(self, key: str, priority: int) -> bool:
        """Set priority of node with given key."""
        node = self._find_node(self._root, key)
        if not node:
            return False
        
        node.priority = priority
        # Rebalance if necessary
        self._root = self._balance_treap(self._root)
        return True
    
    def get_max_priority(self) -> Optional[Tuple[str, Any, int]]:
        """Get node with maximum priority."""
        if not self._root:
            return None
        
        def find_max_priority(node: TreapNode) -> TreapNode:
            max_node = node
            if node.left:
                left_max = find_max_priority(node.left)
                if left_max.priority > max_node.priority:
                    max_node = left_max
            if node.right:
                right_max = find_max_priority(node.right)
                if right_max.priority > max_node.priority:
                    max_node = right_max
            return max_node
        
        max_node = find_max_priority(self._root)
        return (max_node.key, max_node.value, max_node.priority)
    
    def is_treap_valid(self) -> bool:
        """Check if tree satisfies treap properties."""
        def check_treap(node: Optional[TreapNode]) -> bool:
            if not node:
                return True
            
            # Check heap property
            if node.left and node.left.priority > node.priority:
                return False
            if node.right and node.right.priority > node.priority:
                return False
            
            # Check BST property
            if node.left and self._normalize_key(node.left.key) >= self._normalize_key(node.key):
                return False
            if node.right and self._normalize_key(node.right.key) <= self._normalize_key(node.key):
                return False
            
            return check_treap(node.left) and check_treap(node.right)
        
        return check_treap(self._root)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_rotations': self._total_rotations,
            'priority_range': self.priority_range,
            'is_treap_valid': self.is_treap_valid(),
            'strategy': 'TREAP',
            'backend': 'Randomized treap with heap and BST properties',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
