"""
Cuckoo Hash Node Strategy Implementation

This module implements the CUCKOO_HASH strategy for guaranteed O(1)
worst-case lookup time with efficient space utilization.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
import hashlib
import random
from ._base_node import aNodeStrategy
from ...types import NodeMode, NodeTrait


class xCuckooHashStrategy(aNodeStrategy):
    """
    Cuckoo Hash node strategy for guaranteed O(1) worst-case lookups.
    
    Uses cuckoo hashing with two hash tables and eviction-based insertion
    to guarantee constant-time operations in the worst case.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Cuckoo Hash strategy."""
        super().__init__(NodeMode.CUCKOO_HASH, traits, **options)
        
        # Cuckoo hash parameters
        self.initial_capacity = options.get('initial_capacity', 16)
        self.load_factor = options.get('load_factor', 0.5)  # Lower for cuckoo hashing
        self.max_evictions = options.get('max_evictions', 8)
        
        # Two hash tables
        self.capacity = self.initial_capacity
        self._table1: List[Optional[Tuple[str, Any]]] = [None] * self.capacity
        self._table2: List[Optional[Tuple[str, Any]]] = [None] * self.capacity
        
        # Hash function parameters
        self._hash1_a = random.randint(1, 1000000)
        self._hash1_b = random.randint(0, 1000000)
        self._hash2_a = random.randint(1, 1000000)
        self._hash2_b = random.randint(0, 1000000)
        self._prime = 1000003  # Large prime for hash functions
        
        self._size = 0
        self._resize_threshold = int(self.capacity * self.load_factor)
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the cuckoo hash strategy."""
        return (NodeTrait.INDEXED | NodeTrait.HIERARCHICAL)
    
    def _hash1(self, key: str) -> int:
        """First hash function."""
        key_hash = hash(key)
        return ((self._hash1_a * key_hash + self._hash1_b) % self._prime) % self.capacity
    
    def _hash2(self, key: str) -> int:
        """Second hash function."""
        key_hash = hash(key)
        return ((self._hash2_a * key_hash + self._hash2_b) % self._prime) % self.capacity
    
    def _resize(self) -> None:
        """Resize the hash tables when load factor is exceeded."""
        old_table1 = self._table1
        old_table2 = self._table2
        old_capacity = self.capacity
        
        # Double the capacity
        self.capacity = old_capacity * 2
        self._table1 = [None] * self.capacity
        self._table2 = [None] * self.capacity
        self._resize_threshold = int(self.capacity * self.load_factor)
        
        # Regenerate hash function parameters
        self._hash1_a = random.randint(1, 1000000)
        self._hash1_b = random.randint(0, 1000000)
        self._hash2_a = random.randint(1, 1000000)
        self._hash2_b = random.randint(0, 1000000)
        
        # Reinsert all elements
        old_size = self._size
        self._size = 0
        
        for table in [old_table1, old_table2]:
            for entry in table:
                if entry is not None:
                    key, value = entry
                    self._insert_internal(key, value)
    
    def _insert_internal(self, key: str, value: Any) -> bool:
        """Internal insertion with cuckoo eviction."""
        # Try table 1 first
        pos1 = self._hash1(key)
        if self._table1[pos1] is None:
            self._table1[pos1] = (key, value)
            self._size += 1
            return True
        
        # Try table 2
        pos2 = self._hash2(key)
        if self._table2[pos2] is None:
            self._table2[pos2] = (key, value)
            self._size += 1
            return True
        
        # Both positions occupied, start cuckoo eviction
        current_key, current_value = key, value
        current_table = 1  # Start with table 1
        
        for _ in range(self.max_evictions):
            if current_table == 1:
                pos = self._hash1(current_key)
                if self._table1[pos] is None:
                    self._table1[pos] = (current_key, current_value)
                    self._size += 1
                    return True
                
                # Evict existing element
                evicted_key, evicted_value = self._table1[pos]
                self._table1[pos] = (current_key, current_value)
                current_key, current_value = evicted_key, evicted_value
                current_table = 2
            else:
                pos = self._hash2(current_key)
                if self._table2[pos] is None:
                    self._table2[pos] = (current_key, current_value)
                    self._size += 1
                    return True
                
                # Evict existing element
                evicted_key, evicted_value = self._table2[pos]
                self._table2[pos] = (current_key, current_value)
                current_key, current_value = evicted_key, evicted_value
                current_table = 1
        
        # Failed to insert after max evictions, need to resize
        return False
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Store a key-value pair."""
        key_str = str(key)
        
        # Check if key already exists
        if self.has(key_str):
            # Update existing
            pos1 = self._hash1(key_str)
            if self._table1[pos1] is not None and self._table1[pos1][0] == key_str:
                self._table1[pos1] = (key_str, value)
                return
            
            pos2 = self._hash2(key_str)
            if self._table2[pos2] is not None and self._table2[pos2][0] == key_str:
                self._table2[pos2] = (key_str, value)
                return
        
        # Check if resize is needed
        if self._size >= self._resize_threshold:
            self._resize()
        
        # Try to insert
        while not self._insert_internal(key_str, value):
            # Insertion failed, resize and try again
            self._resize()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve a value by key (guaranteed O(1))."""
        key_str = str(key)
        
        # Check table 1
        pos1 = self._hash1(key_str)
        if self._table1[pos1] is not None and self._table1[pos1][0] == key_str:
            return self._table1[pos1][1]
        
        # Check table 2
        pos2 = self._hash2(key_str)
        if self._table2[pos2] is not None and self._table2[pos2][0] == key_str:
            return self._table2[pos2][1]
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists (guaranteed O(1))."""
        key_str = str(key)
        
        # Check table 1
        pos1 = self._hash1(key_str)
        if self._table1[pos1] is not None and self._table1[pos1][0] == key_str:
            return True
        
        # Check table 2
        pos2 = self._hash2(key_str)
        if self._table2[pos2] is not None and self._table2[pos2][0] == key_str:
            return True
        
        return False
    
    def remove(self, key: Any) -> bool:
        """Remove a key-value pair."""
        key_str = str(key)
        
        # Check table 1
        pos1 = self._hash1(key_str)
        if self._table1[pos1] is not None and self._table1[pos1][0] == key_str:
            self._table1[pos1] = None
            self._size -= 1
            return True
        
        # Check table 2
        pos2 = self._hash2(key_str)
        if self._table2[pos2] is not None and self._table2[pos2][0] == key_str:
            self._table2[pos2] = None
            self._size -= 1
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._table1 = [None] * self.capacity
        self._table2 = [None] * self.capacity
        self._size = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        for table in [self._table1, self._table2]:
            for entry in table:
                if entry is not None:
                    yield entry[0]
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        for table in [self._table1, self._table2]:
            for entry in table:
                if entry is not None:
                    yield entry[1]
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        for table in [self._table1, self._table2]:
            for entry in table:
                if entry is not None:
                    yield entry
    
    def __len__(self) -> int:
        """Get the number of key-value pairs."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        return dict(self.items())
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This is a dict-like strategy."""
        return True
    
    # ============================================================================
    # CUCKOO HASH SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_table_utilization(self) -> Tuple[float, float]:
        """Get utilization of each table."""
        table1_used = sum(1 for entry in self._table1 if entry is not None)
        table2_used = sum(1 for entry in self._table2 if entry is not None)
        
        util1 = table1_used / self.capacity if self.capacity > 0 else 0
        util2 = table2_used / self.capacity if self.capacity > 0 else 0
        
        return util1, util2
    
    def get_max_probe_distance(self) -> int:
        """Get maximum probe distance (always 1 for cuckoo hashing)."""
        return 1  # Cuckoo hashing guarantees O(1) lookup
    
    def get_eviction_stats(self) -> Dict[str, int]:
        """Get statistics about evictions (would need tracking in real implementation)."""
        return {
            'total_evictions': 0,  # Would track in real implementation
            'max_eviction_chain': self.max_evictions,
            'resize_count': 0  # Would track in real implementation
        }
    
    def rehash(self) -> None:
        """Force a rehash with new hash functions."""
        # Save current data
        current_items = list(self.items())
        
        # Clear tables and regenerate hash functions
        self._table1 = [None] * self.capacity
        self._table2 = [None] * self.capacity
        self._hash1_a = random.randint(1, 1000000)
        self._hash1_b = random.randint(0, 1000000)
        self._hash2_a = random.randint(1, 1000000)
        self._hash2_b = random.randint(0, 1000000)
        self._size = 0
        
        # Reinsert all items
        for key, value in current_items:
            self.put(key, value)
    
    def analyze_distribution(self) -> Dict[str, Any]:
        """Analyze the distribution of elements across tables."""
        table1_count = sum(1 for entry in self._table1 if entry is not None)
        table2_count = sum(1 for entry in self._table2 if entry is not None)
        
        return {
            'table1_count': table1_count,
            'table2_count': table2_count,
            'table1_percentage': (table1_count / self._size * 100) if self._size > 0 else 0,
            'table2_percentage': (table2_count / self._size * 100) if self._size > 0 else 0,
            'balance_ratio': min(table1_count, table2_count) / max(table1_count, table2_count, 1)
        }
    
    def compact(self) -> None:
        """Compact the hash tables if load factor is too low."""
        current_load = self._size / (2 * self.capacity) if self.capacity > 0 else 0
        
        if current_load < self.load_factor / 4 and self.capacity > self.initial_capacity:
            # Save current data
            current_items = list(self.items())
            
            # Reduce capacity
            self.capacity = max(self.initial_capacity, self.capacity // 2)
            self._table1 = [None] * self.capacity
            self._table2 = [None] * self.capacity
            self._resize_threshold = int(self.capacity * self.load_factor)
            
            # Regenerate hash functions
            self._hash1_a = random.randint(1, 1000000)
            self._hash1_b = random.randint(0, 1000000)
            self._hash2_a = random.randint(1, 1000000)
            self._hash2_b = random.randint(0, 1000000)
            self._size = 0
            
            # Reinsert all items
            for key, value in current_items:
                self.put(key, value)
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        util1, util2 = self.get_table_utilization()
        
        return {
            'strategy': 'CUCKOO_HASH',
            'backend': 'Dual hash tables with eviction',
            'capacity': self.capacity,
            'load_factor': self.load_factor,
            'max_evictions': self.max_evictions,
            'table1_utilization': f"{util1 * 100:.1f}%",
            'table2_utilization': f"{util2 * 100:.1f}%",
            'complexity': {
                'lookup': 'O(1) worst-case',
                'insert': 'O(1) amortized',
                'delete': 'O(1) worst-case',
                'space': 'O(n)',
                'probe_distance': '1 (guaranteed)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        overall_load = self._size / (2 * self.capacity) if self.capacity > 0 else 0
        util1, util2 = self.get_table_utilization()
        distribution = self.analyze_distribution()
        
        return {
            'size': self._size,
            'capacity': self.capacity * 2,  # Total capacity across both tables
            'overall_load_factor': f"{overall_load * 100:.1f}%",
            'table_balance': f"{distribution['balance_ratio']:.2f}",
            'memory_usage': f"{self.capacity * 2 * 16} bytes (estimated)",
            'guaranteed_lookup_time': 'O(1)',
            'resize_threshold': self._resize_threshold
        }
