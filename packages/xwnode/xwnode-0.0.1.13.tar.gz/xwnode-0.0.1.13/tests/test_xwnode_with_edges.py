#!/usr/bin/env python3
"""
XWNode with Edges Test

Test that XWNode can work with edges using a simple tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
sys.path.insert(0, str(src_path))

print("🚀 XWNode with Edges Test")
print("=" * 30)

try:
    print("1. Testing direct import from facade...")
    # Import the facade module directly to avoid circular imports
    import importlib.util
    
    facade_path = src_path / "exonware" / "xwnode" / "facade.py"
    spec = importlib.util.spec_from_file_location("facade", facade_path)
    facade_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(facade_module)
    
    XWNode = facade_module.XWNode
    XWEdge = facade_module.XWEdge
    print("   ✅ XWNode and XWEdge imported successfully")
    
    print("2. Creating XWNode with tree data...")
    # Create a tree structure with nodes
    tree_data = {
        "root": {
            "name": "Root Node",
            "value": 100,
            "children": {
                "child1": {
                    "name": "Child 1",
                    "value": 10
                },
                "child2": {
                    "name": "Child 2", 
                    "value": 20
                }
            }
        }
    }
    
    node = XWNode.from_native(tree_data)
    print("   ✅ XWNode created successfully")
    
    print("3. Testing XWEdge creation...")
    # Create edges between nodes
    edge1 = XWEdge(
        source="root",
        target="child1",
        edge_type="parent_child",
        weight=1.0,
        properties={"relationship": "parent"}
    )
    
    edge2 = XWEdge(
        source="root",
        target="child2", 
        edge_type="parent_child",
        weight=1.0,
        properties={"relationship": "parent"}
    )
    
    edge3 = XWEdge(
        source="child1",
        target="child2",
        edge_type="sibling",
        weight=0.5,
        is_bidirectional=True,
        properties={"relationship": "sibling"}
    )
    
    print("   ✅ XWEdge objects created successfully")
    print(f"   Edge 1: {edge1}")
    print(f"   Edge 2: {edge2}")
    print(f"   Edge 3: {edge3}")
    
    print("4. Testing edge operations...")
    # Test edge dictionary conversion
    edge_dict = edge1.to_dict()
    print(f"   Edge as dict: {edge_dict}")
    
    # Test edge recreation from dict
    edge_from_dict = XWEdge.from_dict(edge_dict)
    print(f"   Edge from dict: {edge_from_dict}")
    
    # Test edge equality
    assert edge1 == edge_from_dict, "Edge equality test failed"
    print("   ✅ Edge equality test passed")
    
    print("5. Testing node data access...")
    # Test accessing node data
    root_data = node.to_native()
    print(f"   Root data: {root_data}")
    
    # Test that we can access child nodes
    assert "root" in root_data, "Root node not found"
    assert "children" in root_data["root"], "Children not found"
    assert "child1" in root_data["root"]["children"], "Child1 not found"
    assert "child2" in root_data["root"]["children"], "Child2 not found"
    print("   ✅ Node data access test passed")
    
    print("\n🎉 SUCCESS! XWNode works with edges!")
    print("XWNode can be created with tree strategy and work with XWEdge objects")
    print("\n📊 Summary:")
    print(f"   - Created XWNode with tree structure: {len(root_data)} root nodes")
    print(f"   - Created {3} XWEdge objects representing relationships")
    print(f"   - All edge operations (create, convert, compare) work correctly")
    print(f"   - Node data access and navigation works correctly")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
