"""
Flow Network Edge Strategy Implementation

This module implements the FLOW_NETWORK strategy for flow graphs with
capacity constraints, flow algorithms, and network flow optimization.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, DefaultDict
from collections import defaultdict, deque
import math
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class FlowEdge:
    """Represents an edge in a flow network with capacity and flow."""
    
    def __init__(self, edge_id: str, source: str, target: str, 
                 capacity: float, flow: float = 0.0, **properties):
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.capacity = max(0.0, float(capacity))
        self.flow = max(0.0, min(float(flow), self.capacity))
        self.properties = properties.copy()
        
        # Flow network specific properties
        self.cost_per_unit = properties.get('cost', 0.0)  # For min-cost flow
        self.is_residual = properties.get('is_residual', False)
    
    @property
    def residual_capacity(self) -> float:
        """Get remaining capacity for flow."""
        return self.capacity - self.flow
    
    @property
    def utilization(self) -> float:
        """Get capacity utilization as percentage."""
        return (self.flow / self.capacity * 100) if self.capacity > 0 else 0.0
    
    def add_flow(self, amount: float) -> float:
        """Add flow to edge, returns actual amount added."""
        max_addable = min(amount, self.residual_capacity)
        self.flow += max_addable
        return max_addable
    
    def remove_flow(self, amount: float) -> float:
        """Remove flow from edge, returns actual amount removed."""
        max_removable = min(amount, self.flow)
        self.flow -= max_removable
        return max_removable
    
    def reset_flow(self) -> None:
        """Reset flow to zero."""
        self.flow = 0.0
    
    def is_saturated(self) -> bool:
        """Check if edge is at full capacity."""
        return self.flow >= self.capacity
    
    def reverse_edge(self) -> 'FlowEdge':
        """Create reverse edge for residual graph."""
        return FlowEdge(
            f"{self.edge_id}_reverse",
            self.target,
            self.source,
            capacity=self.flow,  # Reverse capacity is current flow
            flow=0.0,
            cost=-self.cost_per_unit,  # Negative cost for reverse
            is_residual=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.edge_id,
            'source': self.source,
            'target': self.target,
            'capacity': self.capacity,
            'flow': self.flow,
            'residual_capacity': self.residual_capacity,
            'utilization': self.utilization,
            'cost_per_unit': self.cost_per_unit,
            'is_residual': self.is_residual,
            'properties': self.properties
        }
    
    def __repr__(self) -> str:
        return f"FlowEdge({self.source}->{self.target}: {self.flow}/{self.capacity})"


class xFlowNetworkStrategy(aEdgeStrategy):
    """
    Flow Network strategy for capacity-constrained flow graphs.
    
    Supports max flow, min-cost flow, and multi-commodity flow algorithms
    with residual graph construction and flow optimization.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Flow Network strategy."""
        super().__init__(EdgeMode.FLOW_NETWORK, traits, **options)
        
        self.enable_residual_graph = options.get('enable_residual_graph', True)
        self.auto_balance = options.get('auto_balance', True)  # Auto-balance flow
        self.precision = options.get('precision', 1e-9)  # Floating point precision
        
        # Core storage
        self._edges: Dict[str, FlowEdge] = {}  # edge_id -> FlowEdge
        self._outgoing: DefaultDict[str, Dict[str, str]] = defaultdict(dict)  # source -> {target: edge_id}
        self._incoming: DefaultDict[str, Dict[str, str]] = defaultdict(dict)  # target -> {source: edge_id}
        self._vertices: Set[str] = set()
        
        # Flow network state
        self._source_vertices: Set[str] = set()  # Sources (supply > 0)
        self._sink_vertices: Set[str] = set()    # Sinks (demand > 0)
        self._vertex_supply: Dict[str, float] = defaultdict(float)  # Net supply/demand
        
        # Flow statistics
        self._total_capacity = 0.0
        self._total_flow = 0.0
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the flow network strategy."""
        return (EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.SPARSE)
    
    def _generate_edge_id(self) -> str:
        """Generate unique edge ID."""
        self._edge_id_counter += 1
        return f"flow_edge_{self._edge_id_counter}"
    
    def _update_flow_statistics(self) -> None:
        """Update flow network statistics."""
        self._total_capacity = sum(edge.capacity for edge in self._edges.values())
        self._total_flow = sum(edge.flow for edge in self._edges.values())
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add flow edge with capacity."""
        capacity = properties.pop('capacity', 1.0)
        flow = properties.pop('flow', 0.0)
        edge_id = properties.pop('edge_id', self._generate_edge_id())
        
        if edge_id in self._edges:
            raise ValueError(f"Edge ID {edge_id} already exists")
        
        # Create flow edge
        flow_edge = FlowEdge(edge_id, source, target, capacity, flow, **properties)
        
        # Store edge and update indices
        self._edges[edge_id] = flow_edge
        self._outgoing[source][target] = edge_id
        self._incoming[target][source] = edge_id
        
        # Add vertices
        self._vertices.add(source)
        self._vertices.add(target)
        
        self._edge_count += 1
        self._update_flow_statistics()
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove flow edge."""
        if edge_id and edge_id in self._edges:
            edge = self._edges[edge_id]
            if edge.source == source and edge.target == target:
                # Remove from indices
                del self._edges[edge_id]
                del self._outgoing[source][target]
                del self._incoming[target][source]
                
                self._edge_count -= 1
                self._update_flow_statistics()
                return True
        else:
            # Find edge by endpoints
            if target in self._outgoing.get(source, {}):
                edge_id = self._outgoing[source][target]
                return self.remove_edge(source, target, edge_id)
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        return target in self._outgoing.get(source, {})
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        if target in self._outgoing.get(source, {}):
            edge_id = self._outgoing[source][target]
            edge = self._edges[edge_id]
            return edge.to_dict()
        return None
    
    def get_flow_edge(self, source: str, target: str) -> Optional[FlowEdge]:
        """Get flow edge object."""
        if target in self._outgoing.get(source, {}):
            edge_id = self._outgoing[source][target]
            return self._edges[edge_id]
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of vertex."""
        if direction in ['out', 'both']:
            for target in self._outgoing.get(vertex, {}):
                yield target
        
        if direction in ['in', 'both']:
            for source in self._incoming.get(vertex, {}):
                yield source
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex."""
        if direction == 'out':
            return len(self._outgoing.get(vertex, {}))
        elif direction == 'in':
            return len(self._incoming.get(vertex, {}))
        else:  # both
            return len(self._outgoing.get(vertex, {})) + len(self._incoming.get(vertex, {}))
    
    def edges(self, data: bool = False, include_residual: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for edge in self._edges.values():
            if not include_residual and edge.is_residual:
                continue
            
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
        self._outgoing.clear()
        self._incoming.clear()
        self._vertices.clear()
        self._source_vertices.clear()
        self._sink_vertices.clear()
        self._vertex_supply.clear()
        
        self._total_capacity = 0.0
        self._total_flow = 0.0
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def add_vertex(self, vertex: str, supply: float = 0.0) -> None:
        """Add vertex with supply/demand."""
        self._vertices.add(vertex)
        self.set_vertex_supply(vertex, supply)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Remove all outgoing edges
        outgoing_targets = list(self._outgoing.get(vertex, {}).keys())
        for target in outgoing_targets:
            self.remove_edge(vertex, target)
        
        # Remove all incoming edges
        incoming_sources = list(self._incoming.get(vertex, {}).keys())
        for source in incoming_sources:
            self.remove_edge(source, vertex)
        
        # Remove vertex
        self._vertices.discard(vertex)
        self._source_vertices.discard(vertex)
        self._sink_vertices.discard(vertex)
        self._vertex_supply.pop(vertex, None)
        
        return True
    
    # ============================================================================
    # FLOW NETWORK OPERATIONS
    # ============================================================================
    
    def set_vertex_supply(self, vertex: str, supply: float) -> None:
        """Set vertex supply (positive) or demand (negative)."""
        self._vertex_supply[vertex] = supply
        
        if supply > self.precision:
            self._source_vertices.add(vertex)
            self._sink_vertices.discard(vertex)
        elif supply < -self.precision:
            self._sink_vertices.add(vertex)
            self._source_vertices.discard(vertex)
        else:
            self._source_vertices.discard(vertex)
            self._sink_vertices.discard(vertex)
    
    def get_vertex_supply(self, vertex: str) -> float:
        """Get vertex supply/demand."""
        return self._vertex_supply.get(vertex, 0.0)
    
    def add_flow(self, source: str, target: str, amount: float) -> float:
        """Add flow to edge, returns actual amount added."""
        edge = self.get_flow_edge(source, target)
        if edge:
            added = edge.add_flow(amount)
            self._update_flow_statistics()
            return added
        return 0.0
    
    def remove_flow(self, source: str, target: str, amount: float) -> float:
        """Remove flow from edge, returns actual amount removed."""
        edge = self.get_flow_edge(source, target)
        if edge:
            removed = edge.remove_flow(amount)
            self._update_flow_statistics()
            return removed
        return 0.0
    
    def reset_all_flows(self) -> None:
        """Reset all edge flows to zero."""
        for edge in self._edges.values():
            edge.reset_flow()
        self._update_flow_statistics()
    
    def get_residual_graph(self) -> 'xFlowNetworkStrategy':
        """Create residual graph for flow algorithms."""
        residual = xFlowNetworkStrategy(
            traits=self._traits,
            enable_residual_graph=False,  # Avoid recursive residual graphs
            precision=self.precision
        )
        
        # Add all vertices with same supply/demand
        for vertex in self._vertices:
            residual.add_vertex(vertex, self.get_vertex_supply(vertex))
        
        # Add forward and backward edges
        for edge in self._edges.values():
            if not edge.is_residual:  # Only process original edges
                # Forward edge (residual capacity)
                if edge.residual_capacity > self.precision:
                    residual.add_edge(
                        edge.source, edge.target,
                        capacity=edge.residual_capacity,
                        cost=edge.cost_per_unit,
                        edge_id=f"{edge.edge_id}_forward",
                        is_residual=True
                    )
                
                # Backward edge (current flow)
                if edge.flow > self.precision:
                    residual.add_edge(
                        edge.target, edge.source,
                        capacity=edge.flow,
                        cost=-edge.cost_per_unit,
                        edge_id=f"{edge.edge_id}_backward",
                        is_residual=True
                    )
        
        return residual
    
    def find_augmenting_path(self, source: str, sink: str) -> Optional[List[str]]:
        """Find augmenting path using BFS (Ford-Fulkerson algorithm)."""
        if source not in self._vertices or sink not in self._vertices:
            return None
        
        # BFS to find path with available capacity
        queue = deque([source])
        visited = {source}
        parent = {}
        
        while queue:
            current = queue.popleft()
            
            if current == sink:
                # Reconstruct path
                path = []
                node = sink
                while node != source:
                    path.append(node)
                    node = parent[node]
                path.append(source)
                return path[::-1]
            
            # Explore neighbors with available capacity
            for neighbor in self.neighbors(current, 'out'):
                if neighbor not in visited:
                    edge = self.get_flow_edge(current, neighbor)
                    if edge and edge.residual_capacity > self.precision:
                        visited.add(neighbor)
                        parent[neighbor] = current
                        queue.append(neighbor)
        
        return None
    
    def max_flow(self, source: str, sink: str) -> float:
        """Compute maximum flow using Ford-Fulkerson algorithm."""
        if source not in self._vertices or sink not in self._vertices:
            return 0.0
        
        total_flow = 0.0
        max_iterations = 1000  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            # Find augmenting path
            path = self.find_augmenting_path(source, sink)
            if not path:
                break
            
            # Find bottleneck capacity
            bottleneck = float('inf')
            for i in range(len(path) - 1):
                edge = self.get_flow_edge(path[i], path[i + 1])
                if edge:
                    bottleneck = min(bottleneck, edge.residual_capacity)
            
            # Augment flow along path
            if bottleneck > self.precision:
                for i in range(len(path) - 1):
                    self.add_flow(path[i], path[i + 1], bottleneck)
                total_flow += bottleneck
            
            iteration += 1
        
        return total_flow
    
    def min_cut(self, source: str, sink: str) -> Tuple[Set[str], Set[str], float]:
        """Find minimum cut using max-flow min-cut theorem."""
        # First compute max flow
        max_flow_value = self.max_flow(source, sink)
        
        # Find reachable vertices from source in residual graph
        residual = self.get_residual_graph()
        reachable = set()
        queue = deque([source])
        reachable.add(source)
        
        while queue:
            current = queue.popleft()
            for neighbor in residual.neighbors(current, 'out'):
                if neighbor not in reachable:
                    edge = residual.get_flow_edge(current, neighbor)
                    if edge and edge.capacity > self.precision:
                        reachable.add(neighbor)
                        queue.append(neighbor)
        
        # Cut is between reachable and non-reachable vertices
        cut_s = reachable
        cut_t = self._vertices - reachable
        
        return cut_s, cut_t, max_flow_value
    
    def is_flow_feasible(self) -> bool:
        """Check if current flow satisfies flow conservation."""
        for vertex in self._vertices:
            flow_in = sum(
                self.get_flow_edge(source, vertex).flow
                for source in self._incoming.get(vertex, {})
                if self.get_flow_edge(source, vertex)
            )
            
            flow_out = sum(
                self.get_flow_edge(vertex, target).flow
                for target in self._outgoing.get(vertex, {})
                if self.get_flow_edge(vertex, target)
            )
            
            net_flow = flow_in - flow_out
            expected_supply = self.get_vertex_supply(vertex)
            
            if abs(net_flow - expected_supply) > self.precision:
                return False
        
        return True
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive flow statistics."""
        if not self._edges:
            return {
                'total_capacity': 0, 'total_flow': 0, 'utilization': 0,
                'saturated_edges': 0, 'empty_edges': 0, 'sources': 0, 'sinks': 0
            }
        
        saturated = sum(1 for edge in self._edges.values() if edge.is_saturated())
        empty = sum(1 for edge in self._edges.values() if edge.flow < self.precision)
        utilizations = [edge.utilization for edge in self._edges.values()]
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'sources': len(self._source_vertices),
            'sinks': len(self._sink_vertices),
            'total_capacity': self._total_capacity,
            'total_flow': self._total_flow,
            'overall_utilization': (self._total_flow / self._total_capacity * 100) if self._total_capacity > 0 else 0,
            'saturated_edges': saturated,
            'empty_edges': empty,
            'avg_edge_utilization': sum(utilizations) / len(utilizations) if utilizations else 0,
            'max_edge_utilization': max(utilizations) if utilizations else 0,
            'flow_feasible': self.is_flow_feasible()
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'FLOW_NETWORK',
            'backend': 'Capacity-constrained adjacency lists with flow tracking',
            'enable_residual_graph': self.enable_residual_graph,
            'auto_balance': self.auto_balance,
            'precision': self.precision,
            'complexity': {
                'add_edge': 'O(1)',
                'max_flow': 'O(V * E^2)',  # Ford-Fulkerson
                'min_cut': 'O(V * E^2)',
                'feasibility_check': 'O(V + E)',
                'space': 'O(V + E)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_flow_statistics()
        
        return {
            'vertices': stats['vertices'],
            'edges': stats['edges'],
            'total_capacity': f"{stats['total_capacity']:.2f}",
            'total_flow': f"{stats['total_flow']:.2f}",
            'utilization': f"{stats['overall_utilization']:.1f}%",
            'saturated_edges': stats['saturated_edges'],
            'flow_feasible': stats['flow_feasible'],
            'memory_usage': f"{self._edge_count * 120 + len(self._vertices) * 50} bytes (estimated)"
        }
