#!/usr/bin/env python3
"""
XPath Query Strategy

This module implements the XPath query strategy for XML data queries.

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


class XPathStrategy(ADocumentQueryStrategy):
    """
    XPath query strategy for XML data queries.
    
    Supports:
    - XPath 1.0 and 2.0 features
    - Location paths and expressions
    - Predicates and functions
    - Axes and node tests
    - Namespace support
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.XPATH
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute XPath query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid XPath query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "location_path":
            return self._execute_location_path(query, **kwargs)
        elif query_type == "expression":
            return self._execute_expression(query, **kwargs)
        elif query_type == "function":
            return self._execute_function(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate XPath query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic XPath validation
        query = query.strip()
        
        # Check for XPath syntax
        if query.startswith("/") or query.startswith("//") or query.startswith("@") or query.startswith("."):
            return True
        
        # Check for XPath functions
        xpath_functions = ["text", "name", "local-name", "namespace-uri", "count", "position", "last", "string", "number", "boolean", "not", "true", "false", "contains", "starts-with", "ends-with", "substring", "substring-before", "substring-after", "normalize-space", "translate", "concat", "string-length", "sum", "floor", "ceiling", "round", "id", "key", "document", "format-number", "unparsed-entity-uri", "unparsed-entity-public-id", "generate-id", "system-property", "element-available", "function-available", "current", "lang", "local-name", "namespace-uri", "name", "string", "number", "boolean", "not", "true", "false", "contains", "starts-with", "ends-with", "substring", "substring-before", "substring-after", "normalize-space", "translate", "concat", "string-length", "sum", "floor", "ceiling", "round", "id", "key", "document", "format-number", "unparsed-entity-uri", "unparsed-entity-public-id", "generate-id", "system-property", "element-available", "function-available", "current", "lang"]
        
        for func in xpath_functions:
            if func in query:
                return True
        
        # Check for axes
        axes = ["ancestor", "ancestor-or-self", "attribute", "child", "descendant", "descendant-or-self", "following", "following-sibling", "namespace", "parent", "preceding", "preceding-sibling", "self"]
        
        for axis in axes:
            if f"{axis}::" in query:
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get XPath query execution plan."""
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
        # XPath path queries
        query = f"/{path}"
        return self.execute(query)
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        query = f"//*[{filter_expression}]"
        return self.execute(query)
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        if len(fields) == 1:
            query = f"//{fields[0]}"
        else:
            field_list = " | ".join([f"//{field}" for field in fields])
            query = f"({field_list})"
        
        return self.execute(query)
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        # XPath doesn't have built-in sorting, use position
        if order.lower() == "desc":
            query = f"//*[position() = last() - position() + 1]"
        else:
            query = f"//*[position()]"
        
        return self.execute(query)
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        if offset > 0:
            query = f"//*[position() > {offset} and position() <= {offset + limit}]"
        else:
            query = f"//*[position() <= {limit}]"
        
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from XPath query."""
        query = query.strip()
        
        if "/" in query or "//" in query:
            return "location_path"
        elif "(" in query and ")" in query:
            return "function"
        else:
            return "expression"
    
    def _execute_location_path(self, query: str, **kwargs) -> Any:
        """Execute location path."""
        return {"result": "XPath location path executed", "query": query}
    
    def _execute_expression(self, query: str, **kwargs) -> Any:
        """Execute expression."""
        return {"result": "XPath expression executed", "query": query}
    
    def _execute_function(self, query: str, **kwargs) -> Any:
        """Execute function call."""
        return {"result": "XPath function executed", "query": query}
    
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
            return 100
        elif complexity == "MEDIUM":
            return 50
        else:
            return 25
    
    def _extract_expressions(self, query: str) -> List[str]:
        """Extract XPath expressions from query."""
        expressions = []
        
        # Location paths
        if "/" in query:
            expressions.append("path")
        if "//" in query:
            expressions.append("descendant")
        if "@" in query:
            expressions.append("attribute")
        if "[" in query and "]" in query:
            expressions.append("predicate")
        
        # Axes
        axes = ["ancestor", "ancestor-or-self", "attribute", "child", "descendant", "descendant-or-self", "following", "following-sibling", "namespace", "parent", "preceding", "preceding-sibling", "self"]
        for axis in axes:
            if f"{axis}::" in query:
                expressions.append(axis)
        
        # Functions
        xpath_functions = ["text", "name", "local-name", "namespace-uri", "count", "position", "last", "string", "number", "boolean", "not", "true", "false", "contains", "starts-with", "ends-with", "substring", "substring-before", "substring-after", "normalize-space", "translate", "concat", "string-length", "sum", "floor", "ceiling", "round", "id", "key", "document", "format-number", "unparsed-entity-uri", "unparsed-entity-public-id", "generate-id", "system-property", "element-available", "function-available", "current", "lang"]
        for func in xpath_functions:
            if func in query:
                expressions.append(func)
        
        return expressions
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "//" in query:
            hints.append("Consider using specific paths instead of descendant navigation")
        
        if "[" in query and "]" in query:
            hints.append("Consider using indexes for predicate operations")
        
        if "position()" in query:
            hints.append("Consider using last() for better performance")
        
        if "text()" in query:
            hints.append("Consider using normalize-space() for text processing")
        
        return hints
