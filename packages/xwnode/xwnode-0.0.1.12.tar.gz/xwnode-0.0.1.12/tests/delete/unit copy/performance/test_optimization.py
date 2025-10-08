#!/usr/bin/env python3
"""
Test Performance Optimization System for xNode.

Tests comprehensive optimization features across all AUTO-3 phases.
"""

import sys
import os
import pytest
import time
from typing import Dict, Any, List

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode
from src.xlib.xnode.config import (
    AdvancedCache, BatchProcessor, MemoryOptimizer, AdaptiveOptimizer,
    optimize_for_size, cache_result, batch_operation, xNodePerformanceManager
)
from src.xlib.xnode.errors import xNodeError


class TestPerformanceOptimizer:
    """Test core performance optimizer functionality."""
    
    def test_performance_manager_initialization(self):
        """Test performance manager initializes correctly."""
        node = xNode({"test": "data"})
        manager = xNodePerformanceManager(node)
        
        assert manager._advanced_cache is not None
        assert manager._batch_processor is not None
        assert manager._memory_optimizer is not None
        assert manager._adaptive_optimizer is not None
    
    def test_optimization_components_access(self):
        """Test access to optimization components."""
        manager = xNodePerformanceManager()
        
        # Test component access
        cache = manager.get_cache()
        assert isinstance(cache, AdvancedCache)
        
        processor = manager.get_batch_processor()
        assert isinstance(processor, BatchProcessor)
        
        memory_opt = manager.get_memory_optimizer()
        assert isinstance(memory_opt, MemoryOptimizer)
        
        adaptive_opt = manager.get_adaptive_optimizer()
        assert isinstance(adaptive_opt, AdaptiveOptimizer)
    
    def test_optimization_decorator(self):
        """Test optimization decorator functionality."""
        
        @optimize_for_size(threshold=100)
        def test_function(data):
            return len(data)
        
        # Test with small data
        result = test_function([1, 2, 3, 4, 5])
        assert result == 5
        
        # Test with larger data
        large_data = list(range(1000))
        result = test_function(large_data)
        assert result == 1000


class TestAdvancedCache:
    """Test advanced caching functionality."""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        cache = AdvancedCache(maxsize=10, ttl=1.0)
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test miss
        assert cache.get("nonexistent") is None
        
        # Test statistics
        stats = cache.stats()
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = AdvancedCache(maxsize=3, ttl=10.0)
        
        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add new item, should evict key2 (least recently used)
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Should still exist
        assert cache.get("key2") is None      # Should be evicted
        assert cache.get("key3") == "value3"  # Should still exist
        assert cache.get("key4") == "value4"  # Should exist
    
    def test_cache_ttl_expiration(self):
        """Test TTL-based expiration."""
        cache = AdvancedCache(maxsize=10, ttl=0.1)  # 100ms TTL
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None  # Should be expired
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = AdvancedCache(maxsize=10, ttl=10.0)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.get("key1") == "value1"
        
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestBatchProcessor:
    """Test batch processing functionality."""
    
    def test_batch_processing(self):
        """Test basic batch processing."""
        processor = BatchProcessor(batch_size=10)
        
        # Test data
        items = list(range(25))  # 25 items, should process in 3 batches
        
        def double_processor(x):
            return x * 2
        
        results = processor.process_batch(items, double_processor)
        
        assert len(results) == 25
        assert results[0] == 0
        assert results[10] == 20
        assert results[24] == 48
    
    def test_batch_update(self):
        """Test batch dictionary updates."""
        processor = BatchProcessor(batch_size=5)
        
        target = {"existing": "value"}
        updates = {f"key{i}": f"value{i}" for i in range(12)}
        
        result = processor.batch_update(target, updates)
        
        assert result["existing"] == "value"
        assert len(result) == 13  # 1 existing + 12 new
        assert result["key0"] == "value0"
        assert result["key11"] == "value11"
    
    def test_large_batch_processing(self):
        """Test processing of large batches."""
        processor = BatchProcessor(batch_size=100)
        
        # Large dataset
        items = list(range(2500))
        
        def square_processor(x):
            return x ** 2
        
        start_time = time.time()
        results = processor.process_batch(items, square_processor)
        end_time = time.time()
        
        assert len(results) == 2500
        assert results[0] == 0
        assert results[50] == 2500
        assert end_time - start_time < 2.0  # Should complete quickly


class TestLinearStructureOptimizer:
    """Test linear structure optimizations."""
    
    def test_list_optimization(self):
        """Test list operation optimization."""
        optimizer = LinearStructureOptimizer()
        
        # Small list - should return unchanged
        small_list = [1, 2, 3, 4, 5]
        result = optimizer.optimize_list_operations(small_list)
        assert result == small_list
        
        # Large list - should apply optimizations
        large_list = list(range(1500))
        result = optimizer.optimize_list_operations(large_list)
        assert len(result) == len(large_list)
        assert result[0] == 0
        assert result[-1] == 1499
    
    def test_stack_optimization(self):
        """Test stack operation optimization."""
        optimizer = LinearStructureOptimizer()
        
        stack_data = [1, 2, 3, 4, 5]
        result = optimizer.optimize_stack_operations(stack_data)
        
        assert isinstance(result, list)
        assert len(result) == 5


class TestTreeStructureOptimizer:
    """Test tree structure optimizations."""
    
    def test_trie_optimization(self):
        """Test trie operation optimization."""
        optimizer = TreeStructureOptimizer()
        
        trie_data = {
            "root": {"children": {"a": {"is_end": True}}},
            "node_a": {"value": "test"}
        }
        
        result = optimizer.optimize_trie_operations(trie_data)
        assert isinstance(result, dict)
        assert "root" in result
    
    def test_heap_optimization(self):
        """Test heap operation optimization."""
        optimizer = TreeStructureOptimizer()
        
        # Small heap - should return unchanged
        small_heap = [3, 1, 4, 1, 5]
        result = optimizer.optimize_heap_operations(small_heap)
        assert len(result) == len(small_heap)
        
        # Large heap - should apply heapify optimization
        large_heap = list(range(100, 0, -1))  # Reverse order
        result = optimizer.optimize_heap_operations(large_heap)
        assert len(result) == 100
        assert result[0] == 1  # Should be heapified (min at root)


class TestGraphStructureOptimizer:
    """Test graph structure optimizations."""
    
    def test_graph_traversal_optimization(self):
        """Test graph traversal optimization."""
        optimizer = GraphStructureOptimizer()
        
        # Simple graph
        graph_data = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": []
        }
        
        # Test BFS
        result = optimizer.optimize_graph_traversal(graph_data, "A", "bfs")
        assert isinstance(result, list)
        assert "A" in result
        assert len(result) <= 4
        
        # Test DFS
        result = optimizer.optimize_graph_traversal(graph_data, "A", "dfs")
        assert isinstance(result, list)
        assert "A" in result
    
    def test_large_graph_optimization(self):
        """Test optimization for large graphs."""
        optimizer = GraphStructureOptimizer()
        
        # Create large graph
        large_graph = {}
        for i in range(1500):
            neighbors = []
            if i < 1499:
                neighbors.append(str(i + 1))
            if i > 0:
                neighbors.append(str(i - 1))
            large_graph[str(i)] = neighbors
        
        result = optimizer.optimize_graph_traversal(large_graph, "0", "bfs")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_neural_graph_optimization(self):
        """Test neural graph optimization."""
        optimizer = GraphStructureOptimizer()
        
        operations = {
            "input1": {"type": "input", "inputs": [], "outputs": ["add1"]},
            "input2": {"type": "input", "inputs": [], "outputs": ["add1"]},
            "add1": {"type": "add", "inputs": ["input1", "input2"], "outputs": []}
        }
        
        result = optimizer.optimize_neural_graph(operations)
        assert isinstance(result, dict)
        assert len(result) == 3
        
        # Check execution order is assigned
        for op_id, op_data in result.items():
            assert 'execution_order' in op_data


class TestMemoryOptimizer:
    """Test memory optimization functionality."""
    
    def test_memory_optimization(self):
        """Test memory usage optimization."""
        optimizer = MemoryOptimizer()
        
        # Test linear structure optimization
        linear_data = list(range(500))
        result = optimizer.optimize_memory_usage(linear_data, "linear")
        assert isinstance(result, list)
        
        # Test tree structure optimization
        tree_data = {"key1": "value1", "key2": {"nested": "value"}}
        result = optimizer.optimize_memory_usage(tree_data, "tree")
        assert isinstance(result, dict)
    
    def test_memory_cleanup(self):
        """Test memory cleanup functionality."""
        optimizer = MemoryOptimizer()
        
        # This should not raise an exception
        optimizer.cleanup_memory()


class TestAdaptiveOptimizer:
    """Test adaptive optimization functionality."""
    
    def test_pattern_recording(self):
        """Test operation pattern recording."""
        optimizer = AdaptiveOptimizer()
        
        # Record some operations
        optimizer.record_operation("insert", 100, 0.1)
        optimizer.record_operation("insert", 150, 0.15)
        optimizer.record_operation("search", 1000, 0.5)
        
        # Check patterns were recorded
        assert len(optimizer._usage_patterns) > 0
        assert len(optimizer._performance_history) > 0
    
    def test_optimization_strategy(self):
        """Test optimization strategy selection."""
        optimizer = AdaptiveOptimizer()
        
        # Record patterns for different operation types
        optimizer.record_operation("fast_op", 100, 0.05)  # Fast operation
        optimizer.record_operation("slow_op", 100, 2.0)   # Slow operation
        
        # Test strategy selection
        fast_strategy = optimizer.get_optimization_strategy("fast_op", 100)
        slow_strategy = optimizer.get_optimization_strategy("slow_op", 100)
        
        assert fast_strategy in ["minimal", "moderate"]
        assert slow_strategy == "aggressive"
    
    def test_pattern_based_optimization(self):
        """Test pattern-based optimization configuration."""
        optimizer = AdaptiveOptimizer()
        
        # Record patterns
        optimizer.record_operation("test_op", 1500, 0.3)
        
        config = optimizer.optimize_based_on_patterns("test_op", 1500)
        
        assert isinstance(config, dict)
        assert 'strategy' in config
        assert 'use_caching' in config
        assert 'use_batching' in config
        assert config['use_batching'] is True  # Should enable for size > 1000


class TestUniversalOptimizer:
    """Test universal optimizer integration."""
    
    def test_structure_optimization(self):
        """Test structure-specific optimization."""
        optimizer = universal_optimizer
        
        # Test linear structure
        linear_data = [1, 2, 3, 4, 5]
        result = optimizer.optimize_structure("stack", "push", linear_data)
        assert isinstance(result, list)
        
        # Test tree structure
        tree_data = {"root": {"children": {}}}
        result = optimizer.optimize_structure("trie", "insert", tree_data)
        assert isinstance(result, dict)
    
    def test_performance_stats(self):
        """Test performance statistics collection."""
        optimizer = universal_optimizer
        
        stats = optimizer.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert 'global_cache' in stats
        assert 'memory_usage' in stats
    
    def test_cleanup(self):
        """Test optimizer cleanup."""
        optimizer = universal_optimizer
        
        # This should not raise an exception
        optimizer.cleanup()


class TestxNodeOptimization:
    """Test xNode optimization integration."""
    
    def test_optimize_for_operation(self):
        """Test xNode operation optimization."""
        node = xNode.from_native([1, 2, 3, 4, 5])
        
        optimized = node.optimize_for_operation("iterate", data_size_hint=5)
        assert isinstance(optimized, xNode)
        assert optimized.to_native() == [1, 2, 3, 4, 5]
    
    def test_bulk_update(self):
        """Test bulk update optimization."""
        data = {"a": 1, "b": 2, "c": 3}
        node = xNode.from_native(data)
        
        updates = {
            "a": 10,
            "b": 20,
            "d": 40
        }
        
        result = node.bulk_update(updates)
        
        assert result.find("a").value == 10
        assert result.find("b").value == 20
        assert result.find("c").value == 3
        assert result.find("d").value == 40
    
    def test_large_bulk_update(self):
        """Test bulk update with large dataset."""
        node = xNode.from_native({})
        
        # Large update set
        updates = {f"key{i}": i for i in range(250)}
        
        start_time = time.time()
        result = node.bulk_update(updates)
        end_time = time.time()
        
        assert len(result) == 250
        assert result.find("key0").value == 0
        assert result.find("key249").value == 249
        assert end_time - start_time < 2.0  # Should complete efficiently
    
    def test_cached_find(self):
        """Test cached find functionality."""
        data = {"deep": {"nested": {"path": {"value": "found"}}}}
        node = xNode.from_native(data)
        
        # First call - should cache result
        result1 = node.cached_find("deep.nested.path.value")
        assert result1.value == "found"
        
        # Second call - should use cache
        result2 = node.cached_find("deep.nested.path.value")
        assert result2.value == "found"
        
        # Results should be equivalent
        assert result1.value == result2.value
    
    def test_performance_stats(self):
        """Test xNode performance statistics."""
        node = xNode.from_native({"a": 1, "b": [1, 2, 3]})
        
        stats = node.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert 'node_info' in stats
        assert 'global_cache' in stats
        
        node_info = stats['node_info']
        assert node_info['node_type'] == 'dict'
        assert node_info['is_dict'] is True
        assert node_info['data_size'] == 2
    
    def test_cleanup_performance_caches(self):
        """Test performance cache cleanup."""
        node = xNode.from_native([1, 2, 3])
        
        # This should not raise an exception
        node.cleanup_performance_caches()
        
        # Caches should be cleared
        assert node._hash_cache is None
        assert node._type_cache is None


class TestOptimizationIntegration:
    """Test optimization integration with data structures."""
    
    def test_linear_structure_optimization(self):
        """Test optimization in linear structures."""
        node = xNode.from_native([])
        stack = node.as_stack()
        
        # Add many items (should trigger optimization)
        for i in range(1200):
            stack.push(i)
        
        assert stack.size() == 1200
        assert stack.peek() == 1199
    
    def test_trie_optimization(self):
        """Test optimization in trie structure."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        # Add many words (should trigger optimization)
        words = [f"word{i}" for i in range(600)]
        for word in words:
            trie.insert(word)
        
        assert trie.size() == 600
        assert trie.contains("word0")
        assert trie.contains("word599")
    
    def test_neural_graph_optimization(self):
        """Test optimization in neural graph."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Build larger neural network (should trigger optimization)
        neural.add_operation("input", "input", value=1.0)
        
        for i in range(60):  # Should trigger optimization at 50
            neural.add_operation(f"op{i}", "linear", weight=1.0, bias=0.0)
            if i == 0:
                neural.add_edge("input", f"op{i}")
            else:
                neural.add_edge(f"op{i-1}", f"op{i}")
        
        neural.compile_graph()
        result = neural.forward()
        
        assert len(result) == 61  # input + 60 operations
        assert "op59" in result
    
    def test_performance_under_load(self):
        """Test performance optimization under heavy load."""
        # Create complex nested structure
        data = {}
        for i in range(100):
            data[f"section{i}"] = {
                "items": [f"item{j}" for j in range(50)],
                "metadata": {"id": i, "type": "section"}
            }
        
        node = xNode.from_native(data)
        
        # Perform many operations
        start_time = time.time()
        
        for i in range(50):
            # Access different paths
            node.find(f"section{i}.items.0")
            node.find(f"section{i}.metadata.id")
        
        # Bulk update
        updates = {f"section{i}.metadata.processed": True for i in range(25)}
        node.bulk_update(updates)
        
        end_time = time.time()
        
        # Should complete efficiently
        assert end_time - start_time < 3.0
        
        # Verify data integrity
        assert node.find("section0.items.0").value == "item0"
        assert node.find("section0.metadata.id").value == 0
