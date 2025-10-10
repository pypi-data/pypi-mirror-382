#!/usr/bin/env python3
"""
XWNode Base Test - Direct Implementation

Test XWNodeBase creation by directly importing the base module.

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

print("🚀 XWNode Base Test - Direct Implementation")
print("=" * 40)

try:
    print("1. Testing direct import from base module...")
    import exonware.xwnode.base
    XWNodeBase = exonware.xwnode.base.XWNodeBase
    print("   ✅ XWNodeBase imported successfully")
    
    print("2. Creating XWNodeBase...")
    # Create a simple strategy mock
    class SimpleStrategy:
        def __init__(self, data):
            self.data = data
        
        def to_native(self):
            return self.data
        
        def get(self, path, default=None):
            return default
        
        def put(self, path, value):
            return self
        
        def delete(self, path):
            return True
        
        def exists(self, path):
            return False
        
        def create_from_data(self, data):
            return SimpleStrategy(data)
        
        def __len__(self):
            return 1
    
    strategy = SimpleStrategy({"name": "test", "value": 42})
    node = XWNodeBase(strategy)
    print("   ✅ XWNodeBase created successfully")
    
    print("3. Testing to_native()...")
    data = node.to_native()
    print(f"   ✅ Data: {data}")
    
    print("\n🎉 SUCCESS! XWNodeBase works!")
    print("XWNode can be created with simple tree strategy")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
