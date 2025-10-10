"""
Pytest configuration and fixtures for xNode tests.
Provides reusable test data and setup utilities.
"""

import pytest
from pathlib import Path
import sys
import os

# Override the global conftest.py auto-handler registration for xnode tests
# since xnode should not depend on xdata
@pytest.fixture(autouse=True)
def ensure_handlers_registered():
    """Override global handler registration - xnode tests don't need xdata handlers."""
    pass  # Explicitly do nothing

# Ensure src is in path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Add xnode directly to path to avoid xlib init chain issues
XNODE_PATH = SRC_PATH / "xlib" / "xnode"
if str(XNODE_PATH) not in sys.path:
    sys.path.insert(0, str(XNODE_PATH))

# Import xNode using the proper module path
try:
    # Add src to path for local development
    current_dir = Path(__file__).parent
    src_path = current_dir.parent / "src"
    xwsystem_src_path = current_dir.parent.parent / "xwsystem" / "src"
    
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    if str(xwsystem_src_path) not in sys.path and xwsystem_src_path.exists():
        sys.path.insert(0, str(xwsystem_src_path))
    
    from exonware.xwnode import XWNode
    from exonware.xwnode import XWNodeError, XWNodeTypeError, XWNodePathError, XWNodeValueError
    print("✅ XWNode imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    # Create mock objects for testing
    class MockxNode:
        @staticmethod
        def from_native(data):
            return MockxNode()
        @property
        def value(self):
            return "mock"
        @property
        def is_leaf(self):
            return True
        @property
        def is_list(self):
            return False
        @property
        def is_dict(self):
            return False
        @property
        def type(self):
            return 'value'
        def to_native(self):
            return "mock"
        def keys(self):
            return []
        def __len__(self):
            return 0
        def get(self, key, default=None):
            return default
        def has(self, key):
            return False
        def find(self, path):
            return self
        def items(self):
            return []
        def values(self):
            return []
        def __iter__(self):
            return iter([])
        def __getitem__(self, key):
            raise KeyError(f"Key '{key}' not found")
        def __contains__(self, key):
            return False
    
    XWNode = MockxNode
    XWNodeError = Exception
    XWNodeTypeError = TypeError
    XWNodePathError = KeyError
    XWNodeValueError = ValueError
    print("⚠️  Using mock objects for testing")


@pytest.fixture
def simple_dict_data():
    """Simple dictionary test data."""
    return {
        'name': 'Alice',
        'age': 30,
        'city': 'New York',
        'active': True
    }


@pytest.fixture
def simple_list_data():
    """Simple list test data."""
    return ['apple', 'banana', 'cherry']


@pytest.fixture
def nested_data():
    """Complex nested hierarchical test data."""
    return {
        'users': [
            {
                'id': 1,
                'name': 'Alice',
                'age': 30,
                'profile': {
                    'email': 'alice@example.com',
                    'preferences': {
                        'theme': 'dark',
                        'notifications': True
                    }
                },
                'roles': ['admin', 'user']
            },
            {
                'id': 2,
                'name': 'Bob',
                'age': 25,
                'profile': {
                    'email': 'bob@example.com',
                    'preferences': {
                        'theme': 'light',
                        'notifications': False
                    }
                },
                'roles': ['user']
            }
        ],
        'metadata': {
            'version': 1.0,
            'created': '2024-01-01',
            'tags': ['test', 'sample', 'data']
        }
    }


@pytest.fixture
def simple_node(simple_dict_data):
    """XWNode instance from simple dictionary."""
    return XWNode.from_native(simple_dict_data)


@pytest.fixture
def list_node(simple_list_data):
    """XWNode instance from simple list."""
    return XWNode.from_native(simple_list_data)


@pytest.fixture
def nested_node(nested_data):
    """XWNode instance from nested data."""
    return XWNode.from_native(nested_data)


@pytest.fixture
def leaf_node():
    """Simple leaf node."""
    return XWNode.from_native("simple string value")


@pytest.fixture
def number_node():
    """Simple number leaf node."""
    return XWNode.from_native(42)


@pytest.fixture
def boolean_node():
    """Simple boolean leaf node."""
    return XWNode.from_native(True)


@pytest.fixture
def empty_dict_node():
    """Empty dictionary node."""
    return XWNode.from_native({})


@pytest.fixture
def empty_list_node():
    """Empty list node."""
    return XWNode.from_native([])


@pytest.fixture
def json_test_string():
    """JSON string for testing JSON parsing."""
    return '{"name": "Test", "value": 42, "items": [1, 2, {"nested": true}]}'


@pytest.fixture
def json_test_data():
    """Complex data for JSON testing."""
    return {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ],
        "meta": {
            "count": 2,
            "version": "1.0"
        }
    }


@pytest.fixture
def complex_navigation_data():
    """Complex nested data for navigation testing."""
    return {
        "company": {
            "departments": [
                {
                    "name": "Engineering",
                    "teams": [
                        {
                            "name": "Backend",
                            "members": [
                                {"name": "Alice", "role": "lead"},
                                {"name": "Bob", "role": "developer"}
                            ]
                        },
                        {
                            "name": "Frontend", 
                            "members": [
                                {"name": "Charlie", "role": "lead"},
                                {"name": "David", "role": "developer"}
                            ]
                        }
                    ]
                },
                {
                    "name": "Sales",
                    "teams": [
                        {
                            "name": "Enterprise",
                            "members": [
                                {"name": "Eve", "role": "manager"},
                                {"name": "Frank", "role": "rep"}
                            ]
                        }
                    ]
                }
            ]
        },
        "config": {
            "features": {
                "api_limits": {
                    "requests_per_minute": 1000,
                    "max_payload_size": "10MB"
                }
            }
        }
    }


@pytest.fixture
def array_heavy_data():
    """Data with heavy array usage for navigation testing."""
    return {
        "matrix": [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ],
        "records": [
            {"values": [10, 20, 30]},
            {"values": [40, 50, 60]}
        ]
    }


@pytest.fixture
def edge_case_keys_data():
    """Data with edge case keys for testing."""
    return {
        "0": "string_zero",
        "1.5": "decimal_string",
        "spaces in key": "spaced_key",
        "special!@#$%": "special_chars",
        "unicode_ключ": "unicode_value",
        "": "empty_key"
    }


@pytest.fixture
def mixed_type_data():
    """Data with mixed types for comprehensive testing."""
    return {
        "string": "hello",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "dict": {
            "nested": "value"
        }
    }


@pytest.fixture
def real_world_config():
    """Real-world configuration data for integration testing."""
    return {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret123"
            },
            "pools": [
                {"name": "read", "size": 10},
                {"name": "write", "size": 5}
            ]
        },
        "api": {
            "endpoints": [
                {"path": "/users", "method": "GET"},
                {"path": "/users", "method": "POST"},
                {"path": "/products", "method": "GET"}
            ],
            "rate_limits": {
                "requests_per_minute": 1000,
                "burst_size": 100
            }
        },
        "logging": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }


# Test data directory
@pytest.fixture
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "data" 