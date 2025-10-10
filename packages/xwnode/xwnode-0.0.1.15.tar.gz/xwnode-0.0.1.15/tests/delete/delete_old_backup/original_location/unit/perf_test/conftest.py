"""
Test configuration and fixtures for xNode performance tests.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

from xlib.xnode import xNode


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
        'deep_nesting_ms': 20.0,      # 20ms for deep nesting
        'wide_structure_ms': 50.0,     # 50ms for wide structure
        'large_array_ms': 50.0,        # 50ms for large array
        'navigation_ms': 5.0,          # 5ms for navigation
    } 