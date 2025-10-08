#!/usr/bin/env python3
"""
Main runner script for all xNode tests.
Provides convenient test execution across all xNode components.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_all_tests(verbose=True, coverage=False, component=None):
    """Run xNode tests."""
    
    base_path = Path(__file__).parent
    
    if component:
        # Handle special performance component
        if component == "perf":
            # Use the dedicated performance runner for perf tests
            perf_runner = base_path / "unit" / "perf_test" / "runner.py"
            if not perf_runner.exists():
                print(f"❌ Performance runner not found: {perf_runner}")
                return 1
            
            print(f"🚀 Delegating to dedicated performance runner...")
            print(f"📂 Runner: {perf_runner}")
            print("=" * 60)
            
            # Build command with same options
            cmd = [sys.executable, str(perf_runner)]
            if verbose:
                cmd.append("-v")
            if coverage:
                cmd.append("-c")
            
            result = subprocess.run(cmd)
            return result.returncode
        
        # Handle other components normally
        component_path = base_path / "unit" / f"{component}_tests"
        if not component_path.exists():
            print(f"❌ Component '{component}' not found")
            available_components = [d.name.replace('_tests', '') for d in (base_path / "unit").iterdir() if d.is_dir() and d.name.endswith('_tests')]
            available_components.append("perf")  # Add perf to available components
            print(f"Available components: {', '.join(sorted(available_components))}")
            return 1
        test_path = str(component_path)
    else:
        # Run all tests
        test_path = str(base_path)
    
    # Construct pytest command
    cmd = [sys.executable, "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src.xlib.xnode", "--cov-report=term-missing", "--cov-report=html"])
    
    cmd.extend(["--tb=short", "-x"])  # Stop on first failure
    
    print(f"🧪 Running xNode tests...")
    print(f"📂 Test path: {test_path}")
    print(f"▶️  Command: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    return result.returncode


def list_components():
    """List available test components."""
    base_path = Path(__file__).parent / "unit"
    components = []
    
    if base_path.exists():
        for item in base_path.iterdir():
            if item.is_dir() and item.name.endswith('_tests'):
                component_name = item.name.replace('_tests', '')
                components.append(component_name)
    
    print("📋 Available xNode test components:")
    for component in sorted(components):
        print(f"   📦 {component}")
    return 0


def main():
    """Main runner function."""
    parser = argparse.ArgumentParser(
        description="xNode Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python runner.py                    # Run all tests
    python runner.py -v                 # Run with verbose output
    python runner.py -c                 # Run with coverage
    python runner.py -t core            # Run core tests only
    python runner.py -t navigation      # Run navigation tests only
    python runner.py -t errors          # Run error tests only
    python runner.py -l                 # List available components
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Enable coverage reporting')
    parser.add_argument('-t', '--component', 
                       help='Run specific component tests (core, navigation, errors, model, integration, perf)')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List available test components')
    
    args = parser.parse_args()
    
    if args.list:
        return list_components()
    
    print("🧪 xNode Test Runner")
    print("=" * 50)
    
    return run_all_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        component=args.component
    )


if __name__ == '__main__':
    sys.exit(main()) 