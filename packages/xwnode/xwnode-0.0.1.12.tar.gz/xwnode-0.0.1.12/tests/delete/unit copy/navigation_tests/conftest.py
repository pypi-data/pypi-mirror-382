"""
Navigation tests specific configuration and fixtures.
"""

import pytest
from pathlib import Path
import sys

# Import parent conftest fixtures
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import *  # Import all parent fixtures

# Additional navigation-specific fixtures
@pytest.fixture
def complex_navigation_data():
    """Complex data structure for navigation testing."""
    return {
        'company': {
            'name': 'TechCorp',
            'departments': [
                {
                    'name': 'Engineering',
                    'teams': [
                        {
                            'name': 'Backend',
                            'members': [
                                {'name': 'Alice', 'role': 'lead'},
                                {'name': 'Bob', 'role': 'developer'}
                            ]
                        },
                        {
                            'name': 'Frontend', 
                            'members': [
                                {'name': 'Charlie', 'role': 'lead'},
                                {'name': 'Diana', 'role': 'developer'}
                            ]
                        }
                    ]
                },
                {
                    'name': 'Sales',
                    'teams': [
                        {
                            'name': 'Enterprise',
                            'members': [
                                {'name': 'Eve', 'role': 'manager'},
                                {'name': 'Frank', 'role': 'rep'}
                            ]
                        }
                    ]
                }
            ]
        },
        'config': {
            'version': '2.1.0',
            'features': {
                'auth': True,
                'analytics': False,
                'api_limits': {
                    'requests_per_minute': 1000,
                    'max_payload_size': '10MB'
                }
            }
        }
    }


@pytest.fixture
def array_heavy_data():
    """Data structure with multiple array levels for testing."""
    return {
        'matrix': [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ],
        'records': [
            {'id': 1, 'values': [10, 20, 30]},
            {'id': 2, 'values': [40, 50, 60]},
            {'id': 3, 'values': [70, 80, 90]}
        ]
    }


@pytest.fixture
def edge_case_keys_data():
    """Data with edge case key names for testing."""
    return {
        '': 'empty_key',
        '0': 'string_zero',
        '1.5': 'decimal_string',
        'dots.in.key': 'dotted_key',
        'spaces in key': 'spaced_key',
        'special!@#$%': 'special_chars',
        'unicode_ключ': 'unicode_value'
    } 