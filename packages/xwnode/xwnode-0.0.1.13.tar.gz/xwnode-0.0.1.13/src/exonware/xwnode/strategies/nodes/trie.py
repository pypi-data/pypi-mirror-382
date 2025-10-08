"""
Trie Node Strategy Implementation

This module implements the TRIE strategy for efficient string prefix operations.
"""

from typing import Any, Iterator, Dict, List, Optional
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class TrieNode:
    """Node in the trie structure."""
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word = False
        self.value: Any = None


class xTrieStrategy(ANodeTreeStrategy):
    """
    Trie node strategy for efficient string prefix operations.
    
    Optimized for prefix matching, autocomplete, and string searching.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the trie strategy."""
        super().__init__(data=None, **options)
        self._mode = NodeMode.TRIE
        self._traits = traits
        self._root = TrieNode()
        self._size = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the trie strategy."""
        return (NodeTrait.ORDERED | NodeTrait.HIERARCHICAL | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """Store a key-value pair (key should be string-like)."""
        word = str(key)
        node = self._root
        
        # Traverse/create path
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Mark end of word and store value
        if not node.is_end_of_word:
            self._size += 1
        node.is_end_of_word = True
        node.value = value
    
    def find(self, key: Any) -> Any:
        """Retrieve a value by key."""
        word = str(key)
        node = self._root
        
        # Traverse path
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        
        return node.value if node.is_end_of_word else None
    
    def delete(self, key: Any) -> bool:
        """Remove a key-value pair."""
        word = str(key)
        return self._delete_helper(self._root, word, 0)
    
    def _delete_helper(self, node: TrieNode, word: str, index: int) -> bool:
        """Helper method for deletion."""
        if index == len(word):
            if node.is_end_of_word:
                node.is_end_of_word = False
                node.value = None
                self._size -= 1
                return True
            return False
        
        char = word[index]
        if char not in node.children:
            return False
        
        deleted = self._delete_helper(node.children[char], word, index + 1)
        
        # Clean up empty nodes
        if deleted and not node.children[char].children and not node.children[char].is_end_of_word:
            del node.children[char]
        
        return deleted
    
    def size(self) -> int:
        """Get the number of items."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if the structure is empty."""
        return self._size == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        result = {}
        self._collect_words(self._root, "", result)
        return result
    
    def _collect_words(self, node: TrieNode, prefix: str, result: Dict[str, Any]) -> None:
        """Collect all words from trie."""
        if node.is_end_of_word:
            result[prefix] = node.value
        
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, result)
    
    # ============================================================================
    # TREE STRATEGY METHODS
    # ============================================================================
    
    def traverse(self, order: str = 'inorder') -> List[Any]:
        """Traverse tree in specified order."""
        result = []
        self._collect_words(self._root, "", result)
        return list(result.values())
    
    def get_min(self) -> Any:
        """Get minimum key."""
        # Find leftmost word
        node = self._root
        word = ""
        while node.children:
            char = min(node.children.keys())
            word += char
            node = node.children[char]
        return word if node.is_end_of_word else None
    
    def get_max(self) -> Any:
        """Get maximum key."""
        # Find rightmost word
        node = self._root
        word = ""
        while node.children:
            char = max(node.children.keys())
            word += char
            node = node.children[char]
        return word if node.is_end_of_word else None
    
    # ============================================================================
    # AUTO-3 Phase 2 methods
    # ============================================================================
    
    def as_trie(self):
        """Provide Trie behavioral view."""
        return self
    
    def as_heap(self):
        """Provide Heap behavioral view."""
        # TODO: Implement Heap view
        return self
    
    def as_skip_list(self):
        """Provide SkipList behavioral view."""
        # TODO: Implement SkipList view
        return self
    
    # ============================================================================
    # TRIE SPECIFIC OPERATIONS
    # ============================================================================
    
    def prefix_search(self, prefix: str) -> List[str]:
        """Find all keys with given prefix."""
        node = self._root
        
        # Navigate to prefix
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words with this prefix
        result = []
        self._collect_words(node, prefix, result)
        return list(result.keys())
    
    def longest_common_prefix(self) -> str:
        """Find longest common prefix of all keys."""
        if not self._root.children:
            return ""
        
        prefix = ""
        node = self._root
        
        while len(node.children) == 1 and not node.is_end_of_word:
            char = list(node.children.keys())[0]
            prefix += char
            node = node.children[char]
        
        return prefix
    
    def keys_with_prefix(self, prefix: str) -> List[str]:
        """Get all keys with given prefix."""
        return self.prefix_search(prefix)
    
    def keys_with_suffix(self, suffix: str) -> List[str]:
        """Get all keys with given suffix."""
        # TODO: Implement suffix search
        return []
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Get all keys."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.keys())
    
    def values(self) -> Iterator[Any]:
        """Get all values."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.values())
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.items())
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'TRIE',
            'backend': 'Trie tree',
            'complexity': {
                'insert': 'O(m)',
                'search': 'O(m)',
                'delete': 'O(m)',
                'prefix_search': 'O(m + k)',
                'space': 'O(ALPHABET_SIZE * N * M)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': self._size,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'height': self._get_height()
        }
    
    def _get_height(self) -> int:
        """Get height of trie."""
        return self._height_helper(self._root)
    
    def _height_helper(self, node: TrieNode) -> int:
        """Helper for height calculation."""
        if not node.children:
            return 0
        return 1 + max(self._height_helper(child) for child in node.children.values())
