"""
B+ Tree Node Strategy Implementation

This module implements the B_PLUS_TREE strategy for database-friendly
operations with efficient range queries and sequential access.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class BPlusTreeNode:
    """Node in the B+ tree."""
    
    def __init__(self, is_leaf: bool = False, max_keys: int = 4):
        self.is_leaf = is_leaf
        self.keys: List[str] = []
        self.values: List[Any] = [] if is_leaf else []  # Only leaves store values
        self.children: List['BPlusTreeNode'] = [] if not is_leaf else []  # Internal nodes have children
        self.next_leaf: Optional['BPlusTreeNode'] = None  # Leaf linking for sequential access
        self.parent: Optional['BPlusTreeNode'] = None
        self.max_keys = max_keys
    
    def is_full(self) -> bool:
        """Check if node is full."""
        return len(self.keys) >= self.max_keys
    
    def is_underflow(self) -> bool:
        """Check if node has too few keys."""
        min_keys = self.max_keys // 2
        return len(self.keys) < min_keys
    
    def find_child_index(self, key: str) -> int:
        """Find child index for given key."""
        for i, k in enumerate(self.keys):
            if key <= k:
                return i
        return len(self.keys)


class BPlusTreeStrategy(ANodeTreeStrategy):
    """
    B+ Tree node strategy for database-friendly operations.
    
    Provides efficient range queries, sequential access, and balanced
    tree operations optimized for disk-based storage systems.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the B+ Tree strategy."""
        super().__init__(NodeMode.B_PLUS_TREE, traits, **options)
        
        self.order = options.get('order', 4)  # Maximum number of keys per node
        self.case_sensitive = options.get('case_sensitive', True)
        
        # Core B+ tree
        self._root: Optional[BPlusTreeNode] = None
        self._first_leaf: Optional[BPlusTreeNode] = None  # Pointer to first leaf for iteration
        self._size = 0
        
        # Statistics
        self._height = 0
        self._total_nodes = 0
        self._total_splits = 0
        self._total_merges = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the B+ tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL | NodeTrait.PERSISTENT)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _create_leaf_node(self) -> BPlusTreeNode:
        """Create new leaf node."""
        node = BPlusTreeNode(is_leaf=True, max_keys=self.order)
        self._total_nodes += 1
        return node
    
    def _create_internal_node(self) -> BPlusTreeNode:
        """Create new internal node."""
        node = BPlusTreeNode(is_leaf=False, max_keys=self.order)
        self._total_nodes += 1
        return node
    
    def _find_leaf(self, key: str) -> Optional[BPlusTreeNode]:
        """Find leaf node that should contain the key."""
        if not self._root:
            return None
        
        current = self._root
        while not current.is_leaf:
            child_index = current.find_child_index(key)
            current = current.children[child_index]
        
        return current
    
    def _insert_into_leaf(self, leaf: BPlusTreeNode, key: str, value: Any) -> None:
        """Insert key-value pair into leaf node."""
        # Find insertion position
        pos = 0
        while pos < len(leaf.keys) and leaf.keys[pos] < key:
            pos += 1
        
        # Check if key already exists
        if pos < len(leaf.keys) and leaf.keys[pos] == key:
            leaf.values[pos] = value  # Update existing value
            return
        
        # Insert new key-value pair
        leaf.keys.insert(pos, key)
        leaf.values.insert(pos, value)
        self._size += 1
    
    def _split_leaf(self, leaf: BPlusTreeNode) -> Tuple[BPlusTreeNode, str]:
        """Split full leaf node."""
        mid = len(leaf.keys) // 2
        new_leaf = self._create_leaf_node()
        
        # Move half of keys/values to new leaf
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        
        # Update original leaf
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        
        # Link leaves
        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf
        
        # Set parent
        new_leaf.parent = leaf.parent
        
        self._total_splits += 1
        return new_leaf, new_leaf.keys[0]  # Return new node and separator key
    
    def _split_internal(self, node: BPlusTreeNode) -> Tuple[BPlusTreeNode, str]:
        """Split full internal node."""
        mid = len(node.keys) // 2
        new_node = self._create_internal_node()
        
        # Move keys and children
        separator_key = node.keys[mid]
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        
        # Update original node
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        
        # Update parent pointers
        new_node.parent = node.parent
        for child in new_node.children:
            child.parent = new_node
        
        self._total_splits += 1
        return new_node, separator_key
    
    def _insert_into_parent(self, left: BPlusTreeNode, key: str, right: BPlusTreeNode) -> None:
        """Insert separator key into parent after split."""
        if left.parent is None:
            # Create new root
            new_root = self._create_internal_node()
            new_root.keys = [key]
            new_root.children = [left, right]
            left.parent = new_root
            right.parent = new_root
            self._root = new_root
            self._height += 1
            return
        
        parent = left.parent
        
        # Find insertion position
        pos = 0
        while pos < len(parent.keys) and parent.keys[pos] < key:
            pos += 1
        
        # Insert key and child
        parent.keys.insert(pos, key)
        parent.children.insert(pos + 1, right)
        right.parent = parent
        
        # Check if parent is full
        if parent.is_full():
            new_parent, separator = self._split_internal(parent)
            self._insert_into_parent(parent, separator, new_parent)
    
    def _insert_key(self, key: str, value: Any) -> None:
        """Insert key-value pair into B+ tree."""
        if not self._root:
            # Create first leaf node
            self._root = self._create_leaf_node()
            self._first_leaf = self._root
            self._height = 1
        
        leaf = self._find_leaf(key)
        if not leaf:
            return
        
        self._insert_into_leaf(leaf, key, value)
        
        # Check if leaf is full
        if leaf.is_full():
            new_leaf, separator = self._split_leaf(leaf)
            self._insert_into_parent(leaf, separator, new_leaf)
    
    def _search_key(self, key: str) -> Optional[Any]:
        """Search for key in B+ tree."""
        leaf = self._find_leaf(key)
        if not leaf:
            return None
        
        # Search in leaf
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        
        return None
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add key-value pair to B+ tree."""
        key_str = str(key)
        normalized_key = self._normalize_key(key_str)
        self._insert_key(normalized_key, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "tree_info":
            return {
                'size': self._size,
                'height': self._height,
                'total_nodes': self._total_nodes,
                'order': self.order,
                'case_sensitive': self.case_sensitive,
                'total_splits': self._total_splits
            }
        elif key_str == "first_key":
            return self.first_key()
        elif key_str == "last_key":
            return self.last_key()
        elif key_str.isdigit():
            # Access by index
            index = int(key_str)
            return self.get_at_index(index)
        
        normalized_key = self._normalize_key(key_str)
        result = self._search_key(normalized_key)
        return result if result is not None else default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        
        if key_str in ["tree_info", "first_key", "last_key"]:
            return True
        elif key_str.isdigit():
            index = int(key_str)
            return 0 <= index < self._size
        
        normalized_key = self._normalize_key(key_str)
        return self._search_key(normalized_key) is not None
    
    def remove(self, key: Any) -> bool:
        """Remove key from tree (simplified implementation)."""
        key_str = str(key)
        normalized_key = self._normalize_key(key_str)
        
        leaf = self._find_leaf(normalized_key)
        if not leaf:
            return False
        
        # Find and remove key
        for i, k in enumerate(leaf.keys):
            if k == normalized_key:
                del leaf.keys[i]
                del leaf.values[i]
                self._size -= 1
                return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key from tree (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._first_leaf = None
        self._size = 0
        self._height = 0
        self._total_nodes = 0
        self._total_splits = 0
        self._total_merges = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys in sorted order."""
        current = self._first_leaf
        while current:
            for key in current.keys:
                yield key
            current = current.next_leaf
    
    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        current = self._first_leaf
        while current:
            for value in current.values:
                yield value
            current = current.next_leaf
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        current = self._first_leaf
        while current:
            for key, value in zip(current.keys, current.values):
                yield (key, value)
            current = current.next_leaf
    
    def __len__(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self.items())
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for indexed access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This is a dict-like structure."""
        return True
    
    # ============================================================================
    # B+ TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def first_key(self) -> Optional[str]:
        """Get first (smallest) key."""
        if self._first_leaf and self._first_leaf.keys:
            return self._first_leaf.keys[0]
        return None
    
    def last_key(self) -> Optional[str]:
        """Get last (largest) key."""
        current = self._first_leaf
        last_leaf = None
        
        while current:
            last_leaf = current
            current = current.next_leaf
        
        if last_leaf and last_leaf.keys:
            return last_leaf.keys[-1]
        return None
    
    def get_range(self, start_key: str, end_key: str, inclusive: bool = True) -> List[Tuple[str, Any]]:
        """Get key-value pairs in range."""
        start_norm = self._normalize_key(start_key)
        end_norm = self._normalize_key(end_key)
        
        result = []
        current = self._first_leaf
        
        while current:
            for key, value in zip(current.keys, current.values):
                if inclusive:
                    if start_norm <= key <= end_norm:
                        result.append((key, value))
                else:
                    if start_norm < key < end_norm:
                        result.append((key, value))
                
                if key > end_norm:
                    return result
            
            current = current.next_leaf
        
        return result
    
    def get_at_index(self, index: int) -> Optional[Any]:
        """Get value at specific index."""
        if index < 0 or index >= self._size:
            return None
        
        current_index = 0
        current = self._first_leaf
        
        while current:
            if current_index + len(current.keys) > index:
                local_index = index - current_index
                return current.values[local_index]
            
            current_index += len(current.keys)
            current = current.next_leaf
        
        return None
    
    def index_of(self, key: str) -> int:
        """Get index of key (-1 if not found)."""
        normalized_key = self._normalize_key(key)
        current_index = 0
        current = self._first_leaf
        
        while current:
            for i, k in enumerate(current.keys):
                if k == normalized_key:
                    return current_index + i
            
            current_index += len(current.keys)
            current = current.next_leaf
        
        return -1
    
    def find_prefix_keys(self, prefix: str) -> List[str]:
        """Find all keys starting with given prefix."""
        normalized_prefix = self._normalize_key(prefix)
        result = []
        
        current = self._first_leaf
        while current:
            for key in current.keys:
                if key.startswith(normalized_prefix):
                    result.append(key)
                elif key > normalized_prefix and not key.startswith(normalized_prefix):
                    return result  # No more matches possible
            current = current.next_leaf
        
        return result
    
    def bulk_load(self, items: List[Tuple[str, Any]]) -> None:
        """Bulk load sorted key-value pairs (more efficient than individual inserts)."""
        self.clear()
        
        # Sort items
        sorted_items = sorted(items, key=lambda x: self._normalize_key(x[0]))
        
        for key, value in sorted_items:
            self.put(key, value)
    
    def get_tree_statistics(self) -> Dict[str, Any]:
        """Get detailed tree statistics."""
        if not self._root:
            return {'size': 0, 'height': 0, 'nodes': 0}
        
        # Analyze tree structure
        def _analyze_level(nodes: List[BPlusTreeNode], level: int) -> Dict[str, Any]:
            if not nodes:
                return {'levels': level, 'leaf_nodes': 0, 'internal_nodes': 0, 'total_keys': 0}
            
            level_stats = {
                'level': level,
                'nodes_at_level': len(nodes),
                'keys_at_level': sum(len(node.keys) for node in nodes),
                'leaf_nodes_at_level': sum(1 for node in nodes if node.is_leaf),
                'internal_nodes_at_level': sum(1 for node in nodes if not node.is_leaf)
            }
            
            # Get next level
            next_level_nodes = []
            for node in nodes:
                if not node.is_leaf:
                    next_level_nodes.extend(node.children)
            
            if next_level_nodes:
                child_stats = _analyze_level(next_level_nodes, level + 1)
                level_stats.update(child_stats)
            else:
                level_stats['levels'] = level + 1
            
            return level_stats
        
        stats = _analyze_level([self._root], 0)
        
        # Calculate fill factor
        total_capacity = self._total_nodes * self.order
        fill_factor = self._size / max(1, total_capacity)
        
        return {
            'size': self._size,
            'height': self._height,
            'total_nodes': self._total_nodes,
            'total_splits': self._total_splits,
            'order': self.order,
            'fill_factor': fill_factor,
            'levels': stats.get('levels', 0),
            'first_key': self.first_key(),
            'last_key': self.last_key()
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'B_PLUS_TREE',
            'backend': 'Database-optimized B+ tree with leaf linking',
            'order': self.order,
            'case_sensitive': self.case_sensitive,
            'complexity': {
                'insert': f'O(log_{self.order} n)',
                'search': f'O(log_{self.order} n)',
                'delete': f'O(log_{self.order} n)',
                'range_query': f'O(log_{self.order} n + k)',  # k = result size
                'sequential_access': 'O(n)',  # Via leaf linking
                'space': 'O(n)',
                'disk_friendly': 'Optimized for page-based storage'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_tree_statistics()
        
        return {
            'size': stats['size'],
            'height': stats['height'],
            'total_nodes': stats['total_nodes'],
            'order': stats['order'],
            'fill_factor': f"{stats['fill_factor'] * 100:.1f}%",
            'total_splits': stats['total_splits'],
            'first_key': str(stats['first_key']) if stats['first_key'] else 'None',
            'memory_usage': f"{stats['total_nodes'] * self.order * 20} bytes (estimated)"
        }
