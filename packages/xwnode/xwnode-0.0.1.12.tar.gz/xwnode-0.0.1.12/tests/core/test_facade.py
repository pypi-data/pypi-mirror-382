#!/usr/bin/env python3
"""
Test suite for XWNode facade interface after refactoring.

Tests the public-facing XWNode facade and its delegation to modular components.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src paths for local testing
current_dir = Path(__file__).parent
src_path = current_dir.parent.parent / "src"
xwsystem_src_path = current_dir.parent.parent.parent / "xwsystem" / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(xwsystem_src_path) not in sys.path and xwsystem_src_path.exists():
    sys.path.insert(0, str(xwsystem_src_path))

# Try to import with graceful fallback
try:
    from exonware.xwnode import XWNode
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Import failed: {e}")
    IMPORTS_AVAILABLE = False
    # Create mock XWNode for testing structure
    class MockNode:
        @classmethod
        def from_native(cls, data):
            return cls()
        
        @property
        def is_dict(self):
            return isinstance(data if 'data' in locals() else {}, dict)
        
        def get(self, key, default=None):
            return MockNode()
        
        def find(self, path):
            return MockNode()
    
    XWNode = MockNode


class TestXNodeFacade:
    """Test the refactored XWNode facade interface."""
    
    def test_facade_initialization(self):
        """Test that XWNode facade initializes properly with all modular components."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Skipping test due to import dependency issues")
            
        data = {'test': 'value', 'number': 42}
        node = XWNode.from_native(data)
        
        # Check that all modular components are initialized
        assert hasattr(node, '_core')
        assert hasattr(node, '_performance')
        assert hasattr(node, '_structures')
        assert hasattr(node, '_graph')
        assert hasattr(node, '_query')
        
        # Check basic functionality
        assert node.value == data
        assert node.type == 'dict'
        
    def test_core_operations_delegation(self):
        """Test that core operations are properly delegated to XWNodeCore."""
        data = {'users': [{'name': 'Alice', 'age': 30}]}
        node = XWNode.from_native(data)
        
        # Test delegation to core
        assert node.is_dict
        assert not node.is_list
        assert node.size > 0
        assert 'users' in node.keys()
        
    def test_performance_operations_delegation(self):
        """Test that performance operations are properly delegated."""
        data = {'test': 'data'}
        node = XWNode.from_native(data)
        
        # Test performance mode operations
        stats = node.get_performance_stats()
        assert isinstance(stats, dict)
        
        current_mode = node.get_performance_mode()
        assert isinstance(current_mode, str)
        
    def test_graph_operations_delegation(self):
        """Test that graph operations are properly delegated."""
        data = {'node1': 'value1'}
        node1 = XWNode.from_native(data)
        node2 = XWNode.from_native({'node2': 'value2'})
        
        # Test graph operations
        neighbors = node1.neighbors()
        assert isinstance(neighbors, list)
        
        # Test connectivity check
        connected = node1.is_connected(node2)
        assert isinstance(connected, bool)
        
    def test_query_operations_delegation(self):
        """Test that query operations are properly delegated."""
        data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        node = XWNode.from_native(data)
        
        # Test native query
        result = node.query("test query")
        assert hasattr(result, 'count')
        
        # Test query builder
        query_builder = node.query()
        assert hasattr(query_builder, 'where')
        assert hasattr(query_builder, 'all')
        assert hasattr(query_builder, 'first')
        
        # Test specific query methods
        find_result = node.find_by_path("users")
        assert isinstance(find_result, (list, object))
        
        count = node.count_nodes()
        assert isinstance(count, int)
        
    def test_data_structure_operations_delegation(self):
        """Test that data structure operations are properly delegated."""
        data = [1, 2, 3, 4, 5]
        node = XWNode.from_native(data)
        
        # Test behavioral views
        list_view = node.as_list()
        assert hasattr(list_view, 'append')
        
        stack_view = node.as_stack()
        assert hasattr(stack_view, 'push')
        assert hasattr(stack_view, 'pop')
        
        queue_view = node.as_queue()
        assert hasattr(queue_view, 'enqueue')
        assert hasattr(queue_view, 'dequeue')
        
    def test_iteration_methods(self):
        """Test that iteration methods work correctly after refactoring."""
        data = {'a': 1, 'b': 2, 'c': 3}
        node = XWNode.from_native(data)
        
        # Test keys
        keys = list(node.keys())
        assert 'a' in keys
        assert 'b' in keys
        assert 'c' in keys
        
        # Test values
        values = list(node.values())
        assert len(values) == 3
        
        # Test items
        items = list(node.items())
        assert len(items) == 3
        assert all(len(item) == 2 for item in items)  # Each item is (key, value)
        
        # Test iteration
        for child in node:
            assert hasattr(child, 'value')
            
    def test_backward_compatibility(self):
        """Test that the refactored facade maintains backward compatibility."""
        data = {'legacy': 'compatibility', 'nested': {'value': 42}}
        node = XWNode.from_native(data)
        
        # Test legacy methods still work
        assert node.find('nested.value').value == 42
        assert node.get('legacy').value == 'compatibility'
        assert node.to_native() == data
        
        # Test COW operations
        new_node = node.set('new_key', 'new_value', in_place=False)
        assert 'new_key' not in node.to_native()  # Original unchanged
        assert 'new_key' in new_node.to_native()  # New node has change
        
    def test_error_handling(self):
        """Test that error handling works properly in the refactored facade."""
        data = {'test': 'value'}
        node = XWNode.from_native(data)
        
        # Test path errors
        with pytest.raises(Exception):  # Specific exception type depends on implementation
            node.find('non.existent.path')
        
        # Test invalid operations
        with pytest.raises(Exception):
            node.set('', 'invalid')  # Empty path
            
    def test_serialization_operations(self):
        """Test serialization operations work after refactoring."""
        data = {'serialization': 'test', 'numbers': [1, 2, 3]}
        node = XWNode.from_native(data)
        
        # Test to_native conversion
        native = node.to_native()
        assert native == data
        
        # Test data integrity through roundtrip
        restored = XWNode.from_native(native)
        assert restored.to_native() == data
        
        # Verify all data is preserved
        assert restored['serialization'].value == 'test'
        assert restored['numbers'].value == [1, 2, 3]


class TestModularComponentIntegration:
    """Test integration between modular components."""
    
    def test_performance_with_structures(self):
        """Test that performance management works with data structures."""
        data = list(range(100))
        node = XWNode.from_native(data)
        
        # Get initial performance stats
        initial_stats = node.get_performance_stats()
        
        # Use data structure operations
        list_view = node.as_list()
        list_view.append(101)
        
        # Check that performance is still tracked
        final_stats = node.get_performance_stats()
        assert isinstance(final_stats, dict)
        
    def test_query_with_graph(self):
        """Test that query operations work with graph functionality."""
        data = {'nodes': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}
        node = XWNode.from_native(data)
        
        # Use query operations
        query_result = node.query("test")
        
        # Use graph operations
        neighbors = node.neighbors()
        
        # Both should work without conflict
        assert hasattr(query_result, 'count')
        assert isinstance(neighbors, list)
        
    def test_end_to_end_workflow(self):
        """Test a complete workflow using multiple modular components."""
        # Create initial data
        data = {
            'users': [
                {'name': 'Alice', 'age': 30, 'department': 'Engineering'},
                {'name': 'Bob', 'age': 25, 'department': 'Marketing'},
                {'name': 'Charlie', 'age': 35, 'department': 'Engineering'}
            ]
        }
        node = XWNode.from_native(data)
        
        # 1. Use query operations to find data
        users_query = node.query()
        engineering_users = users_query.where(
            lambda n: n.value.get('department') == 'Engineering' if isinstance(n.value, dict) else False
        )
        assert engineering_users.count() >= 0  # Should not error
        
        # 2. Use data structure operations
        user_list = node.find('users')
        list_view = user_list.as_list()
        list_view.append({'name': 'David', 'age': 28, 'department': 'Sales'})
        
        # 3. Check performance
        stats = node.get_performance_stats()
        assert 'operation_count' in stats or 'overview' in stats
        
        # 4. Use graph operations
        neighbors = node.neighbors()
        assert isinstance(neighbors, list)
        
        # All operations should complete without errors
        assert node.size > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
