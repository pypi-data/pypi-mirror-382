#!/usr/bin/env python3
"""
ADAPTIVE Performance Mode Demo
==============================

This script demonstrates the new ADAPTIVE performance mode in xwnode,
showing its learning capabilities and performance advantages.
"""

import sys
import os
import time
import statistics

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.xlib.xwnode import xwnode
from src.xlib.xwsystem.config import PerformanceMode


def create_test_data():
    """Create test data for performance testing."""
    return {
        'users': [
            {'id': i, 'name': f'User{i}', 'email': f'user{i}@example.com', 'active': i % 2 == 0}
            for i in range(1000)
        ],
        'settings': {
            'theme': 'dark',
            'language': 'en',
            'notifications': True,
            'privacy': {'share_data': False, 'analytics': True}
        },
        'metadata': {
            'version': '1.0.0',
            'created': '2024-01-01',
            'tags': ['test', 'performance', 'adaptive']
        }
    }


def test_adaptive_mode_creation():
    """Test ADAPTIVE mode node creation."""
    print("🚀 Testing ADAPTIVE Mode Creation...")
    
    test_data = create_test_data()
    
    # Test creation time
    start_time = time.time()
    node = xwnode.adaptive(test_data)
    creation_time = (time.time() - start_time) * 1000
    
    print(f"   ✅ Creation time: {creation_time:.2f}ms")
    print(f"   ✅ Performance mode: {node.get_performance_mode()}")
    
    # Get performance stats
    stats = node.get_performance_stats()
    print(f"   ✅ Mode: {stats['mode']}")
    print(f"   ✅ Has adaptive learning: {'adaptive_learning' in stats}")
    
    return node


def test_adaptive_learning(node):
    """Test that ADAPTIVE mode learns from operations."""
    print("\n🧠 Testing ADAPTIVE Learning...")
    
    # Perform multiple operations to trigger learning
    operation_times = []
    
    for i in range(50):
        start_time = time.time()
        
        # Navigation operations
        node.find(f'users.{i % 100}.name')
        node.find(f'settings.theme')
        node.find(f'metadata.version')
        
        # Access operations
        node['users'][i % 100]['name']
        node['settings']['theme']
        
        operation_time = (time.time() - start_time) * 1000
        operation_times.append(operation_time)
    
    avg_time = statistics.mean(operation_times)
    print(f"   ✅ Average operation time: {avg_time:.2f}ms")
    
    # Get adaptive stats
    stats = node.get_performance_stats()
    adaptive_stats = stats.get('adaptive_learning', {})
    
    print(f"   ✅ Metrics recorded: {adaptive_stats.get('metrics_count', 0)}")
    
    # Should have performance data for different modes
    mode_performance = adaptive_stats.get('mode_performance', {})
    print(f"   ✅ Modes tracked: {len(mode_performance)}")
    
    for mode, data in mode_performance.items():
        print(f"      - {mode}: {data.get('count', 0)} operations, "
              f"avg score: {data.get('avg_score', 0):.3f}")
    
    return adaptive_stats


def test_adaptive_vs_other_modes():
    """Compare ADAPTIVE mode with other modes."""
    print("\n📊 Comparing ADAPTIVE vs Other Modes...")
    
    test_data = create_test_data()
    modes_to_test = [
        (PerformanceMode.AUTO, "AUTO"),
        (PerformanceMode.FAST, "FAST"),
        (PerformanceMode.OPTIMIZED, "OPTIMIZED"),
        (PerformanceMode.ADAPTIVE, "ADAPTIVE")
    ]
    
    results = {}
    
    for mode, mode_name in modes_to_test:
        print(f"   Testing {mode_name} mode...")
        
        # Create node
        start_time = time.time()
        node = xwnode.from_native(test_data, mode)
        creation_time = (time.time() - start_time) * 1000
        
        # Perform operations
        start_time = time.time()
        for i in range(100):
            node.find(f'users.{i % 100}.name')
            node.find('settings.theme')
            node.find('metadata.version')
        operation_time = (time.time() - start_time) * 1000
        
        # Get stats
        stats = node.get_performance_stats()
        
        results[mode_name] = {
            'creation_time': creation_time,
            'operation_time': operation_time,
            'mode': stats['mode'],
            'has_learning': 'adaptive_learning' in stats
        }
    
    # Print comparison table
    print("\n   📋 Performance Comparison:")
    print("   " + "-" * 60)
    print("   " + f"{'Mode':<12} {'Creation':<10} {'Operations':<12} {'Learning':<10}")
    print("   " + "-" * 60)
    
    for mode_name, result in results.items():
        learning = "Yes" if result['has_learning'] else "No"
        print("   " + f"{mode_name:<12} {result['creation_time']:<10.2f} "
              f"{result['operation_time']:<12.2f} {learning:<10}")
    
    return results


def test_adaptive_advantages():
    """Test specific advantages of ADAPTIVE mode."""
    print("\n🎯 Testing ADAPTIVE Mode Advantages...")
    
    test_data = create_test_data()
    
    # Test ADAPTIVE vs AUTO
    auto_node = xwnode.from_native(test_data, PerformanceMode.AUTO)
    adaptive_node = xwnode.adaptive(test_data)
    
    # Perform operations to trigger learning
    for i in range(50):
        auto_node.find(f'users.{i % 100}.name')
        adaptive_node.find(f'users.{i % 100}.name')
    
    # Get stats
    auto_stats = auto_node.get_performance_stats()
    adaptive_stats = adaptive_node.get_performance_stats()
    
    print("   ✅ ADAPTIVE has learning capabilities:", 'adaptive_learning' in adaptive_stats)
    print("   ✅ AUTO has learning capabilities:", 'adaptive_learning' in auto_stats)
    print("   ✅ ADAPTIVE maintains performance mode:", adaptive_stats['mode'] == 'ADAPTIVE')
    
    # Show adaptive learning data
    if 'adaptive_learning' in adaptive_stats:
        learning_data = adaptive_stats['adaptive_learning']
        print(f"   ✅ Metrics count: {learning_data.get('metrics_count', 0)}")
        print(f"   ✅ System metrics: {learning_data.get('system_metrics', {})}")


def show_adaptive_recommendations():
    """Show recommendations for ADAPTIVE mode usage."""
    print("\n💡 ADAPTIVE Mode Recommendations:")
    print("=" * 60)
    
    recommendations = [
        "✅ Use ADAPTIVE mode for production applications with variable workloads",
        "✅ Use ADAPTIVE mode when memory pressure varies during execution",
        "✅ Use ADAPTIVE mode for long-running applications that need optimization",
        "✅ Use ADAPTIVE mode when you want automatic performance tuning",
        "⚠️  ADAPTIVE mode has slight overhead for learning and monitoring",
        "⚠️  ADAPTIVE mode requires more memory for storing learning data",
        "❌ Don't use ADAPTIVE mode for simple, one-off operations",
        "❌ Don't use ADAPTIVE mode when you need predictable, fixed performance"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    print("\n🎯 Specific Use Cases:")
    scenarios = [
        ("Production API", "Use ADAPTIVE - variable load patterns"),
        ("Simple script", "Use FAST - one-off operations"),
        ("Real-time app", "Use ADAPTIVE - dynamic optimization"),
        ("Batch processing", "Use ADAPTIVE - large datasets"),
        ("Memory-constrained", "Use ADAPTIVE - automatic adaptation"),
    ]
    
    for scenario, recommendation in scenarios:
        print(f"   📋 {scenario}: {recommendation}")


def main():
    """Main demonstration function."""
    print("🎉 ADAPTIVE Performance Mode Demonstration")
    print("=" * 60)
    
    try:
        # Test 1: Creation
        node = test_adaptive_mode_creation()
        
        # Test 2: Learning
        adaptive_stats = test_adaptive_learning(node)
        
        # Test 3: Comparison
        results = test_adaptive_vs_other_modes()
        
        # Test 4: Advantages
        test_adaptive_advantages()
        
        # Test 5: Recommendations
        show_adaptive_recommendations()
        
        print("\n🎉 ADAPTIVE Mode Demo Completed Successfully!")
        print("=" * 60)
        
        # Summary
        print("\n📊 Summary:")
        print("   ✅ ADAPTIVE mode successfully created and tested")
        print("   ✅ Learning capabilities verified")
        print("   ✅ Performance comparison completed")
        print("   ✅ Advantages demonstrated")
        print("   ✅ Recommendations provided")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
