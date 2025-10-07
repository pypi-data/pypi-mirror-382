#!/usr/bin/env python3
"""
Test script to run all examples and ensure they work correctly.

This script runs all the examples in the goodgleif package to verify
they work with the current data and functionality.
"""

import sys
import traceback
from pathlib import Path


def run_example(example_name: str, example_func):
    """Run a single example and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {example_name}")
    print('='*60)
    
    try:
        result = example_func()
        print(f"\n✓ {example_name} completed successfully")
        return True, result
    except Exception as e:
        print(f"\n✗ {example_name} failed with error:")
        print(f"  {type(e).__name__}: {e}")
        print(f"  Traceback:")
        traceback.print_exc()
        return False, None


def main():
    """Run all examples and report results."""
    print("GoodGleif Examples Test Suite")
    print("=" * 50)
    
    # Import all examples
    try:
        from goodgleif.examples.simple_usage_example import simple_usage_example
        from goodgleif.examples.basic_matching_example import basic_matching_example
        from goodgleif.examples.comprehensive_example import comprehensive_example
        from goodgleif.examples.lei_extraction_example import main as lei_extraction_main
    except ImportError as e:
        print(f"Error importing examples: {e}")
        print("Make sure you're running from the project root directory.")
        return False
    
    # List of examples to run
    examples = [
        ("Simple Usage Example", simple_usage_example),
        ("Basic Matching Example", basic_matching_example),
        ("LEI Extraction Example", lei_extraction_main),
        ("Comprehensive Example", comprehensive_example),
    ]
    
    # Run all examples
    results = {}
    passed = 0
    failed = 0
    
    for name, func in examples:
        success, result = run_example(name, func)
        results[name] = {'success': success, 'result': result}
        
        if success:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)
    print(f"Total examples: {len(examples)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(examples)*100:.1f}%")
    
    if failed > 0:
        print(f"\nFailed examples:")
        for name, result in results.items():
            if not result['success']:
                print(f"  - {name}")
    
    print(f"\n{'='*60}")
    if failed == 0:
        print("🎉 All examples passed!")
        return True
    else:
        print(f"❌ {failed} example(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
