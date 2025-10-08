#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/base.py

Abstract base classes for XWNode.

This module contains the abstract base classes that provide core functionality
for all XWNode implementations.
"""

import threading
import copy
from abc import ABC
from typing import Any, Iterator, Union, Optional, List, Dict, Callable
from collections import OrderedDict

# Core XWNode imports - strategy-agnostic
from .errors import (
    XWNodeTypeError, XWNodePathError, XWNodeSecurityError, XWNodeValueError, XWNodeLimitError
)
from .config import get_config
from .contracts import iNodeFacade, iNodeStrategy, iEdge, iEdgeStrategy, iQuery, iQueryResult, iQueryEngine

# System-level imports - standard imports (no defensive code!)
from exonware.xwsystem.security import get_resource_limits
from exonware.xwsystem.validation import validate_untrusted_data
from exonware.xwsystem.monitoring import create_component_metrics
from exonware.xwsystem.threading import ThreadSafeFactory, create_thread_safe_cache
from exonware.xwsystem.patterns import CircuitBreaker
from exonware.xwsystem import get_logger

logger = get_logger('xwnode.base')

# Metrics setup
_metrics = create_component_metrics('xwnode_base')
measure_operation = _metrics['measure_operation']
record_cache_hit = _metrics['record_cache_hit']
record_cache_miss = _metrics['record_cache_miss']

# Thread-safe cache for path parsing
_path_cache = create_thread_safe_cache(max_size=1024)

# Circuit breaker for strategy operations
_strategy_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    expected_exception=Exception
)


class PathParser:
    """Thread-safe path parser with caching."""
    
    def __init__(self, max_cache_size: int = 1024):
        self._cache = OrderedDict()
        self._max_cache_size = max_cache_size
        self._lock = threading.RLock()
    
    def parse(self, path: str) -> List[str]:
        """Parse a path string into parts."""
        with self._lock:
            if path in self._cache:
                record_cache_hit()
                return self._cache[path]
            
            record_cache_miss()
            parts = self._parse_path(path)
            
            # Cache the result
            if len(self._cache) >= self._max_cache_size:
                self._cache.popitem(last=False)
            self._cache[path] = parts
            
            return parts
    
    def _parse_path(self, path: str) -> List[str]:
        """Internal path parsing logic."""
        if not path:
            return []
        
        parts = []
        current = ""
        in_brackets = False
        in_quotes = False
        quote_char = None
        
        for char in path:
            if in_quotes:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current += char
            elif char in ['"', "'"]:
                in_quotes = True
                quote_char = char
            elif char == '[':
                if current:
                    parts.append(current)
                    current = ""
                in_brackets = True
                current += char
            elif char == ']':
                current += char
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
        
        if current:
            parts.append(current)
        
        return parts
    
    def clear_cache(self):
        """Clear the path cache."""
        with self._lock:
            self._cache.clear()


class GlobalPathCache:
    """Global cache for path lookups."""
    
    def __init__(self, max_size: int = 512):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._lock = threading.RLock()
        self._stats = {'hits': 0, 'misses': 0}
    
    def get(self, node_id: int, path: str) -> Optional[Any]:
        """Get cached result for node and path."""
        key = (node_id, path)
        with self._lock:
            if key in self._cache:
                self._stats['hits'] += 1
                return self._cache[key]
            self._stats['misses'] += 1
            return None
    
    def put(self, node_id: int, path: str, result: Any):
        """Cache result for node and path."""
        key = (node_id, path)
        with self._lock:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = result
    
    def clear(self):
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            return self._stats.copy()


# Global instances
_path_parser = None
_global_path_cache = None

def get_path_parser() -> PathParser:
    """Get the global path parser instance."""
    global _path_parser
    if _path_parser is None:
        _path_parser = PathParser()
    return _path_parser

def get_global_path_cache() -> GlobalPathCache:
    """Get the global path cache instance."""
    global _global_path_cache
    if _global_path_cache is None:
        _global_path_cache = GlobalPathCache()
    return _global_path_cache


class XWNodeBase(iNodeFacade):
    """
    Abstract base class for all XWNode implementations.
    
    This class provides the core functionality that all XWNode implementations
    must have, working through the iNodeStrategy interface.
    """
    
    __slots__ = ('_strategy', '_hash_cache', '_type_cache')
    
    def __init__(self, strategy: iNodeStrategy):
        """Initialize with a strategy implementation."""
        self._strategy = strategy
        self._hash_cache = None
        self._type_cache = None

    @classmethod
    def from_native(cls, data: Any) -> 'XWNodeBase':
        """Create XWNodeBase from native data."""
        # For now, we'll use a simple hash map strategy
        # In the full implementation, this would use the strategy manager
        from .strategies.simple import SimpleNodeStrategy
        strategy = SimpleNodeStrategy.create_from_data(data)
        return cls(strategy)

    def get(self, path: str, default: Any = None) -> Optional['XWNodeBase']:
        """Get a node by path."""
        try:
            result_strategy = self._strategy.get(path, default)
            if result_strategy is None:
                return None
            return XWNodeBase(result_strategy)
        except Exception:
            return None
    
    def set(self, path: str, value: Any, in_place: bool = True) -> 'XWNodeBase':
        """Set a value at path."""
        new_strategy = self._strategy.put(path, value)
        if in_place:
            self._strategy = new_strategy
            return self
        else:
            return XWNodeBase(new_strategy)
    
    def delete(self, path: str, in_place: bool = True) -> 'XWNodeBase':
        """Delete a node at path."""
        success = self._strategy.delete(path)
        return self
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self._strategy.exists(path)
    
    def find(self, path: str, in_place: bool = False) -> Optional['XWNodeBase']:
        """Find a node by path."""
        return self.get(path)
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        return self._strategy.to_native()
    
    def copy(self) -> 'XWNodeBase':
        """Create a deep copy."""
        return XWNodeBase(self._strategy.create_from_data(self._strategy.to_native()))
    
    def count(self, path: str = ".") -> int:
        """Count nodes at path."""
        if path == ".":
            return len(self._strategy)
        node = self.get(path)
        return len(node._strategy) if node else 0
    
    def flatten(self, separator: str = ".") -> Dict[str, Any]:
        """Flatten to dictionary."""
        result = {}
        
        def _flatten(node_strategy, prefix=""):
            if node_strategy.is_leaf:
                result[prefix or "root"] = node_strategy.value
            elif node_strategy.is_dict:
                for key in node_strategy.keys():
                    child = node_strategy.get(key)
                    new_prefix = f"{prefix}{separator}{key}" if prefix else key
                    _flatten(child, new_prefix)
            elif node_strategy.is_list:
                for i in range(len(node_strategy)):
                    child = node_strategy.get(str(i))
                    new_prefix = f"{prefix}{separator}{i}" if prefix else str(i)
                    _flatten(child, new_prefix)
        
        _flatten(self._strategy)
        return result
    
    def merge(self, other: 'XWNodeBase', strategy: str = "replace") -> 'XWNodeBase':
        """Merge with another node."""
        # Simple implementation - just replace
        return XWNodeBase(self._strategy.create_from_data(other.to_native()))
    
    def diff(self, other: 'XWNodeBase') -> Dict[str, Any]:
        """Get differences with another node."""
        return {"changed": True}  # Simple implementation
    
    def transform(self, transformer: callable) -> 'XWNodeBase':
        """Transform using a function."""
        transformed_data = transformer(self.to_native())
        return XWNodeBase(self._strategy.create_from_data(transformed_data))
    
    def select(self, *paths: str) -> Dict[str, 'XWNodeBase']:
        """Select multiple paths."""
        result = {}
        for path in paths:
            node = self.get(path)
            if node:
                result[path] = node
        return result
    
    # Container methods
    def __len__(self) -> int:
        """Get length."""
        return len(self._strategy)
    
    def __iter__(self) -> Iterator['XWNodeBase']:
        """Iterate over children."""
        for child_strategy in self._strategy:
            yield XWNodeBase(child_strategy)
    
    def __getitem__(self, key: Union[str, int]) -> 'XWNodeBase':
        """Get child by key or index."""
        child_strategy = self._strategy[key]
        return XWNodeBase(child_strategy)
    
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        self._strategy[key] = value
    
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        return key in self._strategy
    
    # Type checking properties
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self._strategy.is_leaf
    
    @property
    def is_list(self) -> bool:
        """Check if this is a list node."""
        return self._strategy.is_list
    
    @property
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        return self._strategy.is_dict
    
    @property
    def type(self) -> str:
        """Get the type of this node."""
        return self._strategy.type
    
    @property
    def value(self) -> Any:
        """Get the value of this node."""
        return self._strategy.value


class aEdge(iEdge):
    """Abstract base class for edge implementations."""
    
    def __init__(self, strategy: iEdgeStrategy):
        self._strategy = strategy
    
    def add_edge(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None,
                 is_bidirectional: bool = False, edge_id: Optional[str] = None) -> str:
        """Add an edge between source and target with advanced properties."""
        return self._strategy.add_edge(source, target, edge_type, weight, properties, is_bidirectional, edge_id)
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove an edge between source and target."""
        return self._strategy.remove_edge(source, target, edge_id)
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        return self._strategy.has_edge(source, target)
    
    def get_neighbors(self, node: str, edge_type: Optional[str] = None, direction: str = "outgoing") -> List[str]:
        """Get neighbors of a node with optional filtering."""
        return self._strategy.get_neighbors(node, edge_type, direction)
    
    def get_edges(self, edge_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        """Get all edges with metadata."""
        return self._strategy.get_edges(edge_type, direction)
    
    def get_edge_data(self, source: str, target: str, edge_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get edge data/properties."""
        return self._strategy.get_edge_data(source, target, edge_id)
    
    def shortest_path(self, source: str, target: str, edge_type: Optional[str] = None) -> List[str]:
        """Find shortest path between nodes."""
        return self._strategy.shortest_path(source, target, edge_type)
    
    def find_cycles(self, start_node: str, edge_type: Optional[str] = None, max_depth: int = 10) -> List[List[str]]:
        """Find cycles in the graph."""
        return self._strategy.find_cycles(start_node, edge_type, max_depth)
    
    def traverse_graph(self, start_node: str, strategy: str = "bfs", max_depth: int = 100, 
                      edge_type: Optional[str] = None) -> Iterator[str]:
        """Traverse the graph with cycle detection."""
        return self._strategy.traverse_graph(start_node, strategy, max_depth, edge_type)
    
    def is_connected(self, source: str, target: str, edge_type: Optional[str] = None) -> bool:
        """Check if nodes are connected."""
        return self._strategy.is_connected(source, target, edge_type)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return len(self._strategy)
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over edges with full metadata."""
        return iter(self._strategy)
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        return self._strategy.to_native()
    
    def copy(self) -> 'aEdge':
        """Create a deep copy."""
        return aEdge(copy.deepcopy(self._strategy))


class aQuery(iQuery):
    """Abstract base class for query implementations."""
    
    def __init__(self, node: XWNodeBase, engine: iQueryEngine):
        self._node = node
        self._engine = engine
    
    def query(self, query_string: str, query_type: str = "hybrid", **kwargs) -> iQueryResult:
        """Execute a query."""
        context = {"node": self._node, "type": query_type, **kwargs}
        return self._engine.execute_query(query_string, context)
    
    def find_nodes(self, predicate: Callable[[XWNodeBase], bool], max_results: Optional[int] = None) -> iQueryResult:
        """Find nodes matching predicate."""
        # Simple implementation
        results = []
        count = 0
        
        def _search(node):
            nonlocal count
            if max_results and count >= max_results:
                return
            if predicate(node):
                results.append(node)
                count += 1
            
            for child in node:
                _search(child)
        
        _search(self._node)
        return SimpleQueryResult(results)
    
    def find_by_path(self, path_pattern: str) -> iQueryResult:
        """Find nodes by path pattern."""
        # Simple implementation - exact match
        node = self._node.get(path_pattern)
        return SimpleQueryResult([node] if node else [])
    
    def find_by_value(self, value: Any, exact_match: bool = True) -> iQueryResult:
        """Find nodes by value."""
        results = []
        
        def _search(node):
            if exact_match:
                if node.value == value:
                    results.append(node)
            else:
                if str(value) in str(node.value):
                    results.append(node)
            
            for child in node:
                _search(child)
        
        _search(self._node)
        return SimpleQueryResult(results)
    
    def count_nodes(self, predicate: Optional[Callable[[XWNodeBase], bool]] = None) -> int:
        """Count nodes matching predicate."""
        if predicate is None:
            return self._node.count()
        
        count = 0
        def _count(node):
            nonlocal count
            if predicate(node):
                count += 1
            for child in node:
                _count(child)
        
        _count(self._node)
        return count
    
    # Simplified implementations for other methods
    def select(self, selector: str, **kwargs) -> List[XWNodeBase]:
        return []
    
    def filter(self, condition: str, **kwargs) -> List[XWNodeBase]:
        return []
    
    def where(self, condition: str) -> List[XWNodeBase]:
        return []
    
    def sort(self, key: str = None, reverse: bool = False) -> List[XWNodeBase]:
        return []
    
    def limit(self, count: int) -> List[XWNodeBase]:
        return []
    
    def skip(self, count: int) -> List[XWNodeBase]:
        return []
    
    def first(self) -> Optional[XWNodeBase]:
        return None
    
    def last(self) -> Optional[XWNodeBase]:
        return None
    
    def group_by(self, key: str) -> Dict[str, List[XWNodeBase]]:
        return {}
    
    def distinct(self, key: str = None) -> List[XWNodeBase]:
        return []
    
    def clear_query_cache(self):
        pass
    
    def get_query_stats(self) -> Dict[str, Any]:
        return {}


class SimpleQueryResult(iQueryResult):
    """Simple implementation of query results."""
    
    def __init__(self, nodes: List[XWNodeBase]):
        self._nodes = nodes
        self._metadata = {}
    
    @property
    def nodes(self) -> List[XWNodeBase]:
        return self._nodes
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata
    
    def first(self) -> Optional[XWNodeBase]:
        return self._nodes[0] if self._nodes else None
    
    def count(self) -> int:
        return len(self._nodes)
    
    def filter(self, predicate: Callable[[XWNodeBase], bool]) -> 'SimpleQueryResult':
        filtered = [node for node in self._nodes if predicate(node)]
        return SimpleQueryResult(filtered)
    
    def limit(self, limit: int) -> 'SimpleQueryResult':
        return SimpleQueryResult(self._nodes[:limit])
    
    def offset(self, offset: int) -> 'SimpleQueryResult':
        return SimpleQueryResult(self._nodes[offset:])


class aQueryResult(iQueryResult):
    """Abstract base class for query results."""
    pass


class aQueryEngine(iQueryEngine):
    """Abstract base class for query engines with multi-language support."""
    
    def __init__(self):
        self._parsers = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register default query language parsers."""
        # JSONPath-style queries
        self._parsers['jsonpath'] = self._parse_jsonpath
        self._parsers['xpath'] = self._parse_xpath
        self._parsers['css'] = self._parse_css_selector
        self._parsers['jq'] = self._parse_jq
        self._parsers['sql'] = self._parse_sql_like
        self._parsers['mongo'] = self._parse_mongodb
        self._parsers['graphql'] = self._parse_graphql
        # Default hybrid parser
        self._parsers['hybrid'] = self._parse_hybrid
    
    def register_parser(self, language: str, parser_func: Callable):
        """Register a custom query language parser."""
        self._parsers[language] = parser_func
    
    def detect_query_language(self, query_string: str) -> str:
        """Auto-detect query language from query string."""
        query = query_string.strip()
        
        # GraphQL detection
        if query.startswith('{') and ('query' in query or 'mutation' in query):
            return 'graphql'
        
        # SQL-like detection
        if any(keyword in query.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN']):
            return 'sql'
        
        # MongoDB detection
        if query.startswith('{') and any(op in query for op in ['$match', '$group', '$sort', '$project']):
            return 'mongo'
        
        # XPath detection
        if query.startswith('/') or query.startswith('//') or '//' in query:
            return 'xpath'
        
        # CSS selector detection
        if any(sel in query for sel in ['.', '#', '[', ':', '>']):
            return 'css'
        
        # jq detection
        if query.startswith('.') or any(func in query for func in ['map', 'select', 'group_by']):
            return 'jq'
        
        # JSONPath detection
        if query.startswith('$') or '..' in query:
            return 'jsonpath'
        
        # Default to hybrid
        return 'hybrid'
    
    @measure_operation('query_execute')
    def execute_query(self, query_string: str, context: Dict[str, Any]) -> iQueryResult:
        """Execute query with auto-detection or explicit language."""
        query_type = context.get('query_type', self.detect_query_language(query_string))
        
        if query_type not in self._parsers:
            logger.warning(f"Unknown query language: {query_type}, falling back to hybrid")
            query_type = 'hybrid'
        
        try:
            return self._parsers[query_type](query_string, context)
        except Exception as e:
            logger.error(f"Query execution failed for {query_type}: {e}")
            # Fallback to hybrid parser
            if query_type != 'hybrid':
                return self._parsers['hybrid'](query_string, context)
            raise
    
    def _parse_jsonpath(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse JSONPath-style queries."""
        # Implementation would use jsonpath library
        logger.debug(f"Parsing JSONPath query: {query}")
        return SimpleQueryResult([])
    
    def _parse_xpath(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse XPath-style queries."""
        logger.debug(f"Parsing XPath query: {query}")
        return SimpleQueryResult([])
    
    def _parse_css_selector(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse CSS selector-style queries."""
        logger.debug(f"Parsing CSS selector query: {query}")
        return SimpleQueryResult([])
    
    def _parse_jq(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse jq-style queries."""
        logger.debug(f"Parsing jq query: {query}")
        return SimpleQueryResult([])
    
    def _parse_sql_like(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse SQL-like queries."""
        logger.debug(f"Parsing SQL-like query: {query}")
        return SimpleQueryResult([])
    
    def _parse_mongodb(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse MongoDB-style queries."""
        logger.debug(f"Parsing MongoDB query: {query}")
        return SimpleQueryResult([])
    
    def _parse_graphql(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse GraphQL-style queries."""
        logger.debug(f"Parsing GraphQL query: {query}")
        return SimpleQueryResult([])
    
    def _parse_hybrid(self, query: str, context: Dict[str, Any]) -> iQueryResult:
        """Parse hybrid/default queries."""
        logger.debug(f"Parsing hybrid query: {query}")
        return SimpleQueryResult([])
