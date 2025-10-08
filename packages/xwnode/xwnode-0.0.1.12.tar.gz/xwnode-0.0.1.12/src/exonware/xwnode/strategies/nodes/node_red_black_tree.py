#exonware\xnode\strategies\impls\node_red_black_tree.py
"""
Red-Black Tree Node Strategy Implementation

This module implements the RED_BLACK_TREE strategy for self-balancing binary
search trees with guaranteed O(log n) height and operations.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class RedBlackTreeNode:
    """Node in the red-black tree."""
    
    def __init__(self, key: str, value: Any = None, color: str = 'RED'):
        self.key = key
        self.value = value
        self.color = color  # 'RED' or 'BLACK'
        self.left: Optional['RedBlackTreeNode'] = None
        self.right: Optional['RedBlackTreeNode'] = None
        self.parent: Optional['RedBlackTreeNode'] = None
        self._hash = None
    
    def __hash__(self) -> int:
        """Cache hash for performance."""
        if self._hash is None:
            self._hash = hash((self.key, self.value, self.color))
        return self._hash
    
    def __eq__(self, other) -> bool:
        """Structural equality."""
        if not isinstance(other, RedBlackTreeNode):
            return False
        return (self.key == other.key and 
                self.value == other.value and
                self.color == other.color)
    
    def is_red(self) -> bool:
        """Check if node is red."""
        return self.color == 'RED'
    
    def is_black(self) -> bool:
        """Check if node is black."""
        return self.color == 'BLACK'
    
    def set_red(self) -> None:
        """Set node color to red."""
        self.color = 'RED'
    
    def set_black(self) -> None:
        """Set node color to black."""
        self.color = 'BLACK'


class RedBlackTreeStrategy(ANodeTreeStrategy):
    """
    Red-black tree node strategy for self-balancing binary search trees.
    
    Provides guaranteed O(log n) height and operations through color-based
    balancing rules and rotations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the red-black tree strategy."""
        super().__init__(NodeMode.RED_BLACK_TREE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        
        # Core red-black tree
        self._root: Optional[RedBlackTreeNode] = None
        self._size = 0
        
        # Statistics
        self._total_insertions = 0
        self._total_deletions = 0
        self._total_rotations = 0
        self._max_height = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the red-black tree strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _get_height(self, node: Optional[RedBlackTreeNode]) -> int:
        """Get height of node."""
        if not node:
            return 0
        
        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)
        return 1 + max(left_height, right_height)
    
    def _rotate_left(self, node: RedBlackTreeNode) -> None:
        """Left rotation around node."""
        right_child = node.right
        if not right_child:
            return
        
        # Update parent connections
        node.right = right_child.left
        if right_child.left:
            right_child.left.parent = node
        
        right_child.parent = node.parent
        if not node.parent:
            self._root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child
        
        # Update rotation
        right_child.left = node
        node.parent = right_child
        
        self._total_rotations += 1
    
    def _rotate_right(self, node: RedBlackTreeNode) -> None:
        """Right rotation around node."""
        left_child = node.left
        if not left_child:
            return
        
        # Update parent connections
        node.left = left_child.right
        if left_child.right:
            left_child.right.parent = node
        
        left_child.parent = node.parent
        if not node.parent:
            self._root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child
        
        # Update rotation
        left_child.right = node
        node.parent = left_child
        
        self._total_rotations += 1
    
    def _fix_insertion(self, node: RedBlackTreeNode) -> None:
        """Fix red-black tree properties after insertion."""
        while node.parent and node.parent.is_red():
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle and uncle.is_red():
                    # Case 1: Uncle is red
                    node.parent.set_black()
                    uncle.set_black()
                    node.parent.parent.set_red()
                    node = node.parent.parent
                else:
                    # Case 2: Uncle is black and node is right child
                    if node == node.parent.right:
                        node = node.parent
                        self._rotate_left(node)
                    
                    # Case 3: Uncle is black and node is left child
                    node.parent.set_black()
                    node.parent.parent.set_red()
                    self._rotate_right(node.parent.parent)
            else:
                # Mirror cases for right side
                uncle = node.parent.parent.left
                if uncle and uncle.is_red():
                    # Case 1: Uncle is red
                    node.parent.set_black()
                    uncle.set_black()
                    node.parent.parent.set_red()
                    node = node.parent.parent
                else:
                    # Case 2: Uncle is black and node is left child
                    if node == node.parent.left:
                        node = node.parent
                        self._rotate_right(node)
                    
                    # Case 3: Uncle is black and node is right child
                    node.parent.set_black()
                    node.parent.parent.set_red()
                    self._rotate_left(node.parent.parent)
        
        self._root.set_black()
    
    def _insert_node(self, key: str, value: Any) -> bool:
        """Insert node with given key and value."""
        normalized_key = self._normalize_key(key)
        
        # Create new node
        new_node = RedBlackTreeNode(key, value, 'RED')
        
        # Find insertion point
        current = self._root
        parent = None
        
        while current:
            parent = current
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                # Key already exists, update value
                current.value = value
                return False
        
        # Insert new node
        new_node.parent = parent
        if not parent:
            self._root = new_node
        elif normalized_key < self._normalize_key(parent.key):
            parent.left = new_node
        else:
            parent.right = new_node
        
        # Fix red-black tree properties
        self._fix_insertion(new_node)
        
        self._size += 1
        self._total_insertions += 1
        self._max_height = max(self._max_height, self._get_height(self._root))
        return True
    
    def _find_node(self, key: str) -> Optional[RedBlackTreeNode]:
        """Find node with given key."""
        normalized_key = self._normalize_key(key)
        current = self._root
        
        while current:
            current_key = self._normalize_key(current.key)
            if normalized_key < current_key:
                current = current.left
            elif normalized_key > current_key:
                current = current.right
            else:
                return current
        
        return None
    
    def _find_min(self, node: RedBlackTreeNode) -> RedBlackTreeNode:
        """Find minimum node in subtree."""
        while node.left:
            node = node.left
        return node
    
    def _find_max(self, node: RedBlackTreeNode) -> RedBlackTreeNode:
        """Find maximum node in subtree."""
        while node.right:
            node = node.right
        return node
    
    def _delete_node(self, key: str) -> bool:
        """Delete node with given key."""
        node = self._find_node(key)
        if not node:
            return False
        
        # Find replacement node
        if not node.left:
            replacement = node.right
        elif not node.right:
            replacement = node.left
        else:
            replacement = self._find_min(node.right)
            node.key = replacement.key
            node.value = replacement.value
            node = replacement
        
        # Remove node
        if replacement:
            replacement.parent = node.parent
        
        if not node.parent:
            self._root = replacement
        elif node == node.parent.left:
            node.parent.left = replacement
        else:
            node.parent.right = replacement
        
        # Fix red-black tree properties if needed
        if node.is_black() and replacement:
            self._fix_deletion(replacement)
        elif node.is_black():
            self._fix_deletion(None)
        
        self._size -= 1
        self._total_deletions += 1
        return True
    
    def _fix_deletion(self, node: Optional[RedBlackTreeNode]) -> None:
        """Fix red-black tree properties after deletion."""
        while node != self._root and (not node or node.is_black()):
            if node == node.parent.left:
                sibling = node.parent.right
                if sibling and sibling.is_red():
                    # Case 1: Sibling is red
                    sibling.set_black()
                    node.parent.set_red()
                    self._rotate_left(node.parent)
                    sibling = node.parent.right
                
                if (not sibling.left or sibling.left.is_black()) and \
                   (not sibling.right or sibling.right.is_black()):
                    # Case 2: Sibling and its children are black
                    sibling.set_red()
                    node = node.parent
                else:
                    if not sibling.right or sibling.right.is_black():
                        # Case 3: Sibling's right child is black
                        sibling.left.set_black()
                        sibling.set_red()
                        self._rotate_right(sibling)
                        sibling = node.parent.right
                    
                    # Case 4: Sibling's right child is red
                    sibling.color = node.parent.color
                    node.parent.set_black()
                    sibling.right.set_black()
                    self._rotate_left(node.parent)
                    node = self._root
            else:
                # Mirror cases for right side
                sibling = node.parent.left
                if sibling and sibling.is_red():
                    # Case 1: Sibling is red
                    sibling.set_black()
                    node.parent.set_red()
                    self._rotate_right(node.parent)
                    sibling = node.parent.left
                
                if (not sibling.right or sibling.right.is_black()) and \
                   (not sibling.left or sibling.left.is_black()):
                    # Case 2: Sibling and its children are black
                    sibling.set_red()
                    node = node.parent
                else:
                    if not sibling.left or sibling.left.is_black():
                        # Case 3: Sibling's left child is black
                        sibling.right.set_black()
                        sibling.set_red()
                        self._rotate_left(sibling)
                        sibling = node.parent.left
                    
                    # Case 4: Sibling's left child is red
                    sibling.color = node.parent.color
                    node.parent.set_black()
                    sibling.left.set_black()
                    self._rotate_right(node.parent)
                    node = self._root
        
        if node:
            node.set_black()
    
    def _inorder_traversal(self, node: Optional[RedBlackTreeNode]) -> Iterator[Tuple[str, Any]]:
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
        
        self._insert_node(key, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key."""
        if not isinstance(key, str):
            key = str(key)
        
        node = self._find_node(key)
        return node.value if node else default
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._delete_node(key)
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        if not isinstance(key, str):
            key = str(key)
        
        return self._find_node(key) is not None
    
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
    # RED-BLACK TREE SPECIFIC OPERATIONS
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
    
    def is_valid_rb_tree(self) -> bool:
        """Check if tree satisfies red-black tree properties."""
        if not self._root:
            return True
        
        # Check if root is black
        if self._root.is_red():
            return False
        
        # Check all paths have same number of black nodes
        def check_black_height(node: Optional[RedBlackTreeNode]) -> int:
            if not node:
                return 1
            
            left_height = check_black_height(node.left)
            right_height = check_black_height(node.right)
            
            if left_height != right_height:
                return -1
            
            return left_height + (1 if node.is_black() else 0)
        
        return check_black_height(self._root) != -1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'size': self._size,
            'height': self._get_height(self._root),
            'max_height': self._max_height,
            'total_insertions': self._total_insertions,
            'total_deletions': self._total_deletions,
            'total_rotations': self._total_rotations,
            'is_valid_rb_tree': self.is_valid_rb_tree(),
            'strategy': 'RED_BLACK_TREE',
            'backend': 'Self-balancing red-black tree with guaranteed O(log n) height',
            'traits': [trait.name for trait in NodeTrait if self.has_trait(trait)]
        }
