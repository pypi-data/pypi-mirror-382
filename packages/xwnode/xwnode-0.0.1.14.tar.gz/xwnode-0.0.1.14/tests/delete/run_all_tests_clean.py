#!/usr/bin/env python3
"""
xNode Test Runner - Reorganized Structure
========================================

Comprehensive test runner for the reorganized xNode test suite.
Supports the new modular test structure with component-specific testing.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def run_tests(component: Optional[str] = None, verbose: bool = False, coverage: bool = False, 
              parallel: bool = False, specific_test: Optional[str] = None) -> int:
    """Run xNode tests with various options."""
    
    # Base command
    cmd = ["python", "-m", "pytest"]
    
    # Test directory
    test_dir = Path(__file__).parent
    
    # Determine test path based on component
    if component:
        component_map = {
            'core': 'unit/core',
            'performance': 'unit/performance', 
            'structures': 'unit/structures',
            'graph': 'unit/graph',
            'query': 'unit/query',
            'integration': 'unit/integration',
            'benchmarks': 'benchmarks',
            'all': '.'
        }
        
        if component in component_map:
            test_path = test_dir / component_map[component]
            cmd.append(str(test_path))
        else:
            print(f"❌ Unknown component: {component}")
            print(f"🔍 Available components: {', '.join(component_map.keys())}")
            return 1
    elif specific_test:
        # Run specific test file or pattern
        cmd.append(str(test_dir / specific_test))
    else:
        # Run all tests
        cmd.append(str(test_dir))
    
    # Add options
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=src.xlib.xnode", 
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-branch"
        ])
    
    if parallel:
        cmd.extend(["-n", "auto"])  # Requires pytest-xdist
    
    # Add useful flags
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Fail on unknown markers
        "--strict-config",  # Fail on unknown config options
        "--durations=10",  # Show 10 slowest tests
        "-ra"  # Show short test summary for all except passed
    ])
    
    print(f"🚀 Running xNode tests")
    print(f"📁 Test directory: {test_dir}")
    print(f"🎯 Component: {component if component else 'all'}")
    print(f"📋 Command: {' '.join(cmd)}")
    print("=" * 80)
    
    # Run the tests
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode

def run_component_suite(component: str, verbose: bool = True) -> int:
    """Run tests for a specific component."""
    print(f"\n🧪 Testing {component.upper()} Component")
    print("=" * 50)
    
    return run_tests(component=component, verbose=verbose)

def run_comprehensive_suite() -> int:
    """Run comprehensive test suite covering all components."""
    components = ['core', 'performance', 'structures', 'graph', 'query', 'integration']
    
    print("🎯 Running Comprehensive xNode Test Suite")
    print("=" * 60)
    
    overall_result = 0
    results = {}
    
    for component in components:
        print(f"\n📋 Testing {component.upper()} component...")
        result = run_component_suite(component, verbose=False)
        results[component] = result
        if result != 0:
            overall_result = result
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 60)
    
    for component, result in results.items():
        status = "✅ PASSED" if result == 0 else "❌ FAILED"
        print(f"{component.ljust(15)}: {status}")
    
    print("=" * 60)
    
    if overall_result == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("💥 SOME TESTS FAILED!")
    
    return overall_result

def run_performance_benchmarks() -> int:
    """Run performance benchmarks specifically."""
    print("⚡ Running Performance Benchmarks")
    print("=" * 40)
    
    return run_tests(component='benchmarks', verbose=True)

def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description='xNode Test Runner - Reorganized Structure')
    
    parser.add_argument('--component', '-c', 
                       choices=['core', 'performance', 'structures', 'graph', 'query', 'integration', 'benchmarks', 'all'],
                       help='Run tests for specific component')
    
    parser.add_argument('--test', '-t',
                       help='Run specific test file or pattern')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--coverage', '--cov', action='store_true',
                       help='Generate coverage report')
    
    parser.add_argument('--parallel', '-p', action='store_true',
                       help='Run tests in parallel')
    
    parser.add_argument('--comprehensive', action='store_true',
                       help='Run comprehensive test suite for all components')
    
    parser.add_argument('--benchmarks', action='store_true',
                       help='Run performance benchmarks')
    
    args = parser.parse_args()
    
    try:
        if args.comprehensive:
            return run_comprehensive_suite()
        elif args.benchmarks:
            return run_performance_benchmarks()
        else:
            return run_tests(
                component=args.component,
                verbose=args.verbose,
                coverage=args.coverage,
                parallel=args.parallel,
                specific_test=args.test
            )
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
