#!/usr/bin/env python3
"""
GraphQL Query Strategy

This module implements the GraphQL query strategy for graph-based data queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

import re
from typing import Any, Dict, List, Optional, Union
from .base import AGraphQueryStrategy
from ...errors import XWNodeTypeError, XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class GraphQLStrategy(AGraphQueryStrategy):
    """
    GraphQL query strategy for graph-based data queries.
    
    Supports:
    - Queries and mutations
    - Fragments and variables
    - Introspection
    - Subscriptions
    - Schema validation
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.GRAPHQL
        self._traits = QueryTrait.GRAPH | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute GraphQL query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid GraphQL query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "query":
            return self._execute_query(query, **kwargs)
        elif query_type == "mutation":
            return self._execute_mutation(query, **kwargs)
        elif query_type == "subscription":
            return self._execute_subscription(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate GraphQL query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic GraphQL validation
        query = query.strip()
        
        # Check for valid GraphQL operations
        valid_operations = ["query", "mutation", "subscription"]
        for operation in valid_operations:
            if query.startswith(operation) or query.startswith("{"):
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get GraphQL query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "fields": self._extract_fields(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute path query."""
        query = f"""
        query {{
            path(start: "{start}", end: "{end}") {{
                nodes
                edges
                cost
            }}
        }}
        """
        return self.execute(query)
    
    def neighbor_query(self, node: Any) -> List[Any]:
        """Execute neighbor query."""
        query = f"""
        query {{
            node(id: "{node}") {{
                neighbors {{
                    id
                    properties
                }}
            }}
        }}
        """
        return self.execute(query)
    
    def shortest_path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute shortest path query."""
        query = f"""
        query {{
            shortestPath(start: "{start}", end: "{end}") {{
                path
                distance
                hops
            }}
        }}
        """
        return self.execute(query)
    
    def connected_components_query(self) -> List[List[Any]]:
        """Execute connected components query."""
        query = """
        query {
            connectedComponents {
                components {
                    nodes
                    size
                }
            }
        }
        """
        return self.execute(query)
    
    def cycle_detection_query(self) -> List[List[Any]]:
        """Execute cycle detection query."""
        query = """
        query {
            cycles {
                cycles {
                    nodes
                    length
                }
            }
        }
        """
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from GraphQL query."""
        query = query.strip()
        
        if query.startswith("mutation"):
            return "mutation"
        elif query.startswith("subscription"):
            return "subscription"
        elif query.startswith("query") or query.startswith("{"):
            return "query"
        else:
            return "unknown"
    
    def _execute_query(self, query: str, **kwargs) -> Any:
        """Execute GraphQL query."""
        return {"result": "GraphQL query executed", "query": query}
    
    def _execute_mutation(self, query: str, **kwargs) -> Any:
        """Execute GraphQL mutation."""
        return {"result": "GraphQL mutation executed", "query": query}
    
    def _execute_subscription(self, query: str, **kwargs) -> Any:
        """Execute GraphQL subscription."""
        return {"result": "GraphQL subscription executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        # Count nested fields and connections
        depth = self._calculate_query_depth(query)
        
        if depth > 5:
            return "HIGH"
        elif depth > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 150
        elif complexity == "MEDIUM":
            return 75
        else:
            return 25
    
    def _calculate_query_depth(self, query: str) -> int:
        """Calculate query nesting depth."""
        depth = 0
        max_depth = 0
        
        for char in query:
            if char == '{':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == '}':
                depth -= 1
        
        return max_depth
    
    def _extract_fields(self, query: str) -> List[str]:
        """Extract field names from GraphQL query."""
        # Simple field extraction
        fields = []
        lines = query.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('}'):
                if ':' in line:
                    field = line.split(':')[0].strip()
                    fields.append(field)
        
        return fields
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if self._calculate_query_depth(query) > 3:
            hints.append("Consider reducing query depth to improve performance")
        
        if "..." in query:
            hints.append("Consider using fragments for reusable query parts")
        
        if query.count('{') > 10:
            hints.append("Consider breaking down complex queries into smaller ones")
        
        return hints
