"""
Enhanced Strategy System for XWNode

This package implements the enhanced strategy system with xwsystem-inspired optimizations:
- 28 Node Modes (comprehensive data structure coverage)
- 16 Edge Modes (complete graph support)
- 12 Traits (cross-cutting capabilities)
- Flyweight pattern for memory optimization
- Intelligent pattern detection for AUTO mode selection
- Performance monitoring and optimization recommendations
- Comprehensive metrics and statistics tracking
- Lazy materialization and strategy management
- 100% backward compatibility with existing XWNode

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

from ..types import (
    NodeMode, EdgeMode, QueryMode, NodeTrait, EdgeTrait, QueryTrait,
    AUTO, LEGACY, HASH_MAP, ORDERED_MAP, ORDERED_MAP_BALANCED,
    ARRAY_LIST, LINKED_LIST, TRIE, RADIX_TRIE, PATRICIA,
    HEAP, SET_HASH, SET_TREE, BLOOM_FILTER, CUCKOO_HASH,
    BITMAP, BITSET_DYNAMIC, ROARING_BITMAP, B_TREE, B_PLUS_TREE,
    LSM_TREE, PERSISTENT_TREE, COW_TREE, UNION_FIND, SEGMENT_TREE, FENWICK_TREE,
    SUFFIX_ARRAY, AHO_CORASICK, COUNT_MIN_SKETCH, HYPERLOGLOG,
    ADJ_LIST, DYNAMIC_ADJ_LIST, ADJ_MATRIX, BLOCK_ADJ_MATRIX,
    CSR, CSC, COO, BIDIR_WRAPPER, TEMPORAL_EDGESET,
    HYPEREDGE_SET, EDGE_PROPERTY_STORE, R_TREE, QUADTREE, OCTREE,
    SQL, HIVEQL, PIG, CQL, N1QL, EQL, KQL, FLUX, DATALOG,
    GRAPHQL, SPARQL, GREMLIN, CYPHER,
    LINQ, JSONIQ, JMESPATH, XQUERY, XPATH,
    XML_QUERY, JSON_QUERY
)

# Node strategies
from .nodes.base import ANodeStrategy, ANodeLinearStrategy, ANodeTreeStrategy, ANodeGraphStrategy, ANodeMatrixStrategy
from .nodes.array_list import ArrayListStrategy
from .nodes.linked_list import LinkedListStrategy
from .nodes.stack import StackStrategy
from .nodes.queue import QueueStrategy
from .nodes.priority_queue import PriorityQueueStrategy
from .nodes.deque import DequeStrategy
from .nodes.trie import xTrieStrategy
from .nodes.heap import xHeapStrategy
from .nodes.aho_corasick import xAhoCorasickStrategy
from .nodes.hash_map import HashMapStrategy
from .nodes.union_find import xUnionFindStrategy
from .nodes.adjacency_list import AdjacencyListStrategy
from .nodes.sparse_matrix import SparseMatrixStrategy

# Edge strategies  
from .edges.base import AEdgeStrategy, ALinearEdgeStrategy, ATreeEdgeStrategy, AGraphEdgeStrategy
from .edges.adj_list import AdjListStrategy
from .edges.adj_matrix import AdjMatrixStrategy

# Query strategies
from .queries.base import AQueryStrategy, AStructuredQueryStrategy, AGraphQueryStrategy, ADocumentQueryStrategy
from .queries.xwquery_strategy import XWQueryScriptStrategy
from .queries.xwnode_executor import XWNodeQueryActionExecutor
from .queries.sql import SQLStrategy
from .queries.hiveql import HiveQLStrategy
from .queries.pig import PigStrategy
from .queries.cql import CQLStrategy
from .queries.n1ql import N1QLStrategy
from .queries.kql import KQLStrategy
from .queries.datalog import DatalogStrategy
from .queries.mql import MQLStrategy
from .queries.partiql import PartiQLStrategy
from .queries.elastic_dsl import ElasticDSLStrategy
from .queries.eql import EQLStrategy
from .queries.flux import FluxStrategy
from .queries.promql import PromQLStrategy
from .queries.graphql import GraphQLStrategy
from .queries.sparql import SPARQLStrategy
from .queries.gremlin import GremlinStrategy
from .queries.cypher import CypherStrategy
from .queries.gql import GQLStrategy
from .queries.linq import LINQStrategy
from .queries.hql import HQLStrategy
from .queries.jsoniq import JSONiqStrategy
from .queries.jmespath import JMESPathStrategy
from .queries.jq import JQStrategy
from .queries.xquery import XQueryStrategy
from .queries.xpath import XPathStrategy
from .queries.logql import LogQLStrategy
from .queries.xml_query import XMLQueryStrategy
from .queries.json_query import JSONQueryStrategy

from .registry import StrategyRegistry, get_registry, register_node_strategy, register_edge_strategy
from .advisor import StrategyAdvisor, get_advisor
from .manager import StrategyManager

# Enhanced components
from .flyweight import StrategyFlyweight, get_flyweight, get_flyweight_stats, clear_flyweight_cache
from .pattern_detector import DataPatternDetector, get_detector, analyze_data_patterns, recommend_strategy
from .performance_monitor import StrategyPerformanceMonitor, get_monitor, record_operation, get_performance_summary
from .metrics import StrategyMetricsCollector, get_metrics_collector, collect_comprehensive_metrics, get_metrics_summary

__all__ = [
    # Types and enums
    'NodeMode', 'EdgeMode', 'QueryMode', 'NodeTrait', 'EdgeTrait', 'QueryTrait',
    'AUTO', 'LEGACY', 'HASH_MAP', 'ORDERED_MAP', 'ORDERED_MAP_BALANCED',
    'ARRAY_LIST', 'LINKED_LIST', 'TRIE', 'RADIX_TRIE', 'PATRICIA',
    'HEAP', 'SET_HASH', 'SET_TREE', 'BLOOM_FILTER', 'CUCKOO_HASH',
    'BITMAP', 'BITSET_DYNAMIC', 'ROARING_BITMAP', 'B_TREE', 'B_PLUS_TREE',
    'LSM_TREE', 'PERSISTENT_TREE', 'COW_TREE', 'UNION_FIND', 'SEGMENT_TREE', 'FENWICK_TREE',
    'SUFFIX_ARRAY', 'AHO_CORASICK', 'COUNT_MIN_SKETCH', 'HYPERLOGLOG',
    'ADJ_LIST', 'DYNAMIC_ADJ_LIST', 'ADJ_MATRIX', 'BLOCK_ADJ_MATRIX',
    'CSR', 'CSC', 'COO', 'BIDIR_WRAPPER', 'TEMPORAL_EDGESET',
    'HYPEREDGE_SET', 'EDGE_PROPERTY_STORE', 'R_TREE', 'QUADTREE', 'OCTREE',
    'SQL', 'HIVEQL', 'PIG', 'CQL', 'N1QL', 'EQL', 'KQL', 'FLUX', 'DATALOG',
    'GRAPHQL', 'SPARQL', 'GREMLIN', 'CYPHER',
    'LINQ', 'JSONIQ', 'JMESPATH', 'XQUERY', 'XPATH',
    'XML_QUERY', 'JSON_QUERY',
    
    # Node strategy base classes
    'ANodeStrategy', 'ANodeLinearStrategy', 'ANodeTreeStrategy', 'ANodeGraphStrategy', 'ANodeMatrixStrategy',
    
    # Node strategy implementations
    'ArrayListStrategy', 'LinkedListStrategy', 'StackStrategy', 'QueueStrategy',
    'PriorityQueueStrategy', 'DequeStrategy', 'TrieStrategy', 'HeapStrategy',
    'AhoCorasickStrategy', 'HashMapStrategy', 'UnionFindStrategy',
    'AdjacencyListStrategy', 'SparseMatrixStrategy',
    
    # Edge strategy base classes
    'AEdgeStrategy', 'ALinearEdgeStrategy', 'ATreeEdgeStrategy', 'AGraphEdgeStrategy',
    
    # Edge strategy implementations
    'AdjListStrategy', 'AdjMatrixStrategy',
    
    # Query strategy base classes
    'AQueryStrategy', 'AStructuredQueryStrategy', 'AGraphQueryStrategy', 'ADocumentQueryStrategy',
    
    # Query strategy implementations
    'XWQueryScriptStrategy', 'XWNodeQueryActionExecutor',
    'SQLStrategy', 'HiveQLStrategy', 'PigStrategy', 'CQLStrategy', 'N1QLStrategy',
    'KQLStrategy', 'DatalogStrategy', 'MQLStrategy', 'PartiQLStrategy',
    'ElasticDSLStrategy', 'EQLStrategy', 'FluxStrategy', 'PromQLStrategy',
    'GraphQLStrategy', 'SPARQLStrategy', 'GremlinStrategy', 'CypherStrategy', 'GQLStrategy',
    'LINQStrategy', 'HQLStrategy', 'JSONiqStrategy', 'JMESPathStrategy', 'JQStrategy',
    'XQueryStrategy', 'XPathStrategy', 'LogQLStrategy',
    'XMLQueryStrategy', 'JSONQueryStrategy',
    
    # Strategy management
    'StrategyRegistry', 'get_registry', 'register_node_strategy', 'register_edge_strategy',
    'StrategyAdvisor', 'get_advisor',
    'StrategyManager',
    
    # Enhanced components
    'StrategyFlyweight', 'get_flyweight', 'get_flyweight_stats', 'clear_flyweight_cache',
    'DataPatternDetector', 'get_detector', 'analyze_data_patterns', 'recommend_strategy',
    'StrategyPerformanceMonitor', 'get_monitor', 'record_operation', 'get_performance_summary',
    'StrategyMetricsCollector', 'get_metrics_collector', 'collect_comprehensive_metrics', 'get_metrics_summary'
]
