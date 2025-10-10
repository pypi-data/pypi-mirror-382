# xNode Performance Tests

This directory contains performance benchmarking and profiling tests for xNode operations.

## Structure

```
perf_test/
├── __init__.py              # Package initialization
├── conftest.py              # Test configuration and fixtures
├── test_performance.py      # Main performance benchmark tests
├── runner.py                # Test runner utility
├── perf_xnode.py            # Performance benchmark script
├── perf_xnode.csv           # Performance results log
└── README.md                # This file
```

## Running Tests

### Method 1: Direct pytest
```bash
# Run all performance tests
python -m pytest tests/packages/xnode/unit/perf_test/ -v

# Run specific test file
python -m pytest tests/packages/xnode/unit/perf_test/test_performance.py -v

# Run with coverage
python -m pytest tests/packages/xnode/unit/perf_test/ --cov=xlib.xnode --cov-report=html
```

### Method 2: Using runner
```bash
cd tests/packages/xnode/unit/perf_test
python runner.py                    # Basic run
python runner.py -v                 # Verbose
python runner.py -c                 # With coverage
python runner.py -b                 # Run benchmark
```

### Method 3: Direct benchmark execution
```bash
cd tests/packages/xnode/unit/perf_test
python perf_xnode.py                # Run performance benchmark
```

## Performance Scenarios

The performance tests cover:

- ✅ Deep nesting performance (100 levels)
- ✅ Wide structure performance (10,000 keys)
- ✅ Large array performance (10,000 elements)
- ✅ Navigation performance (path-based and bracket-based)
- ✅ Memory usage profiling
- ✅ Iteration performance

## Results Tracking

Performance results are automatically logged to `perf_xnode.csv` with:
- Timestamp
- xNode version
- Average execution times for each scenario
- Historical tracking for performance improvements

## Benchmark Configuration

- **Iterations**: 1000 runs per scenario
- **Measurement**: High-precision timing using `time.perf_counter()`
- **Output**: CSV format for easy analysis
- **Scenarios**: Deep nesting, wide structure, large arrays 