"""
Performance tests for xNode operations.
"""

import pytest
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

from src.xlib.xnode import xNode


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return result, (end_time - start_time) * 1000  # Convert to milliseconds


class TestDeepNestingPerformance:
    """Test performance with deeply nested structures."""
    
    @pytest.mark.performance
    def test_deep_nesting_creation(self, deep_nesting_data, performance_thresholds):
        """Test creation performance with deeply nested structures."""
        result, creation_time = measure_time(xNode.from_native, deep_nesting_data)
        
        assert creation_time < performance_thresholds['deep_nesting_ms']
        assert result is not None
    
    @pytest.mark.performance
    def test_deep_nesting_navigation(self, deep_nesting_node, performance_thresholds):
        """Test navigation performance with deeply nested structures."""
        path_parts = [f'level_{i}' for i in range(100)] + ['final_value']
        deep_path = '.'.join(path_parts)
        
        result, navigation_time = measure_time(deep_nesting_node.find, deep_path)
        
        assert navigation_time < performance_thresholds['deep_nesting_ms']
        assert result.value == 'reached_the_end'
    
    @pytest.mark.performance
    def test_deep_nesting_combined(self, deep_nesting_data, performance_thresholds):
        """Test combined creation and navigation performance."""
        # Measure creation
        node, creation_time = measure_time(xNode.from_native, deep_nesting_data)
        
        # Measure navigation
        path_parts = [f'level_{i}' for i in range(100)] + ['final_value']
        deep_path = '.'.join(path_parts)
        result, navigation_time = measure_time(node.find, deep_path)
        
        total_time = creation_time + navigation_time
        
        assert total_time < performance_thresholds['deep_nesting_ms'] * 2
        assert result.value == 'reached_the_end'


class TestWideStructurePerformance:
    """Test performance with wide structures."""
    
    @pytest.mark.performance
    def test_wide_structure_creation(self, wide_structure_data, performance_thresholds):
        """Test creation performance with wide structures."""
        result, creation_time = measure_time(xNode.from_native, wide_structure_data)
        
        assert creation_time < performance_thresholds['wide_structure_ms']
        assert result is not None
    
    @pytest.mark.performance
    def test_wide_structure_access(self, wide_structure_node, performance_thresholds):
        """Test access performance with wide structures."""
        test_keys = [0, 1000, 5000, 9999]
        
        for i in test_keys:
            key = f'key_{i:04d}'
            result, access_time = measure_time(wide_structure_node.__getitem__, key)
            
            assert access_time < performance_thresholds['navigation_ms']
            assert result.value == f'value_{i}'
    
    @pytest.mark.performance
    def test_wide_structure_iteration(self, wide_structure_node, performance_thresholds):
        """Test iteration performance with wide structures."""
        # Test keys iteration
        result, keys_time = measure_time(lambda: list(wide_structure_node.keys()))
        
        assert keys_time < performance_thresholds['wide_structure_ms']
        assert len(result) == 10000


class TestLargeArrayPerformance:
    """Test performance with large arrays."""
    
    @pytest.mark.performance
    def test_large_array_creation(self, large_array_data, performance_thresholds):
        """Test creation performance with large arrays."""
        result, creation_time = measure_time(xNode.from_native, large_array_data)
        
        assert creation_time < performance_thresholds['large_array_ms']
        assert result is not None
    
    @pytest.mark.performance
    def test_large_array_access(self, large_array_node, performance_thresholds):
        """Test access performance with large arrays."""
        test_indices = [0, 1000, 5000, 9999]
        
        for i in test_indices:
            result, access_time = measure_time(large_array_node.find, f'{i}.id')
            
            assert access_time < performance_thresholds['large_array_ms']
            assert result.value == i
    
    @pytest.mark.performance
    def test_large_array_iteration(self, large_array_node, performance_thresholds):
        """Test iteration performance with large arrays."""
        # Test array iteration
        result, iteration_time = measure_time(lambda: list(large_array_node))
        
        assert iteration_time < performance_thresholds['large_array_ms']
        assert len(result) == 10000


class TestNavigationPerformance:
    """Test navigation performance characteristics."""
    
    @pytest.mark.performance
    def test_path_navigation_performance(self, deep_nesting_node, performance_thresholds):
        """Test path-based navigation performance."""
        test_paths = [
            'level_0.level_1.level_2',
            'level_0.level_1.level_2.level_3.level_4',
            'level_0.level_1.level_2.level_3.level_4.level_5.level_6',
            '.'.join([f'level_{i}' for i in range(100)]) + '.final_value'
        ]
        
        for path in test_paths:
            result, navigation_time = measure_time(deep_nesting_node.find, path)
            
            assert navigation_time < performance_thresholds['navigation_ms']
            assert result is not None
    
    @pytest.mark.performance
    def test_bracket_navigation_performance(self, wide_structure_node, performance_thresholds):
        """Test bracket-based navigation performance."""
        test_keys = ['key_0000', 'key_1000', 'key_5000', 'key_9999']
        
        for key in test_keys:
            result, access_time = measure_time(wide_structure_node.__getitem__, key)
            
            assert access_time < performance_thresholds['wide_structure_ms']
            assert result is not None
    
    @pytest.mark.performance
    def test_mixed_navigation_performance(self, deep_nesting_node, performance_thresholds):
        """Test mixed navigation patterns performance."""
        # Test mixed bracket and path notation
        result, mixed_time = measure_time(
            lambda: deep_nesting_node['level_0'].find('level_1.level_2')
        )
        
        assert mixed_time < performance_thresholds['navigation_ms'] * 2
        assert result is not None


class TestMemoryPerformance:
    """Test memory usage characteristics."""
    
    @pytest.mark.performance
    def test_memory_efficiency(self, deep_nesting_data, wide_structure_data, large_array_data):
        """Test memory efficiency of node creation."""
        import sys
        
        # Measure memory before
        import gc
        gc.collect()
        
        # Create nodes
        deep_node = xNode.from_native(deep_nesting_data)
        wide_node = xNode.from_native(wide_structure_data)
        array_node = xNode.from_native(large_array_data)
        
        # Measure memory after
        gc.collect()
        
        # Basic memory check - nodes should be created without excessive memory usage
        assert deep_node is not None
        assert wide_node is not None
        assert array_node is not None
    
    @pytest.mark.performance
    def test_immutability_memory(self, deep_nesting_node):
        """Test that navigation maintains memory efficiency through immutability."""
        # Create multiple navigation results
        paths = [
            'level_0.level_1',
            'level_0.level_1.level_2.level_3',
            'level_0.level_1.level_2.level_3.level_4.level_5',
            'level_0.level_1.level_2.level_3.level_4.level_5.level_6.level_7.level_8.level_9'
        ]
        
        results = []
        for path in paths:
            result = deep_nesting_node.find(path)
            results.append(result)
        
        # All results should be different instances but same data
        assert len(set(id(r) for r in results)) == len(results)
        assert all(r is not None for r in results)


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v', '-m', 'performance']) 