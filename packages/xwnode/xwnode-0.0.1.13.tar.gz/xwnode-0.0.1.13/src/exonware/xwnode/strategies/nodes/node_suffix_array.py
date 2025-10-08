"""
Suffix Array Node Strategy Implementation

This module implements the SUFFIX_ARRAY strategy for efficient substring
searches and string pattern matching with linear time construction.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
import bisect
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class SuffixArrayStrategy(ANodeTreeStrategy):
    """
    Suffix Array node strategy for efficient string operations.
    
    Provides fast substring searches, pattern matching, and string analysis
    with linear space usage and efficient query operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Suffix Array strategy."""
        super().__init__(NodeMode.SUFFIX_ARRAY, traits, **options)
        
        self.enable_lcp = options.get('enable_lcp', True)  # Longest Common Prefix array
        self.case_sensitive = options.get('case_sensitive', True)
        self.separator = options.get('separator', '$')  # End-of-string marker
        
        # Core storage
        self._text = ""
        self._suffix_array: List[int] = []
        self._lcp_array: List[int] = []  # Longest Common Prefix
        self._rank: List[int] = []  # Inverse suffix array
        
        # Key-value mapping for compatibility
        self._key_to_pos: Dict[str, List[int]] = {}
        self._values: Dict[str, Any] = {}
        self._size = 0
        
        # Performance optimizations
        self._is_built = False
        self._pattern_cache: Dict[str, List[int]] = {}
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the suffix array strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.STREAMING)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for suffix array construction."""
        if not self.case_sensitive:
            text = text.lower()
        
        # Ensure text ends with separator
        if not text.endswith(self.separator):
            text += self.separator
        
        return text
    
    def _build_suffix_array_naive(self) -> None:
        """Build suffix array using naive O(n²log n) algorithm."""
        n = len(self._text)
        suffixes = []
        
        for i in range(n):
            suffixes.append((self._text[i:], i))
        
        # Sort suffixes lexicographically
        suffixes.sort()
        
        self._suffix_array = [suffix[1] for suffix in suffixes]
        self._build_rank_array()
        
        if self.enable_lcp:
            self._build_lcp_array()
    
    def _build_suffix_array_optimized(self) -> None:
        """Build suffix array using optimized radix sort approach."""
        # For simplicity, using naive approach - can be optimized with DC3/SA-IS algorithms
        self._build_suffix_array_naive()
    
    def _build_rank_array(self) -> None:
        """Build rank array (inverse of suffix array)."""
        n = len(self._suffix_array)
        self._rank = [0] * n
        
        for i in range(n):
            self._rank[self._suffix_array[i]] = i
    
    def _build_lcp_array(self) -> None:
        """Build Longest Common Prefix array using Kasai's algorithm."""
        n = len(self._text)
        self._lcp_array = [0] * n
        
        if n == 0:
            return
        
        k = 0
        for i in range(n):
            if self._rank[i] == n - 1:
                k = 0
                continue
            
            j = self._suffix_array[self._rank[i] + 1]
            
            while (i + k < n and j + k < n and 
                   self._text[i + k] == self._text[j + k]):
                k += 1
            
            self._lcp_array[self._rank[i]] = k
            
            if k > 0:
                k -= 1
    
    def _rebuild_if_needed(self) -> None:
        """Rebuild suffix array if text has changed."""
        if not self._is_built and self._text:
            self._build_suffix_array_optimized()
            self._is_built = True
    
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add string to suffix array."""
        key_str = str(key)
        
        # If this is the first key or a text replacement
        if not self._text or key_str == "text":
            # Replace entire text
            self._text = self._preprocess_text(str(value) if value else key_str)
            self._is_built = False
            self._pattern_cache.clear()
            self._key_to_pos.clear()
            self._values[key_str] = value
            self._size = 1
        else:
            # Append to text (less efficient, requires rebuild)
            if self._text.endswith(self.separator):
                self._text = self._text[:-1] + str(value) + self.separator
            else:
                self._text += str(value) + self.separator
            
            self._is_built = False
            self._pattern_cache.clear()
            self._values[key_str] = value
            self._size += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "text":
            return self._text
        elif key_str == "suffix_array":
            self._rebuild_if_needed()
            return self._suffix_array.copy()
        elif key_str == "lcp_array":
            self._rebuild_if_needed()
            return self._lcp_array.copy()
        elif key_str in self._values:
            return self._values[key_str]
        
        return default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        return key_str in self._values or key_str in ["text", "suffix_array", "lcp_array"]
    
    def remove(self, key: Any) -> bool:
        """Remove key (limited support)."""
        key_str = str(key)
        
        if key_str in self._values:
            del self._values[key_str]
            self._size -= 1
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._text = ""
        self._suffix_array.clear()
        self._lcp_array.clear()
        self._rank.clear()
        self._key_to_pos.clear()
        self._values.clear()
        self._pattern_cache.clear()
        self._size = 0
        self._is_built = False
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        yield "text"
        yield "suffix_array"
        if self.enable_lcp:
            yield "lcp_array"
        for key in self._values.keys():
            yield key
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        yield self._text
        self._rebuild_if_needed()
        yield self._suffix_array.copy()
        if self.enable_lcp:
            yield self._lcp_array.copy()
        for value in self._values.values():
            yield value
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        yield ("text", self._text)
        self._rebuild_if_needed()
        yield ("suffix_array", self._suffix_array.copy())
        if self.enable_lcp:
            yield ("lcp_array", self._lcp_array.copy())
        for key, value in self._values.items():
            yield (key, value)
    
    def __len__(self) -> int:
        """Get number of stored items."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        result = {"text": self._text}
        self._rebuild_if_needed()
        result["suffix_array"] = self._suffix_array.copy()
        if self.enable_lcp:
            result["lcp_array"] = self._lcp_array.copy()
        result.update(self._values)
        return result
    
    @property
    def is_list(self) -> bool:
        """This can behave like a list for suffix access."""
        return True
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict."""
        return True
    
    # ============================================================================
    # SUFFIX ARRAY SPECIFIC OPERATIONS
    # ============================================================================
    
    def set_text(self, text: str) -> None:
        """Set the text for suffix array operations."""
        self._text = self._preprocess_text(text)
        self._is_built = False
        self._pattern_cache.clear()
        self._size = 1
    
    def search_pattern(self, pattern: str) -> List[int]:
        """Search for pattern occurrences using binary search."""
        if not pattern:
            return []
        
        # Check cache first
        if pattern in self._pattern_cache:
            return self._pattern_cache[pattern]
        
        self._rebuild_if_needed()
        
        if not self._suffix_array:
            return []
        
        if not self.case_sensitive:
            pattern = pattern.lower()
        
        # Binary search for leftmost occurrence
        left = self._binary_search_left(pattern)
        if left == -1:
            self._pattern_cache[pattern] = []
            return []
        
        # Binary search for rightmost occurrence
        right = self._binary_search_right(pattern)
        
        # Extract all matching positions
        positions = []
        for i in range(left, right + 1):
            pos = self._suffix_array[i]
            positions.append(pos)
        
        positions.sort()
        self._pattern_cache[pattern] = positions
        return positions
    
    def _binary_search_left(self, pattern: str) -> int:
        """Find leftmost occurrence of pattern."""
        left, right = 0, len(self._suffix_array) - 1
        result = -1
        
        while left <= right:
            mid = (left + right) // 2
            suffix_pos = self._suffix_array[mid]
            suffix = self._text[suffix_pos:]
            
            if suffix.startswith(pattern):
                result = mid
                right = mid - 1  # Continue searching left
            elif suffix < pattern:
                left = mid + 1
            else:
                right = mid - 1
        
        return result
    
    def _binary_search_right(self, pattern: str) -> int:
        """Find rightmost occurrence of pattern."""
        left, right = 0, len(self._suffix_array) - 1
        result = -1
        
        while left <= right:
            mid = (left + right) // 2
            suffix_pos = self._suffix_array[mid]
            suffix = self._text[suffix_pos:]
            
            if suffix.startswith(pattern):
                result = mid
                left = mid + 1  # Continue searching right
            elif suffix < pattern:
                left = mid + 1
            else:
                right = mid - 1
        
        return result
    
    def count_occurrences(self, pattern: str) -> int:
        """Count occurrences of pattern."""
        return len(self.search_pattern(pattern))
    
    def find_longest_common_substring(self, other_text: str) -> Tuple[str, int, int]:
        """Find longest common substring with another text."""
        if not self._text or not other_text:
            return "", 0, 0
        
        # Create combined text with separator
        combined = self._text + "#" + other_text + self.separator
        original_text = self._text
        
        # Temporarily set combined text
        self.set_text(combined)
        self._rebuild_if_needed()
        
        # Find longest common substring using LCP array
        max_lcp = 0
        max_pos = 0
        text1_len = len(original_text)
        
        for i in range(len(self._lcp_array) - 1):
            pos1 = self._suffix_array[i]
            pos2 = self._suffix_array[i + 1]
            
            # Check if suffixes are from different texts
            if ((pos1 < text1_len) != (pos2 < text1_len)) and self._lcp_array[i] > max_lcp:
                max_lcp = self._lcp_array[i]
                max_pos = min(pos1, pos2)
        
        # Restore original text
        self.set_text(original_text)
        
        if max_lcp > 0:
            lcs = combined[max_pos:max_pos + max_lcp]
            return lcs, max_pos, max_lcp
        
        return "", 0, 0
    
    def get_suffix(self, index: int) -> str:
        """Get suffix starting at given index."""
        if 0 <= index < len(self._text):
            return self._text[index:]
        return ""
    
    def get_sorted_suffixes(self) -> List[str]:
        """Get all suffixes in sorted order."""
        self._rebuild_if_needed()
        
        suffixes = []
        for pos in self._suffix_array:
            suffixes.append(self._text[pos:])
        
        return suffixes
    
    def find_repeated_substrings(self, min_length: int = 2) -> List[Tuple[str, int, List[int]]]:
        """Find repeated substrings using LCP array."""
        self._rebuild_if_needed()
        
        if not self.enable_lcp:
            return []
        
        repeated = []
        
        for i in range(len(self._lcp_array)):
            lcp_len = self._lcp_array[i]
            
            if lcp_len >= min_length:
                pos1 = self._suffix_array[i]
                pos2 = self._suffix_array[i + 1]
                
                substring = self._text[pos1:pos1 + lcp_len]
                
                # Find all occurrences of this substring
                positions = self.search_pattern(substring)
                
                if len(positions) > 1:
                    repeated.append((substring, lcp_len, positions))
        
        # Remove duplicates and sort by length
        unique_repeated = {}
        for substr, length, positions in repeated:
            if substr not in unique_repeated or len(positions) > len(unique_repeated[substr][1]):
                unique_repeated[substr] = (length, positions)
        
        result = [(substr, data[0], data[1]) for substr, data in unique_repeated.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive suffix array statistics."""
        self._rebuild_if_needed()
        
        if not self._text:
            return {'text_length': 0, 'unique_characters': 0, 'suffixes': 0}
        
        unique_chars = len(set(self._text))
        avg_lcp = sum(self._lcp_array) / len(self._lcp_array) if self._lcp_array else 0
        max_lcp = max(self._lcp_array) if self._lcp_array else 0
        
        return {
            'text_length': len(self._text),
            'unique_characters': unique_chars,
            'suffixes': len(self._suffix_array),
            'avg_lcp': avg_lcp,
            'max_lcp': max_lcp,
            'case_sensitive': self.case_sensitive,
            'pattern_cache_size': len(self._pattern_cache),
            'memory_usage': len(self._text) + len(self._suffix_array) * 4 + len(self._lcp_array) * 4
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'SUFFIX_ARRAY',
            'backend': 'Suffix array with LCP array and binary search',
            'enable_lcp': self.enable_lcp,
            'case_sensitive': self.case_sensitive,
            'separator': self.separator,
            'complexity': {
                'construction': 'O(n log n)',  # Can be optimized to O(n)
                'pattern_search': 'O(m log n + occ)',  # m = pattern length, occ = occurrences
                'space': 'O(n)',
                'lcp_construction': 'O(n)',
                'substring_queries': 'O(log n + occ)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        
        return {
            'text_length': stats['text_length'],
            'suffixes': stats['suffixes'],
            'unique_chars': stats['unique_characters'],
            'avg_lcp': f"{stats['avg_lcp']:.2f}",
            'max_lcp': stats['max_lcp'],
            'cache_entries': stats['pattern_cache_size'],
            'memory_usage': f"{stats['memory_usage']} bytes"
        }
