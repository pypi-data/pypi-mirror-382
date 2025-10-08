#!/usr/bin/env python3
"""
Simple Import Test

Test basic import functionality for xwnode.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

import sys
import os
from pathlib import Path

# Add src paths for local testing
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
xwsystem_src_path = current_dir.parent.parent / "xwsystem" / "src"

print(f"Current directory: {current_dir}")
print(f"Source path: {src_path}")
print(f"XWSystem path: {xwsystem_src_path}")

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
    print(f"Added src path: {src_path}")

if str(xwsystem_src_path) not in sys.path and xwsystem_src_path.exists():
    sys.path.insert(0, str(xwsystem_src_path))
    print(f"Added xwsystem path: {xwsystem_src_path}")

print(f"Python path: {sys.path[:3]}")

def test_imports():
    """Test basic imports."""
    print("\n🧪 Testing Imports")
    print("=" * 30)
    
    try:
        # Test 1: Import the package
        print("1. Testing package import...")
        import exonware
        print("   ✅ exonware package imported")
        
        # Test 2: Import xwnode subpackage
        print("2. Testing xwnode subpackage import...")
        import exonware.xwnode
        print("   ✅ exonware.xwnode imported")
        
        # Test 3: Import XWNode class
        print("3. Testing XWNode class import...")
        from exonware.xwnode import XWNode
        print("   ✅ XWNode class imported")
        print(f"   XWNode type: {type(XWNode)}")
        
        # Test 4: Try convenience import
        print("4. Testing convenience import...")
        import xwnode
        print("   ✅ xwnode convenience import successful")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_basic_creation():
    """Test basic XWNode creation."""
    print("\n🧪 Testing Basic Creation")
    print("=" * 30)
    
    try:
        from exonware.xwnode import XWNode
        
        # Create a simple node
        print("1. Creating simple XWNode...")
        node = XWNode.from_native({"name": "test", "value": 42})
        print("   ✅ XWNode created successfully")
        print(f"   Node type: {type(node)}")
        
        # Test basic functionality
        print("2. Testing basic functionality...")
        data = node.to_native()
        print(f"   ✅ to_native() works: {data}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple Import Test")
    print("=" * 50)
    
    import_success = test_imports()
    creation_success = test_basic_creation()
    
    if import_success and creation_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("XWNode can be imported and created successfully")
    else:
        print("\n💥 SOME TESTS FAILED!")
        if not import_success:
            print("- Import test failed")
        if not creation_success:
            print("- Creation test failed")
        sys.exit(1)
