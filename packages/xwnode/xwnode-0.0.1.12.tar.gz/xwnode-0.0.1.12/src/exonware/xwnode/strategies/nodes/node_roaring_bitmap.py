"""
Roaring Bitmap Node Strategy Implementation

This module implements the ROARING_BITMAP strategy for highly compressed
bitmap operations with excellent performance for sparse data.
"""

from typing import Any, Iterator, List, Dict, Optional, Set, Tuple
from collections import defaultdict
import struct
from .base import ANodeMatrixStrategy
from ...types import NodeMode, NodeTrait


class Container:
    """Base class for Roaring Bitmap containers."""
    
    def __init__(self):
        self.cardinality = 0
    
    def contains(self, x: int) -> bool:
        """Check if value is in container."""
        raise NotImplementedError
    
    def add(self, x: int) -> bool:
        """Add value to container. Returns True if value was new."""
        raise NotImplementedError
    
    def remove(self, x: int) -> bool:
        """Remove value from container. Returns True if value existed."""
        raise NotImplementedError
    
    def to_array(self) -> List[int]:
        """Convert container to sorted array."""
        raise NotImplementedError


class ArrayContainer(Container):
    """Array container for small sets (< 4096 elements)."""
    
    def __init__(self):
        super().__init__()
        self.values: List[int] = []
    
    def contains(self, x: int) -> bool:
        """Binary search for value."""
        left, right = 0, len(self.values)
        while left < right:
            mid = (left + right) // 2
            if self.values[mid] < x:
                left = mid + 1
            else:
                right = mid
        return left < len(self.values) and self.values[left] == x
    
    def add(self, x: int) -> bool:
        """Insert value in sorted order."""
        left, right = 0, len(self.values)
        while left < right:
            mid = (left + right) // 2
            if self.values[mid] < x:
                left = mid + 1
            else:
                right = mid
        
        if left < len(self.values) and self.values[left] == x:
            return False  # Already exists
        
        self.values.insert(left, x)
        self.cardinality += 1
        return True
    
    def remove(self, x: int) -> bool:
        """Remove value if present."""
        left, right = 0, len(self.values)
        while left < right:
            mid = (left + right) // 2
            if self.values[mid] < x:
                left = mid + 1
            else:
                right = mid
        
        if left < len(self.values) and self.values[left] == x:
            self.values.pop(left)
            self.cardinality -= 1
            return True
        
        return False
    
    def to_array(self) -> List[int]:
        """Return copy of values array."""
        return self.values.copy()
    
    def should_convert_to_bitmap(self) -> bool:
        """Check if should convert to bitmap container."""
        return self.cardinality >= 4096


class BitmapContainer(Container):
    """Bitmap container for dense sets (>= 4096 elements)."""
    
    def __init__(self):
        super().__init__()
        self.bitmap = bytearray(8192)  # 65536 bits = 8192 bytes
    
    def contains(self, x: int) -> bool:
        """Check bit at position x."""
        byte_index = x // 8
        bit_offset = x % 8
        return bool(self.bitmap[byte_index] & (1 << bit_offset))
    
    def add(self, x: int) -> bool:
        """Set bit at position x."""
        byte_index = x // 8
        bit_offset = x % 8
        
        if self.bitmap[byte_index] & (1 << bit_offset):
            return False  # Already set
        
        self.bitmap[byte_index] |= (1 << bit_offset)
        self.cardinality += 1
        return True
    
    def remove(self, x: int) -> bool:
        """Clear bit at position x."""
        byte_index = x // 8
        bit_offset = x % 8
        
        if not (self.bitmap[byte_index] & (1 << bit_offset)):
            return False  # Not set
        
        self.bitmap[byte_index] &= ~(1 << bit_offset)
        self.cardinality -= 1
        return True
    
    def to_array(self) -> List[int]:
        """Convert bitmap to array of set values."""
        result = []
        for byte_index in range(len(self.bitmap)):
            byte_value = self.bitmap[byte_index]
            if byte_value != 0:
                for bit_offset in range(8):
                    if byte_value & (1 << bit_offset):
                        result.append(byte_index * 8 + bit_offset)
        return result
    
    def should_convert_to_array(self) -> bool:
        """Check if should convert to array container."""
        return self.cardinality < 4096


class RoaringBitmapStrategy(ANodeMatrixStrategy):
    """
    Roaring Bitmap node strategy for compressed sparse sets.
    
    Uses a hybrid approach with array containers for sparse data
    and bitmap containers for dense data, providing excellent
    compression and performance characteristics.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Roaring Bitmap strategy."""
        super().__init__(NodeMode.ROARING_BITMAP, traits, **options)
        
        # Roaring bitmap structure: high 16 bits -> container
        self._containers: Dict[int, Container] = {}  # high_bits -> container
        self._size = 0
        
        # Key-value mapping for compatibility
        self._key_to_value: Dict[str, int] = {}  # key -> 32-bit value
        self._value_to_key: Dict[int, str] = {}  # value -> key
        self._values: Dict[str, Any] = {}  # Associated data
        self._next_value = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the roaring bitmap strategy."""
        return (NodeTrait.COMPRESSED | NodeTrait.INDEXED | NodeTrait.STREAMING | NodeTrait.SPATIAL)
    
    def _split_value(self, value: int) -> Tuple[int, int]:
        """Split 32-bit value into high 16 bits and low 16 bits."""
        high = (value >> 16) & 0xFFFF
        low = value & 0xFFFF
        return high, low
    
    def _get_or_create_container(self, high: int) -> Container:
        """Get or create container for high bits."""
        if high not in self._containers:
            self._containers[high] = ArrayContainer()
        return self._containers[high]
    
    def _maybe_convert_container(self, high: int) -> None:
        """Convert container type if needed for efficiency."""
        if high not in self._containers:
            return
        
        container = self._containers[high]
        
        if isinstance(container, ArrayContainer) and container.should_convert_to_bitmap():
            # Convert to bitmap container
            new_container = BitmapContainer()
            for value in container.to_array():
                new_container.add(value)
            self._containers[high] = new_container
        
        elif isinstance(container, BitmapContainer) and container.should_convert_to_array():
            # Convert to array container
            new_container = ArrayContainer()
            for value in container.to_array():
                new_container.add(value)
            self._containers[high] = new_container
    
    def _add_value(self, value: int) -> bool:
        """Add a 32-bit value to the roaring bitmap."""
        high, low = self._split_value(value)
        container = self._get_or_create_container(high)
        
        was_new = container.add(low)
        if was_new:
            self._size += 1
            self._maybe_convert_container(high)
        
        return was_new
    
    def _remove_value(self, value: int) -> bool:
        """Remove a 32-bit value from the roaring bitmap."""
        high, low = self._split_value(value)
        
        if high not in self._containers:
            return False
        
        container = self._containers[high]
        was_removed = container.remove(low)
        
        if was_removed:
            self._size -= 1
            
            # Remove empty containers
            if container.cardinality == 0:
                del self._containers[high]
            else:
                self._maybe_convert_container(high)
        
        return was_removed
    
    def _contains_value(self, value: int) -> bool:
        """Check if 32-bit value is in the roaring bitmap."""
        high, low = self._split_value(value)
        
        if high not in self._containers:
            return False
        
        return self._containers[high].contains(low)
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add key to the roaring bitmap."""
        key_str = str(key)
        
        # Get or assign 32-bit value for this key
        if key_str in self._key_to_value:
            bit_value = self._key_to_value[key_str]
        else:
            # Try to parse key as integer
            try:
                bit_value = int(key_str)
                if bit_value < 0 or bit_value > 0xFFFFFFFF:
                    bit_value = self._next_value
                    self._next_value += 1
            except ValueError:
                bit_value = self._next_value
                self._next_value += 1
            
            self._key_to_value[key_str] = bit_value
            self._value_to_key[bit_value] = key_str
        
        # Add to roaring bitmap if value is truthy
        should_add = value is not None and value is not False
        
        if should_add:
            self._add_value(bit_value)
            self._values[key_str] = value if value is not None else True
        else:
            self._remove_value(bit_value)
            self._values.pop(key_str, None)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value associated with key."""
        key_str = str(key)
        
        if key_str in self._key_to_value:
            bit_value = self._key_to_value[key_str]
            if self._contains_value(bit_value):
                return self._values.get(key_str, True)
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key is in the roaring bitmap."""
        key_str = str(key)
        
        if key_str in self._key_to_value:
            bit_value = self._key_to_value[key_str]
            return self._contains_value(bit_value)
        
        return False
    
    def remove(self, key: Any) -> bool:
        """Remove key from the roaring bitmap."""
        key_str = str(key)
        
        if key_str in self._key_to_value:
            bit_value = self._key_to_value[key_str]
            was_removed = self._remove_value(bit_value)
            
            if was_removed:
                self._values.pop(key_str, None)
                return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key from the roaring bitmap (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._containers.clear()
        self._size = 0
        self._values.clear()
        # Keep key mappings for consistency
    
    def keys(self) -> Iterator[str]:
        """Get all keys with set bits."""
        for key_str, bit_value in self._key_to_value.items():
            if self._contains_value(bit_value):
                yield key_str
    
    def values(self) -> Iterator[Any]:
        """Get all values for set bits."""
        return iter(self._values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs for set bits."""
        for key_str, bit_value in self._key_to_value.items():
            if self._contains_value(bit_value):
                yield (key_str, self._values.get(key_str, True))
    
    def __len__(self) -> int:
        """Get the number of set bits."""
        return self._size
    
    def to_native(self) -> Dict[str, bool]:
        """Convert to native Python dict of boolean values."""
        result = {}
        for key_str, bit_value in self._key_to_value.items():
            result[key_str] = self._contains_value(bit_value)
        return result
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for indexed access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This can behave like a dict."""
        return True
    
    # ============================================================================
    # ROARING BITMAP SPECIFIC OPERATIONS
    # ============================================================================
    
    def add_range(self, start: int, end: int) -> int:
        """Add range of values [start, end). Returns number of new values."""
        added_count = 0
        for value in range(start, end):
            if self._add_value(value):
                added_count += 1
        return added_count
    
    def remove_range(self, start: int, end: int) -> int:
        """Remove range of values [start, end). Returns number of removed values."""
        removed_count = 0
        for value in range(start, end):
            if self._remove_value(value):
                removed_count += 1
        return removed_count
    
    def union(self, other: 'xRoaringBitmapStrategy') -> 'xRoaringBitmapStrategy':
        """Union with another roaring bitmap."""
        result = xRoaringBitmapStrategy(traits=self._traits)
        
        # Union all containers
        all_highs = set(self._containers.keys()) | set(other._containers.keys())
        
        for high in all_highs:
            result_values = set()
            
            if high in self._containers:
                result_values.update(self._containers[high].to_array())
            
            if high in other._containers:
                result_values.update(other._containers[high].to_array())
            
            # Add all values to result
            for low in result_values:
                value = (high << 16) | low
                result._add_value(value)
        
        return result
    
    def intersection(self, other: 'xRoaringBitmapStrategy') -> 'xRoaringBitmapStrategy':
        """Intersection with another roaring bitmap."""
        result = xRoaringBitmapStrategy(traits=self._traits)
        
        # Intersect only common containers
        common_highs = set(self._containers.keys()) & set(other._containers.keys())
        
        for high in common_highs:
            self_values = set(self._containers[high].to_array())
            other_values = set(other._containers[high].to_array())
            common_values = self_values & other_values
            
            # Add common values to result
            for low in common_values:
                value = (high << 16) | low
                result._add_value(value)
        
        return result
    
    def difference(self, other: 'xRoaringBitmapStrategy') -> 'xRoaringBitmapStrategy':
        """Difference with another roaring bitmap."""
        result = xRoaringBitmapStrategy(traits=self._traits)
        
        for high, container in self._containers.items():
            self_values = set(container.to_array())
            
            if high in other._containers:
                other_values = set(other._containers[high].to_array())
                diff_values = self_values - other_values
            else:
                diff_values = self_values
            
            # Add difference values to result
            for low in diff_values:
                value = (high << 16) | low
                result._add_value(value)
        
        return result
    
    def to_array(self) -> List[int]:
        """Convert to sorted array of all values."""
        result = []
        
        for high in sorted(self._containers.keys()):
            container = self._containers[high]
            for low in container.to_array():
                value = (high << 16) | low
                result.append(value)
        
        return result
    
    def rank(self, value: int) -> int:
        """Get rank of value (number of values <= value)."""
        rank = 0
        high, low = self._split_value(value)
        
        # Count all values in containers with smaller high bits
        for container_high in sorted(self._containers.keys()):
            if container_high < high:
                rank += self._containers[container_high].cardinality
            elif container_high == high:
                # Count values in this container <= low
                container = self._containers[container_high]
                for container_low in container.to_array():
                    if container_low <= low:
                        rank += 1
                break
        
        return rank
    
    def select(self, rank: int) -> Optional[int]:
        """Get value at rank (0-indexed)."""
        if rank < 0 or rank >= self._size:
            return None
        
        current_rank = 0
        
        for high in sorted(self._containers.keys()):
            container = self._containers[high]
            if current_rank + container.cardinality > rank:
                # Value is in this container
                container_rank = rank - current_rank
                container_values = container.to_array()
                low = container_values[container_rank]
                return (high << 16) | low
            
            current_rank += container.cardinality
        
        return None
    
    def get_compression_ratio(self) -> float:
        """Get compression ratio compared to uncompressed bitmap."""
        if self._size == 0:
            return 1.0
        
        # Estimate memory usage
        memory_used = 0
        for container in self._containers.values():
            if isinstance(container, ArrayContainer):
                memory_used += len(container.values) * 2  # 2 bytes per value
            else:  # BitmapContainer
                memory_used += 8192  # Fixed 8KB
        
        # Uncompressed would need 4 bytes per value
        uncompressed_size = self._size * 4
        
        return memory_used / max(1, uncompressed_size)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        array_containers = sum(1 for c in self._containers.values() 
                              if isinstance(c, ArrayContainer))
        bitmap_containers = len(self._containers) - array_containers
        
        return {
            'strategy': 'ROARING_BITMAP',
            'backend': 'Hybrid Array/Bitmap containers',
            'total_containers': len(self._containers),
            'array_containers': array_containers,
            'bitmap_containers': bitmap_containers,
            'complexity': {
                'add': 'O(log n) for arrays, O(1) for bitmaps',
                'remove': 'O(log n) for arrays, O(1) for bitmaps',
                'contains': 'O(log n) for arrays, O(1) for bitmaps',
                'union': 'O(n + m)',
                'intersection': 'O(min(n, m))',
                'space': 'O(n) compressed'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        compression_ratio = self.get_compression_ratio()
        
        # Estimate memory usage
        memory_used = 0
        for container in self._containers.values():
            if isinstance(container, ArrayContainer):
                memory_used += len(container.values) * 2 + 24  # Values + overhead
            else:
                memory_used += 8192 + 24  # Bitmap + overhead
        
        return {
            'set_bits': self._size,
            'containers': len(self._containers),
            'compression_ratio': f"{compression_ratio:.3f}",
            'memory_usage': f"{memory_used} bytes (estimated)",
            'memory_per_bit': f"{memory_used / max(1, self._size):.1f} bytes/bit",
            'sparsity': f"{(1 - (self._size / max(1, self._next_value))) * 100:.1f}%"
        }
