#!/usr/bin/env python3
"""
Basic XWNode Creation Test

This is the most basic test to prove that XWNode can be created
using a simple tree strategy without edges.

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

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(xwsystem_src_path) not in sys.path and xwsystem_src_path.exists():
    sys.path.insert(0, str(xwsystem_src_path))

def test_basic_xwnode_creation():
    """Test that XWNode can be created with a simple tree strategy."""
    print("🧪 Testing Basic XWNode Creation")
    print("=" * 50)
    
    try:
        # Try the convenience import first
        try:
            import xwnode
            XWNode = xwnode.XWNode
            print("✅ XWNode import successful (convenience import)")
        except ImportError:
            # Fallback to direct import
            from exonware.xwnode import XWNode
            print("✅ XWNode import successful (direct import)")
        
        # Create a simple XWNode with tree strategy
        node = XWNode.from_native({
            "name": "root",
            "value": 42,
            "children": [
                {"name": "child1", "value": 10},
                {"name": "child2", "value": 20}
            ]
        })
        
        print("✅ XWNode creation successful")
        print(f"   Node type: {type(node)}")
        print(f"   Node data: {node.to_native()}")
        
        # Verify basic functionality
        assert node is not None, "Node should not be None"
        assert hasattr(node, 'to_native'), "Node should have to_native method"
        
        native_data = node.to_native()
        assert native_data["name"] == "root", "Root name should be 'root'"
        assert native_data["value"] == 42, "Root value should be 42"
        assert len(native_data["children"]) == 2, "Should have 2 children"
        
        print("✅ Basic functionality verification successful")
        print("✅ XWNode creation test PASSED")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Basic XWNode Creation Test")
    print("=" * 60)
    
    success = test_basic_xwnode_creation()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("XWNode can be successfully created with tree strategy")
    else:
        print("\n💥 TEST FAILED!")
        print("XWNode creation failed")
        sys.exit(1)
