"""
Hash Map Node Strategy Implementation

This module implements the HASH_MAP strategy for fast key-value operations
using Python's built-in dictionary.
"""

from typing import Any, Iterator, Dict, List, Optional, Union
from .base import ANodeStrategy
from ...types import NodeMode, NodeTrait


class HashMapStrategy(ANodeStrategy):
    """
    Hash Map node strategy for fast O(1) key-value operations.
    
    Uses Python's built-in dictionary for optimal performance
    with associative operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the hash map strategy."""
        super().__init__(data=None, **options)
        self._mode = NodeMode.HASH_MAP
        self._traits = traits
        self._data: Dict[str, Any] = {}
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the hash map strategy."""
        return (NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """Store a key-value pair."""
        str_key = str(key)
        self._data[str_key] = value
    
    def find(self, key: Any) -> Any:
        """Retrieve a value by key."""
        str_key = str(key)
        return self._data.get(str_key)
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        str_key = str(key)
        if str_key in self._data:
            del self._data[str_key]
            return True
        return False
    
    def size(self) -> int:
        """Get the number of items."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if the structure is empty."""
        return len(self._data) == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        return self._data.copy()
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._data.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        return iter(self._data.items())
    
    # ============================================================================
    # HASH MAP SPECIFIC OPERATIONS
    # ============================================================================
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value with default."""
        str_key = str(key)
        return self._data.get(str_key, default)
    
    def setdefault(self, key: Any, default: Any = None) -> Any:
        """Set default value if key doesn't exist."""
        str_key = str(key)
        return self._data.setdefault(str_key, default)
    
    def update(self, other: Dict[str, Any]) -> None:
        """Update with another dictionary."""
        self._data.update(other)
    
    def pop(self, key: Any, default: Any = None) -> Any:
        """Remove and return value."""
        str_key = str(key)
        return self._data.pop(str_key, default)
    
    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'HASH_MAP',
            'backend': 'Python dict',
            'complexity': {
                'get': 'O(1)',
                'put': 'O(1)',
                'delete': 'O(1)',
                'keys': 'O(n)',
                'values': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': len(self._data),
            'memory_usage': f"{len(self._data) * 24} bytes (estimated)",
            'load_factor': 'N/A (Python dict)'
        }
