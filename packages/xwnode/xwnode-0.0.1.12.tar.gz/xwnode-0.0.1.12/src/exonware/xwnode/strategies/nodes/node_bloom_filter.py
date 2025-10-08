"""
Bloom Filter Node Strategy Implementation

This module implements the BLOOM_FILTER strategy for memory-efficient
probabilistic membership testing with no false negatives.
"""

from typing import Any, Iterator, List, Dict, Optional
import hashlib
import math
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class xBloomFilterStrategy(aNodeStrategy):
    """
    Bloom Filter node strategy for probabilistic membership testing.
    
    Provides memory-efficient approximate membership testing with:
    - No false negatives (if it says "no", it's definitely not there)
    - Possible false positives (if it says "yes", it might be there)
    - Configurable false positive rate
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Bloom Filter strategy."""
        super().__init__(NodeMode.BLOOM_FILTER, traits, **options)
        
        # Bloom filter parameters
        self.expected_elements = options.get('expected_elements', 1000)
        self.false_positive_rate = options.get('false_positive_rate', 0.01)
        
        # Calculate optimal parameters
        self.bit_array_size = self._calculate_bit_array_size()
        self.num_hash_functions = self._calculate_num_hash_functions()
        
        # Core storage
        self._bit_array = [0] * self.bit_array_size
        self._values: Dict[str, Any] = {}  # Store actual values for retrieval
        self._size = 0
        self._insertions = 0
        
        # Hash functions
        self._hash_seeds = self._generate_hash_seeds()
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the bloom filter strategy."""
        return (NodeTrait.PROBABILISTIC | NodeTrait.COMPRESSED | NodeTrait.STREAMING)
    
    def _calculate_bit_array_size(self) -> int:
        """Calculate optimal bit array size."""
        # m = -(n * ln(p)) / (ln(2)^2)
        # where n = expected elements, p = false positive rate
        n = self.expected_elements
        p = self.false_positive_rate
        
        if p <= 0 or p >= 1:
            p = 0.01  # Default to 1% false positive rate
        
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return max(1, int(math.ceil(m)))
    
    def _calculate_num_hash_functions(self) -> int:
        """Calculate optimal number of hash functions."""
        # k = (m / n) * ln(2)
        # where m = bit array size, n = expected elements
        m = self.bit_array_size
        n = self.expected_elements
        
        k = (m / n) * math.log(2)
        return max(1, int(round(k)))
    
    def _generate_hash_seeds(self) -> List[int]:
        """Generate seeds for multiple hash functions."""
        seeds = []
        for i in range(self.num_hash_functions):
            # Use different primes as seeds
            seed = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47][i % 15]
            seeds.append(seed * (i + 1))
        return seeds
    
    def _hash_element(self, element: str, seed: int) -> int:
        """Hash an element with a given seed."""
        hash_obj = hashlib.md5(f"{element}{seed}".encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % self.bit_array_size
    
    def _get_bit_positions(self, element: str) -> List[int]:
        """Get all bit positions for an element."""
        positions = []
        for seed in self._hash_seeds:
            pos = self._hash_element(element, seed)
            positions.append(pos)
        return positions
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add an element to the bloom filter."""
        element = str(key)
        
        # Set bits for this element
        positions = self._get_bit_positions(element)
        for pos in positions:
            self._bit_array[pos] = 1
        
        # Store actual value for retrieval (optional)
        was_new = element not in self._values
        self._values[element] = value if value is not None else key
        
        if was_new:
            self._size += 1
        
        self._insertions += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value if definitely present (may have false positives)."""
        element = str(key)
        
        # Check if element might be present
        if self.has(element):
            return self._values.get(element, default)
        else:
            # Definitely not present
            return default
    
    def has(self, key: Any) -> bool:
        """Check if element might be present (probabilistic)."""
        element = str(key)
        
        # Check all bit positions
        positions = self._get_bit_positions(element)
        for pos in positions:
            if self._bit_array[pos] == 0:
                # Definitely not present
                return False
        
        # Might be present (could be false positive)
        return True
    
    def remove(self, key: Any) -> bool:
        """Remove from stored values (cannot remove from bloom filter)."""
        element = str(key)
        
        if element in self._values:
            del self._values[element]
            self._size -= 1
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove from stored values (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._bit_array = [0] * self.bit_array_size
        self._values.clear()
        self._size = 0
        self._insertions = 0
    
    def keys(self) -> Iterator[str]:
        """Get all stored keys (not all elements in filter)."""
        return iter(self._values.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all stored values."""
        return iter(self._values.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all stored key-value pairs."""
        return iter(self._values.items())
    
    def __len__(self) -> int:
        """Get the number of stored elements."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict of stored values."""
        return dict(self._values)
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict but with probabilistic semantics."""
        return True
    
    # ============================================================================
    # BLOOM FILTER SPECIFIC OPERATIONS
    # ============================================================================
    
    def add(self, element: Any) -> None:
        """Add an element to the bloom filter."""
        self.put(element, element)
    
    def might_contain(self, element: Any) -> bool:
        """Check if element might be in the filter (same as has)."""
        return self.has(element)
    
    def definitely_not_contains(self, element: Any) -> bool:
        """Check if element is definitely not in the filter."""
        return not self.has(element)
    
    def get_false_positive_probability(self) -> float:
        """Calculate current false positive probability."""
        if self._insertions == 0:
            return 0.0
        
        # p = (1 - e^(-k*n/m))^k
        # where k = num hash functions, n = insertions, m = bit array size
        k = self.num_hash_functions
        n = self._insertions
        m = self.bit_array_size
        
        if m == 0:
            return 1.0
        
        exponent = -(k * n) / m
        try:
            probability = (1 - math.exp(exponent)) ** k
            return min(1.0, max(0.0, probability))
        except (OverflowError, ValueError):
            return 1.0
    
    def get_capacity_utilization(self) -> float:
        """Get the utilization of the bit array capacity."""
        bits_set = sum(self._bit_array)
        return bits_set / self.bit_array_size if self.bit_array_size > 0 else 0.0
    
    def union(self, other: 'xBloomFilterStrategy') -> 'xBloomFilterStrategy':
        """Create union of two bloom filters (must have same parameters)."""
        if (self.bit_array_size != other.bit_array_size or 
            self.num_hash_functions != other.num_hash_functions):
            raise ValueError("Bloom filters must have same parameters for union")
        
        result = xBloomFilterStrategy(
            traits=self._traits,
            expected_elements=max(self.expected_elements, other.expected_elements),
            false_positive_rate=max(self.false_positive_rate, other.false_positive_rate)
        )
        
        # OR the bit arrays
        for i in range(self.bit_array_size):
            result._bit_array[i] = self._bit_array[i] | other._bit_array[i]
        
        # Combine stored values
        result._values.update(self._values)
        result._values.update(other._values)
        result._size = len(result._values)
        result._insertions = self._insertions + other._insertions
        
        return result
    
    def intersection_estimate(self, other: 'xBloomFilterStrategy') -> float:
        """Estimate intersection size (approximate)."""
        if (self.bit_array_size != other.bit_array_size or 
            self.num_hash_functions != other.num_hash_functions):
            raise ValueError("Bloom filters must have same parameters for intersection")
        
        # Count bits set in both filters
        intersection_bits = sum(1 for i in range(self.bit_array_size) 
                              if self._bit_array[i] == 1 and other._bit_array[i] == 1)
        
        # Rough estimation (not mathematically precise)
        if intersection_bits == 0:
            return 0.0
        
        # Simple heuristic: intersection bits relative to total bits
        total_bits_set = sum(self._bit_array) + sum(other._bit_array)
        if total_bits_set == 0:
            return 0.0
        
        estimated_ratio = intersection_bits / (total_bits_set / 2)
        estimated_size = estimated_ratio * min(self._insertions, other._insertions)
        return max(0.0, estimated_size)
    
    def export_bit_array(self) -> List[int]:
        """Export the bit array for analysis or storage."""
        return self._bit_array.copy()
    
    def import_bit_array(self, bit_array: List[int]) -> None:
        """Import a bit array (must match current size)."""
        if len(bit_array) != self.bit_array_size:
            raise ValueError(f"Bit array size mismatch: expected {self.bit_array_size}, got {len(bit_array)}")
        
        self._bit_array = [int(bit) for bit in bit_array]
    
    def optimize_for_insertions(self, actual_insertions: int) -> 'xBloomFilterStrategy':
        """Create an optimized bloom filter based on actual insertion count."""
        optimized = xBloomFilterStrategy(
            traits=self._traits,
            expected_elements=actual_insertions,
            false_positive_rate=self.false_positive_rate
        )
        
        # Re-insert all stored values
        for key, value in self._values.items():
            optimized.put(key, value)
        
        return optimized
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'BLOOM_FILTER',
            'backend': 'Probabilistic bit array',
            'bit_array_size': self.bit_array_size,
            'num_hash_functions': self.num_hash_functions,
            'expected_elements': self.expected_elements,
            'target_false_positive_rate': self.false_positive_rate,
            'complexity': {
                'add': 'O(k)',
                'contains': 'O(k)',
                'space': 'O(m)',
                'false_negatives': '0%',
                'false_positives': f'{self.false_positive_rate * 100:.2f}% target'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        current_fp_rate = self.get_false_positive_probability()
        capacity_util = self.get_capacity_utilization()
        
        return {
            'stored_elements': self._size,
            'total_insertions': self._insertions,
            'bit_array_size': self.bit_array_size,
            'bits_set': sum(self._bit_array),
            'capacity_utilization': f"{capacity_util * 100:.1f}%",
            'current_false_positive_rate': f"{current_fp_rate * 100:.2f}%",
            'target_false_positive_rate': f"{self.false_positive_rate * 100:.2f}%",
            'memory_usage': f"{self.bit_array_size // 8} bytes (bit array)"
        }
