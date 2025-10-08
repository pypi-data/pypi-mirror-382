"""
Linked List Node Strategy Implementation

This module implements the LINKED_LIST strategy for efficient
insertions and deletions with sequential access patterns.
"""

from typing import Any, Iterator, List, Dict, Optional
from .base import ANodeLinearStrategy
from ...types import NodeMode, NodeTrait


class ListNode:
    """Node in the doubly linked list."""
    
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional['ListNode'] = None
        self.next: Optional['ListNode'] = None


class LinkedListStrategy(ANodeLinearStrategy):
    """
    Linked List node strategy for efficient insertions and deletions.
    
    Provides O(1) insertions/deletions at known positions with
    sequential access patterns optimized for iteration.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Linked List strategy."""
        super().__init__(data=None, **options)
        self._mode = NodeMode.LINKED_LIST
        self._traits = traits
        
        self.doubly_linked = options.get('doubly_linked', True)
        
        # Doubly linked list with sentinel nodes
        self._head = ListNode("HEAD", None)
        self._tail = ListNode("TAIL", None)
        self._head.next = self._tail
        self._tail.prev = self._head
        
        # Quick access mapping
        self._key_to_node: Dict[str, ListNode] = {}
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the linked list strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """Insert key-value pair."""
        key_str = str(key)
        if key_str in self._key_to_node:
            # Update existing
            self._key_to_node[key_str].value = value
        else:
            # Insert new node at end
            self._insert_at_end(key_str, value)
    
    def find(self, key: Any) -> Any:
        """Find value by key."""
        key_str = str(key)
        node = self._key_to_node.get(key_str)
        return node.value if node else None
    
    def delete(self, key: Any) -> bool:
        """Delete by key."""
        key_str = str(key)
        if key_str in self._key_to_node:
            self._remove_node(self._key_to_node[key_str])
            del self._key_to_node[key_str]
            return True
        return False
    
    def size(self) -> int:
        """Get size."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._size == 0
    
    def to_native(self) -> List[Any]:
        """Convert to native list."""
        result = []
        current = self._head.next
        while current != self._tail:
            result.append(current.value)
            current = current.next
        return result
    
    # ============================================================================
    # LINEAR STRATEGY METHODS
    # ============================================================================
    
    def push_front(self, value: Any) -> None:
        """Add element to front."""
        self._insert_after(self._head, str(self._size), value)
    
    def push_back(self, value: Any) -> None:
        """Add element to back."""
        self._insert_before(self._tail, str(self._size), value)
    
    def pop_front(self) -> Any:
        """Remove element from front."""
        if self._size == 0:
            raise IndexError("pop from empty list")
        first_node = self._head.next
        value = first_node.value
        self._remove_node(first_node)
        return value
    
    def pop_back(self) -> Any:
        """Remove element from back."""
        if self._size == 0:
            raise IndexError("pop from empty list")
        last_node = self._tail.prev
        value = last_node.value
        self._remove_node(last_node)
        return value
    
    def get_at_index(self, index: int) -> Any:
        """Get element at index."""
        if index < 0 or index >= self._size:
            raise IndexError("list index out of range")
        
        current = self._head.next
        for _ in range(index):
            current = current.next
        return current.value
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index."""
        if index < 0 or index >= self._size:
            raise IndexError("list index out of range")
        
        current = self._head.next
        for _ in range(index):
            current = current.next
        current.value = value
    
    # ============================================================================
    # AUTO-3 Phase 1 methods
    # ============================================================================
    
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        return self
    
    def as_stack(self):
        """Provide Stack behavioral view."""
        # TODO: Implement Stack view
        return self
    
    def as_queue(self):
        """Provide Queue behavioral view."""
        # TODO: Implement Queue view
        return self
    
    def as_deque(self):
        """Provide Deque behavioral view."""
        # TODO: Implement Deque view
        return self
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _insert_at_end(self, key: str, value: Any) -> None:
        """Insert new node at the end."""
        self._insert_before(self._tail, key, value)
    
    def _insert_after(self, node: ListNode, key: str, value: Any) -> None:
        """Insert new node after specified node."""
        new_node = ListNode(key, value)
        new_node.next = node.next
        new_node.prev = node
        node.next.prev = new_node
        node.next = new_node
        self._key_to_node[key] = new_node
        self._size += 1
    
    def _insert_before(self, node: ListNode, key: str, value: Any) -> None:
        """Insert new node before specified node."""
        new_node = ListNode(key, value)
        new_node.prev = node.prev
        new_node.next = node
        node.prev.next = new_node
        node.prev = new_node
        self._key_to_node[key] = new_node
        self._size += 1
    
    def _remove_node(self, node: ListNode) -> None:
        """Remove node from list."""
        node.prev.next = node.next
        node.next.prev = node.prev
        self._size -= 1
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'LINKED_LIST',
            'backend': 'Doubly linked list',
            'complexity': {
                'get': 'O(n)',
                'put': 'O(1)',
                'insert': 'O(1) at known position',
                'delete': 'O(1) at known position',
                'search': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': self._size,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'doubly_linked': self.doubly_linked
        }
