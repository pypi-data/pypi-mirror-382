"""
#exonware/xwnode/src/exonware/xwnode/strategies/registry.py

Strategy Registry

This module provides the StrategyRegistry class for managing strategy registration,
discovery, and instantiation in the strategy system.
"""

import threading
from typing import Dict, Type, List, Optional, Any, Callable
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

from ..types import NodeMode, EdgeMode, NodeTrait, EdgeTrait, NODE_STRATEGY_METADATA, EDGE_STRATEGY_METADATA, QueryMode, QueryTrait
from ..errors import XWNodeStrategyError, XWNodeError


class StrategyRegistry:
    """
    Central registry for managing strategy implementations.
    
    This class provides thread-safe registration and discovery of strategy
    implementations for both nodes and edges in the strategy system.
    """
    
    def __init__(self):
        """Initialize the strategy registry."""
        self._node_strategies: Dict[NodeMode, Type] = {}
        self._edge_strategies: Dict[EdgeMode, Type] = {}
        self._query_strategies: Dict[str, Type] = {}
        self._node_factories: Dict[NodeMode, Callable] = {}
        self._edge_factories: Dict[EdgeMode, Callable] = {}
        self._query_factories: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        
        # Register default strategies
        self._register_default_strategies()
        self._register_default_query_strategies()
    
    def _register_default_strategies(self):
        """Register default strategy implementations."""
        # Import default strategies
        from .impls.edge_adj_list import xAdjListStrategy
        from .impls.edge_adj_matrix import xAdjMatrixStrategy
        from .impls.edge_csr import xCSRStrategy
        from .impls.edge_dynamic_adj_list import xDynamicAdjListStrategy
        from .impls.edge_temporal_edgeset import xTemporalEdgeSetStrategy
        from .impls.edge_hyperedge_set import xHyperEdgeSetStrategy
        from .impls.edge_rtree import xRTreeStrategy
        from .impls.edge_flow_network import xFlowNetworkStrategy
        from .impls.edge_neural_graph import xNeuralGraphStrategy
        from .impls.edge_csc import xCSCStrategy
        from .impls.edge_bidir_wrapper import xBidirWrapperStrategy
        from .impls.edge_quadtree import xQuadtreeStrategy
        from .impls.edge_coo import xCOOStrategy
        from .impls.edge_octree import xOctreeStrategy
        from .impls.edge_property_store import xEdgePropertyStoreStrategy
        from .impls.edge_tree_graph_basic import xTreeGraphBasicStrategy
        from .impls.edge_weighted_graph import xWeightedGraphStrategy
        
        # Import new strategy implementations
        from .nodes.node_hash_map import xHashMapStrategy
        from .nodes.node_array_list import xArrayListStrategy
        from .nodes.node_trie import xTrieStrategy
        from .nodes.node_heap import xHeapStrategy
        from .nodes.node_btree import xBTreeStrategy
        from .nodes.node_union_find import xUnionFindStrategy
        from .nodes.node_segment_tree import xSegmentTreeStrategy
        from .nodes.node_lsm_tree import xLSMTreeStrategy
        from .nodes.node_fenwick_tree import xFenwickTreeStrategy
        from .nodes.node_set_hash import xSetHashStrategy
        from .nodes.node_bloom_filter import xBloomFilterStrategy
        from .nodes.node_cuckoo_hash import xCuckooHashStrategy
        from .nodes.node_bitmap import xBitmapStrategy
        from .nodes.node_roaring_bitmap import xRoaringBitmapStrategy
        from .nodes.node_suffix_array import xSuffixArrayStrategy
        from .nodes.node_aho_corasick import xAhoCorasickStrategy
        from .nodes.node_count_min_sketch import xCountMinSketchStrategy
        from .nodes.node_hyperloglog import xHyperLogLogStrategy
        from .nodes.node_set_tree import xSetTreeStrategy
        from .nodes.node_linked_list import xLinkedListStrategy
        from .nodes.node_ordered_map import xOrderedMapStrategy
        from .nodes.node_radix_trie import xRadixTrieStrategy
        from .nodes.node_patricia import xPatriciaStrategy
        from .nodes.node_b_plus_tree import xBPlusTreeStrategy
        from .nodes.node_persistent_tree import xPersistentTreeStrategy
        from .nodes.node_cow_tree import xCOWTreeStrategy
        from .nodes.node_skip_list import xSkipListStrategy
        from .nodes.node_red_black_tree import xRedBlackTreeStrategy
        from .nodes.node_avl_tree import xAVLTreeStrategy
        from .nodes.node_treap import xTreapStrategy
        from .nodes.node_splay_tree import xSplayTreeStrategy
        from .nodes.node_ordered_map_balanced import xOrderedMapBalancedStrategy
        from .nodes.node_bitset_dynamic import xBitsetDynamicStrategy
        from .impls.edge_block_adj_matrix import xBlockAdjMatrixStrategy
        
        # Import data interchange optimized strategy
        from .nodes.node_xdata_optimized import DataInterchangeOptimizedStrategy
        
        # Register tree-graph hybrid strategies
        from .nodes.node_tree_graph_hybrid import TreeGraphHybridStrategy
        self.register_node_strategy(NodeMode.TREE_GRAPH_HYBRID, TreeGraphHybridStrategy)
        
        # Register edge strategies
        self.register_edge_strategy(EdgeMode.ADJ_LIST, xAdjListStrategy)
        self.register_edge_strategy(EdgeMode.ADJ_MATRIX, xAdjMatrixStrategy)
        self.register_edge_strategy(EdgeMode.CSR, xCSRStrategy)
        self.register_edge_strategy(EdgeMode.DYNAMIC_ADJ_LIST, xDynamicAdjListStrategy)
        self.register_edge_strategy(EdgeMode.TEMPORAL_EDGESET, xTemporalEdgeSetStrategy)
        self.register_edge_strategy(EdgeMode.HYPEREDGE_SET, xHyperEdgeSetStrategy)
        self.register_edge_strategy(EdgeMode.R_TREE, xRTreeStrategy)
        self.register_edge_strategy(EdgeMode.FLOW_NETWORK, xFlowNetworkStrategy)
        self.register_edge_strategy(EdgeMode.NEURAL_GRAPH, xNeuralGraphStrategy)
        self.register_edge_strategy(EdgeMode.CSC, xCSCStrategy)
        self.register_edge_strategy(EdgeMode.BIDIR_WRAPPER, xBidirWrapperStrategy)
        self.register_edge_strategy(EdgeMode.QUADTREE, xQuadtreeStrategy)
        self.register_edge_strategy(EdgeMode.COO, xCOOStrategy)
        self.register_edge_strategy(EdgeMode.OCTREE, xOctreeStrategy)
        self.register_edge_strategy(EdgeMode.EDGE_PROPERTY_STORE, xEdgePropertyStoreStrategy)
        self.register_edge_strategy(EdgeMode.TREE_GRAPH_BASIC, xTreeGraphBasicStrategy)
        self.register_edge_strategy(EdgeMode.WEIGHTED_GRAPH, xWeightedGraphStrategy)
        
        # Register new node strategies
        self.register_node_strategy(NodeMode.HASH_MAP, xHashMapStrategy)
        self.register_node_strategy(NodeMode.ARRAY_LIST, xArrayListStrategy)
        self.register_node_strategy(NodeMode.TRIE, xTrieStrategy)
        self.register_node_strategy(NodeMode.HEAP, xHeapStrategy)
        self.register_node_strategy(NodeMode.B_TREE, xBTreeStrategy)
        self.register_node_strategy(NodeMode.UNION_FIND, xUnionFindStrategy)
        self.register_node_strategy(NodeMode.SEGMENT_TREE, xSegmentTreeStrategy)
        self.register_node_strategy(NodeMode.LSM_TREE, xLSMTreeStrategy)
        self.register_node_strategy(NodeMode.FENWICK_TREE, xFenwickTreeStrategy)
        self.register_node_strategy(NodeMode.SET_HASH, xSetHashStrategy)
        self.register_node_strategy(NodeMode.BLOOM_FILTER, xBloomFilterStrategy)
        self.register_node_strategy(NodeMode.CUCKOO_HASH, xCuckooHashStrategy)
        self.register_node_strategy(NodeMode.BITMAP, xBitmapStrategy)
        self.register_node_strategy(NodeMode.ROARING_BITMAP, xRoaringBitmapStrategy)
        self.register_node_strategy(NodeMode.SUFFIX_ARRAY, xSuffixArrayStrategy)
        self.register_node_strategy(NodeMode.AHO_CORASICK, xAhoCorasickStrategy)
        self.register_node_strategy(NodeMode.COUNT_MIN_SKETCH, xCountMinSketchStrategy)
        self.register_node_strategy(NodeMode.HYPERLOGLOG, xHyperLogLogStrategy)
        self.register_node_strategy(NodeMode.SET_TREE, xSetTreeStrategy)
        self.register_node_strategy(NodeMode.LINKED_LIST, xLinkedListStrategy)
        self.register_node_strategy(NodeMode.ORDERED_MAP, xOrderedMapStrategy)
        self.register_node_strategy(NodeMode.RADIX_TRIE, xRadixTrieStrategy)
        self.register_node_strategy(NodeMode.PATRICIA, xPatriciaStrategy)
        self.register_node_strategy(NodeMode.B_PLUS_TREE, xBPlusTreeStrategy)
        self.register_node_strategy(NodeMode.PERSISTENT_TREE, xPersistentTreeStrategy)
        self.register_node_strategy(NodeMode.COW_TREE, xCOWTreeStrategy)
        self.register_node_strategy(NodeMode.SKIP_LIST, xSkipListStrategy)
        self.register_node_strategy(NodeMode.RED_BLACK_TREE, xRedBlackTreeStrategy)
        self.register_node_strategy(NodeMode.AVL_TREE, xAVLTreeStrategy)
        self.register_node_strategy(NodeMode.TREAP, xTreapStrategy)
        self.register_node_strategy(NodeMode.SPLAY_TREE, xSplayTreeStrategy)
        self.register_node_strategy(NodeMode.ORDERED_MAP_BALANCED, xOrderedMapBalancedStrategy)
        self.register_node_strategy(NodeMode.BITSET_DYNAMIC, xBitsetDynamicStrategy)
        
        # Edge strategies
        self.register_edge_strategy(EdgeMode.BLOCK_ADJ_MATRIX, xBlockAdjMatrixStrategy)
        
        # Register data interchange optimized strategy factory
        # Note: This will be used by strategy manager when DATA_INTERCHANGE_OPTIMIZED preset is detected
        self.register_data_interchange_optimized_factory()
        
        logger.info("✅ Registered default strategies")
    
    def _register_default_query_strategies(self):
        """Register default query strategy implementations."""
        # Import query strategies
        from .queries.sql import SQLStrategy
            from .queries.graphql import GraphQLStrategy
            from .queries.cypher import CypherStrategy
            from .queries.sparql import SPARQLStrategy
            from .queries.json_query import JSONQueryStrategy
            from .queries.xml_query import XMLQueryStrategy
            from .queries.xpath import XPathStrategy
            from .queries.xquery import XQueryStrategy
            from .queries.jq import JQStrategy
            from .queries.jmespath import JMESPathStrategy
            from .queries.jsoniq import JSONiqStrategy
            from .queries.gremlin import GremlinStrategy
            from .queries.elastic_dsl import ElasticDSLStrategy
            from .queries.eql import EQLStrategy
            from .queries.flux import FluxStrategy
            from .queries.promql import PromQLStrategy
            from .queries.logql import LogQLStrategy
            # from .queries.spl import SPLStrategy  # TODO: Implement SPL strategy
            from .queries.kql import KQLStrategy
            from .queries.cql import CQLStrategy
            from .queries.n1ql import N1QLStrategy
            from .queries.hiveql import HiveQLStrategy
            from .queries.pig import PigStrategy
            from .queries.mql import MQLStrategy
            from .queries.partiql import PartiQLStrategy
            from .queries.linq import LINQStrategy
            from .queries.hql import HQLStrategy
            from .queries.datalog import DatalogStrategy
            # from .queries.ksql import KSQLStrategy  # TODO: Implement KSQL strategy
            from .queries.gql import GQLStrategy
            # from .queries.trino_sql import TrinoSQLStrategy  # TODO: Implement TrinoSQL strategy
            # from .queries.bigquery_sql import BigQuerySQLStrategy  # TODO: Implement BigQuerySQL strategy
            # from .queries.snowflake_sql import SnowflakeSQLStrategy  # TODO: Implement SnowflakeSQL strategy
            # from .queries.lucene import LuceneStrategy  # TODO: Implement Lucene strategy
            
            # Register query strategies
            self.register_query_strategy("SQL", SQLStrategy)
            self.register_query_strategy("GRAPHQL", GraphQLStrategy)
            self.register_query_strategy("CYPHER", CypherStrategy)
            self.register_query_strategy("SPARQL", SPARQLStrategy)
            self.register_query_strategy("JSON_QUERY", JSONQueryStrategy)
            self.register_query_strategy("XML_QUERY", XMLQueryStrategy)
            self.register_query_strategy("XPATH", XPathStrategy)
            self.register_query_strategy("XQUERY", XQueryStrategy)
            self.register_query_strategy("JQ", JQStrategy)
            self.register_query_strategy("JMESPATH", JMESPathStrategy)
            self.register_query_strategy("JSONIQ", JSONiqStrategy)
            self.register_query_strategy("GREMLIN", GremlinStrategy)
            self.register_query_strategy("ELASTIC_DSL", ElasticDSLStrategy)
            self.register_query_strategy("EQL", EQLStrategy)
            self.register_query_strategy("FLUX", FluxStrategy)
            self.register_query_strategy("PROMQL", PromQLStrategy)
            self.register_query_strategy("LOGQL", LogQLStrategy)
            # self.register_query_strategy("SPL", SPLStrategy)  # TODO: Implement SPL strategy
            self.register_query_strategy("KQL", KQLStrategy)
            self.register_query_strategy("CQL", CQLStrategy)
            self.register_query_strategy("N1QL", N1QLStrategy)
            self.register_query_strategy("HIVEQL", HiveQLStrategy)
            self.register_query_strategy("PIG", PigStrategy)
            self.register_query_strategy("MQL", MQLStrategy)
            self.register_query_strategy("PARTIQL", PartiQLStrategy)
            self.register_query_strategy("LINQ", LINQStrategy)
            self.register_query_strategy("HQL", HQLStrategy)
            self.register_query_strategy("DATALOG", DatalogStrategy)
            # self.register_query_strategy("KSQL", KSQLStrategy)  # TODO: Implement KSQL strategy
            self.register_query_strategy("GQL", GQLStrategy)
            # self.register_query_strategy("TRINO_SQL", TrinoSQLStrategy)  # TODO: Implement TrinoSQL strategy
            # self.register_query_strategy("BIGQUERY_SQL", BigQuerySQLStrategy)  # TODO: Implement BigQuerySQL strategy
            # self.register_query_strategy("SNOWFLAKE_SQL", SnowflakeSQLStrategy)  # TODO: Implement SnowflakeSQL strategy
            # self.register_query_strategy("LUCENE", LuceneStrategy)  # TODO: Implement Lucene strategy
            
            logger.info("✅ Registered default query strategies")
            
        except ImportError as e:
            logger.warning(f"⚠️ Could not register default query strategies: {e}")
    
    def register_data_interchange_optimized_factory(self):
        """Register special factory for DATA_INTERCHANGE_OPTIMIZED preset handling."""
        # We'll store this in a special attribute for the strategy manager to use
        def data_interchange_factory(**options):
            from .nodes.node_xdata_optimized import DataInterchangeOptimizedStrategy
            return DataInterchangeOptimizedStrategy(NodeTrait.INDEXED, **options)
        
        self._data_interchange_optimized_factory = data_interchange_factory
        logger.debug("📝 Registered data interchange optimized strategy factory")
    
    def get_data_interchange_optimized_factory(self):
        """Get the data interchange optimized strategy factory."""
        return getattr(self, '_data_interchange_optimized_factory', None)
    
    def register_node_strategy(self, mode: NodeMode, strategy_class: Type, 
                             factory: Optional[Callable] = None) -> None:
        """
        Register a node strategy implementation.
        
        Args:
            mode: The node mode to register
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._node_strategies[mode] = strategy_class
            if factory:
                self._node_factories[mode] = factory
            
            logger.debug(f"📝 Registered node strategy: {mode.name} -> {strategy_class.__name__}")
    
    def register_edge_strategy(self, mode: EdgeMode, strategy_class: Type,
                             factory: Optional[Callable] = None) -> None:
        """
        Register an edge strategy implementation.
        
        Args:
            mode: The edge mode to register
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._edge_strategies[mode] = strategy_class
            if factory:
                self._edge_factories[mode] = factory
            
            logger.debug(f"📝 Registered edge strategy: {mode.name} -> {strategy_class.__name__}")
    
    def register_query_strategy(self, query_type: str, strategy_class: Type,
                              factory: Optional[Callable] = None) -> None:
        """
        Register a query strategy implementation.
        
        Args:
            query_type: The query type to register (e.g., "SQL", "GRAPHQL")
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._query_strategies[query_type.upper()] = strategy_class
            if factory:
                self._query_factories[query_type.upper()] = factory
            
            logger.debug(f"📝 Registered query strategy: {query_type.upper()} -> {strategy_class.__name__}")
    
    def get_node_strategy(self, mode: NodeMode, **kwargs) -> Any:
        """
        Get a node strategy instance.
        
        Args:
            mode: The node mode to instantiate
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyNotFoundError: If the strategy is not registered
            StrategyInitializationError: If strategy initialization fails
        """
        with self._lock:
            if mode not in self._node_strategies:
                raise XWNodeStrategyError(message=f"Strategy '{mode.name}' not found for node")
            
            strategy_class = self._node_strategies[mode]
            
            try:
                if mode in self._node_factories:
                    return self._node_factories[mode](**kwargs)
                else:
                    # Handle new interface that doesn't accept traits and other arguments
                    if mode == NodeMode.TREE_GRAPH_HYBRID:
                        # For TreeGraphHybridStrategy, ignore traits and other arguments
                        return strategy_class()
                    else:
                        return strategy_class(**kwargs)
                    
            except Exception as e:
                raise XWNodeError(message=f"Failed to initialize strategy '{mode.name}': {e}", cause=e)
    
    def get_node_strategy_class(self, mode: NodeMode) -> Type:
        """
        Get the strategy class for the specified mode.
        
        Args:
            mode: Node mode
            
        Returns:
            Strategy class
            
        Raises:
            XWNodeStrategyError: If strategy not found
        """
        with self._lock:
            if mode not in self._node_strategies:
                raise XWNodeStrategyError(message=f"Strategy '{mode.name}' not found for node")
            
            return self._node_strategies[mode]
    
    def get_edge_strategy(self, mode: EdgeMode, **kwargs) -> Any:
        """
        Get an edge strategy instance.
        
        Args:
            mode: The edge mode to instantiate
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyNotFoundError: If the strategy is not registered
            StrategyInitializationError: If strategy initialization fails
        """
        with self._lock:
            if mode not in self._edge_strategies:
                raise XWNodeStrategyError(message=f"Strategy '{mode.name}' not found for edge")
            
            strategy_class = self._edge_strategies[mode]
            
            try:
                if mode in self._edge_factories:
                    return self._edge_factories[mode](**kwargs)
                else:
                    return strategy_class(**kwargs)
                    
            except Exception as e:
                raise XWNodeError(message=f"Failed to initialize strategy '{mode.name}': {e}", cause=e)
    
    def get_query_strategy(self, query_type: str, **kwargs) -> Any:
        """
        Get a query strategy instance.
        
        Args:
            query_type: The query type to instantiate (e.g., "SQL", "GRAPHQL")
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            XWNodeStrategyError: If the strategy is not registered
            XWNodeError: If strategy initialization fails
        """
        with self._lock:
            query_type_upper = query_type.upper()
            if query_type_upper not in self._query_strategies:
                raise XWNodeStrategyError(message=f"Query strategy '{query_type}' not found")
            
            strategy_class = self._query_strategies[query_type_upper]
            
            try:
                if query_type_upper in self._query_factories:
                    return self._query_factories[query_type_upper](**kwargs)
                else:
                    return strategy_class(**kwargs)
                    
            except Exception as e:
                raise XWNodeError(message=f"Failed to initialize query strategy '{query_type}': {e}", cause=e)
    
    def get_query_strategy_class(self, query_type: str) -> Type:
        """
        Get the query strategy class for the specified type.
        
        Args:
            query_type: Query type
            
        Returns:
            Strategy class
            
        Raises:
            XWNodeStrategyError: If strategy not found
        """
        with self._lock:
            query_type_upper = query_type.upper()
            if query_type_upper not in self._query_strategies:
                raise XWNodeStrategyError(message=f"Query strategy '{query_type}' not found")
            
            return self._query_strategies[query_type_upper]
    
    def list_node_modes(self) -> List[NodeMode]:
        """List all registered node modes."""
        with self._lock:
            return list(self._node_strategies.keys())
    
    def list_edge_modes(self) -> List[EdgeMode]:
        """List all registered edge modes."""
        with self._lock:
            return list(self._edge_strategies.keys())
    
    def list_query_types(self) -> List[str]:
        """List all registered query types."""
        with self._lock:
            return list(self._query_strategies.keys())
    
    def get_node_metadata(self, mode: NodeMode) -> Optional[Any]:
        """Get metadata for a node mode."""
        return NODE_STRATEGY_METADATA.get(mode)
    
    def get_edge_metadata(self, mode: EdgeMode) -> Optional[Any]:
        """Get metadata for an edge mode."""
        return EDGE_STRATEGY_METADATA.get(mode)
    
    def has_node_strategy(self, mode: NodeMode) -> bool:
        """Check if a node strategy is registered."""
        with self._lock:
            return mode in self._node_strategies
    
    def has_edge_strategy(self, mode: EdgeMode) -> bool:
        """Check if an edge strategy is registered."""
        with self._lock:
            return mode in self._edge_strategies
    
    def has_query_strategy(self, query_type: str) -> bool:
        """Check if a query strategy is registered."""
        with self._lock:
            return query_type.upper() in self._query_strategies
    
    def unregister_node_strategy(self, mode: NodeMode) -> bool:
        """
        Unregister a node strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            if mode in self._node_strategies:
                del self._node_strategies[mode]
                if mode in self._node_factories:
                    del self._node_factories[mode]
                logger.debug(f"🗑️ Unregistered node strategy: {mode.name}")
                return True
            return False
    
    def unregister_edge_strategy(self, mode: EdgeMode) -> bool:
        """
        Unregister an edge strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            if mode in self._edge_strategies:
                del self._edge_strategies[mode]
                if mode in self._edge_factories:
                    del self._edge_factories[mode]
                logger.debug(f"🗑️ Unregistered edge strategy: {mode.name}")
                return True
            return False
    
    def unregister_query_strategy(self, query_type: str) -> bool:
        """
        Unregister a query strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            query_type_upper = query_type.upper()
            if query_type_upper in self._query_strategies:
                del self._query_strategies[query_type_upper]
                if query_type_upper in self._query_factories:
                    del self._query_factories[query_type_upper]
                logger.debug(f"🗑️ Unregistered query strategy: {query_type_upper}")
                return True
            return False
    
    def clear_node_strategies(self) -> None:
        """Clear all registered node strategies."""
        with self._lock:
            self._node_strategies.clear()
            self._node_factories.clear()
            logger.info("🗑️ Cleared all node strategies")
    
    def clear_edge_strategies(self) -> None:
        """Clear all registered edge strategies."""
        with self._lock:
            self._edge_strategies.clear()
            self._edge_factories.clear()
            logger.info("🗑️ Cleared all edge strategies")
    
    def clear_query_strategies(self) -> None:
        """Clear all registered query strategies."""
        with self._lock:
            self._query_strategies.clear()
            self._query_factories.clear()
            logger.info("🗑️ Cleared all query strategies")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            return {
                "node_strategies": len(self._node_strategies),
                "edge_strategies": len(self._edge_strategies),
                "query_strategies": len(self._query_strategies),
                "node_factories": len(self._node_factories),
                "edge_factories": len(self._edge_factories),
                "query_factories": len(self._query_factories),
                "registered_node_modes": [mode.name for mode in self._node_strategies.keys()],
                "registered_edge_modes": [mode.name for mode in self._edge_strategies.keys()],
                "registered_query_types": list(self._query_strategies.keys())
            }


# Global registry instance
_registry = None


def get_registry() -> StrategyRegistry:
    """Get the global strategy registry instance."""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry


def register_node_strategy(mode: NodeMode, strategy_class: Type, 
                         factory: Optional[Callable] = None) -> None:
    """Register a node strategy with the global registry."""
    get_registry().register_node_strategy(mode, strategy_class, factory)


def register_edge_strategy(mode: EdgeMode, strategy_class: Type,
                         factory: Optional[Callable] = None) -> None:
    """Register an edge strategy with the global registry."""
    get_registry().register_edge_strategy(mode, strategy_class, factory)


def register_query_strategy(query_type: str, strategy_class: Type,
                          factory: Optional[Callable] = None) -> None:
    """Register a query strategy with the global registry."""
    get_registry().register_query_strategy(query_type, strategy_class, factory)


def get_strategy_registry() -> StrategyRegistry:
    """Get the global strategy registry instance (alias for get_registry)."""
    return get_registry()
