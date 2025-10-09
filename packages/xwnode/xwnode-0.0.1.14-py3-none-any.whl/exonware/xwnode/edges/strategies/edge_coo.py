"""
COO (Coordinate) Edge Strategy Implementation

This module implements the COO strategy for sparse graph representation
using coordinate format for efficient sparse matrix operations and conversions.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import defaultdict
import bisect
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class xCOOStrategy(aEdgeStrategy):
    """
    COO (Coordinate) edge strategy for sparse graphs.
    
    Stores edges as coordinate triplets (row, col, value) for efficient
    sparse matrix operations and easy conversion to other formats.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the COO strategy."""
        super().__init__(EdgeMode.COO, traits, **options)
        
        self.weighted = options.get('weighted', True)
        self.allow_duplicates = options.get('allow_duplicates', True)
        self.sort_coordinates = options.get('sort_coordinates', True)
        
        # COO format: three parallel arrays
        self._row_indices: List[int] = []  # Row indices
        self._col_indices: List[int] = []  # Column indices
        self._values: List[float] = []     # Edge values/weights
        
        # Vertex management
        self._vertices: Set[str] = set()
        self._vertex_to_id: Dict[str, int] = {}
        self._id_to_vertex: Dict[int, str] = {}
        self._next_vertex_id = 0
        
        # Matrix dimensions and metadata
        self._num_rows = 0
        self._num_cols = 0
        self._nnz = 0  # Number of non-zeros
        self._is_sorted = True
        
        # Quick access structures
        self._edge_count = 0
        self._coordinate_index: Dict[Tuple[int, int], List[int]] = defaultdict(list)  # (row, col) -> [positions]
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the COO strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.COMPRESSED | EdgeTrait.MULTI)
    
    def _get_or_create_vertex_id(self, vertex: str) -> int:
        """Get or create vertex ID."""
        if vertex not in self._vertex_to_id:
            vertex_id = self._next_vertex_id
            self._vertex_to_id[vertex] = vertex_id
            self._id_to_vertex[vertex_id] = vertex
            self._vertices.add(vertex)
            self._next_vertex_id += 1
            return vertex_id
        return self._vertex_to_id[vertex]
    
    def _update_dimensions(self, row: int, col: int) -> None:
        """Update matrix dimensions."""
        self._num_rows = max(self._num_rows, row + 1)
        self._num_cols = max(self._num_cols, col + 1)
    
    def _add_coordinate(self, row: int, col: int, value: float) -> None:
        """Add coordinate to COO format."""
        position = len(self._row_indices)
        
        self._row_indices.append(row)
        self._col_indices.append(col)
        self._values.append(value)
        
        # Update coordinate index
        coord_key = (row, col)
        self._coordinate_index[coord_key].append(position)
        
        self._nnz += 1
        self._is_sorted = False
        self._update_dimensions(row, col)
    
    def _remove_coordinate_at_position(self, position: int) -> None:
        """Remove coordinate at specific position."""
        if 0 <= position < len(self._row_indices):
            row = self._row_indices[position]
            col = self._col_indices[position]
            
            # Remove from arrays
            del self._row_indices[position]
            del self._col_indices[position]
            del self._values[position]
            
            # Update coordinate index
            coord_key = (row, col)
            self._coordinate_index[coord_key].remove(position)
            if not self._coordinate_index[coord_key]:
                del self._coordinate_index[coord_key]
            
            # Update positions in coordinate index
            for key, positions in self._coordinate_index.items():
                for i, pos in enumerate(positions):
                    if pos > position:
                        positions[i] = pos - 1
            
            self._nnz -= 1
            self._is_sorted = False
    
    def _sort_coordinates(self) -> None:
        """Sort coordinates by (row, col)."""
        if self._is_sorted or self._nnz == 0:
            return
        
        # Create list of (row, col, value, original_index) tuples
        coords = list(zip(self._row_indices, self._col_indices, self._values, range(self._nnz)))
        
        # Sort by (row, col)
        coords.sort(key=lambda x: (x[0], x[1]))
        
        # Rebuild arrays
        self._row_indices = [coord[0] for coord in coords]
        self._col_indices = [coord[1] for coord in coords]
        self._values = [coord[2] for coord in coords]
        
        # Rebuild coordinate index
        self._coordinate_index.clear()
        for i, (row, col, _, _) in enumerate(coords):
            coord_key = (row, col)
            self._coordinate_index[coord_key].append(i)
        
        self._is_sorted = True
    
    def _find_coordinate_positions(self, row: int, col: int) -> List[int]:
        """Find all positions of coordinate (row, col)."""
        coord_key = (row, col)
        return self._coordinate_index.get(coord_key, [])
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge to COO matrix."""
        row_id = self._get_or_create_vertex_id(source)
        col_id = self._get_or_create_vertex_id(target)
        
        weight = properties.get('weight', 1.0) if self.weighted else 1.0
        
        # Check for existing edge
        positions = self._find_coordinate_positions(row_id, col_id)
        
        if positions and not self.allow_duplicates:
            # Update existing edge (use first occurrence)
            self._values[positions[0]] = weight
            return f"{source}->{target}"
        
        # Add new coordinate
        self._add_coordinate(row_id, col_id, weight)
        self._edge_count += 1
        
        return f"{source}->{target}"
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge from COO matrix."""
        if source not in self._vertex_to_id or target not in self._vertex_to_id:
            return False
        
        row_id = self._vertex_to_id[source]
        col_id = self._vertex_to_id[target]
        
        positions = self._find_coordinate_positions(row_id, col_id)
        
        if positions:
            # Remove first occurrence
            self._remove_coordinate_at_position(positions[0])
            self._edge_count -= 1
            return True
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        if source not in self._vertex_to_id or target not in self._vertex_to_id:
            return False
        
        row_id = self._vertex_to_id[source]
        col_id = self._vertex_to_id[target]
        
        return len(self._find_coordinate_positions(row_id, col_id)) > 0
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        if not self.has_edge(source, target):
            return None
        
        row_id = self._vertex_to_id[source]
        col_id = self._vertex_to_id[target]
        positions = self._find_coordinate_positions(row_id, col_id)
        
        if positions:
            value = self._values[positions[0]]
            return {
                'source': source,
                'target': target,
                'weight': value,
                'row_id': row_id,
                'col_id': col_id,
                'duplicates': len(positions) - 1
            }
        
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of vertex."""
        if vertex not in self._vertex_to_id:
            return
        
        vertex_id = self._vertex_to_id[vertex]
        neighbors_found = set()
        
        if direction in ['out', 'both']:
            # Outgoing: vertex is source (row)
            for i in range(self._nnz):
                if self._row_indices[i] == vertex_id:
                    col_id = self._col_indices[i]
                    neighbor = self._id_to_vertex.get(col_id)
                    if neighbor and neighbor not in neighbors_found:
                        neighbors_found.add(neighbor)
                        yield neighbor
        
        if direction in ['in', 'both']:
            # Incoming: vertex is target (column)
            for i in range(self._nnz):
                if self._col_indices[i] == vertex_id:
                    row_id = self._row_indices[i]
                    neighbor = self._id_to_vertex.get(row_id)
                    if neighbor and neighbor not in neighbors_found:
                        neighbors_found.add(neighbor)
                        yield neighbor
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex."""
        return len(list(self.neighbors(vertex, direction)))
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for i in range(self._nnz):
            row_id = self._row_indices[i]
            col_id = self._col_indices[i]
            
            source = self._id_to_vertex.get(row_id)
            target = self._id_to_vertex.get(col_id)
            
            if source and target:
                if data:
                    edge_data = {
                        'weight': self._values[i],
                        'row_id': row_id,
                        'col_id': col_id,
                        'position': i
                    }
                    yield (source, target, edge_data)
                else:
                    yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all data."""
        self._row_indices.clear()
        self._col_indices.clear()
        self._values.clear()
        self._vertices.clear()
        self._vertex_to_id.clear()
        self._id_to_vertex.clear()
        self._coordinate_index.clear()
        
        self._num_rows = 0
        self._num_cols = 0
        self._nnz = 0
        self._edge_count = 0
        self._next_vertex_id = 0
        self._is_sorted = True
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex to graph."""
        self._get_or_create_vertex_id(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertex_to_id:
            return False
        
        vertex_id = self._vertex_to_id[vertex]
        
        # Remove all coordinates involving this vertex
        positions_to_remove = []
        for i in range(self._nnz):
            if self._row_indices[i] == vertex_id or self._col_indices[i] == vertex_id:
                positions_to_remove.append(i)
        
        # Remove in reverse order to maintain indices
        for pos in reversed(positions_to_remove):
            self._remove_coordinate_at_position(pos)
            self._edge_count -= 1
        
        # Remove vertex
        del self._vertex_to_id[vertex]
        del self._id_to_vertex[vertex_id]
        self._vertices.remove(vertex)
        
        return True
    
    # ============================================================================
    # COO SPECIFIC OPERATIONS
    # ============================================================================
    
    def sort(self) -> None:
        """Sort coordinates by (row, col)."""
        self._sort_coordinates()
    
    def get_coordinates(self) -> Tuple[List[int], List[int], List[float]]:
        """Get COO coordinate arrays."""
        if self.sort_coordinates:
            self._sort_coordinates()
        return (self._row_indices.copy(), self._col_indices.copy(), self._values.copy())
    
    def sum_duplicates(self) -> None:
        """Sum duplicate coordinates."""
        if self._nnz == 0:
            return
        
        self._sort_coordinates()
        
        # Track unique coordinates and their sums
        unique_coords = {}
        for i in range(self._nnz):
            coord_key = (self._row_indices[i], self._col_indices[i])
            if coord_key in unique_coords:
                unique_coords[coord_key] += self._values[i]
            else:
                unique_coords[coord_key] = self._values[i]
        
        # Rebuild arrays
        self._row_indices.clear()
        self._col_indices.clear()
        self._values.clear()
        self._coordinate_index.clear()
        
        for (row, col), value in unique_coords.items():
            self._row_indices.append(row)
            self._col_indices.append(col)
            self._values.append(value)
            
            coord_key = (row, col)
            position = len(self._row_indices) - 1
            self._coordinate_index[coord_key].append(position)
        
        self._nnz = len(self._row_indices)
        self._edge_count = self._nnz
        self._is_sorted = True
    
    def eliminate_zeros(self, tolerance: float = 1e-12) -> None:
        """Remove coordinates with zero or near-zero values."""
        positions_to_remove = []
        
        for i in range(self._nnz):
            if abs(self._values[i]) <= tolerance:
                positions_to_remove.append(i)
        
        # Remove in reverse order
        for pos in reversed(positions_to_remove):
            self._remove_coordinate_at_position(pos)
            self._edge_count -= 1
    
    def to_dense_matrix(self) -> List[List[float]]:
        """Convert to dense matrix representation."""
        if self._num_rows == 0 or self._num_cols == 0:
            return []
        
        # Initialize dense matrix with zeros
        matrix = [[0.0 for _ in range(self._num_cols)] for _ in range(self._num_rows)]
        
        # Fill with values
        for i in range(self._nnz):
            row = self._row_indices[i]
            col = self._col_indices[i]
            matrix[row][col] = self._values[i]
        
        return matrix
    
    def transpose(self) -> 'xCOOStrategy':
        """Create transposed COO matrix."""
        transposed = xCOOStrategy(
            traits=self._traits,
            weighted=self.weighted,
            allow_duplicates=self.allow_duplicates,
            sort_coordinates=self.sort_coordinates
        )
        
        # Copy vertex mappings
        transposed._vertices = self._vertices.copy()
        transposed._vertex_to_id = self._vertex_to_id.copy()
        transposed._id_to_vertex = self._id_to_vertex.copy()
        transposed._next_vertex_id = self._next_vertex_id
        
        # Transpose coordinates (swap row and col)
        for i in range(self._nnz):
            col = self._row_indices[i]  # Swapped
            row = self._col_indices[i]  # Swapped
            value = self._values[i]
            
            transposed._add_coordinate(row, col, value)
        
        transposed._edge_count = self._edge_count
        transposed._num_rows = self._num_cols  # Swapped
        transposed._num_cols = self._num_rows  # Swapped
        
        return transposed
    
    def get_sparsity(self) -> float:
        """Get sparsity ratio."""
        total_entries = self._num_rows * self._num_cols
        if total_entries == 0:
            return 0.0
        return 1.0 - (self._nnz / total_entries)
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get detailed memory usage."""
        return {
            'row_indices_bytes': len(self._row_indices) * 4,  # 4 bytes per int
            'col_indices_bytes': len(self._col_indices) * 4,
            'values_bytes': len(self._values) * 8,  # 8 bytes per float
            'coordinate_index_bytes': len(self._coordinate_index) * 50,  # Estimated
            'vertex_mapping_bytes': len(self._vertices) * 50,
            'total_bytes': len(self._row_indices) * 4 + len(self._col_indices) * 4 + len(self._values) * 8 + len(self._coordinate_index) * 50 + len(self._vertices) * 50
        }
    
    def export_matrix(self) -> Dict[str, Any]:
        """Export COO matrix data."""
        return {
            'row_indices': self._row_indices.copy(),
            'col_indices': self._col_indices.copy(),
            'values': self._values.copy(),
            'vertex_to_id': self._vertex_to_id.copy(),
            'id_to_vertex': self._id_to_vertex.copy(),
            'dimensions': (self._num_rows, self._num_cols),
            'nnz': self._nnz,
            'is_sorted': self._is_sorted
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive COO statistics."""
        memory = self.get_memory_usage()
        
        # Calculate duplicate statistics
        unique_coords = set()
        total_duplicates = 0
        for i in range(self._nnz):
            coord = (self._row_indices[i], self._col_indices[i])
            if coord in unique_coords:
                total_duplicates += 1
            else:
                unique_coords.add(coord)
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'matrix_dimensions': (self._num_rows, self._num_cols),
            'nnz': self._nnz,
            'unique_coordinates': len(unique_coords),
            'duplicate_coordinates': total_duplicates,
            'sparsity': self.get_sparsity(),
            'density': 1.0 - self.get_sparsity(),
            'is_sorted': self._is_sorted,
            'memory_usage': memory['total_bytes'],
            'weighted': self.weighted,
            'allow_duplicates': self.allow_duplicates
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'COO',
            'backend': 'Coordinate format with three parallel arrays',
            'weighted': self.weighted,
            'allow_duplicates': self.allow_duplicates,
            'sort_coordinates': self.sort_coordinates,
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(nnz)',  # Need to find and shift
                'has_edge': 'O(nnz)',    # Linear search if unsorted
                'sort': 'O(nnz log nnz)',
                'sum_duplicates': 'O(nnz log nnz)',
                'space': 'O(nnz)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_statistics()
        
        return {
            'vertices': stats['vertices'],
            'edges': stats['edges'],
            'nnz': stats['nnz'],
            'matrix_size': f"{stats['matrix_dimensions'][0]}x{stats['matrix_dimensions'][1]}",
            'sparsity': f"{stats['sparsity'] * 100:.1f}%",
            'duplicates': stats['duplicate_coordinates'],
            'sorted': stats['is_sorted'],
            'memory_usage': f"{stats['memory_usage']} bytes"
        }
