# xNode Test Suite

Comprehensive test suite for xNode functionality, following the established patterns and pytest best practices.

## Overview

This test package provides complete coverage of the xNode library, which offers a lightweight interface for representing and navigating hierarchical data structures.

## Structure

```
tests/packages/xnode/
├── __init__.py                 # Package initialization
├── conftest.py                 # Global fixtures and configuration
├── runner.py                   # Main test runner
├── README.md                   # This file
└── unit/                       # Unit tests organized by component
    ├── core_tests/             # Core XNode functionality
    │   ├── test_xnode_core.py
    │   ├── runner.py
    │   ├── conftest.py
    │   └── README.md
    ├── navigation_tests/       # Path resolution and navigation
    │   ├── test_navigation.py
    │   ├── runner.py
    │   ├── conftest.py
    │   └── README.md
    ├── error_tests/            # Error handling and edge cases
    │   ├── test_errors.py
    │   ├── runner.py
    │   ├── conftest.py
    │   └── README.md
    ├── model_tests/            # Internal model components
    │   ├── test_model.py
    │   ├── runner.py
    │   ├── conftest.py
    │   └── README.md
    └── integration_tests/      # Complex integration scenarios
        ├── test_integration.py
        ├── runner.py
        ├── conftest.py
        └── README.md
```

## Running Tests

### Method 1: Main Runner (Recommended)

```bash
# Run all xNode tests
cd tests/packages/xnode
python runner.py

# Run with verbose output
python runner.py -v

# Run with coverage report
python runner.py -c

# Run specific component tests
python runner.py -t core        # Core functionality
python runner.py -t navigation  # Navigation and path resolution
python runner.py -t errors      # Error handling
python runner.py -t model       # Internal model
python runner.py -t integration # Integration tests

# List available components
python runner.py -l
```

### Method 2: Direct pytest

```bash
# Run all xNode tests
python -m pytest tests/packages/xnode/ -v

# Run specific component
python -m pytest tests/packages/xnode/unit/core_tests/ -v

# Run with coverage
python -m pytest tests/packages/xnode/ --cov=xlib.xnode --cov-report=html
```

### Method 3: Component-specific runners

```bash
# Core tests
cd tests/packages/xnode/unit/core_tests
python runner.py -v

# Navigation tests
cd tests/packages/xnode/unit/navigation_tests
python runner.py -v

# And so on for other components...
```

## Test Components

### 🏗️ Core Tests (`core_tests/`)
- ✅ XNode factory methods (from_python, from_json)
- ✅ Basic properties and type checking
- ✅ Node creation and initialization
- ✅ String representations and conversions

### 🧭 Navigation Tests (`navigation_tests/`)
- ✅ Path resolution with dot notation
- ✅ Bracket notation access
- ✅ Mixed path formats
- ✅ Deep navigation in complex structures
- ✅ get() method with defaults

### ❌ Error Tests (`error_tests/`)
- ✅ XNodePathError scenarios
- ✅ XNodeTypeError conditions
- ✅ XNodeValueError handling
- ✅ Edge cases and boundary conditions

### 🔧 Model Tests (`model_tests/`)
- ✅ ANode abstract base functionality
- ✅ ANodeLeaf primitive values
- ✅ ANodeList array operations
- ✅ ANodeDict mapping operations
- ✅ ANodeFactory tree building

### 🔗 Integration Tests (`integration_tests/`)
- ✅ Complex hierarchical data operations
- ✅ Large data structure navigation
- ✅ Performance with deep nesting
- ✅ Real-world usage scenarios

## Test Features

### Data Fixtures
- Simple and complex test data
- Nested hierarchical structures
- Edge cases (empty containers, null values)
- JSON parsing test data

### Error Testing
- Comprehensive exception coverage
- Path resolution error scenarios
- Type mismatch error conditions
- Boundary condition testing

### Performance Testing
- Large data structure handling
- Deep nesting performance
- Memory usage patterns
- Navigation efficiency

## Test Markers

Tests are organized with pytest markers for selective execution:

- `@pytest.mark.core` - Core functionality tests
- `@pytest.mark.navigation` - Navigation and path tests
- `@pytest.mark.errors` - Error handling tests
- `@pytest.mark.model` - Internal model tests
- `@pytest.mark.integration` - Integration scenario tests
- `@pytest.mark.performance` - Performance-related tests

## Dependencies

- pytest >= 6.0
- pytest-cov (for coverage reports)
- Python 3.8+ (xNode requirement)

## Development

When adding new tests:

1. Follow the established naming conventions
2. Use appropriate fixtures from conftest.py
3. Add proper pytest markers
4. Update component runners if needed
5. Maintain documentation coverage

## Coverage Goals

- 🎯 Target: 95% code coverage
- 🔍 Focus: All public API methods
- ✅ Include: Error conditions and edge cases
- 📊 Monitor: Performance regression prevention 