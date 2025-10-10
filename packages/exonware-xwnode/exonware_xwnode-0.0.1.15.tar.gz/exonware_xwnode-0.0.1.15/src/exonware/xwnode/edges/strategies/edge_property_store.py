"""
Edge Property Store Strategy Implementation

This module implements the EDGE_PROPERTY_STORE strategy for columnar
edge attribute storage with efficient analytical queries.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple, Union
from collections import defaultdict
import statistics
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class PropertyColumn:
    """Columnar storage for a single edge property."""
    
    def __init__(self, name: str, data_type: type = object):
        self.name = name
        self.data_type = data_type
        self.values: List[Any] = []
        self.null_bitmap: List[bool] = []  # True if value is null
        
        # Column statistics
        self._min_value = None
        self._max_value = None
        self._unique_values: Set[Any] = set()
        self._stats_dirty = True
    
    def append(self, value: Any) -> None:
        """Append value to column."""
        if value is None:
            self.values.append(None)
            self.null_bitmap.append(True)
        else:
            self.values.append(value)
            self.null_bitmap.append(False)
            self._unique_values.add(value)
        
        self._stats_dirty = True
    
    def set_value(self, index: int, value: Any) -> None:
        """Set value at specific index."""
        if 0 <= index < len(self.values):
            old_value = self.values[index]
            
            if value is None:
                self.values[index] = None
                self.null_bitmap[index] = True
                if old_value is not None:
                    self._unique_values.discard(old_value)
            else:
                self.values[index] = value
                self.null_bitmap[index] = False
                self._unique_values.add(value)
                if old_value is not None:
                    self._unique_values.discard(old_value)
            
            self._stats_dirty = True
    
    def get_value(self, index: int) -> Any:
        """Get value at specific index."""
        if 0 <= index < len(self.values):
            return self.values[index]
        return None
    
    def remove_at_index(self, index: int) -> None:
        """Remove value at specific index."""
        if 0 <= index < len(self.values):
            old_value = self.values[index]
            del self.values[index]
            del self.null_bitmap[index]
            
            if old_value is not None:
                # Rebuild unique values set
                self._unique_values = set(v for v in self.values if v is not None)
            
            self._stats_dirty = True
    
    def _update_statistics(self) -> None:
        """Update column statistics."""
        if not self._stats_dirty:
            return
        
        non_null_values = [v for v in self.values if v is not None]
        
        if non_null_values:
            try:
                if all(isinstance(v, (int, float)) for v in non_null_values):
                    self._min_value = min(non_null_values)
                    self._max_value = max(non_null_values)
                else:
                    self._min_value = min(non_null_values)
                    self._max_value = max(non_null_values)
            except (TypeError, ValueError):
                self._min_value = None
                self._max_value = None
        else:
            self._min_value = None
            self._max_value = None
        
        self._stats_dirty = False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get column statistics."""
        self._update_statistics()
        
        non_null_values = [v for v in self.values if v is not None]
        null_count = sum(self.null_bitmap)
        
        stats = {
            'name': self.name,
            'data_type': self.data_type.__name__,
            'total_count': len(self.values),
            'non_null_count': len(non_null_values),
            'null_count': null_count,
            'null_percentage': (null_count / max(1, len(self.values))) * 100,
            'unique_count': len(self._unique_values),
            'min_value': self._min_value,
            'max_value': self._max_value
        }
        
        # Add numeric statistics if applicable
        if non_null_values and all(isinstance(v, (int, float)) for v in non_null_values):
            try:
                stats.update({
                    'mean': statistics.mean(non_null_values),
                    'median': statistics.median(non_null_values),
                    'std_dev': statistics.stdev(non_null_values) if len(non_null_values) > 1 else 0,
                    'variance': statistics.variance(non_null_values) if len(non_null_values) > 1 else 0
                })
            except (statistics.StatisticsError, ValueError):
                pass
        
        return stats
    
    def filter_indices(self, predicate: callable) -> List[int]:
        """Get indices where predicate is true."""
        return [i for i, value in enumerate(self.values) if predicate(value)]
    
    def __len__(self) -> int:
        """Get number of values in column."""
        return len(self.values)


class xEdgePropertyStoreStrategy(aEdgeStrategy):
    """
    Edge Property Store strategy for columnar edge attributes.
    
    Efficiently stores and queries edge properties in columnar format
    for analytical workloads and complex property-based filtering.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Edge Property Store strategy."""
        super().__init__(EdgeMode.EDGE_PROPERTY_STORE, traits, **options)
        
        self.enable_compression = options.get('enable_compression', True)
        self.default_batch_size = options.get('batch_size', 1000)
        
        # Core edge storage
        self._source_vertices: List[str] = []  # Source vertex names
        self._target_vertices: List[str] = []  # Target vertex names
        self._edge_ids: List[str] = []         # Edge identifiers
        
        # Columnar property storage
        self._property_columns: Dict[str, PropertyColumn] = {}
        
        # Standard edge properties columns
        self._init_standard_columns()
        
        # Vertex management
        self._vertices: Set[str] = set()
        self._edge_count = 0
        self._next_edge_id = 0
        
        # Indices for fast lookups
        self._edge_index: Dict[Tuple[str, str], List[int]] = defaultdict(list)  # (source, target) -> [positions]
        self._vertex_out_edges: Dict[str, List[int]] = defaultdict(list)  # vertex -> [edge_positions]
        self._vertex_in_edges: Dict[str, List[int]] = defaultdict(list)   # vertex -> [edge_positions]
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the edge property store strategy."""
        return (EdgeTrait.COLUMNAR | EdgeTrait.MULTI | EdgeTrait.COMPRESSED)
    
    def _init_standard_columns(self) -> None:
        """Initialize standard edge property columns."""
        self._property_columns['weight'] = PropertyColumn('weight', float)
        self._property_columns['timestamp'] = PropertyColumn('timestamp', float)
        self._property_columns['label'] = PropertyColumn('label', str)
        self._property_columns['category'] = PropertyColumn('category', str)
    
    def _generate_edge_id(self) -> str:
        """Generate unique edge ID."""
        self._next_edge_id += 1
        return f"edge_{self._next_edge_id}"
    
    def _add_to_indices(self, position: int, source: str, target: str) -> None:
        """Add edge to lookup indices."""
        edge_key = (source, target)
        self._edge_index[edge_key].append(position)
        self._vertex_out_edges[source].append(position)
        self._vertex_in_edges[target].append(position)
        self._vertices.add(source)
        self._vertices.add(target)
    
    def _remove_from_indices(self, position: int) -> None:
        """Remove edge from lookup indices."""
        if position >= len(self._source_vertices):
            return
        
        source = self._source_vertices[position]
        target = self._target_vertices[position]
        edge_key = (source, target)
        
        # Remove from indices
        self._edge_index[edge_key].remove(position)
        if not self._edge_index[edge_key]:
            del self._edge_index[edge_key]
        
        self._vertex_out_edges[source].remove(position)
        self._vertex_in_edges[target].remove(position)
        
        # Update positions in indices (shift down)
        for key, positions in self._edge_index.items():
            for i, pos in enumerate(positions):
                if pos > position:
                    positions[i] = pos - 1
        
        for vertex_edges in self._vertex_out_edges.values():
            for i, pos in enumerate(vertex_edges):
                if pos > position:
                    vertex_edges[i] = pos - 1
        
        for vertex_edges in self._vertex_in_edges.values():
            for i, pos in enumerate(vertex_edges):
                if pos > position:
                    vertex_edges[i] = pos - 1
    
    def _ensure_property_column(self, property_name: str, data_type: type = object) -> None:
        """Ensure property column exists."""
        if property_name not in self._property_columns:
            column = PropertyColumn(property_name, data_type)
            
            # Backfill with None values for existing edges
            for _ in range(self._edge_count):
                column.append(None)
            
            self._property_columns[property_name] = column
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge with properties to columnar store."""
        edge_id = properties.pop('edge_id', self._generate_edge_id())
        
        # Add to core storage
        position = len(self._source_vertices)
        self._source_vertices.append(source)
        self._target_vertices.append(target)
        self._edge_ids.append(edge_id)
        
        # Add to indices
        self._add_to_indices(position, source, target)
        
        # Add properties to columns
        for prop_name, value in properties.items():
            if prop_name not in self._property_columns:
                # Infer data type
                data_type = type(value) if value is not None else object
                self._ensure_property_column(prop_name, data_type)
            
            self._property_columns[prop_name].append(value)
        
        # Fill missing properties with None
        for column_name, column in self._property_columns.items():
            if column_name not in properties:
                column.append(None)
        
        self._edge_count += 1
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge from property store."""
        edge_key = (source, target)
        positions = self._edge_index.get(edge_key, [])
        
        if not positions:
            return False
        
        # Find specific edge by ID or use first
        position_to_remove = positions[0]
        if edge_id:
            for pos in positions:
                if self._edge_ids[pos] == edge_id:
                    position_to_remove = pos
                    break
        
        # Remove from all structures
        self._remove_from_indices(position_to_remove)
        
        del self._source_vertices[position_to_remove]
        del self._target_vertices[position_to_remove]
        del self._edge_ids[position_to_remove]
        
        # Remove from all property columns
        for column in self._property_columns.values():
            column.remove_at_index(position_to_remove)
        
        self._edge_count -= 1
        return True
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        edge_key = (source, target)
        return edge_key in self._edge_index
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data with all properties."""
        edge_key = (source, target)
        positions = self._edge_index.get(edge_key, [])
        
        if not positions:
            return None
        
        # Return data for first matching edge
        position = positions[0]
        edge_data = {
            'source': source,
            'target': target,
            'edge_id': self._edge_ids[position],
            'position': position
        }
        
        # Add all properties
        for prop_name, column in self._property_columns.items():
            edge_data[prop_name] = column.get_value(position)
        
        return edge_data
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of vertex."""
        neighbors_found = set()
        
        if direction in ['out', 'both']:
            for pos in self._vertex_out_edges.get(vertex, []):
                target = self._target_vertices[pos]
                if target not in neighbors_found:
                    neighbors_found.add(target)
                    yield target
        
        if direction in ['in', 'both']:
            for pos in self._vertex_in_edges.get(vertex, []):
                source = self._source_vertices[pos]
                if source not in neighbors_found:
                    neighbors_found.add(source)
                    yield source
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex."""
        if direction == 'out':
            return len(self._vertex_out_edges.get(vertex, []))
        elif direction == 'in':
            return len(self._vertex_in_edges.get(vertex, []))
        else:  # both
            out_neighbors = set(self._target_vertices[pos] for pos in self._vertex_out_edges.get(vertex, []))
            in_neighbors = set(self._source_vertices[pos] for pos in self._vertex_in_edges.get(vertex, []))
            return len(out_neighbors | in_neighbors)
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for i in range(self._edge_count):
            source = self._source_vertices[i]
            target = self._target_vertices[i]
            
            if data:
                edge_data = {'edge_id': self._edge_ids[i]}
                for prop_name, column in self._property_columns.items():
                    edge_data[prop_name] = column.get_value(i)
                yield (source, target, edge_data)
            else:
                yield (source, target)
    
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
        self._source_vertices.clear()
        self._target_vertices.clear()
        self._edge_ids.clear()
        
        for column in self._property_columns.values():
            column.values.clear()
            column.null_bitmap.clear()
            column._unique_values.clear()
            column._stats_dirty = True
        
        self._vertices.clear()
        self._edge_index.clear()
        self._vertex_out_edges.clear()
        self._vertex_in_edges.clear()
        
        self._edge_count = 0
        self._next_edge_id = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex to graph."""
        self._vertices.add(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Find all edges involving this vertex
        edges_to_remove = []
        for i in range(self._edge_count):
            source = self._source_vertices[i]
            target = self._target_vertices[i]
            if source == vertex or target == vertex:
                edges_to_remove.append((source, target, self._edge_ids[i]))
        
        # Remove edges in reverse order to maintain indices
        for source, target, edge_id in reversed(edges_to_remove):
            self.remove_edge(source, target, edge_id)
        
        # Remove vertex
        self._vertices.discard(vertex)
        return True
    
    # ============================================================================
    # COLUMNAR ANALYTICS OPERATIONS
    # ============================================================================
    
    def add_property_column(self, column_name: str, data_type: type = object, default_value: Any = None) -> None:
        """Add new property column."""
        if column_name in self._property_columns:
            return
        
        column = PropertyColumn(column_name, data_type)
        
        # Backfill with default values
        for _ in range(self._edge_count):
            column.append(default_value)
        
        self._property_columns[column_name] = column
    
    def remove_property_column(self, column_name: str) -> bool:
        """Remove property column."""
        if column_name in self._property_columns:
            del self._property_columns[column_name]
            return True
        return False
    
    def get_property_columns(self) -> List[str]:
        """Get list of all property column names."""
        return list(self._property_columns.keys())
    
    def get_column_data(self, column_name: str) -> Optional[List[Any]]:
        """Get all values from a specific column."""
        if column_name in self._property_columns:
            return self._property_columns[column_name].values.copy()
        return None
    
    def set_edge_property(self, source: str, target: str, property_name: str, value: Any) -> bool:
        """Set property value for specific edge."""
        edge_key = (source, target)
        positions = self._edge_index.get(edge_key, [])
        
        if not positions:
            return False
        
        # Ensure column exists
        if property_name not in self._property_columns:
            self._ensure_property_column(property_name, type(value) if value is not None else object)
        
        # Set value for first matching edge
        position = positions[0]
        self._property_columns[property_name].set_value(position, value)
        return True
    
    def get_edge_property(self, source: str, target: str, property_name: str) -> Any:
        """Get property value for specific edge."""
        edge_key = (source, target)
        positions = self._edge_index.get(edge_key, [])
        
        if not positions or property_name not in self._property_columns:
            return None
        
        position = positions[0]
        return self._property_columns[property_name].get_value(position)
    
    def filter_edges_by_property(self, property_name: str, predicate: callable) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Filter edges by property values."""
        if property_name not in self._property_columns:
            return []
        
        column = self._property_columns[property_name]
        matching_indices = column.filter_indices(predicate)
        
        result = []
        for index in matching_indices:
            source = self._source_vertices[index]
            target = self._target_vertices[index]
            edge_data = {'edge_id': self._edge_ids[index]}
            
            for prop_name, prop_column in self._property_columns.items():
                edge_data[prop_name] = prop_column.get_value(index)
            
            result.append((source, target, edge_data))
        
        return result
    
    def aggregate_property(self, property_name: str, operation: str = 'count') -> Any:
        """Aggregate property values across all edges."""
        if property_name not in self._property_columns:
            return None
        
        column = self._property_columns[property_name]
        non_null_values = [v for v in column.values if v is not None]
        
        if not non_null_values:
            return None
        
        if operation == 'count':
            return len(non_null_values)
        elif operation == 'sum':
            return sum(non_null_values) if all(isinstance(v, (int, float)) for v in non_null_values) else None
        elif operation == 'avg' or operation == 'mean':
            return statistics.mean(non_null_values) if all(isinstance(v, (int, float)) for v in non_null_values) else None
        elif operation == 'min':
            return min(non_null_values)
        elif operation == 'max':
            return max(non_null_values)
        elif operation == 'median':
            return statistics.median(non_null_values) if all(isinstance(v, (int, float)) for v in non_null_values) else None
        elif operation == 'unique':
            return len(set(non_null_values))
        else:
            return None
    
    def group_by_property(self, property_name: str) -> Dict[Any, List[int]]:
        """Group edge indices by property values."""
        if property_name not in self._property_columns:
            return {}
        
        column = self._property_columns[property_name]
        groups = defaultdict(list)
        
        for i, value in enumerate(column.values):
            groups[value].append(i)
        
        return dict(groups)
    
    def get_property_statistics(self, property_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific property column."""
        if property_name in self._property_columns:
            return self._property_columns[property_name].get_statistics()
        return None
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all property columns."""
        return {name: column.get_statistics() for name, column in self._property_columns.items()}
    
    def export_to_dataframe_format(self) -> Dict[str, List[Any]]:
        """Export data in DataFrame-compatible format."""
        data = {
            'source': self._source_vertices.copy(),
            'target': self._target_vertices.copy(),
            'edge_id': self._edge_ids.copy()
        }
        
        for prop_name, column in self._property_columns.items():
            data[prop_name] = column.values.copy()
        
        return data
    
    def get_schema(self) -> Dict[str, str]:
        """Get schema information for all columns."""
        schema = {
            'source': 'str',
            'target': 'str',
            'edge_id': 'str'
        }
        
        for prop_name, column in self._property_columns.items():
            schema[prop_name] = column.data_type.__name__
        
        return schema
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the property store."""
        column_stats = self.get_all_statistics()
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'property_columns': len(self._property_columns),
            'column_names': list(self._property_columns.keys()),
            'total_cells': self._edge_count * len(self._property_columns),
            'memory_overhead': len(self._property_columns) * 100,  # Estimated
            'column_statistics': column_stats,
            'enable_compression': self.enable_compression,
            'batch_size': self.default_batch_size
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'EDGE_PROPERTY_STORE',
            'backend': 'Columnar storage with property indices',
            'enable_compression': self.enable_compression,
            'batch_size': self.default_batch_size,
            'property_columns': len(self._property_columns),
            'complexity': {
                'add_edge': 'O(p)',  # p = number of properties
                'remove_edge': 'O(p + degree)',
                'property_filter': 'O(e)',  # e = number of edges
                'property_aggregate': 'O(e)',
                'group_by': 'O(e)',
                'space': 'O(e * p)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_comprehensive_statistics()
        
        return {
            'vertices': stats['vertices'],
            'edges': stats['edges'],
            'property_columns': stats['property_columns'],
            'total_cells': stats['total_cells'],
            'column_names': ', '.join(stats['column_names'][:5]) + ('...' if len(stats['column_names']) > 5 else ''),
            'avg_properties_per_edge': f"{len(self._property_columns):.1f}",
            'memory_usage': f"{stats['edges'] * len(self._property_columns) * 8 + stats['memory_overhead']} bytes (estimated)"
        }
