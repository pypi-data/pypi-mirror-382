"""
Aho-Corasick Node Strategy Implementation

This module implements the AHO_CORASICK strategy for efficient multi-pattern
string matching using the Aho-Corasick automaton algorithm.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class ACNode:
    """Node in the Aho-Corasick trie."""
    
    def __init__(self):
        self.children: Dict[str, 'ACNode'] = {}
        self.failure: Optional['ACNode'] = None
        self.output: Set[str] = set()  # Patterns that end at this node
        self.pattern_indices: Set[int] = set()  # Indices of patterns
        self.depth = 0
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0


class AhoCorasickStrategy(ANodeTreeStrategy):
    """
    Aho-Corasick node strategy for multi-pattern string matching.
    
    Efficiently searches for multiple patterns simultaneously in a text
    using a finite automaton with failure links for linear-time matching.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Aho-Corasick strategy."""
        super().__init__(NodeMode.AHO_CORASICK, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.enable_overlapping = options.get('enable_overlapping', True)
        self.max_pattern_length = options.get('max_pattern_length', 1000)
        
        # Core automaton
        self._root = ACNode()
        self._patterns: List[str] = []
        self._pattern_to_index: Dict[str, int] = {}
        self._automaton_built = False
        
        # Key-value mapping for compatibility
        self._values: Dict[str, Any] = {}
        self._size = 0
        
        # Statistics
        self._total_nodes = 1  # Root node
        self._max_depth = 0
        self._search_cache: Dict[str, List[Tuple[str, int]]] = {}
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the Aho-Corasick strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.STREAMING)
    
    def _preprocess_pattern(self, pattern: str) -> str:
        """Preprocess pattern based on settings."""
        if not self.case_sensitive:
            pattern = pattern.lower()
        return pattern
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text based on settings."""
        if not self.case_sensitive:
            text = text.lower()
        return text
    
    def _add_pattern_to_trie(self, pattern: str, pattern_index: int) -> None:
        """Add pattern to the trie structure."""
        current = self._root
        depth = 0
        
        for char in pattern:
            if char not in current.children:
                current.children[char] = ACNode()
                current.children[char].depth = depth + 1
                self._total_nodes += 1
            
            current = current.children[char]
            depth += 1
        
        # Mark end of pattern
        current.output.add(pattern)
        current.pattern_indices.add(pattern_index)
        self._max_depth = max(self._max_depth, depth)
    
    def _build_failure_links(self) -> None:
        """Build failure links using BFS."""
        queue = deque()
        
        # Initialize failure links for root's children
        for child in self._root.children.values():
            child.failure = self._root
            queue.append(child)
        
        # Build failure links for all other nodes
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # Find the failure link
                failure_node = current.failure
                
                while failure_node is not None and char not in failure_node.children:
                    failure_node = failure_node.failure
                
                if failure_node is not None:
                    child.failure = failure_node.children[char]
                else:
                    child.failure = self._root
                
                # Add output from failure node
                if child.failure:
                    child.output.update(child.failure.output)
                    child.pattern_indices.update(child.failure.pattern_indices)
    
    def _build_automaton(self) -> None:
        """Build the complete Aho-Corasick automaton."""
        if self._automaton_built:
            return
        
        # Build failure links
        self._build_failure_links()
        self._automaton_built = True
        self._search_cache.clear()
    
    def _rebuild_automaton(self) -> None:
        """Rebuild the automaton from scratch."""
        # Reset automaton
        self._root = ACNode()
        self._total_nodes = 1
        self._max_depth = 0
        self._automaton_built = False
        self._search_cache.clear()
        
        # Rebuild trie
        for i, pattern in enumerate(self._patterns):
            self._add_pattern_to_trie(pattern, i)
        
        # Build failure links
        self._build_automaton()
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add pattern to automaton."""
        pattern = str(key)
        processed_pattern = self._preprocess_pattern(pattern)
        
        if len(processed_pattern) > self.max_pattern_length:
            raise ValueError(f"Pattern length {len(processed_pattern)} exceeds maximum {self.max_pattern_length}")
        
        if processed_pattern not in self._pattern_to_index:
            # Add new pattern
            pattern_index = len(self._patterns)
            self._patterns.append(processed_pattern)
            self._pattern_to_index[processed_pattern] = pattern_index
            
            # Add to trie
            self._add_pattern_to_trie(processed_pattern, pattern_index)
            self._automaton_built = False
            self._size += 1
        
        # Store value
        self._values[pattern] = value if value is not None else pattern
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "patterns":
            return self._patterns.copy()
        elif key_str == "automaton_info":
            return {
                'total_nodes': self._total_nodes,
                'max_depth': self._max_depth,
                'automaton_built': self._automaton_built,
                'pattern_count': len(self._patterns)
            }
        elif key_str in self._values:
            return self._values[key_str]
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        pattern = self._preprocess_pattern(key_str)
        return pattern in self._pattern_to_index or key_str in self._values
    
    def remove(self, key: Any) -> bool:
        """Remove pattern (requires automaton rebuild)."""
        pattern = str(key)
        processed_pattern = self._preprocess_pattern(pattern)
        
        if processed_pattern in self._pattern_to_index:
            # Remove pattern
            index = self._pattern_to_index[processed_pattern]
            del self._pattern_to_index[processed_pattern]
            self._patterns.pop(index)
            
            # Update indices
            for i, p in enumerate(self._patterns):
                self._pattern_to_index[p] = i
            
            # Remove value
            self._values.pop(pattern, None)
            self._size -= 1
            
            # Rebuild automaton
            self._rebuild_automaton()
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove pattern (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all patterns."""
        self._root = ACNode()
        self._patterns.clear()
        self._pattern_to_index.clear()
        self._values.clear()
        self._search_cache.clear()
        
        self._total_nodes = 1
        self._max_depth = 0
        self._automaton_built = False
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all pattern keys."""
        for pattern in self._patterns:
            yield pattern
        yield "patterns"
        yield "automaton_info"
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        for value in self._values.values():
            yield value
        yield self._patterns.copy()
        yield self.get("automaton_info")
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        for key, value in self._values.items():
            yield (key, value)
        yield ("patterns", self._patterns.copy())
        yield ("automaton_info", self.get("automaton_info"))
    
    def __len__(self) -> int:
        """Get number of patterns."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        result = dict(self._values)
        result["patterns"] = self._patterns.copy()
        result["automaton_info"] = self.get("automaton_info")
        return result
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for pattern access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict."""
        return True
    
    # ============================================================================
    # AHO-CORASICK SPECIFIC OPERATIONS
    # ============================================================================
    
    def add_pattern(self, pattern: str, metadata: Any = None) -> None:
        """Add pattern with optional metadata."""
        self.put(pattern, metadata)
    
    def search_text(self, text: str) -> List[Tuple[str, int, Any]]:
        """Search for all pattern matches in text."""
        if not text or not self._patterns:
            return []
        
        # Check cache
        cache_key = text[:100]  # Cache based on first 100 chars
        if cache_key in self._search_cache and len(text) <= 100:
            return self._search_cache[cache_key]
        
        processed_text = self._preprocess_text(text)
        self._build_automaton()
        
        matches = []
        current = self._root
        
        for i, char in enumerate(processed_text):
            # Follow failure links until we find a valid transition
            while current is not None and char not in current.children:
                current = current.failure
            
            if current is None:
                current = self._root
                continue
            
            current = current.children[char]
            
            # Report all patterns that end at this position
            for pattern in current.output:
                start_pos = i - len(pattern) + 1
                metadata = self._values.get(pattern, None)
                matches.append((pattern, start_pos, metadata))
        
        # Cache small results
        if len(text) <= 100:
            self._search_cache[cache_key] = matches
        
        return matches
    
    def find_all_matches(self, text: str) -> Dict[str, List[int]]:
        """Find all positions where each pattern matches."""
        matches = self.search_text(text)
        result = defaultdict(list)
        
        for pattern, position, _ in matches:
            result[pattern].append(position)
        
        # Convert to regular dict
        return dict(result)
    
    def count_matches(self, text: str) -> Dict[str, int]:
        """Count occurrences of each pattern."""
        matches = self.find_all_matches(text)
        return {pattern: len(positions) for pattern, positions in matches.items()}
    
    def has_any_match(self, text: str) -> bool:
        """Check if text contains any of the patterns."""
        if not text or not self._patterns:
            return False
        
        processed_text = self._preprocess_text(text)
        self._build_automaton()
        
        current = self._root
        
        for char in processed_text:
            while current is not None and char not in current.children:
                current = current.failure
            
            if current is None:
                current = self._root
                continue
            
            current = current.children[char]
            
            if current.output:
                return True
        
        return False
    
    def find_longest_match(self, text: str) -> Optional[Tuple[str, int, int]]:
        """Find the longest pattern match in text."""
        matches = self.search_text(text)
        
        if not matches:
            return None
        
        longest = max(matches, key=lambda x: len(x[0]))
        pattern, start_pos, _ = longest
        return pattern, start_pos, len(pattern)
    
    def replace_patterns(self, text: str, replacement_func: callable = None) -> str:
        """Replace all pattern matches in text."""
        if not replacement_func:
            replacement_func = lambda pattern, metadata: f"[{pattern}]"
        
        matches = self.search_text(text)
        
        if not matches:
            return text
        
        # Sort matches by position (descending) to avoid index shifts
        matches.sort(key=lambda x: x[1], reverse=True)
        
        result = text
        for pattern, start_pos, metadata in matches:
            end_pos = start_pos + len(pattern)
            replacement = replacement_func(pattern, metadata)
            result = result[:start_pos] + replacement + result[end_pos:]
        
        return result
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about patterns and automaton."""
        if not self._patterns:
            return {'pattern_count': 0, 'total_nodes': 1, 'avg_pattern_length': 0}
        
        pattern_lengths = [len(p) for p in self._patterns]
        unique_chars = set()
        for pattern in self._patterns:
            unique_chars.update(pattern)
        
        return {
            'pattern_count': len(self._patterns),
            'total_nodes': self._total_nodes,
            'max_depth': self._max_depth,
            'avg_pattern_length': sum(pattern_lengths) / len(pattern_lengths),
            'min_pattern_length': min(pattern_lengths),
            'max_pattern_length': max(pattern_lengths),
            'unique_characters': len(unique_chars),
            'alphabet_size': len(unique_chars),
            'automaton_built': self._automaton_built,
            'cache_size': len(self._search_cache)
        }
    
    def validate_automaton(self) -> bool:
        """Validate the automaton structure."""
        self._build_automaton()
        
        def _validate_node(node: ACNode, visited: Set[ACNode]) -> bool:
            if node in visited:
                return True
            
            visited.add(node)
            
            # Check failure link
            if node != self._root and node.failure is None:
                return False
            
            # Check children
            for child in node.children.values():
                if not _validate_node(child, visited):
                    return False
            
            return True
        
        return _validate_node(self._root, set())
    
    def export_automaton(self) -> Dict[str, Any]:
        """Export automaton structure for analysis."""
        self._build_automaton()
        
        def _export_node(node: ACNode, node_id: int) -> Dict[str, Any]:
            return {
                'id': node_id,
                'depth': node.depth,
                'children': list(node.children.keys()),
                'output': list(node.output),
                'has_failure': node.failure is not None
            }
        
        nodes = []
        node_queue = deque([(self._root, 0)])
        node_id = 0
        
        while node_queue:
            node, current_id = node_queue.popleft()
            nodes.append(_export_node(node, current_id))
            
            for child in node.children.values():
                node_id += 1
                node_queue.append((child, node_id))
        
        return {
            'nodes': nodes,
            'patterns': self._patterns.copy(),
            'statistics': self.get_pattern_statistics()
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'AHO_CORASICK',
            'backend': 'Finite automaton with failure links',
            'case_sensitive': self.case_sensitive,
            'enable_overlapping': self.enable_overlapping,
            'max_pattern_length': self.max_pattern_length,
            'complexity': {
                'construction': 'O(Σ|patterns|)',  # Σ = alphabet size
                'search': 'O(|text| + |matches|)',
                'space': 'O(Σ|patterns|)',
                'pattern_addition': 'O(|pattern|)',
                'pattern_removal': 'O(Σ|patterns|)'  # Requires rebuild
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_pattern_statistics()
        
        return {
            'patterns': stats['pattern_count'],
            'nodes': stats['total_nodes'],
            'max_depth': stats['max_depth'],
            'avg_pattern_length': f"{stats['avg_pattern_length']:.1f}",
            'alphabet_size': stats['alphabet_size'],
            'automaton_built': stats['automaton_built'],
            'cache_entries': stats['cache_size'],
            'memory_usage': f"{stats['total_nodes'] * 100 + len(self._patterns) * 50} bytes (estimated)"
        }
