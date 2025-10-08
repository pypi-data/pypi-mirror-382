"""
Linked List Node Strategy Implementation

This module implements the LINKED_LIST strategy for efficient
insertions and deletions with sequential access patterns.
"""

from typing import Any, Iterator, List, Dict, Optional
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class ListNode:
    """Node in the doubly linked list."""
    
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional['ListNode'] = None
        self.next: Optional['ListNode'] = None


class xLinkedListStrategy(aNodeStrategy):
    """
    Linked List node strategy for efficient insertions and deletions.
    
    Provides O(1) insertions/deletions at known positions with
    sequential access patterns optimized for iteration.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Linked List strategy."""
        super().__init__(NodeMode.LINKED_LIST, traits, **options)
        
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
    
    def _insert_after(self, prev_node: ListNode, key: str, value: Any) -> ListNode:
        """Insert new node after given node."""
        new_node = ListNode(key, value)
        next_node = prev_node.next
        
        # Link new node
        prev_node.next = new_node
        new_node.prev = prev_node
        new_node.next = next_node
        next_node.prev = new_node
        
        return new_node
    
    def _remove_node(self, node: ListNode) -> None:
        """Remove node from list."""
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
        
        # Clear references
        node.prev = None
        node.next = None
    
    def _get_node_at_index(self, index: int) -> Optional[ListNode]:
        """Get node at given index."""
        if index < 0 or index >= self._size:
            return None
        
        # Optimize direction based on index
        if index < self._size // 2:
            # Search from head
            current = self._head.next
            for _ in range(index):
                current = current.next
        else:
            # Search from tail
            current = self._tail.prev
            for _ in range(self._size - index - 1):
                current = current.prev
        
        return current if current != self._head and current != self._tail else None
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add/update key-value pair."""
        key_str = str(key)
        
        if key_str in self._key_to_node:
            # Update existing
            self._key_to_node[key_str].value = value
        else:
            # Insert at end
            new_node = self._insert_after(self._tail.prev, key_str, value)
            self._key_to_node[key_str] = new_node
            self._size += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "list_info":
            return {
                'size': self._size,
                'doubly_linked': self.doubly_linked,
                'first': self.first(),
                'last': self.last()
            }
        elif key_str.isdigit():
            # Numeric access by index
            index = int(key_str)
            node = self._get_node_at_index(index)
            return node.value if node else default
        
        node = self._key_to_node.get(key_str)
        return node.value if node else default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        
        if key_str == "list_info":
            return True
        elif key_str.isdigit():
            index = int(key_str)
            return 0 <= index < self._size
        
        return key_str in self._key_to_node
    
    def remove(self, key: Any) -> bool:
        """Remove key from list."""
        key_str = str(key)
        
        if key_str.isdigit():
            # Remove by index
            index = int(key_str)
            node = self._get_node_at_index(index)
            if node:
                self._remove_node(node)
                del self._key_to_node[node.key]
                self._size -= 1
                return True
            return False
        
        node = self._key_to_node.get(key_str)
        if node:
            self._remove_node(node)
            del self._key_to_node[key_str]
            self._size -= 1
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key from list (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._head.next = self._tail
        self._tail.prev = self._head
        self._key_to_node.clear()
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys in insertion order."""
        current = self._head.next
        while current != self._tail:
            yield current.key
            current = current.next
    
    def values(self) -> Iterator[Any]:
        """Get all values in insertion order."""
        current = self._head.next
        while current != self._tail:
            yield current.value
            current = current.next
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in insertion order."""
        current = self._head.next
        while current != self._tail:
            yield (current.key, current.value)
            current = current.next
    
    def __len__(self) -> int:
        """Get number of elements."""
        return self._size
    
    def to_native(self) -> List[Any]:
        """Convert to native Python list."""
        return list(self.values())
    
    @property
    def is_list(self) -> bool:
        """This is a list strategy."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This also behaves like a dict."""
        return True
    
    # ============================================================================
    # LINKED LIST SPECIFIC OPERATIONS
    # ============================================================================
    
    def append(self, value: Any) -> str:
        """Append value to end of list."""
        key = str(self._size)
        self.put(key, value)
        return key
    
    def prepend(self, value: Any) -> str:
        """Prepend value to beginning of list."""
        key = f"prepend_{self._size}"
        new_node = self._insert_after(self._head, key, value)
        self._key_to_node[key] = new_node
        self._size += 1
        return key
    
    def insert_at(self, index: int, value: Any) -> str:
        """Insert value at specific index."""
        if index < 0 or index > self._size:
            raise IndexError(f"Index {index} out of range")
        
        if index == 0:
            return self.prepend(value)
        elif index == self._size:
            return self.append(value)
        
        # Find insertion point
        prev_node = self._get_node_at_index(index - 1)
        if not prev_node:
            raise IndexError(f"Cannot find insertion point at index {index}")
        
        key = f"insert_{index}_{self._size}"
        new_node = self._insert_after(prev_node, key, value)
        self._key_to_node[key] = new_node
        self._size += 1
        return key
    
    def pop(self) -> Any:
        """Remove and return last element."""
        if self._size == 0:
            raise IndexError("pop from empty list")
        
        last_node = self._tail.prev
        value = last_node.value
        self._remove_node(last_node)
        del self._key_to_node[last_node.key]
        self._size -= 1
        return value
    
    def popleft(self) -> Any:
        """Remove and return first element."""
        if self._size == 0:
            raise IndexError("popleft from empty list")
        
        first_node = self._head.next
        value = first_node.value
        self._remove_node(first_node)
        del self._key_to_node[first_node.key]
        self._size -= 1
        return value
    
    def first(self) -> Any:
        """Get first element without removing."""
        if self._size == 0:
            return None
        return self._head.next.value
    
    def last(self) -> Any:
        """Get last element without removing."""
        if self._size == 0:
            return None
        return self._tail.prev.value
    
    def reverse(self) -> None:
        """Reverse the list in place."""
        if self._size <= 1:
            return
        
        # Swap all next/prev pointers
        current = self._head
        while current:
            current.next, current.prev = current.prev, current.next
            current = current.prev  # Note: we swapped, so prev is now next
        
        # Swap head and tail
        self._head, self._tail = self._tail, self._head
    
    def get_at_index(self, index: int) -> Any:
        """Get value at specific index."""
        node = self._get_node_at_index(index)
        if not node:
            raise IndexError(f"Index {index} out of range")
        return node.value
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set value at specific index."""
        node = self._get_node_at_index(index)
        if not node:
            raise IndexError(f"Index {index} out of range")
        node.value = value
    
    def find_index(self, value: Any) -> int:
        """Find index of first occurrence of value."""
        current = self._head.next
        index = 0
        
        while current != self._tail:
            if current.value == value:
                return index
            current = current.next
            index += 1
        
        return -1
    
    def remove_value(self, value: Any) -> bool:
        """Remove first occurrence of value."""
        current = self._head.next
        
        while current != self._tail:
            if current.value == value:
                self._remove_node(current)
                del self._key_to_node[current.key]
                self._size -= 1
                return True
            current = current.next
        
        return False
    
    def count_value(self, value: Any) -> int:
        """Count occurrences of value."""
        count = 0
        current = self._head.next
        
        while current != self._tail:
            if current.value == value:
                count += 1
            current = current.next
        
        return count
    
    def to_array(self) -> List[Any]:
        """Convert to array representation."""
        return list(self.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive linked list statistics."""
        return {
            'size': self._size,
            'doubly_linked': self.doubly_linked,
            'first_value': self.first(),
            'last_value': self.last(),
            'memory_overhead': self._size * (64 if self.doubly_linked else 32),  # Pointer overhead
            'access_pattern': 'sequential'
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'LINKED_LIST',
            'backend': f'{"Doubly" if self.doubly_linked else "Singly"} linked list with sentinel nodes',
            'doubly_linked': self.doubly_linked,
            'complexity': {
                'append': 'O(1)',
                'prepend': 'O(1)',
                'insert_at': 'O(n)',
                'remove_at': 'O(n)',
                'access_by_index': 'O(n)',
                'search': 'O(n)',
                'space': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        
        return {
            'size': stats['size'],
            'first_value': str(stats['first_value']) if stats['first_value'] is not None else 'None',
            'last_value': str(stats['last_value']) if stats['last_value'] is not None else 'None',
            'doubly_linked': stats['doubly_linked'],
            'memory_overhead': f"{stats['memory_overhead']} bytes",
            'access_pattern': stats['access_pattern']
        }
