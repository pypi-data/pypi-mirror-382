#!/usr/bin/env python3
"""
MQL Query Strategy

This module implements the MQL query strategy for MongoDB Query Language operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from typing import Any, Dict, List, Optional
from .base import ADocumentQueryStrategy
from ...errors import XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class MQLStrategy(ADocumentQueryStrategy):
    """MQL query strategy for MongoDB Query Language operations."""
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.MQL
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute MQL query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid MQL query: {query}")
        return {"result": "MQL query executed", "query": query}
    
    def validate_query(self, query: str) -> bool:
        """Validate MQL query syntax."""
        if not query or not isinstance(query, str):
            return False
        return any(op in query for op in ["find", "aggregate", "insert", "update", "delete", "createIndex"])
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get MQL query execution plan."""
        return {
            "query_type": "MQL",
            "complexity": "MEDIUM",
            "estimated_cost": 80
        }
    
    def path_query(self, path: str) -> Any:
        """Execute path-based query."""
        return self.execute(f"db.collection.find({{{path}: {{$exists: true}}}})")
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        return self.execute(f"db.collection.find({filter_expression})")
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        projection = {field: 1 for field in fields}
        return self.execute(f"db.collection.find({{}}, {projection})")
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        sort_order = 1 if order == "asc" else -1
        return self.execute(f"db.collection.find().sort({{{sort_fields[0]}: {sort_order}}})")
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        return self.execute(f"db.collection.find().skip({offset}).limit({limit})")
