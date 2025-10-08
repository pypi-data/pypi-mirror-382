"""
Aho-Corasick Node Strategy Implementation

This module implements the AHO_CORASICK strategy for efficient multi-pattern
string matching using the Aho-Corasick automaton algorithm.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
from .base import ANodeTreeStrategy
from ...types import NodeMode, NodeTrait


class ACNode:
    """Node in the Aho-Corasick trie."""
    
    def __init__(self):
        self.children: Dict[str, 'ACNode'] = {}
        self.failure: Optional['ACNode'] = None
        self.output: Set[str] = set()  # Patterns that end at this node
        self.pattern_indices: Set[int] = set()  # Indices of patterns
        self.depth = 0
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0


class xAhoCorasickStrategy(ANodeTreeStrategy):
    """
    Aho-Corasick node strategy for multi-pattern string matching.
    
    Efficiently searches for multiple patterns simultaneously in a text
    using a finite automaton with failure links for linear-time matching.
    """
    
    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """Initialize the Aho-Corasick strategy."""
        super().__init__(data=None, **options)
        self._mode = NodeMode.AHO_CORASICK
        self._traits = traits
        
        self.case_sensitive = options.get('case_sensitive', True)
        self.enable_overlapping = options.get('enable_overlapping', True)
        self.max_pattern_length = options.get('max_pattern_length', 1000)
        
        # Core automaton
        self._root = ACNode()
        self._patterns: List[str] = []
        self._pattern_to_index: Dict[str, int] = {}
        self._automaton_built = False
        
        # Performance tracking
        self._size_tracker = 0
        self._access_tracker = 0
    
    def get_supported_traits(self) -> NodeTrait:
        """Get the traits supported by the Aho-Corasick strategy."""
        return (NodeTrait.ORDERED | NodeTrait.HIERARCHICAL | NodeTrait.INDEXED)
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """Store a pattern (key should be string-like)."""
        pattern = str(key)
        if not self.case_sensitive:
            pattern = pattern.lower()
        
        if len(pattern) > self.max_pattern_length:
            raise ValueError(f"Pattern too long: {len(pattern)} > {self.max_pattern_length}")
        
        if pattern not in self._pattern_to_index:
            self._patterns.append(pattern)
            self._pattern_to_index[pattern] = len(self._patterns) - 1
            self._automaton_built = False
            self._size_tracker += 1
    
    def find(self, key: Any) -> Any:
        """Find pattern index."""
        pattern = str(key)
        if not self.case_sensitive:
            pattern = pattern.lower()
        return self._pattern_to_index.get(pattern)
    
    def delete(self, key: Any) -> bool:
        """Remove a pattern."""
        pattern = str(key)
        if not self.case_sensitive:
            pattern = pattern.lower()
        
        if pattern in self._pattern_to_index:
            index = self._pattern_to_index[pattern]
            del self._patterns[index]
            del self._pattern_to_index[pattern]
            self._automaton_built = False
            self._size_tracker -= 1
            return True
        return False
    
    def size(self) -> int:
        """Get the number of patterns."""
        return self._size_tracker
    
    def is_empty(self) -> bool:
        """Check if the structure is empty."""
        return self._size_tracker == 0
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python dictionary."""
        return {pattern: index for pattern, index in self._pattern_to_index.items()}
    
    # ============================================================================
    # TREE STRATEGY METHODS
    # ============================================================================
    
    def traverse(self, order: str = 'inorder') -> List[Any]:
        """Traverse patterns in specified order."""
        return self._patterns.copy()
    
    def get_min(self) -> Any:
        """Get minimum pattern."""
        return min(self._patterns) if self._patterns else None
    
    def get_max(self) -> Any:
        """Get maximum pattern."""
        return max(self._patterns) if self._patterns else None
    
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
    # AHO-CORASICK SPECIFIC OPERATIONS
    # ============================================================================
    
    def add_pattern(self, pattern: str, metadata: Any = None) -> None:
        """Add a pattern to the automaton."""
        self.insert(pattern, metadata)
    
    def search_text(self, text: str) -> List[Tuple[str, int, Any]]:
        """Search for all patterns in the given text."""
        if not self._automaton_built:
            self._build_automaton()
        
        results = []
        current = self._root
        
        for i, char in enumerate(text):
            if not self.case_sensitive:
                char = char.lower()
            
            # Follow failure links if needed
            while current != self._root and char not in current.children:
                current = current.failure
            
            # Move to next state
            if char in current.children:
                current = current.children[char]
            
            # Check for matches
            for pattern in current.output:
                pattern_index = self._pattern_to_index[pattern]
                results.append((pattern, i - len(pattern) + 1, pattern_index))
        
        return results
    
    def find_all_matches(self, text: str) -> Dict[str, List[int]]:
        """Find all matches grouped by pattern."""
        matches = self.search_text(text)
        result = defaultdict(list)
        
        for pattern, position, _ in matches:
            result[pattern].append(position)
        
        return dict(result)
    
    def count_matches(self, text: str) -> Dict[str, int]:
        """Count matches for each pattern."""
        all_matches = self.find_all_matches(text)
        return {pattern: len(positions) for pattern, positions in all_matches.items()}
    
    def has_any_match(self, text: str) -> bool:
        """Check if any pattern matches in the text."""
        if not self._automaton_built:
            self._build_automaton()
        
        current = self._root
        
        for char in text:
            if not self.case_sensitive:
                char = char.lower()
            
            while current != self._root and char not in current.children:
                current = current.failure
            
            if char in current.children:
                current = current.children[char]
            
            if current.output:
                return True
        
        return False
    
    def find_longest_match(self, text: str) -> Optional[Tuple[str, int, int]]:
        """Find the longest matching pattern."""
        matches = self.search_text(text)
        if not matches:
            return None
        
        # Find the longest match
        longest = max(matches, key=lambda x: len(x[0]))
        return (longest[0], longest[1], longest[1] + len(longest[0]) - 1)
    
    def replace_patterns(self, text: str, replacement_func: callable = None) -> str:
        """Replace all pattern matches in text."""
        matches = self.search_text(text)
        if not matches:
            return text
        
        # Sort matches by position (descending) to replace from end to start
        matches.sort(key=lambda x: x[1], reverse=True)
        
        result = text
        for pattern, position, _ in matches:
            if replacement_func:
                replacement = replacement_func(pattern, position)
            else:
                replacement = f"[{pattern}]"
            
            result = result[:position] + replacement + result[position + len(pattern):]
        
        return result
    
    def _build_automaton(self) -> None:
        """Build the Aho-Corasick automaton."""
        # Build trie
        for pattern in self._patterns:
            self._add_pattern_to_trie(pattern)
        
        # Build failure links
        self._build_failure_links()
        
        self._automaton_built = True
    
    def _add_pattern_to_trie(self, pattern: str, pattern_index: int) -> None:
        """Add a pattern to the trie."""
        current = self._root
        
        for char in pattern:
            if char not in current.children:
                current.children[char] = ACNode()
                current.children[char].depth = current.depth + 1
            
            current = current.children[char]
        
        current.output.add(pattern)
        current.pattern_indices.add(pattern_index)
    
    def _build_failure_links(self) -> None:
        """Build failure links using BFS."""
        queue = deque()
        
        # Initialize failure links for root's children
        for child in self._root.children.values():
            child.failure = self._root
            queue.append(child)
        
        # Build failure links for remaining nodes
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # Find failure link
                failure = current.failure
                while failure != self._root and char not in failure.children:
                    failure = failure.failure
                
                if char in failure.children:
                    child.failure = failure.children[char]
                else:
                    child.failure = self._root
                
                # Merge output sets
                child.output.update(child.failure.output)
    
    # ============================================================================
    # ITERATION
    # ============================================================================
    
    def keys(self) -> Iterator[str]:
        """Get all patterns."""
        return iter(self._patterns)
    
    def values(self) -> Iterator[Any]:
        """Get all pattern indices."""
        return iter(range(len(self._patterns)))
    
    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all pattern-index pairs."""
        return ((pattern, index) for pattern, index in self._pattern_to_index.items())
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'AHO_CORASICK',
            'backend': 'Aho-Corasick automaton',
            'complexity': {
                'build': 'O(sum of pattern lengths)',
                'search': 'O(text length + number of matches)',
                'space': 'O(sum of pattern lengths)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'patterns': len(self._patterns),
            'automaton_built': self._automaton_built,
            'case_sensitive': self.case_sensitive,
            'max_pattern_length': self.max_pattern_length
        }
