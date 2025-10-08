#!/usr/bin/env python3
"""
Test script to check xwnode imports in isolation.
"""

import sys
import os

# Add our src directory to the front of the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Also add xwsystem src directory
xwsystem_src = os.path.join(os.path.dirname(current_dir), 'xwsystem', 'src')
if os.path.exists(xwsystem_src):
    sys.path.insert(0, xwsystem_src)
    print(f"Added xwsystem path: {xwsystem_src}")

print(f"Testing xwnode imports from: {src_dir}")
print(f"Python path[0]: {sys.path[0]}")

try:
    # Test convenience import
    import xwnode
    print("✓ Convenience import 'xwnode' works")
    print(f"  xwnode module file: {xwnode.__file__}")
    print(f"  xwnode version: {xwnode.__version__}")
except Exception as e:
    print(f"✗ Convenience import failed: {e}")

try:
    # Test direct import
    from exonware.xwnode import XWNode, XWQuery, XWFactory
    print("✓ Direct imports work: XWNode, XWQuery, XWFactory")
except Exception as e:
    print(f"✗ Direct imports failed: {e}")
    import traceback
    traceback.print_exc()

try:
    # Test creating a node
    from exonware.xwnode import XWNode
    node = XWNode({'test': 'data'})
    print("✓ XWNode creation works")
    print(f"  Node value: {node.value}")
except Exception as e:
    print(f"✗ XWNode creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\nImport test complete.")
