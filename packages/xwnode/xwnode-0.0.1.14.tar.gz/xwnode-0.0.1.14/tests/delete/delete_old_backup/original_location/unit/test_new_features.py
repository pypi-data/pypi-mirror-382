#!/usr/bin/env python3
"""
Test new features added to xNode: in-place operations, select, set_many, patch
"""

import sys
import os
import pytest
from typing import Dict, Any

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode


class TestInPlaceOperations:
    """Test in-place operation functionality."""
    
    def test_find_in_place(self):
        """Test find with in_place=True modifies current instance."""
        data = {"user": {"name": "Alice", "profile": {"age": 28}}}
        node = xNode.from_native(data)
        original_id = id(node)
        
        # Test in-place navigation
        result = node.find("user", in_place=True)
        
        # Should return same instance
        assert result is node
        assert id(result) == original_id
        
        # Instance should now point to user data
        assert node.to_native() == {"name": "Alice", "profile": {"age": 28}}
        
        # Further in-place navigation
        node.find("profile", in_place=True)
        assert node.to_native() == {"age": 28}
    
    def test_find_not_in_place(self):
        """Test find with in_place=False creates new instance."""
        data = {"user": {"name": "Alice", "profile": {"age": 28}}}
        node = xNode.from_native(data)
        original_data = node.to_native()
        
        # Test new instance creation
        user_node = node.find("user", in_place=False)
        
        # Should return different instance
        assert user_node is not node
        
        # Original should be unchanged
        assert node.to_native() == original_data
        
        # New instance should have user data
        assert user_node.to_native() == {"name": "Alice", "profile": {"age": 28}}
    
    def test_set_in_place(self):
        """Test set with in_place=True modifies current instance."""
        data = {"user": {"name": "Alice", "age": 28}}
        node = xNode.from_native(data)
        original_id = id(node)
        
        # Test in-place modification
        result = node.set("user.age", 29, in_place=True)
        
        # Should return same instance
        assert result is node
        assert id(result) == original_id
        
        # Data should be modified
        assert node.to_native()["user"]["age"] == 29
    
    def test_set_not_in_place(self):
        """Test set with in_place=False creates new instance."""
        data = {"user": {"name": "Alice", "age": 28}}
        node = xNode.from_native(data)
        original_data = node.to_native()
        
        # Test new instance creation
        new_node = node.set("user.age", 29, in_place=False)
        
        # Should return different instance
        assert new_node is not node
        
        # Original should be unchanged
        assert node.to_native() == original_data
        assert node.to_native()["user"]["age"] == 28
        
        # New instance should have modified data
        assert new_node.to_native()["user"]["age"] == 29
    
    def test_delete_in_place(self):
        """Test delete with in_place=True modifies current instance."""
        data = {"user": {"name": "Alice", "age": 28, "city": "NYC"}}
        node = xNode.from_native(data)
        original_id = id(node)
        
        # Test in-place deletion
        result = node.delete("user.city", in_place=True)
        
        # Should return same instance
        assert result is node
        assert id(result) == original_id
        
        # Data should be modified
        user_data = node.to_native()["user"]
        assert "city" not in user_data
        assert user_data["name"] == "Alice"
        assert user_data["age"] == 28
    
    def test_delete_not_in_place(self):
        """Test delete with in_place=False creates new instance."""
        data = {"user": {"name": "Alice", "age": 28, "city": "NYC"}}
        node = xNode.from_native(data)
        original_data = node.to_native()
        
        # Test new instance creation
        new_node = node.delete("user.city", in_place=False)
        
        # Should return different instance
        assert new_node is not node
        
        # Original should be unchanged
        assert node.to_native() == original_data
        assert "city" in node.to_native()["user"]
        
        # New instance should have deleted data
        user_data = new_node.to_native()["user"]
        assert "city" not in user_data
        assert user_data["name"] == "Alice"


class TestSelectMethod:
    """Test select method functionality."""
    
    def test_select_as_find_alias(self):
        """Test that select works as alias for find."""
        data = {"user": {"profile": {"settings": {"theme": "dark"}}}}
        node = xNode.from_native(data)
        
        # Test both methods return same result
        find_result = node.find("user.profile")
        select_result = node.select("user.profile")
        
        assert find_result.to_native() == select_result.to_native()
    
    def test_select_in_place(self):
        """Test select with in_place parameter."""
        data = {"user": {"profile": {"theme": "dark"}}}
        node = xNode.from_native(data)
        original_id = id(node)
        
        # Test in-place selection
        result = node.select("user.profile", in_place=True)
        
        assert result is node
        assert id(result) == original_id
        assert node.to_native() == {"theme": "dark"}
    
    def test_select_not_in_place(self):
        """Test select without in_place parameter."""
        data = {"user": {"profile": {"theme": "dark"}}}
        node = xNode.from_native(data)
        
        # Test new instance selection
        profile_node = node.select("user.profile", in_place=False)
        
        assert profile_node is not node
        assert profile_node.to_native() == {"theme": "dark"}
        assert node.to_native() == data  # Original unchanged


class TestSetManyMethod:
    """Test set_many method functionality."""
    
    def test_set_many_in_place(self):
        """Test set_many with in_place=True."""
        data = {"user": {"name": "Alice", "age": 28, "city": "NYC"}}
        node = xNode.from_native(data)
        original_id = id(node)
        
        updates = {
            "user.age": 29,
            "user.city": "SF",
            "user.country": "USA"
        }
        
        # Test in-place multiple updates
        result = node.set_many(updates, in_place=True)
        
        # Should return same instance
        assert result is node
        assert id(result) == original_id
        
        # All updates should be applied
        user_data = node.to_native()["user"]
        assert user_data["name"] == "Alice"  # Unchanged
        assert user_data["age"] == 29       # Updated
        assert user_data["city"] == "SF"    # Updated
        assert user_data["country"] == "USA"  # Added
    
    def test_set_many_not_in_place(self):
        """Test set_many with in_place=False."""
        data = {"user": {"name": "Alice", "age": 28, "city": "NYC"}}
        node = xNode.from_native(data)
        original_data = node.to_native()
        
        updates = {
            "user.age": 29,
            "user.city": "SF"
        }
        
        # Test new instance creation
        new_node = node.set_many(updates, in_place=False)
        
        # Should return different instance
        assert new_node is not node
        
        # Original should be unchanged
        assert node.to_native() == original_data
        
        # New instance should have all updates
        user_data = new_node.to_native()["user"]
        assert user_data["age"] == 29
        assert user_data["city"] == "SF"
    
    def test_set_many_empty_updates(self):
        """Test set_many with empty updates dictionary."""
        data = {"user": {"name": "Alice"}}
        node = xNode.from_native(data)
        original_data = node.to_native()
        
        # Test empty updates
        result = node.set_many({}, in_place=True)
        
        # Should return same instance unchanged
        assert result is node
        assert node.to_native() == original_data


class TestPatchMethod:
    """Test patch method functionality."""
    
    def test_patch_add_operation(self):
        """Test patch with add operation."""
        data = {"user": {"name": "Alice"}}
        node = xNode.from_native(data)
        
        operations = [
            {"op": "add", "path": "/user/age", "value": 28},
            {"op": "add", "path": "/user/city", "value": "NYC"}
        ]
        
        result = node.patch(operations)
        
        # Should return new instance
        assert result is not node
        
        # Original unchanged
        assert "age" not in node.to_native()["user"]
        
        # New instance has additions
        user_data = result.to_native()["user"]
        assert user_data["name"] == "Alice"
        assert user_data["age"] == 28
        assert user_data["city"] == "NYC"
    
    def test_patch_replace_operation(self):
        """Test patch with replace operation."""
        data = {"user": {"name": "Alice", "age": 28}}
        node = xNode.from_native(data)
        
        operations = [
            {"op": "replace", "path": "/user/age", "value": 29},
            {"op": "replace", "path": "/user/name", "value": "Bob"}
        ]
        
        result = node.patch(operations)
        
        # New instance has replacements
        user_data = result.to_native()["user"]
        assert user_data["name"] == "Bob"
        assert user_data["age"] == 29
    
    def test_patch_remove_operation(self):
        """Test patch with remove operation."""
        data = {"user": {"name": "Alice", "age": 28, "city": "NYC"}}
        node = xNode.from_native(data)
        
        operations = [
            {"op": "remove", "path": "/user/city"},
            {"op": "remove", "path": "/user/age"}
        ]
        
        result = node.patch(operations)
        
        # New instance has removals
        user_data = result.to_native()["user"]
        assert user_data["name"] == "Alice"
        assert "age" not in user_data
        assert "city" not in user_data
    
    def test_patch_mixed_operations(self):
        """Test patch with mixed operations."""
        data = {"user": {"name": "Alice", "age": 28, "city": "NYC"}}
        node = xNode.from_native(data)
        
        operations = [
            {"op": "replace", "path": "/user/age", "value": 29},
            {"op": "remove", "path": "/user/city"},
            {"op": "add", "path": "/user/country", "value": "USA"}
        ]
        
        result = node.patch(operations)
        
        user_data = result.to_native()["user"]
        assert user_data["name"] == "Alice"    # Unchanged
        assert user_data["age"] == 29          # Replaced
        assert "city" not in user_data         # Removed
        assert user_data["country"] == "USA"   # Added
    
    def test_patch_dot_notation_paths(self):
        """Test patch with dot notation paths."""
        data = {"user": {"profile": {"age": 28}}}
        node = xNode.from_native(data)
        
        operations = [
            {"op": "replace", "path": "user.profile.age", "value": 29}
        ]
        
        result = node.patch(operations)
        
        assert result.to_native()["user"]["profile"]["age"] == 29
    
    def test_patch_list_operations(self):
        """Test patch operations on lists."""
        data = {"items": ["a", "b", "c"]}
        node = xNode.from_native(data)
        
        operations = [
            {"op": "replace", "path": "/items/1", "value": "B"},
            {"op": "add", "path": "/items/3", "value": "d"},
            {"op": "remove", "path": "/items/0"}
        ]
        
        result = node.patch(operations)
        
        items = result.to_native()["items"]
        # Operations: replace index 1 with "B", add "d" at index 3, remove index 0
        # Original: ["a", "b", "c"] -> replace 1: ["a", "B", "c"] -> add at 3: ["a", "B", "c", "d"] -> remove 0: ["B", "c", "d"]
        assert len(items) == 3  # Started with 3, added 1, removed 1 = 3
        assert items[0] == "B"   # Originally at index 1, now at index 0 after removal
        assert items[1] == "c"   # Originally at index 2, now at index 1 after removal  
        assert items[2] == "d"   # Added at index 3, now at index 2 after removal


class TestUniversalTreeOperations:
    """Test that tree operations work with any data structure."""
    
    def test_nested_dictionaries(self):
        """Test operations on deeply nested dictionaries."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        
        node = xNode.from_native(data)
        
        # Test navigation
        deep_node = node.find("level1.level2.level3")
        assert deep_node.to_native() == {"value": "deep"}
        
        # Test modification
        modified = node.set("level1.level2.level3.value", "modified")
        assert modified.to_native()["level1"]["level2"]["level3"]["value"] == "modified"
    
    def test_mixed_structures(self):
        """Test operations on mixed dict/list structures."""
        data = {
            "users": [
                {"name": "Alice", "tags": ["admin", "user"]},
                {"name": "Bob", "tags": ["user"]}
            ]
        }
        
        node = xNode.from_native(data)
        
        # Test navigation through mixed structures
        first_user = node.find("users.0")
        assert first_user.to_native()["name"] == "Alice"
        
        # Test modification in mixed structures
        modified = node.set("users.0.tags.0", "superadmin")
        assert modified.to_native()["users"][0]["tags"][0] == "superadmin"
    
    def test_primitive_types(self):
        """Test that operations work with various primitive types."""
        data = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "empty_dict": {},
            "empty_list": []
        }
        
        node = xNode.from_native(data)
        
        # Test accessing all types
        assert node.find("string").to_native() == "text"
        assert node.find("number").to_native() == 42
        assert node.find("float").to_native() == 3.14
        assert node.find("boolean").to_native() is True
        assert node.find("null").to_native() is None
        assert node.find("list").to_native() == [1, 2, 3]
        assert node.find("empty_dict").to_native() == {}
        assert node.find("empty_list").to_native() == []


class TestErrorHandling:
    """Test error handling for new features."""
    
    def test_invalid_path_in_place(self):
        """Test error handling for invalid paths with in_place operations."""
        data = {"user": {"name": "Alice"}}
        node = xNode.from_native(data)
        
        # Test invalid path should raise error
        with pytest.raises(Exception):  # Could be xNodePathError or similar
            node.find("nonexistent.path", in_place=True)
    
    def test_invalid_patch_operation(self):
        """Test error handling for invalid patch operations."""
        data = {"user": {"name": "Alice"}}
        node = xNode.from_native(data)
        
        # Test invalid operation type
        operations = [{"op": "invalid", "path": "/user/name", "value": "Bob"}]
        
        with pytest.raises(ValueError):
            node.patch(operations)
    
    def test_set_many_invalid_path(self):
        """Test set_many with some invalid paths raises appropriate errors."""
        data = {"user": {"name": "Alice"}}
        node = xNode.from_native(data)
        
        updates = {
            "user.name": "Bob",  # Valid
            "invalid.path.deep": "value"  # Invalid - nonexistent path
        }
        
        # Should raise error for invalid path
        with pytest.raises(Exception):  # Could be xNodeValueError or xNodePathError
            node.set_many(updates, in_place=False)
        
        # Test valid updates work correctly
        valid_updates = {
            "user.name": "Bob"
        }
        result = node.set_many(valid_updates, in_place=False)
        assert result.to_native()["user"]["name"] == "Bob"


if __name__ == "__main__":
    import sys
    
    # Run all tests
    exit_code = pytest.main([__file__, "-v"])
    sys.exit(exit_code)
