"""
Test runner for xNode performance mode tests.

This module provides a comprehensive test suite for the xNode performance
mode system, including all the new functionality we've implemented.
"""

import sys
import os
import pytest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def run_performance_mode_tests():
    """Run all performance mode tests."""
    print("🚀 Running xNode Performance Mode Tests")
    print("=" * 50)
    
    # Test file paths
    test_files = [
        "test_performance_modes.py"
    ]
    
    # Run tests
    for test_file in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            print(f"\n📋 Running tests from: {test_file}")
            print("-" * 30)
            
            # Run pytest on the test file
            result = pytest.main([
                str(test_path),
                "-v",
                "--tb=short",
                "--color=yes"
            ])
            
            if result == 0:
                print(f"✅ {test_file} - All tests passed!")
            else:
                print(f"❌ {test_file} - Some tests failed!")
                return False
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print("\n" + "=" * 50)
    print("🎉 All performance mode tests completed!")
    return True

def run_specific_test_category(category: str):
    """Run tests for a specific category."""
    print(f"🎯 Running {category} tests")
    print("=" * 50)
    
    test_path = Path(__file__).parent / "test_performance_modes.py"
    
    if category == "basics":
        result = pytest.main([
            str(test_path),
            "-k", "TestPerformanceModeBasics",
            "-v",
            "--tb=short"
        ])
    elif category == "profiles":
        result = pytest.main([
            str(test_path),
            "-k", "TestPerformanceProfiles",
            "-v",
            "--tb=short"
        ])
    elif category == "xnode":
        result = pytest.main([
            str(test_path),
            "-k", "TestXNodePerformanceModes",
            "-v",
            "--tb=short"
        ])
    elif category == "integration":
        result = pytest.main([
            str(test_path),
            "-k", "TestIntegrationScenarios",
            "-v",
            "--tb=short"
        ])
    else:
        print(f"❌ Unknown test category: {category}")
        return False
    
    return result == 0

def run_quick_tests():
    """Run a quick subset of tests for development."""
    print("⚡ Running Quick Performance Mode Tests")
    print("=" * 50)
    
    test_path = Path(__file__).parent / "test_performance_modes.py"
    
    # Run only basic functionality tests
    result = pytest.main([
        str(test_path),
        "-k", "test_performance_mode_enum or test_default_profile or test_fast_mode_creation",
        "-v",
        "--tb=short"
    ])
    
    return result == 0

def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run xNode Performance Mode Tests")
    parser.add_argument(
        "--category", 
        choices=["basics", "profiles", "xnode", "integration", "quick"],
        help="Run tests for a specific category"
    )
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Run quick tests for development"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
    elif args.category:
        success = run_specific_test_category(args.category)
    else:
        success = run_performance_mode_tests()
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
