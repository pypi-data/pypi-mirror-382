"""
Adjacency List Edge Strategy Implementation

This module implements the ADJ_LIST strategy for sparse graph representation
with efficient edge addition and neighbor queries.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple
from collections import defaultdict
from .base import AGraphEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class AdjListStrategy(AGraphEdgeStrategy):
    """
    Adjacency List edge strategy for sparse graph representation.
    
    Provides O(1) edge addition and O(degree) neighbor queries,
    ideal for sparse graphs where most vertices have few connections.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Adjacency List strategy."""
        super().__init__(**options)
        self._mode = EdgeMode.ADJ_LIST
        self._traits = traits
        
        self.is_directed = options.get('directed', True)
        self.allow_self_loops = options.get('self_loops', True)
        self.allow_multi_edges = options.get('multi_edges', False)
        
        # Core storage: vertex -> list of (neighbor, edge_data)
        self._outgoing: Dict[str, List[Tuple[str, Dict[str, Any]]]] = defaultdict(list)
        self._incoming: Dict[str, List[Tuple[str, Dict[str, Any]]]] = defaultdict(list) if self.is_directed else None
        
        # Vertex set for fast membership testing
        self._vertices: Set[str] = set()
        
        # Edge properties storage
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the adjacency list strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.MULTI)
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, from_node: Any, to_node: Any, **kwargs) -> None:
        """Add an edge between source and target vertices."""
        source = str(from_node)
        target = str(to_node)
        
        # Validation
        if not self.allow_self_loops and source == target:
            raise ValueError("Self loops not allowed")
        
        if not self.allow_multi_edges and self.has_edge(source, target):
            raise ValueError("Multi edges not allowed")
        
        # Add vertices to set
        self._vertices.add(source)
        self._vertices.add(target)
        
        # Create edge data
        edge_data = {
            'weight': kwargs.get('weight', 1.0),
            'id': f"edge_{self._edge_id_counter}",
            **kwargs
        }
        self._edge_id_counter += 1
        
        # Add outgoing edge
        self._outgoing[source].append((target, edge_data))
        
        # Add incoming edge if directed
        if self.is_directed and self._incoming is not None:
            self._incoming[target].append((source, edge_data))
        elif not self.is_directed:
            # For undirected, add reverse edge
            self._outgoing[target].append((source, edge_data))
        
        self._edge_count += 1
    
    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between vertices."""
        source = str(from_node)
        target = str(to_node)
        
        removed = False
        
        # Remove from outgoing
        for i, (neighbor, _) in enumerate(self._outgoing[source]):
            if neighbor == target:
                self._outgoing[source].pop(i)
                removed = True
                break
        
        # Remove from incoming if directed
        if self.is_directed and self._incoming is not None:
            for i, (neighbor, _) in enumerate(self._incoming[target]):
                if neighbor == source:
                    self._incoming[target].pop(i)
                    break
        elif not self.is_directed:
            # For undirected, remove reverse edge
            for i, (neighbor, _) in enumerate(self._outgoing[target]):
                if neighbor == source:
                    self._outgoing[target].pop(i)
                    break
        
        if removed:
            self._edge_count -= 1
        
        return removed
    
    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists."""
        source = str(from_node)
        target = str(to_node)
        
        for neighbor, _ in self._outgoing[source]:
            if neighbor == target:
                return True
        return False
    
    def get_edge_count(self) -> int:
        """Get total number of edges."""
        return self._edge_count
    
    def get_vertex_count(self) -> int:
        """Get total number of vertices."""
        return len(self._vertices)
    
    # ============================================================================
    # GRAPH EDGE STRATEGY METHODS
    # ============================================================================
    
    def get_neighbors(self, node: Any) -> List[Any]:
        """Get all neighboring nodes."""
        vertex = str(node)
        neighbors = []
        for neighbor, _ in self._outgoing[vertex]:
            neighbors.append(neighbor)
        return neighbors
    
    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight."""
        source = str(from_node)
        target = str(to_node)
        
        for neighbor, edge_data in self._outgoing[source]:
            if neighbor == target:
                return edge_data.get('weight', 1.0)
        return 0.0
    
    def set_edge_weight(self, from_node: Any, to_node: Any, weight: float) -> None:
        """Set edge weight."""
        source = str(from_node)
        target = str(to_node)
        
        for neighbor, edge_data in self._outgoing[source]:
            if neighbor == target:
                edge_data['weight'] = weight
                return
        raise ValueError(f"Edge {source} -> {target} not found")
    
    def find_shortest_path(self, start: Any, end: Any) -> List[Any]:
        """Find shortest path between nodes."""
        # TODO: Implement BFS/Dijkstra
        return []
    
    def find_all_paths(self, start: Any, end: Any) -> List[List[Any]]:
        """Find all paths between nodes."""
        # TODO: Implement DFS
        return []
    
    def get_connected_components(self) -> List[List[Any]]:
        """Get all connected components."""
        # TODO: Implement connected components
        return []
    
    def is_connected(self, start: Any, end: Any) -> bool:
        """Check if two nodes are connected."""
        # TODO: Implement connectivity check
        return False
    
    def get_degree(self, node: Any) -> int:
        """Get degree of node."""
        vertex = str(node)
        return len(self._outgoing[vertex])
    
    def is_cyclic(self) -> bool:
        """Check if graph contains cycles."""
        # TODO: Implement cycle detection
        return False
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'adjacency_list',
            'backend': 'Dictionary of lists',
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(degree)',
                'has_edge': 'O(degree)',
                'get_neighbors': 'O(degree)',
                'space': 'O(V + E)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'directed': self.is_directed,
            'density': f"{(self._edge_count / max(1, len(self._vertices) * (len(self._vertices) - 1))) * 100:.1f}%"
        }
