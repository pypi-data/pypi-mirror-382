#!/usr/bin/env python3
"""
XWQuery Script System Test Runner

This module provides a comprehensive test runner for the XWQuery Script system,
following DEV_GUIDELINES.md standards for production-ready testing.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 10-Sep-2025
"""

import pytest
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class XWQueryScriptTestRunner:
    """Comprehensive test runner for XWQuery Script system."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.test_results = {
            'core': {'passed': 0, 'failed': 0, 'errors': 0, 'tests': []},
            'unit': {'passed': 0, 'failed': 0, 'errors': 0, 'tests': []},
            'integration': {'passed': 0, 'failed': 0, 'errors': 0, 'tests': []}
        }
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all XWQuery Script tests."""
        print("🚀 XWQuery Script System - Comprehensive Test Suite")
        print("=" * 70)
        print(f"📅 Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.start_time = time.time()
        
        # Run core tests
        print("🔧 Running Core Tests...")
        self._run_test_category('core', [
            'tests.core.test_xwquery_script_strategy',
            'tests.core.test_xwnode_query_action_executor'
        ])
        
        # Run unit tests
        print("🧪 Running Unit Tests...")
        self._run_test_category('unit', [
            'tests.unit.test_xwquery_script_integration'
        ])
        
        # Run integration tests
        print("🔗 Running Integration Tests...")
        self._run_test_category('integration', [
            'tests.integration.test_xwquery_script_end_to_end'
        ])
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        return self._generate_report()
    
    def _run_test_category(self, category: str, test_modules: List[str]):
        """Run tests for a specific category."""
        print(f"  📁 Category: {category.upper()}")
        
        for module in test_modules:
            print(f"    📄 Module: {module}")
            try:
                # Run pytest for the module
                result = pytest.main([
                    f"{module}",
                    "-v",
                    "--tb=short",
                    "--no-header",
                    "--disable-warnings"
                ])
                
                # Parse result (pytest returns 0 for success, non-zero for failure)
                if result == 0:
                    self.test_results[category]['passed'] += 1
                    self.test_results[category]['tests'].append({
                        'module': module,
                        'status': 'PASSED',
                        'message': 'All tests passed'
                    })
                    print(f"      ✅ PASSED")
                else:
                    self.test_results[category]['failed'] += 1
                    self.test_results[category]['tests'].append({
                        'module': module,
                        'status': 'FAILED',
                        'message': f'Some tests failed (exit code: {result})'
                    })
                    print(f"      ❌ FAILED (exit code: {result})")
                    
            except Exception as e:
                self.test_results[category]['errors'] += 1
                self.test_results[category]['tests'].append({
                    'module': module,
                    'status': 'ERROR',
                    'message': f'Test execution error: {str(e)}'
                })
                print(f"      💥 ERROR: {str(e)}")
        
        print()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_time = self.end_time - self.start_time
        
        # Calculate totals
        total_passed = sum(cat['passed'] for cat in self.test_results.values())
        total_failed = sum(cat['failed'] for cat in self.test_results.values())
        total_errors = sum(cat['errors'] for cat in self.test_results.values())
        total_tests = total_passed + total_failed + total_errors
        
        # Calculate success rate
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'errors': total_errors,
                'success_rate': success_rate,
                'execution_time': total_time
            },
            'categories': self.test_results,
            'timestamp': datetime.now().isoformat(),
            'status': 'PASSED' if total_failed == 0 and total_errors == 0 else 'FAILED'
        }
        
        # Print report
        self._print_report(report)
        
        return report
    
    def _print_report(self, report: Dict[str, Any]):
        """Print comprehensive test report."""
        print("📊 XWQuery Script System - Test Results")
        print("=" * 70)
        
        # Summary
        summary = report['summary']
        print(f"📈 Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   💥 Errors: {summary['errors']}")
        print(f"   📊 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   ⏱️  Execution Time: {summary['execution_time']:.2f}s")
        print()
        
        # Category breakdown
        print("📁 Category Breakdown:")
        for category, results in report['categories'].items():
            category_total = results['passed'] + results['failed'] + results['errors']
            category_success_rate = (results['passed'] / category_total * 100) if category_total > 0 else 0
            
            print(f"   {category.upper()}:")
            print(f"     Tests: {category_total}")
            print(f"     Passed: {results['passed']}")
            print(f"     Failed: {results['failed']}")
            print(f"     Errors: {results['errors']}")
            print(f"     Success Rate: {category_success_rate:.1f}%")
            print()
        
        # Detailed results
        print("📋 Detailed Results:")
        for category, results in report['categories'].items():
            print(f"   {category.upper()}:")
            for test in results['tests']:
                status_icon = "✅" if test['status'] == 'PASSED' else "❌" if test['status'] == 'FAILED' else "💥"
                print(f"     {status_icon} {test['module']}: {test['status']}")
                if test['status'] != 'PASSED':
                    print(f"        💬 {test['message']}")
            print()
        
        # Overall status
        status_icon = "🎉" if report['status'] == 'PASSED' else "⚠️"
        print(f"{status_icon} Overall Status: {report['status']}")
        
        if report['status'] == 'PASSED':
            print("🚀 XWQuery Script System is production ready!")
        else:
            print("🔧 XWQuery Script System needs attention before production deployment.")
        
        print("=" * 70)
    
    def run_core_tests_only(self) -> Dict[str, Any]:
        """Run only core tests."""
        print("🔧 XWQuery Script System - Core Tests Only")
        print("=" * 50)
        
        self.start_time = time.time()
        
        self._run_test_category('core', [
            'tests.core.test_xwquery_script_strategy',
            'tests.core.test_xwnode_query_action_executor'
        ])
        
        self.end_time = time.time()
        
        # Generate report for core tests only
        core_results = {
            'core': self.test_results['core']
        }
        
        total_passed = core_results['core']['passed']
        total_failed = core_results['core']['failed']
        total_errors = core_results['core']['errors']
        total_tests = total_passed + total_failed + total_errors
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'errors': total_errors,
                'success_rate': success_rate,
                'execution_time': self.end_time - self.start_time
            },
            'categories': core_results,
            'timestamp': datetime.now().isoformat(),
            'status': 'PASSED' if total_failed == 0 and total_errors == 0 else 'FAILED'
        }
        
        self._print_report(report)
        return report
    
    def run_unit_tests_only(self) -> Dict[str, Any]:
        """Run only unit tests."""
        print("🧪 XWQuery Script System - Unit Tests Only")
        print("=" * 50)
        
        self.start_time = time.time()
        
        self._run_test_category('unit', [
            'tests.unit.test_xwquery_script_integration'
        ])
        
        self.end_time = time.time()
        
        # Generate report for unit tests only
        unit_results = {
            'unit': self.test_results['unit']
        }
        
        total_passed = unit_results['unit']['passed']
        total_failed = unit_results['unit']['failed']
        total_errors = unit_results['unit']['errors']
        total_tests = total_passed + total_failed + total_errors
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'errors': total_errors,
                'success_rate': success_rate,
                'execution_time': self.end_time - self.start_time
            },
            'categories': unit_results,
            'timestamp': datetime.now().isoformat(),
            'status': 'PASSED' if total_failed == 0 and total_errors == 0 else 'FAILED'
        }
        
        self._print_report(report)
        return report
    
    def run_integration_tests_only(self) -> Dict[str, Any]:
        """Run only integration tests."""
        print("🔗 XWQuery Script System - Integration Tests Only")
        print("=" * 50)
        
        self.start_time = time.time()
        
        self._run_test_category('integration', [
            'tests.integration.test_xwquery_script_end_to_end'
        ])
        
        self.end_time = time.time()
        
        # Generate report for integration tests only
        integration_results = {
            'integration': self.test_results['integration']
        }
        
        total_passed = integration_results['integration']['passed']
        total_failed = integration_results['integration']['failed']
        total_errors = integration_results['integration']['errors']
        total_tests = total_passed + total_failed + total_errors
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'errors': total_errors,
                'success_rate': success_rate,
                'execution_time': self.end_time - self.start_time
            },
            'categories': integration_results,
            'timestamp': datetime.now().isoformat(),
            'status': 'PASSED' if total_failed == 0 and total_errors == 0 else 'FAILED'
        }
        
        self._print_report(report)
        return report


def main():
    """Main function to run XWQuery Script tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='XWQuery Script System Test Runner')
    parser.add_argument('--category', choices=['all', 'core', 'unit', 'integration'], 
                       default='all', help='Test category to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    runner = XWQueryScriptTestRunner()
    
    try:
        if args.category == 'all':
            report = runner.run_all_tests()
        elif args.category == 'core':
            report = runner.run_core_tests_only()
        elif args.category == 'unit':
            report = runner.run_unit_tests_only()
        elif args.category == 'integration':
            report = runner.run_integration_tests_only()
        
        # Exit with appropriate code
        if report['status'] == 'PASSED':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
