"""
#exonware/xwnode/src/exonware/xwnode/strategies/advisor.py

Strategy Advisor

This module provides the StrategyAdvisor class for intelligent strategy selection,
performance monitoring, and optimization recommendations in the strategy system.
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass
from collections import defaultdict, deque
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

from ..types import NodeMode, EdgeMode, NodeTrait, EdgeTrait, NODE_STRATEGY_METADATA, EDGE_STRATEGY_METADATA


@dataclass
class StrategyRecommendation:
    """A strategy recommendation with rationale and estimated gain."""
    mode: NodeMode | EdgeMode
    rationale: str
    estimated_gain_percent: float
    confidence: float
    migration_cost: str
    data_loss_risk: bool


@dataclass
class PerformanceMetrics:
    """Performance metrics for strategy monitoring."""
    operation_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    memory_usage: float = 0.0
    last_updated: float = 0.0
    
    def update(self, operation_time: float, memory_usage: float = 0.0):
        """Update metrics with new operation data."""
        self.operation_count += 1
        self.total_time += operation_time
        self.avg_time = self.total_time / self.operation_count
        self.min_time = min(self.min_time, operation_time)
        self.max_time = max(self.max_time, operation_time)
        self.memory_usage = memory_usage
        self.last_updated = time.time()


class StrategyAdvisor:
    """
    Intelligent advisor for strategy selection and optimization.
    
    This class provides:
    - Performance monitoring and metrics collection
    - Intelligent strategy recommendations
    - Migration cost analysis
    - Heuristic-based mode selection
    """
    
    def __init__(self, history_size: int = 1000):
        """Initialize the strategy advisor."""
        self.history_size = history_size
        self._node_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._edge_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._operation_history: deque = deque(maxlen=history_size)
        self._lock = threading.RLock()
        
        # Heuristic thresholds
        self._thresholds = {
            'small_dataset': 100,
            'medium_dataset': 10000,
            'large_dataset': 1000000,
            'sparse_graph': 0.02,
            'dense_graph': 0.15,
            'high_churn': 0.1,
            'write_heavy': 0.7,
            'lookup_heavy': 0.7,
            'ordered_heavy': 0.2,
            'prefix_heavy': 0.1,
            'priority_heavy': 0.2,
            'spatial_heavy': 0.1,
            'temporal_heavy': 0.1,
        }
    
    def record_operation(self, strategy_id: str, operation: str, 
                        duration: float, memory_usage: float = 0.0,
                        is_node: bool = True) -> None:
        """
        Record an operation for performance monitoring.
        
        Args:
            strategy_id: Unique identifier for the strategy
            operation: Operation name (e.g., 'get', 'set', 'add_edge')
            duration: Operation duration in seconds
            memory_usage: Memory usage in bytes
            is_node: Whether this is a node or edge operation
        """
        with self._lock:
            metrics = self._node_metrics if is_node else self._edge_metrics
            key = f"{strategy_id}:{operation}"
            metrics[key].update(duration, memory_usage)
            
            # Record in history
            self._operation_history.append({
                'timestamp': time.time(),
                'strategy_id': strategy_id,
                'operation': operation,
                'duration': duration,
                'memory_usage': memory_usage,
                'is_node': is_node
            })
    
    def get_performance_profile(self, strategy_id: str, is_node: bool = True) -> Dict[str, Any]:
        """
        Get performance profile for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            is_node: Whether this is a node or edge strategy
            
        Returns:
            Performance profile dictionary
        """
        with self._lock:
            metrics = self._node_metrics if is_node else self._edge_metrics
            
            profile = {
                'strategy_id': strategy_id,
                'is_node': is_node,
                'operations': {},
                'overall': {
                    'total_operations': 0,
                    'avg_duration': 0.0,
                    'total_duration': 0.0,
                    'memory_usage': 0.0
                }
            }
            
            total_ops = 0
            total_duration = 0.0
            total_memory = 0.0
            
            for key, metric in metrics.items():
                if key.startswith(f"{strategy_id}:"):
                    operation = key.split(":", 1)[1]
                    profile['operations'][operation] = {
                        'count': metric.operation_count,
                        'avg_time': metric.avg_time,
                        'min_time': metric.min_time,
                        'max_time': metric.max_time,
                        'total_time': metric.total_time,
                        'memory_usage': metric.memory_usage,
                        'last_updated': metric.last_updated
                    }
                    
                    total_ops += metric.operation_count
                    total_duration += metric.total_time
                    total_memory = max(total_memory, metric.memory_usage)
            
            if total_ops > 0:
                profile['overall']['total_operations'] = total_ops
                profile['overall']['total_duration'] = total_duration
                profile['overall']['avg_duration'] = total_duration / total_ops
                profile['overall']['memory_usage'] = total_memory
            
            return profile
    
    def suggest_node_strategy(self, data_profile: Dict[str, Any], 
                            current_mode: Optional[NodeMode] = None) -> StrategyRecommendation:
        """
        Suggest optimal node strategy based on data profile.
        
        Args:
            data_profile: Profile of the data and usage patterns
            current_mode: Current strategy mode (if any)
            
        Returns:
            Strategy recommendation
        """
        size = data_profile.get('size', 0)
        operations = data_profile.get('operations', {})
        total_ops = sum(operations.values()) if operations else 0
        
        # Calculate operation ratios
        if total_ops > 0:
            lookup_ratio = operations.get('get', 0) / total_ops
            insert_ratio = operations.get('set', 0) / total_ops
            ordered_ratio = operations.get('ordered_ops', 0) / total_ops
            range_ratio = operations.get('range_ops', 0) / total_ops
            prefix_ratio = operations.get('prefix_ops', 0) / total_ops
            priority_ratio = operations.get('priority_ops', 0) / total_ops
        else:
            lookup_ratio = insert_ratio = ordered_ratio = range_ratio = prefix_ratio = priority_ratio = 0.0
        
        # Decision logic based on heuristics
        if data_profile.get('persistent', False):
            if range_ratio > self._thresholds['ordered_heavy']:
                mode = NodeMode.B_PLUS_TREE
                rationale = f"Persistent data with {range_ratio:.1%} range operations"
                gain = 50.0
            else:
                mode = NodeMode.B_TREE
                rationale = f"Persistent data storage"
                gain = 30.0
        
        elif data_profile.get('write_heavy', False) or insert_ratio > self._thresholds['write_heavy']:
            mode = NodeMode.LSM_TREE
            rationale = f"Write-heavy workload ({insert_ratio:.1%} inserts)"
            gain = 80.0
        
        elif range_ratio > self._thresholds['ordered_heavy']:
            if data_profile.get('updates', False):
                mode = NodeMode.SEGMENT_TREE
                rationale = f"Range operations with updates ({range_ratio:.1%})"
                gain = 60.0
            else:
                mode = NodeMode.FENWICK_TREE
                rationale = f"Range queries ({range_ratio:.1%})"
                gain = 40.0
        
        elif prefix_ratio > self._thresholds['prefix_heavy']:
            if data_profile.get('binary', False):
                mode = NodeMode.PATRICIA
                rationale = f"Binary prefix operations ({prefix_ratio:.1%})"
                gain = 50.0
            else:
                mode = NodeMode.RADIX_TRIE
                rationale = f"String prefix operations ({prefix_ratio:.1%})"
                gain = 40.0
        
        elif priority_ratio > self._thresholds['priority_heavy']:
            mode = NodeMode.HEAP
            rationale = f"Priority operations ({priority_ratio:.1%})"
            gain = 30.0
        
        elif lookup_ratio > self._thresholds['lookup_heavy']:
            if size > self._thresholds['large_dataset']:
                mode = NodeMode.HASH_MAP
                rationale = f"High lookup ratio ({lookup_ratio:.1%}) with large dataset"
                gain = 70.0
            else:
                mode = NodeMode.ARRAY_LIST
                rationale = f"High lookup ratio ({lookup_ratio:.1%}) with small dataset"
                gain = 20.0
        
        elif data_profile.get('connectivity', False):
            mode = NodeMode.UNION_FIND
            rationale = "Connectivity/disjoint set operations"
            gain = 60.0
        
        elif data_profile.get('streaming', False):
            if data_profile.get('frequency', False):
                mode = NodeMode.COUNT_MIN_SKETCH
                rationale = "Streaming frequency estimation"
                gain = 90.0
            else:
                mode = NodeMode.HYPERLOGLOG
                rationale = "Streaming cardinality estimation"
                gain = 85.0
        
        elif size < self._thresholds['small_dataset']:
            mode = NodeMode.ARRAY_LIST
            rationale = f"Small dataset ({size} items)"
            gain = 15.0
        
        elif ordered_ratio > self._thresholds['ordered_heavy']:
            mode = NodeMode.ORDERED_MAP_BALANCED
            rationale = f"Ordered operations ({ordered_ratio:.1%})"
            gain = 25.0
        
        else:
            mode = NodeMode.HASH_MAP
            rationale = "General purpose hash map"
            gain = 20.0
        
        # Calculate migration cost
        migration_cost = self._calculate_migration_cost(current_mode, mode, is_node=True)
        data_loss_risk = self._assess_data_loss_risk(current_mode, mode, is_node=True)
        
        return StrategyRecommendation(
            mode=mode,
            rationale=rationale,
            estimated_gain_percent=gain,
            confidence=0.8,
            migration_cost=migration_cost,
            data_loss_risk=data_loss_risk
        )
    
    def suggest_edge_strategy(self, graph_profile: Dict[str, Any],
                            current_mode: Optional[EdgeMode] = None) -> StrategyRecommendation:
        """
        Suggest optimal edge strategy based on graph profile.
        
        Args:
            graph_profile: Profile of the graph and usage patterns
            current_mode: Current strategy mode (if any)
            
        Returns:
            Strategy recommendation
        """
        n = graph_profile.get('vertices', 0)
        m = graph_profile.get('edges', 0)
        density = m / (n * n) if n > 0 else 0
        
        # Graph characteristics
        is_spatial = graph_profile.get('spatial', False)
        is_temporal = graph_profile.get('temporal', False)
        is_hyper = graph_profile.get('hyper', False)
        is_undirected = graph_profile.get('undirected', False)
        high_churn = graph_profile.get('high_churn', False)
        
        # Decision logic
        if is_hyper:
            mode = EdgeMode.HYPEREDGE_SET
            rationale = "Hypergraph with multi-vertex edges"
            gain = 40.0
        
        elif is_temporal:
            mode = EdgeMode.TEMPORAL_EDGESET
            rationale = "Time-aware edge storage"
            gain = 50.0
        
        elif is_spatial:
            dims = graph_profile.get('dimensions', 2)
            if dims == 2:
                mode = EdgeMode.QUADTREE
                rationale = "2D spatial partitioning"
                gain = 60.0
            elif dims == 3:
                mode = EdgeMode.OCTREE
                rationale = "3D spatial partitioning"
                gain = 60.0
            else:
                mode = EdgeMode.R_TREE
                rationale = "Spatial indexing for arbitrary dimensions"
                gain = 50.0
        
        elif is_undirected:
            mode = EdgeMode.BIDIR_WRAPPER
            rationale = "Undirected graph via bidirectional wrapper"
            gain = 30.0
        
        elif high_churn:
            mode = EdgeMode.DYNAMIC_ADJ_LIST
            rationale = "High churn graph with frequent updates"
            gain = 45.0
        
        elif density <= self._thresholds['sparse_graph']:
            mode = EdgeMode.CSR
            rationale = f"Sparse graph (density: {density:.3f})"
            gain = 35.0
        
        elif density <= self._thresholds['dense_graph']:
            mode = EdgeMode.ADJ_LIST
            rationale = f"Medium density graph (density: {density:.3f})"
            gain = 25.0
        
        else:
            mode = EdgeMode.BLOCK_ADJ_MATRIX
            rationale = f"Dense graph (density: {density:.3f}) with cache optimization"
            gain = 40.0
        
        # Calculate migration cost
        migration_cost = self._calculate_migration_cost(current_mode, mode, is_node=False)
        data_loss_risk = self._assess_data_loss_risk(current_mode, mode, is_node=False)
        
        return StrategyRecommendation(
            mode=mode,
            rationale=rationale,
            estimated_gain_percent=gain,
            confidence=0.8,
            migration_cost=migration_cost,
            data_loss_risk=data_loss_risk
        )
    
    def _calculate_migration_cost(self, from_mode: Optional[NodeMode | EdgeMode], 
                                to_mode: NodeMode | EdgeMode, is_node: bool) -> str:
        """Calculate the cost of migrating between strategies."""
        if from_mode is None:
            return "low"
        
        # Define migration cost matrix
        if is_node:
            cost_matrix = {
                NodeMode.ARRAY_LIST: {NodeMode.ORDERED_MAP: "medium", NodeMode.HASH_MAP: "medium"},
                NodeMode.ORDERED_MAP: {NodeMode.ORDERED_MAP_BALANCED: "low", NodeMode.B_TREE: "medium"},
                NodeMode.TRIE: {NodeMode.RADIX_TRIE: "low", NodeMode.PATRICIA: "low"},
                NodeMode.BITMAP: {NodeMode.BITSET_DYNAMIC: "low", NodeMode.ROARING_BITMAP: "medium"},
            }
        else:
            cost_matrix = {
                EdgeMode.ADJ_LIST: {EdgeMode.DYNAMIC_ADJ_LIST: "low", EdgeMode.CSR: "medium"},
                EdgeMode.ADJ_MATRIX: {EdgeMode.BLOCK_ADJ_MATRIX: "low"},
                EdgeMode.QUADTREE: {EdgeMode.OCTREE: "low", EdgeMode.R_TREE: "medium"},
            }
        
        # Check if migration is in cost matrix
        if from_mode in cost_matrix and to_mode in cost_matrix[from_mode]:
            return cost_matrix[from_mode][to_mode]
        
        # Default cost based on mode types
        if from_mode == to_mode:
            return "none"
        elif is_node and (from_mode in [NodeMode.ARRAY_LIST, NodeMode.LINKED_LIST] and 
                         to_mode in [NodeMode.HASH_MAP, NodeMode.ORDERED_MAP]):
            return "medium"
        elif not is_node and (from_mode in [EdgeMode.ADJ_LIST, EdgeMode.ADJ_MATRIX] and
                             to_mode in [EdgeMode.CSR, EdgeMode.CSC]):
            return "medium"
        else:
            return "high"
    
    def _assess_data_loss_risk(self, from_mode: Optional[NodeMode | EdgeMode],
                              to_mode: NodeMode | EdgeMode, is_node: bool) -> bool:
        """Assess risk of data loss during migration."""
        if from_mode is None:
            return False
        
        # Define lossy migrations
        if is_node:
            lossy_migrations = [
                (NodeMode.ORDERED_MAP, NodeMode.HASH_MAP),  # Order loss
                (NodeMode.TRIE, NodeMode.HASH_MAP),         # Prefix structure loss
                (NodeMode.HEAP, NodeMode.HASH_MAP),         # Priority order loss
                (NodeMode.BLOOM_FILTER, NodeMode.HASH_MAP), # Probabilistic nature loss
            ]
        else:
            lossy_migrations = [
                (EdgeMode.HYPEREDGE_SET, EdgeMode.ADJ_LIST), # Hyperedge structure loss
                (EdgeMode.TEMPORAL_EDGESET, EdgeMode.ADJ_LIST), # Temporal info loss
                (EdgeMode.BIDIR_WRAPPER, EdgeMode.ADJ_LIST), # Bidirectional info loss
            ]
        
        return (from_mode, to_mode) in lossy_migrations
    
    def get_advisor_stats(self) -> Dict[str, Any]:
        """Get advisor statistics."""
        with self._lock:
            return {
                'history_size': len(self._operation_history),
                'node_metrics_count': len(self._node_metrics),
                'edge_metrics_count': len(self._edge_metrics),
                'thresholds': self._thresholds.copy(),
                'last_operation': self._operation_history[-1] if self._operation_history else None
            }


# Global advisor instance
_advisor = None


def get_advisor() -> StrategyAdvisor:
    """Get the global strategy advisor instance."""
    global _advisor
    if _advisor is None:
        _advisor = StrategyAdvisor()
    return _advisor
