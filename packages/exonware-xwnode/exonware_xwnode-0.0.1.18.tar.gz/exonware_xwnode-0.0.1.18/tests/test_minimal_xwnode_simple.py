#!/usr/bin/env python3
"""
Minimal XWNode Test - Simple Version

Test basic XWNode creation without complex dependencies.

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

print("🚀 Minimal XWNode Test - Simple Version")
print("=" * 40)

try:
    print("1. Testing direct import from facade...")
    from exonware.xwnode.facade import XWNode
    print("   ✅ XWNode imported successfully")
    
    print("2. Creating XWNode...")
    node = XWNode.from_native({"name": "test", "value": 42})
    print("   ✅ XWNode created successfully")
    
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
