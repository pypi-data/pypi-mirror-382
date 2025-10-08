"""
ADAPTIVE Mode Tests
==================

Tests specifically for the ADAPTIVE performance mode functionality.
"""

import pytest
import time
import statistics
from src.xlib.xwnode import xwnode
from src.xlib.xwsystem.config import PerformanceMode
from src.xlib.xwnode.config import set_performance_mode


class TestAdaptiveMode:
    """Test ADAPTIVE mode functionality."""
    
    def test_adaptive_mode_creation(self, test_data):
        """Test ADAPTIVE mode node creation."""
        start_time = time.time()
        node = xwnode.adaptive(test_data)
        creation_time = (time.time() - start_time) * 1000
        
        assert node is not None
        assert creation_time < 1000  # Should be fast
        assert node.get_performance_mode() == PerformanceMode.ADAPTIVE
        
        # Test that adaptive mode provides reasonable performance
        stats = node.get_performance_stats()
        assert 'adaptive_learning' in stats
        assert stats['mode'] == 'ADAPTIVE'
    
    def test_adaptive_mode_learning(self, test_data):
        """Test that ADAPTIVE mode learns from operations."""
        node = xwnode.adaptive(test_data)
        
        # Perform multiple operations to trigger learning
        for i in range(50):
            # Navigation operations
            node.find(f'users.{i % 100}.name')
            node.find(f'settings.theme')
            node.find(f'metadata.version')
            
            # Access operations
            node['users'][i % 100]['name']
            node['settings']['theme']
        
        # Get adaptive stats
        stats = node.get_performance_stats()
        adaptive_stats = stats.get('adaptive_learning', {})
        
        # Should have recorded some metrics
        assert adaptive_stats.get('metrics_count', 0) > 0
        
        # Should have performance data for different modes
        mode_performance = adaptive_stats.get('mode_performance', {})
        assert len(mode_performance) > 0
    
    def test_adaptive_mode_adaptation(self, test_data):
        """Test that ADAPTIVE mode adapts to different scenarios."""
        # Create adaptive node
        node = xwnode.adaptive(test_data)
        
        # Perform operations that would trigger adaptation
        for i in range(100):
            # Heavy navigation operations
            for j in range(10):
                node.find(f'users.{j}.name')
                node.find(f'users.{j}.email')
                node.find(f'users.{j}.active')
        
        # Get stats to see if adaptation occurred
        stats = node.get_performance_stats()
        adaptive_stats = stats.get('adaptive_learning', {})
        
        # Should have learning data
        assert adaptive_stats.get('metrics_count', 0) > 0
    
    def test_adaptive_mode_configuration(self, small_data, large_data):
        """Test ADAPTIVE mode configuration options."""
        
        # Small data should work well
        small_node = xwnode.adaptive(small_data)
        assert small_node.get_performance_mode() == PerformanceMode.ADAPTIVE
        
        # Large data should also work well
        large_node = xwnode.adaptive(large_data)
        assert large_node.get_performance_mode() == PerformanceMode.ADAPTIVE
        
        # Both should have adaptive learning enabled
        small_stats = small_node.get_performance_stats()
        large_stats = large_node.get_performance_stats()
        
        assert 'adaptive_learning' in small_stats
        assert 'adaptive_learning' in large_stats
    
    def test_adaptive_mode_error_handling(self):
        """Test ADAPTIVE mode error handling."""
        
        # Test with None data (should be allowed)
        node = xwnode.adaptive(None)
        assert node is not None
        assert node.get_performance_mode() == PerformanceMode.ADAPTIVE
        
        # Test with empty data structures
        empty_dict = {}
        node = xwnode.adaptive(empty_dict)
        assert node is not None
        assert node.get_performance_mode() == PerformanceMode.ADAPTIVE
        
        empty_list = []
        node = xwnode.adaptive(empty_list)
        assert node is not None
        assert node.get_performance_mode() == PerformanceMode.ADAPTIVE
        
        # Test with complex nested data (should handle gracefully)
        complex_data = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'deep_nested'
                    }
                }
            },
            'list': [1, 2, 3, {'nested': 'value'}],
            'mixed': {
                'string': 'test',
                'number': 42,
                'boolean': True,
                'null': None
            }
        }
        
        # Should not crash
        node = xwnode.adaptive(complex_data)
        assert node is not None
        assert node.get_performance_mode() == PerformanceMode.ADAPTIVE
    
    def test_adaptive_mode_memory_efficiency(self, test_data):
        """Test ADAPTIVE mode memory efficiency."""
        
        import gc
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple adaptive nodes
        nodes = []
        for i in range(10):
            node = xwnode.adaptive(test_data)
            nodes.append(node)
        
        # Force garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 10 nodes)
        assert memory_increase < 100, f"Memory usage increased by {memory_increase:.2f}MB"
        
        # Clean up
        del nodes
        gc.collect()
    
    def test_adaptive_mode_thread_safety(self, test_data):
        """Test ADAPTIVE mode thread safety."""
        
        import threading
        import time
        
        node = xwnode.adaptive(test_data)
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(100):
                    # Perform operations
                    node.find(f'users.{i % 100}.name')
                    node.find('settings.theme')
                    time.sleep(0.001)  # Small delay
                results.append(f"Worker {worker_id} completed")
            except Exception as e:
                errors.append(f"Worker {worker_id} error: {e}")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 5, "Not all workers completed"
    
    def test_adaptive_mode_learning_curve(self, test_data):
        """Test ADAPTIVE mode learning curve over time."""
        
        node = xwnode.adaptive(test_data)
        
        # Track performance over multiple operation batches
        performance_history = []
        
        for batch in range(5):
            start_time = time.time()
            
            # Perform batch of operations
            for i in range(20):
                node.find(f'users.{i}.name')
                node.find(f'users.{i}.email')
                node.find('settings.theme')
            
            batch_time = (time.time() - start_time) * 1000
            performance_history.append(batch_time)
            
            # Get current stats
            stats = node.get_performance_stats()
            adaptive_stats = stats.get('adaptive_learning', {})
            
            print(f"Batch {batch + 1}: {batch_time:.2f}ms, "
                  f"Metrics: {adaptive_stats.get('metrics_count', 0)}")
        
        # Performance should be reasonable throughout
        for batch_time in performance_history:
            assert batch_time < 1000, f"Batch took too long: {batch_time:.2f}ms"
        
        # Should have learning data
        final_stats = node.get_performance_stats()
        final_adaptive_stats = final_stats.get('adaptive_learning', {})
        assert final_adaptive_stats.get('metrics_count', 0) > 0
    
    def test_adaptive_mode_advantages(self, test_data):
        """Test specific advantages of ADAPTIVE mode."""
        # Reset performance manager to ensure clean state
        from src.xlib.xnode.config import reset_performance_manager
        reset_performance_manager()
        
        # Test ADAPTIVE vs AUTO
        auto_node = xwnode.from_native(test_data, PerformanceMode.AUTO)
        adaptive_node = xwnode.adaptive(test_data)
        
        # Perform operations to trigger learning
        for i in range(50):
            auto_node.find(f'users.{i % 100}.name')
            adaptive_node.find(f'users.{i % 100}.name')
        
        # Get stats
        auto_stats = auto_node.get_performance_stats()
        adaptive_stats = adaptive_node.get_performance_stats()
        
        print("   ✅ ADAPTIVE has learning capabilities:", 'adaptive_learning' in adaptive_stats)
        print("   ✅ AUTO has learning capabilities:", 'adaptive_learning' in auto_stats)
        print("   ✅ ADAPTIVE maintains performance mode:", adaptive_stats['mode'] == 'ADAPTIVE')
        
        # Show adaptive learning data
        if 'adaptive_learning' in adaptive_stats:
            learning_data = adaptive_stats['adaptive_learning']
            print(f"   ✅ Metrics count: {learning_data.get('metrics_count', 0)}")
            print(f"   ✅ System metrics: {learning_data.get('system_metrics', {})}")
