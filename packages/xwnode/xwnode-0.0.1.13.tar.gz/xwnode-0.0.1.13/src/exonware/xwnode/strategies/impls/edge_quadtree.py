"""
Quadtree Edge Strategy Implementation

This module implements the QUADTREE strategy for 2D spatial
graph partitioning and efficient spatial queries.
"""

from typing import Any, Iterator, List, Dict, Set, Optional, Tuple
from collections import defaultdict
import math
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class QuadTreeNode:
    """Node in the quadtree."""
    
    def __init__(self, x: float, y: float, width: float, height: float, capacity: int = 4):
        self.x = x  # Bottom-left corner
        self.y = y
        self.width = width
        self.height = height
        self.capacity = capacity
        
        # Points stored in this node
        self.points: List[Tuple[float, float, str]] = []  # (x, y, vertex_id)
        
        # Child nodes (NW, NE, SW, SE)
        self.children: List[Optional['QuadTreeNode']] = [None, None, None, None]
        self.is_leaf = True
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within this node's bounds."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def intersects_rect(self, rect_x: float, rect_y: float, rect_w: float, rect_h: float) -> bool:
        """Check if this node intersects with given rectangle."""
        return not (rect_x >= self.x + self.width or
                   rect_x + rect_w <= self.x or
                   rect_y >= self.y + self.height or
                   rect_y + rect_h <= self.y)
    
    def subdivide(self) -> None:
        """Subdivide this node into four children."""
        if not self.is_leaf:
            return
        
        half_w = self.width / 2
        half_h = self.height / 2
        
        # Create four children (NW, NE, SW, SE)
        self.children[0] = QuadTreeNode(self.x, self.y + half_h, half_w, half_h, self.capacity)  # NW
        self.children[1] = QuadTreeNode(self.x + half_w, self.y + half_h, half_w, half_h, self.capacity)  # NE
        self.children[2] = QuadTreeNode(self.x, self.y, half_w, half_h, self.capacity)  # SW
        self.children[3] = QuadTreeNode(self.x + half_w, self.y, half_w, half_h, self.capacity)  # SE
        
        self.is_leaf = False
        
        # Redistribute points to children
        for point in self.points:
            x, y, vertex_id = point
            for child in self.children:
                if child and child.contains_point(x, y):
                    child.insert(x, y, vertex_id)
                    break
        
        self.points.clear()
    
    def insert(self, x: float, y: float, vertex_id: str) -> bool:
        """Insert point into quadtree."""
        if not self.contains_point(x, y):
            return False
        
        if self.is_leaf:
            self.points.append((x, y, vertex_id))
            
            # Subdivide if capacity exceeded
            if len(self.points) > self.capacity:
                self.subdivide()
            
            return True
        else:
            # Insert into appropriate child
            for child in self.children:
                if child and child.insert(x, y, vertex_id):
                    return True
            return False
    
    def query_range(self, rect_x: float, rect_y: float, rect_w: float, rect_h: float) -> List[Tuple[float, float, str]]:
        """Query points within given rectangle."""
        result = []
        
        if not self.intersects_rect(rect_x, rect_y, rect_w, rect_h):
            return result
        
        if self.is_leaf:
            for x, y, vertex_id in self.points:
                if rect_x <= x < rect_x + rect_w and rect_y <= y < rect_y + rect_h:
                    result.append((x, y, vertex_id))
        else:
            for child in self.children:
                if child:
                    result.extend(child.query_range(rect_x, rect_y, rect_w, rect_h))
        
        return result
    
    def query_radius(self, center_x: float, center_y: float, radius: float) -> List[Tuple[float, float, str]]:
        """Query points within given radius."""
        # Convert circle to bounding rectangle for initial filtering
        rect_x = center_x - radius
        rect_y = center_y - radius
        rect_w = rect_h = 2 * radius
        
        candidates = self.query_range(rect_x, rect_y, rect_w, rect_h)
        
        # Filter by actual distance
        result = []
        radius_sq = radius * radius
        
        for x, y, vertex_id in candidates:
            dist_sq = (x - center_x) ** 2 + (y - center_y) ** 2
            if dist_sq <= radius_sq:
                result.append((x, y, vertex_id))
        
        return result
    
    def remove(self, x: float, y: float, vertex_id: str) -> bool:
        """Remove point from quadtree."""
        if not self.contains_point(x, y):
            return False
        
        if self.is_leaf:
            for i, point in enumerate(self.points):
                if point[0] == x and point[1] == y and point[2] == vertex_id:
                    del self.points[i]
                    return True
            return False
        else:
            for child in self.children:
                if child and child.remove(x, y, vertex_id):
                    return True
            return False


class xQuadtreeStrategy(aEdgeStrategy):
    """
    Quadtree edge strategy for 2D spatial graphs.
    
    Efficiently manages spatial relationships with logarithmic
    complexity for spatial queries and nearest neighbor searches.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Quadtree strategy."""
        super().__init__(EdgeMode.QUADTREE, traits, **options)
        
        # Spatial bounds
        self.bounds_x = options.get('bounds_x', 0.0)
        self.bounds_y = options.get('bounds_y', 0.0)
        self.bounds_width = options.get('bounds_width', 1000.0)
        self.bounds_height = options.get('bounds_height', 1000.0)
        self.capacity = options.get('capacity', 4)
        
        # Core quadtree
        self._root = QuadTreeNode(self.bounds_x, self.bounds_y, 
                                 self.bounds_width, self.bounds_height, self.capacity)
        
        # Vertex management
        self._vertices: Dict[str, Tuple[float, float]] = {}  # vertex_id -> (x, y)
        self._edges: Dict[Tuple[str, str], Dict[str, Any]] = {}  # (source, target) -> properties
        self._spatial_edges: Set[Tuple[str, str]] = set()  # Edges based on spatial proximity
        
        # Performance tracking
        self._edge_count = 0
        self._spatial_threshold = options.get('spatial_threshold', 50.0)  # Auto-connect distance
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the quadtree strategy."""
        return (EdgeTrait.SPATIAL | EdgeTrait.SPARSE | EdgeTrait.CACHE_FRIENDLY)
    
    def _auto_connect_spatial(self, vertex: str, x: float, y: float) -> None:
        """Automatically connect vertex to nearby vertices."""
        if self._spatial_threshold <= 0:
            return
        
        # Find nearby vertices
        nearby = self._root.query_radius(x, y, self._spatial_threshold)
        
        for nx, ny, neighbor_id in nearby:
            if neighbor_id != vertex:
                # Calculate distance
                distance = math.sqrt((x - nx) ** 2 + (y - ny) ** 2)
                
                # Add spatial edge
                edge_key = (min(vertex, neighbor_id), max(vertex, neighbor_id))
                if edge_key not in self._edges:
                    self._edges[edge_key] = {
                        'distance': distance,
                        'spatial': True,
                        'weight': 1.0 / (1.0 + distance)  # Inverse distance weight
                    }
                    self._spatial_edges.add(edge_key)
                    self._edge_count += 1
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add edge between spatial vertices."""
        # Ensure vertices exist with positions
        if source not in self._vertices:
            # Assign random position if not specified
            x = properties.get('source_x', self.bounds_x + self.bounds_width * 0.5)
            y = properties.get('source_y', self.bounds_y + self.bounds_height * 0.5)
            self.add_spatial_vertex(source, x, y)
        
        if target not in self._vertices:
            x = properties.get('target_x', self.bounds_x + self.bounds_width * 0.5)
            y = properties.get('target_y', self.bounds_y + self.bounds_height * 0.5)
            self.add_spatial_vertex(target, x, y)
        
        # Calculate distance
        sx, sy = self._vertices[source]
        tx, ty = self._vertices[target]
        distance = math.sqrt((sx - tx) ** 2 + (sy - ty) ** 2)
        
        # Add edge
        edge_key = (min(source, target), max(source, target))
        self._edges[edge_key] = {
            'distance': distance,
            'spatial': properties.get('spatial', False),
            'weight': properties.get('weight', 1.0),
            **properties
        }
        
        if edge_key not in self._spatial_edges:
            self._edge_count += 1
        
        return f"{source}<->{target}"
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge between vertices."""
        edge_key = (min(source, target), max(source, target))
        
        if edge_key in self._edges:
            del self._edges[edge_key]
            self._spatial_edges.discard(edge_key)
            self._edge_count -= 1
            return True
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        edge_key = (min(source, target), max(source, target))
        return edge_key in self._edges
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        edge_key = (min(source, target), max(source, target))
        return self._edges.get(edge_key)
    
    def neighbors(self, vertex: str, direction: str = 'both') -> Iterator[str]:
        """Get neighbors of vertex."""
        for (v1, v2) in self._edges:
            if v1 == vertex:
                yield v2
            elif v2 == vertex:
                yield v1
    
    def degree(self, vertex: str, direction: str = 'both') -> int:
        """Get degree of vertex."""
        return len(list(self.neighbors(vertex, direction)))
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for (source, target), edge_data in self._edges.items():
            if data:
                yield (source, target, edge_data)
            else:
                yield (source, target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices.keys())
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all data."""
        self._root = QuadTreeNode(self.bounds_x, self.bounds_y, 
                                 self.bounds_width, self.bounds_height, self.capacity)
        self._vertices.clear()
        self._edges.clear()
        self._spatial_edges.clear()
        self._edge_count = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex at random position."""
        if vertex not in self._vertices:
            # Random position within bounds
            import random
            x = self.bounds_x + random.random() * self.bounds_width
            y = self.bounds_y + random.random() * self.bounds_height
            self.add_spatial_vertex(vertex, x, y)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._vertices:
            return False
        
        # Remove from quadtree
        x, y = self._vertices[vertex]
        self._root.remove(x, y, vertex)
        
        # Remove all edges
        edges_to_remove = []
        for (v1, v2) in self._edges:
            if v1 == vertex or v2 == vertex:
                edges_to_remove.append((v1, v2))
        
        for edge_key in edges_to_remove:
            del self._edges[edge_key]
            self._spatial_edges.discard(edge_key)
            self._edge_count -= 1
        
        # Remove vertex
        del self._vertices[vertex]
        return True
    
    # ============================================================================
    # SPATIAL OPERATIONS
    # ============================================================================
    
    def add_spatial_vertex(self, vertex: str, x: float, y: float) -> None:
        """Add vertex at specific spatial position."""
        # Remove old position if exists
        if vertex in self._vertices:
            old_x, old_y = self._vertices[vertex]
            self._root.remove(old_x, old_y, vertex)
        
        # Add to quadtree
        self._vertices[vertex] = (x, y)
        self._root.insert(x, y, vertex)
        
        # Auto-connect to nearby vertices
        self._auto_connect_spatial(vertex, x, y)
    
    def get_vertex_position(self, vertex: str) -> Optional[Tuple[float, float]]:
        """Get vertex position."""
        return self._vertices.get(vertex)
    
    def set_vertex_position(self, vertex: str, x: float, y: float) -> None:
        """Update vertex position."""
        self.add_spatial_vertex(vertex, x, y)
    
    def query_range(self, x: float, y: float, width: float, height: float) -> List[str]:
        """Query vertices within rectangular range."""
        points = self._root.query_range(x, y, width, height)
        return [vertex_id for _, _, vertex_id in points]
    
    def query_radius(self, center_x: float, center_y: float, radius: float) -> List[str]:
        """Query vertices within circular range."""
        points = self._root.query_radius(center_x, center_y, radius)
        return [vertex_id for _, _, vertex_id in points]
    
    def nearest_neighbors(self, vertex: str, k: int = 1) -> List[Tuple[str, float]]:
        """Find k nearest neighbors to vertex."""
        if vertex not in self._vertices:
            return []
        
        x, y = self._vertices[vertex]
        
        # Query expanding radius until we have enough candidates
        radius = 10.0
        candidates = []
        
        while len(candidates) < k * 2 and radius <= self.bounds_width:
            candidates = self.query_radius(x, y, radius)
            candidates = [v for v in candidates if v != vertex]
            radius *= 2
        
        # Calculate distances and sort
        distances = []
        for neighbor in candidates:
            nx, ny = self._vertices[neighbor]
            dist = math.sqrt((x - nx) ** 2 + (y - ny) ** 2)
            distances.append((neighbor, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]
    
    def get_spatial_edges_in_range(self, x: float, y: float, width: float, height: float) -> List[Tuple[str, str]]:
        """Get edges where both vertices are in given range."""
        vertices_in_range = set(self.query_range(x, y, width, height))
        
        spatial_edges = []
        for (v1, v2) in self._edges:
            if v1 in vertices_in_range and v2 in vertices_in_range:
                spatial_edges.append((v1, v2))
        
        return spatial_edges
    
    def cluster_vertices(self, max_distance: float) -> List[List[str]]:
        """Cluster vertices based on spatial proximity."""
        visited = set()
        clusters = []
        
        for vertex in self._vertices:
            if vertex in visited:
                continue
            
            # Start new cluster
            cluster = []
            stack = [vertex]
            
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                
                visited.add(current)
                cluster.append(current)
                
                # Find nearby vertices
                x, y = self._vertices[current]
                nearby = self.query_radius(x, y, max_distance)
                
                for neighbor in nearby:
                    if neighbor not in visited:
                        stack.append(neighbor)
            
            if cluster:
                clusters.append(cluster)
        
        return clusters
    
    def get_spatial_statistics(self) -> Dict[str, Any]:
        """Get comprehensive spatial statistics."""
        if not self._vertices:
            return {'vertices': 0, 'edges': 0, 'spatial_density': 0}
        
        # Calculate spatial extent
        positions = list(self._vertices.values())
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions)
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions)
        
        spatial_area = (max_x - min_x) * (max_y - min_y) if len(positions) > 1 else 0
        vertex_density = len(self._vertices) / max(1, spatial_area)
        
        # Edge length statistics
        edge_lengths = []
        for (v1, v2), edge_data in self._edges.items():
            edge_lengths.append(edge_data.get('distance', 0))
        
        avg_edge_length = sum(edge_lengths) / len(edge_lengths) if edge_lengths else 0
        max_edge_length = max(edge_lengths) if edge_lengths else 0
        min_edge_length = min(edge_lengths) if edge_lengths else 0
        
        return {
            'vertices': len(self._vertices),
            'edges': self._edge_count,
            'spatial_edges': len(self._spatial_edges),
            'spatial_extent': (max_x - min_x, max_y - min_y),
            'spatial_area': spatial_area,
            'vertex_density': vertex_density,
            'avg_edge_length': avg_edge_length,
            'min_edge_length': min_edge_length,
            'max_edge_length': max_edge_length,
            'spatial_threshold': self._spatial_threshold,
            'quadtree_capacity': self.capacity
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'QUADTREE',
            'backend': '2D spatial partitioning with quadtree',
            'bounds': f"({self.bounds_x}, {self.bounds_y}, {self.bounds_width}, {self.bounds_height})",
            'capacity': self.capacity,
            'spatial_threshold': self._spatial_threshold,
            'complexity': {
                'insert': 'O(log n)',
                'remove': 'O(log n)',
                'range_query': 'O(log n + k)',  # k = results
                'nearest_neighbor': 'O(log n + k)',
                'space': 'O(n)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_spatial_statistics()
        
        return {
            'vertices': stats['vertices'],
            'edges': stats['edges'],
            'spatial_edges': stats['spatial_edges'],
            'vertex_density': f"{stats['vertex_density']:.2f}",
            'avg_edge_length': f"{stats['avg_edge_length']:.1f}",
            'spatial_area': f"{stats['spatial_area']:.1f}",
            'memory_usage': f"{self._edge_count * 80 + len(self._vertices) * 100} bytes (estimated)"
        }
