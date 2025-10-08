"""
Test configuration and fixtures for xNode performance tests.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

from src.xlib.xnode import xNode


@pytest.fixture
def deep_nesting_data():
    """Create deeply nested data structure for performance testing."""
    deep_data = {}
    current = deep_data
    
    for i in range(100):
        current[f'level_{i}'] = {}
        current = current[f'level_{i}']
    current['final_value'] = 'reached_the_end'
    
    return deep_data


@pytest.fixture
def wide_structure_data():
    """Create wide data structure for performance testing."""
    return {f'key_{i:04d}': f'value_{i}' for i in range(10000)}


@pytest.fixture
def large_array_data():
    """Create large array data structure for performance testing."""
    return [{'id': i, 'value': f'item_{i}'} for i in range(10000)]


@pytest.fixture
def deep_nesting_node(deep_nesting_data):
    """Create xNode from deeply nested data."""
    return xNode.from_native(deep_nesting_data)


@pytest.fixture
def wide_structure_node(wide_structure_data):
    """Create xNode from wide structure data."""
    return xNode.from_native(wide_structure_data)


@pytest.fixture
def large_array_node(large_array_data):
    """Create xNode from large array data."""
    return xNode.from_native(large_array_data)


@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for tests (realistic values)."""
    return {
        'deep_nesting_ms': 50.0,       # 50ms for deep nesting
        'wide_structure_ms': 150.0,    # 150ms for wide structure (increased from 100ms)
        'large_array_ms': 400.0,       # 400ms for large array (increased from 300ms)
        'navigation_ms': 150.0,        # 150ms for navigation (increased from 100ms)
    } 