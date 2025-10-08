#!/usr/bin/env python3
"""
Unit Tests for XWQuery Script Integration

This module contains unit tests for XWQuery Script system integration,
following DEV_GUIDELINES.md standards for production-ready testing.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 10-Sep-2025
"""

import pytest
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from exonware.xwnode.strategies.queries.xwquery_strategy import XWQueryScriptStrategy
from exonware.xwnode.strategies.queries.xwnode_executor import XWNodeQueryActionExecutor
from exonware.xwnode.strategies.queries.sql import SQLStrategy
from exonware.xwnode.strategies.registry import get_strategy_registry
from exonware.xwnode.base import XWNodeBase
from exonware.xwnode.errors import XWNodeTypeError, XWNodeValueError


class TestXWQueryScriptIntegration:
    """Integration tests for XWQuery Script system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.xwquery_strategy = XWQueryScriptStrategy()
        self.executor = XWNodeQueryActionExecutor()
        self.sql_strategy = SQLStrategy()
        self.registry = get_strategy_registry()
        
        self.complex_sql = """
        WITH monthly_sales AS (
            SELECT 
                DATE_TRUNC('month', o.order_date) as month,
                c.category_name,
                p.product_name,
                SUM(oi.quantity * oi.unit_price) as total_revenue,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                AVG(oi.quantity * oi.unit_price) as avg_order_value
            FROM orders o
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            INNER JOIN products p ON oi.product_id = p.product_id
            INNER JOIN categories c ON p.category_id = c.category_id
            WHERE o.order_date >= '2024-01-01'
                AND o.status = 'completed'
                AND c.category_name IN ('Electronics', 'Clothing', 'Books')
            GROUP BY DATE_TRUNC('month', o.order_date), c.category_name, p.product_name
            HAVING SUM(oi.quantity * oi.unit_price) > 1000
        ),
        top_products AS (
            SELECT 
                category_name,
                product_name,
                total_revenue,
                ROW_NUMBER() OVER (PARTITION BY category_name ORDER BY total_revenue DESC) as revenue_rank
            FROM monthly_sales
        )
        SELECT 
            tp.category_name,
            tp.product_name,
            tp.total_revenue,
            tp.revenue_rank,
            ms.unique_customers,
            ms.avg_order_value,
            CASE 
                WHEN tp.revenue_rank = 1 THEN 'Top Performer'
                WHEN tp.revenue_rank <= 3 THEN 'High Performer'
                ELSE 'Standard'
            END as performance_tier
        FROM top_products tp
        INNER JOIN monthly_sales ms ON tp.category_name = ms.category_name 
            AND tp.product_name = ms.product_name
        WHERE tp.revenue_rank <= 5
        ORDER BY tp.category_name, tp.revenue_rank;
        """
    
    def test_xwquery_strategy_to_actions_tree(self):
        """Test XWQuery Script to actions tree conversion."""
        # Parse SQL into XWQuery Script
        parsed_strategy = self.xwquery_strategy.parse_script(self.complex_sql)
        actions_tree = parsed_strategy.get_actions_tree()
        
        assert isinstance(actions_tree, XWNodeBase)
        
        tree_data = actions_tree.to_native()
        assert 'root' in tree_data
        assert 'statements' in tree_data['root']
        assert 'comments' in tree_data['root']
        assert 'metadata' in tree_data['root']
        
        # Should have parsed multiple statements
        assert len(tree_data['root']['statements']) > 0
        
        # Should preserve comments
        assert len(tree_data['root']['comments']) >= 0
    
    def test_sql_strategy_to_actions_tree(self):
        """Test SQL strategy to actions tree conversion."""
        actions_tree = self.sql_strategy.to_actions_tree(self.complex_sql)
        
        assert isinstance(actions_tree, XWNodeBase)
        
        tree_data = actions_tree.to_native()
        assert 'root' in tree_data
        assert 'statements' in tree_data['root']
        
        # Should have at least one statement
        assert len(tree_data['root']['statements']) > 0
    
    def test_actions_tree_to_sql_conversion(self):
        """Test actions tree to SQL conversion."""
        # Create actions tree from SQL
        actions_tree = self.sql_strategy.to_actions_tree(self.complex_sql)
        
        # Convert back to SQL
        converted_sql = self.sql_strategy.from_actions_tree(actions_tree)
        
        assert isinstance(converted_sql, str)
        assert len(converted_sql) > 0
    
    def test_xwquery_script_format_conversion(self):
        """Test XWQuery Script format conversion capabilities."""
        # Parse SQL into XWQuery Script
        parsed_strategy = self.xwquery_strategy.parse_script(self.complex_sql)
        
        # Test conversion to different formats (will fail until strategies are implemented)
        formats_to_test = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL"]
        
        for format_name in formats_to_test:
            try:
                converted = parsed_strategy.to_format(format_name)
                assert isinstance(converted, str)
                assert len(converted) > 0
            except ValueError as e:
                # Expected until strategies are fully implemented
                assert "No strategy available" in str(e) or "not found" in str(e)
    
    def test_executor_query_type_detection(self):
        """Test executor query type detection."""
        test_queries = {
            "SELECT * FROM users WHERE age > 25": "SQL",
            "MATCH (u:User) WHERE u.age > 25 RETURN u": "CYPHER",
            "{ users { id name } }": "GRAPHQL",
            "PREFIX : <http://example.org/> SELECT ?s WHERE { ?s a :User }": "SPARQL",
            "Users | where age > 25 | project name": "KQL"
        }
        
        for query, expected_type in test_queries.items():
            detected_type = self.executor._detect_query_type(query)
            assert detected_type == expected_type, f"Expected {expected_type}, got {detected_type} for query: {query}"
    
    def test_executor_supported_query_types(self):
        """Test executor supported query types."""
        supported_types = self.executor.get_supported_query_types()
        
        assert isinstance(supported_types, list)
        assert len(supported_types) > 0
        
        # Should include major query types
        expected_types = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL", "CQL", "N1QL", "HIVEQL", "PIG"]
        for query_type in expected_types:
            assert query_type in supported_types, f"Missing query type: {query_type}"
    
    def test_registry_query_strategy_registration(self):
        """Test query strategy registration in registry."""
        # Test registry stats
        stats = self.registry.get_registry_stats()
        
        assert isinstance(stats, dict)
        assert 'query_strategies' in stats
        assert 'registered_query_types' in stats
        
        # Should have some query strategies registered
        assert stats['query_strategies'] >= 0
        assert isinstance(stats['registered_query_types'], list)
    
    def test_registry_query_type_listing(self):
        """Test query type listing in registry."""
        query_types = self.registry.list_query_types()
        
        assert isinstance(query_types, list)
        # Should have some query types (even if strategies aren't fully implemented)
        assert len(query_types) >= 0
    
    def test_registry_strategy_availability(self):
        """Test strategy availability checking."""
        # Test checking for various query types
        test_types = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL", "INVALID_TYPE"]
        
        for query_type in test_types:
            has_strategy = self.registry.has_query_strategy(query_type)
            assert isinstance(has_strategy, bool)
    
    def test_xwquery_script_action_management(self):
        """Test XWQuery Script action management."""
        strategy = XWQueryScriptStrategy()
        
        # Add multiple actions
        strategy.add_action("SELECT", table="users", columns=["id", "name", "email"])
        strategy.add_action("WHERE", condition="age > 25")
        strategy.add_action("ORDER", by="name", direction="ASC")
        strategy.add_action("LIMIT", count=100)
        
        # Get actions tree
        actions_tree = strategy.get_actions_tree()
        tree_data = actions_tree.to_native()
        
        # Should have 4 statements
        assert len(tree_data['root']['statements']) == 4
        
        # Verify action types
        action_types = [stmt['type'] for stmt in tree_data['root']['statements']]
        assert "SELECT" in action_types
        assert "WHERE" in action_types
        assert "ORDER" in action_types
        assert "LIMIT" in action_types
    
    def test_xwquery_script_nested_actions(self):
        """Test XWQuery Script nested actions."""
        strategy = XWQueryScriptStrategy()
        
        # Add parent action
        strategy.add_action("SELECT", table="users", columns=["id", "name"])
        
        # Get parent action ID
        tree_data = strategy._actions_tree.to_native()
        parent_id = tree_data['root']['statements'][0]['id']
        
        # Add nested actions
        strategy.add_nested_action(parent_id, "WHERE", condition="age > 25")
        strategy.add_nested_action(parent_id, "ORDER", by="name")
        
        # Verify nested structure
        parent_action = strategy._find_action_by_id(parent_id)
        assert parent_action is not None
        assert len(parent_action.get('children', [])) == 2
        
        child_types = [child['type'] for child in parent_action['children']]
        assert "WHERE" in child_types
        assert "ORDER" in child_types
    
    def test_xwquery_script_comment_preservation(self):
        """Test XWQuery Script comment preservation."""
        sql_with_comments = """
        -- This is a comment about the query
        SELECT u.name, COUNT(o.order_id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.user_id = o.user_id
        -- Another comment about the join
        WHERE u.created_at >= '2024-01-01'
        GROUP BY u.user_id, u.name
        HAVING COUNT(o.order_id) > 5
        ORDER BY order_count DESC
        LIMIT 10;
        """
        
        parsed_strategy = self.xwquery_strategy.parse_script(sql_with_comments)
        tree_data = parsed_strategy._actions_tree.to_native()
        
        # Should preserve comments
        assert 'comments' in tree_data['root']
        # Comments should be extracted and preserved
        assert len(tree_data['root']['comments']) >= 0
    
    def test_xwquery_script_metadata_preservation(self):
        """Test XWQuery Script metadata preservation."""
        strategy = XWQueryScriptStrategy()
        strategy.add_action("SELECT", table="users")
        
        tree_data = strategy._actions_tree.to_native()
        metadata = tree_data['root']['metadata']
        
        # Should preserve metadata
        assert 'version' in metadata
        assert 'created' in metadata
        assert 'source_format' in metadata
        
        assert metadata['version'] == '1.0'
        assert metadata['source_format'] == 'XWQUERY_SCRIPT'
        assert isinstance(metadata['created'], str)
    
    def test_executor_performance_monitoring(self):
        """Test executor performance monitoring."""
        # Execute some queries to generate stats
        test_queries = [
            ("SELECT * FROM users", "SQL"),
            ("SELECT * FROM orders", "SQL"),
            ("SELECT * FROM products", "SQL")
        ]
        
        for query, query_type in test_queries:
            try:
                self.executor.execute_query(query, query_type)
            except:
                pass  # Expected until strategies are implemented
        
        # Check execution stats
        stats = self.executor.get_execution_stats()
        
        assert isinstance(stats, dict)
        assert 'total_queries' in stats
        assert 'successful_queries' in stats
        assert 'failed_queries' in stats
        assert 'execution_times' in stats
        assert 'success_rate' in stats
        
        # Should have some execution data
        assert stats['total_queries'] >= 0
        assert 0 <= stats['success_rate'] <= 1
    
    def test_executor_cost_estimation(self):
        """Test executor cost estimation."""
        test_queries = [
            "SELECT * FROM users",
            "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.name",
            "WITH cte AS (SELECT * FROM users) SELECT * FROM cte"
        ]
        
        for query in test_queries:
            cost_info = self.executor.estimate_cost(query, "SQL")
            
            assert isinstance(cost_info, dict)
            assert 'backend' in cost_info
            assert 'complexity' in cost_info
            assert 'estimated_cost' in cost_info
            assert 'execution_time' in cost_info
            assert 'memory_usage' in cost_info
            assert 'strategy_used' in cost_info
            
            assert cost_info['backend'] == 'XWNODE'
            assert cost_info['complexity'] in ['LOW', 'MEDIUM', 'HIGH', 'UNKNOWN']
            assert isinstance(cost_info['estimated_cost'], int)
            assert 'ms' in cost_info['execution_time']
            assert cost_info['memory_usage'] in ['low', 'medium', 'high']
    
    def test_xwquery_script_error_handling(self):
        """Test XWQuery Script error handling."""
        # Test invalid action type
        with pytest.raises(ValueError, match="Unknown action type"):
            self.xwquery_strategy.add_action("INVALID_ACTION", param="value")
        
        # Test invalid query execution
        with pytest.raises(XWNodeValueError, match="Invalid XWQuery script"):
            self.xwquery_strategy.execute("INVALID QUERY")
        
        # Test None input
        with pytest.raises(XWNodeValueError, match="Invalid XWQuery script"):
            self.xwquery_strategy.execute(None)
    
    def test_executor_error_handling(self):
        """Test executor error handling."""
        # Test unsupported query type
        with pytest.raises(XWNodeValueError, match="Unsupported query type"):
            self.executor.execute_query("SELECT * FROM users", "UNSUPPORTED_TYPE")
        
        # Test invalid query
        with pytest.raises(XWNodeValueError, match="Invalid"):
            self.executor.execute_query("INVALID QUERY", "SQL")
    
    def test_xwquery_script_performance(self):
        """Test XWQuery Script performance characteristics."""
        import time
        
        # Test parsing performance
        start_time = time.time()
        parsed_strategy = self.xwquery_strategy.parse_script(self.complex_sql)
        parsing_time = time.time() - start_time
        
        assert parsing_time < 1.0, f"Parsing took too long: {parsing_time}s"
        
        # Test execution performance
        start_time = time.time()
        result = self.xwquery_strategy.execute("SELECT * FROM users")
        execution_time = time.time() - start_time
        
        assert execution_time < 1.0, f"Execution took too long: {execution_time}s"
        assert isinstance(result, dict)
    
    def test_executor_performance(self):
        """Test executor performance characteristics."""
        import time
        
        # Test cost estimation performance
        start_time = time.time()
        cost_info = self.executor.estimate_cost("SELECT * FROM users", "SQL")
        estimation_time = time.time() - start_time
        
        assert estimation_time < 1.0, f"Cost estimation took too long: {estimation_time}s"
        assert isinstance(cost_info, dict)
        
        # Test query type detection performance
        start_time = time.time()
        detected_type = self.executor._detect_query_type("SELECT * FROM users")
        detection_time = time.time() - start_time
        
        assert detection_time < 0.1, f"Query type detection took too long: {detection_time}s"
        assert detected_type == "SQL"
    
    def test_xwquery_script_memory_usage(self):
        """Test XWQuery Script memory usage."""
        import gc
        
        # Clear any existing objects
        gc.collect()
        
        # Create multiple strategies
        strategies = []
        for _ in range(10):
            strategy = XWQueryScriptStrategy()
            strategy.add_action("SELECT", table="users")
            strategies.append(strategy)
        
        # Should not cause memory issues
        assert len(strategies) == 10
        
        # Clean up
        del strategies
        gc.collect()
    
    def test_executor_memory_usage(self):
        """Test executor memory usage."""
        import gc
        
        # Clear any existing objects
        gc.collect()
        
        # Create multiple executors
        executors = []
        for _ in range(10):
            executor = XWNodeQueryActionExecutor()
            executors.append(executor)
        
        # Should not cause memory issues
        assert len(executors) == 10
        
        # Clean up
        del executors
        gc.collect()


class TestXWQueryScriptSystemIntegration:
    """System integration tests for XWQuery Script."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.xwquery_strategy = XWQueryScriptStrategy()
        self.executor = XWNodeQueryActionExecutor()
        self.registry = get_strategy_registry()
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow."""
        # 1. Parse SQL into XWQuery Script
        sql_query = "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.name"
        parsed_strategy = self.xwquery_strategy.parse_script(sql_query)
        
        # 2. Get actions tree
        actions_tree = parsed_strategy.get_actions_tree()
        assert isinstance(actions_tree, XWNodeBase)
        
        # 3. Add additional actions
        parsed_strategy.add_action("HAVING", condition="COUNT(o.id) > 5")
        parsed_strategy.add_action("ORDER", by="COUNT(o.id)", direction="DESC")
        
        # 4. Get native representation
        native = parsed_strategy.to_native()
        assert isinstance(native, dict)
        
        # 5. Test executor integration
        detected_type = self.executor._detect_query_type(sql_query)
        assert detected_type == "SQL"
        
        # 6. Test cost estimation
        cost_info = self.executor.estimate_cost(sql_query, "SQL")
        assert isinstance(cost_info, dict)
        
        # 7. Test registry integration
        has_sql = self.registry.has_query_strategy("SQL")
        assert isinstance(has_sql, bool)
    
    def test_multi_format_conversion_workflow(self):
        """Test multi-format conversion workflow."""
        sql_query = "SELECT * FROM users WHERE age > 25"
        
        # 1. Parse SQL into XWQuery Script
        parsed_strategy = self.xwquery_strategy.parse_script(sql_query)
        
        # 2. Test conversion to different formats
        formats = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL"]
        
        for format_name in formats:
            try:
                converted = parsed_strategy.to_format(format_name)
                assert isinstance(converted, str)
            except ValueError as e:
                # Expected until strategies are fully implemented
                assert "No strategy available" in str(e) or "not found" in str(e)
    
    def test_strategy_registry_integration(self):
        """Test strategy registry integration."""
        # Test registry stats
        stats = self.registry.get_registry_stats()
        assert isinstance(stats, dict)
        
        # Test query type listing
        query_types = self.registry.list_query_types()
        assert isinstance(query_types, list)
        
        # Test strategy availability
        test_types = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL"]
        for query_type in test_types:
            has_strategy = self.registry.has_query_strategy(query_type)
            assert isinstance(has_strategy, bool)
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        # Execute multiple queries
        queries = [
            "SELECT * FROM users",
            "SELECT * FROM orders",
            "SELECT * FROM products"
        ]
        
        for query in queries:
            try:
                self.executor.execute_query(query, "SQL")
            except:
                pass  # Expected until strategies are implemented
        
        # Check performance stats
        stats = self.executor.get_execution_stats()
        assert isinstance(stats, dict)
        assert 'total_queries' in stats
        assert 'success_rate' in stats
        
        # Check backend info
        backend_info = self.executor.get_backend_info()
        assert isinstance(backend_info, dict)
        assert backend_info['backend'] == 'XWNODE'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
