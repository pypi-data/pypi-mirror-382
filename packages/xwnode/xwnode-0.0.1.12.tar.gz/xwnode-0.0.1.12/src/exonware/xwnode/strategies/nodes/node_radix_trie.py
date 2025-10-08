"""
Radix Trie Node Strategy Implementation

This module implements the RADIX_TRIE strategy for compressed prefix
matching with path compression for memory efficiency.
"""

from typing import Any, Iterator, List, Dict, Optional, Tuple
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class RadixTrieNode:
    """Node in the radix trie (compressed trie)."""
    
    def __init__(self, edge_label: str = ""):
        self.edge_label = edge_label  # Compressed edge label
        self.children: Dict[str, 'RadixTrieNode'] = {}
        self.is_terminal = False
        self.value = None
        self.key = None  # Full key that ends at this node
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0


class RadixTrieStrategy(ANodeTreeStrategy):
    """
    Radix Trie node strategy for compressed prefix matching.
    
    Provides memory-efficient string storage with path compression
    and fast prefix-based operations.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Radix Trie strategy."""
        super().__init__(NodeMode.RADIX_TRIE, traits, **options)
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.compress_single_child = options.get('compress_single_child', True)
        
        # Core radix trie
        self._root = RadixTrieNode()
        self._size = 0
        
        # Statistics
        self._total_nodes = 1  # Root node
        self._max_depth = 0
        self._total_compression = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the radix trie strategy."""
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.COMPRESSED | NodeTrait.HIERARCHICAL)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key based on case sensitivity."""
        return key if self.case_sensitive else key.lower()
    
    def _find_common_prefix(self, str1: str, str2: str) -> int:
        """Find length of common prefix between two strings."""
        i = 0
        min_len = min(len(str1), len(str2))
        while i < min_len and str1[i] == str2[i]:
            i += 1
        return i
    
    def _split_node(self, node: RadixTrieNode, split_pos: int) -> RadixTrieNode:
        """Split node at given position in edge label."""
        if split_pos == 0 or split_pos >= len(node.edge_label):
            return node
        
        # Create new intermediate node
        old_label = node.edge_label
        new_node = RadixTrieNode(old_label[:split_pos])
        
        # Update current node
        node.edge_label = old_label[split_pos:]
        
        # Move node to be child of new node
        first_char = node.edge_label[0] if node.edge_label else ""
        new_node.children[first_char] = node
        
        self._total_nodes += 1
        return new_node
    
    def _insert_recursive(self, node: RadixTrieNode, key: str, value: Any, depth: int = 0) -> RadixTrieNode:
        """Recursively insert key-value pair."""
        self._max_depth = max(self._max_depth, depth)
        
        if not key:
            # Reached end of key
            if not node.is_terminal:
                self._size += 1
            node.is_terminal = True
            node.value = value
            node.key = key
            return node
        
        # Find matching child
        first_char = key[0]
        
        if first_char not in node.children:
            # No matching child, create new one
            new_node = RadixTrieNode(key)
            new_node.is_terminal = True
            new_node.value = value
            new_node.key = key
            node.children[first_char] = new_node
            self._total_nodes += 1
            self._size += 1
            return node
        
        child = node.children[first_char]
        edge_label = child.edge_label
        
        # Find common prefix
        common_prefix_len = self._find_common_prefix(key, edge_label)
        
        if common_prefix_len == len(edge_label):
            # Key matches or extends beyond edge label
            remaining_key = key[common_prefix_len:]
            self._insert_recursive(child, remaining_key, value, depth + 1)
        elif common_prefix_len == len(key):
            # Key is prefix of edge label - need to split
            split_node = self._split_node(child, common_prefix_len)
            if not split_node.is_terminal:
                self._size += 1
            split_node.is_terminal = True
            split_node.value = value
            split_node.key = key
            node.children[first_char] = split_node
        else:
            # Partial match - need to split and create branch
            split_node = self._split_node(child, common_prefix_len)
            
            # Insert remaining key
            remaining_key = key[common_prefix_len:]
            self._insert_recursive(split_node, remaining_key, value, depth + 1)
            
            node.children[first_char] = split_node
        
        return node
    
    def _find_node(self, key: str) -> Optional[RadixTrieNode]:
        """Find node for given key."""
        normalized_key = self._normalize_key(key)
        current = self._root
        remaining = normalized_key
        
        while remaining and current:
            first_char = remaining[0]
            
            if first_char not in current.children:
                return None
            
            child = current.children[first_char]
            edge_label = child.edge_label
            
            if remaining.startswith(edge_label):
                # Match found, continue with remaining
                remaining = remaining[len(edge_label):]
                current = child
            else:
                # Partial match or no match
                return None
        
        return current if current and current.is_terminal else None
    
    def _collect_all_keys(self, node: RadixTrieNode, prefix: str = "") -> List[Tuple[str, Any]]:
        """Collect all keys with values starting from given node."""
        result = []
        
        current_prefix = prefix + node.edge_label
        
        if node.is_terminal:
            result.append((node.key or current_prefix, node.value))
        
        for child in node.children.values():
            result.extend(self._collect_all_keys(child, current_prefix))
        
        return result
    
    def _collect_prefix_keys(self, node: RadixTrieNode, prefix: str, target_prefix: str) -> List[Tuple[str, Any]]:
        """Collect keys with given prefix starting from node."""
        result = []
        current_prefix = prefix + node.edge_label
        
        if current_prefix.startswith(target_prefix):
            # This path matches prefix
            if node.is_terminal:
                result.append((node.key or current_prefix, node.value))
            
            for child in node.children.values():
                result.extend(self._collect_prefix_keys(child, current_prefix, target_prefix))
        elif target_prefix.startswith(current_prefix):
            # Target prefix extends beyond current path
            for child in node.children.values():
                result.extend(self._collect_prefix_keys(child, current_prefix, target_prefix))
        
        return result
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """Add key-value pair to radix trie."""
        key_str = str(key)
        normalized_key = self._normalize_key(key_str)
        self._insert_recursive(self._root, normalized_key, value)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key."""
        key_str = str(key)
        
        if key_str == "trie_info":
            return {
                'size': self._size,
                'total_nodes': self._total_nodes,
                'max_depth': self._max_depth,
                'case_sensitive': self.case_sensitive,
                'compression_ratio': self._total_compression / max(1, self._total_nodes)
            }
        elif key_str == "all_keys":
            all_items = self._collect_all_keys(self._root)
            return [key for key, _ in all_items]
        
        node = self._find_node(key_str)
        return node.value if node else default
    
    def has(self, key: Any) -> bool:
        """Check if key exists."""
        key_str = str(key)
        
        if key_str in ["trie_info", "all_keys"]:
            return True
        
        return self._find_node(key_str) is not None
    
    def remove(self, key: Any) -> bool:
        """Remove key from trie (simplified implementation)."""
        key_str = str(key)
        node = self._find_node(key_str)
        
        if node and node.is_terminal:
            node.is_terminal = False
            node.value = None
            node.key = None
            self._size -= 1
            return True
        
        return False
    
    def delete(self, key: Any) -> bool:
        """Remove key from trie (alias for remove)."""
        return self.remove(key)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = RadixTrieNode()
        self._size = 0
        self._total_nodes = 1
        self._max_depth = 0
        self._total_compression = 0
    
    def keys(self) -> Iterator[str]:
        """Get all keys in lexicographic order."""
        all_items = self._collect_all_keys(self._root)
        for key, _ in sorted(all_items):
            yield key
    
    def values(self) -> Iterator[Any]:
        """Get all values in key order."""
        all_items = self._collect_all_keys(self._root)
        for _, value in sorted(all_items):
            yield value
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs in sorted order."""
        all_items = self._collect_all_keys(self._root)
        for key, value in sorted(all_items):
            yield (key, value)
    
    def __len__(self) -> int:
        """Get number of keys."""
        return self._size
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dict."""
        all_items = self._collect_all_keys(self._root)
        return dict(all_items)
    
    @property
    def is_list(self) -> bool:
        """This is not a list strategy."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """This behaves like a dict."""
        return True
    
    # ============================================================================
    # RADIX TRIE SPECIFIC OPERATIONS
    # ============================================================================
    
    def find_with_prefix(self, prefix: str) -> List[Tuple[str, Any]]:
        """Find all keys starting with given prefix."""
        normalized_prefix = self._normalize_key(prefix)
        return self._collect_prefix_keys(self._root, "", normalized_prefix)
    
    def get_keys_with_prefix(self, prefix: str) -> List[str]:
        """Get keys starting with given prefix."""
        prefix_items = self.find_with_prefix(prefix)
        return [key for key, _ in prefix_items]
    
    def get_values_with_prefix(self, prefix: str) -> List[Any]:
        """Get values for keys starting with given prefix."""
        prefix_items = self.find_with_prefix(prefix)
        return [value for _, value in prefix_items]
    
    def count_with_prefix(self, prefix: str) -> int:
        """Count keys starting with given prefix."""
        return len(self.find_with_prefix(prefix))
    
    def longest_common_prefix(self) -> str:
        """Find longest common prefix of all keys."""
        if self._size == 0:
            return ""
        
        all_keys = list(self.keys())
        if len(all_keys) == 1:
            return all_keys[0]
        
        # Find LCP of first and last keys (they're sorted)
        first_key = all_keys[0]
        last_key = all_keys[-1]
        
        common_len = self._find_common_prefix(first_key, last_key)
        return first_key[:common_len]
    
    def get_all_prefixes(self, key: str) -> List[str]:
        """Get all prefixes of key that exist in trie."""
        normalized_key = self._normalize_key(key)
        prefixes = []
        
        for i in range(1, len(normalized_key) + 1):
            prefix = normalized_key[:i]
            if self.has(prefix):
                prefixes.append(prefix)
        
        return prefixes
    
    def is_prefix_of_any(self, prefix: str) -> bool:
        """Check if prefix is a prefix of any key in trie."""
        return len(self.find_with_prefix(prefix)) > 0
    
    def get_autocomplete_suggestions(self, prefix: str, max_suggestions: int = 10) -> List[str]:
        """Get autocomplete suggestions for given prefix."""
        suggestions = self.get_keys_with_prefix(prefix)
        return suggestions[:max_suggestions]
    
    def compute_compression_statistics(self) -> Dict[str, Any]:
        """Compute detailed compression statistics."""
        def _analyze_node(node: RadixTrieNode, depth: int = 0) -> Dict[str, int]:
            stats = {
                'nodes': 1,
                'terminals': 1 if node.is_terminal else 0,
                'total_edge_length': len(node.edge_label),
                'compressed_edges': 1 if len(node.edge_label) > 1 else 0,
                'max_depth': depth
            }
            
            for child in node.children.values():
                child_stats = _analyze_node(child, depth + 1)
                stats['nodes'] += child_stats['nodes']
                stats['terminals'] += child_stats['terminals']
                stats['total_edge_length'] += child_stats['total_edge_length']
                stats['compressed_edges'] += child_stats['compressed_edges']
                stats['max_depth'] = max(stats['max_depth'], child_stats['max_depth'])
            
            return stats
        
        stats = _analyze_node(self._root)
        
        # Calculate compression ratio
        total_key_length = sum(len(key) for key in self.keys())
        compression_ratio = (stats['total_edge_length'] / max(1, total_key_length)) if total_key_length > 0 else 0
        
        return {
            'total_nodes': stats['nodes'],
            'terminal_nodes': stats['terminals'],
            'total_edge_length': stats['total_edge_length'],
            'compressed_edges': stats['compressed_edges'],
            'max_depth': stats['max_depth'],
            'compression_ratio': compression_ratio,
            'avg_edge_length': stats['total_edge_length'] / max(1, stats['nodes']),
            'keys': self._size
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive radix trie statistics."""
        compression_stats = self.compute_compression_statistics()
        
        return {
            'size': self._size,
            'total_nodes': self._total_nodes,
            'max_depth': self._max_depth,
            'case_sensitive': self.case_sensitive,
            'compression_statistics': compression_stats,
            'memory_efficiency': f"{compression_stats['compression_ratio']:.2%}",
            'avg_key_length': sum(len(key) for key in self.keys()) / max(1, self._size)
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'RADIX_TRIE',
            'backend': 'Compressed trie with path compression',
            'case_sensitive': self.case_sensitive,
            'compress_single_child': self.compress_single_child,
            'complexity': {
                'insert': 'O(k)',  # k = key length
                'search': 'O(k)',
                'delete': 'O(k)',
                'prefix_search': 'O(k + m)',  # m = number of matches
                'space': 'O(ALPHABET_SIZE * N * M)',  # N = nodes, M = avg edge length
                'compression': 'Path compression reduces space'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        comp_stats = stats['compression_statistics']
        
        return {
            'size': stats['size'],
            'total_nodes': stats['total_nodes'],
            'max_depth': stats['max_depth'],
            'compression_ratio': f"{comp_stats['compression_ratio']:.2%}",
            'avg_edge_length': f"{comp_stats['avg_edge_length']:.1f}",
            'memory_efficiency': stats['memory_efficiency'],
            'memory_usage': f"{stats['total_nodes'] * 80} bytes (estimated)"
        }
