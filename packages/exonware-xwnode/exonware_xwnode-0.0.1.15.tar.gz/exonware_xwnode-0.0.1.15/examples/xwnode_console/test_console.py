#!/usr/bin/env python3
"""Quick test to verify console can start without errors."""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("Python version:", sys.version)
print()

try:
    print("Testing console import with lazy loading...")
    from examples.xwnode_console import console
    print("✅ Console module imported successfully")
    
    from examples.xwnode_console import data
    print("✅ Data module imported successfully")
    
    # Test data generation
    collections = data.load_all_collections(seed=42)
    print(f"✅ Generated {sum(len(v) for v in collections.values())} total records")
    
    # Test console creation (should not trigger xwsystem)
    test_console = console.XWQueryConsole(seed=42, verbose=False)
    print("✅ Console created successfully")
    
    print("\n" + "="*60)
    print("SUCCESS - Console ready to run!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

