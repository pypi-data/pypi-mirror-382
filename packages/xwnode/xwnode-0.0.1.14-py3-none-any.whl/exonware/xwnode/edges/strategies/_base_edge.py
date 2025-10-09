"""
Abstract Edge Strategy Interface

This module defines the abstract base class that all edge strategies must implement
in the strategy system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Iterator, Union, Set
from ...types import EdgeMode, EdgeTrait


class aEdgeStrategy(ABC):
    """
    Abstract base class for all edge strategies.
    
    This abstract base class defines the contract that all edge strategy
    implementations must follow, ensuring consistency and interoperability.
    """
    
    def __init__(self, mode: EdgeMode, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the abstract edge strategy."""
        self.mode = mode
        self.traits = traits
        self.options = options
        self._edges: Dict[tuple[Any, Any], Dict[str, Any]] = {}
        self._vertices: Set[Any] = set()
        self._edge_count = 0
        
        # Validate traits compatibility with mode
        self._validate_traits()
    
    def _validate_traits(self) -> None:
        """Validate that the requested traits are compatible with this strategy."""
        supported_traits = self.get_supported_traits()
        unsupported = self.traits & ~supported_traits
        if unsupported != EdgeTrait.NONE:
            unsupported_names = [trait.name for trait in EdgeTrait if trait in unsupported]
            raise ValueError(f"Strategy {self.mode.name} does not support traits: {unsupported_names}")
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by this strategy implementation."""
        # Default implementation - subclasses should override
        return EdgeTrait.NONE
    
    def has_trait(self, trait: EdgeTrait) -> bool:
        """Check if this strategy has a specific trait."""
        return bool(self.traits & trait)
    
    def require_trait(self, trait: EdgeTrait, operation: str = "operation") -> None:
        """Require a specific trait for an operation."""
        if not self.has_trait(trait):
            from ...errors import UnsupportedCapabilityError
            raise UnsupportedCapabilityError(f"{operation} requires {trait.name} capability")
    
    # ============================================================================
    # CORE OPERATIONS (Required)
    # ============================================================================
    
    @abstractmethod
    def add_edge(self, u: Any, v: Any, **properties) -> None:
        """
        Add an edge between vertices u and v.
        
        Args:
            u: Source vertex
            v: Target vertex
            **properties: Edge properties (weight, label, etc.)
        """
        pass
    
    @abstractmethod
    def remove_edge(self, u: Any, v: Any) -> bool:
        """
        Remove an edge between vertices u and v.
        
        Args:
            u: Source vertex
            v: Target vertex
            
        Returns:
            True if edge was found and removed, False otherwise
        """
        pass
    
    @abstractmethod
    def has_edge(self, u: Any, v: Any) -> bool:
        """
        Check if an edge exists between vertices u and v.
        
        Args:
            u: Source vertex
            v: Target vertex
            
        Returns:
            True if edge exists, False otherwise
        """
        pass
    
    @abstractmethod
    def neighbors(self, u: Any) -> Iterator[Any]:
        """
        Get neighbors of vertex u.
        
        Args:
            u: Vertex to get neighbors for
            
        Returns:
            Iterator over neighbor vertices
        """
        pass
    
    @abstractmethod
    def degree(self, u: Any) -> int:
        """
        Get the degree (number of edges) of vertex u.
        
        Args:
            u: Vertex to get degree for
            
        Returns:
            Number of edges incident to u
        """
        pass
    
    @abstractmethod
    def edges(self) -> Iterator[tuple[Any, Any, Dict[str, Any]]]:
        """
        Get all edges in the graph.
        
        Returns:
            Iterator over (u, v, properties) tuples
        """
        pass
    
    @abstractmethod
    def vertices(self) -> Iterator[Any]:
        """
        Get all vertices in the graph.
        
        Returns:
            Iterator over vertices
        """
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get the number of edges."""
        pass
    
    # ============================================================================
    # CAPABILITY-BASED OPERATIONS (Optional)
    # ============================================================================
    
    def get_edge_weight(self, u: Any, v: Any) -> float:
        """
        Get weight of edge (u, v) (requires WEIGHTED trait).
        
        Args:
            u: Source vertex
            v: Target vertex
            
        Returns:
            Weight of the edge
            
        Raises:
            UnsupportedCapabilityError: If WEIGHTED trait not supported
        """
        if EdgeTrait.WEIGHTED not in self.traits:
            raise XWNodeUnsupportedCapabilityError("WEIGHTED", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for weighted strategies
        edge_data = self._edges.get((u, v), {})
        return edge_data.get('weight', 1.0)
    
    def set_edge_weight(self, u: Any, v: Any, weight: float) -> None:
        """
        Set weight of edge (u, v) (requires WEIGHTED trait).
        
        Args:
            u: Source vertex
            v: Target vertex
            weight: New weight value
            
        Raises:
            UnsupportedCapabilityError: If WEIGHTED trait not supported
        """
        if EdgeTrait.WEIGHTED not in self.traits:
            raise XWNodeUnsupportedCapabilityError("WEIGHTED", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for weighted strategies
        if (u, v) in self._edges:
            self._edges[(u, v)]['weight'] = weight
    
    def get_edge_property(self, u: Any, v: Any, property_name: str) -> Any:
        """
        Get a property of edge (u, v).
        
        Args:
            u: Source vertex
            v: Target vertex
            property_name: Name of the property
            
        Returns:
            Property value, or None if not found
        """
        edge_data = self._edges.get((u, v), {})
        return edge_data.get(property_name)
    
    def set_edge_property(self, u: Any, v: Any, property_name: str, value: Any) -> None:
        """
        Set a property of edge (u, v).
        
        Args:
            u: Source vertex
            v: Target vertex
            property_name: Name of the property
            value: Property value
        """
        if (u, v) in self._edges:
            self._edges[(u, v)][property_name] = value
    
    def get_spatial_edges(self, bounds: Dict[str, Any]) -> List[tuple[Any, Any, Dict[str, Any]]]:
        """
        Get edges within spatial bounds (requires SPATIAL trait).
        
        Args:
            bounds: Spatial bounds (e.g., {'x_min': 0, 'x_max': 10, 'y_min': 0, 'y_max': 10})
            
        Returns:
            List of (u, v, properties) tuples within bounds
            
        Raises:
            UnsupportedCapabilityError: If SPATIAL trait not supported
        """
        if EdgeTrait.SPATIAL not in self.traits:
            raise XWNodeUnsupportedCapabilityError("SPATIAL", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for spatial strategies
        # This would be overridden by actual spatial implementations
        return list(self.edges())
    
    def get_temporal_edges(self, start_time: Any, end_time: Any) -> List[tuple[Any, Any, Dict[str, Any]]]:
        """
        Get edges within temporal range (requires TEMPORAL trait).
        
        Args:
            start_time: Start time (inclusive)
            end_time: End time (exclusive)
            
        Returns:
            List of (u, v, properties) tuples within time range
            
        Raises:
            UnsupportedCapabilityError: If TEMPORAL trait not supported
        """
        if EdgeTrait.TEMPORAL not in self.traits:
            raise XWNodeUnsupportedCapabilityError("TEMPORAL", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for temporal strategies
        result = []
        for u, v, props in self.edges():
            edge_time = props.get('time', 0)
            if start_time <= edge_time < end_time:
                result.append((u, v, props))
        return result
    
    def add_hyperedge(self, vertices: List[Any], **properties) -> str:
        """
        Add a hyperedge connecting multiple vertices (requires HYPER trait).
        
        Args:
            vertices: List of vertices to connect
            **properties: Hyperedge properties
            
        Returns:
            Hyperedge identifier
            
        Raises:
            UnsupportedCapabilityError: If HYPER trait not supported
        """
        if EdgeTrait.HYPER not in self.traits:
            raise XWNodeUnsupportedCapabilityError("HYPER", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for hyperedge strategies
        # This would be overridden by actual hyperedge implementations
        raise NotImplementedError("Hyperedge support not implemented in base class")
    
    # ============================================================================
    # GRAPH ANALYSIS OPERATIONS
    # ============================================================================
    
    def vertex_count(self) -> int:
        """Get the number of vertices."""
        return len(self._vertices)
    
    def edge_count(self) -> int:
        """Get the number of edges."""
        return len(self)
    
    def density(self) -> float:
        """Calculate graph density."""
        n = self.vertex_count()
        if n <= 1:
            return 0.0
        return self.edge_count() / (n * (n - 1))
    
    def is_directed(self) -> bool:
        """Check if graph is directed."""
        return EdgeTrait.DIRECTED in self.traits
    
    def is_weighted(self) -> bool:
        """Check if graph is weighted."""
        return EdgeTrait.WEIGHTED in self.traits
    
    def is_spatial(self) -> bool:
        """Check if graph has spatial properties."""
        return EdgeTrait.SPATIAL in self.traits
    
    def is_temporal(self) -> bool:
        """Check if graph has temporal properties."""
        return EdgeTrait.TEMPORAL in self.traits
    
    def is_hyper(self) -> bool:
        """Check if graph supports hyperedges."""
        return EdgeTrait.HYPER in self.traits
    
    # ============================================================================
    # STRATEGY METADATA
    # ============================================================================
    
    def capabilities(self) -> EdgeTrait:
        """Get the capabilities supported by this strategy."""
        return self.traits
    
    def backend_info(self) -> Dict[str, Any]:
        """Get information about the backend implementation."""
        return {
            "mode": self.mode.name,
            "traits": str(self.traits),
            "vertices": self.vertex_count(),
            "edges": self.edge_count(),
            "density": self.density(),
            "options": self.options.copy()
        }
    
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this strategy."""
        return {
            "vertices": self.vertex_count(),
            "edges": self.edge_count(),
            "density": self.density(),
            "mode": self.mode.name,
            "traits": str(self.traits)
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all edges and vertices."""
        self._edges.clear()
        self._vertices.clear()
        self._edge_count = 0
    
    def add_vertex(self, v: Any) -> None:
        """Add a vertex to the graph."""
        self._vertices.add(v)
    
    def remove_vertex(self, v: Any) -> bool:
        """Remove a vertex and all its incident edges."""
        if v not in self._vertices:
            return False
        
        # Remove all edges incident to v
        edges_to_remove = []
        for (u, w) in self._edges.keys():
            if u == v or w == v:
                edges_to_remove.append((u, w))
        
        for (u, w) in edges_to_remove:
            self.remove_edge(u, w)
        
        self._vertices.remove(v)
        return True
    
    def __contains__(self, edge: tuple[Any, Any]) -> bool:
        """Check if edge exists."""
        u, v = edge
        return self.has_edge(u, v)
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(mode={self.mode.name}, vertices={self.vertex_count()}, edges={self.edge_count()})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(mode={self.mode.name}, traits={self.traits}, vertices={self.vertex_count()}, edges={self.edge_count()})"


# Import here to avoid circular imports
from ...errors import XWNodeUnsupportedCapabilityError
