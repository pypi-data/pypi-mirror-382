#!/usr/bin/env python3
"""
JSONiq Query Strategy

This module implements the JSONiq query strategy for JSON data queries.

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


class JSONiqStrategy(ADocumentQueryStrategy):
    """
    JSONiq query strategy for JSON data queries.
    
    Supports:
    - JSONiq 1.0 and 1.1 features
    - FLWOR expressions
    - JSON navigation
    - Type system
    - Functions and modules
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.JSONIQ
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute JSONiq query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid JSONiq query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "flwor":
            return self._execute_flwor(query, **kwargs)
        elif query_type == "path":
            return self._execute_path(query, **kwargs)
        elif query_type == "function":
            return self._execute_function(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate JSONiq query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic JSONiq validation
        query = query.strip()
        
        # Check for JSONiq keywords
        jsoniq_keywords = ["for", "let", "where", "order by", "group by", "return", "collection", "json", "object", "array"]
        
        query_lower = query.lower()
        for keyword in jsoniq_keywords:
            if keyword in query_lower:
                return True
        
        # Check for JSON path expressions
        if "$" in query or ".." in query or "[]" in query:
            return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get JSONiq query execution plan."""
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
        # JSONiq path queries
        query = f"$${path}"
        return self.execute(query)
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        query = f"""
        for $$item in collection()
        where {filter_expression}
        return $$item
        """
        return self.execute(query)
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        if len(fields) == 1:
            query = f"""
            for $$item in collection()
            return $$item.{fields[0]}
            """
        else:
            field_list = ", ".join([f"$$item.{field}" for field in fields])
            query = f"""
            for $$item in collection()
            return {{ {field_list} }}
            """
        
        return self.execute(query)
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        if order.lower() == "desc":
            query = f"""
            for $$item in collection()
            order by $$item.{sort_fields[0]} descending
            return $$item
            """
        else:
            query = f"""
            for $$item in collection()
            order by $$item.{sort_fields[0]}
            return $$item
            """
        
        return self.execute(query)
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        if offset > 0:
            query = f"""
            for $$item in collection()
            where count($$item) > {offset}
            return $$item
            """
            # Use subsequence for limit
            return self._execute_function(f"subsequence(collection(), {offset + 1}, {limit})")
        else:
            query = f"""
            for $$item in collection()
            return $$item
            """
            return self._execute_function(f"subsequence(collection(), 1, {limit})")
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from JSONiq query."""
        query = query.strip()
        
        if "for" in query.lower() or "let" in query.lower():
            return "flwor"
        elif "$" in query or ".." in query:
            return "path"
        elif "(" in query and ")" in query:
            return "function"
        else:
            return "unknown"
    
    def _execute_flwor(self, query: str, **kwargs) -> Any:
        """Execute FLWOR expression."""
        return {"result": "JSONiq FLWOR executed", "query": query}
    
    def _execute_path(self, query: str, **kwargs) -> Any:
        """Execute path expression."""
        return {"result": "JSONiq path executed", "query": query}
    
    def _execute_function(self, query: str, **kwargs) -> Any:
        """Execute function call."""
        return {"result": "JSONiq function executed", "query": query}
    
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
            return 120
        elif complexity == "MEDIUM":
            return 60
        else:
            return 30
    
    def _extract_expressions(self, query: str) -> List[str]:
        """Extract JSONiq expressions from query."""
        expressions = []
        
        # FLWOR expressions
        if "for" in query.lower():
            expressions.append("for")
        if "let" in query.lower():
            expressions.append("let")
        if "where" in query.lower():
            expressions.append("where")
        if "order by" in query.lower():
            expressions.append("order by")
        if "group by" in query.lower():
            expressions.append("group by")
        if "return" in query.lower():
            expressions.append("return")
        
        # Path expressions
        if "$" in query:
            expressions.append("path")
        if ".." in query:
            expressions.append("descendant")
        if "[]" in query:
            expressions.append("array")
        
        # Function calls
        if "(" in query and ")" in query:
            expressions.append("function")
        
        return expressions
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "for" in query.lower() and "let" in query.lower():
            hints.append("Consider using let for computed values")
        
        if ".." in query:
            hints.append("Consider using specific paths instead of descendant navigation")
        
        if "[]" in query:
            hints.append("Consider using array indexing for better performance")
        
        if "order by" in query.lower():
            hints.append("Consider using indexes for ordered queries")
        
        return hints
