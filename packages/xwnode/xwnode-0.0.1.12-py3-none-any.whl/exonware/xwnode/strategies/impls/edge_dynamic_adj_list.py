"""
Dynamic Adjacency List Edge Strategy Implementation

This module implements the DYNAMIC_ADJ_LIST strategy for efficiently handling
graphs with frequent structural changes and dynamic edge properties.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, DefaultDict
from collections import defaultdict, deque
import time
import threading
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class VersionedEdge:
    """Represents an edge with version history for dynamic updates."""
    
    def __init__(self, edge_id: str, source: str, target: str, **properties):
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.version = 1
        self.properties = properties.copy()
        self.is_active = True
        self.history: List[Dict[str, Any]] = []
    
    def update_properties(self, **new_properties) -> None:
        """Update edge properties with versioning."""
        # Save current state to history
        self.history.append({
            'version': self.version,
            'timestamp': self.updated_at,
            'properties': self.properties.copy()
        })
        
        # Update to new state
        self.properties.update(new_properties)
        self.updated_at = time.time()
        self.version += 1
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the version history of this edge."""
        return self.history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.edge_id,
            'source': self.source,
            'target': self.target,
            'properties': self.properties,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'version': self.version,
            'is_active': self.is_active
        }


class xDynamicAdjListStrategy(aEdgeStrategy):
    """
    Dynamic Adjacency List edge strategy for frequently changing graphs.
    
    Optimized for graphs with frequent edge additions, removals, and property updates.
    Provides efficient batch operations, change tracking, and version history.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Dynamic Adjacency List strategy."""
        super().__init__(EdgeMode.DYNAMIC_ADJ_LIST, traits, **options)
        
        self.is_directed = options.get('directed', True)
        self.track_history = options.get('track_history', True)
        self.max_history_per_edge = options.get('max_history_per_edge', 10)
        self.enable_batching = options.get('enable_batching', True)
        
        # Core storage with dynamic updates in mind
        self._outgoing: DefaultDict[str, Dict[str, VersionedEdge]] = defaultdict(dict)
        self._incoming: DefaultDict[str, Dict[str, VersionedEdge]] = defaultdict(dict) if self.is_directed else None
        
        # Vertex management
        self._vertices: Set[str] = set()
        
        # Change tracking
        self._edge_count = 0
        self._edge_id_counter = 0
        self._change_log: deque = deque(maxlen=1000)  # Recent changes
        self._batch_operations: List[Dict[str, Any]] = []
        
        # Performance optimizations
        self._lock = threading.RLock() if options.get('thread_safe', False) else None
        self._dirty_vertices: Set[str] = set()  # Vertices with pending updates
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the dynamic adjacency list strategy."""
        return (EdgeTrait.SPARSE | EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | 
                EdgeTrait.MULTI | EdgeTrait.TEMPORAL)
    
    def _with_lock(self, func):
        """Execute function with lock if thread safety is enabled."""
        if self._lock:
            with self._lock:
                return func()
        else:
            return func()
    
    def _log_change(self, operation: str, **details) -> None:
        """Log a change operation."""
        change_record = {
            'timestamp': time.time(),
            'operation': operation,
            'details': details
        }
        self._change_log.append(change_record)
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add an edge with dynamic property support."""
        def _add():
            # Generate edge ID
            edge_id = f"edge_{self._edge_id_counter}"
            self._edge_id_counter += 1
            
            # Create versioned edge
            edge = VersionedEdge(edge_id, source, target, **properties)
            
            # Add vertices
            self._vertices.add(source)
            self._vertices.add(target)
            
            # Store edge
            self._outgoing[source][target] = edge
            
            if self.is_directed and self._incoming is not None:
                self._incoming[target][source] = edge
            elif not self.is_directed and source != target:
                self._outgoing[target][source] = edge
            
            self._edge_count += 1
            self._dirty_vertices.add(source)
            self._dirty_vertices.add(target)
            
            # Log change
            self._log_change('add_edge', edge_id=edge_id, source=source, 
                           target=target, properties=properties)
            
            return edge_id
        
        return self._with_lock(_add)
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove edge with change tracking."""
        def _remove():
            if source not in self._outgoing or target not in self._outgoing[source]:
                return False
            
            edge = self._outgoing[source][target]
            
            # Check edge ID if specified
            if edge_id and edge.edge_id != edge_id:
                return False
            
            # Mark as inactive instead of deleting (for history)
            if self.track_history:
                edge.is_active = False
                edge.updated_at = time.time()
            else:
                del self._outgoing[source][target]
            
            # Remove from incoming list
            if self.is_directed and self._incoming is not None:
                if target in self._incoming and source in self._incoming[target]:
                    if self.track_history:
                        self._incoming[target][source].is_active = False
                    else:
                        del self._incoming[target][source]
            elif not self.is_directed and source != target:
                if target in self._outgoing and source in self._outgoing[target]:
                    if self.track_history:
                        self._outgoing[target][source].is_active = False
                    else:
                        del self._outgoing[target][source]
            
            self._edge_count -= 1
            self._dirty_vertices.add(source)
            self._dirty_vertices.add(target)
            
            # Log change
            self._log_change('remove_edge', edge_id=edge.edge_id, 
                           source=source, target=target)
            
            return True
        
        return self._with_lock(_remove)
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if active edge exists."""
        def _has():
            if source not in self._outgoing or target not in self._outgoing[source]:
                return False
            
            edge = self._outgoing[source][target]
            return edge.is_active
        
        return self._with_lock(_has)
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data with version information."""
        def _get():
            if source not in self._outgoing or target not in self._outgoing[source]:
                return None
            
            edge = self._outgoing[source][target]
            if not edge.is_active:
                return None
            
            return edge.to_dict()
        
        return self._with_lock(_get)
    
    def update_edge_properties(self, source: str, target: str, **properties) -> bool:
        """Update edge properties with versioning."""
        def _update():
            if source not in self._outgoing or target not in self._outgoing[source]:
                return False
            
            edge = self._outgoing[source][target]
            if not edge.is_active:
                return False
            
            edge.update_properties(**properties)
            
            # Trim history if needed
            if len(edge.history) > self.max_history_per_edge:
                edge.history = edge.history[-self.max_history_per_edge:]
            
            self._dirty_vertices.add(source)
            self._dirty_vertices.add(target)
            
            # Log change
            self._log_change('update_edge', edge_id=edge.edge_id,
                           source=source, target=target, properties=properties)
            
            return True
        
        return self._with_lock(_update)
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors with active edge filtering."""
        def _neighbors():
            if direction == 'out':
                if vertex in self._outgoing:
                    for target, edge in self._outgoing[vertex].items():
                        if edge.is_active:
                            yield target
            elif direction == 'in':
                if self.is_directed and self._incoming is not None:
                    if vertex in self._incoming:
                        for source, edge in self._incoming[vertex].items():
                            if edge.is_active:
                                yield source
                elif not self.is_directed:
                    if vertex in self._outgoing:
                        for neighbor, edge in self._outgoing[vertex].items():
                            if edge.is_active:
                                yield neighbor
            elif direction == 'both':
                seen = set()
                for neighbor in self.neighbors(vertex, 'out'):
                    if neighbor not in seen:
                        seen.add(neighbor)
                        yield neighbor
                for neighbor in self.neighbors(vertex, 'in'):
                    if neighbor not in seen:
                        seen.add(neighbor)
                        yield neighbor
        
        return self._with_lock(_neighbors)
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree counting only active edges."""
        return sum(1 for _ in self.neighbors(vertex, direction))
    
    def edges(self, data: bool = False, include_inactive: bool = False) -> Iterator[tuple]:
        """Get all edges with optional inactive edge inclusion."""
        def _edges():
            seen_edges = set()
            
            for source, adj_dict in self._outgoing.items():
                for target, edge in adj_dict.items():
                    if edge.is_active or include_inactive:
                        edge_key = (source, target, edge.edge_id)
                        
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            
                            if data:
                                yield (source, target, edge.to_dict())
                            else:
                                yield (source, target)
        
        return self._with_lock(_edges)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._vertices)
    
    def __len__(self) -> int:
        """Get the number of active edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return len(self._vertices)
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        def _clear():
            self._outgoing.clear()
            if self._incoming is not None:
                self._incoming.clear()
            self._vertices.clear()
            self._edge_count = 0
            self._edge_id_counter = 0
            self._change_log.clear()
            self._batch_operations.clear()
            self._dirty_vertices.clear()
            
            self._log_change('clear_all')
        
        self._with_lock(_clear)
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex."""
        def _add():
            self._vertices.add(vertex)
            self._log_change('add_vertex', vertex=vertex)
        
        self._with_lock(_add)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove a vertex and all its edges."""
        def _remove():
            if vertex not in self._vertices:
                return False
            
            # Count edges to remove
            edges_removed = 0
            
            # Remove outgoing edges
            if vertex in self._outgoing:
                edges_removed += len([e for e in self._outgoing[vertex].values() if e.is_active])
                for edge in self._outgoing[vertex].values():
                    if edge.is_active:
                        edge.is_active = False
                        edge.updated_at = time.time()
            
            # Remove incoming edges
            for source, adj_dict in self._outgoing.items():
                if vertex in adj_dict and adj_dict[vertex].is_active:
                    adj_dict[vertex].is_active = False
                    adj_dict[vertex].updated_at = time.time()
                    edges_removed += 1
            
            self._edge_count -= edges_removed
            self._vertices.remove(vertex)
            
            self._log_change('remove_vertex', vertex=vertex, edges_removed=edges_removed)
            return True
        
        return self._with_lock(_remove)
    
    # ============================================================================
    # DYNAMIC-SPECIFIC OPERATIONS
    # ============================================================================
    
    def start_batch(self) -> None:
        """Start batch operation mode."""
        if self.enable_batching:
            self._batch_operations.clear()
    
    def end_batch(self) -> int:
        """End batch operation mode and return number of operations."""
        if self.enable_batching:
            operations_count = len(self._batch_operations)
            self._batch_operations.clear()
            return operations_count
        return 0
    
    def get_change_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent change history."""
        return list(self._change_log)[-limit:] if self._change_log else []
    
    def get_edge_history(self, source: str, target: str) -> List[Dict[str, Any]]:
        """Get version history for a specific edge."""
        if source not in self._outgoing or target not in self._outgoing[source]:
            return []
        
        edge = self._outgoing[source][target]
        return edge.get_history()
    
    def get_dirty_vertices(self) -> Set[str]:
        """Get vertices that have pending updates."""
        return self._dirty_vertices.copy()
    
    def mark_clean(self, vertex: str) -> None:
        """Mark a vertex as clean (no pending updates)."""
        self._dirty_vertices.discard(vertex)
    
    def mark_all_clean(self) -> None:
        """Mark all vertices as clean."""
        self._dirty_vertices.clear()
    
    def compact_history(self) -> int:
        """Compact edge histories and remove inactive edges."""
        def _compact():
            compacted_count = 0
            
            for source, adj_dict in self._outgoing.items():
                to_remove = []
                for target, edge in adj_dict.items():
                    if not edge.is_active and not self.track_history:
                        to_remove.append(target)
                    elif edge.is_active and len(edge.history) > self.max_history_per_edge:
                        # Keep only recent history
                        edge.history = edge.history[-self.max_history_per_edge:]
                        compacted_count += 1
                
                for target in to_remove:
                    del adj_dict[target]
                    compacted_count += 1
            
            self._log_change('compact_history', compacted_count=compacted_count)
            return compacted_count
        
        return self._with_lock(_compact)
    
    def get_temporal_edges(self, start_time: float, end_time: float) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Get edges that were active during the specified time period."""
        result = []
        
        for source, adj_dict in self._outgoing.items():
            for target, edge in adj_dict.items():
                if (edge.created_at <= end_time and 
                    (edge.is_active or edge.updated_at >= start_time)):
                    result.append((source, target, edge.to_dict()))
        
        return result
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'DYNAMIC_ADJ_LIST',
            'backend': 'Versioned adjacency lists with change tracking',
            'directed': self.is_directed,
            'track_history': self.track_history,
            'enable_batching': self.enable_batching,
            'thread_safe': self._lock is not None,
            'complexity': {
                'add_edge': 'O(1)',
                'remove_edge': 'O(1)',
                'update_edge': 'O(1)',
                'has_edge': 'O(1)',
                'neighbors': 'O(degree)',
                'space': 'O(V + E + H)'  # H = history
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        total_history_entries = sum(
            len(edge.history) 
            for adj_dict in self._outgoing.values() 
            for edge in adj_dict.values()
        )
        
        active_edges = sum(
            1 for adj_dict in self._outgoing.values() 
            for edge in adj_dict.values() 
            if edge.is_active
        )
        
        return {
            'vertices': len(self._vertices),
            'active_edges': active_edges,
            'total_edges': sum(len(adj_dict) for adj_dict in self._outgoing.values()),
            'dirty_vertices': len(self._dirty_vertices),
            'change_log_size': len(self._change_log),
            'total_history_entries': total_history_entries,
            'avg_history_per_edge': total_history_entries / max(1, active_edges),
            'memory_usage': f"{active_edges * 120 + total_history_entries * 80} bytes (estimated)"
        }
