#!/usr/bin/env python3
"""
Standalone XWNode Test

Test XWNode functionality without complex imports.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

import sys
import os
from pathlib import Path

print("🚀 Standalone XWNode Test")
print("=" * 30)

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
sys.path.insert(0, str(src_path))

try:
    print("1. Testing basic import...")
    # Import the base module directly without going through __init__.py
    import importlib.util
    
    base_path = src_path / "exonware" / "xwnode" / "base.py"
    spec = importlib.util.spec_from_file_location("base", base_path)
    base_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_module)
    
    XWNodeBase = base_module.XWNodeBase
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
