#!/usr/bin/env python3
"""
Integration test script to verify xwnode installation modes work correctly.
Tests the integration between xwnode and xwsystem with different installation modes.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.4
Generation Date: 25-Sep-2025
"""
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
# Add xwsystem src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "xwsystem" / "src"))

import pytest

def test_default_installation():
    """Test default (lite) installation."""
    from exonware.xwnode import XWNode, XWQuery, XWFactory
    
    # Test basic functionality
    node = XWNode.from_native({"test": "data"})
    data = node.to_native()
    assert data == {"test": "data"}

def test_xwsystem_integration():
    """Test xwsystem integration."""
    from exonware.xwsystem import JSONSerializer, YAMLSerializer
    
    # Test serialization
    data = {"test": "data", "number": 42}
    json_serializer = JSONSerializer()
    json_data = json_serializer.dumps(data)
    data_from_json = json_serializer.loads(json_data)
    assert data_from_json == data

def test_lazy_import():
    """Test lazy import functionality."""
    from exonware.xwnode import xwimport
    
    # Test importing a standard library module
    json_module = xwimport("json")
    assert json_module is not None

def test_installation_modes_standalone():
    """Test script that can be run standalone to verify installation modes."""
    print("🚀 Testing xwnode installation modes...\n")
    
    tests = [
        ("Default Installation", test_default_installation),
        ("XWSystem Integration", test_xwsystem_integration),
        ("Lazy Import", test_lazy_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"Testing {test_name.lower()}...")
            test_func()
            print(f"✅ {test_name} works")
            results.append(True)
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append(False)
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! xwnode installation modes work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(test_installation_modes_standalone())
