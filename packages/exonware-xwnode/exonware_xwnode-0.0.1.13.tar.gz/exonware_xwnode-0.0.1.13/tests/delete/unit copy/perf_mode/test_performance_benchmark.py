"""
Performance Benchmark Tests
===========================

Comprehensive benchmarking that shows actual performance metrics for each mode.
"""

import pytest
import time
import gc
import psutil
import os
from src.xlib.xwnode import xwnode
from src.xlib.xwsystem.config import PerformanceMode
from src.xlib.xwnode.config import set_performance_mode, reset_performance_manager

# Import test configuration
try:
    from .test_config import *
except ImportError:
    # Default values if config file doesn't exist
    BENCHMARK_COMPREHENSIVE_OPS = 50
    BENCHMARK_MEMORY_OPS = 100
    BENCHMARK_SPEED_OPS = 150
    BENCHMARK_ADAPTIVE_OPS = 200
    BENCHMARK_LEARNING_OPS = 200


class PerformanceBenchmark:
    """Performance benchmarking utility."""
    
    @staticmethod
    def measure_memory():
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    @staticmethod
    def benchmark_mode(mode: PerformanceMode, data: dict, operations: int = 10):
        """Benchmark a specific performance mode."""
        # Reset and prepare
        reset_performance_manager()
        gc.collect()
        
        # Set mode
        set_performance_mode(mode)
        
        # Measure creation
        memory_before = PerformanceBenchmark.measure_memory()
        start_time = time.perf_counter()
        
        node = xwnode.from_native(data, mode)
        
        creation_time = (time.perf_counter() - start_time) * 1000
        memory_after_creation = PerformanceBenchmark.measure_memory()
        
        # Measure operations
        start_time = time.perf_counter()
        
        for i in range(operations):
            # Standard operations
            node.find('users.0.name')
            node.find('settings.theme')
            node.find('metadata.version')
            
            # Access operations
            node['users'][0]['name']
            node['settings']['theme']
        
        operations_time = (time.perf_counter() - start_time) * 1000
        memory_after_ops = PerformanceBenchmark.measure_memory()
        
        # Get performance stats
        stats = node.get_performance_stats()
        
        # Calculate metrics
        creation_memory = memory_after_creation - memory_before
        operations_memory = memory_after_ops - memory_after_creation
        total_memory = memory_after_ops - memory_before
        
        result = {
            'mode': mode.name,
            'creation_time_ms': creation_time,
            'operations_time_ms': operations_time,
            'total_time_ms': creation_time + operations_time,
            'creation_memory_mb': creation_memory,
            'operations_memory_mb': operations_memory,
            'total_memory_mb': total_memory,
            'cache_hit_rate': stats.get('cache_stats', {}).get('hit_rate', 0) * 100,
            'has_adaptive_learning': 'adaptive_learning' in stats,
            'metrics_count': stats.get('adaptive_learning', {}).get('metrics_count', 0)
        }
        
        # Cleanup
        del node
        gc.collect()
        
        return result


class TestPerformanceBenchmark:
    """Test performance benchmarking with detailed metrics."""
    
    def test_comprehensive_performance_benchmark(self, test_data, clean_performance_manager):
        """Comprehensive performance benchmark showing detailed metrics for each mode."""
        
        # Test all performance modes
        modes = [
            PerformanceMode.AUTO,
            PerformanceMode.DEFAULT,
            PerformanceMode.FAST,
            PerformanceMode.OPTIMIZED,
            PerformanceMode.ADAPTIVE,
            PerformanceMode.DUAL_ADAPTIVE
        ]
        
        results = {}
        
        print("\n" + "="*80)
        print("🚀 COMPREHENSIVE PERFORMANCE BENCHMARK")
        print("="*80)
        
        for mode in modes:
            print(f"\n📊 Benchmarking {mode.name} mode...")
            
            try:
                result = PerformanceBenchmark.benchmark_mode(mode, test_data, operations=BENCHMARK_SPEED_OPS)  # Use same ops for fair comparison
                results[mode.name] = result
                
                print(f"   ✅ Creation: {result['creation_time_ms']:.2f}ms")
                print(f"   ✅ Operations: {result['operations_time_ms']:.2f}ms")
                print(f"   ✅ Memory: {result['total_memory_mb']:.2f}MB")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[mode.name] = {'error': str(e)}
        
        # Print detailed comparison table
        self._print_performance_table(results)
        
        # Verify all modes completed successfully
        for mode_name, result in results.items():
            assert 'error' not in result, f"{mode_name} mode failed: {result.get('error')}"
            assert result['creation_time_ms'] < 1000, f"{mode_name} creation too slow: {result['creation_time_ms']:.2f}ms"
            assert result['operations_time_ms'] < 1000, f"{mode_name} operations too slow: {result['operations_time_ms']:.2f}ms"
    
    def test_memory_efficiency_comparison(self, test_data, clean_performance_manager):
        """Compare memory efficiency across performance modes."""
        
        modes = [PerformanceMode.FAST, PerformanceMode.OPTIMIZED, PerformanceMode.ADAPTIVE]
        memory_results = {}
        
        print("\n" + "="*60)
        print("💾 MEMORY EFFICIENCY COMPARISON")
        print("="*60)
        
        for mode in modes:
            result = PerformanceBenchmark.benchmark_mode(mode, test_data, operations=BENCHMARK_SPEED_OPS)  # Use same ops for fair comparison
            memory_results[mode.name] = result
            
            print(f"\n🔍 {mode.name} Mode:")
            print(f"   Creation Memory: {result['creation_memory_mb']:.2f}MB")
            print(f"   Operations Memory: {result['operations_memory_mb']:.2f}MB")
            print(f"   Total Memory: {result['total_memory_mb']:.2f}MB")
            print(f"   Cache Hit Rate: {result['cache_hit_rate']:.1f}%")
        
        # Find most memory efficient
        most_efficient = min(memory_results.items(), key=lambda x: x[1]['total_memory_mb'])
        print(f"\n🏆 Most Memory Efficient: {most_efficient[0]} ({most_efficient[1]['total_memory_mb']:.2f}MB)")
        
        # Verify memory usage is reasonable
        for mode_name, result in memory_results.items():
            assert result['total_memory_mb'] < 100, f"{mode_name} uses too much memory: {result['total_memory_mb']:.2f}MB"
    
    def test_speed_performance_comparison(self, test_data, clean_performance_manager):
        """Compare speed performance across modes."""
        
        modes = [PerformanceMode.FAST, PerformanceMode.DEFAULT, PerformanceMode.ADAPTIVE]
        speed_results = {}
        
        print("\n" + "="*60)
        print("⚡ SPEED PERFORMANCE COMPARISON")
        print("="*60)
        
        for mode in modes:
            result = PerformanceBenchmark.benchmark_mode(mode, test_data, operations=BENCHMARK_SPEED_OPS)  # Controlled by runner configuration
            speed_results[mode.name] = result
            
            print(f"\n🔍 {mode.name} Mode:")
            print(f"   Creation Time: {result['creation_time_ms']:.2f}ms")
            print(f"   Operations Time: {result['operations_time_ms']:.2f}ms")
            print(f"   Total Time: {result['total_time_ms']:.2f}ms")
            print(f"   Operations/sec: {BENCHMARK_SPEED_OPS * 1000/result['operations_time_ms']:.0f}")  # Dynamic calculation
        
        # Find fastest
        fastest = min(speed_results.items(), key=lambda x: x[1]['total_time_ms'])
        print(f"\n🏆 Fastest Mode: {fastest[0]} ({fastest[1]['total_time_ms']:.2f}ms total)")
        
        # Verify speed is reasonable
        for mode_name, result in speed_results.items():
            assert result['total_time_ms'] < 2000, f"{mode_name} too slow: {result['total_time_ms']:.2f}ms"
    
    def test_adaptive_mode_learning_metrics(self, test_data, clean_performance_manager):
        """Test ADAPTIVE mode learning capabilities and metrics."""
        
        print("\n" + "="*60)
        print("🧠 ADAPTIVE MODE LEARNING METRICS")
        print("="*60)
        
        # Benchmark ADAPTIVE mode
        result = PerformanceBenchmark.benchmark_mode(PerformanceMode.ADAPTIVE, test_data, operations=BENCHMARK_SPEED_OPS)  # Use same ops for fair comparison
        
        print(f"\n📊 ADAPTIVE Mode Performance:")
        print(f"   Creation Time: {result['creation_time_ms']:.2f}ms")
        print(f"   Operations Time: {result['operations_time_ms']:.2f}ms")
        print(f"   Memory Usage: {result['total_memory_mb']:.2f}MB")
        print(f"   Cache Hit Rate: {result['cache_hit_rate']:.1f}%")
        print(f"   Has Learning: {result['has_adaptive_learning']}")
        print(f"   Metrics Count: {result['metrics_count']}")
        
        # Verify ADAPTIVE mode characteristics
        assert result['has_adaptive_learning'], "ADAPTIVE mode should have learning capabilities"
        assert result['metrics_count'] > 0, "ADAPTIVE mode should record metrics"
        assert result['cache_hit_rate'] >= 0, "Cache hit rate should be valid"
    
    def _print_performance_table(self, results):
        """Print a detailed performance comparison table."""
        
        print("\n" + "="*100)
        print("📊 DETAILED PERFORMANCE COMPARISON TABLE")
        print("="*100)
        print(f"{'Mode':<12} {'Creation':<10} {'Operations':<12} {'Total':<10} {'Memory':<10} {'Cache%':<8} {'Learning':<10}")
        print("-"*100)
        
        for mode_name, result in results.items():
            if 'error' in result:
                print(f"{mode_name:<12} {'ERROR':<10} {'ERROR':<12} {'ERROR':<10} {'ERROR':<10} {'ERROR':<8} {'ERROR':<10}")
            else:
                learning = "Yes" if result['has_adaptive_learning'] else "No"
                print(f"{mode_name:<12} {result['creation_time_ms']:<10.2f} "
                      f"{result['operations_time_ms']:<12.2f} {result['total_time_ms']:<10.2f} "
                      f"{result['total_memory_mb']:<10.2f} {result['cache_hit_rate']:<8.1f} {learning:<10}")
        
        print("="*100)
        print("📝 Legend: Times in milliseconds, Memory in MB, Cache% = Cache Hit Rate")
