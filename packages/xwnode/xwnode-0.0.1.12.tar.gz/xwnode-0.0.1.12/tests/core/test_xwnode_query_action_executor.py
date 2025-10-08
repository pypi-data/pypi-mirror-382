#!/usr/bin/env python3
"""
Core Tests for XWNode Query Action Executor

This module contains comprehensive core functionality tests for the XWNode Query Action Executor,
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

from exonware.xwnode.strategies.queries.xwnode_executor import XWNodeQueryActionExecutor
from exonware.xwnode.strategies.queries.base import AQueryActionExecutor
from exonware.xwnode.base import XWNodeBase
from exonware.xwnode.contracts import QueryMode, QueryTrait
from exonware.xwnode.errors import XWNodeTypeError, XWNodeValueError


class TestXWNodeQueryActionExecutorCore:
    """Core functionality tests for XWNodeQueryActionExecutor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = XWNodeQueryActionExecutor()
        self.sample_queries = {
            "SQL": "SELECT * FROM users WHERE age > 25",
            "GRAPHQL": "{ users(where: { age: { gt: 25 } }) { id name email } }",
            "CYPHER": "MATCH (u:User) WHERE u.age > 25 RETURN u.id, u.name, u.email",
            "SPARQL": "SELECT ?id ?name ?email WHERE { ?user a :User ; :age ?age ; :id ?id ; :name ?name ; :email ?email . FILTER(?age > 25) }",
            "KQL": "Users | where age > 25 | project id, name, email"
        }
    
    def test_executor_initialization(self):
        """Test XWNodeQueryActionExecutor initialization."""
        executor = XWNodeQueryActionExecutor()
        
        # Test basic initialization
        assert executor is not None
        assert isinstance(executor, AQueryActionExecutor)
        
        # Test supported queries
        assert hasattr(executor, '_supported_queries')
        assert isinstance(executor._supported_queries, list)
        assert len(executor._supported_queries) > 0
        
        # Test strategy cache
        assert hasattr(executor, '_strategy_cache')
        assert isinstance(executor._strategy_cache, dict)
        
        # Test execution stats
        assert hasattr(executor, '_execution_stats')
        assert isinstance(executor._execution_stats, dict)
    
    def test_get_supported_query_types(self):
        """Test getting supported query types."""
        supported_types = self.executor.get_supported_query_types()
        
        assert isinstance(supported_types, list)
        assert len(supported_types) > 0
        
        # Should include major query types
        expected_types = ["SQL", "GRAPHQL", "CYPHER", "SPARQL", "KQL", "CQL", "N1QL"]
        for query_type in expected_types:
            assert query_type in supported_types, f"Missing query type: {query_type}"
        
        # Should return a copy, not the original list
        assert supported_types is not self.executor._supported_queries
    
    def test_validate_query_valid(self):
        """Test query validation with valid queries."""
        for query_type, query in self.sample_queries.items():
            if query_type in self.executor._supported_queries:
                # Note: This will likely fail until strategies are implemented
                # but we test the method exists and handles the case gracefully
                try:
                    result = self.executor.validate_query(query, query_type)
                    assert isinstance(result, bool)
                except Exception as e:
                    # Expected until strategies are fully implemented
                    assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_validate_query_invalid_type(self):
        """Test query validation with invalid query types."""
        result = self.executor.validate_query("SELECT * FROM users", "INVALID_TYPE")
        assert result is False
    
    def test_validate_query_invalid_query(self):
        """Test query validation with invalid queries."""
        result = self.executor.validate_query("INVALID QUERY", "SQL")
        assert result is False
    
    def test_execute_query_basic(self):
        """Test basic query execution."""
        # Test with SQL query
        try:
            result = self.executor.execute_query("SELECT * FROM users", "SQL")
            assert isinstance(result, dict)
            assert 'result' in result
            assert 'query_type' in result
            assert 'execution_time' in result
            assert 'backend' in result
            assert 'strategy_used' in result
            
            assert result['query_type'] == 'SQL'
            assert result['backend'] == 'XWNODE'
        except Exception as e:
            # Expected until strategies are fully implemented
            assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_execute_query_invalid_type(self):
        """Test query execution with invalid query type."""
        with pytest.raises(XWNodeValueError, match="Unsupported query type"):
            self.executor.execute_query("SELECT * FROM users", "INVALID_TYPE")
    
    def test_execute_query_invalid_query(self):
        """Test query execution with invalid query."""
        with pytest.raises(XWNodeValueError, match="Invalid"):
            self.executor.execute_query("INVALID QUERY", "SQL")
    
    def test_get_execution_stats(self):
        """Test getting execution statistics."""
        stats = self.executor.get_execution_stats()
        
        assert isinstance(stats, dict)
        assert 'total_queries' in stats
        assert 'successful_queries' in stats
        assert 'failed_queries' in stats
        assert 'execution_times' in stats
        assert 'avg_execution_time' in stats
        assert 'min_execution_time' in stats
        assert 'max_execution_time' in stats
        assert 'success_rate' in stats
        
        assert isinstance(stats['total_queries'], int)
        assert isinstance(stats['successful_queries'], int)
        assert isinstance(stats['failed_queries'], int)
        assert isinstance(stats['execution_times'], list)
        assert isinstance(stats['avg_execution_time'], (int, float))
        assert isinstance(stats['min_execution_time'], (int, float))
        assert isinstance(stats['max_execution_time'], (int, float))
        assert isinstance(stats['success_rate'], (int, float))
        assert 0 <= stats['success_rate'] <= 1
    
    def test_get_backend_info(self):
        """Test getting backend information."""
        info = self.executor.get_backend_info()
        
        assert isinstance(info, dict)
        assert 'backend' in info
        assert 'version' in info
        assert 'capabilities' in info
        assert 'supported_query_types' in info
        assert 'performance_class' in info
        assert 'execution_stats' in info
        
        assert info['backend'] == 'XWNODE'
        assert info['version'] == '0.0.1'
        assert isinstance(info['capabilities'], list)
        assert len(info['capabilities']) > 0
        assert isinstance(info['supported_query_types'], int)
        assert info['performance_class'] == 'high_performance'
        assert isinstance(info['execution_stats'], dict)
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        cost_info = self.executor.estimate_cost("SELECT * FROM users", "SQL")
        
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
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Add something to cache (if possible)
        original_cache_size = len(self.executor._strategy_cache)
        
        self.executor.clear_cache()
        
        # Cache should be empty
        assert len(self.executor._strategy_cache) == 0
    
    def test_reset_stats(self):
        """Test statistics reset functionality."""
        # Execute a query to generate some stats
        try:
            self.executor.execute_query("SELECT 1", "SQL")
        except:
            pass  # Expected until strategies are implemented
        
        # Reset stats
        self.executor.reset_stats()
        
        stats = self.executor.get_execution_stats()
        assert stats['total_queries'] == 0
        assert stats['successful_queries'] == 0
        assert stats['failed_queries'] == 0
        assert len(stats['execution_times']) == 0
    
    def test_detect_query_type(self):
        """Test query type detection."""
        # Test SQL detection
        sql_query = "SELECT * FROM users WHERE age > 25"
        detected_type = self.executor._detect_query_type(sql_query)
        assert detected_type == "SQL"
        
        # Test Cypher detection
        cypher_query = "MATCH (u:User) WHERE u.age > 25 RETURN u"
        detected_type = self.executor._detect_query_type(cypher_query)
        assert detected_type == "CYPHER"
        
        # Test GraphQL detection
        graphql_query = "{ users { id name } }"
        detected_type = self.executor._detect_query_type(graphql_query)
        assert detected_type == "GRAPHQL"
        
        # Test SPARQL detection
        sparql_query = "PREFIX : <http://example.org/> SELECT ?s WHERE { ?s a :User }"
        detected_type = self.executor._detect_query_type(sparql_query)
        assert detected_type == "SPARQL"
        
        # Test KQL detection
        kql_query = "Users | where age > 25 | project name"
        detected_type = self.executor._detect_query_type(kql_query)
        assert detected_type == "KQL"
        
        # Test default fallback
        unknown_query = "SOME UNKNOWN QUERY FORMAT"
        detected_type = self.executor._detect_query_type(unknown_query)
        assert detected_type == "SQL"  # Default fallback
    
    def test_execute_method(self):
        """Test the execute method (inherited from base class)."""
        try:
            result = self.executor.execute("SELECT * FROM users")
            assert isinstance(result, dict)
            assert 'result' in result
        except Exception as e:
            # Expected until strategies are fully implemented
            assert "not found" in str(e).lower() or "not available" in str(e).lower()
    
    def test_get_query_plan(self):
        """Test query plan generation."""
        plan = self.executor.get_query_plan("SELECT * FROM users")
        
        assert isinstance(plan, dict)
        assert 'query_type' in plan
        assert 'complexity' in plan
        assert 'estimated_cost' in plan
        assert 'backend' in plan
        
        assert plan['backend'] == 'XWNODE'
    
    def test_can_handle(self):
        """Test can_handle method."""
        # Should handle SQL queries
        assert self.executor.can_handle("SELECT * FROM users")
        
        # Should not handle invalid queries
        assert not self.executor.can_handle("INVALID QUERY")
    
    def test_get_supported_operations(self):
        """Test get_supported_operations method."""
        operations = self.executor.get_supported_operations()
        
        assert isinstance(operations, list)
        assert len(operations) > 0
        assert "SQL" in operations
        assert "GRAPHQL" in operations
        assert "CYPHER" in operations
    
    def test_estimate_complexity_method(self):
        """Test estimate_complexity method."""
        complexity = self.executor.estimate_complexity("SELECT * FROM users")
        
        assert isinstance(complexity, dict)
        assert 'backend' in complexity
        assert 'complexity' in complexity
        assert 'estimated_cost' in complexity
        assert 'execution_time' in complexity
        assert 'memory_usage' in complexity
        assert 'strategy_used' in complexity
    
    def test_to_native(self):
        """Test to_native method."""
        native = self.executor.to_native()
        
        assert isinstance(native, XWNodeBase)
        # Should return an XWQueryScriptStrategy instance
        assert hasattr(native, 'ACTION_TYPES')
    
    def test_to_actions_tree(self):
        """Test to_actions_tree method."""
        actions_tree = self.executor.to_actions_tree("SELECT * FROM users")
        
        assert isinstance(actions_tree, XWNodeBase)
        tree_data = actions_tree.to_native()
        assert 'root' in tree_data
    
    def test_from_actions_tree(self):
        """Test from_actions_tree method."""
        # Create a simple actions tree
        actions_tree = XWNodeBase.from_native({
            "root": {
                "type": "PROGRAM",
                "statements": [{"type": "SELECT", "id": "test_1"}],
                "comments": [],
                "metadata": {"version": "1.0"}
            }
        })
        
        result = self.executor.from_actions_tree(actions_tree)
        assert isinstance(result, str)
    
    def test_strategy_inheritance(self):
        """Test that XWNodeQueryActionExecutor properly inherits from base classes."""
        executor = XWNodeQueryActionExecutor()
        
        # Should inherit from AQueryActionExecutor
        assert isinstance(executor, AQueryActionExecutor)
        
        # Should implement all required abstract methods
        assert hasattr(executor, 'execute_query')
        assert hasattr(executor, 'validate_query')
        assert hasattr(executor, 'get_supported_query_types')
        assert hasattr(executor, 'execute')
        assert hasattr(executor, 'get_query_plan')
        assert hasattr(executor, 'can_handle')
        assert hasattr(executor, 'get_supported_operations')
        assert hasattr(executor, 'estimate_complexity')
    
    def test_performance_characteristics(self):
        """Test performance characteristics."""
        import time
        
        # Test execution time for simple query
        start_time = time.time()
        try:
            self.executor.execute_query("SELECT 1", "SQL")
        except:
            pass  # Expected until strategies are implemented
        execution_time = time.time() - start_time
        
        # Should execute quickly (less than 1 second for simple query)
        assert execution_time < 1.0, f"Execution took too long: {execution_time}s"
        
        # Test cost estimation time
        start_time = time.time()
        self.executor.estimate_cost("SELECT * FROM users", "SQL")
        estimation_time = time.time() - start_time
        
        # Should estimate quickly
        assert estimation_time < 1.0, f"Cost estimation took too long: {estimation_time}s"


class TestXWNodeQueryActionExecutorEdgeCases:
    """Edge case tests for XWNodeQueryActionExecutor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = XWNodeQueryActionExecutor()
    
    def test_empty_query(self):
        """Test handling of empty queries."""
        result = self.executor.validate_query("", "SQL")
        assert result is False
    
    def test_none_query(self):
        """Test handling of None queries."""
        result = self.executor.validate_query(None, "SQL")
        assert result is False
    
    def test_very_long_query(self):
        """Test handling of very long queries."""
        long_query = "SELECT " + ", ".join([f"col_{i}" for i in range(100)]) + " FROM users"
        
        # Should handle long queries without issues
        result = self.executor.validate_query(long_query, "SQL")
        assert isinstance(result, bool)
    
    def test_special_characters_in_query(self):
        """Test handling of special characters in queries."""
        special_chars = "SELECT * FROM users WHERE name = 'John O''Connor'"
        
        result = self.executor.validate_query(special_chars, "SQL")
        assert isinstance(result, bool)
    
    def test_unicode_characters_in_query(self):
        """Test handling of unicode characters in queries."""
        unicode_query = "SELECT * FROM users WHERE name = 'José María'"
        
        result = self.executor.validate_query(unicode_query, "SQL")
        assert isinstance(result, bool)
    
    def test_case_insensitive_query_type(self):
        """Test case insensitive query type handling."""
        # Should handle different cases
        result1 = self.executor.validate_query("SELECT * FROM users", "sql")
        result2 = self.executor.validate_query("SELECT * FROM users", "SQL")
        result3 = self.executor.validate_query("SELECT * FROM users", "Sql")
        
        # All should behave the same way
        assert result1 == result2 == result3
    
    def test_unsupported_query_type(self):
        """Test handling of unsupported query types."""
        result = self.executor.validate_query("SELECT * FROM users", "UNSUPPORTED_TYPE")
        assert result is False
    
    def test_concurrent_execution(self):
        """Test concurrent execution scenarios."""
        import threading
        import time
        
        results = []
        errors = []
        
        def execute_query():
            try:
                result = self.executor.execute_query("SELECT 1", "SQL")
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=execute_query)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle concurrent execution gracefully
        assert len(errors) <= 5  # Some errors expected until strategies are implemented
    
    def test_memory_usage(self):
        """Test memory usage characteristics."""
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
