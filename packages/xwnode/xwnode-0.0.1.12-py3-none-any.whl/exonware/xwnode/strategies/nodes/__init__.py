"""
Node Strategies Package

This package contains all node strategy implementations organized by type:
- Linear strategies (arrays, lists, stacks, queues)
- Tree strategies (tries, heaps, BSTs)
- Graph strategies (union-find, neural graphs)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from .base import ANodeStrategy, ANodeLinearStrategy, ANodeTreeStrategy, ANodeGraphStrategy

# Linear strategies
from .array_list import ArrayListStrategy
from .linked_list import LinkedListStrategy

# Tree strategies
from .trie import xTrieStrategy
from .heap import xHeapStrategy
from .aho_corasick import xAhoCorasickStrategy

# Graph strategies
from .hash_map import HashMapStrategy
from .union_find import xUnionFindStrategy

__all__ = [
    # Base classes
    'ANodeStrategy',
    'ANodeLinearStrategy', 
    'ANodeTreeStrategy',
    'ANodeGraphStrategy',
    
    # Linear strategies
    'ArrayListStrategy',
    'LinkedListStrategy',
    
    # Tree strategies
    'xTrieStrategy',
    'xHeapStrategy',
    'xAhoCorasickStrategy',
    
    # Graph strategies
    'HashMapStrategy',
    'xUnionFindStrategy'
]
