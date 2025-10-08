#!/usr/bin/env python3
"""
XWQuery Script Strategy

This module implements the central XWQuery Script strategy that handles all 50 action types
and provides conversion between different query formats using actions in tree format.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime

from .base import AQueryStrategy
from ...base import XWNodeBase
from ...contracts import QueryMode, QueryTrait
from ...errors import XWNodeTypeError, XWNodeValueError


class XWQueryScriptStrategy(AQueryStrategy):
    """
    Central script strategy using 50 action types in tree format.
    
    This strategy serves as the universal converter between all query formats
    by parsing them into a standardized action tree structure.
    """
    
    # 50 Action Headers from XWQUERY_SCRIPT.md
    ACTION_TYPES = [
        # Core SQL Operations (1-45)
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", 
        "MERGE", "LOAD", "STORE", "WHERE", "FILTER", "OPTIONAL", "UNION", 
        "BETWEEN", "LIKE", "IN", "TERM", "RANGE", "HAS", "MATCH", "JOIN", 
        "WITH", "OUT", "IN_TRAVERSE", "PATH", "RETURN", "PROJECT", "EXTEND", 
        "FOREACH", "LET", "FOR", "DESCRIBE", "CONSTRUCT", "ORDER", "BY", 
        "GROUP", "HAVING", "SUMMARIZE", "AGGREGATE", "WINDOW", "SLICING", 
        "INDEXING", "ASK", "SUBSCRIBE", "SUBSCRIPTION", "MUTATION", "VALUES",
        # Additional Operations (46-50)
        "DISTINCT", "PIPE", "OPTIONS"
    ]
    
    def __init__(self, actions_tree: Optional[XWNodeBase] = None, **options):
        super().__init__(**options)
        self._mode = QueryMode.AUTO
        self._traits = QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL | QueryTrait.BATCH
        
        if actions_tree is None:
            self._actions_tree = XWNodeBase.from_native({
                "root": {
                    "type": "PROGRAM",
                    "statements": [],
                    "comments": [],
                    "metadata": {
                        "version": "1.0",
                        "created": datetime.now().isoformat(),
                        "source_format": "XWQUERY_SCRIPT"
                    }
                }
            })
        else:
            self._actions_tree = actions_tree
        
        self._comments = []
        self._metadata = {}
    
    def execute(self, query: str, context: Dict[str, Any] = None, **kwargs) -> Any:
        """Execute XWQuery script."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid XWQuery script: {query}")
        
        # Parse and execute the script
        script_strategy = self.parse_script(query)
        return self._execute_actions_tree(script_strategy._actions_tree, **kwargs)
    
    def validate_query(self, query: str) -> bool:
        """Validate XWQuery script syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic validation - check for valid action types
        query_upper = query.upper()
        valid_actions = any(action in query_upper for action in self.ACTION_TYPES)
        
        return valid_actions
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get XWQuery script execution plan."""
        return {
            "query_type": "XWQUERY_SCRIPT",
            "action_count": len(self._extract_actions(query)),
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def can_handle(self, query_string: str) -> bool:
        """Check if this strategy can handle the given query string."""
        return self.validate_query(query_string)
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported query operations."""
        return self.ACTION_TYPES.copy()
    
    def estimate_complexity(self, query_string: str) -> Dict[str, Any]:
        """Estimate query complexity and resource requirements."""
        actions = self._extract_actions(query_string)
        complexity_level = self._estimate_complexity(query_string)
        
        return {
            "complexity": complexity_level,
            "action_count": len(actions),
            "estimated_cost": self._estimate_cost(query_string),
            "memory_usage": "low" if complexity_level == "LOW" else "medium" if complexity_level == "MEDIUM" else "high",
            "execution_time": f"{self._estimate_cost(query_string)}ms"
        }
    
    def parse_script(self, script_content: str) -> 'XWQueryScriptStrategy':
        """Parse XWQuery script content into actions tree."""
        parsed_actions = self._parse_xwquery_script(script_content)
        self._actions_tree = XWNodeBase.from_native(parsed_actions)
        return self
    
    def to_format(self, target_format: str) -> str:
        """Convert script to any supported format using available strategies."""
        strategy_class = self._get_strategy_class(target_format)
        if not strategy_class:
            raise ValueError(f"No strategy available for format: {target_format}")
        
        strategy = strategy_class()
        return strategy.from_actions_tree(self._actions_tree)
    
    def from_format(self, query_content: str, source_format: str) -> 'XWQueryScriptStrategy':
        """Create script strategy from any supported format."""
        strategy_class = self._get_strategy_class(source_format)
        if not strategy_class:
            raise ValueError(f"No strategy available for format: {source_format}")
        
        strategy = strategy_class()
        actions_tree = strategy.to_actions_tree(query_content)
        self._actions_tree = actions_tree
        return self
    
    def _parse_xwquery_script(self, script_content: str) -> Dict[str, Any]:
        """Parse XWQuery script into tree structure with nesting support."""
        return {
            "root": {
                "type": "PROGRAM",
                "statements": self._parse_statements(script_content),
                "comments": self._extract_comments(script_content),
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "source_format": "XWQUERY_SCRIPT"
                }
            }
        }
    
    def _parse_statements(self, script_content: str) -> List[Dict[str, Any]]:
        """Parse individual statements with nesting support."""
        statements = []
        lines = script_content.split('\n')
        current_statement = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            # Parse statement based on action type
            for action_type in self.ACTION_TYPES:
                if line.upper().startswith(action_type):
                    statement = self._parse_statement_line(line, action_type, line_num)
                    if statement:
                        statements.append(statement)
                    break
        
        return statements
    
    def _parse_statement_line(self, line: str, action_type: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single statement line."""
        return {
            "type": action_type,
            "id": f"action_{line_num}",
            "content": line,
            "line_number": line_num,
            "timestamp": datetime.now().isoformat(),
            "children": []  # For nested actions
        }
    
    def _extract_comments(self, script_content: str) -> List[Dict[str, Any]]:
        """Extract comments from script content."""
        comments = []
        lines = script_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('--'):
                comments.append({
                    "text": line.strip(),
                    "line_number": line_num,
                    "timestamp": datetime.now().isoformat()
                })
        
        return comments
    
    def _extract_actions(self, query: str) -> List[str]:
        """Extract action types from query."""
        actions = []
        query_upper = query.upper()
        
        for action_type in self.ACTION_TYPES:
            if action_type in query_upper:
                actions.append(action_type)
        
        return actions
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        actions = self._extract_actions(query)
        
        if len(actions) > 10:
            return "HIGH"
        elif len(actions) > 5:
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
            return 10
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "SELECT *" in query.upper():
            hints.append("Consider specifying columns instead of using *")
        if "WHERE" not in query.upper() and "SELECT" in query.upper():
            hints.append("Consider adding WHERE clause to limit results")
        
        return hints
    
    def _get_strategy_class(self, format_name: str) -> Optional[Type[AQueryStrategy]]:
        """Get strategy class for format using XWNode's strategy registry."""
        from ..registry import get_strategy_registry
        registry = get_strategy_registry()
        return registry.get_query_strategy(format_name.upper())
    
    def _get_strategy_class_fallback(self, format_name: str) -> Optional[Type[AQueryStrategy]]:
        """Fallback strategy class lookup."""
        strategy_map = {
            "SQL": "sql",
            "GRAPHQL": "graphql",
            "CYPHER": "cypher",
            "SPARQL": "sparql",
            "JSON_QUERY": "json_query",
            "XML_QUERY": "xml_query",
            "XPATH": "xpath",
            "XQUERY": "xquery",
            "JQ": "jq",
            "JMESPATH": "jmespath",
            "JSONIQ": "jsoniq",
            "GREMLIN": "gremlin",
            "ELASTIC_DSL": "elastic_dsl",
            "EQL": "eql",
            "FLUX": "flux",
            "PROMQL": "promql",
            "LOGQL": "logql",
            "SPL": "spl",
            "KQL": "kql",
            "CQL": "cql",
            "N1QL": "n1ql",
            "HIVEQL": "hiveql",
            "PIG": "pig",
            "MQL": "mql",
            "PARTIQL": "partiql",
            "LINQ": "linq",
            "HQL": "hql",
            "DATALOG": "datalog",
            "KSQL": "ksql",
            "GQL": "gql"
        }
        
        module_name = strategy_map.get(format_name.upper())
        if module_name:
            try:
                module = __import__(f'.{module_name}', fromlist=['.'], package=__package__)
                strategy_class_name = f"{format_name.title()}Strategy"
                return getattr(module, strategy_class_name, None)
            except (ImportError, AttributeError):
                pass
        
        return None
    
    def _execute_actions_tree(self, actions_tree: XWNodeBase, **kwargs) -> Any:
        """Execute actions tree."""
        # This would execute the parsed actions
        # For now, return a mock result
        return {
            "result": "XWQuery Script executed successfully",
            "actions_executed": len(actions_tree.get('root', {}).get('statements', [])),
            "execution_time": "0.001s"
        }
    
    def add_action(self, action_type: str, **action_params) -> 'XWQueryScriptStrategy':
        """Add an action to the actions tree with proper nesting."""
        if action_type not in self.ACTION_TYPES:
            raise ValueError(f"Unknown action type: {action_type}")
        
        action = {
            "type": action_type,
            "id": f"action_{len(self._get_all_actions())}",
            "params": action_params,
            "timestamp": datetime.now().isoformat(),
            "children": []
        }
        
        # Get current statements and add new action
        root_data = self._actions_tree.to_native()
        if 'root' not in root_data:
            root_data['root'] = {"statements": [], "comments": [], "metadata": {}}
        
        if 'statements' not in root_data['root']:
            root_data['root']['statements'] = []
        
        root_data['root']['statements'].append(action)
        
        # Update the actions tree
        self._actions_tree = XWNodeBase.from_native(root_data)
        
        return self
    
    def add_nested_action(self, parent_action_id: str, action_type: str, **action_params) -> 'XWQueryScriptStrategy':
        """Add a nested action (e.g., subquery, JOIN condition)."""
        parent = self._find_action_by_id(parent_action_id)
        if parent:
            child_action = {
                "type": action_type,
                "id": f"action_{len(self._get_all_actions())}",
                "params": action_params,
                "timestamp": datetime.now().isoformat(),
                "children": []
            }
            parent.get('children', []).append(child_action)
        
        return self
    
    def _find_action_by_id(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Find action by ID in the tree."""
        return self._search_tree(self._actions_tree, action_id)
    
    def _search_tree(self, node: XWNodeBase, action_id: str) -> Optional[Dict[str, Any]]:
        """Recursively search for action in tree."""
        if isinstance(node, XWNodeBase):
            node_data = node.to_native()
        else:
            node_data = node
        
        if isinstance(node_data, dict):
            if node_data.get('id') == action_id:
                return node_data
            
            for key, value in node_data.items():
                if isinstance(value, (list, dict)):
                    result = self._search_tree(value, action_id)
                    if result:
                        return result
        
        elif isinstance(node_data, list):
            for item in node_data:
                result = self._search_tree(item, action_id)
                if result:
                    return result
        
        return None
    
    def _get_all_actions(self) -> List[Dict[str, Any]]:
        """Get all actions from the tree (flattened)."""
        actions = []
        self._flatten_tree(self._actions_tree, actions)
        return actions
    
    def _flatten_tree(self, node: XWNodeBase, actions: List[Dict[str, Any]]):
        """Flatten the tree to get all actions."""
        if isinstance(node, XWNodeBase):
            node_data = node.to_native()
        else:
            node_data = node
        
        if isinstance(node_data, dict):
            if 'type' in node_data and 'id' in node_data:
                actions.append(node_data)
            
            for value in node_data.values():
                if isinstance(value, (list, dict)):
                    self._flatten_tree(value, actions)
        
        elif isinstance(node_data, list):
            for item in node_data:
                self._flatten_tree(item, actions)
    
    def get_actions_tree(self) -> XWNodeBase:
        """Get the actions tree as XWNodeBase."""
        return self._actions_tree
    
    def to_native(self) -> Dict[str, Any]:
        """Convert to native Python object."""
        return {
            "actions_tree": self._actions_tree.to_native(),
            "comments": self._comments,
            "metadata": self._metadata,
            "action_types": self.ACTION_TYPES
        }
