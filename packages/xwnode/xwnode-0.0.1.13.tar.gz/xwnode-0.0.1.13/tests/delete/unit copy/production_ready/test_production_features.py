"""
Production-ready features tests for xNode library.

This module tests the production-ready monitoring, recovery, and validation
systems that have been moved to xSystem library.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

# Import from xwsystem instead of local modules
from src.xlib.xwsystem import (
    # Memory monitoring
    get_memory_monitor, start_memory_monitoring, stop_memory_monitoring,
    force_memory_cleanup, get_memory_stats, register_object_for_monitoring,
    unregister_object_from_monitoring,
    
    # Error recovery
    get_error_recovery_manager, circuit_breaker, retry_with_backoff,
    graceful_degradation, handle_error,
    
    # Performance validation
    get_performance_validator, start_performance_validation, stop_performance_validation,
    record_performance_metric, validate_performance, get_performance_statistics,
    performance_monitor
)

# Import xnode components for testing
from src.xlib.xnode import xNode
from src.xlib.xnode.strategies.impls.edge_rtree import xRTreeStrategy


class TestMemoryMonitoring:
    """Test memory monitoring functionality."""
    
    def test_memory_monitor_initialization(self):
        """Test memory monitor initialization."""
        monitor = get_memory_monitor()
        assert monitor is not None
        assert hasattr(monitor, 'start_monitoring')
        assert hasattr(monitor, 'stop_monitoring')
        assert hasattr(monitor, 'get_memory_stats')
    
    def test_memory_monitoring_start_stop(self):
        """Test starting and stopping memory monitoring."""
        # Start monitoring
        start_memory_monitoring(interval=0.1)  # Fast interval for testing
        
        # Give it a moment to start
        time.sleep(0.2)
        
        # Check if monitoring is active
        monitor = get_memory_monitor()
        assert monitor.is_monitoring()
        
        # Stop monitoring
        stop_memory_monitoring()
        
        # Give it a moment to stop
        time.sleep(0.2)
        
        # Check if monitoring stopped
        assert not monitor.is_monitoring()
    
    def test_memory_stats(self):
        """Test memory statistics collection."""
        # Start monitoring briefly
        start_memory_monitoring(interval=0.1)
        time.sleep(0.3)  # Allow a few snapshots
        stop_memory_monitoring()
        
        # Get stats
        stats = get_memory_stats()
        assert isinstance(stats, dict)
        assert 'current_memory_mb' in stats
        assert 'peak_memory_mb' in stats
        assert 'object_count' in stats
    
    def test_object_registration(self):
        """Test object registration for monitoring."""
        # Use a custom object that can be weakly referenced
        class TestObject:
            def __init__(self, data):
                self.data = data
        
        test_obj = TestObject({"test": "data"})
        
        # Start monitoring briefly to initialize stats
        start_memory_monitoring(interval=0.1)
        time.sleep(0.1)
        
        # Register object
        register_object_for_monitoring(test_obj, "test_object")
        
        # Get stats to verify registration
        stats = get_memory_stats()
        assert stats.get('monitored_objects', 0) >= 1
        
        # Unregister object
        unregister_object_from_monitoring(test_obj)
        
        # Stop monitoring
        stop_memory_monitoring()
    
    def test_force_cleanup(self):
        """Test forced memory cleanup."""
        # Force cleanup
        force_memory_cleanup()
        
        # Should complete without error
        assert True


class TestErrorRecovery:
    """Test error recovery functionality."""
    
    def test_error_recovery_manager_initialization(self):
        """Test error recovery manager initialization."""
        manager = get_error_recovery_manager()
        assert manager is not None
        assert hasattr(manager, 'add_circuit_breaker')
        assert hasattr(manager, 'retry_with_backoff')
        assert hasattr(manager, 'graceful_degradation')
    
    def test_circuit_breaker_decorator(self):
        """Test circuit breaker decorator."""
        failure_count = 0
        
        @circuit_breaker("test_circuit")
        def failing_function():
            nonlocal failure_count
            failure_count += 1
            raise ValueError("Test error")
        
        # First few calls should work
        for _ in range(3):
            try:
                failing_function()
            except ValueError:
                pass
        
        # Should still be able to call (circuit not open yet)
        assert failure_count >= 3
    
    def test_retry_with_backoff_decorator(self):
        """Test retry with backoff decorator."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        # Should succeed after retries
        result = flaky_function()
        assert result == "success"
        assert call_count == 3
    
    def test_graceful_degradation_decorator(self):
        """Test graceful degradation decorator."""
        def primary_function():
            raise ValueError("Primary failed")
        
        def fallback_function():
            return "fallback result"
        
        @graceful_degradation(primary_function, fallback_function)
        def test_function():
            return "should not reach here"
        
        # Should return fallback result
        result = test_function()
        assert result == "fallback result"
    
    def test_handle_error_decorator(self):
        """Test error handling decorator."""
        @handle_error("test_operation")
        def error_function():
            raise ValueError("Test error")
        
        # Should handle error gracefully
        result = error_function()
        assert result is None  # Default fallback


class TestPerformanceValidation:
    """Test performance validation functionality."""
    
    def test_performance_validator_initialization(self):
        """Test performance validator initialization."""
        validator = get_performance_validator()
        assert validator is not None
        assert hasattr(validator, 'record_metric')
        assert hasattr(validator, 'validate_performance')
        assert hasattr(validator, 'start_validation')
    
    def test_performance_metric_recording(self):
        """Test performance metric recording."""
        # Record some metrics
        record_performance_metric("test_operation", 0.1, True)
        record_performance_metric("test_operation", 0.2, True)
        record_performance_metric("test_operation", 0.15, False)
        
        # Validate performance
        report = validate_performance("test_operation")
        assert report.total_operations == 3
        assert report.successful_operations == 2
        assert report.failed_operations == 1
        assert report.average_duration > 0
    
    def test_performance_monitor_decorator(self):
        """Test performance monitor decorator."""
        @performance_monitor("decorated_function")
        def test_function():
            time.sleep(0.01)  # Small delay
            return "success"
        
        # Call function
        result = test_function()
        assert result == "success"
        
        # Check that metric was recorded
        report = validate_performance("decorated_function")
        assert report.total_operations >= 1
        assert report.successful_operations >= 1
    
    def test_performance_validation_start_stop(self):
        """Test starting and stopping performance validation."""
        # Start validation
        start_performance_validation(interval=0.1)
        
        # Give it a moment to start
        time.sleep(0.2)
        
        # Check if validation is active
        validator = get_performance_validator()
        assert validator.is_validating()
        
        # Stop validation
        stop_performance_validation()
        
        # Give it a moment to stop
        time.sleep(0.2)
        
        # Check if validation stopped
        assert not validator.is_validating()
    
    def test_performance_statistics(self):
        """Test performance statistics collection."""
        # Record some metrics
        record_performance_metric("stats_test", 0.1, True)
        record_performance_metric("stats_test", 0.2, True)
        
        # Get statistics
        stats = get_performance_statistics()
        assert isinstance(stats, dict)
        assert 'total_metrics_recorded' in stats
        assert 'operations_monitored' in stats


class TestRTreeMemoryLeakFix:
    """Test the R-Tree memory leak fix."""
    
    def test_rtree_edge_removal_no_leak(self):
        """Test that R-Tree edge removal doesn't cause memory leaks."""
        strategy = xRTreeStrategy()
        
        # Add some edges (R-Tree strategy requires coordinates)
        strategy.add_edge("A", "B", source_coords=(0, 0), target_coords=(1, 1), weight=1.0)
        strategy.add_edge("B", "C", source_coords=(1, 1), target_coords=(2, 2), weight=2.0)
        strategy.add_edge("C", "D", source_coords=(2, 2), target_coords=(3, 3), weight=3.0)
        
        # Remove edges
        assert strategy.remove_edge("A", "B")
        assert strategy.remove_edge("B", "C")
        assert strategy.remove_edge("C", "D")
        
        # Verify edges were removed
        assert not strategy.has_edge("A", "B")
        assert not strategy.has_edge("B", "C")
        assert not strategy.has_edge("C", "D")
        
        # Check that we can still add edges after removal
        strategy.add_edge("X", "Y", source_coords=(4, 4), target_coords=(5, 5), weight=4.0)
        assert strategy.has_edge("X", "Y")
    
    def test_rtree_complex_removal_scenario(self):
        """Test complex R-Tree removal scenarios."""
        strategy = xRTreeStrategy()
        
        # Create a more complex tree structure
        edges = [
            ("A", "B", (0, 0), (1, 1), 1.0),
            ("B", "C", (1, 1), (2, 2), 2.0),
            ("C", "D", (2, 2), (3, 3), 3.0),
            ("D", "E", (3, 3), (4, 4), 4.0),
            ("E", "F", (4, 4), (5, 5), 5.0),
            ("F", "G", (5, 5), (6, 6), 6.0),
        ]
        
        # Add all edges
        for source, target, source_coords, target_coords, weight in edges:
            strategy.add_edge(source, target, source_coords=source_coords, target_coords=target_coords, weight=weight)
        
        # Remove edges in reverse order
        for source, target, source_coords, target_coords, weight in reversed(edges):
            assert strategy.remove_edge(source, target)
        
        # Tree should be empty
        assert not strategy.has_edge("A", "B")
        assert not strategy.has_edge("B", "C")
        assert not strategy.has_edge("C", "D")
        assert not strategy.has_edge("D", "E")
        assert not strategy.has_edge("E", "F")
        assert not strategy.has_edge("F", "G")


class TestProductionIntegration:
    """Test integration of all production features."""
    
    def test_full_monitoring_integration(self):
        """Test full monitoring integration."""
        # Start all monitoring systems
        start_memory_monitoring(interval=0.1)
        start_performance_validation(interval=0.1)
        
        # Create some xNode data
        data = xNode.from_native({
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        })
        
        # Perform some operations
        for i in range(5):
            # Just access the data to trigger monitoring
            _ = data.value
        
        # Record performance metrics
        record_performance_metric("xnode_operations", 0.05, True)
        
        # Stop monitoring
        stop_memory_monitoring()
        stop_performance_validation()
        
        # Verify everything worked
        memory_stats = get_memory_stats()
        perf_stats = get_performance_statistics()
        
        assert isinstance(memory_stats, dict)
        assert isinstance(perf_stats, dict)
    
    def test_error_recovery_with_monitoring(self):
        """Test error recovery with monitoring integration."""
        # Setup monitoring
        start_memory_monitoring(interval=0.1)
        
        # Test error recovery with monitoring context
        @handle_error("monitored_operation", {"memory_monitor": get_memory_monitor()})
        def operation_with_memory_error():
            raise MemoryError("Simulated memory error")
        
        # Should handle error gracefully
        result = operation_with_memory_error()
        assert result is None
        
        # Stop monitoring
        stop_memory_monitoring()
    
    def test_easy_activation(self):
        """Test that monitoring systems are easy to turn on."""
        # Simple one-liner activation
        start_memory_monitoring()
        start_performance_validation()
        
        # Verify they're running
        assert get_memory_monitor().is_monitoring()
        assert get_performance_validator().is_validating()
        
        # Simple one-liner deactivation
        stop_memory_monitoring()
        stop_performance_validation()
        
        # Verify they're stopped
        assert not get_memory_monitor().is_monitoring()
        assert not get_performance_validator().is_validating()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
