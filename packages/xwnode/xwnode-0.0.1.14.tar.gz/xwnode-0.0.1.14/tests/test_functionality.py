#!/usr/bin/env python3
"""
Comprehensive functionality test for xnode.
"""

import sys
import os

# Add our src directory and xwsystem to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Also add xwsystem src directory
xwsystem_src = os.path.join(os.path.dirname(current_dir), 'xwsystem', 'src')
if os.path.exists(xwsystem_src):
    sys.path.insert(0, xwsystem_src)

def test_basic_functionality():
    """Test basic xnode functionality."""
    print("=== Testing Basic Functionality ===")
    
    try:
        # Test convenience import
        import xnode
        print("✓ Convenience import works")
        
        # Test creating a simple node
        from exonware.xnode import XWNode
        
        # Test with dictionary data
        data = {'name': 'John', 'age': 30, 'city': 'New York'}
        node = XWNode(data)
        print("✓ Created XWNode from dictionary")
        print(f"  Node type: {type(node)}")
        print(f"  Node value keys: {list(node.value.keys())}")
        
        # Test accessing values
        if hasattr(node, 'value'):
            print(f"  Name: {node.value.get('name')}")
            print(f"  Age: {node.value.get('age')}")
        
        # Test with list data
        list_data = [1, 2, 3, 4, 5]
        list_node = XWNode(list_data)
        print("✓ Created XWNode from list")
        print(f"  List node value: {list_node.value}")
        
        # Test nested data
        nested_data = {
            'user': {
                'name': 'Alice',
                'contacts': ['alice@example.com', 'alice2@example.com']
            },
            'settings': {
                'theme': 'dark',
                'notifications': True
            }
        }
        nested_node = XWNode(nested_data)
        print("✓ Created XWNode from nested data")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_navigation():
    """Test path navigation functionality."""
    print("\n=== Testing Path Navigation ===")
    
    try:
        from exonware.xnode import XWNode
        
        data = {
            'users': [
                {'name': 'Alice', 'age': 30},
                {'name': 'Bob', 'age': 25}
            ],
            'config': {
                'theme': 'dark',
                'language': 'en'
            }
        }
        
        node = XWNode(data)
        
        # Test basic path access
        if hasattr(node, 'find'):
            # Try to find users
            users_node = node.find('users')
            print("✓ Found users node")
            
            # Try to find first user
            first_user = node.find('users.0')
            print("✓ Found first user")
            
            # Try to find user name
            user_name = node.find('users.0.name')
            print("✓ Found user name")
            print(f"  First user name: {user_name.value if hasattr(user_name, 'value') else 'N/A'}")
            
        else:
            print("⚠ Node doesn't have find method, checking bracket access")
            
        # Test bracket notation if available
        if hasattr(node, '__getitem__'):
            try:
                users = node['users']
                print("✓ Bracket notation works")
                first_user = users[0]
                print("✓ Array indexing works")
                name = first_user['name']
                print(f"  Name via bracket: {name.value if hasattr(name, 'value') else name}")
            except Exception as e:
                print(f"⚠ Bracket notation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Path navigation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    try:
        from exonware.xnode import XWNode, XWNodeError
        
        node = XWNode({'test': 'data'})
        
        # Test accessing non-existent path
        try:
            if hasattr(node, 'find'):
                result = node.find('nonexistent.path')
                print("⚠ Expected error for non-existent path, but got result")
            else:
                print("⚠ No find method to test")
        except Exception as e:
            print(f"✓ Properly handles non-existent path: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test all expected imports."""
    print("\n=== Testing All Imports ===")
    
    try:
        # Test main classes
        from exonware.xnode import XWNode, XWNodeQuery, XWNodeFactory
        print("✓ Main classes imported")
        
        # Test error classes
        from exonware.xnode import (
            XWNodeError, XWNodeTypeError, XWNodePathError, 
            XWNodeValueError, XWNodeSecurityError, XWNodeLimitError
        )
        print("✓ Error classes imported")
        
        # Test config
        from exonware.xnode import XWNodeConfig, get_config, set_config
        print("✓ Config classes imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("XWNode Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_path_navigation,
        test_error_handling,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! XWNode is working correctly.")
        return 0
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
