"""
Stack Strategy Implementation

Implements a LIFO (Last In, First Out) data structure using Python's list.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

from typing import Any, Iterator, List, Optional, Dict, Union
from .base import ANodeLinearStrategy
from ...types import NodeMode, NodeTrait


class StackStrategy(ANodeLinearStrategy):
    """
    Stack node strategy for LIFO (Last In, First Out) operations.
    
    Provides O(1) push and pop operations with efficient memory usage
    for stack-based algorithms and recursive function simulation.
    """
    
    def __init__(self):
        """Initialize an empty stack."""
        super().__init__()
        self._stack: List[Any] = []
        self._mode = NodeMode.STACK
        self._traits = {NodeTrait.LIFO, NodeTrait.FAST_INSERT, NodeTrait.FAST_DELETE}
    
    def insert(self, key: str, value: Any) -> None:
        """Push an item onto the stack."""
        self._stack.append((key, value))
        self._record_access("push")
    
    def find(self, key: str) -> Optional[Any]:
        """Find an item in the stack (O(n) operation)."""
        for k, v in reversed(self._stack):
            if k == key:
                self._record_access("find")
                return v
        return None
    
    def delete(self, key: str) -> bool:
        """Remove an item from the stack."""
        for i, (k, v) in enumerate(self._stack):
            if k == key:
                self._stack.pop(i)
                self._record_access("delete")
                return True
        return False
    
    def size(self) -> int:
        """Get the number of items in the stack."""
        return len(self._stack)
    
    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return len(self._stack) == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert stack to native dictionary format."""
        return dict(reversed(self._stack))
    
    def from_native(self, data: Dict[str, Any]) -> None:
        """Load stack from native dictionary format."""
        self._stack = [(k, v) for k, v in data.items()]
    
    def push(self, value: Any) -> None:
        """Push a value onto the stack."""
        key = f"item_{len(self._stack)}"
        self.insert(key, value)
    
    def pop(self) -> Optional[Any]:
        """Pop and return the top item from the stack."""
        if self.is_empty():
            return None
        key, value = self._stack.pop()
        self._record_access("pop")
        return value
    
    def peek(self) -> Optional[Any]:
        """Peek at the top item without removing it."""
        if self.is_empty():
            return None
        key, value = self._stack[-1]
        self._record_access("peek")
        return value
    
    def clear(self) -> None:
        """Clear all items from the stack."""
        self._stack.clear()
        self._record_access("clear")
    
    def get_at_index(self, index: int) -> Optional[Any]:
        """Get item at specific index (0 = top of stack)."""
        if 0 <= index < len(self._stack):
            key, value = self._stack[-(index + 1)]
            self._record_access("get_at_index")
            return value
        return None
    
    def push_front(self, value: Any) -> None:
        """Push to front (bottom) of stack."""
        self._stack.insert(0, (f"item_{len(self._stack)}", value))
        self._record_access("push_front")
    
    def push_back(self, value: Any) -> None:
        """Push to back (top) of stack."""
        self.push(value)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate through stack items (top to bottom)."""
        for key, value in reversed(self._stack):
            yield value
    
    def __repr__(self) -> str:
        """String representation of the stack."""
        return f"StackStrategy(size={len(self._stack)}, top={self.peek()})"
    
    # Required abstract methods from base classes
    def pop_front(self) -> Any:
        """Remove element from front (same as pop for stack)."""
        return self.pop()
    
    def pop_back(self) -> Any:
        """Remove element from back (not applicable for stack)."""
        raise NotImplementedError("Stack doesn't support pop_back")
    
    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index (not recommended for stack)."""
        if 0 <= index < len(self._stack):
            key, old_value = self._stack[-(index + 1)]
            self._stack[-(index + 1)] = (key, value)
    
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        return self
    
    def as_stack(self):
        """Provide Stack behavioral view."""
        return self
    
    def as_queue(self):
        """Provide Queue behavioral view (not recommended)."""
        raise NotImplementedError("Stack cannot behave as Queue")
    
    def as_deque(self):
        """Provide Deque behavioral view."""
        return self
