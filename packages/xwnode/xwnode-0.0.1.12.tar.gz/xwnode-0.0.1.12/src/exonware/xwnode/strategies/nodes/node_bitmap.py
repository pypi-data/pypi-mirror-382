"""
Bitmap Node Strategy Implementation

This module implements the BITMAP strategy for efficient bit manipulation
and boolean operations with compressed storage.
"""

from typing import Any, Iterator, List, Dict, Optional, Union
import array
from .base import ANodeMatrixStrategy
from ...types import NodeMode, NodeTrait


class BitmapStrategy(ANodeMatrixStrategy):
    """
    Bitmap node strategy for efficient bit manipulation and boolean operations.
    
    Provides space-efficient storage for boolean flags and supports
    fast bitwise operations with compressed representation.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Bitmap strategy."""
        super().__init__(NodeMode.BITMAP, traits, **options)
        
        self.initial_size = options.get('initial_size', 1024)
        self.auto_resize = options.get('auto_resize', True)
        self.compression_threshold = options.get('compression_threshold', 0.1)  # 10% fill rate
        
        # Core storage using Python array for efficiency
        self._bits = array.array('B')  # Byte array for bit storage
        self._capacity_bits = 0
        self._size = 0  # Number of set bits
        self._max_index = -1  # Highest index with a bit set
        
        # Key-value mapping for compatibility
        self._key_to_index: Dict[str, int] = {}
        self._index_to_key: Dict[int, str] = {}
        self._values: Dict[str, Any] = {}  # Associated values
        self._next_index = 0
        
        # Initialize with initial capacity
        self._resize_to(self.initial_size)
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the bitmap strategy."""
        return (NodeTrait.COMPRESSED | NodeTrait.INDEXED | NodeTrait.STREAMING)
    
    def _resize_to(self, new_bit_capacity: int) -> None:
        """Resize bitmap to new bit capacity."""
        new_byte_capacity = (new_bit_capacity + 7) // 8  # Round up to nearest byte
        
        if new_byte_capacity > len(self._bits):
            # Expand
            self._bits.extend([0] * (new_byte_capacity - len(self._bits)))
        elif new_byte_capacity < len(self._bits):
            # Shrink
            self._bits = self._bits[:new_byte_capacity]
        
        self._capacity_bits = new_bit_capacity
    
    def _ensure_capacity(self, bit_index: int) -> None:
        """Ensure bitmap has capacity for the given bit index."""
        if bit_index >= self._capacity_bits:
            if self.auto_resize:
                new_capacity = max(bit_index + 1, self._capacity_bits * 2)
                self._resize_to(new_capacity)
            else:
                raise IndexError(f"Bit index {bit_index} exceeds capacity {self._capacity_bits}")
    
    def _get_bit(self, bit_index: int) -> bool:
        """Get bit value at index."""
        if bit_index >= self._capacity_bits or bit_index < 0:
            return False
        
        byte_index = bit_index // 8
        bit_offset = bit_index % 8
        
        if byte_index >= len(self._bits):
            return False
        
        return bool(self._bits[byte_index] & (1 << bit_offset))
    
    def _set_bit(self, bit_index: int, value: bool) -> bool:
        """Set bit value at index. Returns True if bit was changed."""
        self._ensure_capacity(bit_index)
        
        byte_index = bit_index // 8
        bit_offset = bit_index % 8
        
        old_value = bool(self._bits[byte_index] & (1 << bit_offset))
        
        if value:
            self._bits[byte_index] |= (1 << bit_offset)
            if not old_value:
                self._size += 1
                self._max_index = max(self._max_index, bit_index)
        else:
            self._bits[byte_index] &= ~(1 << bit_offset)
            if old_value:
                self._size -= 1
                if bit_index == self._max_index:
                    self._update_max_index()
        
        return old_value != value
    
    def _update_max_index(self) -> None:
        """Update the maximum set bit index."""
        self._max_index = -1
        for i in range(self._capacity_bits - 1, -1, -1):
            if self._get_bit(i):
                self._max_index = i
                break
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Set a bit and associate a value."""
        key_str = str(key)
        
        # Get or assign bit index for this key
        if key_str in self._key_to_index:
            bit_index = self._key_to_index[key_str]
        else:
            # Try to parse key as integer index
            try:
                bit_index = int(key_str)
                if bit_index < 0:
                    bit_index = self._next_index
                    self._next_index += 1
            except ValueError:
                bit_index = self._next_index
                self._next_index += 1
            
            self._key_to_index[key_str] = bit_index
            self._index_to_key[bit_index] = key_str
        
        # Set the bit (treat None as False, everything else as True)
        bit_value = value is not None and value is not False
        self._set_bit(bit_index, bit_value)
        
        # Store associated value
        if bit_value:
            self._values[key_str] = value if value is not None else True
        else:
            self._values.pop(key_str, None)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value associated with key."""
        key_str = str(key)
        
        if key_str in self._key_to_index:
            bit_index = self._key_to_index[key_str]
            if self._get_bit(bit_index):
                return self._values.get(key_str, True)
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if bit is set for key."""
        key_str = str(key)
        
        if key_str in self._key_to_index:
            bit_index = self._key_to_index[key_str]
            return self._get_bit(bit_index)
        
        return False
    
    def remove(self, key: Any) -> bool:
        """Clear bit for key."""
        key_str = str(key)
        
        if key_str in self._key_to_index:
            bit_index = self._key_to_index[key_str]
            was_set = self._get_bit(bit_index)
            
            if was_set:
                self._set_bit(bit_index, False)
                self._values.pop(key_str, None)
                return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Clear bit for key (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all bits."""
        self._bits = array.array('B', [0] * len(self._bits))
        self._size = 0
        self._max_index = -1
        self._values.clear()
        # Keep key mappings for consistency
    
    def keys(self) -> Iterator[str]:
        """Get all keys with set bits."""
        for key_str, bit_index in self._key_to_index.items():
            if self._get_bit(bit_index):
                yield key_str
    
    def values(self) -> Iterator[Any]:
        """Get all values for set bits."""
        return iter(self._values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs for set bits."""
        for key_str, bit_index in self._key_to_index.items():
            if self._get_bit(bit_index):
                yield (key_str, self._values.get(key_str, True))
    
    def __len__(self) -> int:
        """Get the number of set bits."""
        return self._size
    
    def to_native(self) -> Dict[str, bool]:
        """Convert to native Python dict of boolean values."""
        result = {}
        for key_str, bit_index in self._key_to_index.items():
            result[key_str] = self._get_bit(bit_index)
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
    # BITMAP-SPECIFIC OPERATIONS
    # ============================================================================
    
    def set_bit(self, index: int, value: bool = True) -> bool:
        """Set bit at index. Returns previous value."""
        old_value = self._get_bit(index)
        self._set_bit(index, value)
        return old_value
    
    def get_bit(self, index: int) -> bool:
        """Get bit value at index."""
        return self._get_bit(index)
    
    def flip_bit(self, index: int) -> bool:
        """Flip bit at index. Returns new value."""
        current_value = self._get_bit(index)
        new_value = not current_value
        self._set_bit(index, new_value)
        return new_value
    
    def count_set_bits(self, start: int = 0, end: Optional[int] = None) -> int:
        """Count set bits in range [start, end)."""
        if end is None:
            end = self._capacity_bits
        
        count = 0
        for i in range(start, min(end, self._capacity_bits)):
            if self._get_bit(i):
                count += 1
        
        return count
    
    def find_first_set(self, start: int = 0) -> Optional[int]:
        """Find first set bit starting from index."""
        for i in range(start, self._capacity_bits):
            if self._get_bit(i):
                return i
        return None
    
    def find_first_clear(self, start: int = 0) -> Optional[int]:
        """Find first clear bit starting from index."""
        for i in range(start, self._capacity_bits):
            if not self._get_bit(i):
                return i
        return None
    
    def bitwise_and(self, other: 'xBitmapStrategy') -> 'xBitmapStrategy':
        """Bitwise AND with another bitmap."""
        result = xBitmapStrategy(
            traits=self._traits,
            initial_size=max(self._capacity_bits, other._capacity_bits)
        )
        
        max_bits = min(self._capacity_bits, other._capacity_bits)
        for i in range(max_bits):
            if self._get_bit(i) and other._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def bitwise_or(self, other: 'xBitmapStrategy') -> 'xBitmapStrategy':
        """Bitwise OR with another bitmap."""
        result = xBitmapStrategy(
            traits=self._traits,
            initial_size=max(self._capacity_bits, other._capacity_bits)
        )
        
        max_bits = max(self._capacity_bits, other._capacity_bits)
        for i in range(max_bits):
            if self._get_bit(i) or other._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def bitwise_xor(self, other: 'xBitmapStrategy') -> 'xBitmapStrategy':
        """Bitwise XOR with another bitmap."""
        result = xBitmapStrategy(
            traits=self._traits,
            initial_size=max(self._capacity_bits, other._capacity_bits)
        )
        
        max_bits = max(self._capacity_bits, other._capacity_bits)
        for i in range(max_bits):
            if self._get_bit(i) != other._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def bitwise_not(self) -> 'xBitmapStrategy':
        """Bitwise NOT (invert all bits)."""
        result = xBitmapStrategy(
            traits=self._traits,
            initial_size=self._capacity_bits
        )
        
        for i in range(self._capacity_bits):
            if not self._get_bit(i):
                result._set_bit(i, True)
        
        return result
    
    def compress(self) -> None:
        """Compress bitmap by removing trailing zero bytes."""
        if self._max_index < 0:
            # No bits set, minimize to 1 byte
            self._resize_to(8)
            return
        
        # Resize to just fit the highest set bit
        new_capacity = ((self._max_index + 8) // 8) * 8
        self._resize_to(new_capacity)
    
    def get_compression_ratio(self) -> float:
        """Get compression ratio (set bits / total capacity)."""
        if self._capacity_bits == 0:
            return 0.0
        return self._size / self._capacity_bits
    
    def to_bytes(self) -> bytes:
        """Export bitmap as bytes."""
        return self._bits.tobytes()
    
    def from_bytes(self, data: bytes) -> None:
        """Import bitmap from bytes."""
        self._bits = array.array('B', data)
        self._capacity_bits = len(self._bits) * 8
        
        # Recalculate size and max_index
        self._size = 0
        self._max_index = -1
        
        for i in range(self._capacity_bits):
            if self._get_bit(i):
                self._size += 1
                self._max_index = i
    
    def get_bit_pattern(self, start: int = 0, length: int = 64) -> str:
        """Get bit pattern as string for debugging."""
        pattern = ""
        end = min(start + length, self._capacity_bits)
        
        for i in range(start, end):
            pattern += "1" if self._get_bit(i) else "0"
            if (i - start + 1) % 8 == 0 and i < end - 1:
                pattern += " "  # Byte separator
        
        return pattern
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'BITMAP',
            'backend': 'Python array (byte-based)',
            'capacity_bits': self._capacity_bits,
            'capacity_bytes': len(self._bits),
            'auto_resize': self.auto_resize,
            'complexity': {
                'set_bit': 'O(1)',
                'get_bit': 'O(1)',
                'count_bits': 'O(n)',
                'bitwise_ops': 'O(n)',
                'space': 'O(n/8) bytes'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        compression_ratio = self.get_compression_ratio()
        memory_efficiency = (self._size * 8) / max(1, len(self._bits)) * 100
        
        return {
            'set_bits': self._size,
            'total_capacity_bits': self._capacity_bits,
            'capacity_bytes': len(self._bits),
            'max_set_index': self._max_index,
            'compression_ratio': f"{compression_ratio:.3f}",
            'memory_efficiency': f"{memory_efficiency:.1f}%",
            'memory_usage': f"{len(self._bits)} bytes (bits) + {len(self._values) * 24} bytes (values)"
        }
