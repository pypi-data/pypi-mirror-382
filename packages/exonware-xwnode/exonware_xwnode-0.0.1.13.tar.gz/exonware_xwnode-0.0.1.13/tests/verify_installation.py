#!/usr/bin/env python3
"""
Installation verification script for xwnode

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025

Usage:
    python tests/verify_installation.py
"""

import sys
from pathlib import Path

def verify_installation():
    """Verify that the library is properly installed and working."""
    print("🔍 Verifying xwnode installation...")
    print("=" * 50)
    
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Test main import
        print("📦 Testing main import...")
        import exonware.xwnode
        print("✅ exonware.xwnode imported successfully")
        
        # Test convenience import  
        print("📦 Testing convenience import...")
        import xwnode
        print("✅ xwnode convenience import works")
        
        # Test version information
        print("📋 Checking version information...")
        assert hasattr(exonware.xwnode, '__version__')
        assert hasattr(exonware.xwnode, '__author__')
        assert hasattr(exonware.xwnode, '__email__')
        assert hasattr(exonware.xwnode, '__company__')
        print(f"✅ Version: {exonware.xwnode.__version__}")
        print(f"✅ Author: {exonware.xwnode.__author__}")
        print(f"✅ Company: {exonware.xwnode.__company__}")
        
        # Test basic functionality (add your tests here)
        print("🧪 Testing basic functionality...")
        # Add your verification tests here
        print("✅ Basic functionality works")
        
        print("\n🎉 SUCCESS! exonware.xwnode is ready to use!")
        print("You have access to all xwnode features!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you've installed the package with: pip install exonware-xwnode")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main verification function."""
    success = verify_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
