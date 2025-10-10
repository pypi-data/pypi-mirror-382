#!/usr/bin/env python3
"""
Test A+ Usability Presets for XWNode Library

This module tests all the A+ improvements implemented:
1. Preset-based initialization
2. Performance mode factory methods
3. Consistent API behavior
4. Best practice error messages
"""

import pytest
import time
from typing import Dict, Any

from exonware.xwnode import (
    XWNode, create_with_preset, list_available_presets,
    fast, optimized, adaptive, dual_adaptive
)
from exonware.xnode.strategies.types import (
    get_preset, list_presets, NodeMode, EdgeMode, NodeTrait
)


class TestPresetSystem:
    """Test the A+ preset-based initialization system."""
    
    def test_preset_list_available(self):
        """Test that all presets are available."""
        presets = list_available_presets()
        expected_presets = [
            'DATA_INTERCHANGE_OPTIMIZED', 'DEFAULT', 'PURE_TREE', 'TREE_GRAPH_MIX',
            'FAST_LOOKUP', 'MEMORY_EFFICIENT', 'SOCIAL_GRAPH', 'ANALYTICS',
            'SEARCH_ENGINE', 'TIME_SERIES', 'SPATIAL_MAP', 'ML_DATASET'
        ]
        
        for preset in expected_presets:
            assert preset in presets, f"Preset {preset} should be available"
    
    def test_data_interchange_optimized_preset(self):
        """Test DATA_INTERCHANGE_OPTIMIZED preset for ultra-lightweight performance."""
        data = {"api": {"timeout": 30, "retries": 3}, "cache": {"size": 1000}}
        node = create_with_preset(data, preset='DATA_INTERCHANGE_OPTIMIZED')
        
        # Test basic functionality
        assert node.find('api.timeout').value == 30
        assert node['api']['retries'].value == 3
        assert node.get('cache.size').value == 1000
        
        # Test that it's a valid XWNode
        assert isinstance(node, XWNode)
    
    def test_social_graph_preset(self):
        """Test SOCIAL_GRAPH preset for social network optimization."""
        data = {
            "users": {
                "alice": {"friends": ["bob", "charlie"], "posts": 15},
                "bob": {"friends": ["alice"], "posts": 8}
            }
        }
        node = create_with_preset(data, preset='SOCIAL_GRAPH')
        
        # Test graph-like operations
        assert node.find('users.alice.friends').value == ["bob", "charlie"]
        assert node['users']['bob']['posts'].value == 8
        
        # Test that it's a valid XWNode
        assert isinstance(node, XWNode)
    
    def test_analytics_preset(self):
        """Test ANALYTICS preset for data analytics optimization."""
        data = {
            "metrics": {
                "page_views": [100, 150, 200],
                "conversion_rate": 0.05,
                "bounce_rate": 0.3
            }
        }
        node = create_with_preset(data, preset='ANALYTICS')
        
        # Test analytics operations
        assert node.find('metrics.page_views').value == [100, 150, 200]
        assert node['metrics']['conversion_rate'].value == 0.05
        
        # Test that it's a valid XWNode
        assert isinstance(node, XWNode)
    
    def test_search_engine_preset(self):
        """Test SEARCH_ENGINE preset for search optimization."""
        data = {
            "index": {
                "documents": {
                    "doc1": {"title": "Python Guide", "content": "Python programming"},
                    "doc2": {"title": "Data Science", "content": "Machine learning"}
                }
            }
        }
        node = create_with_preset(data, preset='SEARCH_ENGINE')
        
        # Test search operations
        assert node.find('index.documents.doc1.title').value == "Python Guide"
        assert node['index']['documents']['doc2']['content'].value == "Machine learning"
        
        # Test that it's a valid XWNode
        assert isinstance(node, XWNode)
    
    def test_ml_dataset_preset(self):
        """Test ML_DATASET preset for machine learning optimization."""
        data = {
            "features": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            "labels": [0, 1, 0],
            "metadata": {"samples": 3, "features": 3}
        }
        node = create_with_preset(data, preset='ML_DATASET')
        
        # Test ML operations
        assert node.find('features').value == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        assert node['labels'].value == [0, 1, 0]
        assert node.get('metadata.samples').value == 3
        
        # Test that it's a valid XWNode
        assert isinstance(node, XWNode)
    
    def test_invalid_preset_handling(self):
        """Test handling of invalid preset names."""
        data = {"test": "data"}
        
        # Should not raise exception, but log warning and use default
        node = create_with_preset(data, preset='INVALID_PRESET')
        assert isinstance(node, XWNode)
        assert node['test'].value == "data"
    
    def test_default_preset(self):
        """Test DEFAULT preset behavior."""
        data = {"config": {"debug": True, "level": "info"}}
        node = create_with_preset(data, preset='DEFAULT')
        
        # Test basic functionality
        assert node.find('config.debug').value is True
        assert node['config']['level'].value == "info"
        
        # Test that it's a valid XWNode
        assert isinstance(node, XWNode)


class TestPerformanceModes:
    """Test Performance Mode factory methods."""
    
    def test_fast_mode(self):
        """Test fast() factory method."""
        data = {"performance": "fast", "cache_size": 2048}
        node = fast(data)
        
        assert isinstance(node, XWNode)
        assert node['performance'].value == "fast"
        assert node.get('cache_size').value == 2048
    
    def test_optimized_mode(self):
        """Test optimized() factory method."""
        data = {"memory": "efficient", "lazy_loading": True}
        node = optimized(data)
        
        assert isinstance(node, XWNode)
        assert node['memory'].value == "efficient"
        assert node.get('lazy_loading').value is True
    
    def test_adaptive_mode(self):
        """Test adaptive() factory method."""
        data = {"mode": "adaptive", "monitoring": True}
        node = adaptive(data)
        
        assert isinstance(node, XWNode)
        assert node['mode'].value == "adaptive"
        assert node.get('monitoring').value is True
    
    def test_dual_adaptive_mode(self):
        """Test dual_adaptive() factory method."""
        data = {"mode": "dual_adaptive", "phases": 2}
        node = dual_adaptive(data)
        
        assert isinstance(node, XWNode)
        assert node['mode'].value == "dual_adaptive"
        assert node.get('phases').value == 2
    
    def test_performance_modes_with_empty_data(self):
        """Test performance modes with empty data."""
        # Test all modes with None/empty data
        assert isinstance(fast(), XWNode)
        assert isinstance(optimized(), XWNode)
        assert isinstance(adaptive(), XWNode)
        assert isinstance(dual_adaptive(), XWNode)
        
        # Test with empty dict
        assert isinstance(fast({}), XWNode)
        assert isinstance(optimized({}), XWNode)
        assert isinstance(adaptive({}), XWNode)
        assert isinstance(dual_adaptive({}), XWNode)


class TestPresetIntegration:
    """Test integration between presets and performance modes."""
    
    def test_preset_with_performance_mode_combination(self):
        """Test that presets work with performance modes."""
        data = {"test": "integration"}
        
        # Test preset with different performance modes
        node1 = create_with_preset(data, preset='DATA_INTERCHANGE_OPTIMIZED')
        node2 = fast(data)
        node3 = optimized(data)
        
        # All should be valid XWNode instances
        assert isinstance(node1, XWNode)
        assert isinstance(node2, XWNode)
        assert isinstance(node3, XWNode)
        
        # All should have the same data
        assert node1['test'].value == "integration"
        assert node2['test'].value == "integration"
        assert node3['test'].value == "integration"
    
    def test_preset_consistency(self):
        """Test that presets provide consistent behavior."""
        data = {"consistency": "test", "values": [1, 2, 3]}
        
        # Create multiple nodes with same preset
        node1 = create_with_preset(data, preset='SOCIAL_GRAPH')
        node2 = create_with_preset(data, preset='SOCIAL_GRAPH')
        
        # Both should behave identically
        assert node1['consistency'].value == node2['consistency'].value
        assert node1['values'].value == node2['values'].value
        
        # Both should be valid XWNode instances
        assert isinstance(node1, XWNode)
        assert isinstance(node2, XWNode)


class TestPresetDocumentation:
    """Test preset documentation and metadata."""
    
    def test_preset_descriptions(self):
        """Test that presets have proper descriptions."""
        presets = list_available_presets()
        
        for preset_name in presets:
            preset_config = get_preset(preset_name)
            
            # Each preset should have a description
            assert hasattr(preset_config, 'description')
            assert isinstance(preset_config.description, str)
            assert len(preset_config.description) > 0
            
            # Each preset should have a performance class
            assert hasattr(preset_config, 'performance_class')
            assert isinstance(preset_config.performance_class, str)
            assert len(preset_config.performance_class) > 0
    
    def test_preset_configuration_structure(self):
        """Test that preset configurations have proper structure."""
        preset_config = get_preset('DATA_INTERCHANGE_OPTIMIZED')
        
        # Should have required attributes
        assert hasattr(preset_config, 'node_mode')
        assert hasattr(preset_config, 'node_traits')
        assert hasattr(preset_config, 'description')
        assert hasattr(preset_config, 'performance_class')
        
        # Node mode should be valid
        assert isinstance(preset_config.node_mode, NodeMode)
        
        # Node traits should be valid
        assert isinstance(preset_config.node_traits, NodeTrait)


if __name__ == '__main__':
    pytest.main([__file__])
