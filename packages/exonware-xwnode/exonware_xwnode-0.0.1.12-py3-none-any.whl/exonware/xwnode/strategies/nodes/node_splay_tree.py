#exonware\xnode\strategies\impls\node_splay_tree.py
"""
Splay Tree Node Strategy Implementation

This module implements the SPLAY_TREE strategy for self-adjusting binary
search trees with amortized O(log n) performance.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class SplayTreeNode:
    """Node in the splay tree."""
    
    def __init__(self, key: str, value: Any = None):
        self.key = key
        self.value = value
        self.left: Optional['SplayTreeNode'] = None
        self.right: Optional['SplayTreeNode'] = None
        self.parent: Optional['SplayTreeNode'] = None
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, SplayTreeNode):
            return False
        return self.key == other.key and self.value == other.value


class SplayTreeStrategy(ANodeTreeStrategy):
    """
    Splay tree node strategy for self-adjusting binary search trees.
    
    Provides amortized O(log n) performance by moving accessed nodes
    to the root through splaying operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the splay tree strategy."""
        super().__init__(NodeMode.SPLAY_TREE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        
        # Core splay tree
        self._root: Optional[SplayTreeNode] = None
        self._size = 0
        
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_splays = 0
        self._max_height = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the splay tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _get_height(self, node: Optional[SplayTreeNode]) -> int:
        """Get height of node."""
        if not node:
            return 0
        
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)
    
    def _rotate_right(self, node: SplayTreeNode) -> None:
        """Right rotation around node."""
        left_child = node.left
        if not left_child:
            return
        
        # Update parent connections
        node.left = left_child.right
        if left_child.right:
            left_child.right.parent = node
        
        left_child.parent = node.parent
        if not node.parent:
            self._root = left_child
        elif node == node.parent.left:
            node.parent.left = left_child
        else:
            node.parent.right = left_child
        
        # Update rotation
        left_child.right = node
        node.parent = left_child
    
    def _rotate_left(self, node: SplayTreeNode) -> None:
        """Left rotation around node."""
        right_child = node.right
        if not right_child:
            return
        
        # Update parent connections
        node.right = right_child.left
        if right_child.left:
            right_child.left.parent = node
        
        right_child.parent = node.parent
        if not node.parent:
            self._root = right_child
        elif node == node.parent.right:
            node.parent.right = right_child
        else:
            node.parent.left = right_child
        
        # Update rotation
        right_child.left = node
        node.parent = right_child
    
    def _splay(self, node: SplayTreeNode) -> None:
        """Splay node to root."""
        while node.parent:
            parent = node.parent
            grandparent = parent.parent
            
            if not grandparent:
                # Zig case
                if node == parent.left:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)
            elif node == parent.left and parent == grandparent.left:
                # Zig-zig case (left-left)
                self._rotate_right(grandparent)
                self._rotate_right(parent)
            elif node == parent.right and parent == grandparent.right:
                # Zig-zig case (right-right)
                self._rotate_left(grandparent)
                self._rotate_left(parent)
            elif node == parent.right and parent == grandparent.left:
                # Zig-zag case (left-right)
                self._rotate_left(parent)
                self._rotate_right(grandparent)
            else:
                # Zig-zag case (right-left)
                self._rotate_right(parent)
                self._rotate_left(grandparent)
            
            self._total_splays += 1
    
    def _find_node(self, key: str) -> Optional[SplayTreeNode]:
        """Find node with given key and splay it to root."""
        normalized_key = self._normalize_key(key)
        current = self._root
        
        while current:
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                # Found the node, splay it to root
                self._splay(current)
                return current
        
        return None
    
    def _insert_node(self, key: str, value: Any) -> bool:
        """Insert node with given key and value."""
        normalized_key = self._normalize_key(key)
        
        # Create new node
        new_node = SplayTreeNode(key, value)
        
        # Find insertion point
        current = self._root
        parent = None
        
        while current:
            parent = current
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                # Key already exists, update value and splay
                current.value = value
                self._splay(current)
                return False
        
        # Insert new node
        new_node.parent = parent
        if not parent:
            self._root = new_node
        elif normalized_key < self._normalize_key(parent.key):
            parent.left = new_node
        else:
            parent.right = new_node
        
        # Splay new node to root
        self._splay(new_node)
        
        self._size += 1
        self._total_insertions += 1
        self._max_height = max(self._max_height, self._get_height(self._root))
        return True
    
    def _delete_node(self, key: str) -> bool:
        """Delete node with given key."""
        node = self._find_node(key)
        if not node:
            return False
        
        # Splay node to root
        self._splay(node)
        
        # If node has no children, just remove it
        if not node.left and not node.right:
            self._root = None
        elif not node.left:
            # Only right child
            self._root = node.right
            self._root.parent = None
        elif not node.right:
            # Only left child
            self._root = node.left
            self._root.parent = None
        else:
            # Both children exist
            # Find maximum in left subtree
            max_left = node.left
            while max_left.right:
                max_left = max_left.right
            
            # Splay max_left to root of left subtree
            self._splay(max_left)
            
            # Attach right subtree to max_left
            max_left.right = node.right
            if node.right:
                node.right.parent = max_left
            
            # Make max_left the new root
            self._root = max_left
            self._root.parent = None
        
        self._size -= 1
        self._total_deletions += 1
        return True
    
    def _inorder_traversal(self, node: Optional[SplayTreeNode]) -> Iterator[Tuple[str, Any]]:
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
        
        self._insert_node(key, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
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
    # SPLAY TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min(self) -> Optional[Tuple[str, Any]]:
        """Get the minimum key-value pair."""
        if not self._root:
            return None
        
        # Find minimum and splay it to root
        current = self._root
        while current.left:
            current = current.left
        
        self._splay(current)
        return (current.key, current.value)
    
    def get_max(self) -> Optional[Tuple[str, Any]]:
        """Get the maximum key-value pair."""
        if not self._root:
            return None
        
        # Find maximum and splay it to root
        current = self._root
        while current.right:
            current = current.right
        
        self._splay(current)
        return (current.key, current.value)
    
    def get_height(self) -> int:
        """Get the height of the tree."""
        return self._get_height(self._root)
    
    def splay_to_root(self, key: str) -> bool:
        """Splay node with given key to root."""
        node = self._find_node(key)
        return node is not None
    
    def get_root_key(self) -> Optional[str]:
        """Get the key of the root node."""
        return self._root.key if self._root else None
    
    def get_root_value(self) -> Optional[Any]:
        """Get the value of the root node."""
        return self._root.value if self._root else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_splays': self._total_splays,
            'root_key': self.get_root_key(),
            'strategy': 'SPLAY_TREE',
            'backend': 'Self-adjusting splay tree with amortized O(log n) performance',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
