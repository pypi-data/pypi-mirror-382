"""
Hash Set Node Strategy Implementation

This module implements the SET_HASH strategy for efficient set operations
with O(1) average-case membership testing and insertion.
"""

from typing import Any, Iterator, Set, Dict, Union, List
import hashlib
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class xSetHashStrategy(aNodeStrategy):
    """
    Hash Set node strategy for efficient set operations.
    
    Provides O(1) average-case membership testing, insertion, and deletion
    with automatic handling of duplicates and fast set operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Hash Set strategy."""
        super().__init__(NodeMode.SET_HASH, traits, **options)
        
        self.load_factor = options.get('load_factor', 0.75)
        self.initial_capacity = options.get('initial_capacity', 16)
        
        # Core storage: hash set for uniqueness
        self._set: Set[str] = set()
        self._values: Dict[str, Any] = {}  # Value storage for compatibility
        self._size = 0
        
        # Set-specific options
        self.case_sensitive = options.get('case_sensitive', True)
        self.allow_none = options.get('allow_none', True)
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the hash set strategy."""
        return (NodeTrait.INDEXED | NodeTrait.STREAMING)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add a value to the set (key becomes the set element)."""
        if value is None and not self.allow_none:
            return
        
        # Use key as the set element
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        
        # Add to set (automatic deduplication)
        was_new = element not in self._set
        self._set.add(element)
        self._values[element] = value if value is not None else key
        
        if was_new:
            self._size += 1
        
        # Keep size in sync
        self._size = len(self._set)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key (check if element exists in set)."""
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        
        return self._values.get(element, default)
    
    def has(self, key: Any) -> bool:
        """Check if key exists in set (O(1) membership test)."""
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        
        return element in self._set
    
    def remove(self, key: Any) -> bool:
        """Remove element from set."""
        element = str(key) if not self.case_sensitive else str(key)
        if not self.case_sensitive:
            element = element.lower()
        
        if element in self._set:
            self._set.remove(element)
            if element in self._values:
                del self._values[element]
            self._size -= 1
            return True
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove element from set (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all elements from the set."""
        self._set.clear()
        self._values.clear()
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all elements in the set."""
        return iter(self._set)
    
    def values(self) -> Iterator[Any]:
        """Get all values (for compatibility)."""
        return iter(self._values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all element-value pairs."""
        return iter(self._values.items())
    
    def __len__(self) -> int:
        """Get the number of elements in the set."""
        return self._size
    
    def to_native(self) -> Set[Any]:
        """Convert to native Python set."""
        return set(self._set)
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict but represents a set."""
        return True
    
    # ============================================================================
    # SET-SPECIFIC OPERATIONS
    # ============================================================================
    
    def add(self, element: Any) -> bool:
        """Add an element to the set. Returns True if element was new."""
        element_str = str(element) if not self.case_sensitive else str(element)
        if not self.case_sensitive:
            element_str = element_str.lower()
        
        was_new = element_str not in self._set
        self._set.add(element_str)
        self._values[element_str] = element
        
        if was_new:
            self._size += 1
        
        return was_new
    
    def discard(self, element: Any) -> None:
        """Remove element if present (no error if not found)."""
        self.remove(element)
    
    def pop(self) -> Any:
        """Remove and return an arbitrary element."""
        if not self._set:
            raise KeyError("pop from empty set")
        
        element = self._set.pop()
        value = self._values.pop(element, element)
        self._size -= 1
        return value
    
    def union(self, other: Union['xSetHashStrategy', Set, List]) -> 'xSetHashStrategy':
        """Return union of this set with another."""
        result = xSetHashStrategy(
            traits=self._traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        
        # Add all elements from this set
        for element in self._set:
            result.add(self._values[element])
        
        # Add elements from other
        if isinstance(other, xSetHashStrategy):
            for element in other._set:
                result.add(other._values[element])
        elif isinstance(other, (set, list)):
            for element in other:
                result.add(element)
        
        return result
    
    def intersection(self, other: Union['xSetHashStrategy', Set, List]) -> 'xSetHashStrategy':
        """Return intersection of this set with another."""
        result = xSetHashStrategy(
            traits=self._traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        
        if isinstance(other, xSetHashStrategy):
            common = self._set.intersection(other._set)
            for element in common:
                result.add(self._values[element])
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            common = self._set.intersection(other_set)
            for element in common:
                result.add(self._values[element])
        
        return result
    
    def difference(self, other: Union['xSetHashStrategy', Set, List]) -> 'xSetHashStrategy':
        """Return difference of this set with another."""
        result = xSetHashStrategy(
            traits=self._traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        
        if isinstance(other, xSetHashStrategy):
            diff = self._set.difference(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            diff = self._set.difference(other_set)
        else:
            diff = self._set.copy()
        
        for element in diff:
            result.add(self._values[element])
        
        return result
    
    def symmetric_difference(self, other: Union['xSetHashStrategy', Set, List]) -> 'xSetHashStrategy':
        """Return symmetric difference of this set with another."""
        result = xSetHashStrategy(
            traits=self._traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        
        if isinstance(other, xSetHashStrategy):
            sym_diff = self._set.symmetric_difference(other._set)
            for element in sym_diff:
                if element in self._values:
                    result.add(self._values[element])
                elif element in other._values:
                    result.add(other._values[element])
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            sym_diff = self._set.symmetric_difference(other_set)
            for element in sym_diff:
                if element in self._values:
                    result.add(self._values[element])
                else:
                    # Find original element in other
                    for orig in other:
                        if (str(orig).lower() if not self.case_sensitive else str(orig)) == element:
                            result.add(orig)
                            break
        
        return result
    
    def is_subset(self, other: Union['xSetHashStrategy', Set, List]) -> bool:
        """Check if this set is a subset of another."""
        if isinstance(other, xSetHashStrategy):
            return self._set.issubset(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            return self._set.issubset(other_set)
        return False
    
    def is_superset(self, other: Union['xSetHashStrategy', Set, List]) -> bool:
        """Check if this set is a superset of another."""
        if isinstance(other, xSetHashStrategy):
            return self._set.issuperset(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            return self._set.issuperset(other_set)
        return False
    
    def is_disjoint(self, other: Union['xSetHashStrategy', Set, List]) -> bool:
        """Check if this set has no elements in common with another."""
        if isinstance(other, xSetHashStrategy):
            return self._set.isdisjoint(other._set)
        elif isinstance(other, (set, list)):
            other_set = {str(x).lower() if not self.case_sensitive else str(x) for x in other}
            return self._set.isdisjoint(other_set)
        return True
    
    def copy(self) -> 'xSetHashStrategy':
        """Create a shallow copy of the set."""
        result = xSetHashStrategy(
            traits=self._traits,
            case_sensitive=self.case_sensitive,
            allow_none=self.allow_none
        )
        
        for element in self._set:
            result.add(self._values[element])
        
        return result
    
    def update(self, *others) -> None:
        """Update the set with elements from other iterables."""
        for other in others:
            if isinstance(other, xSetHashStrategy):
                for element in other._set:
                    self.add(other._values[element])
            elif isinstance(other, (set, list, tuple)):
                for element in other:
                    self.add(element)
    
    def get_hash(self) -> str:
        """Get a hash representation of the set."""
        # Sort elements for consistent hashing
        sorted_elements = sorted(self._set)
        content = ''.join(sorted_elements)
        return hashlib.md5(content.encode()).hexdigest()
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'SET_HASH',
            'backend': 'Python set + dict',
            'case_sensitive': self.case_sensitive,
            'allow_none': self.allow_none,
            'complexity': {
                'add': 'O(1) average',
                'remove': 'O(1) average',
                'contains': 'O(1) average',
                'union': 'O(n + m)',
                'intersection': 'O(min(n, m))',
                'space': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        collision_estimate = max(0, len(self._values) - len(self._set))
        
        return {
            'size': self._size,
            'unique_elements': len(self._set),
            'collisions_estimate': collision_estimate,
            'load_factor': self.load_factor,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'hash': self.get_hash()[:8] + "..."
        }
