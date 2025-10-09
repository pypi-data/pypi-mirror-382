"""
Test A+ Usability Improvements for xNode Library

This module tests all the A+ improvements implemented:
1. Preset-based initialization
2. Zero-overhead error handling
3. Consistent API behavior
4. XDATA_OPTIMIZED strategy
5. Best practice error messages
"""

import pytest
import time
from typing import Dict, Any

from src.xlib.xnode import xNode
from src.xlib.xnode.strategies.types import (
    get_preset, list_presets, NodeMode, EdgeMode, NodeTrait,
    TREE_GRAPH_HYBRID  # New renamed mode
)
from src.xlib.xnode.errors import (
    xNodeError, xNodePathError, xNodeTypeError, xNodeValueError,
    ErrorFactory, xNodeUnsupportedCapabilityError
)


class TestPresetSystem:
    """Test the A+ preset-based initialization system."""
    
    def test_preset_list_available(self):
        """Test that all presets are available."""
        presets = list_presets()
        expected_presets = [
            'DATA_INTERCHANGE_OPTIMIZED', 'DEFAULT', 'PURE_TREE', 'TREE_GRAPH_MIX',
            'FAST_LOOKUP', 'MEMORY_EFFICIENT', 'SOCIAL_GRAPH', 'ANALYTICS',
            'SEARCH_ENGINE', 'TIME_SERIES', 'SPATIAL_MAP', 'ML_DATASET'
        ]
        
        for preset in expected_presets:
            assert preset in presets, f"Preset {preset} should be available"
    
    def test_data_interchange_optimized_preset(self):
        """Test DATA_INTERCHANGE_OPTIMIZED preset for ultra-lightweight performance."""
        data = {"api": {"timeout": 30, "retries": 3}, "cache": {"size": 1000}}
        node = xNode(data, preset='DATA_INTERCHANGE_OPTIMIZED')
        
        # Test basic functionality
        assert node.find('api.timeout').value == 30
        assert node['api']['retries'].value == 3
        assert node.get('cache.size').value == 1000
        
        # Test that graph operations are disabled
        with pytest.raises(xNodeUnsupportedCapabilityError) as exc_info:
            _ = node.edges
        
        assert "graph_operations" in str(exc_info.value)
        assert "Use preset='SOCIAL_GRAPH'" in str(exc_info.value)
        
        # Test performance stats
        stats = node.get_performance_stats()
        assert stats['preset'] == 'DATA_INTERCHANGE_OPTIMIZED'
        assert stats['capabilities']['graph_enabled'] is False
        assert stats['capabilities']['data_interchange_optimized'] is True
    
    def test_social_graph_preset(self):
        """Test SOCIAL_GRAPH preset with graph capabilities."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        node = xNode(data, preset='SOCIAL_GRAPH')
        
        # Test basic functionality
        assert node.find('users.0.name').value == "Alice"
        
        # Test that graph operations are enabled
        assert hasattr(node, 'edges')
        assert hasattr(node, 'neighbors')
        assert hasattr(node, 'connect')
        
        # Test performance stats
        stats = node.get_performance_stats()
        assert stats['preset'] == 'SOCIAL_GRAPH'
        assert stats['capabilities']['graph_enabled'] is True
    
    def test_invalid_preset_error(self):
        """Test error handling for invalid preset names."""
        with pytest.raises(xNodeValueError) as exc_info:
            xNode({}, preset='INVALID_PRESET')
        
        error = exc_info.value
        assert "Unknown preset 'INVALID_PRESET'" in str(error)
        assert "Available presets:" in str(error)
        assert "DATA_INTERCHANGE_OPTIMIZED" in str(error)
    
    def test_preset_override(self):
        """Test that preset values can be overridden."""
        data = {"test": "data"}
        node = xNode(data, preset='FAST_LOOKUP', node_traits=NodeTrait.INDEXED)
        
        # Should still work with override
        assert node.find('test').value == "data"


class TestConsistentNavigation:
    """Test the A+ consistent navigation API."""
    
    def test_find_vs_find_strict(self):
        """Test consistent behavior between find() and find_strict()."""
        data = {"users": [{"name": "Alice", "age": 30}]}
        node = xNode(data, preset='DEFAULT')
        
        # Valid path - both should work
        result1 = node.find('users.0.name')
        result2 = node.find_strict('users.0.name')
        assert result1.value == result2.value == "Alice"
        
        # Invalid path - find returns None, find_strict raises
        assert node.find('users.0.nonexistent') is None
        
        with pytest.raises(xNodePathError) as exc_info:
            node.find_strict('users.0.nonexistent')
        
        error = exc_info.value
        assert "Path navigation failed" in str(error)
        assert "nonexistent" in str(error)
        assert "not_found" in str(error)
    
    def test_get_with_default(self):
        """Test consistent get() behavior with defaults."""
        node = xNode({"existing": "value"}, preset='DEFAULT')
        
        # Existing key
        result = node.get('existing')
        assert result.value == "value"
        
        # Non-existing key with default
        result = node.get('nonexistent', 'default_value')
        assert result.value == "default_value"
        
        # Non-existing key without default
        result = node.get('nonexistent')
        assert result is None
    
    def test_zero_overhead_success_path(self):
        """Test that success path has minimal overhead."""
        data = {"test": {"nested": {"value": 42}}}
        node = xNode(data, preset='FAST_LOOKUP')
        
        # Time successful operations
        start_time = time.time()
        for _ in range(1000):
            result = node.find('test.nested.value')
            assert result.value == 42
        success_time = time.time() - start_time
        
        # Should be very fast (less than 1ms per operation)
        assert success_time < 1.0, f"Success path too slow: {success_time:.3f}s for 1000 operations"


class TestErrorHandling:
    """Test the A+ best practice error handling system."""
    
    def test_rich_path_errors(self):
        """Test rich context in path errors."""
        node = xNode({"users": ["Alice", "Bob"]}, preset='DEFAULT')
        
        # Test key not found with suggestions
        with pytest.raises(xNodePathError) as exc_info:
            node.find_strict('user')  # Typo: should be 'users'
        
        error = exc_info.value
        assert error.reason == "not_found"
        assert error.path == "user"
        assert "Did you mean: users?" in str(error)
    
    def test_type_mismatch_errors(self):
        """Test type mismatch errors with clear messages."""
        node = xNode({"value": 42}, preset='DEFAULT')
        
        # Try to access child of leaf node
        with pytest.raises(xNodePathError) as exc_info:
            node.find_strict('value.child')
        
        error = exc_info.value
        assert error.reason == "type_mismatch"
        assert "Cannot access children of leaf nodes" in str(error)
    
    def test_index_out_of_bounds_errors(self):
        """Test index out of bounds errors with helpful suggestions."""
        node = xNode([1, 2, 3], preset='DEFAULT')
        
        with pytest.raises(xNodePathError) as exc_info:
            node.find_strict('5')  # Index 5 is out of bounds
        
        error = exc_info.value
        assert error.reason == "out_of_bounds"
        assert "Valid range: 0-2" in str(error)
    
    def test_error_factory_performance(self):
        """Test that error factory creates errors efficiently."""
        start_time = time.time()
        
        for i in range(1000):
            error = ErrorFactory.path_not_found(f"path.{i}", f"segment_{i}", ["key1", "key2", "key3"])
            assert isinstance(error, xNodePathError)
        
        creation_time = time.time() - start_time
        assert creation_time < 0.1, f"Error creation too slow: {creation_time:.3f}s for 1000 errors"
    
    def test_error_chaining(self):
        """Test error chaining and fluent API."""
        error = (ErrorFactory.path_not_found("test.path", "segment")
                .add_context(operation="test", user_id=123)
                .suggest("Check your spelling")
                .suggest("Use valid keys only"))
        
        assert error.context['operation'] == "test"
        assert error.context['user_id'] == 123
        assert len(error.suggestions) == 2
        assert "Check your spelling" in error.suggestions


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing code."""
    
    def test_legacy_factory_methods(self):
        """Test that legacy factory methods still work."""
        data = {"test": "value"}
        
        # Legacy methods should map to presets
        node1 = xNode.from_native(data)
        node2 = xNode.fast(data)
        node3 = xNode.optimized(data)
        
        # All should work
        assert node1.find('test').value == "value"
        assert node2.find('test').value == "value"
        assert node3.find('test').value == "value"
    
    def test_legacy_mode_mapping(self):
        """Test that LEGACY mode maps to TREE_GRAPH_HYBRID."""
        from src.xlib.xnode.strategies.types import LEGACY
        
        # LEGACY should map to TREE_GRAPH_HYBRID
        assert LEGACY == TREE_GRAPH_HYBRID
    
    def test_existing_api_unchanged(self):
        """Test that existing API methods still work."""
        data = {"users": [{"name": "Alice"}], "config": {"debug": True}}
        node = xNode(data, preset='DEFAULT')
        
        # Test all existing methods
        assert len(node) == 2
        assert node.type == 'dict'
        assert node.size == 2
        assert 'users' in node
        assert node.has('config')
        
        # Test iteration
        keys = list(node.keys())
        assert 'users' in keys and 'config' in keys
        
        # Test items
        items = dict(node.items())
        assert len(items) == 2


class TestPerformanceOptimizations:
    """Test performance optimizations in A+ implementation."""
    
    def test_data_interchange_optimized_performance(self):
        """Test DATA_INTERCHANGE_OPTIMIZED performance characteristics."""
        # Create large dataset
        large_data = {f"item_{i}": {"value": i, "data": f"test_{i}"} for i in range(1000)}
        
        # Time creation
        start_time = time.time()
        node = xNode(large_data, preset='DATA_INTERCHANGE_OPTIMIZED')
        creation_time = time.time() - start_time
        
        # Should be fast
        assert creation_time < 1.0, f"Creation too slow: {creation_time:.3f}s"
        
        # Time access operations
        start_time = time.time()
        for i in range(100):
            result = node.find(f'item_{i}.value')
            assert result.value == i
        access_time = time.time() - start_time
        
        # Should be very fast
        assert access_time < 0.1, f"Access too slow: {access_time:.3f}s for 100 operations"
        
        # Test memory efficiency (should be minimal)
        stats = node.get_performance_stats()
        assert stats['capabilities']['data_interchange_optimized'] is True
    
    def test_copy_on_write_behavior(self):
        """Test copy-on-write semantics (when implemented)."""
        original_data = {"shared": {"data": "original"}}
        node1 = xNode(original_data, preset='DATA_INTERCHANGE_OPTIMIZED')
        
        # Create a copy with modification
        node2 = node1.set('shared.data', 'modified', in_place=False)
        
        # Original should be unchanged
        assert node1.find('shared.data').value == 'original'
        assert node2.find('shared.data').value == 'modified'


class TestIntegrationWithXData:
    """Test integration patterns for xData library."""
    
    def test_data_interchange_factory_method(self):
        """Test the dedicated data interchange factory method."""
        data = {"config": {"api_key": "secret", "timeout": 30}}
        node = xNode.data_interchange_optimized(data)
        
        assert node.find('config.api_key').value == "secret"
        assert node.get_performance_mode() == 'DATA_INTERCHANGE_OPTIMIZED'
    
    def test_data_interchange_patterns(self):
        """Test common data interchange patterns."""
        # JSON-like data
        json_data = {
            "version": "1.0",
            "data": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"}
            ],
            "metadata": {"created": "2023-01-01"}
        }
        
        node = xNode(json_data, preset='DATA_INTERCHANGE_OPTIMIZED')
        
        # Test navigation patterns common in data interchange
        assert node.find('version').value == "1.0"
        assert node.find('data.0.name').value == "item1"
        assert node.find('metadata.created').value == "2023-01-01"
        
        # Test modification patterns
        updated = node.set('data.0.processed', True, in_place=False)
        assert updated.find('data.0.processed').value is True
        assert node.find('data.0.processed') is None  # Original unchanged


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, '-v'])
