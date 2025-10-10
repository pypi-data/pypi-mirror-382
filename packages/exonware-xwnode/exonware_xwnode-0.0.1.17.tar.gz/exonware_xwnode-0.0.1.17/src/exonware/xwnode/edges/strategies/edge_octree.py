"""
Octree Edge Strategy Implementation

This module implements the OCTREE strategy for 3D spatial
graph partitioning and efficient 3D spatial queries.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import defaultdict
import math
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class OctreeNode:
    """Node in the octree (3D spatial partitioning)."""
    
    def __init__(self, x: float, y: float, z: float, size: float, capacity: int = 8):
        self.x = x  # Center coordinates
        self.y = y
        self.z = z
        self.size = size  # Half-size of the cube
        self.capacity = capacity
        
        # Points stored in this node
        self.points: List[Tuple[float, float, float, str]] = []  # (x, y, z, vertex_id)
        
        # Child nodes (8 octants)
        self.children: List[Optional['OctreeNode']] = [None] * 8
        self.is_leaf = True
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """Check if point is within this node's bounds."""
        return (self.x - self.size <= x < self.x + self.size and
                self.y - self.size <= y < self.y + self.size and
                self.z - self.size <= z < self.z + self.size)
    
    def intersects_box(self, box_x: float, box_y: float, box_z: float, 
                      box_w: float, box_h: float, box_d: float) -> bool:
        """Check if this node intersects with given box."""
        return not (box_x >= self.x + self.size or
                   box_x + box_w <= self.x - self.size or
                   box_y >= self.y + self.size or
                   box_y + box_h <= self.y - self.size or
                   box_z >= self.z + self.size or
                   box_z + box_d <= self.z - self.size)
    
    def intersects_sphere(self, center_x: float, center_y: float, center_z: float, radius: float) -> bool:
        """Check if this node intersects with given sphere."""
        # Find closest point on cube to sphere center
        closest_x = max(self.x - self.size, min(center_x, self.x + self.size))
        closest_y = max(self.y - self.size, min(center_y, self.y + self.size))
        closest_z = max(self.z - self.size, min(center_z, self.z + self.size))
        
        # Calculate distance from sphere center to closest point
        dx = center_x - closest_x
        dy = center_y - closest_y
        dz = center_z - closest_z
        distance_sq = dx * dx + dy * dy + dz * dz
        
        return distance_sq <= radius * radius
    
    def subdivide(self) -> None:
        """Subdivide this node into eight children."""
        if not self.is_leaf:
            return
        
        half_size = self.size / 2
        quarter_size = half_size / 2
        
        # Create eight children (octants)
        octants = [
            (self.x - quarter_size, self.y - quarter_size, self.z - quarter_size),  # 0: ---
            (self.x + quarter_size, self.y - quarter_size, self.z - quarter_size),  # 1: +--
            (self.x - quarter_size, self.y + quarter_size, self.z - quarter_size),  # 2: -+-
            (self.x + quarter_size, self.y + quarter_size, self.z - quarter_size),  # 3: ++-
            (self.x - quarter_size, self.y - quarter_size, self.z + quarter_size),  # 4: --+
            (self.x + quarter_size, self.y - quarter_size, self.z + quarter_size),  # 5: +-+
            (self.x - quarter_size, self.y + quarter_size, self.z + quarter_size),  # 6: -++
            (self.x + quarter_size, self.y + quarter_size, self.z + quarter_size),  # 7: +++
        ]
        
        for i, (cx, cy, cz) in enumerate(octants):
            self.children[i] = OctreeNode(cx, cy, cz, quarter_size, self.capacity)
        
        self.is_leaf = False
        
        # Redistribute points to children
        for point in self.points:
            x, y, z, vertex_id = point
            for child in self.children:
                if child and child.contains_point(x, y, z):
                    child.insert(x, y, z, vertex_id)
                    break
        
        self.points.clear()
    
    def insert(self, x: float, y: float, z: float, vertex_id: str) -> bool:
        """Insert point into octree."""
        if not self.contains_point(x, y, z):
            return False
        
        if self.is_leaf:
            self.points.append((x, y, z, vertex_id))
            
            # Subdivide if capacity exceeded
            if len(self.points) > self.capacity:
                self.subdivide()
            
            return True
        else:
            # Insert into appropriate child
            for child in self.children:
                if child and child.insert(x, y, z, vertex_id):
                    return True
            return False
    
    def query_box(self, box_x: float, box_y: float, box_z: float,
                  box_w: float, box_h: float, box_d: float) -> List[Tuple[float, float, float, str]]:
        """Query points within given box."""
        result = []
        
        if not self.intersects_box(box_x, box_y, box_z, box_w, box_h, box_d):
            return result
        
        if self.is_leaf:
            for x, y, z, vertex_id in self.points:
                if (box_x <= x < box_x + box_w and
                    box_y <= y < box_y + box_h and
                    box_z <= z < box_z + box_d):
                    result.append((x, y, z, vertex_id))
        else:
            for child in self.children:
                if child:
                    result.extend(child.query_box(box_x, box_y, box_z, box_w, box_h, box_d))
        
        return result
    
    def query_sphere(self, center_x: float, center_y: float, center_z: float, radius: float) -> List[Tuple[float, float, float, str]]:
        """Query points within given sphere."""
        if not self.intersects_sphere(center_x, center_y, center_z, radius):
            return []
        
        result = []
        radius_sq = radius * radius
        
        if self.is_leaf:
            for x, y, z, vertex_id in self.points:
                dx = x - center_x
                dy = y - center_y
                dz = z - center_z
                dist_sq = dx * dx + dy * dy + dz * dz
                
                if dist_sq <= radius_sq:
                    result.append((x, y, z, vertex_id))
        else:
            for child in self.children:
                if child:
                    result.extend(child.query_sphere(center_x, center_y, center_z, radius))
        
        return result
    
    def remove(self, x: float, y: float, z: float, vertex_id: str) -> bool:
        """Remove point from octree."""
        if not self.contains_point(x, y, z):
            return False
        
        if self.is_leaf:
            for i, point in enumerate(self.points):
                if (point[0] == x and point[1] == y and 
                    point[2] == z and point[3] == vertex_id):
                    del self.points[i]
                    return True
            return False
        else:
            for child in self.children:
                if child and child.remove(x, y, z, vertex_id):
                    return True
            return False


class xOctreeStrategy(aEdgeStrategy):
    """
    Octree edge strategy for 3D spatial graphs.
    
    Efficiently manages 3D spatial relationships with logarithmic
    complexity for 3D spatial queries and nearest neighbor searches.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Octree strategy."""
        super().__init__(EdgeMode.OCTREE, traits, **options)
        
        # 3D spatial bounds
        self.center_x = options.get('center_x', 0.0)
        self.center_y = options.get('center_y', 0.0)
        self.center_z = options.get('center_z', 0.0)
        self.size = options.get('size', 500.0)  # Half-size of the root cube
        self.capacity = options.get('capacity', 8)
        
        # Core octree
        self._root = OctreeNode(self.center_x, self.center_y, self.center_z, self.size, self.capacity)
        
        # Vertex management
        self._vertices: Dict[str, Tuple[float, float, float]] = {}  # vertex_id -> (x, y, z)
        self._edges: Dict[Tuple[str, str], Dict[str, Any]] = {}  # (source, target) -> properties
        self._spatial_edges: Set[Tuple[str, str]] = set()  # Edges based on spatial proximity
        
        # Performance tracking
        self._edge_count = 0
        self._spatial_threshold = options.get('spatial_threshold', 50.0)  # Auto-connect distance
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the octree strategy."""
        return (EdgeTrait.SPATIAL | EdgeTrait.SPARSE | EdgeTrait.CACHE_FRIENDLY)
    
    def _auto_connect_spatial(self, vertex: str, x: float, y: float, z: float) -> None:
        """Automatically connect vertex to nearby vertices."""
        if self._spatial_threshold <= 0:
            return
        
        # Find nearby vertices
        nearby = self._root.query_sphere(x, y, z, self._spatial_threshold)
        
        for nx, ny, nz, neighbor_id in nearby:
            if neighbor_id != vertex:
                # Calculate 3D distance
                distance = math.sqrt((x - nx) ** 2 + (y - ny) ** 2 + (z - nz) ** 2)
                
                # Add spatial edge
                edge_key = (min(vertex, neighbor_id), max(vertex, neighbor_id))
                if edge_key not in self._edges:
                    self._edges[edge_key] = {
                        'distance': distance,
                        'spatial': True,
                        'weight': 1.0 / (1.0 + distance),  # Inverse distance weight
                        'dimension': '3D'
                    }
                    self._spatial_edges.add(edge_key)
                    self._edge_count += 1
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge between 3D spatial vertices."""
        # Ensure vertices exist with positions
        if source not in self._vertices:
            x = properties.get('source_x', 0.0)
            y = properties.get('source_y', 0.0)
            z = properties.get('source_z', 0.0)
            self.add_spatial_vertex(source, x, y, z)
        
        if target not in self._vertices:
            x = properties.get('target_x', 0.0)
            y = properties.get('target_y', 0.0)
            z = properties.get('target_z', 0.0)
            self.add_spatial_vertex(target, x, y, z)
        
        # Calculate 3D distance
        sx, sy, sz = self._vertices[source]
        tx, ty, tz = self._vertices[target]
        distance = math.sqrt((sx - tx) ** 2 + (sy - ty) ** 2 + (sz - tz) ** 2)
        
        # Add edge
        edge_key = (min(source, target), max(source, target))
        self._edges[edge_key] = {
            'distance': distance,
            'spatial': properties.get('spatial', False),
            'weight': properties.get('weight', 1.0),
            'dimension': '3D',
            **properties
        }
        
        if edge_key not in self._spatial_edges:
            self._edge_count += 1
        
        return f"{source}<->{target}"
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge between vertices."""
        edge_key = (min(source, target), max(source, target))
        
        if edge_key in self._edges:
            del self._edges[edge_key]
            self._spatial_edges.discard(edge_key)
            self._edge_count -= 1
            return True
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        edge_key = (min(source, target), max(source, target))
        return edge_key in self._edges
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        edge_key = (min(source, target), max(source, target))
        return self._edges.get(edge_key)
    
    def neighbors(self, vertex: str, direction: str = 'both') -> Iterator[str]:
        """Get neighbors of vertex."""
        for (v1, v2) in self._edges:
            if v1 == vertex:
                yield v2
            elif v2 == vertex:
                yield v1
    
    def degree(self, vertex: str, direction: str = 'both') -> int:
        """Get degree of vertex."""
        return len(list(self.neighbors(vertex, direction)))
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for (source, target), edge_data in self._edges.items():
            if data:
                yield (source, target, edge_data)
            else:
                yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices.keys())
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = OctreeNode(self.center_x, self.center_y, self.center_z, self.size, self.capacity)
        self._vertices.clear()
        self._edges.clear()
        self._spatial_edges.clear()
        self._edge_count = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex at random 3D position."""
        if vertex not in self._vertices:
            # Random position within bounds
            import random
            x = self.center_x + (random.random() - 0.5) * 2 * self.size
            y = self.center_y + (random.random() - 0.5) * 2 * self.size
            z = self.center_z + (random.random() - 0.5) * 2 * self.size
            self.add_spatial_vertex(vertex, x, y, z)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Remove from octree
        x, y, z = self._vertices[vertex]
        self._root.remove(x, y, z, vertex)
        
        # Remove all edges
        edges_to_remove = []
        for (v1, v2) in self._edges:
            if v1 == vertex or v2 == vertex:
                edges_to_remove.append((v1, v2))
        
        for edge_key in edges_to_remove:
            del self._edges[edge_key]
            self._spatial_edges.discard(edge_key)
            self._edge_count -= 1
        
        # Remove vertex
        del self._vertices[vertex]
        return True
    
    # ============================================================================
    # 3D SPATIAL OPERATIONS
    # ============================================================================
    
    def add_spatial_vertex(self, vertex: str, x: float, y: float, z: float) -> None:
        """Add vertex at specific 3D spatial position."""
        # Remove old position if exists
        if vertex in self._vertices:
            old_x, old_y, old_z = self._vertices[vertex]
            self._root.remove(old_x, old_y, old_z, vertex)
        
        # Add to octree
        self._vertices[vertex] = (x, y, z)
        self._root.insert(x, y, z, vertex)
        
        # Auto-connect to nearby vertices
        self._auto_connect_spatial(vertex, x, y, z)
    
    def get_vertex_position(self, vertex: str) -> Optional[Tuple[float, float, float]]:
        """Get vertex 3D position."""
        return self._vertices.get(vertex)
    
    def set_vertex_position(self, vertex: str, x: float, y: float, z: float) -> None:
        """Update vertex 3D position."""
        self.add_spatial_vertex(vertex, x, y, z)
    
    def query_box(self, x: float, y: float, z: float, 
                  width: float, height: float, depth: float) -> List[str]:
        """Query vertices within 3D box."""
        points = self._root.query_box(x, y, z, width, height, depth)
        return [vertex_id for _, _, _, vertex_id in points]
    
    def query_sphere(self, center_x: float, center_y: float, center_z: float, radius: float) -> List[str]:
        """Query vertices within 3D sphere."""
        points = self._root.query_sphere(center_x, center_y, center_z, radius)
        return [vertex_id for _, _, _, vertex_id in points]
    
    def nearest_neighbors_3d(self, vertex: str, k: int = 1) -> List[Tuple[str, float]]:
        """Find k nearest neighbors to vertex in 3D space."""
        if vertex not in self._vertices:
            return []
        
        x, y, z = self._vertices[vertex]
        
        # Query expanding radius until we have enough candidates
        radius = 10.0
        candidates = []
        
        while len(candidates) < k * 2 and radius <= self.size * 2:
            candidates = self.query_sphere(x, y, z, radius)
            candidates = [v for v in candidates if v != vertex]
            radius *= 2
        
        # Calculate 3D distances and sort
        distances = []
        for neighbor in candidates:
            nx, ny, nz = self._vertices[neighbor]
            dist = math.sqrt((x - nx) ** 2 + (y - ny) ** 2 + (z - nz) ** 2)
            distances.append((neighbor, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]
    
    def get_spatial_edges_in_box(self, x: float, y: float, z: float,
                                width: float, height: float, depth: float) -> List[Tuple[str, str]]:
        """Get edges where both vertices are in given 3D box."""
        vertices_in_box = set(self.query_box(x, y, z, width, height, depth))
        
        spatial_edges = []
        for (v1, v2) in self._edges:
            if v1 in vertices_in_box and v2 in vertices_in_box:
                spatial_edges.append((v1, v2))
        
        return spatial_edges
    
    def cluster_vertices_3d(self, max_distance: float) -> List[List[str]]:
        """Cluster vertices based on 3D spatial proximity."""
        visited = set()
        clusters = []
        
        for vertex in self._vertices:
            if vertex in visited:
                continue
            
            # Start new cluster
            cluster = []
            stack = [vertex]
            
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                
                visited.add(current)
                cluster.append(current)
                
                # Find nearby vertices in 3D
                x, y, z = self._vertices[current]
                nearby = self.query_sphere(x, y, z, max_distance)
                
                for neighbor in nearby:
                    if neighbor not in visited:
                        stack.append(neighbor)
            
            if cluster:
                clusters.append(cluster)
        
        return clusters
    
    def get_bounding_box(self) -> Tuple[float, float, float, float, float, float]:
        """Get 3D bounding box of all vertices."""
        if not self._vertices:
            return (0, 0, 0, 0, 0, 0)
        
        positions = list(self._vertices.values())
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions)
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions)
        min_z = min(pos[2] for pos in positions)
        max_z = max(pos[2] for pos in positions)
        
        return (min_x, min_y, min_z, max_x, max_y, max_z)
    
    def get_3d_statistics(self) -> Dict[str, Any]:
        """Get comprehensive 3D spatial statistics."""
        if not self._vertices:
            return {'vertices': 0, 'edges': 0, 'volume': 0}
        
        # Calculate 3D extent
        min_x, min_y, min_z, max_x, max_y, max_z = self.get_bounding_box()
        
        volume = (max_x - min_x) * (max_y - min_y) * (max_z - min_z) if len(self._vertices) > 1 else 0
        vertex_density = len(self._vertices) / max(1, volume)
        
        # Edge length statistics (3D distances)
        edge_lengths = []
        for (v1, v2), edge_data in self._edges.items():
            edge_lengths.append(edge_data.get('distance', 0))
        
        avg_edge_length = sum(edge_lengths) / len(edge_lengths) if edge_lengths else 0
        max_edge_length = max(edge_lengths) if edge_lengths else 0
        min_edge_length = min(edge_lengths) if edge_lengths else 0
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'spatial_edges': len(self._spatial_edges),
            'bounding_box': (min_x, min_y, min_z, max_x, max_y, max_z),
            'volume': volume,
            'vertex_density': vertex_density,
            'avg_edge_length': avg_edge_length,
            'min_edge_length': min_edge_length,
            'max_edge_length': max_edge_length,
            'spatial_threshold': self._spatial_threshold,
            'octree_capacity': self.capacity,
            'octree_size': self.size * 2  # Full cube size
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'OCTREE',
            'backend': '3D spatial partitioning with octree',
            'center': f"({self.center_x}, {self.center_y}, {self.center_z})",
            'size': self.size * 2,  # Full cube size
            'capacity': self.capacity,
            'spatial_threshold': self._spatial_threshold,
            'complexity': {
                'insert': 'O(log n)',
                'remove': 'O(log n)',
                'box_query': 'O(log n + k)',  # k = results
                'sphere_query': 'O(log n + k)',
                'nearest_neighbor': 'O(log n + k)',
                'space': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_3d_statistics()
        
        return {
            'vertices': stats['vertices'],
            'edges': stats['edges'],
            'spatial_edges': stats['spatial_edges'],
            'vertex_density': f"{stats['vertex_density']:.3f}",
            'avg_edge_length': f"{stats['avg_edge_length']:.1f}",
            'volume': f"{stats['volume']:.1f}",
            'octree_size': f"{stats['octree_size']:.1f}",
            'memory_usage': f"{self._edge_count * 100 + len(self._vertices) * 120} bytes (estimated)"
        }
