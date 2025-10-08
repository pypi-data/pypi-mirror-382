"""
Error tests specific configuration and fixtures.
"""

import pytest
from pathlib import Path
import sys

# Import parent conftest fixtures
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import *  # Import all parent fixtures

# Additional error-specific fixtures
@pytest.fixture
def problematic_data():
    """Data that might cause various edge case scenarios."""
    return {
        'normal': 'value',
        'empty_dict': {},
        'empty_list': [],
        'null_value': None,
        'nested_nulls': {
            'level1': {
                'null_here': None,
                'empty_here': {}
            }
        }
    } 