"""
Hash Map Node Strategy Implementation

This module implements the HASH_MAP strategy for fast key-value operations
using Python's built-in dictionary.
"""

from typing import Any, Iterator, Dict, List, Optional, Union
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait
from ..utils import (
    safe_to_native_conversion,
    is_list_like,
    create_basic_metrics,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class xHashMapStrategy(aNodeStrategy):
    """
    Hash Map node strategy for fast O(1) key-value operations.
    
    Uses Python's built-in dictionary for optimal performance
    with associative operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the hash map strategy."""
        super().__init__(NodeMode.HASH_MAP, traits, **options)
        self._data: Dict[str, Any] = {}
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the hash map strategy."""
        return (NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        str_key = str(key)
        if str_key not in self._data:
            update_size_tracker(self._size_tracker, 1)
        self._data[str_key] = value
        record_access(self._access_tracker, 'put_count')
    
    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve a value by path."""
        record_access(self._access_tracker, 'get_count')
        
        # Handle simple key lookup
        if '.' not in path:
            return self._data.get(path, default)
        
        # Handle path navigation
        parts = path.split('.')
        current = self._data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return str(key) in self._data
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.get(path) is not None
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair."""
        str_key = str(key)
        if str_key in self._data:
            del self._data[str_key]
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            return True
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair (alias for remove)."""
        return self.remove(key)
    
    def put(self, path: str, value: Any) -> 'xHashMapStrategy':
        """Set a value at path."""
        # Handle simple key setting (non-string or string without dots)
        if not isinstance(path, str) or '.' not in path:
            str_key = str(path)
            if str_key not in self._data:
                update_size_tracker(self._size_tracker, 1)
            self._data[str_key] = value
            record_access(self._access_tracker, 'put_count')
            return self
        
        # Handle path setting
        parts = path.split('.')
        current = self._data
        
        # Navigate to the parent of the target
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        return self
    
    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()
        self._size_tracker['size'] = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        return iter(self._data.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        return iter(self._data.items())
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self._size_tracker['size']
    
    def __getitem__(self, key: Union[str, int]) -> Any:
        """Get item by key or index."""
        return self.get(str(key))
    
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set item by key or index."""
        self.put(str(key), value)
    
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        return self.has(str(key))
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate over values."""
        return self.values()
    
    @classmethod
    def create_from_data(cls, data: Any) -> 'xHashMapStrategy':
        """
        Create a new strategy instance from data.
        
        Args:
            data: The data to create the strategy from
            
        Returns:
            A new strategy instance containing the data
        """
        instance = cls()
        if isinstance(data, dict):
            for key, value in data.items():
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                instance.put(i, value)
        else:
            # For primitive values, store directly
            instance.put('_value', data)
        return instance
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        # Return a copy with all nested XWNode objects converted to native types
        return {k: safe_to_native_conversion(v) for k, v in self._data.items()}
    
    @property
    def value(self) -> Any:
        """Get the value of this node."""
        # If this is a primitive value node (has only _value key), return the value directly
        if len(self._data) == 1 and '_value' in self._data:
            return self._data['_value']
        # Otherwise return the native representation
        return self.to_native()
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self._data) == 0
    
    @property
    def is_list(self) -> bool:
        """This is never a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This is always a dict strategy."""
        return True
    
    @property
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        return False
    
    @property
    def is_object(self) -> bool:
        """Check if this is an object node."""
        return False
    
    @property
    def type(self) -> str:
        """Get the type of this node."""
        return "dict"
    
    @property
    def uri(self) -> Optional[str]:
        """Get the URI of this node."""
        return None
    
    @property
    def reference_type(self) -> Optional[str]:
        """Get the reference type of this node."""
        return None
    
    @property
    def object_type(self) -> Optional[str]:
        """Get the object type of this node."""
        return None
    
    @property
    def mime_type(self) -> Optional[str]:
        """Get the MIME type of this node."""
        return None
    
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Get the metadata of this node."""
        return None
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return create_basic_backend_info(
            'HASH_MAP',
            'Python dict',
            load_factor=len(self._data) / max(8, len(self._data)),
            collision_rate='~5% (Python dict optimized)'
        )
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        base_metrics = create_basic_metrics('HASH_MAP', self._size_tracker['size'])
        access_metrics = get_access_metrics(self._access_tracker)
        base_metrics.update(access_metrics)
        return base_metrics
