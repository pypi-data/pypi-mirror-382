#!/usr/bin/env python3
"""
xNode Performance Benchmarks.

This module provides comprehensive performance benchmarks for the xNode library,
demonstrating its performance characteristics across different scenarios and data sizes.

Software Architect: Eng. Muhammad AlShehri
Developer: Eng. Muhammad AlShehri
Tester: Eng. Muhammad AlShehri
Company: eXonware.com
"""

import time
import json
import random
import string
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from statistics import mean, median, stdev

from .. import xNode, PerformanceMode, get_metrics, get_pool_stats


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
    test_name: str
    performance_mode: str
    data_size: int
    operation_count: int
    total_time: float
    avg_time_per_op: float
    memory_usage_mb: float
    cache_hit_rate: float
    pool_efficiency: float


class xNodeBenchmark:
    """Comprehensive benchmark suite for xNode performance testing."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.metrics = get_metrics()
    
    def generate_test_data(self, size: str = 'medium') -> Dict[str, Any]:
        """Generate test data of specified size."""
        if size == 'small':
            return {
                'users': [
                    {'id': i, 'name': f'User{i}', 'email': f'user{i}@example.com'}
                    for i in range(100)
                ],
                'settings': {
                    'theme': 'dark',
                    'language': 'en',
                    'notifications': True
                }
            }
        elif size == 'medium':
            return {
                'users': [
                    {
                        'id': i,
                        'name': f'User{i}',
                        'email': f'user{i}@example.com',
                        'profile': {
                            'age': random.randint(18, 80),
                            'location': f'City{i}',
                            'interests': [f'interest{j}' for j in range(5)]
                        }
                    }
                    for i in range(1000)
                ],
                'products': [
                    {
                        'id': f'prod{i}',
                        'name': f'Product{i}',
                        'price': round(random.uniform(10, 1000), 2),
                        'category': random.choice(['electronics', 'clothing', 'books'])
                    }
                    for i in range(500)
                ]
            }
        else:  # large
            return {
                'users': [
                    {
                        'id': i,
                        'name': f'User{i}',
                        'email': f'user{i}@example.com',
                        'profile': {
                            'age': random.randint(18, 80),
                            'location': f'City{i}',
                            'interests': [f'interest{j}' for j in range(10)],
                            'preferences': {
                                'theme': random.choice(['light', 'dark']),
                                'language': random.choice(['en', 'es', 'fr', 'de']),
                                'timezone': f'UTC+{random.randint(-12, 12)}'
                            }
                        },
                        'orders': [
                            {
                                'order_id': f'order{i}_{j}',
                                'items': [
                                    {
                                        'product_id': f'prod{k}',
                                        'quantity': random.randint(1, 5),
                                        'price': round(random.uniform(10, 500), 2)
                                    }
                                    for k in range(random.randint(1, 5))
                                ]
                            }
                            for j in range(random.randint(0, 10))
                        ]
                    }
                    for i in range(10000)
                ]
            }
    
    def benchmark_creation(self, data: Dict[str, Any], mode: PerformanceMode) -> BenchmarkResult:
        """Benchmark node creation performance."""
        start_time = time.time()
        
        # Create xNode with specified mode
        if mode == PerformanceMode.FAST:
            node = xNode.fast(data)
        elif mode == PerformanceMode.OPTIMIZED:
            node = xNode.optimized(data)
        elif mode == PerformanceMode.ADAPTIVE:
            node = xNode.adaptive(data)
        elif mode == PerformanceMode.DUAL_ADAPTIVE:
            node = xNode.dual_adaptive(data)
        else:
            node = xNode.from_native(data, mode)
        
        end_time = time.time()
        
        # Get metrics
        pool_stats = get_pool_stats()
        
        return BenchmarkResult(
            test_name="Node Creation",
            performance_mode=str(mode),
            data_size=len(json.dumps(data)),
            operation_count=1,
            total_time=end_time - start_time,
            avg_time_per_op=end_time - start_time,
            memory_usage_mb=self._get_memory_usage(),
            cache_hit_rate=self.metrics.get('cache_hit_rate', 0.0),
            pool_efficiency=pool_stats.get('efficiency', 0.0)
        )
    
    def benchmark_navigation(self, node: xNode, paths: List[str], mode: PerformanceMode) -> BenchmarkResult:
        """Benchmark path navigation performance."""
        start_time = time.time()
        
        # Navigate to each path
        for path in paths:
            try:
                node.find(path)
            except:
                pass  # Ignore errors for benchmarking
        
        end_time = time.time()
        
        # Get metrics
        pool_stats = get_pool_stats()
        
        return BenchmarkResult(
            test_name="Path Navigation",
            performance_mode=str(mode),
            data_size=0,  # Not relevant for navigation
            operation_count=len(paths),
            total_time=end_time - start_time,
            avg_time_per_op=(end_time - start_time) / len(paths),
            memory_usage_mb=self._get_memory_usage(),
            cache_hit_rate=self.metrics.get('cache_hit_rate', 0.0),
            pool_efficiency=pool_stats.get('efficiency', 0.0)
        )
    
    def benchmark_serialization(self, node: xNode, mode: PerformanceMode) -> BenchmarkResult:
        """Benchmark serialization performance."""
        start_time = time.time()
        
        # Serialize to native data
        native_data = node.to_native()
        
        end_time = time.time()
        
        # Get metrics
        pool_stats = get_pool_stats()
        
        return BenchmarkResult(
            test_name="Native Serialization",
            performance_mode=str(mode),
            data_size=len(str(native_data)),
            operation_count=1,
            total_time=end_time - start_time,
            avg_time_per_op=end_time - start_time,
            memory_usage_mb=self._get_memory_usage(),
            cache_hit_rate=self.metrics.get('cache_hit_rate', 0.0),
            pool_efficiency=pool_stats.get('efficiency', 0.0)
        )
    
    def benchmark_iteration(self, node: xNode, mode: PerformanceMode) -> BenchmarkResult:
        """Benchmark iteration performance."""
        start_time = time.time()
        
        # Iterate through all nodes
        count = 0
        for _ in node:
            count += 1
        
        end_time = time.time()
        
        # Get metrics
        pool_stats = get_pool_stats()
        
        return BenchmarkResult(
            test_name="Node Iteration",
            performance_mode=str(mode),
            data_size=0,  # Not relevant for iteration
            operation_count=count,
            total_time=end_time - start_time,
            avg_time_per_op=(end_time - start_time) / count if count > 0 else 0,
            memory_usage_mb=self._get_memory_usage(),
            cache_hit_rate=self.metrics.get('cache_hit_rate', 0.0),
            pool_efficiency=pool_stats.get('efficiency', 0.0)
        )
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def run_comprehensive_benchmark(self) -> List[BenchmarkResult]:
        """Run comprehensive benchmark across all performance modes and data sizes."""
        print("🚀 Starting xNode Comprehensive Performance Benchmark")
        print("=" * 60)
        
        data_sizes = ['small', 'medium', 'large']
        performance_modes = [
            PerformanceMode.FAST,
            PerformanceMode.OPTIMIZED,
            PerformanceMode.ADAPTIVE,
            PerformanceMode.DUAL_ADAPTIVE
        ]
        
        for data_size in data_sizes:
            print(f"\n📊 Testing {data_size.upper()} dataset")
            print("-" * 40)
            
            # Generate test data
            test_data = self.generate_test_data(data_size)
            
            for mode in performance_modes:
                print(f"  🔧 Testing {mode} mode...")
                
                # Reset metrics
                self.metrics.reset()
                
                # Benchmark creation
                creation_result = self.benchmark_creation(test_data, mode)
                self.results.append(creation_result)
                
                # Create node for other tests
                if mode == PerformanceMode.FAST:
                    node = xNode.fast(test_data)
                elif mode == PerformanceMode.OPTIMIZED:
                    node = xNode.optimized(test_data)
                elif mode == PerformanceMode.ADAPTIVE:
                    node = xNode.adaptive(test_data)
                elif mode == PerformanceMode.DUAL_ADAPTIVE:
                    node = xNode.dual_adaptive(test_data)
                
                # Generate test paths
                test_paths = self._generate_test_paths(test_data, 100)
                
                # Benchmark navigation
                nav_result = self.benchmark_navigation(node, test_paths, mode)
                self.results.append(nav_result)
                
                # Benchmark serialization
                ser_result = self.benchmark_serialization(node, mode)
                self.results.append(ser_result)
                
                # Benchmark iteration
                iter_result = self.benchmark_iteration(node, mode)
                self.results.append(iter_result)
        
        return self.results
    
    def _generate_test_paths(self, data: Dict[str, Any], count: int) -> List[str]:
        """Generate test paths for navigation benchmarking."""
        paths = []
        
        def extract_paths(obj, current_path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    paths.append(new_path)
                    if len(paths) >= count:
                        return
                    extract_paths(value, new_path)
            elif isinstance(obj, list):
                for i, value in enumerate(obj[:10]):  # Limit to first 10 items
                    new_path = f"{current_path}[{i}]"
                    paths.append(new_path)
                    if len(paths) >= count:
                        return
                    extract_paths(value, new_path)
        
        extract_paths(data)
        return paths[:count]
    
    def print_results(self):
        """Print benchmark results in a formatted table."""
        print("\n📈 BENCHMARK RESULTS")
        print("=" * 80)
        
        # Group results by test name
        test_groups = {}
        for result in self.results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)
        
        for test_name, results in test_groups.items():
            print(f"\n🔍 {test_name.upper()}")
            print("-" * 60)
            print(f"{'Mode':<15} {'Data Size':<12} {'Ops':<6} {'Total Time':<12} {'Avg Time':<12} {'Memory':<10} {'Cache':<8} {'Pool':<8}")
            print("-" * 80)
            
            for result in results:
                print(f"{result.performance_mode:<15} {result.data_size:<12} {result.operation_count:<6} "
                      f"{result.total_time*1000:<11.2f}ms {result.avg_time_per_op*1000:<11.2f}ms "
                      f"{result.memory_usage_mb:<9.1f}MB {result.cache_hit_rate:<7.2%} {result.pool_efficiency:<7.2%}")
    
    def export_results(self, filename: str = 'xnode_benchmark_results.json'):
        """Export benchmark results to JSON file."""
        results_dict = []
        for result in self.results:
            results_dict.append({
                'test_name': result.test_name,
                'performance_mode': result.performance_mode,
                'data_size': result.data_size,
                'operation_count': result.operation_count,
                'total_time': result.total_time,
                'avg_time_per_op': result.avg_time_per_op,
                'memory_usage_mb': result.memory_usage_mb,
                'cache_hit_rate': result.cache_hit_rate,
                'pool_efficiency': result.pool_efficiency
            })
        
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n💾 Results exported to {filename}")


def main():
    """Main benchmark runner."""
    benchmark = xNodeBenchmark()
    results = benchmark.run_comprehensive_benchmark()
    benchmark.print_results()
    benchmark.export_results()


if __name__ == "__main__":
    main()
