#exonware\xnode\strategies\impls\node_avl_tree.py
"""
AVL Tree Node Strategy Implementation

This module implements the AVL_TREE strategy for strictly balanced binary
search trees with guaranteed O(log n) height and operations.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class AVLTreeNode:
    """Node in the AVL tree."""
    
    def __init__(self, key: str, value: Any = None, height: int = 1):
        self.key = key
        self.value = value
        self.height = height
        self.left: Optional['AVLTreeNode'] = None
        self.right: Optional['AVLTreeNode'] = None
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value, self.height))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, AVLTreeNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.height == other.height)


class AVLTreeStrategy(ANodeTreeStrategy):
    """
    AVL tree node strategy for strictly balanced binary search trees.
    
    Provides guaranteed O(log n) height and operations through height-based
    balancing rules and rotations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the AVL tree strategy."""
        super().__init__(NodeMode.AVL_TREE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        
        # Core AVL tree
        self._root: Optional[AVLTreeNode] = None
        self._size = 0
        
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_rotations = 0
        self._max_height = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the AVL tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _get_height(self, node: Optional[AVLTreeNode]) -> int:
        """Get height of node."""
        return node.height if node else 0
    
    def _get_balance(self, node: Optional[AVLTreeNode]) -> int:
        """Get balance factor of node."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _update_height(self, node: AVLTreeNode) -> None:
        """Update height of node."""
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
    
    def _rotate_right(self, node: AVLTreeNode) -> AVLTreeNode:
        """Right rotation around node."""
        left_child = node.left
        if not left_child:
            return node
        
        # Perform rotation
        node.left = left_child.right
        left_child.right = node
        
        # Update heights
        self._update_height(node)
        self._update_height(left_child)
        
        self._total_rotations += 1
        return left_child
    
    def _rotate_left(self, node: AVLTreeNode) -> AVLTreeNode:
        """Left rotation around node."""
        right_child = node.right
        if not right_child:
            return node
        
        # Perform rotation
        node.right = right_child.left
        right_child.left = node
        
        # Update heights
        self._update_height(node)
        self._update_height(right_child)
        
        self._total_rotations += 1
        return right_child
    
    def _balance_node(self, node: AVLTreeNode) -> AVLTreeNode:
        """Balance node using AVL rotations."""
        # Update height
        self._update_height(node)
        
        # Get balance factor
        balance = self._get_balance(node)
        
        # Left heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                # Left-Right case
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
            else:
                # Left-Left case
                return self._rotate_right(node)
        
        # Right heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                # Right-Left case
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
            else:
                # Right-Right case
                return self._rotate_left(node)
        
        return node
    
    def _insert_node(self, node: Optional[AVLTreeNode], key: str, value: Any) -> Tuple[AVLTreeNode, bool]:
        """Insert node with given key and value."""
        if not node:
            new_node = AVLTreeNode(key, value)
            return new_node, True
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            node.left, inserted = self._insert_node(node.left, key, value)
        elif normalized_key > node_key:
            node.right, inserted = self._insert_node(node.right, key, value)
        else:
            # Key already exists, update value
            node.value = value
            return node, False
        
        # Balance the node
        balanced_node = self._balance_node(node)
        return balanced_node, inserted
    
    def _find_node(self, node: Optional[AVLTreeNode], key: str) -> Optional[AVLTreeNode]:
        """Find node with given key."""
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
    
    def _find_min(self, node: AVLTreeNode) -> AVLTreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _find_max(self, node: AVLTreeNode) -> AVLTreeNode:
        """Find maximum node in subtree."""
        while node.right:
            node = node.right
        return node
    
    def _delete_node(self, node: Optional[AVLTreeNode], key: str) -> Tuple[Optional[AVLTreeNode], bool]:
        """Delete node with given key."""
        if not node:
            return None, False
        
        normalized_key = self._normalize_key(key)
        node_key = self._normalize_key(node.key)
        
        if normalized_key < node_key:
            node.left, deleted = self._delete_node(node.left, key)
        elif normalized_key > node_key:
            node.right, deleted = self._delete_node(node.right, key)
        else:
            # Found node to delete
            if not node.left:
                return node.right, True
            elif not node.right:
                return node.left, True
            else:
                # Node has both children, find successor
                successor = self._find_min(node.right)
                node.key = successor.key
                node.value = successor.value
                node.right, _ = self._delete_node(node.right, successor.key)
                deleted = True
        
        if not deleted:
            return node, False
        
        # Balance the node
        balanced_node = self._balance_node(node)
        return balanced_node, True
    
    def _inorder_traversal(self, node: Optional[AVLTreeNode]) -> Iterator[Tuple[str, Any]]:
        """In-order traversal of tree."""
        if node:
            yield from self._inorder_traversal(node.left)
            yield (node.key, node.value)
            yield from self._inorder_traversal(node.right)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        self._root, inserted = self._insert_node(self._root, key, value)
        if inserted:
            self._size += 1
            self._total_insertions += 1
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
        
        self._root, deleted = self._delete_node(self._root, key)
        if deleted:
            self._size -= 1
            self._total_deletions += 1
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
    # AVL TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_min(self) -> Optional[Tuple[str, Any]]:
        """Get the minimum key-value pair."""
        if not self._root:
            return None
        
        min_node = self._find_min(self._root)
        return (min_node.key, min_node.value)
    
    def get_max(self) -> Optional[Tuple[str, Any]]:
        """Get the maximum key-value pair."""
        if not self._root:
            return None
        
        max_node = self._find_max(self._root)
        return (max_node.key, max_node.value)
    
    def get_height(self) -> int:
        """Get the height of the tree."""
        return self._get_height(self._root)
    
    def is_balanced(self) -> bool:
        """Check if tree is AVL balanced."""
        def check_balance(node: Optional[AVLTreeNode]) -> bool:
            if not node:
                return True
            
            balance = self._get_balance(node)
            if abs(balance) > 1:
                return False
            
            return check_balance(node.left) and check_balance(node.right)
        
        return check_balance(self._root)
    
    def get_balance_factor(self, key: str) -> Optional[int]:
        """Get balance factor of node with given key."""
        node = self._find_node(self._root, key)
        return self._get_balance(node) if node else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_rotations': self._total_rotations,
            'is_balanced': self.is_balanced(),
            'strategy': 'AVL_TREE',
            'backend': 'Strictly balanced AVL tree with guaranteed O(log n) height',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
