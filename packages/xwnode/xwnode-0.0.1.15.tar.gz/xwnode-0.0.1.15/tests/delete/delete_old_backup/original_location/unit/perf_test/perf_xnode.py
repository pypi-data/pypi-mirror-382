#!/usr/bin/env python3
"""
Performance benchmark script for xNode operations.
Runs 1000 iterations of each scenario and logs average times to CSV.
"""

import sys
import os
import time
import csv
from pathlib import Path

# Add src to path for imports
# From tests/packages/xnode/unit/perf_test/ go up 5 levels to reach project root
project_root = Path(__file__).parent.parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    # Try direct import first
    import src.xlib.xnode as xnode_module
    XNode = xnode_module.XNode
    print("✅ Successfully imported XNode")
except ImportError:
    try:
        # Fallback to alternative import method
        from src.xlib.xnode import XNode
        print("✅ Successfully imported XNode (fallback)")
    except ImportError as e:
        print(f"❌ Failed to import XNode: {e}")
        print(f"📂 Current working directory: {os.getcwd()}")
        print(f"📂 Script location: {Path(__file__).parent}")
        print(f"📂 Src path: {src_path}")
        print(f"📂 Src exists: {src_path.exists()}")
        if src_path.exists():
            print(f"📂 Src contents: {list(src_path.iterdir())}")
        sys.exit(1)

# Configuration
ITERATIONS = 1000
CSV_FILE = Path(__file__).parent / "perf_xnode.csv"

def measure_time(func, *args, **kwargs):
    """Measure execution time of a function over multiple iterations."""
    times = []
    for _ in range(ITERATIONS):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Error in {func.__name__}: {e}")
            return float('inf')
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds
    
    # Remove outliers (top and bottom 5%)
    times.sort()
    trimmed_times = times[int(0.05 * len(times)):int(0.95 * len(times))]
    return sum(trimmed_times) / len(trimmed_times)

def scenario_deep_nesting():
    """Test performance with deep nested structures."""
    # Create 100 levels of nesting
    data = {}
    current = data
    for i in range(100):
        current[f'level_{i}'] = {}
        current = current[f'level_{i}']
    current['value'] = 'deep_value'
    
    # Test creation and navigation
    node = XNode.from_native(data)
    result = node.find('level_0.level_1.level_2.level_3.level_4')
    return result.value

def scenario_wide_structure():
    """Test performance with wide structures."""
    # Create dict with 10,000 keys
    data = {f'key_{i}': f'value_{i}' for i in range(10000)}
    
    # Test creation and access
    node = XNode.from_native(data)
    result = node['key_5000']
    return result.value

def scenario_large_array():
    """Test performance with large arrays."""
    # Create array with 10,000 elements
    data = [f'item_{i}' for i in range(10000)]
    
    # Test creation and access
    node = XNode.from_native(data)
    result = node[5000]
    return result.value

def scenario_lazy_loading():
    """Test lazy loading performance with large structures."""
    # Create a large nested structure
    data = {
        'large_list': [{'id': i, 'data': f'item_{i}', 'nested': {'value': i * 2}} for i in range(1000)],
        'large_dict': {f'key_{i}': {'value': i, 'nested': [i, i+1, i+2]} for i in range(1000)}
    }
    
    # Test with lazy loading enabled (default)
    node = XNode.from_native(data, use_lazy=True)
    # Access only a few items to test lazy behavior
    result1 = node.find('large_list.100.nested.value')
    result2 = node.find('large_dict.key_500.value')
    return result1.value + result2.value

def scenario_bulk_operations():
    """Test bulk operations performance."""
    # Create initial data
    data = {'users': [], 'settings': {}}
    node = XNode.from_native(data)
    
    # Perform multiple operations in bulk
    result = (node.bulk()
              .set('settings.theme', 'dark')
              .set('settings.language', 'en')
              .append('users', {'name': 'John', 'age': 30})
              .append('users', {'name': 'Jane', 'age': 25})
              .update('settings', {'notifications': True})
              .execute())
    
    return len(result.find('users'))

def scenario_conversion_caching():
    """Test conversion caching performance."""
    # Create data with repeated conversions
    data = {'value': 42, 'text': 'hello', 'flag': True}
    node = XNode.from_native(data)
    
    # Call to_native multiple times to test caching
    results = []
    for _ in range(10):
        results.append(node.to_native())
    
    return len(results)

def scenario_optimized_iteration():
    """Test optimized iteration performance."""
    # Create large list for iteration
    data = [{'id': i, 'value': f'item_{i}'} for i in range(1000)]
    node = XNode.from_native(data)
    
    # Test chunked iteration
    total_items = 0
    for chunk in node.iter_optimized(chunk_size=50).chunked(50):
        total_items += len(chunk)
    
    return total_items

def scenario_filter_nodes():
    """Test node filtering performance."""
    # Create mixed data structure
    data = {
        'numbers': [1, 2, 3, 4, 5],
        'strings': ['a', 'b', 'c'],
        'nested': {
            'values': [10, 20, 30],
            'flags': [True, False, True]
        }
    }
    node = XNode.from_native(data)
    
    # Filter for leaf nodes with numeric values
    filtered = node.filter_nodes(lambda n: n.is_leaf and isinstance(n.value, int))
    return len(filtered)

def scenario_path_caching():
    """Test path caching performance."""
    # Create nested structure for repeated path access
    data = {
        'level1': {
            'level2': {
                'level3': {
                    'target': 'found'
                }
            }
        }
    }
    node = XNode.from_native(data)
    
    # Access same path multiple times to test caching
    results = []
    for _ in range(20):
        result = node.find('level1.level2.level3.target')
        results.append(result.value)
    
    return len(results)

def ensure_csv_header():
    """Ensure CSV file has proper header."""
    if not CSV_FILE.exists():
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'xnode_version', 
                'deep_nesting_ms', 'wide_structure_ms', 'large_array_ms',
                'lazy_loading_ms', 'bulk_operations_ms', 'conversion_caching_ms',
                'optimized_iteration_ms', 'filter_nodes_ms', 'path_caching_ms'
            ])

def log_to_csv(results):
    """Log results to CSV file."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    xnode_version = '0.0.1'  # From __init__.py
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp, xnode_version,
            results['deep_nesting'],
            results['wide_structure'], 
            results['large_array'],
            results['lazy_loading'],
            results['bulk_operations'],
            results['conversion_caching'],
            results['optimized_iteration'],
            results['filter_nodes'],
            results['path_caching']
        ])

def main():
    """Run all performance benchmarks."""
    print("🚀 Starting xNode Performance Benchmarks")
    print(f"📊 Running {ITERATIONS} iterations per scenario...")
    print()
    
    # Ensure CSV file exists
    ensure_csv_header()
    
    scenarios = [
        ('Deep Nesting', scenario_deep_nesting),
        ('Wide Structure', scenario_wide_structure),
        ('Large Array', scenario_large_array),
        ('Lazy Loading', scenario_lazy_loading),
        ('Bulk Operations', scenario_bulk_operations),
        ('Conversion Caching', scenario_conversion_caching),
        ('Optimized Iteration', scenario_optimized_iteration),
        ('Filter Nodes', scenario_filter_nodes),
        ('Path Caching', scenario_path_caching),
    ]
    
    results = {}
    
    for name, func in scenarios:
        print(f"⏱️  Running {name}...")
        avg_time = measure_time(func)
        results[name.lower().replace(' ', '_')] = round(avg_time, 3)
        print(f"   Average: {avg_time:.3f}ms")
    
    # Log to CSV
    log_to_csv(results)
    
    print()
    print("✅ Performance benchmarks completed!")
    print(f"📄 Results logged to: {CSV_FILE}")
    print()
    print("📈 Summary:")
    for name, time_ms in results.items():
        print(f"   {name.replace('_', ' ').title()}: {time_ms:.3f}ms")

if __name__ == "__main__":
    main() 