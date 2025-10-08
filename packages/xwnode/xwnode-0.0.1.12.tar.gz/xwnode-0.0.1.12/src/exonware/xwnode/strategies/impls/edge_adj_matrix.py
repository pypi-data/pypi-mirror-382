"""
Adjacency Matrix Edge Strategy Implementation

This module implements the ADJ_MATRIX strategy for dense graph representation
with O(1) edge operations and efficient matrix-based algorithms.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, Union
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class xAdjMatrixStrategy(aEdgeStrategy):
    """
    Adjacency Matrix edge strategy for dense graph representation.
    
    Provides O(1) edge operations and efficient matrix-based graph algorithms,
    ideal for dense graphs where most vertices are connected.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Adjacency Matrix strategy."""
        super().__init__(EdgeMode.ADJ_MATRIX, traits, **options)
        
        self.is_directed = options.get('directed', True)
        self.initial_capacity = options.get('initial_capacity', 100)
        self.allow_self_loops = options.get('self_loops', True)
        self.default_weight = options.get('default_weight', 1.0)
        
        # Core storage: 2D matrix of edge weights/properties
        self._matrix: List[List[Optional[Dict[str, Any]]]] = []
        self._capacity = 0
        
        # Vertex management
        self._vertex_to_index: Dict[str, int] = {}
        self._index_to_vertex: Dict[int, str] = {}
        self._vertex_count = 0
        self._edge_count = 0
        self._edge_id_counter = 0
        
        # Initialize matrix
        self._resize_matrix(self.initial_capacity)
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the adjacency matrix strategy."""
        return (EdgeTrait.DENSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.CACHE_FRIENDLY)
    
    # ============================================================================
    # MATRIX MANAGEMENT
    # ============================================================================
    
    def _resize_matrix(self, new_capacity: int) -> None:
        """Resize the adjacency matrix to accommodate more vertices."""
        old_capacity = self._capacity
        self._capacity = new_capacity
        
        # Expand existing rows
        for row in self._matrix:
            row.extend([None] * (new_capacity - old_capacity))
        
        # Add new rows
        for _ in range(old_capacity, new_capacity):
            self._matrix.append([None] * new_capacity)
    
    def _get_vertex_index(self, vertex: str) -> int:
        """Get or create index for vertex."""
        if vertex in self._vertex_to_index:
            return self._vertex_to_index[vertex]
        
        # Need to add new vertex
        if self._vertex_count >= self._capacity:
            self._resize_matrix(self._capacity * 2)
        
        index = self._vertex_count
        self._vertex_to_index[vertex] = index
        self._index_to_vertex[index] = vertex
        self._vertex_count += 1
        
        return index
    
    def _get_vertex_by_index(self, index: int) -> Optional[str]:
        """Get vertex name by index."""
        return self._index_to_vertex.get(index)
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add an edge between source and target vertices."""
        # Validate self-loops
        if source == target and not self.allow_self_loops:
            raise ValueError(f"Self-loops not allowed: {source} -> {target}")
        
        # Get vertex indices
        source_idx = self._get_vertex_index(source)
        target_idx = self._get_vertex_index(target)
        
        # Generate edge ID
        edge_id = f"edge_{self._edge_id_counter}"
        self._edge_id_counter += 1
        
        # Create edge data
        edge_data = {
            'id': edge_id,
            'source': source,
            'target': target,
            'weight': properties.get('weight', self.default_weight),
            'properties': properties.copy()
        }
        
        # Check if edge already exists
        if self._matrix[source_idx][target_idx] is not None:
            # Update existing edge
            self._matrix[source_idx][target_idx] = edge_data
        else:
            # Add new edge
            self._matrix[source_idx][target_idx] = edge_data
            self._edge_count += 1
        
        # For undirected graphs, add symmetric edge
        if not self.is_directed and source != target:
            if self._matrix[target_idx][source_idx] is None:
                self._matrix[target_idx][source_idx] = edge_data
                # Don't increment edge count for undirected (it's the same edge)
    
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge between source and target."""
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return False
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        # Check if edge exists
        if self._matrix[source_idx][target_idx] is None:
            return False
        
        # If edge_id specified, verify it matches
        if edge_id and self._matrix[source_idx][target_idx]['id'] != edge_id:
            return False
        
        # Remove edge
        self._matrix[source_idx][target_idx] = None
        self._edge_count -= 1
        
        # For undirected graphs, remove symmetric edge
        if not self.is_directed and source != target:
            self._matrix[target_idx][source_idx] = None
        
        return True
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between source and target."""
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return False
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        return self._matrix[source_idx][target_idx] is not None
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data between source and target."""
        if source not in self._vertex_to_index or target not in self._vertex_to_index:
            return None
        
        source_idx = self._vertex_to_index[source]
        target_idx = self._vertex_to_index[target]
        
        return self._matrix[source_idx][target_idx]
    
    def get_edge_weight(self, source: str, target: str) -> Optional[float]:
        """Get edge weight between source and target."""
        edge_data = self.get_edge_data(source, target)
        return edge_data['weight'] if edge_data else None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of a vertex."""
        if vertex not in self._vertex_to_index:
            return
        
        vertex_idx = self._vertex_to_index[vertex]
        
        if direction == 'out':
            # Outgoing neighbors (columns)
            for target_idx in range(self._vertex_count):
                if self._matrix[vertex_idx][target_idx] is not None:
                    yield self._index_to_vertex[target_idx]
        elif direction == 'in':
            # Incoming neighbors (rows)
            for source_idx in range(self._vertex_count):
                if self._matrix[source_idx][vertex_idx] is not None:
                    yield self._index_to_vertex[source_idx]
        elif direction == 'both':
            # All neighbors
            seen = set()
            for neighbor in self.neighbors(vertex, 'out'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    yield neighbor
            for neighbor in self.neighbors(vertex, 'in'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    yield neighbor
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of a vertex."""
        if vertex not in self._vertex_to_index:
            return 0
        
        vertex_idx = self._vertex_to_index[vertex]
        
        if direction == 'out':
            # Count non-None entries in row
            return sum(1 for target_idx in range(self._vertex_count) 
                      if self._matrix[vertex_idx][target_idx] is not None)
        elif direction == 'in':
            # Count non-None entries in column
            return sum(1 for source_idx in range(self._vertex_count) 
                      if self._matrix[source_idx][vertex_idx] is not None)
        elif direction == 'both':
            out_degree = self.degree(vertex, 'out')
            in_degree = self.degree(vertex, 'in')
            # For undirected graphs, avoid double counting
            return out_degree if not self.is_directed else out_degree + in_degree
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges in the graph."""
        for source_idx in range(self._vertex_count):
            for target_idx in range(self._vertex_count):
                edge_data = self._matrix[source_idx][target_idx]
                if edge_data is not None:
                    source = self._index_to_vertex[source_idx]
                    target = self._index_to_vertex[target_idx]
                    
                    # For undirected graphs, avoid returning duplicate edges
                    if not self.is_directed and source > target:
                        continue
                    
                    if data:
                        yield (source, target, edge_data)
                    else:
                        yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices in the graph."""
        for vertex in self._vertex_to_index.keys():
            yield vertex
    
    def __len__(self) -> int:
        """Get the number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return self._vertex_count
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        # Reset matrix
        for row in self._matrix:
            for i in range(len(row)):
                row[i] = None
        
        # Reset mappings
        self._vertex_to_index.clear()
        self._index_to_vertex.clear()
        self._vertex_count = 0
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph."""
        if vertex not in self._vertex_to_index:
            self._get_vertex_index(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and all its edges."""
        if vertex not in self._vertex_to_index:
            return False
        
        vertex_idx = self._vertex_to_index[vertex]
        
        # Count and remove all edges involving this vertex
        edges_removed = 0
        
        # Remove outgoing edges (row)
        for target_idx in range(self._vertex_count):
            if self._matrix[vertex_idx][target_idx] is not None:
                self._matrix[vertex_idx][target_idx] = None
                edges_removed += 1
        
        # Remove incoming edges (column)
        for source_idx in range(self._vertex_count):
            if source_idx != vertex_idx and self._matrix[source_idx][vertex_idx] is not None:
                self._matrix[source_idx][vertex_idx] = None
                edges_removed += 1
        
        self._edge_count -= edges_removed
        
        # Note: We don't actually remove the vertex from the matrix to avoid
        # reindexing all other vertices. Instead, we just mark it as removed.
        del self._vertex_to_index[vertex]
        del self._index_to_vertex[vertex_idx]
        
        return True
    
    # ============================================================================
    # MATRIX-SPECIFIC OPERATIONS
    # ============================================================================
    
    def get_matrix(self) -> List[List[Optional[float]]]:
        """Get the adjacency matrix as weights."""
        matrix = []
        for source_idx in range(self._vertex_count):
            row = []
            for target_idx in range(self._vertex_count):
                edge_data = self._matrix[source_idx][target_idx]
                weight = edge_data['weight'] if edge_data else None
                row.append(weight)
            matrix.append(row)
        return matrix
    
    def get_binary_matrix(self) -> List[List[int]]:
        """Get the adjacency matrix as binary (0/1)."""
        matrix = []
        for source_idx in range(self._vertex_count):
            row = []
            for target_idx in range(self._vertex_count):
                edge_exists = self._matrix[source_idx][target_idx] is not None
                row.append(1 if edge_exists else 0)
            matrix.append(row)
        return matrix
    
    def set_matrix(self, matrix: List[List[Union[float, int, None]]], vertices: List[str]) -> None:
        """Set the entire matrix from a weight matrix."""
        if len(matrix) != len(vertices) or any(len(row) != len(vertices) for row in matrix):
            raise ValueError("Matrix dimensions must match vertex count")
        
        # Clear existing data
        self.clear()
        
        # Add vertices
        for vertex in vertices:
            self.add_vertex(vertex)
        
        # Add edges based on matrix
        for i, source in enumerate(vertices):
            for j, target in enumerate(vertices):
                weight = matrix[i][j]
                if weight is not None and weight != 0:
                    self.add_edge(source, target, weight=weight)
    
    def matrix_multiply(self, other: 'xAdjMatrixStrategy') -> 'xAdjMatrixStrategy':
        """Multiply this matrix with another adjacency matrix."""
        if self._vertex_count != other._vertex_count:
            raise ValueError("Matrices must have same dimensions")
        
        result = xAdjMatrixStrategy(
            traits=self._traits,
            directed=self.is_directed,
            initial_capacity=self._vertex_count
        )
        
        # Add vertices
        for vertex in self.vertices():
            result.add_vertex(vertex)
        
        # Perform matrix multiplication
        vertices = list(self.vertices())
        for i, source in enumerate(vertices):
            for j, target in enumerate(vertices):
                sum_value = 0
                for k in range(self._vertex_count):
                    intermediate = self._index_to_vertex[k]
                    
                    weight1 = self.get_edge_weight(source, intermediate)
                    weight2 = other.get_edge_weight(intermediate, target)
                    
                    if weight1 is not None and weight2 is not None:
                        sum_value += weight1 * weight2
                
                if sum_value != 0:
                    result.add_edge(source, target, weight=sum_value)
        
        return result
    
    def transpose(self) -> 'xAdjMatrixStrategy':
        """Get the transpose of this matrix."""
        result = xAdjMatrixStrategy(
            traits=self._traits,
            directed=True,  # Transpose is always directed
            initial_capacity=self._vertex_count
        )
        
        # Add vertices
        for vertex in self.vertices():
            result.add_vertex(vertex)
        
        # Add transposed edges
        for source, target, edge_data in self.edges(data=True):
            result.add_edge(target, source, **edge_data['properties'])
        
        return result
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'ADJ_MATRIX',
            'backend': 'Python 2D list matrix',
            'directed': self.is_directed,
            'capacity': self._capacity,
            'utilized': self._vertex_count,
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(1)',
                'has_edge': 'O(1)',
                'neighbors': 'O(V)',
                'space': 'O(V²)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        density = self._edge_count / max(1, self._vertex_count * (self._vertex_count - 1)) if self._vertex_count > 1 else 0
        memory_utilization = self._vertex_count / max(1, self._capacity) * 100
        
        return {
            'vertices': self._vertex_count,
            'edges': self._edge_count,
            'matrix_capacity': self._capacity,
            'memory_utilization': f"{memory_utilization:.1f}%",
            'density': round(density, 4),
            'memory_usage': f"{self._capacity * self._capacity * 8} bytes (estimated)",
            'sparsity': f"{(1 - density) * 100:.1f}%"
        }
