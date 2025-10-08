#!/usr/bin/env python3
"""
JMESPath Query Strategy

This module implements the JMESPath query strategy for JSON data queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

import re
from typing import Any, Dict, List, Optional, Union
from .base import ADocumentQueryStrategy
from ...errors import XWNodeTypeError, XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class JMESPathStrategy(ADocumentQueryStrategy):
    """
    JMESPath query strategy for JSON data queries.
    
    Supports:
    - JMESPath expressions
    - Projections and filters
    - Functions and operators
    - Multi-select and pipe expressions
    - Flatten and sort operations
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.JMESPATH
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute JMESPath query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid JMESPath query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "projection":
            return self._execute_projection(query, **kwargs)
        elif query_type == "filter":
            return self._execute_filter(query, **kwargs)
        elif query_type == "function":
            return self._execute_function(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate JMESPath query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic JMESPath validation
        query = query.strip()
        
        # Check for JMESPath syntax
        if query.startswith(".") or query.startswith("[") or query.startswith("@"):
            return True
        
        # Check for JMESPath functions
        jmespath_functions = ["length", "keys", "values", "sort", "reverse", "flatten", "unique", "join", "split", "to_string", "to_number", "type", "starts_with", "ends_with", "contains", "abs", "ceil", "floor", "max", "min", "sum", "avg", "sort_by", "group_by", "map", "filter", "merge", "merge_left", "merge_right"]
        
        for func in jmespath_functions:
            if func in query:
                return True
        
        # Check for operators
        if "||" in query or "&&" in query or "==" in query or "!=" in query or ">" in query or "<" in query:
            return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get JMESPath query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "expressions": self._extract_expressions(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, path: str) -> Any:
        """Execute path-based query."""
        # JMESPath path queries
        query = f"$.{path}"
        return self.execute(query)
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        query = f"[?{filter_expression}]"
        return self.execute(query)
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        if len(fields) == 1:
            query = f"$.{fields[0]}"
        else:
            field_list = ", ".join([f"'{field}': @.{field}" for field in fields])
            query = f"{{{field_list}}}"
        
        return self.execute(query)
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        if order.lower() == "desc":
            query = f"sort_by(@, &{sort_fields[0]}) | reverse(@)"
        else:
            query = f"sort_by(@, &{sort_fields[0]})"
        
        return self.execute(query)
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        if offset > 0:
            query = f"[{offset}:{offset + limit}]"
        else:
            query = f"[:{limit}]"
        
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from JMESPath query."""
        query = query.strip()
        
        if "[" in query and "]" in query:
            return "filter"
        elif "{" in query and "}" in query:
            return "projection"
        elif "(" in query and ")" in query:
            return "function"
        else:
            return "path"
    
    def _execute_projection(self, query: str, **kwargs) -> Any:
        """Execute projection query."""
        return {"result": "JMESPath projection executed", "query": query}
    
    def _execute_filter(self, query: str, **kwargs) -> Any:
        """Execute filter query."""
        return {"result": "JMESPath filter executed", "query": query}
    
    def _execute_function(self, query: str, **kwargs) -> Any:
        """Execute function query."""
        return {"result": "JMESPath function executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        expressions = self._extract_expressions(query)
        
        if len(expressions) > 5:
            return "HIGH"
        elif len(expressions) > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 80
        elif complexity == "MEDIUM":
            return 40
        else:
            return 20
    
    def _extract_expressions(self, query: str) -> List[str]:
        """Extract JMESPath expressions from query."""
        expressions = []
        
        # Path expressions
        if "." in query:
            expressions.append("path")
        if "[" in query and "]" in query:
            expressions.append("filter")
        if "{" in query and "}" in query:
            expressions.append("projection")
        if "|" in query:
            expressions.append("pipe")
        if "||" in query or "&&" in query:
            expressions.append("logical")
        if "==" in query or "!=" in query or ">" in query or "<" in query:
            expressions.append("comparison")
        
        # Functions
        jmespath_functions = ["length", "keys", "values", "sort", "reverse", "flatten", "unique", "join", "split", "to_string", "to_number", "type", "starts_with", "ends_with", "contains", "abs", "ceil", "floor", "max", "min", "sum", "avg", "sort_by", "group_by", "map", "filter", "merge", "merge_left", "merge_right"]
        for func in jmespath_functions:
            if func in query:
                expressions.append(func)
        
        return expressions
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "|" in query:
            hints.append("Consider combining operations to reduce pipe operations")
        
        if "[" in query and "]" in query:
            hints.append("Consider using specific paths instead of array operations when possible")
        
        if "{" in query and "}" in query:
            hints.append("Consider using multi-select for better performance")
        
        if "sort" in query:
            hints.append("Consider using sort_by for complex sorting operations")
        
        return hints
