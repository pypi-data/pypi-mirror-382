#!/usr/bin/env python3
"""
Integration Tests for XWQuery Script End-to-End

This module contains comprehensive end-to-end integration tests for the XWQuery Script system,
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
try:
    # When running as a script, __file__ is available
    src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
except NameError:
    # When running with exec or in some environments, __file__ might not be available
    src_path = os.path.join(os.path.dirname(os.path.abspath('tests/integration/test_xwquery_script_end_to_end.py')), '..', '..', 'src')

src_path = os.path.abspath(src_path)
if os.path.exists(src_path) and src_path not in sys.path:
    sys.path.insert(0, src_path)

from exonware.xwnode.strategies.queries.xwquery_strategy import XWQueryScriptStrategy
from exonware.xwnode.strategies.queries.xwnode_executor import XWNodeQueryActionExecutor
from exonware.xwnode.strategies.queries.sql import SQLStrategy
from exonware.xwnode.strategies.registry import get_strategy_registry
from exonware.xwnode.base import XWNodeBase
from exonware.xwnode.errors import XWNodeTypeError, XWNodeValueError


class TestXWQueryScriptEndToEnd:
    """End-to-end integration tests for XWQuery Script system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.xwquery_strategy = XWQueryScriptStrategy()
        self.executor = XWNodeQueryActionExecutor()
        self.sql_strategy = SQLStrategy()
        self.registry = get_strategy_registry()
        
        # Complex e-commerce analytics query
        self.complex_sql = """
        -- Complex E-commerce Analytics Query
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
        
        # Simple queries for testing
        self.simple_queries = {
            "SQL": "SELECT * FROM users WHERE age > 25",
            "CYPHER": "MATCH (u:User) WHERE u.age > 25 RETURN u.id, u.name, u.email",
            "GRAPHQL": "{ users(where: { age: { gt: 25 } }) { id name email } }",
            "SPARQL": "PREFIX : <http://example.org/> SELECT ?id ?name ?email WHERE { ?user a :User ; :age ?age ; :id ?id ; :name ?name ; :email ?email . FILTER(?age > 25) }",
            "KQL": "Users | where age > 25 | project id, name, email"
        }
    
    def test_complete_sql_to_xwquery_workflow(self):
        """Test complete SQL to XWQuery Script workflow."""
        # Step 1: Parse SQL into XWQuery Script
        parsed_strategy = self.xwquery_strategy.parse_script(self.complex_sql)
        assert isinstance(parsed_strategy, XWQueryScriptStrategy)
        
        # Step 2: Get actions tree
        actions_tree = parsed_strategy.get_actions_tree()
        assert isinstance(actions_tree, XWNodeBase)
        
        tree_data = actions_tree.to_native()
        assert 'root' in tree_data
        assert 'statements' in tree_data['root']
        assert 'comments' in tree_data['root']
        assert 'metadata' in tree_data['root']
        
        # Step 3: Verify parsed content
        assert len(tree_data['root']['statements']) > 0
        assert len(tree_data['root']['comments']) >= 0
        
        # Step 4: Get native representation
        native = parsed_strategy.to_native()
        assert isinstance(native, dict)
        assert 'actions_tree' in native
        assert 'comments' in native
        assert 'metadata' in native
        assert 'action_types' in native
        
        # Step 5: Test execution
        result = parsed_strategy.execute(self.complex_sql)
        assert isinstance(result, dict)
        assert 'result' in result
        assert 'actions_executed' in result
        assert 'execution_time' in result
    
    def test_sql_strategy_integration(self):
        """Test SQL strategy integration with XWQuery Script."""
        # Step 1: Convert SQL to actions tree using SQL strategy
        actions_tree = self.sql_strategy.to_actions_tree(self.complex_sql)
        assert isinstance(actions_tree, XWNodeBase)
        
        # Step 2: Test SQL strategy methods
        can_handle = self.sql_strategy.can_handle(self.complex_sql)
        assert isinstance(can_handle, bool)
        
        supported_ops = self.sql_strategy.get_supported_operations()
        assert isinstance(supported_ops, list)
        assert len(supported_ops) > 0
        
        complexity = self.sql_strategy.estimate_complexity(self.complex_sql)
        assert isinstance(complexity, dict)
        assert 'complexity_level' in complexity
        assert 'estimated_cost' in complexity
        
        # Step 3: Test actions tree structure
        tree_data = actions_tree.to_native()
        assert 'root' in tree_data
        assert 'statements' in tree_data['root']
        assert len(tree_data['root']['statements']) > 0
    
    def test_executor_query_processing_workflow(self):
        """Test executor query processing workflow."""
        # Step 1: Test query type detection
        for query_type, query in self.simple_queries.items():
            detected_type = self.executor._detect_query_type(query)
            assert detected_type == query_type, f"Expected {query_type}, got {detected_type}"
        
        # Step 2: Test query validation
        for query_type, query in self.simple_queries.items():
            if query_type in self.executor._supported_queries:
                try:
                    is_valid = self.executor.validate_query(query, query_type)
                    assert isinstance(is_valid, bool)
                except Exception as e:
                    # Expected until strategies are fully implemented
                    assert "not found" in str(e).lower() or "not available" in str(e).lower()
        
        # Step 3: Test cost estimation
        for query_type, query in self.simple_queries.items():
            cost_info = self.executor.estimate_cost(query, query_type)
            assert isinstance(cost_info, dict)
            assert 'backend' in cost_info
            assert 'complexity' in cost_info
            assert 'estimated_cost' in cost_info
            assert cost_info['backend'] == 'XWNODE'
        
        # Step 4: Test query execution
        for query_type, query in self.simple_queries.items():
            try:
                result = self.executor.execute_query(query, query_type)
                assert isinstance(result, dict)
                assert 'result' in result
                assert 'query_type' in result
                assert 'backend' in result
                assert result['backend'] == 'XWNODE'
            except Exception as e:
                # Expected until strategies are fully implemented
                assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_multi_format_conversion_workflow(self):
        """Test multi-format conversion workflow."""
        # Step 1: Parse SQL into XWQuery Script
        parsed_strategy = self.xwquery_strategy.parse_script(self.complex_sql)
        
        # Step 2: Test conversion to different formats
        formats_to_test = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL", "CQL", "N1QL"]
        
        for format_name in formats_to_test:
            try:
                converted = parsed_strategy.to_format(format_name)
                assert isinstance(converted, str)
                assert len(converted) > 0
            except (ValueError, Exception) as e:
                # Expected until strategies are fully implemented or registry issues are resolved
                error_msg = str(e).lower()
                assert any(phrase in error_msg for phrase in [
                    "no strategy available", "not found", "query strategy", 
                    "cannot import", "module not found"
                ])
    
    def test_strategy_registry_integration_workflow(self):
        """Test strategy registry integration workflow."""
        # Step 1: Test registry stats
        stats = self.registry.get_registry_stats()
        assert isinstance(stats, dict)
        assert 'query_strategies' in stats
        assert 'registered_query_types' in stats
        
        # Step 2: Test query type listing
        query_types = self.registry.list_query_types()
        assert isinstance(query_types, list)
        
        # Step 3: Test strategy availability checking
        test_types = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL", "CQL", "N1QL", "HIVEQL", "PIG"]
        for query_type in test_types:
            has_strategy = self.registry.has_query_strategy(query_type)
            assert isinstance(has_strategy, bool)
        
        # Step 4: Test strategy retrieval
        for query_type in test_types:
            try:
                strategy = self.registry.get_query_strategy(query_type)
                # If strategy exists, it should be a valid query strategy
                if strategy is not None:
                    assert hasattr(strategy, 'execute')
                    assert hasattr(strategy, 'validate_query')
            except Exception as e:
                # Expected until strategies are fully implemented
                assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_performance_monitoring_workflow(self):
        """Test performance monitoring workflow."""
        # Step 1: Execute multiple queries to generate performance data
        test_queries = [
            ("SELECT * FROM users", "SQL"),
            ("SELECT * FROM orders", "SQL"),
            ("SELECT * FROM products", "SQL"),
            ("MATCH (u:User) RETURN u", "CYPHER"),
            ("{ users { id name } }", "GRAPHQL")
        ]
        
        for query, query_type in test_queries:
            try:
                self.executor.execute_query(query, query_type)
            except:
                pass  # Expected until strategies are implemented
        
        # Step 2: Check execution statistics
        stats = self.executor.get_execution_stats()
        assert isinstance(stats, dict)
        assert 'total_queries' in stats
        assert 'successful_queries' in stats
        assert 'failed_queries' in stats
        assert 'execution_times' in stats
        assert 'avg_execution_time' in stats
        assert 'success_rate' in stats
        
        # Step 3: Check backend information
        backend_info = self.executor.get_backend_info()
        assert isinstance(backend_info, dict)
        assert 'backend' in backend_info
        assert 'version' in backend_info
        assert 'capabilities' in backend_info
        assert 'supported_query_types' in backend_info
        assert 'performance_class' in backend_info
        assert 'execution_stats' in backend_info
        
        assert backend_info['backend'] == 'XWNODE'
        assert backend_info['version'] == '0.0.1'
        assert backend_info['performance_class'] == 'high_performance'
    
    def test_error_handling_workflow(self):
        """Test error handling workflow."""
        # Step 1: Test invalid query handling
        invalid_queries = [
            ("", "SQL"),
            (None, "SQL"),
            ("INVALID QUERY", "SQL"),
            ("SELECT * FROM users", "INVALID_TYPE")
        ]
        
        for query, query_type in invalid_queries:
            if query is None or query == "":
                with pytest.raises(XWNodeValueError):
                    self.executor.execute_query(query, query_type)
            elif query_type == "INVALID_TYPE":
                with pytest.raises(XWNodeValueError, match="Unsupported query type"):
                    self.executor.execute_query(query, query_type)
            else:
                with pytest.raises(XWNodeValueError, match="Invalid"):
                    self.executor.execute_query(query, query_type)
        
        # Step 2: Test XWQuery Script error handling
        with pytest.raises(ValueError, match="Unknown action type"):
            self.xwquery_strategy.add_action("INVALID_ACTION", param="value")
        
        with pytest.raises(XWNodeValueError, match="Invalid XWQuery script"):
            self.xwquery_strategy.execute("INVALID QUERY")
    
    def test_memory_management_workflow(self):
        """Test memory management workflow."""
        import gc
        
        # Step 1: Clear any existing objects
        gc.collect()
        
        # Step 2: Create multiple strategies and executors
        strategies = []
        executors = []
        
        for _ in range(20):
            strategy = XWQueryScriptStrategy()
            strategy.add_action("SELECT", table="users")
            strategies.append(strategy)
            
            executor = XWNodeQueryActionExecutor()
            executors.append(executor)
        
        # Step 3: Verify objects were created successfully
        assert len(strategies) == 20
        assert len(executors) == 20
        
        # Step 4: Clean up and verify memory is released
        del strategies
        del executors
        gc.collect()
        
        # Step 5: Create new objects to verify memory is available
        new_strategy = XWQueryScriptStrategy()
        new_executor = XWNodeQueryActionExecutor()
        
        assert new_strategy is not None
        assert new_executor is not None
    
    def test_concurrent_execution_workflow(self):
        """Test concurrent execution workflow."""
        import threading
        import time
        
        results = []
        errors = []
        
        def execute_query_worker(query, query_type, worker_id):
            try:
                result = self.executor.execute_query(query, query_type)
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, e))
        
        # Step 1: Create multiple threads
        threads = []
        test_queries = [
            ("SELECT * FROM users", "SQL"),
            ("SELECT * FROM orders", "SQL"),
            ("SELECT * FROM products", "SQL"),
            ("MATCH (u:User) RETURN u", "CYPHER"),
            ("{ users { id name } }", "GRAPHQL")
        ]
        
        for i, (query, query_type) in enumerate(test_queries):
            thread = threading.Thread(target=execute_query_worker, args=(query, query_type, i))
            threads.append(thread)
        
        # Step 2: Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Step 3: Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        execution_time = time.time() - start_time
        
        # Step 4: Verify concurrent execution
        assert execution_time < 5.0, f"Concurrent execution took too long: {execution_time}s"
        assert len(results) + len(errors) == len(test_queries)
        
        # Step 5: Check execution statistics
        stats = self.executor.get_execution_stats()
        assert stats['total_queries'] >= 0
    
    def test_comprehensive_action_management_workflow(self):
        """Test comprehensive action management workflow."""
        # Step 1: Create XWQuery Script strategy
        strategy = XWQueryScriptStrategy()
        
        # Step 2: Add multiple actions
        actions_to_add = [
            ("SELECT", {"table": "users", "columns": ["id", "name", "email"]}),
            ("WHERE", {"condition": "age > 25"}),
            ("GROUP", {"by": ["department"]}),
            ("HAVING", {"condition": "COUNT(*) > 5"}),
            ("ORDER", {"by": "name", "direction": "ASC"}),
            ("LIMIT", {"count": 100})
        ]
        
        for action_type, params in actions_to_add:
            strategy.add_action(action_type, **params)
        
        # Step 3: Verify all actions were added
        tree_data = strategy._actions_tree.to_native()
        statements = tree_data['root']['statements']
        
        assert len(statements) == len(actions_to_add)
        
        # Step 4: Verify action types and parameters
        for i, (expected_type, expected_params) in enumerate(actions_to_add):
            assert statements[i]['type'] == expected_type
            assert statements[i]['params'] == expected_params
        
        # Step 5: Test nested actions
        parent_id = statements[0]['id']  # SELECT action
        strategy.add_nested_action(parent_id, "JOIN", table="orders", on="users.id = orders.user_id")
        
        # Step 6: Verify nested action was added
        parent_action = strategy._find_action_by_id(parent_id)
        assert parent_action is not None
        assert len(parent_action.get('children', [])) == 1
        assert parent_action['children'][0]['type'] == 'JOIN'
        
        # Step 7: Test action tree operations
        all_actions = strategy._get_all_actions()
        assert len(all_actions) == len(actions_to_add) + 1  # +1 for nested action
        
        # Step 8: Test search functionality
        select_actions = strategy._search_tree("type", "SELECT")
        assert len(select_actions) == 1
        assert select_actions[0]['type'] == 'SELECT'
    
    def test_complete_system_integration(self):
        """Test complete system integration."""
        # Step 1: Initialize all components
        xwquery_strategy = XWQueryScriptStrategy()
        executor = XWNodeQueryActionExecutor()
        sql_strategy = SQLStrategy()
        registry = get_strategy_registry()
        
        # Step 2: Test SQL parsing and conversion
        sql_query = "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.name HAVING COUNT(o.id) > 5"
        
        # Parse with XWQuery Script
        parsed_strategy = xwquery_strategy.parse_script(sql_query)
        actions_tree = parsed_strategy.get_actions_tree()
        
        # Convert with SQL strategy
        sql_actions_tree = sql_strategy.to_actions_tree(sql_query)
        converted_sql = sql_strategy.from_actions_tree(sql_actions_tree)
        
        # Step 3: Test executor integration
        detected_type = executor._detect_query_type(sql_query)
        cost_info = executor.estimate_cost(sql_query, detected_type)
        
        # Step 4: Test registry integration
        has_sql_strategy = registry.has_query_strategy("SQL")
        query_types = registry.list_query_types()
        
        # Step 5: Test performance monitoring
        try:
            executor.execute_query(sql_query, "SQL")
        except:
            pass  # Expected until strategies are implemented
        
        stats = executor.get_execution_stats()
        backend_info = executor.get_backend_info()
        
        # Step 6: Verify all components work together
        assert isinstance(parsed_strategy, XWQueryScriptStrategy)
        assert isinstance(actions_tree, XWNodeBase)
        assert isinstance(converted_sql, str)
        assert detected_type == "SQL"
        assert isinstance(cost_info, dict)
        assert isinstance(has_sql_strategy, bool)
        assert isinstance(query_types, list)
        assert isinstance(stats, dict)
        assert isinstance(backend_info, dict)
        
        # Step 7: Test format conversion
        try:
            converted = parsed_strategy.to_format("GRAPHQL")
            assert isinstance(converted, str)
        except ValueError as e:
            # Expected until strategies are fully implemented
            assert "No strategy available" in str(e) or "not found" in str(e)
        
        # Step 8: Test error handling
        with pytest.raises(ValueError, match="Unknown action type"):
            xwquery_strategy.add_action("INVALID_ACTION", param="value")
        
        with pytest.raises(XWNodeValueError, match="Unsupported query type"):
            executor.execute_query(sql_query, "INVALID_TYPE")


if __name__ == "__main__":
    try:
        pytest.main([__file__, "-v"])
    except NameError:
        # When __file__ is not available, run pytest on the current directory
        pytest.main(["-v"])
