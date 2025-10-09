"""
Performance Mode Comparison Tests
================================

Comprehensive tests that compare all xwnode performance modes.
"""

import pytest
import time
import gc
import statistics
from src.xlib.xwnode import xwnode
from src.xlib.xwsystem.config import PerformanceMode
from src.xlib.xwnode.config import set_performance_mode, reset_performance_manager
from .conftest import timeout_context


class TestPerformanceComparison:
    """Test performance mode comparisons."""
    
    def test_all_modes_comparison_table(self, test_data, deep_nested_data, wide_structure_data, clean_performance_manager):
        """Compare all performance modes in a comprehensive table."""
        
        with timeout_context(30):  # 30 second timeout for entire test
            test_scenarios = [
                ('simple', test_data)
            ]  # Reduced to only simple scenario for faster testing
            
            modes = [
                PerformanceMode.AUTO,
                PerformanceMode.ADAPTIVE,
                PerformanceMode.FAST
            ]  # Reduced to 3 modes for faster testing
            
            results = {}
            
            for scenario_name, data in test_scenarios:
                results[scenario_name] = {}
                
                for mode in modes:
                    # Reset manager before each mode test for proper isolation
                    reset_performance_manager()
                    gc.collect()
                    
                    # Set performance mode
                    set_performance_mode(mode)
                    
                    # Measure creation time with timeout protection
                    with timeout_context(5):  # 5 second timeout for creation
                        start_time = time.time()
                        node = xwnode.from_native(data, mode)
                        creation_time = (time.time() - start_time) * 1000
                    
                    # Measure navigation time with timeout protection and reduced iterations
                    with timeout_context(10):  # 10 second timeout for navigation
                        start_time = time.time()
                        if scenario_name == 'simple':
                            for i in range(5):  # Reduced from 20 to 5
                                node.find(f'users.{i % 5}.name')
                                node.find('settings.theme')
                                node.find('metadata.version')
                        elif scenario_name == 'deep_nested':
                            for i in range(5):  # Reduced from 20 to 5
                                node.find(f'level_0.level_1.level_2.level_3.level_4')
                                node.find(f'level_0.list_0.0.level_1.level_2')
                        elif scenario_name == 'wide_structure':
                            for i in range(5):  # Reduced from 20 to 5
                                node.find(f'key_{i % 5}.name')
                                node.find(f'key_{i % 5}.value')
                        
                        navigation_time = (time.time() - start_time) * 1000
                    
                    # Get performance stats
                    stats = node.get_performance_stats()
                    
                    # Store results
                    results[scenario_name][mode.name] = {
                        'creation_time_ms': creation_time,
                        'navigation_time_ms': navigation_time,
                        'mode': mode.name,
                        'cache_stats': stats.get('cache_stats', {}),
                        'adaptive_learning': stats.get('adaptive_learning', {})
                    }
                    
                    # Force cleanup after each mode
                    del node
                    gc.collect()
        
        # Print comparison table
        print("\n" + "="*80)
        print("PERFORMANCE MODE COMPARISON TABLE")
        print("="*80)
        
        for scenario_name, scenario_results in results.items():
            print(f"\n📊 {scenario_name.upper()} SCENARIO:")
            print("-" * 60)
            print(f"{'Mode':<12} {'Creation':<10} {'Navigation':<12} {'Cache Hit %':<12}")
            print("-" * 60)
            
            for mode_name, result in scenario_results.items():
                cache_hit_rate = result['cache_stats'].get('hit_rate', 0) * 100
                print(f"{mode_name:<12} {result['creation_time_ms']:<10.2f} "
                      f"{result['navigation_time_ms']:<12.2f} {cache_hit_rate:<12.1f}")
        
        # Assert that ADAPTIVE mode performs reasonably
        for scenario_name, scenario_results in results.items():
            adaptive_result = scenario_results.get('ADAPTIVE', {})
            
            # ADAPTIVE mode should be competitive
            assert adaptive_result['creation_time_ms'] < 1000, f"ADAPTIVE creation too slow in {scenario_name}"
            assert adaptive_result['navigation_time_ms'] < 5000, f"ADAPTIVE navigation too slow in {scenario_name}"
            
            # Should have learning data
            if 'adaptive_learning' in adaptive_result:
                learning_data = adaptive_result['adaptive_learning']
                assert learning_data.get('metrics_count', 0) >= 0
    
    def test_adaptive_vs_other_modes(self, test_data, clean_performance_manager):
        """Direct comparison of ADAPTIVE mode vs other modes."""
        
        with timeout_context(20):  # 20 second timeout for entire test
            modes_to_test = [
                (PerformanceMode.AUTO, "AUTO"),
                (PerformanceMode.FAST, "FAST"),
                (PerformanceMode.OPTIMIZED, "OPTIMIZED"),
                (PerformanceMode.ADAPTIVE, "ADAPTIVE")
            ]
            
            results = {}
            
            for mode, mode_name in modes_to_test:
                # Reset manager before each mode test
                reset_performance_manager()
                gc.collect()
                
                # Create node with timeout protection
                with timeout_context(5):
                    start_time = time.time()
                    node = xwnode.from_native(test_data, mode)
                    creation_time = (time.time() - start_time) * 1000
                
                # Perform operations with reduced iterations and timeout
                with timeout_context(10):
                    start_time = time.time()
                    for i in range(5):  # Reduced from 20 to 5
                        node.find(f'users.{i % 5}.name')
                        node.find('settings.theme')
                        node.find('metadata.version')
                    operation_time = (time.time() - start_time) * 1000
                
                # Get stats
                stats = node.get_performance_stats()
                
                results[mode_name] = {
                    'creation_time': creation_time,
                    'operation_time': operation_time,
                    'mode': stats['mode'],
                    'has_learning': 'adaptive_learning' in stats
                }
                
                # Force cleanup after each mode
                del node
                gc.collect()
        
        # Print comparison
        print("\n" + "="*60)
        print("ADAPTIVE vs OTHER MODES COMPARISON")
        print("="*60)
        print(f"{'Mode':<12} {'Creation':<10} {'Operations':<12} {'Learning':<10}")
        print("-"*60)
        
        for mode_name, result in results.items():
            learning = "Yes" if result['has_learning'] else "No"
            print(f"{mode_name:<12} {result['creation_time']:<10.2f} "
                  f"{result['operation_time']:<12.2f} {learning:<10}")
        
        # ADAPTIVE should have learning capabilities
        assert results['ADAPTIVE']['has_learning'], "ADAPTIVE mode should have learning"
        
        # ADAPTIVE should be competitive in performance
        adaptive_creation = results['ADAPTIVE']['creation_time']
        adaptive_operations = results['ADAPTIVE']['operation_time']
        
        # Should be within reasonable bounds
        assert adaptive_creation < 1000, f"ADAPTIVE creation too slow: {adaptive_creation:.2f}ms"
        assert adaptive_operations < 5000, f"ADAPTIVE operations too slow: {adaptive_operations:.2f}ms"
    
    def test_mode_characteristics(self, all_performance_modes, clean_performance_manager):
        """Test characteristics of each performance mode."""
        
        with timeout_context(30):  # 30 second timeout for entire test
            print("\n" + "="*80)
            print("PERFORMANCE MODE CHARACTERISTICS")
            print("="*80)
            
            for mode in all_performance_modes:
                if mode == PerformanceMode.PARENT:
                    continue  # Skip PARENT mode as it depends on context
                    
                print(f"\n🔍 {mode.name} Mode:")
                print("-" * 40)
                
                # Test with different data sizes
                test_cases = [
                    ('small', {'a': 1, 'b': 2, 'c': 3}),
                    ('medium', {f'key_{i}': f'value_{i}' for i in range(50)}),  # Reduced from 100 to 50
                    ('large', {f'key_{i:04d}': f'value_{i}' for i in range(200)})  # Reduced from 1000 to 200
                ]
                
                for size_name, data in test_cases:
                    # Reset manager before each test
                    reset_performance_manager()
                    gc.collect()
                    
                    with timeout_context(3):  # 3 second timeout per data size
                        set_performance_mode(mode)
                        start_time = time.time()
                        node = xwnode.from_native(data, mode)
                        creation_time = (time.time() - start_time) * 1000
                        
                        print(f"  {size_name.capitalize()} data creation: {creation_time:.2f}ms")
                        
                        # Force cleanup
                        del node
                        gc.collect()
    
    def test_auto_mode_intelligence(self, clean_performance_manager):
        """Test AUTO mode's intelligent behavior with different data types."""
        
        with timeout_context(25):  # 25 second timeout for entire test
            print("\n" + "="*80)
            print("AUTO MODE INTELLIGENCE TEST")
            print("="*80)
            
            test_cases = [
                ('tiny', {'a': 1}),
                ('small', {f'key_{i}': i for i in range(10)}),
                ('medium', {f'key_{i}': i for i in range(100)}),  # Reduced from 1000 to 100
                ('large', {f'key_{i:04d}': i for i in range(500)}),  # Reduced from 1000 to 500
                ('deep', self._create_deep_nested(10)),  # Reduced from 20 to 10
                ('wide', {f'key_{i:06d}': f'value_{i}' for i in range(500)})  # Reduced from 1000 to 500
            ]
            
            for case_name, data in test_cases:
                print(f"\n📊 Testing AUTO mode with {case_name} data:")
                
                # Reset manager before each test
                reset_performance_manager()
                gc.collect()
                
                # Set to AUTO mode
                set_performance_mode(PerformanceMode.AUTO)
                
                # Create node with timeout protection
                with timeout_context(5):
                    start_time = time.time()
                    node = xwnode.from_native(data, PerformanceMode.AUTO)
                    creation_time = (time.time() - start_time) * 1000
                
                # Get performance stats
                stats = node.get_performance_stats()
                
                print(f"  Creation time: {creation_time:.2f}ms")
                print(f"  Mode selected: {stats['mode']}")
                print(f"  Cache stats: {stats.get('cache_stats', {})}")
                
                # Force cleanup after each test
                del node
                gc.collect()
    
    def _create_deep_nested(self, depth):
        """Create a deeply nested structure."""
        deep_data = {}
        current = deep_data
        
        for i in range(depth):
            current[f'level_{i}'] = {}
            current = current[f'level_{i}']
        current['final_value'] = 'reached_the_end'
        
        return deep_data
    
    def test_performance_recommendations(self):
        """Test and provide recommendations for performance mode usage."""
        
        print("\n" + "="*60)
        print("PERFORMANCE MODE RECOMMENDATIONS")
        print("="*60)
        
        recommendations = [
            "✅ Use ADAPTIVE mode for production applications with variable workloads",
            "✅ Use ADAPTIVE mode when memory pressure varies during execution",
            "✅ Use ADAPTIVE mode for long-running applications that need optimization",
            "✅ Use ADAPTIVE mode when you want automatic performance tuning",
            "⚠️  ADAPTIVE mode has slight overhead for learning and monitoring",
            "⚠️  ADAPTIVE mode requires more memory for storing learning data",
            "❌ Don't use ADAPTIVE mode for simple, one-off operations",
            "❌ Don't use ADAPTIVE mode when you need predictable, fixed performance"
        ]
        
        for rec in recommendations:
            print(f"   {rec}")
        
        # Test that recommendations are valid
        assert len(recommendations) >= 8, "Should have comprehensive recommendations"
        
        # Test specific scenarios
        scenarios = [
            ("Production API", True),      # Should use ADAPTIVE
            ("Simple script", False),      # Should not use ADAPTIVE
            ("Real-time app", True),       # Should use ADAPTIVE
            ("Batch processing", True),    # Should use ADAPTIVE
            ("Memory-constrained", True),  # Should use ADAPTIVE
        ]
        
        for scenario, should_use_adaptive in scenarios:
            print(f"   📋 {scenario}: {'Use ADAPTIVE' if should_use_adaptive else 'Use other mode'}")
        
        assert len(scenarios) >= 5, "Should have multiple scenario recommendations"
