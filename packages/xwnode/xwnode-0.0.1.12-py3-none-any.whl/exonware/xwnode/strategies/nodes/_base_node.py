"""
Abstract Node Strategy Interface

This module defines the abstract base class that all node strategies must implement
in the strategy system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Iterator, Union
from ...types import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class aNodeStrategy(ABC):
    """
    Abstract base class for all node strategies.
    
    This abstract base class defines the contract that all node strategy
    implementations must follow, ensuring consistency and interoperability.
    """
    
    def __init__(self, mode: NodeMode, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the abstract node strategy."""
        self.mode = mode
        self.traits = traits
        self.options = options
        self._data: Dict[str, Any] = {}
        self._size = 0
        
        # Validate traits compatibility with mode
        self._validate_traits()
    
    def _validate_traits(self) -> None:
        """Validate that the requested traits are compatible with this strategy."""
        supported_traits = self.get_supported_traits()
        unsupported = self.traits & ~supported_traits
        if unsupported != NodeTrait.NONE:
            unsupported_names = [trait.name for trait in NodeTrait if trait in unsupported]
            raise ValueError(f"Strategy {self.mode.name} does not support traits: {unsupported_names}")
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by this strategy implementation."""
        # Default implementation - subclasses should override
        return NodeTrait.NONE
    
    def has_trait(self, trait: NodeTrait) -> bool:
        """Check if this strategy has a specific trait."""
        return bool(self.traits & trait)
    
    def require_trait(self, trait: NodeTrait, operation: str = "operation") -> None:
        """Require a specific trait for an operation."""
        if not self.has_trait(trait):
            from ...errors import UnsupportedCapabilityError
            raise UnsupportedCapabilityError(f"{operation} requires {trait.name} capability")
    
    # ============================================================================
    # CORE OPERATIONS (Required)
    # ============================================================================
    
    @abstractmethod
    def put(self, key: Any, value: Any = None) -> None:
        """
        Store a key-value pair.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        pass
    
    @abstractmethod
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve a value by key.
        
        Args:
            key: The key to look up
            default: Default value if key not found
            
        Returns:
            The value associated with the key, or default if not found
        """
        pass
    
    @abstractmethod
    def delete(self, key: Any) -> bool:
        """
        Remove a key-value pair.
        
        Args:
            key: The key to remove
            
        Returns:
            True if key was found and removed, False otherwise
        """
        pass
    
    @abstractmethod
    def has(self, key: Any) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists, False otherwise
        """
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get the number of key-value pairs."""
        pass
    
    @abstractmethod
    def keys(self) -> Iterator[Any]:
        """Get an iterator over all keys."""
        pass
    
    @abstractmethod
    def values(self) -> Iterator[Any]:
        """Get an iterator over all values."""
        pass
    
    @abstractmethod
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get an iterator over all key-value pairs."""
        pass
    
    # ============================================================================
    # CAPABILITY-BASED OPERATIONS (Optional)
    # ============================================================================
    
    def get_ordered(self, start: Any = None, end: Any = None) -> List[tuple[Any, Any]]:
        """
        Get items in order (requires ORDERED trait).
        
        Args:
            start: Start key (inclusive)
            end: End key (exclusive)
            
        Returns:
            List of (key, value) pairs in order
            
        Raises:
            UnsupportedCapabilityError: If ORDERED trait not supported
        """
        if NodeTrait.ORDERED not in self.traits:
            raise XWNodeUnsupportedCapabilityError("ORDERED", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for ordered strategies
        items = list(self.items())
        if start is not None:
            items = [(k, v) for k, v in items if k >= start]
        if end is not None:
            items = [(k, v) for k, v in items if k < end]
        return items
    
    def get_with_prefix(self, prefix: str) -> List[tuple[Any, Any]]:
        """
        Get items with given prefix (requires HIERARCHICAL trait).
        
        Args:
            prefix: The prefix to match
            
        Returns:
            List of (key, value) pairs with matching prefix
            
        Raises:
            UnsupportedCapabilityError: If HIERARCHICAL trait not supported
        """
        if NodeTrait.HIERARCHICAL not in self.traits:
            raise XWNodeUnsupportedCapabilityError("HIERARCHICAL", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for hierarchical strategies
        return [(k, v) for k, v in self.items() if str(k).startswith(prefix)]
    
    def get_priority(self) -> Optional[tuple[Any, Any]]:
        """
        Get highest priority item (requires PRIORITY trait).
        
        Returns:
            (key, value) pair with highest priority, or None if empty
            
        Raises:
            UnsupportedCapabilityError: If PRIORITY trait not supported
        """
        if NodeTrait.PRIORITY not in self.traits:
            raise XWNodeUnsupportedCapabilityError("PRIORITY", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for priority strategies
        if not self._data:
            return None
        return min(self.items(), key=lambda x: x[0])
    
    def get_weighted(self, key: Any) -> float:
        """
        Get weight for a key (requires WEIGHTED trait).
        
        Args:
            key: The key to get weight for
            
        Returns:
            Weight value for the key
            
        Raises:
            UnsupportedCapabilityError: If WEIGHTED trait not supported
        """
        if NodeTrait.WEIGHTED not in self.traits:
            raise XWNodeUnsupportedCapabilityError("WEIGHTED", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for weighted strategies
        return self._data.get(key, {}).get('weight', 1.0)
    
    # ============================================================================
    # STRATEGY METADATA
    # ============================================================================
    
    def capabilities(self) -> NodeTrait:
        """Get the capabilities supported by this strategy."""
        return self.traits
    
    def backend_info(self) -> Dict[str, Any]:
        """Get information about the backend implementation."""
        return {
            "mode": self.mode.name,
            "traits": str(self.traits),
            "size": len(self),
            "options": self.options.copy()
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this strategy."""
        return {
            "size": len(self),
            "mode": self.mode.name,
            "traits": str(self.traits)
        }
    
    # ============================================================================
    # FACTORY METHODS
    # ============================================================================
    
    @classmethod
    def create_from_data(cls, data: Any) -> 'aNodeStrategy':
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
            # For primitive values, store as root value
            instance.put('_value', data)
        return instance
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all data."""
        self._data.clear()
        self._size = 0
    
    def __contains__(self, key: Any) -> bool:
        """Check if key exists."""
        return self.has(key)
    
    def __getitem__(self, key: Any) -> Any:
        """Get value by key."""
        return self.get(key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """Set value by key."""
        self.put(key, value)
    
    def __delitem__(self, key: Any) -> None:
        """Delete key."""
        if not self.delete(key):
            raise KeyError(key)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate over keys."""
        return self.keys()
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(mode={self.mode.name}, size={len(self)})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(mode={self.mode.name}, traits={self.traits}, size={len(self)})"



