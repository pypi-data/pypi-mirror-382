# xNode Core Tests

This directory contains unit tests for core xNode functionality.

## Structure

```
core_tests/
├── __init__.py              # Package initialization
├── conftest.py              # Test configuration and fixtures
├── test_xnode_core.py       # Main core functionality tests
├── runner.py                # Test runner utility
└── README.md                # This file
```

## Running Tests

### Method 1: Direct pytest
```bash
# Run all core tests
python -m pytest tests/packages/xnode/unit/core_tests/ -v

# Run specific test file
python -m pytest tests/packages/xnode/unit/core_tests/test_xnode_core.py -v

# Run with coverage
python -m pytest tests/packages/xnode/unit/core_tests/ --cov=xlib.xnode --cov-report=html
```

### Method 2: Using runner
```bash
cd tests/packages/xnode/unit/core_tests
python runner.py                    # Basic run
python runner.py -v                 # Verbose
python runner.py -c                 # With coverage
python runner.py -t test_specific   # Specific test
```

### Method 3: Direct execution
```bash
cd tests/packages/xnode/unit/core_tests
python test_xnode_core.py
```

## Test Coverage

The core tests cover:

- ✅ XNode factory methods (from_python, from_json)
- ✅ Basic properties and type checking
- ✅ Node creation and initialization
- ✅ String representations and conversions
- ✅ Container operations (len, iter, keys, items)
- ✅ Bracket notation access
- ✅ JSON parsing and conversion
- ✅ Empty container handling 