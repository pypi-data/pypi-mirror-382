"""
HyperEdge Set Strategy Implementation

This module implements the HYPEREDGE_SET strategy for hypergraphs where
edges can connect multiple vertices simultaneously.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, FrozenSet
from collections import defaultdict
import uuid
import time
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class HyperEdge:
    """Represents a hyperedge connecting multiple vertices."""
    
    def __init__(self, edge_id: str, vertices: Set[str], **properties):
        self.edge_id = edge_id
        self.vertices = frozenset(vertices)  # Immutable set of vertices
        self.properties = properties.copy()
        self.created_at = time.time()
        self.size = len(self.vertices)
        
        # Validate hyperedge
        if self.size < 2:
            raise ValueError("HyperEdge must connect at least 2 vertices")
    
    def contains_vertex(self, vertex: str) -> bool:
        """Check if vertex is in this hyperedge."""
        return vertex in self.vertices
    
    def get_other_vertices(self, vertex: str) -> Set[str]:
        """Get all other vertices in this hyperedge."""
        if vertex not in self.vertices:
            return set()
        return set(self.vertices) - {vertex}
    
    def intersects_with(self, other: 'HyperEdge') -> bool:
        """Check if this hyperedge shares vertices with another."""
        return bool(self.vertices & other.vertices)
    
    def is_subset_of(self, other: 'HyperEdge') -> bool:
        """Check if all vertices are contained in another hyperedge."""
        return self.vertices.issubset(other.vertices)
    
    def union_with(self, other: 'HyperEdge') -> Set[str]:
        """Get union of vertices with another hyperedge."""
        return set(self.vertices | other.vertices)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.edge_id,
            'vertices': list(self.vertices),
            'size': self.size,
            'properties': self.properties,
            'created_at': self.created_at
        }
    
    def __repr__(self) -> str:
        return f"HyperEdge({self.edge_id}, {set(self.vertices)})"
    
    def __hash__(self) -> int:
        return hash((self.edge_id, self.vertices))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, HyperEdge):
            return False
        return self.edge_id == other.edge_id and self.vertices == other.vertices


class xHyperEdgeSetStrategy(aEdgeStrategy):
    """
    HyperEdge Set strategy for hypergraph representation.
    
    Efficiently manages hyperedges where each edge can connect multiple vertices,
    supporting complex graph patterns like clustering, group relationships,
    and multi-way connections.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the HyperEdge Set strategy."""
        super().__init__(EdgeMode.HYPEREDGE_SET, traits, **options)
        
        self.max_edge_size = options.get('max_edge_size', 100)  # Max vertices per hyperedge
        self.enable_indexing = options.get('enable_indexing', True)
        self.track_statistics = options.get('track_statistics', True)
        
        # Core storage
        self._hyperedges: Dict[str, HyperEdge] = {}  # edge_id -> HyperEdge
        self._vertex_to_edges: Dict[str, Set[str]] = defaultdict(set)  # vertex -> set of edge_ids
        self._vertices: Set[str] = set()
        
        # Size-based indexing for efficient queries
        self._edges_by_size: Dict[int, Set[str]] = defaultdict(set) if self.enable_indexing else None
        
        # Statistics
        self._edge_count = 0
        self._total_connections = 0  # Sum of all edge sizes
        self._max_degree = 0  # Maximum vertex degree
        
        # Performance optimizations
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the hyperedge set strategy."""
        return (EdgeTrait.HYPER | EdgeTrait.WEIGHTED | EdgeTrait.SPARSE | EdgeTrait.MULTI)
    
    def _generate_edge_id(self) -> str:
        """Generate a unique edge ID."""
        self._edge_id_counter += 1
        return f"he_{self._edge_id_counter}"
    
    def _update_indices(self, hyperedge: HyperEdge, operation: str) -> None:
        """Update internal indices after edge operations."""
        if operation == "add":
            # Update vertex-to-edges mapping
            for vertex in hyperedge.vertices:
                self._vertex_to_edges[vertex].add(hyperedge.edge_id)
                self._vertices.add(vertex)
            
            # Update size index
            if self._edges_by_size is not None:
                self._edges_by_size[hyperedge.size].add(hyperedge.edge_id)
            
            # Update statistics
            self._edge_count += 1
            self._total_connections += hyperedge.size
            
            # Update max degree
            for vertex in hyperedge.vertices:
                degree = len(self._vertex_to_edges[vertex])
                self._max_degree = max(self._max_degree, degree)
        
        elif operation == "remove":
            # Update vertex-to-edges mapping
            for vertex in hyperedge.vertices:
                self._vertex_to_edges[vertex].discard(hyperedge.edge_id)
                if not self._vertex_to_edges[vertex]:
                    del self._vertex_to_edges[vertex]
                    self._vertices.discard(vertex)
            
            # Update size index
            if self._edges_by_size is not None:
                self._edges_by_size[hyperedge.size].discard(hyperedge.edge_id)
                if not self._edges_by_size[hyperedge.size]:
                    del self._edges_by_size[hyperedge.size]
            
            # Update statistics
            self._edge_count -= 1
            self._total_connections -= hyperedge.size
            
            # Recalculate max degree (expensive, could be optimized)
            self._max_degree = max((len(edges) for edges in self._vertex_to_edges.values()), default=0)
    
    # ============================================================================
    # CORE EDGE OPERATIONS (Adapted for hyperedges)
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add a binary hyperedge (compatibility method)."""
        return self.add_hyperedge([source, target], **properties)
    
    def add_hyperedge(self, vertices: List[str], edge_id: Optional[str] = None, **properties) -> str:
        """Add a hyperedge connecting multiple vertices."""
        # Validate input
        vertex_set = set(vertices)
        if len(vertex_set) < 2:
            raise ValueError("Hyperedge must connect at least 2 distinct vertices")
        
        if len(vertex_set) > self.max_edge_size:
            raise ValueError(f"Hyperedge size {len(vertex_set)} exceeds maximum {self.max_edge_size}")
        
        # Generate edge ID if not provided
        if edge_id is None:
            edge_id = self._generate_edge_id()
        elif edge_id in self._hyperedges:
            raise ValueError(f"HyperEdge ID {edge_id} already exists")
        
        # Create hyperedge
        hyperedge = HyperEdge(edge_id, vertex_set, **properties)
        
        # Store and index
        self._hyperedges[edge_id] = hyperedge
        self._update_indices(hyperedge, "add")
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove a binary edge (compatibility method)."""
        if edge_id:
            return self.remove_hyperedge(edge_id)
        else:
            # Find and remove edge containing both vertices
            for eid in self._vertex_to_edges.get(source, set()).copy():
                hyperedge = self._hyperedges.get(eid)
                if hyperedge and target in hyperedge.vertices and hyperedge.size == 2:
                    return self.remove_hyperedge(eid)
            return False
    
    def remove_hyperedge(self, edge_id: str) -> bool:
        """Remove a hyperedge by ID."""
        if edge_id not in self._hyperedges:
            return False
        
        hyperedge = self._hyperedges[edge_id]
        
        # Remove from storage and indices
        del self._hyperedges[edge_id]
        self._update_indices(hyperedge, "remove")
        
        return True
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if binary edge exists (compatibility method)."""
        return self.has_connection(source, target)
    
    def has_connection(self, vertex1: str, vertex2: str) -> bool:
        """Check if two vertices are connected by any hyperedge."""
        if vertex1 not in self._vertex_to_edges:
            return False
        
        for edge_id in self._vertex_to_edges[vertex1]:
            hyperedge = self._hyperedges[edge_id]
            if vertex2 in hyperedge.vertices:
                return True
        
        return False
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get data for binary edge (compatibility method)."""
        # Find first hyperedge containing both vertices
        if source not in self._vertex_to_edges:
            return None
        
        for edge_id in self._vertex_to_edges[source]:
            hyperedge = self._hyperedges[edge_id]
            if target in hyperedge.vertices:
                return hyperedge.to_dict()
        
        return None
    
    def get_hyperedge_data(self, edge_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific hyperedge."""
        hyperedge = self._hyperedges.get(edge_id)
        return hyperedge.to_dict() if hyperedge else None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get all vertices connected to given vertex."""
        if vertex not in self._vertex_to_edges:
            return iter([])
        
        connected_vertices = set()
        
        for edge_id in self._vertex_to_edges[vertex]:
            hyperedge = self._hyperedges[edge_id]
            connected_vertices.update(hyperedge.get_other_vertices(vertex))
        
        return iter(connected_vertices)
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex (number of connected vertices)."""
        return len(set(self.neighbors(vertex)))
    
    def hyperedge_degree(self, vertex: str) -> int:
        """Get hyperedge degree (number of hyperedges containing vertex)."""
        return len(self._vertex_to_edges.get(vertex, set()))
    
    def edges(self, data: bool = False, include_hyperedges: bool = True) -> Iterator[tuple]:
        """Get all edges/hyperedges."""
        if include_hyperedges:
            # Return hyperedges as (vertices, data)
            for hyperedge in self._hyperedges.values():
                if data:
                    yield (list(hyperedge.vertices), hyperedge.to_dict())
                else:
                    yield (list(hyperedge.vertices),)
        else:
            # Return binary projections
            seen_pairs = set()
            for hyperedge in self._hyperedges.values():
                vertices = list(hyperedge.vertices)
                for i in range(len(vertices)):
                    for j in range(i + 1, len(vertices)):
                        pair = tuple(sorted([vertices[i], vertices[j]]))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            if data:
                                yield (pair[0], pair[1], hyperedge.to_dict())
                            else:
                                yield (pair[0], pair[1])
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get number of hyperedges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all hyperedges and vertices."""
        self._hyperedges.clear()
        self._vertex_to_edges.clear()
        self._vertices.clear()
        
        if self._edges_by_size is not None:
            self._edges_by_size.clear()
        
        self._edge_count = 0
        self._total_connections = 0
        self._max_degree = 0
        self._edge_id_counter = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add an isolated vertex."""
        self._vertices.add(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its hyperedges."""
        if vertex not in self._vertices:
            return False
        
        # Remove all hyperedges containing this vertex
        edge_ids_to_remove = list(self._vertex_to_edges.get(vertex, set()))
        for edge_id in edge_ids_to_remove:
            self.remove_hyperedge(edge_id)
        
        return True
    
    # ============================================================================
    # HYPERGRAPH-SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_hyperedges_containing(self, vertex: str) -> List[HyperEdge]:
        """Get all hyperedges containing a specific vertex."""
        result = []
        for edge_id in self._vertex_to_edges.get(vertex, set()):
            hyperedge = self._hyperedges.get(edge_id)
            if hyperedge:
                result.append(hyperedge)
        return result
    
    def get_hyperedges_by_size(self, size: int) -> List[HyperEdge]:
        """Get all hyperedges of specific size."""
        if self._edges_by_size is None or size not in self._edges_by_size:
            return []
        
        result = []
        for edge_id in self._edges_by_size[size]:
            hyperedge = self._hyperedges.get(edge_id)
            if hyperedge:
                result.append(hyperedge)
        
        return result
    
    def get_k_uniform_subgraph(self, k: int) -> 'xHyperEdgeSetStrategy':
        """Extract k-uniform subgraph (all hyperedges of size k)."""
        subgraph = xHyperEdgeSetStrategy(
            traits=self._traits,
            max_edge_size=self.max_edge_size,
            enable_indexing=self.enable_indexing
        )
        
        for hyperedge in self.get_hyperedges_by_size(k):
            subgraph.add_hyperedge(
                list(hyperedge.vertices), 
                hyperedge.edge_id,
                **hyperedge.properties
            )
        
        return subgraph
    
    def find_maximal_cliques(self) -> List[Set[str]]:
        """Find maximal cliques in the hypergraph."""
        # Simple algorithm - can be optimized
        cliques = []
        
        for hyperedge in self._hyperedges.values():
            # Check if this hyperedge forms a clique
            vertices = list(hyperedge.vertices)
            is_clique = True
            
            # Check all pairs are connected
            for i in range(len(vertices)):
                for j in range(i + 1, len(vertices)):
                    if not self.has_connection(vertices[i], vertices[j]):
                        is_clique = False
                        break
                if not is_clique:
                    break
            
            if is_clique:
                # Check if it's maximal (not contained in existing clique)
                is_maximal = True
                for existing_clique in cliques:
                    if hyperedge.vertices.issubset(existing_clique):
                        is_maximal = False
                        break
                
                if is_maximal:
                    # Remove any cliques that are subsets of this one
                    cliques = [c for c in cliques if not c.issubset(hyperedge.vertices)]
                    cliques.append(set(hyperedge.vertices))
        
        return cliques
    
    def get_incidence_matrix(self) -> Tuple[List[str], List[str], List[List[int]]]:
        """Get incidence matrix representation."""
        vertices = sorted(self._vertices)
        edge_ids = sorted(self._hyperedges.keys())
        
        matrix = []
        for edge_id in edge_ids:
            hyperedge = self._hyperedges[edge_id]
            row = [1 if vertex in hyperedge.vertices else 0 for vertex in vertices]
            matrix.append(row)
        
        return vertices, edge_ids, matrix
    
    def get_vertex_neighborhoods(self, vertex: str, radius: int = 1) -> Set[str]:
        """Get all vertices within given radius from vertex."""
        if radius <= 0 or vertex not in self._vertices:
            return set()
        
        current_level = {vertex}
        all_neighbors = set()
        
        for _ in range(radius):
            next_level = set()
            for v in current_level:
                neighbors = set(self.neighbors(v))
                next_level.update(neighbors)
                all_neighbors.update(neighbors)
            
            current_level = next_level - all_neighbors - {vertex}
            if not current_level:
                break
        
        return all_neighbors
    
    def hypergraph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive hypergraph statistics."""
        if not self._hyperedges:
            return {
                'vertices': 0, 'hyperedges': 0, 'avg_degree': 0,
                'avg_hyperedge_size': 0, 'max_hyperedge_size': 0,
                'min_hyperedge_size': 0, 'uniformity': 0
            }
        
        hyperedge_sizes = [he.size for he in self._hyperedges.values()]
        vertex_degrees = [self.hyperedge_degree(v) for v in self._vertices]
        
        return {
            'vertices': len(self._vertices),
            'hyperedges': self._edge_count,
            'total_connections': self._total_connections,
            'avg_degree': sum(vertex_degrees) / len(vertex_degrees) if vertex_degrees else 0,
            'max_degree': max(vertex_degrees) if vertex_degrees else 0,
            'avg_hyperedge_size': sum(hyperedge_sizes) / len(hyperedge_sizes),
            'max_hyperedge_size': max(hyperedge_sizes),
            'min_hyperedge_size': min(hyperedge_sizes),
            'uniformity': len(set(hyperedge_sizes)) == 1,  # All same size
            'density': self._total_connections / (len(self._vertices) * self._edge_count) if self._vertices and self._edge_count else 0
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        stats = self.hypergraph_statistics()
        
        return {
            'strategy': 'HYPEREDGE_SET',
            'backend': 'Set-based hyperedge storage with vertex indexing',
            'max_edge_size': self.max_edge_size,
            'enable_indexing': self.enable_indexing,
            'track_statistics': self.track_statistics,
            'complexity': {
                'add_hyperedge': 'O(k)',  # k = edge size
                'remove_hyperedge': 'O(k)',
                'has_connection': 'O(degree)',
                'neighbors': 'O(degree * avg_edge_size)',
                'space': 'O(V + E * avg_edge_size)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.hypergraph_statistics()
        
        # Estimate memory usage
        vertex_memory = len(self._vertices) * 50  # Estimated bytes per vertex
        edge_memory = sum(he.size * 30 + 100 for he in self._hyperedges.values())  # Estimated
        index_memory = sum(len(edges) * 8 for edges in self._vertex_to_edges.values())
        
        return {
            'vertices': stats['vertices'],
            'hyperedges': stats['hyperedges'],
            'total_connections': stats['total_connections'],
            'avg_hyperedge_size': f"{stats['avg_hyperedge_size']:.1f}",
            'max_degree': stats['max_degree'],
            'density': f"{stats['density']:.3f}",
            'memory_usage': f"{vertex_memory + edge_memory + index_memory} bytes (estimated)",
            'index_efficiency': f"{len(self._vertex_to_edges) / max(1, len(self._vertices)):.2f}"
        }
