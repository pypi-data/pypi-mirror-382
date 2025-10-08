#!/usr/bin/env python3
#exonware/xwnode/src/exonware/xwnode/strategies/pattern_detector.py
"""
Data Pattern Detector for Strategy Selection

Intelligent pattern detection that analyzes data characteristics to recommend
the optimal strategy for different use cases. This enhances the AUTO mode
selection with sophisticated heuristics.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

import re
import time
import threading
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

from ..types import NodeMode, EdgeMode, NodeTrait, EdgeTrait



class DataPattern(Enum):
    """Data pattern types for strategy selection."""
    SEQUENTIAL_NUMERIC = "sequential_numeric"
    STRING_KEYS = "string_keys"
    MIXED_KEYS = "mixed_keys"
    PREFIX_HEAVY = "prefix_heavy"
    HIERARCHICAL = "hierarchical"
    FLAT_STRUCTURE = "flat_structure"
    LARGE_DATASET = "large_dataset"
    SMALL_DATASET = "small_dataset"
    FREQUENT_UPDATES = "frequent_updates"
    READ_HEAVY = "read_heavy"
    WRITE_HEAVY = "write_heavy"
    TEMPORAL_DATA = "temporal_data"
    SPATIAL_DATA = "spatial_data"
    GRAPH_STRUCTURE = "graph_structure"


@dataclass
class StrategyRecommendation:
    """Strategy recommendation with confidence score."""
    mode: Union[NodeMode, EdgeMode]
    confidence: float
    reasoning: str
    estimated_performance_gain: float
    data_loss_risk: bool
    alternative_modes: List[Union[NodeMode, EdgeMode]]


@dataclass
class DataProfile:
    """Comprehensive data profile for strategy selection."""
    size: int
    depth: int
    key_types: Set[type]
    value_types: Set[type]
    patterns: Set[DataPattern]
    access_pattern: str
    update_frequency: str
    memory_usage_estimate: int
    complexity_score: float


class DataPatternDetector:
    """
    Intelligent data pattern detector that analyzes data characteristics
    to recommend optimal strategies for different use cases.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize pattern detector.
        
        Args:
            confidence_threshold: Minimum confidence level for recommendations
        """
        self._confidence_threshold = confidence_threshold
        self._pattern_weights = self._build_pattern_weights()
        self._strategy_rules = self._build_strategy_rules()
        self._stats = {
            'analyses_performed': 0,
            'recommendations_given': 0,
            'high_confidence_recommendations': 0,
            'average_analysis_time': 0.0
        }
    
    def analyze_data(self, data: Any, **context: Any) -> DataProfile:
        """
        Analyze data and create a comprehensive profile.
        
        Args:
            data: Data to analyze
            **context: Additional context (size, access_pattern, etc.)
            
        Returns:
            DataProfile with analysis results
        """
        start_time = time.time()
        
        try:
            # Basic characteristics
            size = self._calculate_size(data)
            depth = self._calculate_depth(data)
            key_types, value_types = self._analyze_types(data)
            
            # Pattern detection
            patterns = self._detect_patterns(data, context)
            
            # Performance characteristics
            access_pattern = context.get('access_pattern', 'mixed')
            update_frequency = context.get('update_frequency', 'moderate')
            memory_usage = self._estimate_memory_usage(data)
            complexity_score = self._calculate_complexity_score(data, patterns)
            
            profile = DataProfile(
                size=size,
                depth=depth,
                key_types=key_types,
                value_types=value_types,
                patterns=patterns,
                access_pattern=access_pattern,
                update_frequency=update_frequency,
                memory_usage_estimate=memory_usage,
                complexity_score=complexity_score
            )
            
            # Update statistics
            analysis_time = time.time() - start_time
            self._update_stats(analysis_time)
            
            logger.debug(f"🔍 Data analysis completed in {analysis_time:.3f}s: {len(patterns)} patterns detected")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Data analysis failed: {e}")
            # Return minimal profile
            return DataProfile(
                size=0, depth=0, key_types=set(), value_types=set(),
                patterns=set(), access_pattern='unknown', update_frequency='unknown',
                memory_usage_estimate=0, complexity_score=0.0
            )
    
    def recommend_node_strategy(self, profile: DataProfile, **options: Any) -> StrategyRecommendation:
        """
        Recommend optimal node strategy based on data profile.
        
        Args:
            profile: Data profile from analysis
            **options: Additional options for recommendation
            
        Returns:
            Strategy recommendation with confidence score
        """
        recommendations = []
        
        # Apply strategy rules
        for rule in self._strategy_rules['node']:
            confidence = self._evaluate_rule(rule, profile)
            if confidence >= self._confidence_threshold:
                recommendations.append((
                    rule['mode'],
                    confidence,
                    rule['reasoning'],
                    rule.get('performance_gain', 0.0),
                    rule.get('data_loss_risk', False)
                ))
        
        if not recommendations:
            # Fallback to default recommendation
            return StrategyRecommendation(
                mode=NodeMode.HASH_MAP,
                confidence=0.5,
                reasoning="No specific patterns detected, using default hash map strategy",
                estimated_performance_gain=0.0,
                data_loss_risk=False,
                alternative_modes=[NodeMode.ARRAY_LIST, NodeMode.TREE_GRAPH_HYBRID]
            )
        
        # Sort by confidence and select best
        recommendations.sort(key=lambda x: x[1], reverse=True)
        best_mode, best_confidence, reasoning, performance_gain, data_loss_risk = recommendations[0]
        
        # Get alternatives
        alternatives = [rec[0] for rec in recommendations[1:3]]  # Top 2 alternatives
        
        self._stats['recommendations_given'] += 1
        if best_confidence >= 0.8:
            self._stats['high_confidence_recommendations'] += 1
        
        logger.debug(f"🎯 Node strategy recommendation: {best_mode.name} (confidence: {best_confidence:.2f})")
        
        return StrategyRecommendation(
            mode=best_mode,
            confidence=best_confidence,
            reasoning=reasoning,
            estimated_performance_gain=performance_gain,
            data_loss_risk=data_loss_risk,
            alternative_modes=alternatives
        )
    
    def recommend_edge_strategy(self, profile: DataProfile, **options: Any) -> StrategyRecommendation:
        """
        Recommend optimal edge strategy based on data profile.
        
        Args:
            profile: Data profile from analysis
            **options: Additional options for recommendation
            
        Returns:
            Strategy recommendation with confidence score
        """
        recommendations = []
        
        # Apply strategy rules
        for rule in self._strategy_rules['edge']:
            confidence = self._evaluate_rule(rule, profile)
            if confidence >= self._confidence_threshold:
                recommendations.append((
                    rule['mode'],
                    confidence,
                    rule['reasoning'],
                    rule.get('performance_gain', 0.0),
                    rule.get('data_loss_risk', False)
                ))
        
        if not recommendations:
            # Fallback to default recommendation
            return StrategyRecommendation(
                mode=EdgeMode.ADJ_LIST,
                confidence=0.5,
                reasoning="No specific patterns detected, using default adjacency list strategy",
                estimated_performance_gain=0.0,
                data_loss_risk=False,
                alternative_modes=[EdgeMode.ADJ_MATRIX]
            )
        
        # Sort by confidence and select best
        recommendations.sort(key=lambda x: x[1], reverse=True)
        best_mode, best_confidence, reasoning, performance_gain, data_loss_risk = recommendations[0]
        
        # Get alternatives
        alternatives = [rec[0] for rec in recommendations[1:2]]  # Top alternative
        
        self._stats['recommendations_given'] += 1
        if best_confidence >= 0.8:
            self._stats['high_confidence_recommendations'] += 1
        
        logger.debug(f"🎯 Edge strategy recommendation: {best_mode.name} (confidence: {best_confidence:.2f})")
        
        return StrategyRecommendation(
            mode=best_mode,
            confidence=best_confidence,
            reasoning=reasoning,
            estimated_performance_gain=performance_gain,
            data_loss_risk=data_loss_risk,
            alternative_modes=alternatives
        )
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate the size of the data structure."""
        if isinstance(data, (dict, list)):
            return len(data)
        elif hasattr(data, '__len__'):
            return len(data)
        else:
            return 1
    
    def _calculate_depth(self, data: Any, current_depth: int = 0, max_depth: int = 10) -> int:
        """Calculate the maximum nesting depth."""
        if current_depth >= max_depth:
            return current_depth
        
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1, max_depth) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1, max_depth) for item in data)
        else:
            return current_depth
    
    def _analyze_types(self, data: Any) -> Tuple[Set[type], Set[type]]:
        """Analyze key and value types in the data."""
        key_types = set()
        value_types = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                key_types.add(type(key))
                value_types.add(type(value))
        elif isinstance(data, list):
            for item in data:
                value_types.add(type(item))
        else:
            value_types.add(type(data))
        
        return key_types, value_types
    
    def _detect_patterns(self, data: Any, context: Dict[str, Any]) -> Set[DataPattern]:
        """Detect patterns in the data."""
        patterns = set()
        
        if isinstance(data, dict):
            keys = list(data.keys())
            
            # Check for sequential numeric keys
            if self._is_sequential_numeric_keys(keys):
                patterns.add(DataPattern.SEQUENTIAL_NUMERIC)
            
            # Check for string keys
            if all(isinstance(k, str) for k in keys):
                patterns.add(DataPattern.STRING_KEYS)
                
                # Check for prefix patterns
                if self._has_prefix_patterns(keys):
                    patterns.add(DataPattern.PREFIX_HEAVY)
            
            # Check for mixed key types
            if len(set(type(k) for k in keys)) > 1:
                patterns.add(DataPattern.MIXED_KEYS)
            
            # Check for hierarchical structure
            if self._is_hierarchical(data):
                patterns.add(DataPattern.HIERARCHICAL)
            else:
                patterns.add(DataPattern.FLAT_STRUCTURE)
        
        # Size-based patterns
        size = self._calculate_size(data)
        if size > 1000:
            patterns.add(DataPattern.LARGE_DATASET)
        elif size < 100:
            patterns.add(DataPattern.SMALL_DATASET)
        
        # Context-based patterns
        if context.get('update_frequency') == 'high':
            patterns.add(DataPattern.FREQUENT_UPDATES)
        elif context.get('access_pattern') == 'read_heavy':
            patterns.add(DataPattern.READ_HEAVY)
        elif context.get('access_pattern') == 'write_heavy':
            patterns.add(DataPattern.WRITE_HEAVY)
        
        return patterns
    
    def _is_sequential_numeric_keys(self, keys: List[Any]) -> bool:
        """Check if keys are sequential numeric indices."""
        if not keys:
            return False
        
        try:
            # Convert to integers and check if sequential
            int_keys = [int(k) for k in keys if str(k).isdigit()]
            if len(int_keys) != len(keys):
                return False
            
            int_keys.sort()
            return int_keys == list(range(len(int_keys)))
        except (ValueError, TypeError):
            return False
    
    def _has_prefix_patterns(self, keys: List[str]) -> bool:
        """Check if keys have common prefixes."""
        if len(keys) < 3:
            return False
        
        # Find common prefixes
        common_prefixes = set()
        for i, key1 in enumerate(keys):
            for key2 in keys[i+1:]:
                prefix = self._common_prefix(key1, key2)
                if len(prefix) > 2:  # Meaningful prefix
                    common_prefixes.add(prefix)
        
        return len(common_prefixes) > 0
    
    def _common_prefix(self, str1: str, str2: str) -> str:
        """Find common prefix between two strings."""
        prefix = ""
        for i in range(min(len(str1), len(str2))):
            if str1[i] == str2[i]:
                prefix += str1[i]
            else:
                break
        return prefix
    
    def _is_hierarchical(self, data: Any, max_check: int = 5) -> bool:
        """Check if data has hierarchical structure."""
        if not isinstance(data, dict):
            return False
        
        checked = 0
        for value in data.values():
            if checked >= max_check:
                break
            if isinstance(value, (dict, list)):
                return True
            checked += 1
        
        return False
    
    def _estimate_memory_usage(self, data: Any) -> int:
        """Estimate memory usage in bytes."""
        try:
            import sys
            return sys.getsizeof(data)
        except:
            # Fallback estimation
            size = self._calculate_size(data)
            return size * 50  # Rough estimate: 50 bytes per item
    
    def _calculate_complexity_score(self, data: Any, patterns: Set[DataPattern]) -> float:
        """Calculate complexity score (0.0 to 1.0)."""
        score = 0.0
        
        # Base complexity from size
        size = self._calculate_size(data)
        if size > 10000:
            score += 0.3
        elif size > 1000:
            score += 0.2
        elif size > 100:
            score += 0.1
        
        # Pattern-based complexity
        if DataPattern.MIXED_KEYS in patterns:
            score += 0.2
        if DataPattern.HIERARCHICAL in patterns:
            score += 0.2
        if DataPattern.PREFIX_HEAVY in patterns:
            score += 0.1
        if DataPattern.FREQUENT_UPDATES in patterns:
            score += 0.1
        
        return min(score, 1.0)
    
    def _build_pattern_weights(self) -> Dict[DataPattern, float]:
        """Build weights for different patterns."""
        return {
            DataPattern.SEQUENTIAL_NUMERIC: 0.9,
            DataPattern.STRING_KEYS: 0.7,
            DataPattern.PREFIX_HEAVY: 0.8,
            DataPattern.HIERARCHICAL: 0.6,
            DataPattern.LARGE_DATASET: 0.5,
            DataPattern.SMALL_DATASET: 0.3,
            DataPattern.FREQUENT_UPDATES: 0.4,
            DataPattern.READ_HEAVY: 0.3,
            DataPattern.WRITE_HEAVY: 0.4,
        }
    
    def _build_strategy_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build strategy selection rules."""
        return {
            'node': [
                {
                    'mode': NodeMode.ARRAY_LIST,
                    'conditions': [DataPattern.SEQUENTIAL_NUMERIC, DataPattern.SMALL_DATASET],
                    'reasoning': 'Sequential numeric keys with small dataset - optimal for array list',
                    'performance_gain': 0.3,
                    'data_loss_risk': False
                },
                {
                    'mode': NodeMode.HASH_MAP,
                    'conditions': [DataPattern.STRING_KEYS, DataPattern.FLAT_STRUCTURE],
                    'reasoning': 'String keys with flat structure - optimal for hash map',
                    'performance_gain': 0.2,
                    'data_loss_risk': False
                },
                {
                    'mode': NodeMode.TREE_GRAPH_HYBRID,
                    'conditions': [DataPattern.PREFIX_HEAVY, DataPattern.HIERARCHICAL],
                    'reasoning': 'Prefix-heavy hierarchical data - optimal for tree structure',
                    'performance_gain': 0.4,
                    'data_loss_risk': False
                },
                {
                    'mode': NodeMode.HASH_MAP,
                    'conditions': [DataPattern.LARGE_DATASET, DataPattern.READ_HEAVY],
                    'reasoning': 'Large dataset with read-heavy access - optimized for data interchange',
                    'performance_gain': 0.5,
                    'data_loss_risk': False
                }
            ],
            'edge': [
                {
                    'mode': EdgeMode.ADJ_LIST,
                    'conditions': [DataPattern.GRAPH_STRUCTURE],
                    'reasoning': 'Graph structure detected - optimal for adjacency list',
                    'performance_gain': 0.3,
                    'data_loss_risk': False
                },
                {
                    'mode': EdgeMode.ADJ_MATRIX,
                    'conditions': [DataPattern.LARGE_DATASET, DataPattern.SPATIAL_DATA],
                    'reasoning': 'Large spatial dataset - optimal for adjacency matrix',
                    'performance_gain': 0.2,
                    'data_loss_risk': False
                }
            ]
        }
    
    def _evaluate_rule(self, rule: Dict[str, Any], profile: DataProfile) -> float:
        """Evaluate how well a rule matches the profile."""
        conditions = rule.get('conditions', [])
        if not conditions:
            return 0.0
        
        matches = 0
        total_conditions = len(conditions)
        
        for condition in conditions:
            if condition in profile.patterns:
                matches += 1
        
        # Base confidence from pattern matches
        confidence = matches / total_conditions
        
        # Adjust based on data characteristics
        if profile.size > 1000 and DataPattern.LARGE_DATASET in conditions:
            confidence += 0.1
        elif profile.size < 100 and DataPattern.SMALL_DATASET in conditions:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _update_stats(self, analysis_time: float) -> None:
        """Update internal statistics."""
        self._stats['analyses_performed'] += 1
        
        # Update average analysis time
        total_time = self._stats['average_analysis_time'] * (self._stats['analyses_performed'] - 1)
        self._stats['average_analysis_time'] = (total_time + analysis_time) / self._stats['analyses_performed']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return self._stats.copy()


# Global detector instance
_detector_instance: Optional[DataPatternDetector] = None
_detector_lock = threading.Lock()


def get_detector() -> DataPatternDetector:
    """
    Get the global pattern detector instance.
    
    Returns:
        Global DataPatternDetector instance
    """
    global _detector_instance
    
    if _detector_instance is None:
        with _detector_lock:
            if _detector_instance is None:
                _detector_instance = DataPatternDetector()
                logger.info("🔍 Initialized global data pattern detector")
    
    return _detector_instance


def analyze_data_patterns(data: Any, **context: Any) -> DataProfile:
    """
    Analyze data patterns using the global detector.
    
    Args:
        data: Data to analyze
        **context: Additional context
        
    Returns:
        Data profile
    """
    return get_detector().analyze_data(data, **context)


def recommend_strategy(profile: DataProfile, strategy_type: str = 'node', **options: Any) -> StrategyRecommendation:
    """
    Get strategy recommendation using the global detector.
    
    Args:
        profile: Data profile
        strategy_type: 'node' or 'edge'
        **options: Additional options
        
    Returns:
        Strategy recommendation
    """
    detector = get_detector()
    if strategy_type == 'node':
        return detector.recommend_node_strategy(profile, **options)
    else:
        return detector.recommend_edge_strategy(profile, **options)
