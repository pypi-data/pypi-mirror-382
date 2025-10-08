#exonware\xnode\strategies\impls\node_persistent_tree.py
"""
Persistent Tree Node Strategy Implementation

This module implements the PERSISTENT_TREE strategy for immutable functional
trees with structural sharing and lock-free concurrency.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class PersistentTreeNode:
    """Immutable node in the persistent tree."""
    
    def __init__(self, key: str, value: Any = None, left: Optional['PersistentTreeNode'] = None, 
                 right: Optional['PersistentTreeNode'] = None, height: int = 1):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.height = height
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value, id(self.left), id(self.right)))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, PersistentTreeNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.left is other.left and
                self.right is other.right)


class PersistentTreeStrategy(ANodeTreeStrategy):
    """
    Persistent tree node strategy for immutable functional trees.
    
    Provides lock-free concurrency through immutability and structural sharing.
    Each operation returns a new tree while sharing unchanged nodes.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the persistent tree strategy."""
        super().__init__(NodeMode.PERSISTENT_TREE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.balanced = options.get('balanced', True)  # Use AVL balancing
        
        # Core persistent tree
        self._root: Optional[PersistentTreeNode] = None
        self._size = 0
        self._version = 0
        
        # Statistics
        self._total_allocations = 0
        self._total_shares = 0
        self._max_height = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the persistent tree strategy."""
        return (NodeTrait.PERSISTENT | NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _create_node(self, key: str, value: Any, left: Optional[PersistentTreeNode] = None,
                    right: Optional[PersistentTreeNode] = None) -> PersistentTreeNode:
        """Create new node with structural sharing."""
        self._total_allocations += 1
        height = 1 + max(
            left.height if left else 0,
            right.height if right else 0
        )
        return PersistentTreeNode(key, value, left, right, height)
    
    def _get_height(self, node: Optional[PersistentTreeNode]) -> int:
        """Get height of node."""
        return node.height if node else 0
    
    def _get_balance(self, node: Optional[PersistentTreeNode]) -> int:
        """Get balance factor of node."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _rotate_right(self, node: PersistentTreeNode) -> PersistentTreeNode:
        """Right rotation for AVL balancing."""
        left = node.left
        if not left:
            return node
        
        # Create new nodes with structural sharing
        new_right = self._create_node(node.key, node.value, left.right, node.right)
        new_root = self._create_node(left.key, left.value, left.left, new_right)
        
        return new_root
    
    def _rotate_left(self, node: PersistentTreeNode) -> PersistentTreeNode:
        """Left rotation for AVL balancing."""
        right = node.right
        if not right:
            return node
        
        # Create new nodes with structural sharing
        new_left = self._create_node(node.key, node.value, node.left, right.left)
        new_root = self._create_node(right.key, right.value, new_left, right.right)
        
        return new_root
    
    def _balance_node(self, node: PersistentTreeNode) -> PersistentTreeNode:
        """Balance node using AVL rotations."""
        if not self.balanced:
            return node
        
        balance = self._get_balance(node)
        
        # Left heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                # Left-Right case
                new_left = self._rotate_left(node.left)
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._rotate_right(new_node)
            else:
                # Left-Left case
                return self._rotate_right(node)
        
        # Right heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                # Right-Left case
                new_right = self._rotate_right(node.right)
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._rotate_left(new_node)
            else:
                # Right-Right case
                return self._rotate_left(node)
        
        return node
    
    def _insert_node(self, node: Optional[PersistentTreeNode], key: str, value: Any) -> Tuple[PersistentTreeNode, bool]:
        """Insert node with structural sharing."""
        if not node:
            new_node = self._create_node(key, value)
            return new_node, True
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            new_left, inserted = self._insert_node(node.left, key, value)
            if inserted:
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        elif normalized_key > node_key:
            new_right, inserted = self._insert_node(node.right, key, value)
            if inserted:
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        else:
            # Key exists, update value
            if node.value == value:
                # Share unchanged node
                self._total_shares += 1
                return node, False
            else:
                new_node = self._create_node(node.key, value, node.left, node.right)
                return new_node, False
    
    def _find_node(self, node: Optional[PersistentTreeNode], key: str) -> Optional[PersistentTreeNode]:
        """Find node by key."""
        if not node:
            return None
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            return self._find_node(node.left, key)
        elif normalized_key > node_key:
            return self._find_node(node.right, key)
        else:
            return node
    
    def _delete_node(self, node: Optional[PersistentTreeNode], key: str) -> Tuple[Optional[PersistentTreeNode], bool]:
        """Delete node with structural sharing."""
        if not node:
            return None, False
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            new_left, deleted = self._delete_node(node.left, key)
            if deleted:
                new_node = self._create_node(node.key, node.value, new_left, node.right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        elif normalized_key > node_key:
            new_right, deleted = self._delete_node(node.right, key)
            if deleted:
                new_node = self._create_node(node.key, node.value, node.left, new_right)
                return self._balance_node(new_node), True
            else:
                # Share unchanged node
                self._total_shares += 1
                return node, False
        else:
            # Found node to delete
            if not node.left:
                return node.right, True
            elif not node.right:
                return node.left, True
            else:
                # Node has both children, find successor
                successor = self._find_min(node.right)
                new_right, _ = self._delete_node(node.right, successor.key)
                new_node = self._create_node(successor.key, successor.value, node.left, new_right)
                return self._balance_node(new_node), True
    
    def _find_min(self, node: PersistentTreeNode) -> PersistentTreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _inorder_traversal(self, node: Optional[PersistentTreeNode]) -> Iterator[Tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair, returning new tree."""
        if not isinstance(key, str):
            key = str(key)
        
        new_root, inserted = self._insert_node(self._root, key, value)
        self._root = new_root
        
        if inserted:
            self._size += 1
            self._version += 1
        
        self._max_height = max(self._max_height, self._get_height(self._root))
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
        node = self._find_node(self._root, key)
        return node.value if node else default
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        new_root, deleted = self._delete_node(self._root, key)
        self._root = new_root
        
        if deleted:
            self._size -= 1
            self._version += 1
        
        return deleted
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._find_node(self._root, key) is not None
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = None
        self._size = 0
        self._version += 1
    
    def size(self) -> int:
        """Get number of key-value pairs."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self._root is None
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Iterate over keys in sorted order."""
        for key, _ in self._inorder_traversal(self._root):
            yield key
    
    def values(self) -> Iterator[Any]:
        """Iterate over values in key order."""
        for _, value in self._inorder_traversal(self._root):
            yield value
    
    def items(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over key-value pairs in sorted order."""
        yield from self._inorder_traversal(self._root)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        yield from self.keys()
    
    # ============================================================================
    # PERSISTENT TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def snapshot(self) -> 'xPersistentTreeStrategy':
        """Create a snapshot of the current tree."""
        snapshot = xPersistentTreeStrategy(self.traits, **self.options)
        snapshot._root = self._root  # Share root (structural sharing)
        snapshot._size = self._size
        snapshot._version = self._version
        return snapshot
    
    def merge(self, other: 'xPersistentTreeStrategy') -> 'xPersistentTreeStrategy':
        """Merge with another persistent tree."""
        result = xPersistentTreeStrategy(self.traits, **self.options)
        
        # Copy all items from both trees
        for key, value in self.items():
            result.put(key, value)
        for key, value in other.items():
            result.put(key, value)
        
        return result
    
    def get_version(self) -> int:
        """Get current version number."""
        return self._version
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'version': self._version,
            'total_allocations': self._total_allocations,
            'total_shares': self._total_shares,
            'sharing_ratio': self._total_shares / max(1, self._total_allocations),
            'strategy': 'PERSISTENT_TREE',
            'backend': 'Immutable AVL tree with structural sharing',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
