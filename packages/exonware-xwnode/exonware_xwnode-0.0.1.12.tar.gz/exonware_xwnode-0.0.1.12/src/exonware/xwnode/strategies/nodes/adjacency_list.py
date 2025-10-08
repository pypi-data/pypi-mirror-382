"""
Adjacency List Strategy Implementation

Implements graph operations using adjacency list representation.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

from typing import Any, Iterator, List, Optional, Dict, Union, Set, Tuple
from collections import defaultdict
from .base import ANodeGraphStrategy
from ...types import NodeMode, NodeTrait


class AdjacencyListStrategy(ANodeGraphStrategy):
    """
    Adjacency List node strategy for graph operations.
    
    Uses adjacency list representation for efficient neighbor queries
    and edge operations in sparse graphs.
    """
    
    def __init__(self):
        """Initialize an empty adjacency list."""
        super().__init__()
        self._adj_list: Dict[str, List[Tuple[str, float]]] = defaultdict(list)  # node -> [(neighbor, weight)]
        self._nodes: Dict[str, Any] = {}  # node -> data
        self._mode = NodeMode.ADJACENCY_LIST
        self._traits = {NodeTrait.GRAPH, NodeTrait.SPARSE, NodeTrait.FAST_NEIGHBORS}
    
    def insert(self, key: str, value: Any) -> None:
        """Insert a node into the graph."""
        self._nodes[key] = value
        if key not in self._adj_list:
            self._adj_list[key] = []
    
    def find(self, key: str) -> Optional[Any]:
        """Find a node in the graph."""
        return self._nodes.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete a node and all its edges."""
        if key not in self._nodes:
            return False
        
        # Remove node
        del self._nodes[key]
        
        # Remove all edges to this node
        for node in self._adj_list:
            self._adj_list[node] = [(neighbor, weight) for neighbor, weight in self._adj_list[node] if neighbor != key]
        
        # Remove node's adjacency list
        if key in self._adj_list:
            del self._adj_list[key]
        
        return True
    
    def size(self) -> int:
        """Get the number of nodes in the graph."""
        return len(self._nodes)
    
    def to_native(self) -> Dict[str, Any]:
        """Convert graph to native dictionary format."""
        return {
            'nodes': self._nodes,
            'edges': {node: neighbors for node, neighbors in self._adj_list.items() if neighbors}
        }
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load graph from native dictionary format."""
        self._nodes = data.get('nodes', {})
        edges = data.get('edges', {})
        
        self._adj_list.clear()
        for node, neighbors in edges.items():
            self._adj_list[node] = neighbors
    
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0) -> None:
        """Add an edge between two nodes."""
        if from_node not in self._nodes:
            self._nodes[from_node] = None
        if to_node not in self._nodes:
            self._nodes[to_node] = None
        
        # Add edge (avoid duplicates)
        neighbors = self._adj_list[from_node]
        for i, (neighbor, _) in enumerate(neighbors):
            if neighbor == to_node:
                neighbors[i] = (to_node, weight)
                return
        
        neighbors.append((to_node, weight))
    
    def remove_edge(self, from_node: str, to_node: str) -> bool:
        """Remove an edge between two nodes."""
        if from_node not in self._adj_list:
            return False
        
        neighbors = self._adj_list[from_node]
        for i, (neighbor, _) in enumerate(neighbors):
            if neighbor == to_node:
                neighbors.pop(i)
                return True
        return False
    
    def has_edge(self, from_node: str, to_node: str) -> bool:
        """Check if an edge exists between two nodes."""
        if from_node not in self._adj_list:
            return False
        
        for neighbor, _ in self._adj_list[from_node]:
            if neighbor == to_node:
                return True
        return False
    
    def get_edge_weight(self, from_node: str, to_node: str) -> Optional[float]:
        """Get the weight of an edge between two nodes."""
        if from_node not in self._adj_list:
            return None
        
        for neighbor, weight in self._adj_list[from_node]:
            if neighbor == to_node:
                return weight
        return None
    
    def get_neighbors(self, node: str) -> List[str]:
        """Get all neighbors of a node."""
        if node not in self._adj_list:
            return []
        return [neighbor for neighbor, _ in self._adj_list[node]]
    
    def get_neighbors_with_weights(self, node: str) -> List[Tuple[str, float]]:
        """Get all neighbors with their edge weights."""
        if node not in self._adj_list:
            return []
        return self._adj_list[node].copy()
    
    def get_in_degree(self, node: str) -> int:
        """Get the in-degree of a node."""
        count = 0
        for neighbors in self._adj_list.values():
            for neighbor, _ in neighbors:
                if neighbor == node:
                    count += 1
        return count
    
    def get_out_degree(self, node: str) -> int:
        """Get the out-degree of a node."""
        if node not in self._adj_list:
            return 0
        return len(self._adj_list[node])
    
    def get_degree(self, node: str) -> int:
        """Get the total degree of a node (in + out)."""
        return self.get_in_degree(node) + self.get_out_degree(node)
    
    def is_connected(self, from_node: str, to_node: str) -> bool:
        """Check if two nodes are connected (BFS)."""
        if from_node not in self._nodes or to_node not in self._nodes:
            return False
        
        if from_node == to_node:
            return True
        
        visited = set()
        queue = [from_node]
        
        while queue:
            current = queue.pop(0)
            if current == to_node:
                return True
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor, _ in self._adj_list.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return False
    
    def get_connected_components(self) -> List[Set[str]]:
        """Get all connected components in the graph."""
        visited = set()
        components = []
        
        for node in self._nodes:
            if node not in visited:
                component = set()
                queue = [node]
                
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    component.add(current)
                    
                    # Add neighbors
                    for neighbor, _ in self._adj_list.get(current, []):
                        if neighbor not in visited:
                            queue.append(neighbor)
                
                if component:
                    components.append(component)
        
        return components
    
    def clear(self) -> None:
        """Clear all nodes and edges."""
        self._nodes.clear()
        self._adj_list.clear()
    
    def __iter__(self) -> Iterator[str]:
        """Iterate through all nodes."""
        for node in self._nodes:
            yield node
    
    def __repr__(self) -> str:
        """String representation of the adjacency list."""
        return f"AdjacencyListStrategy({len(self._nodes)} nodes, {sum(len(neighbors) for neighbors in self._adj_list.values())} edges)"
    
    # Required abstract methods from base classes
    def find_path(self, start: Any, end: Any) -> List[Any]:
        """Find path between nodes using BFS."""
        if start not in self._nodes or end not in self._nodes:
            return []
        
        if start == end:
            return [start]
        
        visited = set()
        queue = [(start, [start])]
        
        while queue:
            current, path = queue.pop(0)
            if current == end:
                return path
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor, _ in self._adj_list.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def as_union_find(self):
        """Provide Union-Find behavioral view."""
        return self
    
    def as_neural_graph(self):
        """Provide Neural Graph behavioral view."""
        return self
    
    def as_flow_network(self):
        """Provide Flow Network behavioral view."""
        return self
