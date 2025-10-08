"""
xNode Navigation Tests
======================

Comprehensive tests for XNode navigation functionality including:
- Path resolution with dot notation
- Bracket notation access
- Mixed path formats
- Deep navigation in complex structures
- get() method with defaults
- Edge cases and error conditions

Following pytest best practices and established test patterns.
"""

import pytest
from pathlib import Path
import sys

# Setup path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Import from conftest.py which sets up the proper imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from conftest import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
except ImportError:
    try:
        from src.xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError
    except ImportError:
        from xlib.xnode import xNode, xNodeError, xNodeTypeError, xNodePathError, xNodeValueError


class TestDotNotationNavigation:
    """Test navigation using dot notation paths."""
    
    @pytest.mark.navigation
    def test_simple_dot_navigation(self, nested_node):
        """Test basic dot notation navigation."""
        # Navigate to nested values
        version_node = nested_node.find('metadata.version')
        assert version_node.value == 1.0
        
        created_node = nested_node.find('metadata.created')
        assert created_node.value == '2024-01-01'
    
    @pytest.mark.navigation
    def test_array_index_dot_navigation(self, nested_node):
        """Test dot notation with array indices."""
        # Navigate to first user's name
        first_user_name = nested_node.find('users.0.name')
        assert first_user_name.value == 'Alice'
        
        # Navigate to second user's age
        second_user_age = nested_node.find('users.1.age')
        assert second_user_age.value == 25
    
    @pytest.mark.navigation
    def test_deep_nested_dot_navigation(self, nested_node):
        """Test deep nested navigation with dot notation."""
        # Navigate to deeply nested preference
        alice_theme = nested_node.find('users.0.profile.preferences.theme')
        assert alice_theme.value == 'dark'
        
        bob_notifications = nested_node.find('users.1.profile.preferences.notifications')
        assert bob_notifications.value is False
    
    @pytest.mark.navigation
    def test_array_within_array_navigation(self, nested_node):
        """Test navigation to arrays within arrays."""
        # Navigate to first user's first role
        first_role = nested_node.find('users.0.roles.0')
        assert first_role.value == 'admin'
        
        # Navigate to second user's only role
        second_role = nested_node.find('users.1.roles.0')
        assert second_role.value == 'user'
    
    @pytest.mark.navigation
    def test_metadata_array_navigation(self, nested_node):
        """Test navigation to metadata array elements."""
        # Navigate to tags array elements
        first_tag = nested_node.find('metadata.tags.0')
        assert first_tag.value == 'test'
        
        second_tag = nested_node.find('metadata.tags.1')
        assert second_tag.value == 'sample'
        
        third_tag = nested_node.find('metadata.tags.2')
        assert third_tag.value == 'data'


class TestBracketNotationNavigation:
    """Test navigation using bracket notation."""
    
    @pytest.mark.navigation
    def test_simple_bracket_navigation(self, nested_node):
        """Test basic bracket notation navigation."""
        # Navigate using brackets
        users_node = nested_node['users']
        assert users_node.is_list
        assert len(users_node) == 2
        
        metadata_node = nested_node['metadata']
        assert metadata_node.is_dict
    
    @pytest.mark.navigation
    def test_chained_bracket_navigation(self, nested_node):
        """Test chained bracket notation."""
        # Chain bracket access
        first_user = nested_node['users'][0]
        assert first_user['name'].value == 'Alice'
        assert first_user['age'].value == 30
        
        # Deep chaining
        alice_email = nested_node['users'][0]['profile']['email']
        assert alice_email.value == 'alice@example.com'
    
    @pytest.mark.navigation
    def test_mixed_bracket_types(self, nested_node):
        """Test mixing string and integer bracket access."""
        # Mix string keys and integer indices
        theme = nested_node['users'][0]['profile']['preferences']['theme']
        assert theme.value == 'dark'
        
        # Array access within dict access
        first_role = nested_node['users'][1]['roles'][0]
        assert first_role.value == 'user'


class TestMixedPathFormats:
    """Test navigation using mixed path formats."""
    
    @pytest.mark.navigation
    def test_mixed_dot_and_bracket(self, complex_navigation_data):
        """Test mixing dot notation and bracket access."""
        node = xNode.from_native(complex_navigation_data)
        
        # Mix dot and bracket notation
        backend_lead = node.find('company.departments.0.teams.0.members.0.name')
        assert backend_lead.value == 'Alice'
        
        # Alternative access pattern
        sales_manager = node.find('company.departments.1.teams.0.members.0.role')
        assert sales_manager.value == 'manager'
    
    @pytest.mark.navigation
    def test_complex_nested_access(self, complex_navigation_data):
        """Test complex nested structure access."""
        node = xNode.from_native(complex_navigation_data)
        
        # Navigate to configuration values
        api_limit = node.find('config.features.api_limits.requests_per_minute')
        assert api_limit.value == 1000
        
        payload_size = node.find('config.features.api_limits.max_payload_size')
        assert payload_size.value == '10MB'
    
    @pytest.mark.navigation
    def test_array_heavy_navigation(self, array_heavy_data):
        """Test navigation in array-heavy structures."""
        node = xNode.from_native(array_heavy_data)
        
        # Navigate matrix elements
        matrix_center = node.find('matrix.1.1')
        assert matrix_center.value == 5
        
        # Navigate record values
        second_record_second_value = node.find('records.1.values.1')
        assert second_record_second_value.value == 50


class TestGetMethodWithDefaults:
    """Test the get() method with default values."""
    
    @pytest.mark.navigation
    def test_get_existing_path(self, nested_node):
        """Test get() method with existing path."""
        result = nested_node.get('users.0.name')
        assert result is not None
        assert result.value == 'Alice'
    
    @pytest.mark.navigation
    def test_get_nonexistent_path_with_default(self, nested_node):
        """Test get() method with nonexistent path and default."""
        result = nested_node.get('users.0.nonexistent', 'default_value')
        assert result is not None
        assert result.value == 'default_value'
    
    @pytest.mark.navigation
    def test_get_nonexistent_path_without_default(self, nested_node):
        """Test get() method with nonexistent path and no default."""
        result = nested_node.get('users.0.nonexistent')
        assert result is None
    
    @pytest.mark.navigation
    def test_get_with_complex_default(self, nested_node):
        """Test get() method with complex default value."""
        default_dict = {'default': True, 'nested': {'value': 42}}
        result = nested_node.get('nonexistent.path', default_dict)
        
        assert result is not None
        assert result.is_dict
        assert result.value == default_dict
    
    @pytest.mark.navigation
    def test_get_with_none_default(self, nested_node):
        """Test get() method with explicit None default."""
        result = nested_node.get('nonexistent.path', None)
        # When default is None, get() returns None directly (not wrapped in xNode)
        assert result is None


class TestEmptyPathNavigation:
    """Test navigation with empty or special paths."""
    
    @pytest.mark.navigation
    def test_empty_path_returns_self(self, nested_node):
        """Test that empty path returns the node itself."""
        result = nested_node.find('')
        assert result is nested_node
        assert result.value == nested_node.value
    
    @pytest.mark.navigation
    def test_whitespace_path_handling(self, nested_node):
        """Test handling of whitespace in paths."""
        # Whitespace-only paths are treated as empty paths, returning current node
        result1 = nested_node.find(' ')
        assert result1 is not None
        assert result1.value == nested_node.value  # Should return same data
        
        result2 = nested_node.find('  ')
        assert result2 is not None
        assert result2.value == nested_node.value  # Should return same data


class TestEdgeCaseNavigation:
    """Test navigation with edge case scenarios."""
    
    @pytest.mark.navigation
    def test_numeric_string_keys(self, edge_case_keys_data):
        """Test navigation with numeric string keys."""
        node = xNode.from_native(edge_case_keys_data)
        
        # Access string keys that look like numbers
        zero_key = node['0']
        assert zero_key.value == 'string_zero'
        
        decimal_key = node['1.5']
        assert decimal_key.value == 'decimal_string'
    
    @pytest.mark.navigation
    def test_special_character_keys(self, edge_case_keys_data):
        """Test navigation with special character keys."""
        node = xNode.from_native(edge_case_keys_data)
        
        # Access keys with special characters
        spaced_key = node['spaces in key']
        assert spaced_key.value == 'spaced_key'
        
        special_key = node['special!@#$%']
        assert special_key.value == 'special_chars'
    
    @pytest.mark.navigation
    def test_unicode_keys(self, edge_case_keys_data):
        """Test navigation with Unicode keys."""
        node = xNode.from_native(edge_case_keys_data)
        
        unicode_key = node['unicode_ключ']
        assert unicode_key.value == 'unicode_value'
    
    @pytest.mark.navigation
    def test_empty_string_key(self, edge_case_keys_data):
        """Test navigation with empty string key."""
        node = xNode.from_native(edge_case_keys_data)
        
        empty_key = node['']
        assert empty_key.value == 'empty_key'


class TestNavigationErrorHandling:
    """Test error handling in navigation scenarios."""
    
    @pytest.mark.navigation
    def test_invalid_path_on_dict(self, nested_node):
        """Test invalid path navigation on dict nodes."""
        with pytest.raises(xNodePathError, match="Cannot resolve path"):
            nested_node.find('nonexistent.path.here')
    
    @pytest.mark.navigation
    def test_invalid_array_index(self, nested_node):
        """Test invalid array index in path."""
        with pytest.raises(xNodePathError, match="Cannot resolve path"):
            nested_node.find('users.10.name')  # Index out of bounds
    
    @pytest.mark.navigation
    def test_navigation_on_leaf_node(self, leaf_node):
        """Test that navigation on leaf nodes raises appropriate error."""
        with pytest.raises(xNodePathError, match="Cannot resolve path"):
            leaf_node.find('some.path')
    
    @pytest.mark.navigation
    def test_array_access_on_dict_with_string_index(self, nested_node):
        """Test array-style access on dict with non-numeric string."""
        with pytest.raises(xNodePathError, match="Cannot resolve path"):
            nested_node.find('metadata.nonexistent_numeric_key')
    
    @pytest.mark.navigation
    def test_dict_access_on_array_with_invalid_key(self, nested_node):
        """Test dict-style access on array with invalid key."""
        with pytest.raises(xNodePathError, match="Cannot resolve path"):
            nested_node.find('users.invalid_key.name')


class TestNavigationPerformance:
    """Test navigation performance characteristics."""
    
    @pytest.mark.navigation
    @pytest.mark.performance
    def test_deep_navigation_performance(self):
        """Test navigation performance with deeply nested structures."""
        # Create a deeply nested structure
        deep_data = {'root': {}}
        current = deep_data['root']
        
        # Create 50 levels of nesting
        for i in range(50):
            current[f'level_{i}'] = {}
            current = current[f'level_{i}']
        current['final_value'] = 'deep_value'
        
        # Test navigation
        node = xNode.from_native(deep_data)
        path_parts = ['root'] + [f'level_{i}' for i in range(50)] + ['final_value']
        deep_path = '.'.join(path_parts)
        
        result = node.find(deep_path)
        assert result.value == 'deep_value'
    
    @pytest.mark.navigation
    @pytest.mark.performance
    def test_wide_navigation_performance(self):
        """Test navigation performance with wide structures."""
        # Create a wide structure (many siblings)
        wide_data = {}
        for i in range(1000):
            wide_data[f'key_{i}'] = f'value_{i}'
        
        node = xNode.from_native(wide_data)
        
        # Test access to various keys
        result_1 = node.find('key_0')
        assert result_1.value == 'value_0'
        
        result_500 = node.find('key_500')
        assert result_500.value == 'value_500'
        
        result_999 = node.find('key_999')
        assert result_999.value == 'value_999'


class TestNavigationImmutability:
    """Test that navigation maintains immutability."""
    
    @pytest.mark.navigation
    def test_navigation_returns_new_instances(self, nested_node):
        """Test that navigation always returns new xNode instances."""
        users_node_1 = nested_node.find('users')
        users_node_2 = nested_node.find('users')
        
        # Should be different instances but same data
        assert users_node_1 is not users_node_2
        assert users_node_1.value == users_node_2.value
    
    @pytest.mark.navigation
    def test_bracket_access_returns_new_instances(self, nested_node):
        """Test that bracket access returns new xNode instances."""
        user_1 = nested_node['users'][0]
        user_2 = nested_node['users'][0]
        
        # Should be different instances but same data
        assert user_1 is not user_2
        assert user_1.value == user_2.value
    
    @pytest.mark.navigation
    def test_original_node_unchanged_after_navigation(self, nested_node):
        """Test that original node is unchanged after navigation."""
        original_value = nested_node.value
        
        # Perform various navigation operations
        nested_node.find('users.0.name')
        nested_node['metadata']['version']
        nested_node.get('users.1.age')
        
        # Original should be unchanged
        assert nested_node.value == original_value


if __name__ == '__main__':
    """Allow running tests directly."""
    pytest.main([__file__, '-v']) 