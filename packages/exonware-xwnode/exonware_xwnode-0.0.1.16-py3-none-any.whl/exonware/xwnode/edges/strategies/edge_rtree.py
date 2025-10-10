"""
R-Tree Edge Strategy Implementation

This module implements the R_TREE strategy for spatial indexing of edges
with geometric coordinates and efficient spatial queries.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, NamedTuple
from collections import defaultdict
import math
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class Rectangle(NamedTuple):
    """Represents a bounding rectangle."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    
    def area(self) -> float:
        """Calculate rectangle area."""
        return max(0, self.max_x - self.min_x) * max(0, self.max_y - self.min_y)
    
    def perimeter(self) -> float:
        """Calculate rectangle perimeter."""
        return 2 * (max(0, self.max_x - self.min_x) + max(0, self.max_y - self.min_y))
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if rectangle contains point."""
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y
    
    def intersects(self, other: 'Rectangle') -> bool:
        """Check if rectangle intersects with another."""
        return not (other.max_x < self.min_x or other.min_x > self.max_x or
                   other.max_y < self.min_y or other.min_y > self.max_y)
    
    def contains_rectangle(self, other: 'Rectangle') -> bool:
        """Check if this rectangle contains another."""
        return (self.min_x <= other.min_x and self.max_x >= other.max_x and
                self.min_y <= other.min_y and self.max_y >= other.max_y)
    
    def union(self, other: 'Rectangle') -> 'Rectangle':
        """Get bounding rectangle of union."""
        return Rectangle(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y)
        )
    
    def enlargement_needed(self, other: 'Rectangle') -> float:
        """Calculate area enlargement needed to include another rectangle."""
        union_rect = self.union(other)
        return union_rect.area() - self.area()


class SpatialEdge:
    """Represents an edge with spatial coordinates."""
    
    def __init__(self, edge_id: str, source: str, target: str, 
                 source_coords: Tuple[float, float], 
                 target_coords: Tuple[float, float], **properties):
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.source_coords = source_coords
        self.target_coords = target_coords
        self.properties = properties.copy()
        
        # Calculate bounding rectangle
        self.bounding_rect = Rectangle(
            min(source_coords[0], target_coords[0]),
            min(source_coords[1], target_coords[1]),
            max(source_coords[0], target_coords[0]),
            max(source_coords[1], target_coords[1])
        )
        
        # Calculate edge length
        dx = target_coords[0] - source_coords[0]
        dy = target_coords[1] - source_coords[1]
        self.length = math.sqrt(dx * dx + dy * dy)
    
    def intersects_rectangle(self, rect: Rectangle) -> bool:
        """Check if edge intersects with rectangle."""
        # First check if bounding rectangles intersect
        if not self.bounding_rect.intersects(rect):
            return False
        
        # Check if either endpoint is inside rectangle
        if (rect.contains_point(*self.source_coords) or 
            rect.contains_point(*self.target_coords)):
            return True
        
        # Check line-rectangle intersection (simplified)
        return self._line_intersects_rectangle(rect)
    
    def _line_intersects_rectangle(self, rect: Rectangle) -> bool:
        """Check if line segment intersects rectangle edges."""
        x1, y1 = self.source_coords
        x2, y2 = self.target_coords
        
        # Check intersection with each rectangle edge
        edges = [
            ((rect.min_x, rect.min_y), (rect.max_x, rect.min_y)),  # Bottom
            ((rect.max_x, rect.min_y), (rect.max_x, rect.max_y)),  # Right
            ((rect.max_x, rect.max_y), (rect.min_x, rect.max_y)),  # Top
            ((rect.min_x, rect.max_y), (rect.min_x, rect.min_y))   # Left
        ]
        
        for (ex1, ey1), (ex2, ey2) in edges:
            if self._segments_intersect((x1, y1), (x2, y2), (ex1, ey1), (ex2, ey2)):
                return True
        
        return False
    
    def _segments_intersect(self, p1: Tuple[float, float], p2: Tuple[float, float],
                           p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
        """Check if two line segments intersect."""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def distance_to_point(self, x: float, y: float) -> float:
        """Calculate distance from point to edge."""
        x1, y1 = self.source_coords
        x2, y2 = self.target_coords
        
        # Vector from source to target
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            # Degenerate case: source and target are same point
            return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        
        # Parameter t for projection onto line
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        
        # Closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return math.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.edge_id,
            'source': self.source,
            'target': self.target,
            'source_coords': self.source_coords,
            'target_coords': self.target_coords,
            'length': self.length,
            'bounding_rect': {
                'min_x': self.bounding_rect.min_x,
                'min_y': self.bounding_rect.min_y,
                'max_x': self.bounding_rect.max_x,
                'max_y': self.bounding_rect.max_y
            },
            'properties': self.properties
        }


class RTreeNode:
    """Node in the R-Tree structure."""
    
    def __init__(self, is_leaf: bool = False, max_entries: int = 4):
        self.is_leaf = is_leaf
        self.max_entries = max_entries
        self.entries: List[Tuple[Rectangle, Any]] = []  # (bounding_rect, child_or_edge)
        self.bounding_rect: Optional[Rectangle] = None
    
    def is_full(self) -> bool:
        """Check if node is full."""
        return len(self.entries) >= self.max_entries
    
    def update_bounding_rect(self) -> None:
        """Update bounding rectangle to encompass all entries."""
        if not self.entries:
            self.bounding_rect = None
            return
        
        min_x = min(rect.min_x for rect, _ in self.entries)
        min_y = min(rect.min_y for rect, _ in self.entries)
        max_x = max(rect.max_x for rect, _ in self.entries)
        max_y = max(rect.max_y for rect, _ in self.entries)
        
        self.bounding_rect = Rectangle(min_x, min_y, max_x, max_y)
    
    def add_entry(self, rect: Rectangle, data: Any) -> None:
        """Add entry to node."""
        self.entries.append((rect, data))
        self.update_bounding_rect()


class xRTreeStrategy(aEdgeStrategy):
    """
    R-Tree edge strategy for spatial indexing of edges.
    
    Efficiently manages edges with spatial coordinates, supporting
    fast spatial queries like range searches, nearest neighbor,
    and geometric intersections.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the R-Tree strategy."""
        super().__init__(EdgeMode.R_TREE, traits, **options)
        
        self.max_entries = options.get('max_entries', 4)
        self.min_entries = max(1, self.max_entries // 2)
        self.is_directed = options.get('directed', True)
        
        # Core storage
        self._edges: Dict[str, SpatialEdge] = {}
        self._vertex_coords: Dict[str, Tuple[float, float]] = {}
        self._vertices: Set[str] = set()
        
        # R-Tree structure
        self._root: Optional[RTreeNode] = None
        self._edge_count = 0
        self._edge_id_counter = 0
        
        # Statistics
        self._tree_height = 0
        self._total_nodes = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the R-tree strategy."""
        return (EdgeTrait.SPATIAL | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.SPARSE)
    
    def _generate_edge_id(self) -> str:
        """Generate unique edge ID."""
        self._edge_id_counter += 1
        return f"spatial_edge_{self._edge_id_counter}"
    
    def _choose_leaf(self, rect: Rectangle) -> RTreeNode:
        """Choose leaf node for insertion using minimum enlargement heuristic."""
        if self._root is None:
            self._root = RTreeNode(is_leaf=True, max_entries=self.max_entries)
            return self._root
        
        current = self._root
        
        while not current.is_leaf:
            best_child = None
            best_enlargement = float('inf')
            best_area = float('inf')
            
            for child_rect, child_node in current.entries:
                enlargement = child_rect.enlargement_needed(rect)
                area = child_rect.area()
                
                if (enlargement < best_enlargement or 
                    (enlargement == best_enlargement and area < best_area)):
                    best_enlargement = enlargement
                    best_area = area
                    best_child = child_node
            
            current = best_child
        
        return current
    
    def _split_node(self, node: RTreeNode) -> Tuple[RTreeNode, RTreeNode]:
        """Split overfull node using quadratic split algorithm."""
        # Find two entries with maximum waste of space
        max_waste = -1
        seed1_idx = seed2_idx = 0
        
        for i in range(len(node.entries)):
            for j in range(i + 1, len(node.entries)):
                rect1, _ = node.entries[i]
                rect2, _ = node.entries[j]
                
                union_area = rect1.union(rect2).area()
                waste = union_area - rect1.area() - rect2.area()
                
                if waste > max_waste:
                    max_waste = waste
                    seed1_idx = i
                    seed2_idx = j
        
        # Create two new nodes
        node1 = RTreeNode(is_leaf=node.is_leaf, max_entries=self.max_entries)
        node2 = RTreeNode(is_leaf=node.is_leaf, max_entries=self.max_entries)
        
        # Add seeds
        node1.add_entry(*node.entries[seed1_idx])
        node2.add_entry(*node.entries[seed2_idx])
        
        # Distribute remaining entries
        remaining_entries = [node.entries[i] for i in range(len(node.entries)) 
                           if i != seed1_idx and i != seed2_idx]
        
        for rect, data in remaining_entries:
            enlargement1 = node1.bounding_rect.enlargement_needed(rect)
            enlargement2 = node2.bounding_rect.enlargement_needed(rect)
            
            if enlargement1 < enlargement2:
                node1.add_entry(rect, data)
            elif enlargement2 < enlargement1:
                node2.add_entry(rect, data)
            else:
                # Equal enlargement, choose smaller area
                if node1.bounding_rect.area() <= node2.bounding_rect.area():
                    node1.add_entry(rect, data)
                else:
                    node2.add_entry(rect, data)
        
        return node1, node2
    
    def _insert_with_split(self, edge: SpatialEdge) -> None:
        """Insert edge with node splitting if necessary."""
        leaf = self._choose_leaf(edge.bounding_rect)
        leaf.add_entry(edge.bounding_rect, edge)
        
        # Handle overflow
        if leaf.is_full() and len(leaf.entries) > self.max_entries:
            node1, node2 = self._split_node(leaf)
            
            if leaf == self._root:
                # Create new root
                new_root = RTreeNode(is_leaf=False, max_entries=self.max_entries)
                new_root.add_entry(node1.bounding_rect, node1)
                new_root.add_entry(node2.bounding_rect, node2)
                self._root = new_root
                self._tree_height += 1
            else:
                # Replace leaf with split nodes (simplified - full implementation would propagate splits)
                pass
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add spatial edge with coordinates."""
        # Extract coordinates from properties
        source_coords = properties.pop('source_coords', None)
        target_coords = properties.pop('target_coords', None)
        
        if source_coords is None and source in self._vertex_coords:
            source_coords = self._vertex_coords[source]
        if target_coords is None and target in self._vertex_coords:
            target_coords = self._vertex_coords[target]
        
        if source_coords is None or target_coords is None:
            raise ValueError("Both source_coords and target_coords must be provided")
        
        # Generate edge ID
        edge_id = properties.pop('edge_id', self._generate_edge_id())
        
        # Create spatial edge
        spatial_edge = SpatialEdge(edge_id, source, target, source_coords, target_coords, **properties)
        
        # Store edge and update vertices
        self._edges[edge_id] = spatial_edge
        self._vertex_coords[source] = source_coords
        self._vertex_coords[target] = target_coords
        self._vertices.add(source)
        self._vertices.add(target)
        
        # Insert into R-Tree
        self._insert_with_split(spatial_edge)
        self._edge_count += 1
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove spatial edge with proper R-Tree cleanup."""
        edge_to_remove = None
        edge_id_to_remove = None
        
        # Find the edge to remove
        if edge_id and edge_id in self._edges:
            edge = self._edges[edge_id]
            if edge.source == source and edge.target == target:
                edge_to_remove = edge
                edge_id_to_remove = edge_id
        else:
            # Find edge by endpoints
            for eid, edge in self._edges.items():
                if edge.source == source and edge.target == target:
                    edge_to_remove = edge
                    edge_id_to_remove = eid
                    break
        
        if edge_to_remove is None:
            return False
        
        # Remove from edge storage
        del self._edges[edge_id_to_remove]
        self._edge_count -= 1
        
        # Remove from R-Tree structure
        self._remove_from_rtree(edge_to_remove)
        
        return True
    
    def _remove_from_rtree(self, edge: SpatialEdge) -> bool:
        """Remove edge from R-Tree structure with proper cleanup."""
        if self._root is None:
            return False
        
        # Find the leaf node containing this edge
        leaf_node = self._find_leaf_containing_edge(self._root, edge)
        if leaf_node is None:
            return False
        
        # Remove edge from leaf node
        edge_removed = False
        for i, (rect, data) in enumerate(leaf_node.entries):
            if isinstance(data, SpatialEdge) and data.edge_id == edge.edge_id:
                leaf_node.entries.pop(i)
                edge_removed = True
                break
        
        if not edge_removed:
            return False
        
        # Update leaf node's bounding rectangle
        leaf_node.update_bounding_rect()
        
        # Handle underflow in leaf node
        if len(leaf_node.entries) < self.min_entries and leaf_node != self._root:
            self._handle_underflow(leaf_node)
        else:
            # Propagate bounding rectangle changes up the tree
            self._propagate_changes_up(leaf_node)
        
        # Rebuild tree if root becomes empty
        if self._root and len(self._root.entries) == 0:
            self._rebuild_tree()
        
        return True
    
    def _find_leaf_containing_edge(self, node: RTreeNode, edge: SpatialEdge) -> Optional[RTreeNode]:
        """Find the leaf node containing the specified edge."""
        if node.is_leaf:
            # Check if this leaf contains the edge
            for rect, data in node.entries:
                if isinstance(data, SpatialEdge) and data.edge_id == edge.edge_id:
                    return node
            return None
        
        # Search in child nodes
        for rect, child_node in node.entries:
            if rect.intersects(edge.bounding_rect):
                result = self._find_leaf_containing_edge(child_node, edge)
                if result is not None:
                    return result
        
        return None
    
    def _handle_underflow(self, node: RTreeNode) -> None:
        """Handle underflow in a node by redistributing or merging entries."""
        # Find sibling nodes
        parent = self._find_parent(self._root, node)
        if parent is None:
            return
        
        siblings = []
        for rect, child in parent.entries:
            if child != node:
                siblings.append(child)
        
        # Try to redistribute entries from siblings
        for sibling in siblings:
            if len(sibling.entries) > self.min_entries:
                # Redistribute one entry from sibling
                entry_to_move = sibling.entries.pop()
                node.entries.append(entry_to_move)
                
                # Update bounding rectangles
                node.update_bounding_rect()
                sibling.update_bounding_rect()
                self._propagate_changes_up(parent)
                return
        
        # If redistribution fails, merge with a sibling
        if siblings:
            sibling = siblings[0]
            # Move all entries from node to sibling
            sibling.entries.extend(node.entries)
            sibling.update_bounding_rect()
            
            # Remove node from parent
            for i, (rect, child) in enumerate(parent.entries):
                if child == node:
                    parent.entries.pop(i)
                    break
            
            parent.update_bounding_rect()
            self._propagate_changes_up(parent)
    
    def _find_parent(self, current: RTreeNode, target: RTreeNode) -> Optional[RTreeNode]:
        """Find the parent of a target node."""
        if current.is_leaf:
            return None
        
        for rect, child in current.entries:
            if child == target:
                return current
            
            result = self._find_parent(child, target)
            if result is not None:
                return result
        
        return None
    
    def _propagate_changes_up(self, node: RTreeNode) -> None:
        """Propagate bounding rectangle changes up the tree."""
        parent = self._find_parent(self._root, node)
        if parent is not None:
            parent.update_bounding_rect()
            self._propagate_changes_up(parent)
    
    def _rebuild_tree(self) -> None:
        """Rebuild the R-Tree from existing edges."""
        if not self._edges:
            self._root = None
            self._tree_height = 0
            self._total_nodes = 0
            return
        
        # Collect all edges
        edges = list(self._edges.values())
        
        # Clear current tree
        self._root = None
        self._tree_height = 0
        self._total_nodes = 0
        
        # Rebuild tree by re-inserting all edges
        for edge in edges:
            self._insert_edge_into_tree(edge)
    
    def _insert_edge_into_tree(self, edge: SpatialEdge) -> None:
        """Insert edge into R-Tree structure."""
        if self._root is None:
            self._root = RTreeNode(is_leaf=True, max_entries=self.max_entries)
            self._tree_height = 1
            self._total_nodes = 1
        
        # Choose leaf for insertion
        leaf = self._choose_leaf(edge.bounding_rect)
        
        # Add edge to leaf
        leaf.add_entry(edge.bounding_rect, edge)
        
        # Handle overflow
        if leaf.is_full():
            self._handle_overflow(leaf)
    
    def _handle_overflow(self, node: RTreeNode) -> None:
        """Handle overflow in a node by splitting."""
        if not node.is_full():
            return
        
        # Split the node
        node1, node2 = self._split_node(node)
        
        # If this is the root, create a new root
        if node == self._root:
            new_root = RTreeNode(is_leaf=False, max_entries=self.max_entries)
            new_root.add_entry(node1.bounding_rect, node1)
            new_root.add_entry(node2.bounding_rect, node2)
            self._root = new_root
            self._tree_height += 1
            self._total_nodes += 1
        else:
            # Replace the original node with the first split node
            parent = self._find_parent(self._root, node)
            if parent is not None:
                # Find and replace the original node
                for i, (rect, child) in enumerate(parent.entries):
                    if child == node:
                        parent.entries[i] = (node1.bounding_rect, node1)
                        break
                
                # Add the second split node to parent
                parent.add_entry(node2.bounding_rect, node2)
                parent.update_bounding_rect()
                
                # Handle overflow in parent if necessary
                if parent.is_full():
                    self._handle_overflow(parent)
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        for edge in self._edges.values():
            if edge.source == source and edge.target == target:
                return True
        return False
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        for edge in self._edges.values():
            if edge.source == source and edge.target == target:
                return edge.to_dict()
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of vertex."""
        neighbors = set()
        
        for edge in self._edges.values():
            if direction in ['out', 'both'] and edge.source == vertex:
                neighbors.add(edge.target)
            if direction in ['in', 'both'] and edge.target == vertex:
                neighbors.add(edge.source)
        
        return iter(neighbors)
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex."""
        return len(list(self.neighbors(vertex, direction)))
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for edge in self._edges.values():
            if data:
                yield (edge.source, edge.target, edge.to_dict())
            else:
                yield (edge.source, edge.target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all data."""
        self._edges.clear()
        self._vertex_coords.clear()
        self._vertices.clear()
        self._root = None
        self._edge_count = 0
        self._edge_id_counter = 0
        self._tree_height = 0
    
    def add_vertex(self, vertex: str, coords: Tuple[float, float] = None) -> None:
        """Add vertex with coordinates."""
        self._vertices.add(vertex)
        if coords:
            self._vertex_coords[vertex] = coords
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Remove all edges involving this vertex
        edges_to_remove = [eid for eid, edge in self._edges.items() 
                          if edge.source == vertex or edge.target == vertex]
        
        for edge_id in edges_to_remove:
            edge = self._edges[edge_id]
            self.remove_edge(edge.source, edge.target, edge_id)
        
        self._vertices.discard(vertex)
        self._vertex_coords.pop(vertex, None)
        
        return True
    
    # ============================================================================
    # SPATIAL QUERY OPERATIONS
    # ============================================================================
    
    def range_query(self, min_x: float, min_y: float, max_x: float, max_y: float) -> List[SpatialEdge]:
        """Find all edges intersecting with rectangle."""
        query_rect = Rectangle(min_x, min_y, max_x, max_y)
        result = []
        
        def search_node(node: RTreeNode):
            if node is None:
                return
            
            for rect, data in node.entries:
                if query_rect.intersects(rect):
                    if node.is_leaf:
                        # data is SpatialEdge
                        if data.intersects_rectangle(query_rect):
                            result.append(data)
                    else:
                        # data is child node
                        search_node(data)
        
        search_node(self._root)
        return result
    
    def point_query(self, x: float, y: float, radius: float = 0.0) -> List[SpatialEdge]:
        """Find edges near a point within radius."""
        if radius == 0.0:
            # Exact point query
            query_rect = Rectangle(x, y, x, y)
        else:
            # Range query with radius
            query_rect = Rectangle(x - radius, y - radius, x + radius, y + radius)
        
        candidates = self.range_query(query_rect.min_x, query_rect.min_y, 
                                    query_rect.max_x, query_rect.max_y)
        
        if radius == 0.0:
            return candidates
        
        # Filter by actual distance
        result = []
        for edge in candidates:
            if edge.distance_to_point(x, y) <= radius:
                result.append(edge)
        
        return result
    
    def nearest_neighbor(self, x: float, y: float, k: int = 1) -> List[Tuple[SpatialEdge, float]]:
        """Find k nearest edges to point."""
        # Simple implementation - can be optimized with priority queue
        distances = []
        
        for edge in self._edges.values():
            distance = edge.distance_to_point(x, y)
            distances.append((edge, distance))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]
    
    def edges_in_region(self, center_x: float, center_y: float, radius: float) -> List[SpatialEdge]:
        """Find all edges within circular region."""
        # Use square approximation for efficiency
        candidates = self.range_query(center_x - radius, center_y - radius,
                                    center_x + radius, center_y + radius)
        
        result = []
        for edge in candidates:
            # Check if any part of edge is within radius
            dist_to_source = math.sqrt((edge.source_coords[0] - center_x) ** 2 + 
                                     (edge.source_coords[1] - center_y) ** 2)
            dist_to_target = math.sqrt((edge.target_coords[0] - center_x) ** 2 + 
                                     (edge.target_coords[1] - center_y) ** 2)
            
            if dist_to_source <= radius or dist_to_target <= radius:
                result.append(edge)
            elif edge.distance_to_point(center_x, center_y) <= radius:
                result.append(edge)
        
        return result
    
    def get_bounding_box(self) -> Optional[Rectangle]:
        """Get bounding box of all edges."""
        if self._root and self._root.bounding_rect:
            return self._root.bounding_rect
        return None
    
    def spatial_statistics(self) -> Dict[str, Any]:
        """Get spatial statistics."""
        if not self._edges:
            return {'edges': 0, 'vertices': 0, 'total_length': 0, 'avg_length': 0}
        
        lengths = [edge.length for edge in self._edges.values()]
        bounding_box = self.get_bounding_box()
        
        return {
            'edges': len(self._edges),
            'vertices': len(self._vertices),
            'total_length': sum(lengths),
            'avg_length': sum(lengths) / len(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'bounding_box': bounding_box._asdict() if bounding_box else None,
            'tree_height': self._tree_height,
            'spatial_extent': {
                'width': bounding_box.max_x - bounding_box.min_x if bounding_box else 0,
                'height': bounding_box.max_y - bounding_box.min_y if bounding_box else 0
            }
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'R_TREE',
            'backend': 'R-Tree spatial index with quadratic split',
            'max_entries': self.max_entries,
            'min_entries': self.min_entries,
            'is_directed': self.is_directed,
            'complexity': {
                'insert': f'O(log_M n)',  # M = max_entries
                'delete': f'O(log_M n)',
                'range_query': f'O(log_M n + k)',  # k = result size
                'point_query': f'O(log_M n + k)',
                'space': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.spatial_statistics()
        
        return {
            'edges': self._edge_count,
            'vertices': len(self._vertices),
            'tree_height': self._tree_height,
            'avg_edge_length': f"{stats.get('avg_length', 0):.2f}",
            'spatial_extent': f"{stats.get('spatial_extent', {}).get('width', 0):.1f} x {stats.get('spatial_extent', {}).get('height', 0):.1f}",
            'memory_usage': f"{self._edge_count * 150 + len(self._vertices) * 50} bytes (estimated)"
        }
