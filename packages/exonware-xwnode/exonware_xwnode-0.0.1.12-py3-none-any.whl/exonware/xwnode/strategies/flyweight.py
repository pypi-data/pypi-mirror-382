#!/usr/bin/env python3
#exonware/xwnode/src/exonware/xwnode/strategies/flyweight.py
"""
Strategy Flyweight Pattern Implementation

Optimizes memory usage by sharing strategy instances with identical configurations.
This prevents creating multiple instances of the same strategy type with the same
configuration, which is especially important for high-throughput applications.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

import threading
import hashlib
import json
from typing import Any, Dict, Hashable, Optional, Type, TypeVar, Union
from weakref import WeakValueDictionary
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

from ..types import NodeMode, EdgeMode, NodeTrait, EdgeTrait
from .nodes.base import ANodeStrategy
from .edges.base import AEdgeStrategy


T = TypeVar('T', bound=Union[ANodeStrategy, AEdgeStrategy])


class StrategyFlyweight:
    """
    Flyweight factory for strategy instances.
    
    Manages shared strategy instances to reduce memory footprint and
    improve performance by avoiding redundant object creation.
    """
    
    def __init__(self):
        """Initialize the flyweight factory."""
        self._node_instances: WeakValueDictionary[str, ANodeStrategy] = WeakValueDictionary()
        self._edge_instances: WeakValueDictionary[str, AEdgeStrategy] = WeakValueDictionary()
        self._lock = threading.RLock()
        self._stats = {
            'node_created': 0,
            'node_reused': 0,
            'edge_created': 0,
            'edge_reused': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'memory_saved_instances': 0
        }
    
    def get_node_strategy(
        self, 
        strategy_class: Type[T],
        mode: NodeMode,
        traits: NodeTrait = NodeTrait.NONE,
        **config: Any
    ) -> T:
        """
        Get a node strategy instance, creating or reusing based on configuration.
        
        Args:
            strategy_class: The strategy class to instantiate
            mode: Node mode for the strategy
            traits: Node traits for the strategy
            **config: Configuration parameters for the strategy
            
        Returns:
            Shared strategy instance
        """
        # Create a hashable key from the class and configuration
        cache_key = self._create_node_cache_key(strategy_class, mode, traits, config)
        
        with self._lock:
            # Check if we already have this instance
            if cache_key in self._node_instances:
                self._stats['cache_hits'] += 1
                self._stats['node_reused'] += 1
                self._stats['memory_saved_instances'] += 1
                logger.debug(f"♻️ Reusing node strategy: {strategy_class.__name__}")
                return self._node_instances[cache_key]
            
            # Create new instance
            self._stats['cache_misses'] += 1
            self._stats['node_created'] += 1
            
            try:
                instance = strategy_class(traits=traits, mode=mode, **config)
                self._node_instances[cache_key] = instance
                logger.debug(f"🆕 Created new node strategy: {strategy_class.__name__}")
                return instance
                
            except Exception as e:
                logger.error(f"❌ Failed to create {strategy_class.__name__} instance: {e}")
                raise
    
    def get_edge_strategy(
        self, 
        strategy_class: Type[T],
        mode: EdgeMode,
        traits: EdgeTrait = EdgeTrait.NONE,
        **config: Any
    ) -> T:
        """
        Get an edge strategy instance, creating or reusing based on configuration.
        
        Args:
            strategy_class: The strategy class to instantiate
            mode: Edge mode for the strategy
            traits: Edge traits for the strategy
            **config: Configuration parameters for the strategy
            
        Returns:
            Shared strategy instance
        """
        # Create a hashable key from the class and configuration
        cache_key = self._create_edge_cache_key(strategy_class, mode, traits, config)
        
        with self._lock:
            # Check if we already have this instance
            if cache_key in self._edge_instances:
                self._stats['cache_hits'] += 1
                self._stats['edge_reused'] += 1
                self._stats['memory_saved_instances'] += 1
                logger.debug(f"♻️ Reusing edge strategy: {strategy_class.__name__}")
                return self._edge_instances[cache_key]
            
            # Create new instance
            self._stats['cache_misses'] += 1
            self._stats['edge_created'] += 1
            
            try:
                instance = strategy_class(traits=traits, mode=mode, **config)
                self._edge_instances[cache_key] = instance
                logger.debug(f"🆕 Created new edge strategy: {strategy_class.__name__}")
                return instance
                
            except Exception as e:
                logger.error(f"❌ Failed to create {strategy_class.__name__} instance: {e}")
                raise
    
    def _create_node_cache_key(
        self, 
        strategy_class: Type[T], 
        mode: NodeMode,
        traits: NodeTrait,
        config: Dict[str, Any]
    ) -> str:
        """
        Create a hashable cache key from class, mode, traits, and configuration.
        
        Args:
            strategy_class: The strategy class
            mode: Node mode
            traits: Node traits
            config: Configuration dictionary
            
        Returns:
            String cache key
        """
        # Start with class name and module
        key_parts = [f"{strategy_class.__module__}.{strategy_class.__name__}"]
        
        # Add mode and traits
        key_parts.append(f"mode:{mode.name}")
        key_parts.append(f"traits:{traits.name}")
        
        # Add configuration (sorted for consistency)
        if config:
            config_str = json.dumps(config, sort_keys=True, default=str)
            key_parts.append(f"config:{config_str}")
        
        # Create hash for shorter key
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _create_edge_cache_key(
        self, 
        strategy_class: Type[T], 
        mode: EdgeMode,
        traits: EdgeTrait,
        config: Dict[str, Any]
    ) -> str:
        """
        Create a hashable cache key from class, mode, traits, and configuration.
        
        Args:
            strategy_class: The strategy class
            mode: Edge mode
            traits: Edge traits
            config: Configuration dictionary
            
        Returns:
            String cache key
        """
        # Start with class name and module
        key_parts = [f"{strategy_class.__module__}.{strategy_class.__name__}"]
        
        # Add mode and traits
        key_parts.append(f"mode:{mode.name}")
        key_parts.append(f"traits:{traits.name}")
        
        # Add configuration (sorted for consistency)
        if config:
            config_str = json.dumps(config, sort_keys=True, default=str)
            key_parts.append(f"config:{config_str}")
        
        # Create hash for shorter key
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get flyweight statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_created = self._stats['node_created'] + self._stats['edge_created']
            total_reused = self._stats['node_reused'] + self._stats['edge_reused']
            total_requests = total_created + total_reused
            
            cache_hit_rate = (self._stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'node_strategies': {
                    'created': self._stats['node_created'],
                    'reused': self._stats['node_reused'],
                    'active': len(self._node_instances)
                },
                'edge_strategies': {
                    'created': self._stats['edge_created'],
                    'reused': self._stats['edge_reused'],
                    'active': len(self._edge_instances)
                },
                'cache_performance': {
                    'hits': self._stats['cache_hits'],
                    'misses': self._stats['cache_misses'],
                    'hit_rate_percent': round(cache_hit_rate, 2),
                    'memory_saved_instances': self._stats['memory_saved_instances']
                },
                'total_instances': {
                    'created': total_created,
                    'reused': total_reused,
                    'active': len(self._node_instances) + len(self._edge_instances)
                }
            }
    
    def clear_cache(self) -> None:
        """Clear all cached strategy instances."""
        with self._lock:
            node_count = len(self._node_instances)
            edge_count = len(self._edge_instances)
            
            self._node_instances.clear()
            self._edge_instances.clear()
            
            logger.info(f"🧹 Cleared flyweight cache: {node_count} node + {edge_count} edge instances")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get detailed cache information.
        
        Returns:
            Dictionary with detailed cache information
        """
        with self._lock:
            return {
                'node_cache_size': len(self._node_instances),
                'edge_cache_size': len(self._edge_instances),
                'total_cache_size': len(self._node_instances) + len(self._edge_instances),
                'node_cache_keys': list(self._node_instances.keys()),
                'edge_cache_keys': list(self._edge_instances.keys())
            }


# Global flyweight instance
_flyweight_instance: Optional[StrategyFlyweight] = None
_flyweight_lock = threading.Lock()


def get_flyweight() -> StrategyFlyweight:
    """
    Get the global strategy flyweight instance.
    
    Returns:
        Global StrategyFlyweight instance
    """
    global _flyweight_instance
    
    if _flyweight_instance is None:
        with _flyweight_lock:
            if _flyweight_instance is None:
                _flyweight_instance = StrategyFlyweight()
                logger.info("🏭 Initialized global strategy flyweight")
    
    return _flyweight_instance


def get_flyweight_stats() -> Dict[str, Any]:
    """
    Get flyweight statistics.
    
    Returns:
        Flyweight statistics dictionary
    """
    return get_flyweight().get_stats()


def clear_flyweight_cache() -> None:
    """Clear the global flyweight cache."""
    get_flyweight().clear_cache()


def get_flyweight_cache_info() -> Dict[str, Any]:
    """
    Get flyweight cache information.
    
    Returns:
        Cache information dictionary
    """
    return get_flyweight().get_cache_info()
