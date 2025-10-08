#!/usr/bin/env python3
"""
XWNode Facade - Main Public API

This module provides the main public API for the xwnode library,
implementing the facade pattern to hide complexity and provide
a clean, intuitive interface.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

import logging
from typing import Any, Dict, List, Optional, Union, Iterator

from .base import XWNodeBase
from .config import get_config, set_config
from .errors import XWNodeError, XWNodeTypeError, XWNodeValueError
from .strategies import StrategyManager, get_registry

logger = logging.getLogger(__name__)


class XWNode(XWNodeBase):
    """
    Main XWNode class providing a unified interface for all node operations.
    
    This class implements the facade pattern, hiding the complexity of the
    underlying strategy system while providing a clean, intuitive API.
    """
    
    def __init__(self, data: Any = None, mode: str = 'AUTO', **options):
        """
        Initialize XWNode with data and configuration.
        
        Args:
            data: Initial data to store in the node
            mode: Strategy mode ('AUTO', 'HASH_MAP', 'ARRAY_LIST', etc.)
            **options: Additional configuration options
        """
        self._data = data
        self._mode = mode
        self._options = options
        self._strategy_manager = StrategyManager()
        self._setup_strategy()
        # Initialize base class with the created strategy
        super().__init__(self._strategy)
    
    def _setup_strategy(self):
        """Setup the appropriate strategy based on mode and data."""
        try:
            # For now, use the create_node_strategy method which handles data properly
            self._strategy = self._strategy_manager.create_node_strategy(self._data or {})
        except Exception as e:
            logger.warning(f"Failed to setup strategy: {e}, using default")
            # Create a simple strategy as fallback
            from .strategies.simple import SimpleNodeStrategy
            self._strategy = SimpleNodeStrategy.create_from_data(self._data or {})
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a value with the given key."""
        try:
            self._strategy.insert(key, value)
        except Exception as e:
            raise XWNodeError(f"Failed to put key '{key}': {e}")
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        try:
            result = self._strategy.find(key)
            return result if result is not None else default
        except Exception as e:
            raise XWNodeError(f"Failed to get key '{key}': {e}")
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        try:
            return self._strategy.find(key) is not None
        except Exception as e:
            raise XWNodeError(f"Failed to check key '{key}': {e}")
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair."""
        try:
            return self._strategy.delete(key)
        except Exception as e:
            raise XWNodeError(f"Failed to remove key '{key}': {e}")
    
    def clear(self) -> None:
        """Clear all data."""
        try:
            # Create new strategy instance
            self._setup_strategy()
        except Exception as e:
            raise XWNodeError(f"Failed to clear: {e}")
    
    def size(self) -> int:
        """Get the number of items."""
        try:
            return self._strategy.size()
        except Exception as e:
            raise XWNodeError(f"Failed to get size: {e}")
    
    def is_empty(self) -> bool:
        """Check if the node is empty."""
        try:
            return self._strategy.is_empty()
        except Exception as e:
            raise XWNodeError(f"Failed to check if empty: {e}")
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        try:
            # Convert to string keys for consistency
            return (str(key) for key in self._strategy.keys())
        except Exception as e:
            raise XWNodeError(f"Failed to get keys: {e}")
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        try:
            return self._strategy.values()
        except Exception as e:
            raise XWNodeError(f"Failed to get values: {e}")
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        try:
            return ((str(key), value) for key, value in self._strategy.items())
        except Exception as e:
            raise XWNodeError(f"Failed to get items: {e}")
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return self.keys()
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self.size()
    
    # ============================================================================
    # CONVERSION
    # ============================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        try:
            return dict(self.items())
        except Exception as e:
            raise XWNodeError(f"Failed to convert to dict: {e}")
    
    def to_list(self) -> List[Any]:
        """Convert to list."""
        try:
            return list(self.values())
        except Exception as e:
            raise XWNodeError(f"Failed to convert to list: {e}")
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        try:
            return self._strategy.to_native()
        except Exception as e:
            raise XWNodeError(f"Failed to convert to native: {e}")
    
    # ============================================================================
    # STRATEGY INFORMATION
    # ============================================================================
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about the current strategy."""
        try:
            return {
                'mode': self._strategy.get_mode(),
                'traits': str(self._strategy.get_traits()) if self._strategy.get_traits() else None,
                'backend_info': getattr(self._strategy, 'backend_info', {}),
                'metrics': getattr(self._strategy, 'metrics', {})
            }
        except Exception as e:
            raise XWNodeError(f"Failed to get strategy info: {e}")
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations."""
        try:
            # Get operations based on strategy type
            operations = ['put', 'get', 'has', 'remove', 'clear', 'size', 'is_empty']
            
            # Add strategy-specific operations
            if hasattr(self._strategy, 'push_front'):
                operations.extend(['push_front', 'push_back', 'pop_front', 'pop_back'])
            
            if hasattr(self._strategy, 'get_parent'):
                operations.extend(['get_parent', 'get_children', 'traverse'])
            
            if hasattr(self._strategy, 'add_edge'):
                operations.extend(['add_edge', 'remove_edge', 'has_edge', 'get_neighbors'])
            
            return operations
        except Exception as e:
            raise XWNodeError(f"Failed to get supported operations: {e}")
    
    # ============================================================================
    # STRATEGY MIGRATION
    # ============================================================================
    
    def migrate_to(self, new_mode: str, **options) -> None:
        """Migrate to a different strategy mode."""
        try:
            # Get current data
            current_data = self.to_native()
            
            # Create new strategy
            new_strategy = self._strategy_manager.get_strategy(new_mode, **options)
            
            # Migrate data
            if hasattr(new_strategy, 'migrate_from'):
                new_strategy.migrate_from(self._strategy)
            else:
                # Fallback: recreate from data
                for key, value in self.items():
                    new_strategy.insert(key, value)
            
            # Update strategy
            self._strategy = new_strategy
            self._mode = new_mode
            
        except Exception as e:
            raise XWNodeError(f"Failed to migrate to '{new_mode}': {e}")
    
    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================
    
    def __getitem__(self, key: Any) -> Any:
        """Get item using bracket notation."""
        return self.get(key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """Set item using bracket notation."""
        self.put(key, value)
    
    def __delitem__(self, key: Any) -> None:
        """Delete item using bracket notation."""
        if not self.remove(key):
            raise KeyError(key)
    
    def __contains__(self, key: Any) -> bool:
        """Check if key exists using 'in' operator."""
        return self.has(key)
    
    def __str__(self) -> str:
        """String representation."""
        try:
            return f"XWNode({self.to_dict()})"
        except:
            return f"XWNode(mode={self._mode}, size={self.size()})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        try:
            return f"XWNode({self.to_dict()}, mode='{self._mode}')"
        except:
            return f"XWNode(mode='{self._mode}', size={self.size()})"


class XWQuery:
    """Query interface for XWNode."""
    
    def __init__(self, node: XWNode):
        """Initialize query interface."""
        self._node = node
    
    def find(self, pattern: str) -> List[Any]:
        """Find items matching pattern."""
        # TODO: Implement pattern matching
        return []
    
    def filter(self, predicate) -> List[Any]:
        """Filter items by predicate."""
        # TODO: Implement filtering
        return []


class XWFactory:
    """Factory for creating XWNode instances."""
    
    @staticmethod
    def create(mode: str = 'AUTO', **options) -> XWNode:
        """Create XWNode with specified mode."""
        return XWNode(mode=mode, **options)
    
    @staticmethod
    def from_dict(data: Dict[str, Any], mode: str = 'AUTO') -> XWNode:
        """Create XWNode from dictionary."""
        node = XWNode(mode=mode)
        for key, value in data.items():
            node.put(key, value)
        return node
    
    @staticmethod
    def from_list(data: List[Any], mode: str = 'ARRAY_LIST') -> XWNode:
        """Create XWNode from list."""
        node = XWNode(mode=mode)
        for i, value in enumerate(data):
            node.put(i, value)
        return node


# A+ Usability Presets
def create_with_preset(data: Any = None, preset: str = 'DEFAULT') -> XWNode:
    """Create XWNode with A+ usability preset."""
    from .types import get_preset
    
    try:
        preset_config = get_preset(preset)
        # For now, create with basic configuration
        # TODO: Integrate with StrategyManager for full preset support
        return XWNode(data)
    except ValueError as e:
        logger.warning(f"Unknown preset '{preset}', using DEFAULT: {e}")
        return XWNode(data)

def list_available_presets() -> List[str]:
    """List all available A+ usability presets."""
    from .types import list_presets
    return list_presets()

# Performance Mode Factory Methods
def fast(data: Any = None) -> XWNode:
    """Create XWNode optimized for speed."""
    return XWNode(data, mode='HASH_MAP')

def optimized(data: Any = None) -> XWNode:
    """Create XWNode optimized for memory."""
    return XWNode(data, mode='ARRAY_LIST')

def adaptive(data: Any = None) -> XWNode:
    """Create XWNode with adaptive strategy selection."""
    return XWNode(data, mode='AUTO')

def dual_adaptive(data: Any = None) -> XWNode:
    """Create XWNode with dual adaptive strategy."""
    return XWNode(data, mode='AUTO', adaptive=True)


class XWEdge:
    """
    XWEdge class for managing edges between nodes.
    
    This class provides a simple interface for creating and managing
    edges between XWNode instances with support for different edge types.
    """
    
    def __init__(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None):
        """
        Initialize an edge between source and target nodes.
        
        Args:
            source: Source node identifier
            target: Target node identifier
            edge_type: Type of edge (default, directed, weighted, etc.)
            weight: Edge weight (default: 1.0)
            properties: Additional edge properties
            is_bidirectional: Whether the edge is bidirectional
            edge_id: Optional unique edge identifier
        """
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.weight = weight
        self.properties = properties or {}
        self.is_bidirectional = is_bidirectional
        self.edge_id = edge_id or f"{source}->{target}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation."""
        return {
            'source': self.source,
            'target': self.target,
            'edge_type': self.edge_type,
            'weight': self.weight,
            'properties': self.properties,
            'is_bidirectional': self.is_bidirectional,
            'edge_id': self.edge_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'XWEdge':
        """Create edge from dictionary representation."""
        return cls(
            source=data['source'],
            target=data['target'],
            edge_type=data.get('edge_type', 'default'),
            weight=data.get('weight', 1.0),
            properties=data.get('properties', {}),
            is_bidirectional=data.get('is_bidirectional', False),
            edge_id=data.get('edge_id')
        )
    
    def __repr__(self) -> str:
        direction = "<->" if self.is_bidirectional else "->"
        return f"XWEdge({self.source}{direction}{self.target}, type={self.edge_type}, weight={self.weight})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, XWEdge):
            return False
        return (self.source == other.source and 
                self.target == other.target and 
                self.edge_type == other.edge_type)


# Convenience functions
def create_node(data: Any = None) -> XWNode:
    """Create a new XWNode instance."""
    return XWNode(data)

def from_dict(data: Dict[str, Any]) -> XWNode:
    """Create XWNode from dictionary."""
    return XWFactory.from_dict(data)

def from_list(data: List[Any]) -> XWNode:
    """Create XWNode from list."""
    return XWFactory.from_list(data)

def empty_node() -> XWNode:
    """Create an empty XWNode."""
    return XWNode()

# Export main classes
__all__ = [
    'XWNode',
    'XWEdge',
    'XWQuery', 
    'XWFactory',
    'create_node',
    'from_dict',
    'from_list',
    'empty_node',
    # A+ Usability Presets
    'create_with_preset',
    'list_available_presets',
    # Performance Modes
    'fast',
    'optimized', 
    'adaptive',
    'dual_adaptive'
]