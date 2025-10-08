"""
Heap Node Strategy Implementation

This module implements the HEAP strategy for priority queue operations.
"""

import heapq
from typing import Any, Iterator, List, Optional, Dict
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait
from ..utils import (
    MinHeap,
    safe_to_native_conversion,
    create_basic_metrics,
    create_basic_backend_info,
    create_size_tracker,
    create_access_tracker,
    update_size_tracker,
    record_access,
    get_access_metrics
)


class HeapStrategy(ANodeTreeStrategy):
    """
    Heap node strategy for priority queue operations.
    
    Optimized for push, pop, and peek operations with configurable min/max behavior.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the heap strategy."""
        super().__init__(NodeMode.HEAP, traits, **options)
        self._is_max_heap = options.get('max_heap', False)
        self._heap = MinHeap(max_heap=self._is_max_heap)
        self._size_tracker = create_size_tracker()
        self._access_tracker = create_access_tracker()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the heap strategy."""
        return (NodeTrait.ORDERED | NodeTrait.PRIORITY_QUEUE)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair (key is priority, value is data)."""
        priority = float(key) if key is not None else 0.0
        data = value if value is not None else key
        self._heap.push(data, priority)
        update_size_tracker(self._size_tracker, 1)
        record_access(self._access_tracker, 'put_count')
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key (peek operation)."""
        record_access(self._access_tracker, 'get_count')
        try:
            return self._heap.peek()
        except IndexError:
            return default
    
    def has(self, key: Any) -> bool:
        """Check if heap has any items."""
        return len(self._heap) > 0
    
    def remove(self, key: Any) -> bool:
        """Remove the top item from the heap."""
        try:
            self._heap.pop()
            update_size_tracker(self._size_tracker, -1)
            record_access(self._access_tracker, 'delete_count')
            return True
        except IndexError:
            return False
    
    def delete(self, key: Any) -> bool:
        """Remove the top item (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._heap = MinHeap(max_heap=self._is_max_heap)
        self._size_tracker['size'] = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys (priorities) in heap order."""
        return (str(priority) for priority, _, _ in self._heap._heap)
    
    def values(self) -> Iterator[Any]:
        """Get all values in heap order."""
        return (value for _, _, value in self._heap._heap)
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in heap order."""
        return ((str(priority), value) for priority, _, value in self._heap._heap)
    
    def __len__(self) -> int:
        """Get the number of items."""
        return self._size_tracker['size']
    
    def to_native(self) -> List[Any]:
        """Convert to native Python list sorted by priority."""
        return [safe_to_native_conversion(value) for _, _, value in sorted(self._heap._heap)]
    
    @property
    def is_list(self) -> bool:
        """This behaves like a list (priority-ordered)."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This is not a dict strategy."""
        return False
    
    # ============================================================================
    # HEAP-SPECIFIC OPERATIONS
    # ============================================================================
    
    def push(self, value: Any, priority: float = None) -> str:
        """Push a value with optional priority. Returns the generated key."""
        key = self._heap.push(value, priority)
        update_size_tracker(self._size_tracker, 1)
        return key
    
    def pop(self) -> Any:
        """Remove and return the highest/lowest priority item."""
        value = self._heap.pop()
        update_size_tracker(self._size_tracker, -1)
        return value
    
    def peek(self) -> Any:
        """Peek at the highest/lowest priority item without removing."""
        return self._heap.peek()
    
    def peek_priority(self) -> float:
        """Peek at the priority of the top item."""
        return self._heap.peek_priority()
    
    def pushpop(self, value: Any, priority: float = None) -> Any:
        """Push value and pop the highest/lowest priority item efficiently."""
        old_value = self._heap.pushpop(value, priority)
        if old_value is None:
            update_size_tracker(self._size_tracker, 1)
        return old_value
    
    def replace(self, value: Any, priority: float = None) -> Any:
        """Replace the top item and return the old top item."""
        old_value = self._heap.replace(value, priority)
        return old_value
    
    def heapify(self) -> None:
        """Rebuild the heap in-place."""
        self._heap.heapify()
    
    def nlargest(self, n: int) -> List[Any]:
        """Get the n largest items."""
        return self._heap.nlargest(n)
    
    def nsmallest(self, n: int) -> List[Any]:
        """Get the n smallest items."""
        return self._heap.nsmallest(n)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        heap_type = "Max Heap" if self._is_max_heap else "Min Heap"
        return create_basic_backend_info(
            'HEAP',
            f'Python heapq ({heap_type})',
            complexity={
                'push': 'O(log n)',
                'pop': 'O(log n)',
                'peek': 'O(1)',
                'heapify': 'O(n)'
            }
        )
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        base_metrics = create_basic_metrics('HEAP', self._size_tracker['size'])
        access_metrics = get_access_metrics(self._access_tracker)
        base_metrics.update(access_metrics)
        base_metrics.update({
            'heap_type': 'max' if self._is_max_heap else 'min',
            'is_empty': len(self._heap) == 0
        })
        return base_metrics
