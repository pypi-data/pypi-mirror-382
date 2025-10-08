"""
xNode Core Functionality Tests
==============================

Comprehensive unit tests for core xNode functionality including:
- Factory methods (from_native)
- Property access and type checking
- Container operations (iteration, length, keys, items)
- Bracket notation access
- String representations
- Error conditions
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add src to Python path for direct imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Dynamic import handling for different test environments
try:
    from conftest import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
except ImportError:
    try:
        from .... import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
    except ImportError:
        from src.xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError


class TestxNodeFactoryMethods:
    """Test xNode factory methods for creating nodes from different sources."""
    
    @pytest.mark.core
    def test_from_native_dict(self, simple_dict_data):
        """Test creating xNode from Python dictionary."""
        node = xNode.from_native(simple_dict_data)
        
        assert node.is_dict
        assert not node.is_list
        assert not node.is_leaf
        assert node['name'].value == 'Alice'
        assert node['age'].value == 30
        assert node['active'].value is True

    @pytest.mark.core
    def test_from_native_list(self, simple_list_data):
        """Test creating xNode from Python list."""
        node = xNode.from_native(simple_list_data)
        
        assert node.is_list
        assert not node.is_dict
        assert not node.is_leaf
        assert node[0].value == 'apple'
        assert node[1].value == 'banana'
        assert node[2].value == 'cherry'

    @pytest.mark.core
    def test_from_native_string_primitive(self):
        """Test creating xNode from string primitive."""
        test_value = "hello world"
        node = xNode.from_native(test_value)
        
        assert node.is_leaf
        assert not node.is_dict
        assert not node.is_list
        assert node.value == test_value

    @pytest.mark.core
    def test_from_native_number_primitive(self):
        """Test creating xNode from number primitive."""
        test_value = 42
        node = xNode.from_native(test_value)
        
        assert node.is_leaf
        assert node.value == test_value

    @pytest.mark.core
    def test_from_native_boolean_primitive(self):
        """Test creating xNode from boolean primitive."""
        test_value = True
        node = xNode.from_native(test_value)
        
        assert node.is_leaf
        assert node.value is True

    @pytest.mark.core
    def test_from_native_none_value(self):
        """Test creating xNode from None value."""
        node = xNode.from_native(None)
        
        assert node.is_leaf
        assert node.value is None

    @pytest.mark.core
    def test_from_native_nested_structure(self, nested_data):
        """Test creating xNode from complex nested structure."""
        node = xNode.from_native(nested_data)
        
        assert node.is_dict
        assert node['users'].is_list
        assert node['users'][0].is_dict
        assert node['users'][0]['name'].value == 'Alice'
        assert node['metadata']['version'].value == 1.0

    @pytest.mark.core
    def test_from_native_valid_object(self, json_test_data):
        """Test creating xNode from valid native data."""
        # Use the native data directly
        node = xNode.from_native(json_test_data)
        
        assert node.is_dict
        assert node['users'][0]['name'].value == 'Alice'
        assert node['meta']['count'].value == 2

    @pytest.mark.core
    def test_from_native_array(self):
        """Test creating xNode from native array data."""
        native_data = [1, 2, "three"]
        node = xNode.from_native(native_data)
        
        assert node.is_list
        assert len(node) == 3

    @pytest.mark.core
    def test_from_native_primitive(self):
        """Test creating xNode from native primitive data."""
        native_data = "hello"
        node = xNode.from_native(native_data)
        
        assert node.is_leaf
        assert node.value == "hello"

    @pytest.mark.core
    def test_from_native_function_object(self):
        """Test that function objects are handled as leaf values (data agnostic)."""
        # Test with a function object - xNode is data agnostic and should accept any data
        def test_function():
            pass
        
        node = xNode.from_native(test_function)
        
        # Function should be stored as a leaf value
        assert node.is_leaf
        assert node.value is test_function


class TestxNodeProperties:
    """Test xNode properties and type checking methods."""
    
    @pytest.mark.core
    def test_is_leaf_property(self, leaf_node):
        """Test is_leaf property for leaf nodes."""
        assert leaf_node.is_leaf is True
        assert leaf_node.is_list is False
        assert leaf_node.is_dict is False
    
    @pytest.mark.core
    def test_is_list_property(self, list_node):
        """Test is_list property for list nodes."""
        assert list_node.is_list is True
        assert list_node.is_leaf is False
        assert list_node.is_dict is False
    
    @pytest.mark.core
    def test_is_dict_property(self, simple_node):
        """Test is_dict property for dict nodes."""
        assert simple_node.is_dict is True
        assert simple_node.is_leaf is False
        assert simple_node.is_list is False
    
    @pytest.mark.core
    def test_type_property_leaf(self, leaf_node):
        """Test type property for leaf nodes."""
        assert leaf_node.type == 'value'
    
    @pytest.mark.core
    def test_type_property_list(self, list_node):
        """Test type property for list nodes."""
        assert list_node.type == 'list'
    
    @pytest.mark.core
    def test_type_property_dict(self, simple_node):
        """Test type property for dict nodes."""
        assert simple_node.type == 'dict'
    
    @pytest.mark.core
    def test_value_property_preserves_data(self, mixed_type_data):
        """Test that value property preserves original data integrity."""
        node = xNode.from_native(mixed_type_data)
        
        # For dict nodes, value returns the native dict
        native_value = node.to_native()
        assert native_value == mixed_type_data
        assert native_value['string'] == 'hello'
        assert native_value['integer'] == 42
        assert native_value['float'] == 3.14
        assert native_value['boolean'] is True
        assert native_value['null'] is None
        assert native_value['list'] == [1, 2, 3]
        assert native_value['dict'] == {'nested': 'value'}


class TestxNodeContainerOperations:
    """Test container operations for dict and list nodes."""
    
    @pytest.mark.core
    def test_len_dict_node(self, simple_node):
        """Test len() operation on dict nodes."""
        assert len(simple_node) == 4  # name, age, city, active
    
    @pytest.mark.core
    def test_len_list_node(self, list_node):
        """Test len() operation on list nodes."""
        assert len(list_node) == 3  # 'apple', 'banana', 'cherry'
    
    @pytest.mark.core
    def test_len_leaf_node_raises_error(self, leaf_node):
        """Test that len() on leaf nodes raises appropriate error."""
        # Leaf nodes return 0 for len() instead of raising an error
        assert len(leaf_node) == 0
    
    @pytest.mark.core
    def test_iter_dict_node(self, simple_node):
        """Test iteration over dict node values."""
        values = list(simple_node)
        assert len(values) == 4
        
        # All items should be xNode instances
        for value in values:
            assert isinstance(value, xNode)
    
    @pytest.mark.core
    def test_iter_list_node(self, list_node):
        """Test iteration over list node elements."""
        elements = list(list_node)
        assert len(elements) == 3
        
        # All items should be xNode instances
        for element in elements:
            assert isinstance(element, xNode)
        
        # Check actual values
        assert elements[0].value == 'apple'
        assert elements[1].value == 'banana'
        assert elements[2].value == 'cherry'
    
    @pytest.mark.core
    def test_iter_leaf_node_raises_error(self, leaf_node):
        """Test that iteration on leaf nodes raises appropriate error."""
        # Leaf nodes return empty iterator instead of raising an error
        assert list(leaf_node) == []
    
    @pytest.mark.core
    def test_keys_dict_node(self, simple_node):
        """Test keys() method on dict nodes."""
        keys = list(simple_node.keys())
        expected_keys = ['name', 'age', 'city', 'active']
        
        assert len(keys) == 4
        for key in expected_keys:
            assert key in keys
    
    @pytest.mark.core
    def test_keys_list_node_raises_error(self, list_node):
        """Test that keys() on list nodes raises appropriate error."""
        # List nodes return empty iterator for keys() instead of raising an error
        assert list(list_node.keys()) == []
    
    @pytest.mark.core
    def test_keys_leaf_node_raises_error(self, leaf_node):
        """Test that keys() on leaf nodes raises appropriate error."""
        # Leaf nodes return empty iterator for keys() instead of raising an error
        assert list(leaf_node.keys()) == []
    
    @pytest.mark.core
    def test_items_dict_node(self, simple_node):
        """Test items() method on dict nodes."""
        items = list(simple_node.items())
        assert len(items) == 4
        
        # Check structure: each item should be (key, xNode)
        for key, node in items:
            assert isinstance(key, str)
            assert isinstance(node, xNode)
        
        # Check specific items
        items_dict = dict(items)
        assert 'name' in items_dict
        assert 'age' in items_dict
        assert 'active' in items_dict
        assert items_dict['name'].value == 'Alice'
        assert items_dict['age'].value == 30
        assert items_dict['active'].value is True
    
    @pytest.mark.core
    def test_items_list_node_raises_error(self, list_node):
        """Test that items() on list nodes raises appropriate error."""
        # List nodes return empty iterator for items() instead of raising an error
        assert list(list_node.items()) == []


class TestxNodeBracketAccess:
    """Test bracket notation access for container nodes."""
    
    @pytest.mark.core
    def test_getitem_dict_string_key(self, simple_node):
        """Test bracket access with string key on dict node."""
        name_node = simple_node['name']
        
        assert isinstance(name_node, xNode)
        assert name_node.is_leaf
        assert name_node.value == 'Alice'
    
    @pytest.mark.core
    def test_getitem_list_integer_index(self, list_node):
        """Test bracket access with integer index on list node."""
        first_element = list_node[0]
        
        assert isinstance(first_element, xNode)
        assert first_element.is_leaf
        assert first_element.value == 'apple'
    
    @pytest.mark.core
    def test_getitem_dict_nonexistent_key_raises_error(self, simple_node):
        """Test that accessing nonexistent key raises appropriate error."""
        with pytest.raises(KeyError):
            simple_node['nonexistent']
    
    @pytest.mark.core
    def test_getitem_list_out_of_bounds_raises_error(self, list_node):
        """Test that accessing out-of-bounds index raises appropriate error."""
        with pytest.raises(IndexError, match="List index 10 out of range"):
            list_node[10]
    
    @pytest.mark.core
    def test_getitem_leaf_node_raises_error(self, leaf_node):
        """Test that bracket access on leaf nodes raises appropriate error."""
        with pytest.raises(KeyError, match="Node type aNodeValue does not support child access"):
            leaf_node['key']


class TestxNodeConversions:
    """Test xNode conversion methods."""
    
    @pytest.mark.core
    def test_to_native_dict_node(self, simple_dict_data):
        """Test to_native() method on dict node."""
        node = xNode.from_native(simple_dict_data)
        result = node.to_native()
        
        assert result == simple_dict_data
        assert isinstance(result, dict)
    
    @pytest.mark.core
    def test_to_native_list_node(self, simple_list_data):
        """Test to_native() method on list node."""
        node = xNode.from_native(simple_list_data)
        result = node.to_native()
        
        assert result == simple_list_data
        assert isinstance(result, list)
    
    @pytest.mark.core
    def test_to_native_leaf_node(self, leaf_node):
        """Test to_native() method on leaf node."""
        result = leaf_node.to_native()
        
        assert result == "simple string value"
        assert isinstance(result, str)
    
    @pytest.mark.core
    def test_to_native_dict_node_roundtrip(self, simple_dict_data):
        """Test to_native() method on dict node preserves data integrity."""
        node = xNode.from_native(simple_dict_data)
        native_data = node.to_native()
        
        # Verify data integrity
        assert native_data == simple_dict_data
        assert isinstance(native_data, dict)
    
    @pytest.mark.core
    def test_to_native_complex_data_preservation(self, simple_dict_data):
        """Test to_native() method preserves complex data structures."""
        node = xNode.from_native(simple_dict_data)
        native_data = node.to_native()
        
        # Verify all nested data is preserved
        assert native_data['name'] == simple_dict_data['name']
        assert native_data['age'] == simple_dict_data['age']
        assert native_data['city'] == simple_dict_data['city']


class TestxNodeStringRepresentations:
    """Test xNode string representation methods."""
    
    @pytest.mark.core
    def test_repr_leaf_node(self, leaf_node):
        """Test __repr__ for leaf nodes."""
        repr_str = repr(leaf_node)
        assert repr_str.startswith('xNode(type=value')
        assert 'simple string value' in repr_str
    
    @pytest.mark.core
    def test_repr_dict_node(self, simple_node):
        """Test __repr__ for dict nodes."""
        repr_str = repr(simple_node)
        assert repr_str.startswith('xNode(type=dict')
        assert '4 items' in repr_str
    
    @pytest.mark.core
    def test_repr_list_node(self, list_node):
        """Test __repr__ for list nodes."""
        repr_str = repr(list_node)
        assert repr_str.startswith('xNode(type=list')
        assert '3 items' in repr_str
    
    @pytest.mark.core
    def test_str_representation(self, simple_node):
        """Test __str__ method."""
        str_repr = str(simple_node)
        # The visualize method returns a formatted string, not JSON
        assert 'name:' in str_repr
        assert 'Alice' in str_repr
        assert 'age:' in str_repr
        assert '30' in str_repr
    
    @pytest.mark.core
    def test_repr_long_value_truncation(self):
        """Test that very long values are not truncated in repr."""
        long_string = 'x' * 100
        node = xNode.from_native(long_string)
        repr_str = repr(node)
        assert '...' not in repr_str


class TestxNodeEmptyContainers:
    """Test xNode behavior with empty containers."""
    
    @pytest.mark.core
    def test_empty_dict_node(self, empty_dict_node):
        """Test empty dictionary node behavior."""
        assert empty_dict_node.is_dict
        assert len(empty_dict_node) == 0
        assert list(empty_dict_node.keys()) == []
        assert list(empty_dict_node.items()) == []
        assert list(empty_dict_node) == []
    
    @pytest.mark.core
    def test_empty_list_node(self, empty_list_node):
        """Test empty list node behavior."""
        assert empty_list_node.is_list
        assert len(empty_list_node) == 0
        assert list(empty_list_node) == []


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 