# xNode Test Suite - Reorganized Structure

Comprehensive test suite for the xNode library with proper organization following SRP and testing best practices.

## Overview

This test package provides complete coverage of the xNode library's refactored architecture:
- Core functionality (`xNodeCore`)
- Performance management (`PerformanceModes`)
- Data structures (`DataStructures`) 
- Graph operations (`GraphOperations`)
- Query operations (`QueryOperations`)
- Production-grade optimization (`UniversalOptimizer`)

## New Organized Structure

```
src/xlib/xnode/tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Global fixtures and configuration
├── runner.py                      # Main test runner
├── README.md                      # This documentation
├── run_all_tests.py              # Comprehensive test execution
│
├── unit/                          # Unit tests by component
│   ├── __init__.py
│   ├── core/                      # Core xNode functionality
│   │   ├── __init__.py
│   │   ├── test_xnode_core.py     # Core node operations
│   │   ├── test_facade.py         # Public facade interface
│   │   ├── conftest.py
│   │   └── README.md
│   │
│   ├── performance/               # Performance management
│   │   ├── __init__.py
│   │   ├── test_performance_modes.py   # Performance mode management
│   │   ├── test_optimization.py        # Optimization strategies
│   │   ├── conftest.py
│   │   └── README.md
│   │
│   ├── structures/                # Data structure views
│   │   ├── __init__.py
│   │   ├── test_linear.py         # LinkedList, Stack, Queue, Deque
│   │   ├── test_trees.py          # Trie, Heap, SkipList
│   │   ├── test_graphs.py         # Union-Find, FSM, DAG, Flow
│   │   ├── test_advanced.py       # Neural Graph, Hypergraph
│   │   ├── conftest.py
│   │   └── README.md
│   │
│   ├── graph/                     # Graph operations
│   │   ├── __init__.py
│   │   ├── test_graph_ops.py      # Basic graph operations
│   │   ├── test_algorithms.py     # Graph algorithms
│   │   ├── conftest.py
│   │   └── README.md
│   │
│   ├── query/                     # Query operations
│   │   ├── __init__.py
│   │   ├── test_native_query.py   # Native query functionality
│   │   ├── test_query_builder.py  # Legacy query builder
│   │   ├── conftest.py
│   │   └── README.md
│   │
│   └── integration/               # Integration tests
│       ├── __init__.py
│       ├── test_end_to_end.py     # Complete workflows
│       ├── test_modular_integration.py  # Cross-module testing
│       ├── conftest.py
│       └── README.md
│
├── benchmarks/                    # Performance benchmarks
│   ├── __init__.py
│   ├── benchmarks.py              # Main benchmark suite
│   ├── test_performance_regression.py  # Regression testing
│   ├── conftest.py
│   └── README.md
│
└── utilities/                     # Test utilities and helpers
    ├── __init__.py
    ├── fixtures.py                # Common test fixtures
    ├── helpers.py                 # Test helper functions
    └── data/                      # Test data files
        ├── sample_data.json
        ├── large_dataset.json
        └── edge_cases.json
```

## Running Tests

### Comprehensive Test Execution
```bash
# Run all tests with coverage
cd src/xlib/xnode/tests
python run_all_tests.py --coverage

# Run specific component tests
python run_all_tests.py --component core
python run_all_tests.py --component performance
python run_all_tests.py --component structures

# Run with different options
python run_all_tests.py --verbose --parallel
```

### Component-Specific Testing
```bash
# Core functionality
python -m pytest unit/core/ -v

# Performance management  
python -m pytest unit/performance/ -v

# Data structures
python -m pytest unit/structures/ -v

# Graph operations
python -m pytest unit/graph/ -v

# Query operations
python -m pytest unit/query/ -v

# Integration tests
python -m pytest unit/integration/ -v
```

### Benchmarks and Performance
```bash
# Run performance benchmarks
python -m pytest benchmarks/ -v

# Performance regression testing
python benchmarks/test_performance_regression.py
```

## Test Organization Principles

### Single Responsibility
- Each test file focuses on one specific component or functionality
- Clear separation between unit tests, integration tests, and benchmarks
- Modular test structure matching the refactored codebase

### Comprehensive Coverage
- **Core Tests**: Basic functionality, facade interface, error handling
- **Performance Tests**: Mode management, optimization strategies, health monitoring
- **Structure Tests**: All data structure behavioral views
- **Graph Tests**: Operations, algorithms, traversal strategies
- **Query Tests**: Native queries, query builder, search operations
- **Integration Tests**: End-to-end workflows, cross-component interactions

### Best Practices
- Consistent fixture usage across all test modules
- Proper test isolation and cleanup
- Performance regression prevention
- Clear test documentation and examples
- Maintainable test code following project standards

## Coverage Goals

- 🎯 **Target**: 95% code coverage across all components
- 🔍 **Focus**: All public API methods and error conditions
- ✅ **Include**: Edge cases, performance scenarios, integration paths
- 📊 **Monitor**: Performance regression prevention and optimization effectiveness

## Development Guidelines

When adding new tests:

1. **Follow the modular structure** - place tests in appropriate component directories
2. **Use consistent naming** - `test_[component]_[functionality].py`
3. **Leverage shared fixtures** - use `conftest.py` files appropriately
4. **Add proper markers** - use pytest markers for test categorization
5. **Update documentation** - maintain README files for each component
6. **Include performance tests** - ensure optimization changes don't regress performance

## Dependencies

- pytest >= 6.0
- pytest-cov (for coverage reports)
- pytest-xdist (for parallel execution)
- pytest-benchmark (for performance testing)
- Python 3.8+ (xNode requirement)

This reorganized test structure ensures maintainability, comprehensive coverage, and alignment with the refactored xNode architecture.
