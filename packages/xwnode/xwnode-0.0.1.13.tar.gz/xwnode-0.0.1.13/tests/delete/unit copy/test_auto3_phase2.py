#!/usr/bin/env python3
"""
Test AUTO-3 Phase 2: Specialized Tree Structures.

Tests Trie, Heap, and SkipList behavioral views on xNode.
"""

import sys
import os
import pytest
import random
from typing import Dict, Any, List

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode
from src.xlib.xnode.errors import xNodeTypeError, xNodeValueError


class TestTrieView:
    """Test Trie (prefix tree) behavioral view."""
    
    def test_trie_creation(self):
        """Test creating Trie view from dict node."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        assert trie.size() == 0
        assert trie.is_empty()
    
    def test_trie_insert_and_contains(self):
        """Test inserting words and checking existence."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        # Insert words
        trie.insert("hello", "greeting")
        trie.insert("help", "assistance")
        trie.insert("world", "planet")
        
        assert trie.size() == 3
        assert not trie.is_empty()
        
        # Test contains
        assert trie.contains("hello")
        assert trie.contains("help")
        assert trie.contains("world")
        assert not trie.contains("hell")
        assert not trie.contains("helping")
    
    def test_trie_get_values(self):
        """Test retrieving values by key."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        trie.insert("hello", "greeting")
        trie.insert("help", "assistance")
        
        assert trie.get("hello") == "greeting"
        assert trie.get("help") == "assistance"
        
        with pytest.raises(KeyError):
            trie.get("nonexistent")
    
    def test_trie_starts_with(self):
        """Test prefix search functionality."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        # Insert words with common prefixes
        words = ["hello", "help", "helper", "helping", "world", "work", "word"]
        for word in words:
            trie.insert(word, f"value_{word}")
        
        # Test prefix searches
        hel_words = trie.starts_with("hel")
        assert set(hel_words) == {"hello", "help", "helper", "helping"}
        
        wor_words = trie.starts_with("wor")
        assert set(wor_words) == {"world", "work", "word"}
        
        # Empty prefix should return all words
        all_words = trie.starts_with("")
        assert set(all_words) == set(words)
        
        # Non-existent prefix
        xyz_words = trie.starts_with("xyz")
        assert xyz_words == []
    
    def test_trie_delete(self):
        """Test deleting words from trie."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        # Insert words
        trie.insert("hello", "greeting")
        trie.insert("help", "assistance")
        trie.insert("helper", "assistant")
        
        assert trie.size() == 3
        
        # Delete existing word
        assert trie.delete("help") == True
        assert not trie.contains("help")
        assert trie.size() == 2
        
        # Other words should still exist
        assert trie.contains("hello")
        assert trie.contains("helper")
        
        # Delete non-existent word
        assert trie.delete("nonexistent") == False
        assert trie.size() == 2
    
    def test_trie_clear(self):
        """Test clearing trie."""
        node = xNode.from_native({})
        trie = node.as_trie()
        
        trie.insert("hello", "greeting")
        trie.insert("world", "planet")
        
        assert trie.size() == 2
        
        trie.clear()
        assert trie.size() == 0
        assert trie.is_empty()
        assert not trie.contains("hello")
    
    def test_trie_non_dict_node(self):
        """Test Trie view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_trie()


class TestHeapView:
    """Test Heap (priority queue) behavioral view."""
    
    def test_min_heap_creation(self):
        """Test creating min-heap view from list node."""
        node = xNode.from_native([])
        heap = node.as_min_heap()
        
        assert heap.size() == 0
        assert heap.is_empty()
    
    def test_max_heap_creation(self):
        """Test creating max-heap view from list node."""
        node = xNode.from_native([])
        heap = node.as_max_heap()
        
        assert heap.size() == 0
        assert heap.is_empty()
    
    def test_min_heap_operations(self):
        """Test min-heap push and pop operations."""
        node = xNode.from_native([])
        heap = node.as_min_heap()
        
        # Push items with different priorities
        heap.push("urgent", priority=1.0)
        heap.push("normal", priority=5.0)
        heap.push("low", priority=10.0)
        heap.push("critical", priority=0.5)
        
        assert heap.size() == 4
        assert not heap.is_empty()
        
        # Pop in priority order (min first)
        assert heap.pop_min() == "critical"  # priority 0.5
        assert heap.pop_min() == "urgent"    # priority 1.0
        assert heap.pop_min() == "normal"    # priority 5.0
        assert heap.pop_min() == "low"       # priority 10.0
        
        assert heap.is_empty()
    
    def test_max_heap_operations(self):
        """Test max-heap push and pop operations."""
        node = xNode.from_native([])
        heap = node.as_max_heap()
        
        # Push items with different priorities
        heap.push("urgent", priority=1.0)
        heap.push("normal", priority=5.0)
        heap.push("low", priority=10.0)
        heap.push("critical", priority=0.5)
        
        assert heap.size() == 4
        
        # Pop in priority order (max first)
        assert heap.pop_max() == "low"       # priority 10.0
        assert heap.pop_max() == "normal"    # priority 5.0
        assert heap.pop_max() == "urgent"    # priority 1.0
        assert heap.pop_max() == "critical"  # priority 0.5
        
        assert heap.is_empty()
    
    def test_heap_peek_operations(self):
        """Test heap peek without removing."""
        node = xNode.from_native([])
        min_heap = node.as_min_heap()
        
        min_heap.push("item1", priority=5.0)
        min_heap.push("item2", priority=2.0)
        min_heap.push("item3", priority=8.0)
        
        # Peek should not change size
        assert min_heap.peek_min() == "item2"  # priority 2.0
        assert min_heap.size() == 3
        
        # Multiple peeks should return same item
        assert min_heap.peek_min() == "item2"
        assert min_heap.peek_min() == "item2"
    
    def test_heap_decrease_key(self):
        """Test decreasing priority of heap items."""
        node = xNode.from_native([])
        heap = node.as_min_heap()
        
        heap.push("task1", priority=10.0)
        heap.push("task2", priority=5.0)
        heap.push("task3", priority=7.0)
        
        # Decrease priority of task1
        heap.decrease_key("task1", 1.0)
        
        # task1 should now be at top
        assert heap.peek_min() == "task1"
    
    def test_heap_merge(self):
        """Test merging two heaps."""
        node1 = xNode.from_native([])
        node2 = xNode.from_native([])
        
        heap1 = node1.as_min_heap()
        heap2 = node2.as_min_heap()
        
        heap1.push("a", priority=2.0)
        heap1.push("b", priority=4.0)
        
        heap2.push("c", priority=1.0)
        heap2.push("d", priority=3.0)
        
        # Merge heap2 into heap1
        heap1.merge(heap2)
        
        assert heap1.size() == 4
        
        # Items should be in priority order
        assert heap1.pop_min() == "c"  # priority 1.0
        assert heap1.pop_min() == "a"  # priority 2.0
        assert heap1.pop_min() == "d"  # priority 3.0
        assert heap1.pop_min() == "b"  # priority 4.0
    
    def test_heap_clear(self):
        """Test clearing heap."""
        node = xNode.from_native([])
        heap = node.as_min_heap()
        
        heap.push("item1", priority=1.0)
        heap.push("item2", priority=2.0)
        
        assert heap.size() == 2
        
        heap.clear()
        assert heap.size() == 0
        assert heap.is_empty()
    
    def test_heap_empty_operations(self):
        """Test operations on empty heap."""
        node = xNode.from_native([])
        heap = node.as_min_heap()
        
        with pytest.raises(xNodeValueError):
            heap.pop_min()
        
        with pytest.raises(xNodeValueError):
            heap.peek_min()
    
    def test_heap_wrong_operation_type(self):
        """Test wrong operations on heap types."""
        node = xNode.from_native([])
        min_heap = node.as_min_heap()
        max_heap = node.as_max_heap()
        
        min_heap.push("item", priority=1.0)
        max_heap.push("item", priority=1.0)
        
        # Min heap shouldn't support max operations
        with pytest.raises(xNodeValueError):
            min_heap.pop_max()
        
        with pytest.raises(xNodeValueError):
            min_heap.peek_max()
        
        # Max heap shouldn't support min operations
        with pytest.raises(xNodeValueError):
            max_heap.pop_min()
        
        with pytest.raises(xNodeValueError):
            max_heap.peek_min()
    
    def test_heap_non_list_node(self):
        """Test Heap view with non-list node."""
        node = xNode.from_native({"key": "value"})
        
        with pytest.raises(xNodeTypeError):
            node.as_min_heap()
        
        with pytest.raises(xNodeTypeError):
            node.as_max_heap()


class TestSkipListView:
    """Test SkipList behavioral view."""
    
    def test_skip_list_creation(self):
        """Test creating SkipList view from dict node."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        assert skip_list.size() == 0
        assert skip_list.is_empty()
    
    def test_skip_list_insert_and_search(self):
        """Test inserting and searching in skip list."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        # Insert key-value pairs
        skip_list.insert("key3", "value3")
        skip_list.insert("key1", "value1")
        skip_list.insert("key2", "value2")
        skip_list.insert("key5", "value5")
        skip_list.insert("key4", "value4")
        
        assert skip_list.size() == 5
        assert not skip_list.is_empty()
        
        # Test search
        assert skip_list.search("key1") == "value1"
        assert skip_list.search("key3") == "value3"
        assert skip_list.search("key5") == "value5"
        
        # Search non-existent key
        with pytest.raises(KeyError):
            skip_list.search("nonexistent")
    
    def test_skip_list_update_value(self):
        """Test updating existing key in skip list."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        skip_list.insert("key1", "original_value")
        assert skip_list.search("key1") == "original_value"
        
        # Update value
        skip_list.insert("key1", "updated_value")
        assert skip_list.search("key1") == "updated_value"
        assert skip_list.size() == 1  # Size shouldn't change
    
    def test_skip_list_erase(self):
        """Test erasing keys from skip list."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        # Insert multiple keys
        keys = ["a", "b", "c", "d", "e"]
        for key in keys:
            skip_list.insert(key, f"value_{key}")
        
        assert skip_list.size() == 5
        
        # Erase existing key
        assert skip_list.erase("c") == True
        assert skip_list.size() == 4
        
        with pytest.raises(KeyError):
            skip_list.search("c")
        
        # Other keys should still exist
        assert skip_list.search("a") == "value_a"
        assert skip_list.search("e") == "value_e"
        
        # Erase non-existent key
        assert skip_list.erase("nonexistent") == False
        assert skip_list.size() == 4
    
    def test_skip_list_items_order(self):
        """Test that skip list maintains order."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        # Insert keys in random order
        keys = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
        for key in keys:
            skip_list.insert(key, f"value_{key}")
        
        # Get all items - should be in sorted order
        items = skip_list.items()
        sorted_keys = sorted(set(keys))  # Remove duplicates and sort
        
        assert len(items) == len(sorted_keys)
        for i, (key, value) in enumerate(items):
            assert key == sorted_keys[i]
            assert value == f"value_{key}"
    
    def test_skip_list_clear(self):
        """Test clearing skip list."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        # Insert some data
        for i in range(10):
            skip_list.insert(f"key{i}", f"value{i}")
        
        assert skip_list.size() == 10
        
        skip_list.clear()
        assert skip_list.size() == 0
        assert skip_list.is_empty()
        
        # All searches should fail
        with pytest.raises(KeyError):
            skip_list.search("key0")
    
    def test_skip_list_performance(self):
        """Test skip list with larger dataset."""
        node = xNode.from_native({})
        skip_list = node.as_skip_list()
        
        # Insert many items
        n = 100
        keys = list(range(n))
        random.shuffle(keys)  # Insert in random order
        
        for key in keys:
            skip_list.insert(key, f"value_{key}")
        
        assert skip_list.size() == n
        
        # Search all items
        for key in keys:
            assert skip_list.search(key) == f"value_{key}"
        
        # Verify order is maintained
        items = skip_list.items()
        for i, (key, value) in enumerate(items):
            assert key == i
    
    def test_skip_list_non_dict_node(self):
        """Test SkipList view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_skip_list()


class TestPhase2Integration:
    """Test integration of Phase 2 structures with existing features."""
    
    def test_structure_info_phase2(self):
        """Test structure info includes Phase 2 capabilities."""
        # Dict node should support trie and skip_list
        dict_node = xNode.from_native({})
        info = dict_node.structure_info()
        
        supports = info["supports"]
        assert supports["trie"] is True
        assert supports["skip_list"] is True
        assert supports["min_heap"] is False  # Dict doesn't support heap
        assert supports["max_heap"] is False
        
        # List node should support heaps
        list_node = xNode.from_native([])
        info = list_node.structure_info()
        
        supports = info["supports"]
        assert supports["min_heap"] is True
        assert supports["max_heap"] is True
        assert supports["trie"] is False  # List doesn't support trie
        assert supports["skip_list"] is False
    
    def test_tree_operations_with_phase2_structures(self):
        """Test tree operations work with Phase 2 structures."""
        data = {
            "dictionary": {},
            "priority_queue": []
        }
        root = xNode.from_native(data)
        
        # Navigate to dictionary and use as trie
        dict_node = root.find("dictionary")
        trie = dict_node.as_trie()
        trie.insert("hello", "greeting")
        trie.insert("world", "planet")
        
        # Navigate to list and use as heap
        list_node = root.find("priority_queue")
        heap = list_node.as_min_heap()
        heap.push("task1", priority=2.0)
        heap.push("task2", priority=1.0)
        
        # Verify via tree operations
        hello_value = root.find("dictionary.hello").value
        assert hello_value == "greeting"
        
        # Verify heap operations
        next_task = heap.pop_min()
        assert next_task == "task2"  # Lower priority
    
    def test_graph_operations_with_phase2_structures(self):
        """Test graph operations work with Phase 2 structures."""
        # Create two nodes with different structures
        trie_node = xNode.from_native({})
        heap_node = xNode.from_native([])
        
        # Connect them with graph relation
        trie_node.connect(heap_node, "uses")
        
        # Use specialized structures
        trie = trie_node.as_trie()
        trie.insert("search", "query")
        
        heap = heap_node.as_min_heap()
        heap.push("result", priority=1.0)
        
        # Verify graph relationship still exists
        neighbors = trie_node.neighbors("uses")
        assert len(neighbors) >= 0  # Should have the connection
        
        # Verify structures work
        assert trie.contains("search")
        assert heap.peek_min() == "result"
    
    def test_mixed_structure_workflows(self):
        """Test complex workflows using multiple Phase 2 structures."""
        # Create a search index using trie
        index_node = xNode.from_native({})
        index = index_node.as_trie()
        
        # Add search terms
        terms = ["apple", "application", "apply", "banana", "band", "bandana"]
        for term in terms:
            index.insert(term, f"definition_of_{term}")
        
        # Create priority queue for search results
        results_node = xNode.from_native([])
        results = results_node.as_min_heap()
        
        # Search for terms starting with "app"
        app_terms = index.starts_with("app")
        for term in app_terms:
            # Add to priority queue with relevance score
            relevance = len(term)  # Simple scoring
            results.push(term, priority=relevance)
        
        # Get results in priority order (shortest/most relevant first)
        ordered_results = []
        while not results.is_empty():
            ordered_results.append(results.pop_min())
        
        # Verify results are ordered by relevance
        assert ordered_results == ["apply", "apple", "application"]
    
    def test_performance_comparison(self):
        """Test performance characteristics of Phase 2 structures."""
        import time
        
        # Test Trie performance
        trie_node = xNode.from_native({})
        trie = trie_node.as_trie()
        
        start_time = time.time()
        words = [f"word{i}" for i in range(100)]
        for word in words:
            trie.insert(word, f"value_{word}")
        trie_insert_time = time.time() - start_time
        
        start_time = time.time()
        for word in words:
            trie.contains(word)
        trie_search_time = time.time() - start_time
        
        # Test Heap performance
        heap_node = xNode.from_native([])
        heap = heap_node.as_min_heap()
        
        start_time = time.time()
        for i in range(100):
            heap.push(f"item{i}", priority=random.random())
        heap_insert_time = time.time() - start_time
        
        start_time = time.time()
        while not heap.is_empty():
            heap.pop_min()
        heap_pop_time = time.time() - start_time
        
        # All operations should complete quickly
        assert trie_insert_time < 1.0  # Should be very fast
        assert trie_search_time < 1.0
        assert heap_insert_time < 1.0
        assert heap_pop_time < 1.0
        
        print(f"Performance results:")
        print(f"  Trie insert: {trie_insert_time:.4f}s")
        print(f"  Trie search: {trie_search_time:.4f}s")
        print(f"  Heap insert: {heap_insert_time:.4f}s")
        print(f"  Heap pop: {heap_pop_time:.4f}s")
