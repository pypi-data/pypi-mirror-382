"""
Balanced Ordered Map Node Strategy Implementation

This module implements the ORDERED_MAP_BALANCED strategy for self-balancing
ordered operations with guaranteed O(log n) performance.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class AVLNode:
    """Node in the AVL tree."""
    
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height = 1
        self.size = 1  # Size of subtree
    
    def update_stats(self) -> None:
        """Update height and size based on children."""
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        self.height = max(left_height, right_height) + 1
        
        left_size = self.left.size if self.left else 0
        right_size = self.right.size if self.right else 0
        self.size = left_size + right_size + 1
    
    def balance_factor(self) -> int:
        """Calculate balance factor."""
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        return left_height - right_height


class OrderedMapBalancedStrategy(ANodeTreeStrategy):
    """
    Balanced Ordered Map node strategy using AVL tree.
    
    Provides guaranteed O(log n) operations with automatic balancing
    for optimal performance in all scenarios.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Balanced Ordered Map strategy."""
        super().__init__(NodeMode.ORDERED_MAP_BALANCED, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.allow_duplicates = options.get('allow_duplicates', False)
        
        # Core AVL tree
        self._root: Optional[AVLNode] = None
        self._size = 0
        
        # Statistics
        self._rotations = 0
        self._max_height = 0
        self._rebalances = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the balanced ordered map strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Perform right rotation."""
        x = y.left
        T2 = x.right
        
        # Perform rotation
        x.right = y
        y.left = T2
        
        # Update heights and sizes
        y.update_stats()
        x.update_stats()
        
        self._rotations += 1
        return x
    
    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Perform left rotation."""
        y = x.right
        T2 = y.left
        
        # Perform rotation
        y.left = x
        x.right = T2
        
        # Update heights and sizes
        x.update_stats()
        y.update_stats()
        
        self._rotations += 1
        return y
    
    def _insert_node(self, node: Optional[AVLNode], key: str, value: Any) -> AVLNode:
        """Insert key-value pair into AVL tree."""
        normalized_key = self._normalize_key(key)
        
        # 1. Perform normal BST insertion
        if not node:
            self._size += 1
            return AVLNode(key, value)
        
        if normalized_key < self._normalize_key(node.key):
            node.left = self._insert_node(node.left, key, value)
        elif normalized_key > self._normalize_key(node.key):
            node.right = self._insert_node(node.right, key, value)
        else:
            # Key already exists
            if not self.allow_duplicates:
                node.value = value  # Update existing value
                return node
            else:
                # For duplicates, insert to right
                node.right = self._insert_node(node.right, key, value)
        
        # 2. Update height and size
        node.update_stats()
        self._max_height = max(self._max_height, node.height)
        
        # 3. Get balance factor
        balance = node.balance_factor()
        
        # 4. If unbalanced, perform rotations
        if balance > 1:
            # Left heavy
            if normalized_key < self._normalize_key(node.left.key):
                # Left-Left case
                self._rebalances += 1
                return self._rotate_right(node)
            else:
                # Left-Right case
                self._rebalances += 1
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        
        if balance < -1:
            # Right heavy
            if normalized_key > self._normalize_key(node.right.key):
                # Right-Right case
                self._rebalances += 1
                return self._rotate_left(node)
            else:
                # Right-Left case
                self._rebalances += 1
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
        
        return node
    
    def _find_node(self, node: Optional[AVLNode], key: str) -> Optional[AVLNode]:
        """Find node with given key."""
        if not node:
            return None
        
        normalized_key = self._normalize_key(key)
        node_key_norm = self._normalize_key(node.key)
        
        if normalized_key == node_key_norm:
            return node
        elif normalized_key < node_key_norm:
            return self._find_node(node.left, key)
        else:
            return self._find_node(node.right, key)
    
    def _find_min(self, node: AVLNode) -> AVLNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _delete_node(self, node: Optional[AVLNode], key: str) -> Optional[AVLNode]:
        """Delete node with given key."""
        if not node:
            return None
        
        normalized_key = self._normalize_key(key)
        node_key_norm = self._normalize_key(node.key)
        
        if normalized_key < node_key_norm:
            node.left = self._delete_node(node.left, key)
        elif normalized_key > node_key_norm:
            node.right = self._delete_node(node.right, key)
        else:
            # Node to be deleted found
            self._size -= 1
            
            if not node.left or not node.right:
                # Node with 0 or 1 child
                temp = node.left if node.left else node.right
                if not temp:
                    # No child case
                    return None
                else:
                    # One child case
                    return temp
            else:
                # Node with 2 children
                temp = self._find_min(node.right)
                node.key = temp.key
                node.value = temp.value
                node.right = self._delete_node(node.right, temp.key)
        
        # Update height and size
        node.update_stats()
        
        # Get balance factor
        balance = node.balance_factor()
        
        # Rebalance if needed
        if balance > 1:
            if node.left and node.left.balance_factor() >= 0:
                # Left-Left case
                self._rebalances += 1
                return self._rotate_right(node)
            else:
                # Left-Right case
                self._rebalances += 1
                if node.left:
                    node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        
        if balance < -1:
            if node.right and node.right.balance_factor() <= 0:
                # Right-Right case
                self._rebalances += 1
                return self._rotate_left(node)
            else:
                # Right-Left case
                self._rebalances += 1
                if node.right:
                    node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
        
        return node
    
    def _inorder_traversal(self, node: Optional[AVLNode], result: List[Tuple[str, Any]]) -> None:
        """Inorder traversal to collect key-value pairs."""
        if node:
            self._inorder_traversal(node.left, result)
            result.append((node.key, node.value))
            self._inorder_traversal(node.right, result)
    
    def _range_query(self, node: Optional[AVLNode], start: str, end: str, inclusive: bool, result: List[Tuple[str, Any]]) -> None:
        """Collect nodes in range."""
        if not node:
            return
        
        node_key_norm = self._normalize_key(node.key)
        start_norm = self._normalize_key(start)
        end_norm = self._normalize_key(end)
        
        # Check if we should go left
        if node_key_norm > start_norm or (inclusive and node_key_norm >= start_norm):
            self._range_query(node.left, start, end, inclusive, result)
        
        # Check if current node is in range
        if inclusive:
            if start_norm <= node_key_norm <= end_norm:
                result.append((node.key, node.value))
        else:
            if start_norm < node_key_norm < end_norm:
                result.append((node.key, node.value))
        
        # Check if we should go right
        if node_key_norm < end_norm or (inclusive and node_key_norm <= end_norm):
            self._range_query(node.right, start, end, inclusive, result)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add key-value pair to balanced tree."""
        key_str = str(key)
        self._root = self._insert_node(self._root, key_str, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "tree_info":
            return {
                'size': self._size,
                'height': self._root.height if self._root else 0,
                'max_height': self._max_height,
                'rotations': self._rotations,
                'rebalances': self._rebalances,
                'case_sensitive': self.case_sensitive,
                'balance_factor': self._root.balance_factor() if self._root else 0
            }
        elif key_str == "balance_stats":
            return self.get_balance_statistics()
        elif key_str.isdigit():
            # Access by index
            index = int(key_str)
            return self.get_at_index(index)
        
        node = self._find_node(self._root, key_str)
        return node.value if node else default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        
        if key_str in ["tree_info", "balance_stats"]:
            return True
        elif key_str.isdigit():
            index = int(key_str)
            return 0 <= index < self._size
        
        return self._find_node(self._root, key_str) is not None
    
    def remove(self, key: Any) -> bool:
        """Remove key from tree."""
        key_str = str(key)
        
        if key_str.isdigit():
            # Remove by index
            index = int(key_str)
            return self.remove_at_index(index)
        
        old_size = self._size
        self._root = self._delete_node(self._root, key_str)
        return self._size < old_size
    
    def delete(self, key: Any) -> bool:
        """Remove key from tree (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
        self._rotations = 0
        self._max_height = 0
        self._rebalances = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys in sorted order."""
        result = []
        self._inorder_traversal(self._root, result)
        for key, _ in result:
            yield key
    
    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        result = []
        self._inorder_traversal(self._root, result)
        for _, value in result:
            yield value
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        result = []
        self._inorder_traversal(self._root, result)
        for key, value in result:
            yield (key, value)
    
    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self.items())
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for indexed access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This is a dict-like structure."""
        return True
    
    # ============================================================================
    # BALANCED TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def first_key(self) -> Optional[str]:
        """Get first (smallest) key."""
        if not self._root:
            return None
        
        node = self._root
        while node.left:
            node = node.left
        return node.key
    
    def last_key(self) -> Optional[str]:
        """Get last (largest) key."""
        if not self._root:
            return None
        
        node = self._root
        while node.right:
            node = node.right
        return node.key
    
    def get_range(self, start_key: str, end_key: str, inclusive: bool = True) -> List[Tuple[str, Any]]:
        """Get key-value pairs in range with O(log n + k) complexity."""
        result = []
        self._range_query(self._root, start_key, end_key, inclusive, result)
        return result
    
    def get_at_index(self, index: int) -> Optional[Any]:
        """Get value at specific index with O(log n) complexity."""
        if index < 0 or index >= self._size:
            return None
        
        def _find_by_index(node: Optional[AVLNode], target_index: int) -> Optional[Any]:
            if not node:
                return None
            
            left_size = node.left.size if node.left else 0
            
            if target_index == left_size:
                return node.value
            elif target_index < left_size:
                return _find_by_index(node.left, target_index)
            else:
                return _find_by_index(node.right, target_index - left_size - 1)
        
        return _find_by_index(self._root, index)
    
    def index_of(self, key: str) -> int:
        """Get index of key with O(log n) complexity."""
        def _find_index(node: Optional[AVLNode], target_key: str, current_index: int = 0) -> int:
            if not node:
                return -1
            
            normalized_target = self._normalize_key(target_key)
            normalized_node = self._normalize_key(node.key)
            
            left_size = node.left.size if node.left else 0
            
            if normalized_target == normalized_node:
                return current_index + left_size
            elif normalized_target < normalized_node:
                return _find_index(node.left, target_key, current_index)
            else:
                return _find_index(node.right, target_key, current_index + left_size + 1)
        
        return _find_index(self._root, key)
    
    def remove_at_index(self, index: int) -> bool:
        """Remove element at specific index."""
        if index < 0 or index >= self._size:
            return False
        
        # Find key at index first
        def _key_at_index(node: Optional[AVLNode], target_index: int) -> Optional[str]:
            if not node:
                return None
            
            left_size = node.left.size if node.left else 0
            
            if target_index == left_size:
                return node.key
            elif target_index < left_size:
                return _key_at_index(node.left, target_index)
            else:
                return _key_at_index(node.right, target_index - left_size - 1)
        
        key = _key_at_index(self._root, index)
        if key:
            return self.remove(key)
        return False
    
    def get_balance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive balance statistics."""
        def _analyze_balance(node: Optional[AVLNode]) -> Dict[str, Any]:
            if not node:
                return {
                    'nodes': 0,
                    'height': 0,
                    'balance_factors': [],
                    'perfect_balance': True,
                    'max_imbalance': 0
                }
            
            left_stats = _analyze_balance(node.left)
            right_stats = _analyze_balance(node.right)
            
            balance_factor = node.balance_factor()
            balance_factors = left_stats['balance_factors'] + right_stats['balance_factors'] + [balance_factor]
            
            return {
                'nodes': 1 + left_stats['nodes'] + right_stats['nodes'],
                'height': node.height,
                'balance_factors': balance_factors,
                'perfect_balance': left_stats['perfect_balance'] and right_stats['perfect_balance'] and abs(balance_factor) <= 1,
                'max_imbalance': max(abs(balance_factor), left_stats['max_imbalance'], right_stats['max_imbalance'])
            }
        
        stats = _analyze_balance(self._root)
        
        # Calculate theoretical minimum height
        import math
        theoretical_min_height = math.ceil(math.log2(self._size + 1)) if self._size > 0 else 0
        
        return {
            'size': self._size,
            'height': stats['height'],
            'theoretical_min_height': theoretical_min_height,
            'height_efficiency': theoretical_min_height / max(1, stats['height']),
            'total_rotations': self._rotations,
            'total_rebalances': self._rebalances,
            'perfect_balance': stats['perfect_balance'],
            'max_imbalance': stats['max_imbalance'],
            'avg_balance_factor': sum(stats['balance_factors']) / max(1, len(stats['balance_factors'])),
            'is_balanced': stats['max_imbalance'] <= 1
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ORDERED_MAP_BALANCED',
            'backend': 'Self-balancing AVL tree',
            'case_sensitive': self.case_sensitive,
            'allow_duplicates': self.allow_duplicates,
            'complexity': {
                'insert': 'O(log n)',
                'search': 'O(log n)',
                'delete': 'O(log n)',
                'range_query': 'O(log n + k)',  # k = result size
                'index_access': 'O(log n)',
                'balance_operations': 'O(1) per rotation',
                'space': 'O(n)',
                'height_guarantee': 'O(log n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        balance_stats = self.get_balance_statistics()
        
        return {
            'size': balance_stats['size'],
            'height': balance_stats['height'],
            'height_efficiency': f"{balance_stats['height_efficiency'] * 100:.1f}%",
            'total_rotations': balance_stats['total_rotations'],
            'total_rebalances': balance_stats['total_rebalances'],
            'is_balanced': balance_stats['is_balanced'],
            'max_imbalance': balance_stats['max_imbalance'],
            'memory_usage': f"{balance_stats['size'] * 80} bytes (estimated)"
        }
