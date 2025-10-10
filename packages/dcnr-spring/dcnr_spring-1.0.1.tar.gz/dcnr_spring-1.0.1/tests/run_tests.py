#!/usr/bin/env python3
"""
Test runner for dcnr-spring package.

This script runs all test modules and provides a summary of the results.
"""

import unittest
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def discover_and_run_tests():
    """Discover and run all tests in the tests directory."""
    
    # Get the directory containing this script (tests directory)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover all test modules in the tests directory
    test_suite = loader.discover(
        start_dir=tests_dir,
        pattern='test_*.py',
        top_level_dir=project_root
    )
    
    # Create a test runner with verbosity
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run the tests
    print("Running dcnr-spring package tests...")
    print("=" * 70)
    
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} test(s) failed")
    
    return success

def run_specific_test_module(module_name):
    """Run tests from a specific module."""
    try:
        # Import the module
        module = __import__(f'tests.{module_name}', fromlist=[''])
        
        # Create test suite from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
        
    except ImportError as e:
        print(f"Error importing test module '{module_name}': {e}")
        return False

def main():
    """Main entry point for the test runner."""
    
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        if not module_name.startswith('test_'):
            module_name = f'test_{module_name}'
        
        success = run_specific_test_module(module_name)
    else:
        # Run all tests
        success = discover_and_run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
