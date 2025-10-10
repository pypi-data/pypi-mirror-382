"""
Temporal EdgeSet Strategy Implementation

This module implements the TEMPORAL_EDGESET strategy for time-aware graphs
with temporal queries and time-based edge evolution.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, NamedTuple
from collections import defaultdict
import time
import bisect
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class TimeInterval(NamedTuple):
    """Represents a time interval."""
    start: float
    end: Optional[float]  # None means ongoing
    
    def contains(self, timestamp: float) -> bool:
        """Check if timestamp is within this interval."""
        return self.start <= timestamp <= (self.end if self.end is not None else float('inf'))
    
    def overlaps(self, other: 'TimeInterval') -> bool:
        """Check if this interval overlaps with another."""
        if self.end is None or other.end is None:
            return True  # Ongoing intervals always overlap
        return self.start <= other.end and other.start <= self.end


class TemporalEdge:
    """Represents an edge with temporal validity periods."""
    
    def __init__(self, edge_id: str, source: str, target: str, 
                 start_time: float, end_time: Optional[float] = None, **properties):
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.interval = TimeInterval(start_time, end_time)
        self.properties = properties.copy()
        self.created_at = time.time()
    
    def is_active_at(self, timestamp: float) -> bool:
        """Check if edge is active at given timestamp."""
        return self.interval.contains(timestamp)
    
    def is_currently_active(self) -> bool:
        """Check if edge is currently active."""
        return self.is_active_at(time.time())
    
    def overlaps_with(self, other: 'TemporalEdge') -> bool:
        """Check if this edge's time interval overlaps with another."""
        return self.interval.overlaps(other.interval)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.edge_id,
            'source': self.source,
            'target': self.target,
            'start_time': self.interval.start,
            'end_time': self.interval.end,
            'properties': self.properties,
            'created_at': self.created_at,
            'is_active': self.is_currently_active()
        }


class xTemporalEdgeSetStrategy(aEdgeStrategy):
    """
    Temporal EdgeSet strategy for time-aware graph management.
    
    Provides efficient temporal queries, time-based edge activation/deactivation,
    and historical graph state reconstruction.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Temporal EdgeSet strategy."""
        super().__init__(EdgeMode.TEMPORAL_EDGESET, traits, **options)
        
        self.is_directed = options.get('directed', True)
        self.default_duration = options.get('default_duration', None)  # None = infinite
        self.time_precision = options.get('time_precision', 0.001)  # 1ms precision
        
        # Core temporal storage
        # edges_by_time: timestamp -> list of (edge_id, 'start'/'end')
        self._edges_by_time: Dict[float, List[Tuple[str, str]]] = defaultdict(list)
        self._sorted_timestamps: List[float] = []  # Sorted for binary search
        
        # Edge storage
        self._edges: Dict[str, TemporalEdge] = {}  # edge_id -> TemporalEdge
        self._outgoing: Dict[str, Set[str]] = defaultdict(set)  # source -> set of edge_ids
        self._incoming: Dict[str, Set[str]] = defaultdict(set) if self.is_directed else None
        
        # Vertex management
        self._vertices: Set[str] = set()
        self._edge_id_counter = 0
        self._current_time_cache = None
        self._cache_timestamp = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the temporal edgeset strategy."""
        return (EdgeTrait.TEMPORAL | EdgeTrait.DIRECTED | EdgeTrait.SPARSE | EdgeTrait.WEIGHTED)
    
    def _round_time(self, timestamp: float) -> float:
        """Round timestamp to configured precision."""
        return round(timestamp / self.time_precision) * self.time_precision
    
    def _add_time_event(self, timestamp: float, edge_id: str, event_type: str) -> None:
        """Add a time-based event."""
        rounded_time = self._round_time(timestamp)
        
        self._edges_by_time[rounded_time].append((edge_id, event_type))
        
        # Maintain sorted timestamps
        if rounded_time not in self._sorted_timestamps:
            bisect.insort(self._sorted_timestamps, rounded_time)
    
    def _get_active_edges_at(self, timestamp: float) -> Set[str]:
        """Get all active edge IDs at a specific timestamp."""
        # Use cache if timestamp is current
        current_time = time.time()
        if (self._current_time_cache is not None and 
            abs(timestamp - current_time) < self.time_precision and
            abs(self._cache_timestamp - current_time) < 1.0):  # 1 second cache
            return self._current_time_cache
        
        active_edges = set()
        
        # Process events up to the timestamp
        for ts in self._sorted_timestamps:
            if ts > timestamp:
                break
            
            for edge_id, event_type in self._edges_by_time[ts]:
                if event_type == 'start':
                    active_edges.add(edge_id)
                elif event_type == 'end':
                    active_edges.discard(edge_id)
        
        # Add ongoing edges that started before timestamp
        for edge_id, edge in self._edges.items():
            if (edge.interval.start <= timestamp and 
                edge.interval.end is None and 
                edge_id not in active_edges):
                active_edges.add(edge_id)
        
        # Cache if this is current time
        if abs(timestamp - current_time) < self.time_precision:
            self._current_time_cache = active_edges.copy()
            self._cache_timestamp = current_time
        
        return active_edges
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add a temporal edge."""
        # Extract temporal properties
        start_time = properties.pop('start_time', time.time())
        end_time = properties.pop('end_time', self.default_duration)
        
        if end_time is not None and isinstance(end_time, (int, float)) and end_time > 0:
            # Convert relative duration to absolute end time
            if end_time < start_time:
                end_time = start_time + end_time
        
        # Generate edge ID
        edge_id = f"tedge_{self._edge_id_counter}"
        self._edge_id_counter += 1
        
        # Create temporal edge
        edge = TemporalEdge(edge_id, source, target, start_time, end_time, **properties)
        
        # Store edge
        self._edges[edge_id] = edge
        self._outgoing[source].add(edge_id)
        
        if self.is_directed and self._incoming is not None:
            self._incoming[target].add(edge_id)
        elif not self.is_directed and source != target:
            self._outgoing[target].add(edge_id)
        
        # Add vertices
        self._vertices.add(source)
        self._vertices.add(target)
        
        # Register time events
        self._add_time_event(start_time, edge_id, 'start')
        if end_time is not None:
            self._add_time_event(end_time, edge_id, 'end')
        
        # Invalidate cache
        self._current_time_cache = None
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove a temporal edge (mark as ended)."""
        # Find edge to remove
        target_edge_id = None
        
        if edge_id:
            if edge_id in self._edges:
                edge = self._edges[edge_id]
                if edge.source == source and edge.target == target:
                    target_edge_id = edge_id
        else:
            # Find first matching edge
            for eid in self._outgoing.get(source, set()):
                edge = self._edges.get(eid)
                if edge and edge.target == target and edge.is_currently_active():
                    target_edge_id = eid
                    break
        
        if not target_edge_id:
            return False
        
        edge = self._edges[target_edge_id]
        
        # End the edge at current time if it's ongoing
        if edge.interval.end is None:
            current_time = time.time()
            edge.interval = TimeInterval(edge.interval.start, current_time)
            self._add_time_event(current_time, target_edge_id, 'end')
        
        # Remove from adjacency lists
        self._outgoing[source].discard(target_edge_id)
        if self.is_directed and self._incoming is not None:
            self._incoming[target].discard(target_edge_id)
        elif not self.is_directed:
            self._outgoing[target].discard(target_edge_id)
        
        # Invalidate cache
        self._current_time_cache = None
        
        return True
    
    def has_edge(self, source: str, target: str, timestamp: Optional[float] = None) -> bool:
        """Check if edge exists at specific time (default: current time)."""
        if timestamp is None:
            timestamp = time.time()
        
        active_edges = self._get_active_edges_at(timestamp)
        
        for edge_id in active_edges:
            edge = self._edges.get(edge_id)
            if edge and edge.source == source and edge.target == target:
                return True
        
        return False
    
    def get_edge_data(self, source: str, target: str, 
                     timestamp: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Get edge data at specific time."""
        if timestamp is None:
            timestamp = time.time()
        
        active_edges = self._get_active_edges_at(timestamp)
        
        for edge_id in active_edges:
            edge = self._edges.get(edge_id)
            if edge and edge.source == source and edge.target == target:
                return edge.to_dict()
        
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out', 
                 timestamp: Optional[float] = None) -> Iterator[str]:
        """Get neighbors at specific time."""
        if timestamp is None:
            timestamp = time.time()
        
        active_edges = self._get_active_edges_at(timestamp)
        seen = set()
        
        if direction in ['out', 'both']:
            for edge_id in self._outgoing.get(vertex, set()):
                if edge_id in active_edges:
                    edge = self._edges[edge_id]
                    if edge.target not in seen:
                        seen.add(edge.target)
                        yield edge.target
        
        if direction in ['in', 'both'] and self.is_directed and self._incoming is not None:
            for edge_id in self._incoming.get(vertex, set()):
                if edge_id in active_edges:
                    edge = self._edges[edge_id]
                    if edge.source not in seen:
                        seen.add(edge.source)
                        yield edge.source
    
    def degree(self, vertex: str, direction: str = 'out', 
              timestamp: Optional[float] = None) -> int:
        """Get degree at specific time."""
        return sum(1 for _ in self.neighbors(vertex, direction, timestamp))
    
    def edges(self, data: bool = False, timestamp: Optional[float] = None) -> Iterator[tuple]:
        """Get all edges at specific time."""
        if timestamp is None:
            timestamp = time.time()
        
        active_edges = self._get_active_edges_at(timestamp)
        seen = set()
        
        for edge_id in active_edges:
            edge = self._edges[edge_id]
            edge_key = (edge.source, edge.target)
            
            # Avoid duplicates for undirected graphs
            if not self.is_directed and edge.source > edge.target:
                edge_key = (edge.target, edge.source)
            
            if edge_key not in seen:
                seen.add(edge_key)
                
                if data:
                    yield (edge.source, edge.target, edge.to_dict())
                else:
                    yield (edge.source, edge.target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get the number of currently active edges."""
        return len(self._get_active_edges_at(time.time()))
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        self._edges.clear()
        self._edges_by_time.clear()
        self._sorted_timestamps.clear()
        self._outgoing.clear()
        if self._incoming is not None:
            self._incoming.clear()
        self._vertices.clear()
        self._edge_id_counter = 0
        self._current_time_cache = None
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex."""
        self._vertices.add(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and end all its edges."""
        if vertex not in self._vertices:
            return False
        
        current_time = time.time()
        
        # End all edges involving this vertex
        for edge_id in list(self._outgoing.get(vertex, set())):
            edge = self._edges.get(edge_id)
            if edge and edge.interval.end is None:
                edge.interval = TimeInterval(edge.interval.start, current_time)
                self._add_time_event(current_time, edge_id, 'end')
        
        # End incoming edges
        if self.is_directed and self._incoming is not None:
            for edge_id in list(self._incoming.get(vertex, set())):
                edge = self._edges.get(edge_id)
                if edge and edge.interval.end is None:
                    edge.interval = TimeInterval(edge.interval.start, current_time)
                    self._add_time_event(current_time, edge_id, 'end')
        
        # Clear adjacency lists
        self._outgoing[vertex].clear()
        if self._incoming is not None:
            self._incoming[vertex].clear()
        
        self._vertices.remove(vertex)
        self._current_time_cache = None
        
        return True
    
    # ============================================================================
    # TEMPORAL-SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_edge_history(self, source: str, target: str) -> List[Dict[str, Any]]:
        """Get complete temporal history of edges between two vertices."""
        history = []
        
        for edge in self._edges.values():
            if edge.source == source and edge.target == target:
                history.append(edge.to_dict())
        
        # Sort by start time
        history.sort(key=lambda x: x['start_time'])
        return history
    
    def get_graph_at_time(self, timestamp: float) -> Dict[str, Any]:
        """Get complete graph state at specific timestamp."""
        active_edges = self._get_active_edges_at(timestamp)
        
        graph_state = {
            'timestamp': timestamp,
            'vertices': list(self._vertices),
            'edges': []
        }
        
        for edge_id in active_edges:
            edge = self._edges[edge_id]
            graph_state['edges'].append(edge.to_dict())
        
        return graph_state
    
    def get_time_range_edges(self, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Get all edges that were active during the time range."""
        result = []
        
        for edge in self._edges.values():
            # Check if edge interval overlaps with query range
            edge_end = edge.interval.end if edge.interval.end is not None else float('inf')
            
            if edge.interval.start <= end_time and edge_end >= start_time:
                result.append(edge.to_dict())
        
        return result
    
    def get_temporal_path(self, source: str, target: str, 
                         start_time: float, max_duration: float) -> Optional[List[str]]:
        """Find temporal path respecting edge timing constraints."""
        # Simple temporal BFS
        queue = [(source, start_time, [source])]
        visited = set()
        
        while queue:
            current_vertex, current_time, path = queue.pop(0)
            
            if current_vertex == target:
                return path
            
            state_key = (current_vertex, int(current_time / self.time_precision))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            # Explore neighbors at current time
            for neighbor in self.neighbors(current_vertex, 'out', current_time):
                if neighbor not in path:  # Avoid cycles
                    new_time = current_time + self.time_precision  # Move forward in time
                    new_path = path + [neighbor]
                    
                    if new_time - start_time <= max_duration:
                        queue.append((neighbor, new_time, new_path))
        
        return None
    
    def compact_old_edges(self, cutoff_time: float) -> int:
        """Remove edges that ended before cutoff time."""
        to_remove = []
        
        for edge_id, edge in self._edges.items():
            if (edge.interval.end is not None and 
                edge.interval.end < cutoff_time):
                to_remove.append(edge_id)
        
        for edge_id in to_remove:
            edge = self._edges[edge_id]
            
            # Remove from adjacency lists
            self._outgoing[edge.source].discard(edge_id)
            if self._incoming is not None:
                self._incoming[edge.target].discard(edge_id)
            
            # Remove from time events
            start_time = self._round_time(edge.interval.start)
            if edge.interval.end:
                end_time = self._round_time(edge.interval.end)
                if end_time in self._edges_by_time:
                    self._edges_by_time[end_time] = [
                        (eid, event) for eid, event in self._edges_by_time[end_time]
                        if eid != edge_id
                    ]
            
            # Remove edge
            del self._edges[edge_id]
        
        # Clean up empty timestamps
        empty_timestamps = [ts for ts, events in self._edges_by_time.items() if not events]
        for ts in empty_timestamps:
            del self._edges_by_time[ts]
            self._sorted_timestamps.remove(ts)
        
        self._current_time_cache = None
        return len(to_remove)
    
    def get_temporal_statistics(self) -> Dict[str, Any]:
        """Get statistics about temporal aspects."""
        current_time = time.time()
        active_count = len(self._get_active_edges_at(current_time))
        total_count = len(self._edges)
        
        # Calculate average edge duration
        durations = []
        for edge in self._edges.values():
            if edge.interval.end is not None:
                durations.append(edge.interval.end - edge.interval.start)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_edges': total_count,
            'active_edges': active_count,
            'ended_edges': total_count - active_count,
            'time_events': sum(len(events) for events in self._edges_by_time.values()),
            'unique_timestamps': len(self._sorted_timestamps),
            'avg_edge_duration': avg_duration,
            'oldest_edge': min((e.interval.start for e in self._edges.values()), default=current_time),
            'newest_edge': max((e.interval.start for e in self._edges.values()), default=current_time)
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'TEMPORAL_EDGESET',
            'backend': 'Time-indexed edge sets with binary search',
            'directed': self.is_directed,
            'time_precision': self.time_precision,
            'default_duration': self.default_duration,
            'complexity': {
                'add_edge': 'O(log T)',  # T = number of timestamps
                'remove_edge': 'O(log T)',
                'has_edge': 'O(T + E)',  # Worst case
                'temporal_query': 'O(log T + E_active)',
                'space': 'O(V + E + T)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_temporal_statistics()
        
        return {
            'vertices': len(self._vertices),
            'total_edges': stats['total_edges'],
            'active_edges': stats['active_edges'],
            'time_events': stats['time_events'],
            'timestamps': len(self._sorted_timestamps),
            'memory_usage': f"{stats['total_edges'] * 100 + stats['time_events'] * 20} bytes (estimated)",
            'cache_hit_rate': 'N/A'  # Would track in real implementation
        }
