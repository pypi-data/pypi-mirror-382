#!/usr/bin/env python3
"""
Minimal XWNode Test

The most basic test to prove XWNode can be created.

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

print("🚀 Minimal XWNode Test")
print("=" * 30)

try:
    print("1. Importing XWNode...")
    from exonware.xwnode import XWNode
    print("   ✅ Import successful")
    
    print("2. Creating XWNode...")
    node = XWNode.from_native({"name": "test", "value": 42})
    print("   ✅ Creation successful")
    
    print("3. Testing to_native()...")
    data = node.to_native()
    print(f"   ✅ Data: {data}")
    
    print("\n🎉 SUCCESS! XWNode works!")
    print("XWNode can be created with simple tree strategy")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
