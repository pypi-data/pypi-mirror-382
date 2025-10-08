"""
#exonware/xwnode/src/exonware/xwnode/strategies/nodes/node_tree_graph_hybrid.py

Tree Graph Hybrid Strategy Implementation

This module provides a unified tree engine strategy that contains all the XWNodeBase functionality
in one file, decoupled from XWNode. This eliminates the dual architecture and provides
a single, clean implementation.
"""

import threading
import copy
from abc import ABC, abstractmethod
from typing import Any, Union, List, Dict, Optional, Iterator, Tuple, Callable
from collections import OrderedDict

from ...types import NodeMode, NodeTrait
from ...abc import iNodeStrategy, NodeTrait
from ...errors import xNodePathError
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

# Import shared utilities
from ..utils import (
    PathParser, TrieNode, UnionFind, MinHeap,
    create_path_parser, create_performance_tracker
)

logger = get_logger('xnode.tree_engine')

# ============================================================================
# TREE GRAPH HYBRID INTERNAL NODE CLASSES
# ============================================================================

class TreeGraphNode(ABC):
    """Abstract base for all internal nodes in the TreeGraphHybrid strategy."""
    __slots__ = ('_parent', '_cached_native', '_hash')
    
    def __init__(self, parent: Optional['TreeGraphNode'] = None):
        self._parent: Optional['TreeGraphNode'] = parent
        self._cached_native: Optional[Any] = None
        self._hash: Optional[int] = None
    
    @property
    def parent(self) -> Optional['TreeGraphNode']:
        """Get the parent node."""
        return self._parent
    
    @parent.setter
    def parent(self, value: Optional['TreeGraphNode']):
        """Set the parent node."""
        self._parent = value
    
    def _get_child(self, key_or_index: Union[str, int]) -> 'TreeGraphNode':
        """Get a child node by key or index."""
        raise TypeError(f"Node type {type(self).__name__} does not support child access.")
    
    @abstractmethod
    def _to_native(self) -> Any:
        """Convert this node and its children to a native Python object."""
        pass
    
    def _invalidate_cache(self):
        """Invalidate cached data when the node changes."""
        self._cached_native = None
        self._hash = None
        # Propagate invalidation up the tree
        if self._parent:
            self._parent._invalidate_cache()
    
    def _get_root(self) -> 'TreeGraphNode':
        """Get the root node of the tree."""
        current = self
        while current._parent is not None:
            current = current._parent
        return current
    
    def _get_key_in_parent(self) -> Optional[Union[str, int]]:
        """Get the key or index of this node in its parent."""
        if self._parent is None:
            return None
        
        if isinstance(self._parent, TreeGraphDictNode):
            for key, child in self._parent._children.items():
                if child is self:
                    return key
        elif isinstance(self._parent, TreeGraphListNode):
            try:
                return self._parent._children.index(self)
            except ValueError:
                pass
        
        return None
    
    def _get_path(self) -> str:
        """Get the path from the root to this node as a dot-separated string."""
        if self._parent is None:
            return ""
        
        parent_path = self._parent._get_path()
        key = self._get_key_in_parent()
        
        if key is None:
            return parent_path
        
        if parent_path:
            return f"{parent_path}.{key}"
        else:
            return str(key)
    
    def cleanup(self) -> None:
        """Clean up the node before returning to pool."""
        self._parent = None
        self._cached_native = None
        self._hash = None
    
    def reset(self, parent: Optional['TreeGraphNode'] = None) -> None:
        """Reset the node to initial state."""
        self._parent = parent
        self._cached_native = None
        self._hash = None


class TreeGraphValueNode(TreeGraphNode):
    """Internal node for a primitive value in TreeGraphHybrid strategy."""
    __slots__ = ('_value',)
    
    def __init__(self, value: Any, parent: Optional['TreeGraphNode'] = None):
        super().__init__(parent)
        self._value = value
    
    @property
    def value(self) -> Any:
        """Get the primitive value stored in this leaf node."""
        return self._value
    
    def _to_native(self) -> Any:
        """Convert this node to a native Python object."""
        return self._value


class TreeGraphListNode(TreeGraphNode):
    """Internal node for a list with lazy-loading in TreeGraphHybrid strategy."""
    __slots__ = ('_children', '_source_data', '_is_lazy')
    
    def __init__(self, source_data: List[Any], is_lazy: bool, parent: Optional['TreeGraphNode'] = None):
        super().__init__(parent)
        self._source_data = source_data
        self._is_lazy = is_lazy
        self._children: List['TreeGraphNode'] = []
        
        # Don't load children here to avoid recursion
        # They will be loaded on-demand in _get_child, _to_native, etc.
    
    def _eager_load(self, data: List[Any]) -> List['TreeGraphNode']:
        """Eagerly load all children."""
        self._children = []
        for item in data:
            if item is None:
                self._children.append(TreeGraphValueNode(None, self))
            elif isinstance(item, (str, int, float, bool)):
                self._children.append(TreeGraphValueNode(item, self))
            elif isinstance(item, list):
                is_lazy = len(item) > 100
                self._children.append(TreeGraphListNode(item, is_lazy, self))
            elif isinstance(item, dict):
                is_lazy = len(item) > 100
                self._children.append(TreeGraphDictNode(item, is_lazy, self))
            else:
                self._children.append(TreeGraphValueNode(item, self))
        
        self._source_data = None  # Clear source data after loading
        return self._children
    
    def _get_child(self, index: Union[str, int]) -> 'TreeGraphNode':
        """Get a child node by index."""
        if isinstance(index, str):
            try:
                index = int(index)
            except ValueError:
                raise TypeError(f"List index must be an integer, got {index}")
        
        if not isinstance(index, int):
            raise TypeError(f"List index must be an integer, got {type(index).__name__}")
        
        if index < 0:
            index = len(self) + index
        
        if index < 0 or index >= len(self):
            raise IndexError(f"List index {index} out of range")
        
        # Lazy load if needed
        if self._source_data is not None:
            self._eager_load(self._source_data)
        
        return self._children[index]
    
    def _to_native(self) -> List[Any]:
        """Convert this node and its children to a native Python object."""
        # Lazy load if needed
        if self._source_data is not None:
            self._eager_load(self._source_data)
        
        return [child._to_native() for child in self._children]
    
    def __iter__(self) -> Iterator['TreeGraphNode']:
        """Iterate over child nodes."""
        if self._source_data is not None:
            self._eager_load(self._source_data)
        return iter(self._children)
    
    def __len__(self) -> int:
        """Get the number of child nodes."""
        if self._source_data is not None:
            return len(self._source_data)
        return len(self._children)


class TreeGraphDictNode(TreeGraphNode):
    """Internal node for a dictionary with lazy-loading in TreeGraphHybrid strategy."""
    __slots__ = ('_children', '_source_data', '_is_lazy', '_keys')
    
    def __init__(self, source_data: Dict[str, Any], is_lazy: bool, parent: Optional['TreeGraphNode'] = None):
        super().__init__(parent)
        self._source_data = source_data
        self._is_lazy = is_lazy
        self._children: Dict[str, 'TreeGraphNode'] = {}
        self._keys = list(source_data.keys())
        
        # Don't load children here to avoid recursion
        # They will be loaded on-demand in _get_child, _to_native, etc.
    
    def _eager_load(self, data: Dict[str, Any]) -> Dict[str, 'TreeGraphNode']:
        """Eagerly load all children."""
        # Don't clear existing children if we're loading from empty data
        if not data:
            self._source_data = None
            return self._children
        
        self._children = {}
        for key, value in data.items():
            if value is None:
                self._children[key] = TreeGraphValueNode(None, self)
            elif isinstance(value, (str, int, float, bool)):
                self._children[key] = TreeGraphValueNode(value, self)
            elif isinstance(value, list):
                is_lazy = len(value) > 100
                self._children[key] = TreeGraphListNode(value, is_lazy, self)
            elif isinstance(value, dict):
                is_lazy = len(value) > 100
                self._children[key] = TreeGraphDictNode(value, is_lazy, self)
            else:
                self._children[key] = TreeGraphValueNode(value, self)
        
        self._source_data = None  # Clear source data after loading
        return self._children
    
    def _get_child(self, key: Union[str, int]) -> 'TreeGraphNode':
        """Get a child node by key."""
        if not isinstance(key, str):
            raise TypeError(f"Dictionary key must be a string, got {type(key).__name__}")
        
        # Lazy load if needed
        if self._source_data is not None:
            self._eager_load(self._source_data)
        
        # Check if key exists in children
        if key not in self._children:
            raise xNodePathError(f"Key '{key}' not found in dictionary")
        
        return self._children[key]
    
    def _to_native(self) -> Dict[str, Any]:
        """Convert this node and its children to a native Python object."""
        # Lazy load if needed
        if self._source_data is not None:
            self._eager_load(self._source_data)
        
        return {key: child._to_native() for key, child in self._children.items()}
    
    def items(self) -> Iterator[Tuple[str, 'TreeGraphNode']]:
        """Iterate over key-value pairs."""
        if self._source_data is not None:
            self._eager_load(self._source_data)
        return self._children.items()
    
    def __iter__(self) -> Iterator['TreeGraphNode']:
        """Iterate over child nodes."""
        if self._source_data is not None:
            self._eager_load(self._source_data)
        return iter(self._children.values())
    
    def __len__(self) -> int:
        """Get the number of child nodes."""
        if self._source_data is not None:
            return len(self._source_data)
        return len(self._children)
    
    def keys(self) -> Iterator[str]:
        """Iterate over keys."""
        if self._source_data is not None:
            return iter(self._source_data.keys())
        return iter(self._children.keys())


class TreeGraphReferenceNode(TreeGraphNode):
    """Internal node for a reference in TreeGraphHybrid strategy."""
    __slots__ = ('_uri', '_reference_type', '_metadata')
    
    def __init__(self, uri: str, reference_type: str, metadata: Dict[str, Any], parent: Optional['TreeGraphNode'] = None):
        super().__init__(parent)
        self._uri = uri
        self._reference_type = reference_type
        self._metadata = metadata or {}
    
    @property
    def uri(self) -> str:
        """Get the URI of the reference."""
        return self._uri
    
    @property
    def reference_type(self) -> str:
        """Get the type of the reference."""
        return self._reference_type
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the metadata of the reference."""
        return self._metadata
    
    def _to_native(self) -> Dict[str, Any]:
        """Convert this node to a native Python object."""
        return {
            'type': 'reference',
            'uri': self._uri,
            'reference_type': self._reference_type,
            'metadata': self._metadata
        }
    
    def cleanup(self) -> None:
        """Clean up the node before returning to pool."""
        super().cleanup()
        self._uri = ""
        self._reference_type = ""
        self._metadata = {}
    
    def reset(self, uri: str, reference_type: str, metadata: Dict[str, Any], parent: Optional['TreeGraphNode'] = None) -> None:
        """Reset the node to initial state."""
        super().reset(parent)
        self._uri = uri
        self._reference_type = reference_type
        self._metadata = metadata or {}


class TreeGraphObjectNode(TreeGraphNode):
    """Internal node for an object reference in TreeGraphHybrid strategy."""
    __slots__ = ('_uri', '_object_type', '_mime_type', '_size', '_metadata')
    
    def __init__(self, uri: str, object_type: str, mime_type: Optional[str], size: Optional[int], metadata: Dict[str, Any], parent: Optional['TreeGraphNode'] = None):
        super().__init__(parent)
        self._uri = uri
        self._object_type = object_type
        self._mime_type = mime_type
        self._size = size
        self._metadata = metadata or {}
    
    @property
    def uri(self) -> str:
        """Get the URI of the object."""
        return self._uri
    
    @property
    def object_type(self) -> str:
        """Get the type of the object."""
        return self._object_type
    
    @property
    def mime_type(self) -> Optional[str]:
        """Get the MIME type of the object."""
        return self._mime_type
    
    @property
    def size(self) -> Optional[int]:
        """Get the size of the object."""
        return self._size
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the metadata of the object."""
        return self._metadata
    
    def _to_native(self) -> Dict[str, Any]:
        """Convert this node to a native Python object."""
        result = {
            'type': 'object',
            'uri': self._uri,
            'object_type': self._object_type,
            'metadata': self._metadata
        }
        if self._mime_type:
            result['mime_type'] = self._mime_type
        if self._size is not None:
            result['size'] = self._size
        return result
    
    def cleanup(self) -> None:
        """Clean up the node before returning to pool."""
        super().cleanup()
        self._uri = ""
        self._object_type = ""
        self._mime_type = None
        self._size = None
        self._metadata = {}
    
    def reset(self, uri: str, object_type: str, mime_type: Optional[str], size: Optional[int], metadata: Dict[str, Any], parent: Optional['TreeGraphNode'] = None) -> None:
        """Reset the node to initial state."""
        super().reset(parent)
        self._uri = uri
        self._object_type = object_type
        self._mime_type = mime_type
        self._size = size
        self._metadata = metadata or {}


# ============================================================================
# TREE GRAPH HYBRID NODE FACTORY
# ============================================================================

class TreeGraphNodeFactory:
    """Factory for creating TreeGraphHybrid internal nodes with performance optimizations."""
    
    @staticmethod
    def from_native(data: Any, parent: Optional[TreeGraphNode] = None, depth: int = 0, visited: Optional[set] = None) -> TreeGraphNode:
        """Create a node from native Python data."""
        # Check depth limit
        if depth > 1000:  # Simple depth limit
            raise ValueError("Maximum depth exceeded")
        
        # Initialize visited set for circular reference detection
        if visited is None:
            visited = set()
        
        # Check for circular references
        if id(data) in visited:
            # Return a placeholder node for circular references
            return TreeGraphValueNode(f"<circular_reference_{id(data)}>", parent)
        
        # Add current object to visited set
        visited.add(id(data))
        
        try:
            if data is None:
                node = TreeGraphValueNode(None, parent)
            elif isinstance(data, (str, int, float, bool)):
                node = TreeGraphValueNode(data, parent)
            elif isinstance(data, list):
                # Determine if lazy loading should be used
                is_lazy = len(data) > 100
                node = TreeGraphListNode(data, is_lazy, parent)
            elif isinstance(data, dict):
                # Determine if lazy loading should be used
                is_lazy = len(data) > 100
                node = TreeGraphDictNode(data, is_lazy, parent)
            else:
                # For other types, create a value node
                node = TreeGraphValueNode(data, parent)
            
            return node
        finally:
            # Remove current object from visited set when done
            visited.discard(id(data))
    
    @staticmethod
    def to_native(node: TreeGraphNode) -> Any:
        """Convert a node to native Python data."""
        return node._to_native()


# ============================================================================
# PATH PARSER (Moved from core.py)
# ============================================================================

class PathParser:
    """Thread-safe path parser with caching."""
    
    def __init__(self, max_cache_size: int = 1024):
        self._cache = OrderedDict()
        self._max_cache_size = max_cache_size
        self._lock = threading.RLock()
    
    def parse(self, path: str) -> List[str]:
        """Parse a path string into parts."""
        with self._lock:
            if path in self._cache:
                return self._cache[path]
            
            parts = self._parse_path(path)
            
            # Cache the result
            if len(self._cache) >= self._max_cache_size:
                self._cache.popitem(last=False)
            self._cache[path] = parts
            
            return parts
    
    def _parse_path(self, path: str) -> List[str]:
        """Internal path parsing logic."""
        if not path:
            return []
        
        # Simple dot-separated path parsing
        return [part for part in path.split('.') if part]


# ============================================================================
# TREE GRAPH HYBRID STRATEGY
# ============================================================================

class TreeGraphHybridStrategy(iNodeStrategy):
    """
    Unified TreeGraphHybrid strategy combining aNode model with advanced data structures.
    
    This strategy provides:
    - Tree-based navigation with graph capabilities
    - Advanced data structures (Trie, Heap, Union-Find, etc.)
    - Performance optimizations and caching
    - Circular reference detection
    - Lazy loading and object pooling
    """
    
    def __init__(self):
        """Initialize the TreeGraphHybrid strategy."""
        self._root: Optional[TreeGraphNode] = None
        self._node_count = 0
        self._edge_count = 0
        self._cache = {}
        self._size = 0
        self._performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'operations': 0
        }
        # Initialize shared utilities
        self._path_parser = create_path_parser()
        self._performance_tracker = create_performance_tracker()
    
    @property
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "tree_graph_hybrid"
    
    @property
    def supported_traits(self) -> List[NodeTrait]:
        """Get supported traits for this strategy."""
        return [
            NodeTrait.LAZY_LOADING,
            NodeTrait.OBJECT_POOLING,
            NodeTrait.CIRCULAR_REF_DETECTION,
            NodeTrait.PERFORMANCE_TRACKING,
            NodeTrait.GRAPH_CAPABILITIES,
            NodeTrait.QUERY_CAPABILITIES,
            NodeTrait.SECURITY_FEATURES
        ]
    
    def create_from_data(self, data: Any) -> 'TreeGraphHybridStrategy':
        """Create the tree from data."""
        self._root = TreeGraphNodeFactory.from_native(data)
        self._size = self._calculate_size(self._root)
        # Force eager loading for immediate access
        if isinstance(self._root, TreeGraphDictNode) and self._root._source_data is not None:
            self._root._eager_load(self._root._source_data)
        elif isinstance(self._root, TreeGraphListNode) and self._root._source_data is not None:
            self._root._eager_load(self._root._source_data)
        return self
    
    def _calculate_size(self, node: TreeGraphNode) -> int:
        """Calculate the size of the tree."""
        if isinstance(node, TreeGraphValueNode):
            return 1
        elif isinstance(node, TreeGraphListNode):
            # For lists, return the number of items
            if node._source_data is not None:
                return len(node._source_data)
            else:
                return len(node._children)
        elif isinstance(node, TreeGraphDictNode):
            # For dictionaries, return the number of key-value pairs
            if node._source_data is not None:
                return len(node._source_data)
            else:
                return len(node._children)
        else:
            return 1
    
    def get_native(self, key: str, default: Any = None) -> Any:
        """Get a native Python value by key."""
        self._performance_tracker.record_access()
        
        try:
            if self._root is None:
                return default
            
            # Handle path navigation
            if '.' in key:
                return self._get_by_path(key, default)
            
            # Handle direct key access
            if isinstance(self._root, TreeGraphDictNode):
                child = self._root._get_child(key)
                return child._to_native()
            elif isinstance(self._root, TreeGraphListNode):
                try:
                    index = int(key)
                    child = self._root._get_child(index)
                    return child._to_native()
                except ValueError:
                    return default
            elif isinstance(self._root, TreeGraphValueNode):
                # If root is a value node, only return it if key is empty or matches
                if key == "" or key == "value":
                    return self._root._to_native()
                return default
            else:
                return default
                
        except (KeyError, IndexError, TypeError):
            return default
    
    def _get_by_path(self, path: str, default: Any = None) -> Any:
        """Get a value by path."""
        if self._root is None:
            return default
        
        try:
            segments = self._path_parser.parse(path)
            current = self._root
            
            for segment in segments:
                if isinstance(current, TreeGraphDictNode):
                    current = current._get_child(segment)
                elif isinstance(current, TreeGraphListNode):
                    try:
                        index = int(segment)
                        current = current._get_child(index)
                    except ValueError:
                        return default
                else:
                    return default
            
            return current._to_native()
            
        except (KeyError, IndexError, TypeError):
            return default
    
    def _get_by_key(self, key: str, default: Any = None) -> Any:
        """Get a value by direct key."""
        if self._root is None:
            return default
        
        try:
            if isinstance(self._root, TreeGraphDictNode):
                child = self._root._get_child(key)
                return child._to_native()
            elif isinstance(self._root, TreeGraphListNode):
                try:
                    index = int(key)
                    child = self._root._get_child(index)
                    return child._to_native()
                except ValueError:
                    return default
            elif isinstance(self._root, TreeGraphValueNode):
                # If root is a value node, only return it if key is empty or matches
                if key == "" or key == "value":
                    return self._root._to_native()
                return default
            else:
                return default
                
        except (KeyError, IndexError, TypeError):
            return default
    
    def put(self, key: str, value: Any) -> None:
        """Set a value by key."""
        self._performance_tracker.record_access()
        
        if self._root is None:
            # Create root if it doesn't exist
            self._root = TreeGraphDictNode({}, False)
        
        # Handle path navigation
        if '.' in key:
            self._put_by_path(key, value)
        else:
            # Handle direct key access
            if isinstance(self._root, TreeGraphDictNode):
                # Create child node directly to avoid recursion
                if value is None:
                    child = TreeGraphValueNode(None, self._root)
                elif isinstance(value, (str, int, float, bool)):
                    child = TreeGraphValueNode(value, self._root)
                elif isinstance(value, list):
                    is_lazy = len(value) > 100
                    child = TreeGraphListNode(value, is_lazy, self._root)
                elif isinstance(value, dict):
                    is_lazy = len(value) > 100
                    child = TreeGraphDictNode(value, is_lazy, self._root)
                else:
                    child = TreeGraphValueNode(value, self._root)
                
                self._root._children[key] = child
                self._root._invalidate_cache()
    
    def _put_by_path(self, path: str, value: Any) -> None:
        """Set a value by path."""
        if self._root is None:
            self._root = TreeGraphDictNode({}, False)
        
        try:
            segments = self._path_parser.parse(path)
            current = self._root
            
            # Navigate to parent of target
            for segment in segments[:-1]:
                if isinstance(current, TreeGraphDictNode):
                    if segment not in current._children:
                        current._children[segment] = TreeGraphDictNode({}, False)
                    current = current._children[segment]
                elif isinstance(current, TreeGraphListNode):
                    try:
                        index = int(segment)
                        while len(current._children) <= index:
                            current._children.append(TreeGraphValueNode(None, current))
                        current = current._children[index]
                    except ValueError:
                        return
                else:
                    return
            
            # Set the final value
            final_segment = segments[-1]
            if isinstance(current, TreeGraphDictNode):
                # Create child node directly to avoid recursion
                if value is None:
                    child = TreeGraphValueNode(None, current)
                elif isinstance(value, (str, int, float, bool)):
                    child = TreeGraphValueNode(value, current)
                elif isinstance(value, list):
                    is_lazy = len(value) > 100
                    child = TreeGraphListNode(value, is_lazy, current)
                elif isinstance(value, dict):
                    is_lazy = len(value) > 100
                    child = TreeGraphDictNode(value, is_lazy, current)
                else:
                    child = TreeGraphValueNode(value, current)
                
                current._children[final_segment] = child
                current._invalidate_cache()
            elif isinstance(current, TreeGraphListNode):
                try:
                    index = int(final_segment)
                    while len(current._children) <= index:
                        current._children.append(TreeGraphValueNode(None, current))
                    
                    # Create child node directly to avoid recursion
                    if value is None:
                        child = TreeGraphValueNode(None, current)
                    elif isinstance(value, (str, int, float, bool)):
                        child = TreeGraphValueNode(value, current)
                    elif isinstance(value, list):
                        is_lazy = len(value) > 100
                        child = TreeGraphListNode(value, is_lazy, current)
                    elif isinstance(value, dict):
                        is_lazy = len(value) > 100
                        child = TreeGraphDictNode(value, is_lazy, current)
                    else:
                        child = TreeGraphValueNode(value, current)
                    
                    current._children[index] = child
                    current._invalidate_cache()
                except ValueError:
                    return
                    
        except (KeyError, IndexError, TypeError):
            pass
    
    def has(self, key: str) -> bool:
        """Check if key exists."""
        return self.get_native(key) is not None
    
    def delete(self, key: str) -> bool:
        """Remove a key-value pair."""
        # Implementation for deletion
        # This would need to handle both direct keys and paths
        return False
    
    def remove(self, key: str) -> bool:
        """Remove a key-value pair (alias for delete)."""
        return self.delete(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        if self._root is None or not isinstance(self._root, TreeGraphDictNode):
            return iter([])
        # Trigger lazy loading if needed
        if self._root._source_data is not None:
            self._root._eager_load(self._root._source_data)
        return self._root.keys()
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        if self._root is None or not isinstance(self._root, TreeGraphDictNode):
            return iter([])
        # Trigger lazy loading if needed
        if self._root._source_data is not None:
            self._root._eager_load(self._root._source_data)
        return (child._to_native() for child in self._root._children.values())
    
    def items(self) -> Iterator[Tuple[str, Any]]:
        """Get all key-value pairs."""
        if self._root is None or not isinstance(self._root, TreeGraphDictNode):
            return iter([])
        # Trigger lazy loading if needed
        if self._root._source_data is not None:
            self._root._eager_load(self._root._source_data)
        return ((key, child._to_native()) for key, child in self._root._children.items())
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self._size
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        if self._root is None:
            return {}
        return self._root._to_native()
    
    def backend_info(self) -> Dict[str, Any]:
        """Get information about the backend implementation."""
        return {
            "strategy": "TREE_GRAPH_HYBRID",
            "backend": "TreeGraphNode tree with lazy loading and advanced data structures",
            "complexity": {
                "get": "O(depth)",
                "put": "O(depth)",
                "has": "O(depth)",
                "delete": "O(depth)",
                "union_find": "O(α(n))",
                "trie": "O(k) where k = word length",
                "heap": "O(log n)"
            },
            "features": [
                "lazy_loading",
                "object_pooling",
                "caching",
                "tree_navigation",
                "path_parsing",
                "union_find",
                "trie_operations",
                "priority_queue",
                "advanced_traits"
            ]
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        metrics = self._performance_tracker.get_metrics()
        metrics.update({
            "size": self._size,
            "has_root": self._root is not None
        })
        return metrics
    
    # ============================================================================
    # ADVANCED DATA STRUCTURE OPERATIONS
    # ============================================================================
    
    def union_find_make_set(self, x: Any) -> None:
        """Create new set with element x in Union-Find structure."""
        uf = self._get_union_find()
        uf.make_set(x)
        self._save_union_find()
    
    def union_find_find(self, x: Any) -> Any:
        """Find root of set containing x in Union-Find structure."""
        uf = self._get_union_find()
        return uf.find(x)
    
    def union_find_union(self, x: Any, y: Any) -> None:
        """Union sets containing x and y in Union-Find structure."""
        uf = self._get_union_find()
        uf.union(x, y)
        self._save_union_find()
    
    def union_find_connected(self, x: Any, y: Any) -> bool:
        """Check if x and y are in same set in Union-Find structure."""
        uf = self._get_union_find()
        return uf.connected(x, y)
    
    def union_find_size(self) -> int:
        """Get number of elements in Union-Find structure."""
        uf = self._get_union_find()
        return uf.size()
    
    def union_find_sets_count(self) -> int:
        """Get number of disjoint sets in Union-Find structure."""
        uf = self._get_union_find()
        return uf.sets_count()
    
    def trie_insert(self, word: str, value: Any = None) -> None:
        """Insert word into Trie structure."""
        if not isinstance(word, str):
            raise ValueError(f"Word must be string, got {type(word)}")
        self._insert_trie_word(word, value)
        self._save_trie()
    
    def trie_contains(self, word: str) -> bool:
        """Check if word exists in Trie structure."""
        if not isinstance(word, str):
            return False
        
        current = self._get_trie()
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        
        return current.is_end_word
    
    def trie_get(self, word: str) -> Any:
        """Get value associated with word in Trie structure."""
        if not isinstance(word, str):
            raise ValueError(f"Word must be string, got {type(word)}")
        
        current = self._get_trie()
        for char in word:
            if char not in current.children:
                raise ValueError(f"Word '{word}' not found in trie")
            current = current.children[char]
        
        return current.value
    
    def trie_starts_with(self, prefix: str) -> List[str]:
        """Find all words starting with prefix in Trie structure."""
        if not isinstance(prefix, str):
            return []
        
        current = self._get_trie()
        for char in prefix:
            if char not in current.children:
                return []
            current = current.children[char]
        
        # Collect all words from this node
        result = {}
        self._collect_trie_words(current, prefix, result)
        return list(result.keys())
    
    def heap_push(self, value: Any, priority: float = 0.0) -> None:
        """Push item with priority into MinHeap."""
        heap = self._get_heap()
        heap.push(value, priority)
        self._save_heap()
    
    def heap_pop_min(self) -> Any:
        """Pop minimum priority item from MinHeap."""
        heap = self._get_heap()
        result = heap.pop_min()
        self._save_heap()
        return result
    
    def heap_peek_min(self) -> Any:
        """Peek at minimum without removing from MinHeap."""
        heap = self._get_heap()
        return heap.peek_min()
    
    def heap_size(self) -> int:
        """Get heap size."""
        heap = self._get_heap()
        return heap.size()
    
    def heap_is_empty(self) -> bool:
        """Check if heap is empty."""
        heap = self._get_heap()
        return heap.is_empty()

    # ============================================================================
    # ADVANCED OPERATIONS HELPER METHODS
    # ============================================================================
    
    def _get_union_find(self) -> UnionFind:
        """Get or create Union-Find structure from node data."""
        if not hasattr(self, '_union_find'):
            self._union_find = UnionFind()
            # Load existing data if available
            data = self.to_native()
            if isinstance(data, dict) and 'union_find' in data:
                uf_data = data['union_find']
                if isinstance(uf_data, dict):
                    for element, parent in uf_data.get('sets', {}).items():
                        self._union_find._parent[element] = parent
                    for element, rank in uf_data.get('ranks', {}).items():
                        self._union_find._rank[element] = rank
                    self._union_find._sets_count = uf_data.get('sets_count', 0)
        return self._union_find
    
    def _save_union_find(self) -> None:
        """Save Union-Find structure to node data."""
        if hasattr(self, '_union_find'):
            uf_data = {
                'sets': dict(self._union_find._parent),
                'ranks': dict(self._union_find._rank),
                'sets_count': self._union_find._sets_count
            }
            # Save to node data
            current_data = self.to_native()
            if not isinstance(current_data, dict):
                current_data = {}
            current_data['union_find'] = uf_data
            # Update the strategy with new data
            self._root = TreeGraphNodeFactory.from_native(current_data, None)
    
    def _get_trie(self) -> TrieNode:
        """Get or create Trie structure from node data."""
        if not hasattr(self, '_trie_root'):
            self._trie_root = TrieNode()
            # Load existing data if available
            data = self.to_native()
            if isinstance(data, dict):
                for word, value in data.items():
                    if isinstance(word, str):
                        self._insert_trie_word(word, value)
        return self._trie_root
    
    def _insert_trie_word(self, word: str, value: Any) -> None:
        """Insert word into trie."""
        current = self._get_trie()
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_word = True
        current.value = value
    
    def _save_trie(self) -> None:
        """Save Trie structure to node data."""
        if hasattr(self, '_trie_root'):
            all_words = {}
            self._collect_trie_words(self._trie_root, "", all_words)
            # Save to node data
            current_data = self.to_native()
            if not isinstance(current_data, dict):
                current_data = {}
            current_data.update(all_words)
            # Update the strategy with new data
            self._root = TreeGraphNodeFactory.from_native(current_data, None)
    
    def _collect_trie_words(self, node: TrieNode, prefix: str, result: Dict[str, Any]) -> None:
        """Recursively collect all words from trie."""
        if node.is_end_word:
            result[prefix] = node.value
        
        for char, child in node.children.items():
            self._collect_trie_words(child, prefix + char, result)
    
    def _get_heap(self) -> MinHeap:
        """Get or create MinHeap structure from node data."""
        if not hasattr(self, '_heap'):
            self._heap = MinHeap()
            # Load existing data if available
            data = self.to_native()
            if isinstance(data, dict) and 'heap' in data:
                heap_data = data['heap']
                if isinstance(heap_data, list):
                    for priority, value in heap_data:
                        self._heap.push(value, priority)
        return self._heap
    
    def _save_heap(self) -> None:
        """Save MinHeap structure to node data."""
        if hasattr(self, '_heap'):
            heap_data = list(self._heap._heap)
            # Save to node data
            current_data = self.to_native()
            if not isinstance(current_data, dict):
                current_data = {}
            current_data['heap'] = heap_data
            # Update the strategy with new data
            self._root = TreeGraphNodeFactory.from_native(current_data, None)

    # ============================================================================
    # REQUIRED INTERFACE METHODS
    # ============================================================================

    def to_native(self) -> Any:
        """Convert to native Python object."""
        if self._root is None:
            return {}
        return self._root._to_native()

    def get(self, path: str, default: Any = None) -> Optional['TreeGraphHybridStrategy']:
        """Get a child node by path."""
        if self._root is None:
            return None
        
        try:
            if '.' in path:
                result = self._get_node_by_path(path)
            else:
                result = self._get_node_by_key(path)
            
            if result is None:
                return None
            
            # Create a new strategy instance with the result
            new_strategy = TreeGraphHybridStrategy()
            new_strategy._root = result
            return new_strategy
        except Exception:
            return None
    
    def _get_node_by_path(self, path: str) -> Optional[TreeGraphNode]:
        """Get a node by path."""
        if self._root is None:
            return None
        
        try:
            segments = self._path_parser.parse(path)
            current = self._root
            
            for segment in segments:
                if isinstance(current, TreeGraphDictNode):
                    current = current._get_child(segment)
                elif isinstance(current, TreeGraphListNode):
                    try:
                        index = int(segment)
                        current = current._get_child(index)
                    except ValueError:
                        return None
                else:
                    return None
            
            return current
            
        except (KeyError, IndexError, TypeError):
            return None
    
    def _get_node_by_key(self, key: str) -> Optional[TreeGraphNode]:
        """Get a node by direct key."""
        if self._root is None:
            return None
        
        try:
            if isinstance(self._root, TreeGraphDictNode):
                return self._root._get_child(key)
            elif isinstance(self._root, TreeGraphListNode):
                try:
                    index = int(key)
                    return self._root._get_child(index)
                except ValueError:
                    return None
            elif isinstance(self._root, TreeGraphValueNode):
                # If root is a value node, only return it if key is empty or matches
                if key == "" or key == "value":
                    return self._root
                return None
            else:
                return None
                
        except (KeyError, IndexError, TypeError):
            return None

    def put(self, path: str, value: Any) -> 'TreeGraphHybridStrategy':
        """Set a value at path."""
        if self._root is None:
            self._root = TreeGraphNodeFactory.from_native({})
        
        # For now, implement a simple put operation
        # This would need to be enhanced for complex path navigation
        if '.' not in path:
            # Simple key assignment
            if isinstance(self._root, TreeGraphDictNode):
                value_node = TreeGraphNodeFactory.from_native(value, self._root)
                self._root._children[path] = value_node
            else:
                # Convert to dict if needed
                current_data = self.to_native()
                if not isinstance(current_data, dict):
                    current_data = {}
                current_data[path] = value
                self._root = TreeGraphNodeFactory.from_native(current_data)
        
        return self

    def delete(self, path: str) -> bool:
        """Delete a node at path."""
        if self._root is None:
            return False
        
        try:
            if '.' not in path:
                if isinstance(self._root, TreeGraphDictNode):
                    if path in self._root._children:
                        del self._root._children[path]
                        return True
            return False
        except Exception:
            return False

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.get(path) is not None

    def keys(self) -> Iterator[str]:
        """Get keys (for dict-like nodes)."""
        if self._root is None:
            return iter([])
        
        if isinstance(self._root, TreeGraphDictNode):
            return iter(self._root._children.keys())
        elif isinstance(self._root, TreeGraphListNode):
            return iter(str(i) for i in range(len(self._root._children)))
        else:
            return iter([])

    def values(self) -> Iterator['TreeGraphHybridStrategy']:
        """Get values (for dict-like nodes)."""
        if self._root is None:
            return iter([])
        
        if isinstance(self._root, TreeGraphDictNode):
            for child in self._root._children.values():
                new_strategy = TreeGraphHybridStrategy()
                new_strategy._root = child
                yield new_strategy
        elif isinstance(self._root, TreeGraphListNode):
            for child in self._root._children:
                new_strategy = TreeGraphHybridStrategy()
                new_strategy._root = child
                yield new_strategy
        else:
            return iter([])

    def items(self) -> Iterator[tuple[str, 'TreeGraphHybridStrategy']]:
        """Get items (for dict-like nodes)."""
        if self._root is None:
            return iter([])
        
        if isinstance(self._root, TreeGraphDictNode):
            for key, child in self._root._children.items():
                new_strategy = TreeGraphHybridStrategy()
                new_strategy._root = child
                yield (key, new_strategy)
        elif isinstance(self._root, TreeGraphListNode):
            for i, child in enumerate(self._root._children):
                new_strategy = TreeGraphHybridStrategy()
                new_strategy._root = child
                yield (str(i), new_strategy)
        else:
            return iter([])

    def __len__(self) -> int:
        """Get length."""
        if self._root is None:
            return 0
        
        if isinstance(self._root, TreeGraphDictNode):
            return len(self._root._children)
        elif isinstance(self._root, TreeGraphListNode):
            return len(self._root._children)
        else:
            return 1

    def __iter__(self) -> Iterator['TreeGraphHybridStrategy']:
        """Iterate over children."""
        return self.values()

    def __getitem__(self, key: Union[str, int]) -> 'TreeGraphHybridStrategy':
        """Get child by key or index."""
        if self._root is None:
            raise KeyError(f"Key '{key}' not found")
        
        if isinstance(self._root, TreeGraphDictNode):
            if key not in self._root._children:
                raise KeyError(f"Key '{key}' not found")
            child = self._root._children[key]
        elif isinstance(self._root, TreeGraphListNode):
            if not isinstance(key, int):
                raise TypeError("List indices must be integers")
            if key < 0 or key >= len(self._root._children):
                raise IndexError("List index out of range")
            child = self._root._children[key]
        else:
            raise TypeError(f"Cannot access key '{key}' on node of type {type(self._root)}")
        
        new_strategy = TreeGraphHybridStrategy()
        new_strategy._root = child
        return new_strategy

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        if self._root is None:
            self._root = TreeGraphNodeFactory.from_native({})
        
        if isinstance(self._root, TreeGraphDictNode):
            value_node = TreeGraphNodeFactory.from_native(value, self._root)
            self._root._children[key] = value_node
        elif isinstance(self._root, TreeGraphListNode):
            if not isinstance(key, int):
                raise TypeError("List indices must be integers")
            value_node = TreeGraphNodeFactory.from_native(value, self._root)
            if key >= len(self._root._children):
                # Extend list if needed
                while len(self._root._children) <= key:
                    self._root._children.append(TreeGraphNodeFactory.from_native(None, self._root))
            self._root._children[key] = value_node
        else:
            raise TypeError(f"Cannot set key '{key}' on node of type {type(self._root)}")

    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        if self._root is None:
            return False
        
        if isinstance(self._root, TreeGraphDictNode):
            return key in self._root._children
        elif isinstance(self._root, TreeGraphListNode):
            if not isinstance(key, int):
                return False
            return 0 <= key < len(self._root._children)
        else:
            return False

    # Type checking properties
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        if self._root is None:
            return True
        return isinstance(self._root, TreeGraphValueNode)

    @property
    def is_list(self) -> bool:
        """Check if this is a list node."""
        if self._root is None:
            return False
        return isinstance(self._root, TreeGraphListNode)

    @property
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        if self._root is None:
            return False
        return isinstance(self._root, TreeGraphDictNode)

    @property
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        if self._root is None:
            return False
        return isinstance(self._root, TreeGraphReferenceNode)

    @property
    def is_object(self) -> bool:
        """Check if this is an object node."""
        if self._root is None:
            return False
        return isinstance(self._root, TreeGraphObjectNode)

    @property
    def type(self) -> str:
        """Get the type of this node."""
        if self._root is None:
            return 'empty'
        elif isinstance(self._root, TreeGraphValueNode):
            return 'value'
        elif isinstance(self._root, TreeGraphListNode):
            return 'list'
        elif isinstance(self._root, TreeGraphDictNode):
            return 'dict'
        elif isinstance(self._root, TreeGraphReferenceNode):
            return 'reference'
        elif isinstance(self._root, TreeGraphObjectNode):
            return 'object'
        else:
            return 'unknown'

    @property
    def value(self) -> Any:
        """Get the value of this node."""
        if self._root is None:
            return None
        return self._root._to_native()

    # Optional properties with default implementations
    @property
    def uri(self) -> Optional[str]:
        """Get URI (for reference/object nodes)."""
        if self._root is None:
            return None
        return getattr(self._root, 'uri', None)

    @property
    def reference_type(self) -> Optional[str]:
        """Get reference type (for reference nodes)."""
        if self._root is None:
            return None
        return getattr(self._root, 'reference_type', None)

    @property
    def object_type(self) -> Optional[str]:
        """Get object type (for object nodes)."""
        if self._root is None:
            return None
        return getattr(self._root, 'object_type', None)

    @property
    def mime_type(self) -> Optional[str]:
        """Get MIME type (for object nodes)."""
        if self._root is None:
            return None
        return getattr(self._root, 'mime_type', None)

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata (for reference/object nodes)."""
        if self._root is None:
            return None
        return getattr(self._root, 'metadata', None)
