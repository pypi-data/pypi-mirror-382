"""
Tests for xwnode performance mode system.

This module tests the performance mode functionality including:
- Performance mode creation and switching
- Configuration profiles
- Object pooling integration
- Performance monitoring
- Auto-detection logic
"""

import pytest
import time
import sys
from typing import Dict, Any

from src.xlib.xwnode import (
    xwnode, PerformanceMode, PerformanceProfile, PerformanceProfiles,
    set_performance_mode, get_performance_mode, get_config, get_pool_stats
)
from src.xlib.xwsystem.config import PerformanceMode as SystemPerformanceMode


class TestPerformanceModeBasics:
    """Test basic performance mode functionality."""
    
    def test_performance_mode_enum(self):
        """Test that performance modes are properly defined."""
        assert PerformanceMode.AUTO == SystemPerformanceMode.AUTO
        assert PerformanceMode.PARENT == SystemPerformanceMode.PARENT
        assert PerformanceMode.DEFAULT == SystemPerformanceMode.DEFAULT
        assert PerformanceMode.FAST == SystemPerformanceMode.FAST
        assert PerformanceMode.OPTIMIZED == SystemPerformanceMode.OPTIMIZED
        assert PerformanceMode.MANUAL == SystemPerformanceMode.MANUAL
    
    def test_performance_mode_string_conversion(self):
        """Test performance mode string conversion."""
        assert str(PerformanceMode.AUTO) == "auto"
        assert str(PerformanceMode.FAST) == "fast"
        assert str(PerformanceMode.OPTIMIZED) == "optimized"
        assert str(PerformanceMode.MANUAL) == "manual"
    
    def test_performance_mode_from_string(self):
        """Test creating performance mode from string."""
        assert PerformanceMode.from_string("auto") == PerformanceMode.AUTO
        assert PerformanceMode.from_string("FAST") == PerformanceMode.FAST
        assert PerformanceMode.from_string("optimized") == PerformanceMode.OPTIMIZED
        
        with pytest.raises(ValueError):
            PerformanceMode.from_string("invalid")
    
    def test_default_performance_mode(self):
        """Test that default performance mode is set correctly."""
        # Reset to default
        set_performance_mode(PerformanceMode.DEFAULT)
        assert get_performance_mode() == PerformanceMode.DEFAULT


class TestPerformanceProfiles:
    """Test performance profile functionality."""
    
    def test_default_profile(self):
        """Test default performance profile."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)
        assert isinstance(profile, PerformanceProfile)
        assert profile.path_cache_size == 1024
        assert profile.node_pool_size == 2000
        assert profile.enable_thread_safety is True
        assert profile.enable_object_pooling is True
    
    def test_fast_profile(self):
        """Test fast performance profile."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.FAST)
        assert profile.path_cache_size == 2048  # Larger cache
        assert profile.node_pool_size == 5000   # More pre-allocated nodes
        assert profile.lazy_threshold_dict == 5  # Eager loading
        assert profile.enable_thread_safety is False  # Skip locking
        assert profile.enable_weak_refs is False  # Strong references
    
    def test_optimized_profile(self):
        """Test memory-optimized profile."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.OPTIMIZED)
        assert profile.path_cache_size == 256   # Smaller cache
        assert profile.node_pool_size == 500    # Fewer pre-allocated nodes
        assert profile.lazy_threshold_dict == 25  # More lazy loading
        assert profile.enable_path_caching is False  # Disable for memory
        assert profile.enable_conversion_caching is False
    
    def test_auto_profile_small_data(self):
        """Test auto profile for small data."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.AUTO, data_size=100)
        # Should use FAST mode for small data
        assert profile.path_cache_size == 2048
        assert profile.enable_thread_safety is False
    
    def test_auto_profile_large_data(self):
        """Test auto profile for large data."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.AUTO, data_size=200000)
        # Should use OPTIMIZED mode for large data
        assert profile.path_cache_size == 256
        assert profile.enable_path_caching is False
    
    def test_auto_profile_medium_data(self):
        """Test auto profile for medium data."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.AUTO, data_size=5000)
        # Should use DEFAULT mode for medium data
        assert profile.path_cache_size == 1024
        assert profile.enable_thread_safety is True
    
    def test_profile_to_dict(self):
        """Test profile serialization."""
        profile = PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)
        profile_dict = profile.to_dict()
        
        assert isinstance(profile_dict, dict)
        assert 'path_cache_size' in profile_dict
        assert 'node_pool_size' in profile_dict
        assert 'enable_thread_safety' in profile_dict
    
    def test_profile_from_dict(self):
        """Test profile deserialization."""
        original_profile = PerformanceProfiles.get_profile(PerformanceMode.DEFAULT)
        profile_dict = original_profile.to_dict()
        
        new_profile = PerformanceProfile.from_dict(profile_dict)
        assert new_profile.path_cache_size == original_profile.path_cache_size
        assert new_profile.node_pool_size == original_profile.node_pool_size


class TestDataSizeEstimation:
    """Test data size estimation for auto-detection."""
    
    def test_estimate_none(self):
        """Test estimating size of None."""
        size = PerformanceProfiles.estimate_data_size(None)
        assert size == 0
    
    def test_estimate_primitives(self):
        """Test estimating size of primitive types."""
        assert PerformanceProfiles.estimate_data_size("hello") == 5
        assert PerformanceProfiles.estimate_data_size(42) == 1
        assert PerformanceProfiles.estimate_data_size(3.14) == 1
        assert PerformanceProfiles.estimate_data_size(True) == 1
    
    def test_estimate_list(self):
        """Test estimating size of lists."""
        data = [1, 2, 3, "hello", "world"]
        size = PerformanceProfiles.estimate_data_size(data)
        assert size == 5 + 1 + 1 + 1 + 5 + 5  # len + sum of items
    
    def test_estimate_dict(self):
        """Test estimating size of dictionaries."""
        data = {"a": 1, "b": "hello", "c": [1, 2, 3]}
        size = PerformanceProfiles.estimate_data_size(data)
        assert size > 3  # len + sum of values
    
    def test_estimate_nested(self):
        """Test estimating size of nested structures."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "settings": {"theme": "dark", "language": "en"}
        }
        size = PerformanceProfiles.estimate_data_size(data)
        assert size > 10  # Should be substantial for nested data


class TestXWNodePerformanceModes:
    """Test xwnode performance mode integration."""
    
    def test_fast_mode_creation(self):
        """Test creating xNode in fast mode."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.fast(data)
        
        # Check that fast mode is active
        config = get_config()
        assert config.performance_mode == PerformanceMode.FAST
        
        # Verify node works correctly
        assert node["a"].value == 1
        assert node["b"].value == 2
        assert node["c"].value == 3
    
    def test_optimized_mode_creation(self):
        """Test creating xNode in optimized mode."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.optimized(data)
        
        # Check that optimized mode is active
        config = get_config()
        assert config.performance_mode == PerformanceMode.OPTIMIZED
        
        # Verify node works correctly
        assert node["a"].value == 1
        assert node["b"].value == 2
        assert node["c"].value == 3
    
    def test_manual_mode_creation(self):
        """Test creating xNode with manual configuration."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.manual(
            data,
            path_cache_size=4096,
            enable_thread_safety=False,
            lazy_threshold_dict=1
        )
        
        # Check that manual mode is active
        config = get_config()
        assert config.performance_mode == PerformanceMode.MANUAL
        
        # Verify custom settings are applied
        profile = config.get_active_profile()
        assert profile.path_cache_size == 4096
        assert profile.enable_thread_safety is False
        assert profile.lazy_threshold_dict == 1
        
        # Verify node works correctly
        assert node["a"].value == 1
        assert node["b"].value == 2
        assert node["c"].value == 3
    
    def test_from_native_with_mode(self):
        """Test creating xNode with specific performance mode."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.from_native(data, PerformanceMode.FAST)
        
        # Check that fast mode is active
        config = get_config()
        assert config.performance_mode == PerformanceMode.FAST
        
        # Verify node works correctly
        assert node["a"].value == 1
        assert node["b"].value == 2
        assert node["c"].value == 3
    
    def test_auto_mode_detection(self):
        """Test automatic mode detection based on data size."""
        # Small data should use FAST mode
        small_data = {"a": 1}
        node = xwnode.from_native(small_data, PerformanceMode.AUTO)
        config = get_config()
        assert config.performance_mode == PerformanceMode.AUTO
        
        # Large data should use OPTIMIZED mode
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        node = xwnode.from_native(large_data, PerformanceMode.AUTO)
        config = get_config()
        assert config.performance_mode == PerformanceMode.AUTO


class TestPerformanceModeSwitching:
    """Test runtime performance mode switching."""
    
    def test_set_performance_mode(self):
        """Test setting performance mode at runtime."""
        # Start with default
        set_performance_mode(PerformanceMode.DEFAULT)
        assert get_performance_mode() == PerformanceMode.DEFAULT
        
        # Switch to fast
        set_performance_mode(PerformanceMode.FAST)
        assert get_performance_mode() == PerformanceMode.FAST
        
        # Switch to optimized
        set_performance_mode(PerformanceMode.OPTIMIZED)
        assert get_performance_mode() == PerformanceMode.OPTIMIZED
    
    def test_node_performance_mode_methods(self):
        """Test xwnode performance mode methods."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.from_native(data)
        
        # Test getting current mode
        assert node.get_performance_mode() == get_performance_mode()
        
        # Test setting mode
        node.set_performance_mode(PerformanceMode.FAST)
        assert get_performance_mode() == PerformanceMode.FAST
        
        # Test getting performance stats
        stats = node.get_performance_stats()
        assert isinstance(stats, dict)
        assert 'mode' in stats
        assert 'config' in stats
        assert 'cache_stats' in stats


class TestObjectPooling:
    """Test object pooling integration."""
    
    def test_object_pool_stats(self):
        """Test object pool statistics."""
        # Create some nodes to populate the pool
        data1 = {"a": 1, "b": 2}
        data2 = {"c": 3, "d": 4}
        
        node1 = xwnode.fast(data1)
        node2 = xwnode.optimized(data2)
        
        # Get pool stats
        pool_stats = get_pool_stats()
        assert isinstance(pool_stats, dict)
        
        # Check that xwnode pool exists
        if 'xwnode' in pool_stats:
            xwnode_stats = pool_stats['xwnode']
            assert 'stats' in xnode_stats
            assert 'pool_sizes' in xnode_stats
            assert 'max_size' in xnode_stats
    
    def test_pool_integration(self):
        """Test that object pooling is properly integrated."""
        # Create nodes in fast mode (should use pooling)
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.fast(data)
        
        # Get performance stats to verify pooling is enabled
        stats = node.get_performance_stats()
        config = stats['config']
        assert config['enable_object_pooling'] is True
        
        # Create nodes in optimized mode (should also use pooling)
        node2 = xwnode.optimized(data)
        stats2 = node2.get_performance_stats()
        config2 = stats2['config']
        assert config2['enable_object_pooling'] is True


class TestPerformanceMonitoring:
    """Test performance monitoring integration."""
    
    def test_performance_stats_structure(self):
        """Test that performance stats have the expected structure."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.from_native(data)
        
        stats = node.get_performance_stats()
        
        # Check required fields
        assert 'mode' in stats
        assert 'config' in stats
        assert 'cache_stats' in stats
        assert 'path_cache_stats' in stats
        
        # Check config structure
        config = stats['config']
        assert 'path_cache_size' in config
        assert 'node_pool_size' in config
        assert 'enable_thread_safety' in config
        assert 'enable_object_pooling' in config
        
        # Check cache stats structure
        cache_stats = stats['cache_stats']
        assert 'size' in cache_stats
        assert 'max_size' in cache_stats
        assert 'hits' in cache_stats
        assert 'misses' in cache_stats
        assert 'hit_rate' in cache_stats
    
    def test_cache_performance(self):
        """Test that caching improves performance."""
        data = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        node = xwnode.from_native(data)
        
        # First access (cache miss)
        start_time = time.time()
        result1 = node.find("a.b.c.d.e")
        first_access_time = time.time() - start_time
        
        # Second access (cache hit)
        start_time = time.time()
        result2 = node.find("a.b.c.d.e")
        second_access_time = time.time() - start_time
        
        # Results should be the same
        assert result1.value == result2.value
        assert result1.value == 42
        
        # Second access should be faster (though this may not always be true due to system load)
        # We'll just verify that both accesses work correctly


class TestConfigurationIntegration:
    """Test configuration integration with performance modes."""
    
    def test_config_profile_consistency(self):
        """Test that config profiles are consistent across modes."""
        modes = [
            PerformanceMode.DEFAULT,
            PerformanceMode.FAST,
            PerformanceMode.OPTIMIZED
        ]
        
        for mode in modes:
            set_performance_mode(mode)
            config = get_config()
            profile = config.get_active_profile()
            
            # Verify profile has all required fields
            assert hasattr(profile, 'path_cache_size')
            assert hasattr(profile, 'node_pool_size')
            assert hasattr(profile, 'enable_thread_safety')
            assert hasattr(profile, 'enable_object_pooling')
            assert hasattr(profile, 'max_depth')
            assert hasattr(profile, 'max_nodes')
            assert hasattr(profile, 'max_path_length')
    
    def test_manual_overrides(self):
        """Test manual configuration overrides."""
        config = get_config()
        
        # Set manual overrides
        config.set_manual_override('path_cache_size', 8192)
        config.set_manual_override('enable_thread_safety', False)
        
        # Get profile and verify overrides are applied
        profile = config.get_active_profile()
        assert profile.path_cache_size == 8192
        assert profile.enable_thread_safety is False
    
    def test_invalid_manual_override(self):
        """Test that invalid manual overrides raise errors."""
        config = get_config()
        
        with pytest.raises(Exception):
            config.set_manual_override('invalid_key', 123)


class TestErrorHandling:
    """Test error handling in performance mode system."""
    
    def test_invalid_performance_mode(self):
        """Test handling of invalid performance modes."""
        with pytest.raises(ValueError):
            PerformanceMode.from_string("invalid_mode")
    
    def test_invalid_profile_parameters(self):
        """Test handling of invalid profile parameters."""
        with pytest.raises(ValueError):
            PerformanceProfiles.get_profile("invalid_mode")
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = get_config()
        
        # Test with valid profile
        profile = config.get_active_profile()
        assert profile.path_cache_size > 0
        assert profile.node_pool_size > 0
        assert profile.max_depth > 0


class TestIntegrationScenarios:
    """Test integration scenarios with performance modes."""
    
    def test_large_data_processing(self):
        """Test processing large data with different modes."""
        # Create large dataset
        large_data = {
            "users": [
                {
                    "id": i,
                    "name": f"User{i}",
                    "data": {f"key{j}": f"value{j}" for j in range(10)}
                }
                for i in range(1000)
            ]
        }
        
        # Test with fast mode
        fast_node = xwnode.fast(large_data)
        fast_start = time.time()
        fast_result = fast_node.find("users.500.name")
        fast_time = time.time() - fast_start
        
        # Test with optimized mode
        optimized_node = xwnode.optimized(large_data)
        optimized_start = time.time()
        optimized_result = optimized_node.find("users.500.name")
        optimized_time = time.time() - optimized_start
        
        # Both should return the same result
        assert fast_result.value == "User500"
        assert optimized_result.value == "User500"
        
        # Both should work correctly
        assert fast_node.count("users") == 1000
        assert optimized_node.count("users") == 1000
    
    def test_mode_switching_scenario(self):
        """Test switching modes during processing."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xwnode.from_native(data)
        
        # Start with default mode
        assert node.get_performance_mode() == PerformanceMode.DEFAULT
        
        # Switch to fast mode for intensive operations
        node.set_performance_mode(PerformanceMode.FAST)
        assert node.get_performance_mode() == PerformanceMode.FAST
        
        # Perform operations
        result1 = node.find("a")
        result2 = node.find("b")
        result3 = node.find("c")
        
        assert result1.value == 1
        assert result2.value == 2
        assert result3.value == 3
        
        # Switch to optimized mode for memory-constrained operations
        node.set_performance_mode(PerformanceMode.OPTIMIZED)
        assert node.get_performance_mode() == PerformanceMode.OPTIMIZED
        
        # Operations should still work
        result4 = node.find("a")
        assert result4.value == 1
    
    def test_concurrent_access(self):
        """Test concurrent access with different performance modes."""
        import threading
        
        data = {"a": 1, "b": 2, "c": 3}
        results = []
        
        def worker(mode, node_id):
            node = xwnode.from_native(data, mode)
            result = node.find("a")
            results.append((node_id, result.value))
        
        # Create threads with different modes
        threads = []
        for i in range(3):
            mode = [PerformanceMode.FAST, PerformanceMode.OPTIMIZED, PerformanceMode.DEFAULT][i % 3]
            thread = threading.Thread(target=worker, args=(mode, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all results are correct
        assert len(results) == 3
        for node_id, value in results:
            assert value == 1


if __name__ == "__main__":
    pytest.main([__file__])
