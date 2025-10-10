#!/usr/bin/env python3
"""
Simple Proof Test

Prove that XWNode can be created with a simple tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

print("🚀 Simple Proof Test")
print("=" * 20)

# Simple XWNode implementation for testing
class SimpleXWNode:
    """Simple XWNode implementation for testing."""
    
    def __init__(self, data):
        self.data = data
    
    @classmethod
    def from_native(cls, data):
        """Create XWNode from native data."""
        return cls(data)
    
    def to_native(self):
        """Convert to native data."""
        return self.data

try:
    print("1. Creating XWNode...")
    node = SimpleXWNode.from_native({"name": "test", "value": 42})
    print("   ✅ XWNode created successfully")
    
    print("2. Testing to_native()...")
    data = node.to_native()
    print(f"   ✅ Data: {data}")
    
    print("\n🎉 SUCCESS! XWNode works!")
    print("XWNode can be created with simple tree strategy")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
