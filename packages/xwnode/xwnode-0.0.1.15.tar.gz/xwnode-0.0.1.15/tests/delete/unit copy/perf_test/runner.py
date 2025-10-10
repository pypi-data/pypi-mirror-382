#!/usr/bin/env python3
"""
Performance test runner for xwnode.
Provides convenient test execution and benchmark running.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path

def setup_environment():
    """Setup the Python environment for running tests."""
    # Use xwsystem utility for path setup
    try:
        from src.xlib.xwsystem.utils.paths import setup_python_path
        project_root, src_path = setup_python_path(__file__, levels_up=6)
        return project_root, src_path
    except ImportError:
        # Fallback to manual calculation if xwsystem not available
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent.parent.parent.parent
        src_path = project_root / "src"
        
        # Add src to Python path
        src_path_str = str(src_path)
        if src_path_str not in sys.path:
            sys.path.insert(0, src_path_str)
        
        return project_root, src_path

def run_performance_tests(verbose=True, coverage=False, benchmark=False):
    """Run xwnode performance tests."""
    
    base_path = Path(__file__).parent
    
    if benchmark:
        # Run benchmark script directly
        return run_benchmark_only()
    
    # For performance tests, run BOTH pytest tests AND benchmark logging
    print(f"🧪 Running xwnode Performance Tests + Benchmark...")
    print("=" * 60)
    
    # First run the pytest tests (validation)
    test_result = run_pytest_tests(verbose, coverage, base_path)
    
    if test_result == 0:  # Only run benchmark if tests pass
        print("\n" + "=" * 60)
        print("✅ Performance tests passed! Running benchmark logging...")
        print("=" * 60)
        
        # Then run the benchmark script (CSV logging)
        benchmark_result = run_benchmark_only()
        
        return benchmark_result  # Return benchmark result as overall result
    else:
        print("❌ Performance tests failed. Skipping benchmark logging.")
        return test_result


def run_pytest_tests(verbose=True, coverage=False, base_path=None):
    """Run just the pytest performance tests."""
    if base_path is None:
        base_path = Path(__file__).parent
    
    # Setup environment first
    project_root, src_path = setup_environment()
    
    test_path = str(base_path)
    
    # Build PYTHONPATH more robustly
    python_path_parts = [str(src_path), str(project_root)]
    existing_pythonpath = os.environ.get('PYTHONPATH', '')
    if existing_pythonpath:
        python_path_parts.append(existing_pythonpath)
    
    python_path = os.pathsep.join(python_path_parts)
    
    # Construct pytest command
    cmd = [sys.executable, "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src.xlib.xwnode", "--cov-report=term-missing", "--cov-report=html"])
    
    # Add warning suppression for clean output
    cmd.extend(["-W", "ignore::UserWarning", "-W", "ignore::DeprecationWarning"])
    cmd.extend(["--tb=short", "-x"])  # Stop on first failure
    
    print(f"🧪 Running pytest performance tests...")
    print(f"📂 Test path: {test_path}")
    print(f"📂 Project root: {project_root}")
    print(f"📂 Source path: {src_path}")
    print(f"▶️  Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, timeout=300,  # 5 minute timeout
                              cwd=str(project_root),  # Run from project root
                              env={
                                  **dict(os.environ),
                                  'PYTHONPATH': python_path
                              })
        return result.returncode
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def run_benchmark_only():
    """Run just the benchmark script."""
    base_path = Path(__file__).parent
    benchmark_script = base_path / "perf_xwnode.py"
    
    if not benchmark_script.exists():
        print(f"❌ Benchmark script not found: {benchmark_script}")
        return 1
    
    # Setup environment first
    project_root, src_path = setup_environment()
    
    # Build PYTHONPATH more robustly
    python_path_parts = [str(src_path), str(project_root)]
    existing_pythonpath = os.environ.get('PYTHONPATH', '')
    if existing_pythonpath:
        python_path_parts.append(existing_pythonpath)
    
    python_path = os.pathsep.join(python_path_parts)
    
    print(f"🚀 Running xwnode Performance Benchmark...")
    print(f"📂 Script: {benchmark_script}")
    print(f"📂 Project root: {project_root}")
    print(f"📂 Source path: {src_path}")
    
    try:
        result = subprocess.run([sys.executable, str(benchmark_script)], 
                              timeout=600,  # 10 minute timeout
                              cwd=str(project_root),  # Run from project root
                              env={
                                  **dict(os.environ),
                                  'PYTHONPATH': python_path
                              })
        return result.returncode
    except subprocess.TimeoutExpired:
        print("❌ Benchmark timed out after 10 minutes")
        return 1
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        return 1


def show_performance_history():
    """Show performance history from CSV."""
    base_path = Path(__file__).parent
    csv_path = base_path / "perf_xwnode.csv"
    detailed_csv_path = base_path / "perf_xwnode_detailed.csv"
    
    if not csv_path.exists() and not detailed_csv_path.exists():
        print("❌ No performance history found. Run benchmark first.")
        return 1
    
    print("📊 xwnode Performance History")
    print("=" * 80)
    
    try:
        import csv
        
        # Show original format data
        if csv_path.exists():
            print("📈 Original Performance Metrics (perf_xwnode.csv):")
            print("-" * 80)
            
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if rows:
                    # Show last 3 entries from original format
                    print("Last 3 benchmark runs:")
                    print("-" * 50)
                    
                    for i, row in enumerate(rows[-3:], 1):
                        iterations = row.get('iterations', 'N/A')
                        print(f"{i}. {row['timestamp']} (v{row['xwnode_version']}, {iterations} iterations)")
                        print(f"   📊 Core Performance (avg per iteration):")
                        print(f"      Deep nesting:       {row.get('deep_nesting_avg_ms', 'N/A')} ms")
                        print(f"      Wide structure:     {row.get('wide_structure_avg_ms', 'N/A')} ms")
                        print(f"      Large array:        {row.get('large_array_avg_ms', 'N/A')} ms")
                        print()
                else:
                    print("No data found in original CSV.")
        
        # Show detailed format data
        if detailed_csv_path.exists():
            print("🚀 Detailed Performance Metrics (perf_xwnode_detailed.csv):")
            print("-" * 80)
            
            with open(detailed_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if rows:
                    # Show last 3 entries from detailed format
                    print("Last 3 benchmark runs:")
                    print("-" * 50)
                    
                    for i, row in enumerate(rows[-3:], 1):
                        iterations = row.get('iterations', 'N/A')
                        print(f"{i}. {row['timestamp']} (v{row['xwnode_version']}, {iterations} iterations)")
                        print(f"   📊 Core Performance (avg per iteration):")
                        print(f"      Deep nesting:       {row.get('deep_nesting_ms', 'N/A')} ms")
                        print(f"      Wide structure:     {row.get('wide_structure_ms', 'N/A')} ms")
                        print(f"      Large array:        {row.get('large_array_ms', 'N/A')} ms")
                        
                        print(f"   🚀 Optimization Features (avg per iteration):")
                        print(f"      Lazy loading:       {row.get('lazy_loading_ms', 'N/A')} ms")
                        print(f"      Bulk operations:    {row.get('bulk_operations_ms', 'N/A')} ms")
                        print(f"      Conversion caching: {row.get('conversion_caching_ms', 'N/A')} ms")
                        print(f"      Optimized iteration:{row.get('optimized_iteration_ms', 'N/A')} ms")
                        print(f"      Filter nodes:       {row.get('filter_nodes_ms', 'N/A')} ms")
                        print(f"      Path caching:       {row.get('path_caching_ms', 'N/A')} ms")
                        print()
                else:
                    print("No data found in detailed CSV.")
        
        # Show improvement analysis if we have multiple entries
        if csv_path.exists():
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if len(rows) >= 2:
                    print("📈 Performance Trend Analysis (Original Metrics):")
                    print("-" * 80)
                    show_improvement_analysis(rows, is_detailed=False)
    
    except Exception as e:
        print(f"❌ Error reading performance history: {e}")
        return 1
    
    return 0


def show_improvement_analysis(rows, is_detailed=False):
    """Show performance improvement analysis between runs."""
    try:
        if len(rows) < 2:
            print("   Need at least 2 benchmark runs for comparison.")
            return
        
        latest = rows[-1]
        previous = rows[-2]
        
        # Compare core metrics based on format
        if is_detailed:
            metrics_to_compare = [
                ('deep_nesting_ms', 'Deep Nesting'),
                ('wide_structure_ms', 'Wide Structure'),
                ('large_array_ms', 'Large Array'),
            ]
        else:
            metrics_to_compare = [
                ('deep_nesting_avg_ms', 'Deep Nesting'),
                ('wide_structure_avg_ms', 'Wide Structure'),
                ('large_array_avg_ms', 'Large Array'),
            ]
        
        improvements_found = False
        
        for key, name in metrics_to_compare:
            latest_val = latest.get(key)
            previous_val = previous.get(key)
            
            if latest_val and previous_val:
                try:
                    latest_num = float(latest_val)
                    previous_num = float(previous_val)
                    
                    if previous_num > 0:
                        improvement = ((previous_num - latest_num) / previous_num) * 100
                        
                        if abs(improvement) > 1:  # Only show significant changes
                            if improvement > 0:
                                print(f"   ✅ {name}: {improvement:.1f}% faster ({previous_num:.3f}ms → {latest_num:.3f}ms)")
                            else:
                                print(f"   ⚠️  {name}: {abs(improvement):.1f}% slower ({previous_num:.3f}ms → {latest_num:.3f}ms)")
                            improvements_found = True
                
                except (ValueError, TypeError):
                    continue
        
        if not improvements_found:
            print("   📊 Performance appears stable between runs.")
    
    except Exception as e:
        print(f"   ❌ Error in improvement analysis: {e}")


def main():
    """Main runner function."""
    parser = argparse.ArgumentParser(
        description="xwnode Performance Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python runner.py                    # Run performance tests + benchmark
    python runner.py -v                 # Run with verbose output
    python runner.py -c                 # Run with coverage
    python runner.py -b                 # Run benchmark only (no tests)
    python runner.py -t                 # Run tests only (no benchmark)
    python runner.py -H                 # Show performance history
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Enable coverage reporting')
    parser.add_argument('-b', '--benchmark', action='store_true',
                       help='Run performance benchmark only (no tests)')
    parser.add_argument('-t', '--tests-only', action='store_true',
                       help='Run pytest tests only (no benchmark)')
    parser.add_argument('-H', '--history', action='store_true',
                       help='Show performance history')
    
    args = parser.parse_args()
    
    try:
        if args.history:
            return show_performance_history()
        
        if args.tests_only:
            print("🧪 xwnode Performance Tests Only")
            print("=" * 50)
            return run_pytest_tests(args.verbose, args.coverage)
        
        print("🧪 xwnode Performance Test Runner")
        print("=" * 50)
        
        return run_performance_tests(
            verbose=args.verbose,
            coverage=args.coverage,
            benchmark=args.benchmark
        )
    
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 