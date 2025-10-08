#!/usr/bin/env python3
#exonware/xwnode/src/exonware/xwnode/strategies/metrics.py
"""
Strategy Metrics and Statistics

Comprehensive metrics collection and analysis for strategy performance,
memory usage, and optimization recommendations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

import time
import threading
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

from ..types import NodeMode, EdgeMode
from .flyweight import get_flyweight_stats
from .pattern_detector import get_detector
from .performance_monitor import get_monitor, get_performance_summary



class MetricType(Enum):
    """Types of metrics to collect."""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    USAGE = "usage"
    OPTIMIZATION = "optimization"
    ERROR = "error"


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""
    timestamp: float
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyMetrics:
    """Comprehensive metrics for a strategy."""
    strategy_id: str
    strategy_name: str
    mode: Union[NodeMode, EdgeMode]
    total_operations: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    memory_usage: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    optimization_score: float = 0.0
    last_updated: float = field(default_factory=time.time)
    snapshots: List[MetricSnapshot] = field(default_factory=list)


class StrategyMetricsCollector:
    """
    Comprehensive metrics collector for strategy performance analysis.
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize metrics collector.
        
        Args:
            history_size: Maximum number of metric snapshots to keep
        """
        self._history_size = history_size
        self._strategy_metrics: Dict[str, StrategyMetrics] = {}
        self._global_metrics: Dict[str, Any] = {
            'total_strategies': 0,
            'total_operations': 0,
            'total_memory_usage': 0.0,
            'average_performance': 0.0,
            'system_uptime': time.time(),
            'last_collection': time.time()
        }
        self._lock = threading.RLock()
        self._collection_interval = 60.0  # 1 minute
        self._last_collection = time.time()
    
    def collect_comprehensive_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive metrics from all components.
        
        Returns:
            Complete metrics dictionary
        """
        with self._lock:
            current_time = time.time()
            
            # Collect from all components
            flyweight_stats = get_flyweight_stats()
            monitor_summary = get_performance_summary()
            detector_stats = get_detector().get_stats()
            
            # Update global metrics
            self._global_metrics.update({
                'total_strategies': len(self._strategy_metrics),
                'total_operations': monitor_summary.get('total_operations', 0),
                'total_memory_usage': monitor_summary.get('average_operation_time', 0.0),
                'average_performance': monitor_summary.get('average_operation_time', 0.0),
                'last_collection': current_time,
                'collection_interval': current_time - self._last_collection
            })
            
            self._last_collection = current_time
            
            return {
                'timestamp': current_time,
                'global_metrics': self._global_metrics.copy(),
                'flyweight_metrics': flyweight_stats,
                'performance_metrics': monitor_summary,
                'detector_metrics': detector_stats,
                'strategy_metrics': self._get_strategy_metrics_summary(),
                'optimization_recommendations': self._generate_optimization_recommendations(),
                'system_health': self._assess_system_health()
            }
    
    def record_strategy_metric(
        self,
        strategy_id: str,
        strategy_name: str,
        mode: Union[NodeMode, EdgeMode],
        metric_type: MetricType,
        value: float,
        **metadata: Any
    ) -> None:
        """
        Record a metric for a specific strategy.
        
        Args:
            strategy_id: Unique strategy identifier
            strategy_name: Human-readable strategy name
            mode: Strategy mode
            metric_type: Type of metric
            value: Metric value
            **metadata: Additional metadata
        """
        with self._lock:
            # Get or create strategy metrics
            if strategy_id not in self._strategy_metrics:
                self._strategy_metrics[strategy_id] = StrategyMetrics(
                    strategy_id=strategy_id,
                    strategy_name=strategy_name,
                    mode=mode
                )
            
            metrics = self._strategy_metrics[strategy_id]
            
            # Update metrics based on type
            if metric_type == MetricType.PERFORMANCE:
                metrics.total_operations += 1
                metrics.total_time += value
                metrics.average_time = metrics.total_time / metrics.total_operations
            elif metric_type == MetricType.MEMORY:
                metrics.memory_usage = value
            elif metric_type == MetricType.ERROR:
                metrics.error_count += 1
                metrics.error_rate = metrics.error_count / max(metrics.total_operations, 1)
            
            # Add snapshot
            snapshot = MetricSnapshot(
                timestamp=time.time(),
                metric_type=metric_type,
                value=value,
                metadata=metadata
            )
            metrics.snapshots.append(snapshot)
            
            # Trim history
            if len(metrics.snapshots) > self._history_size:
                metrics.snapshots = metrics.snapshots[-self._history_size:]
            
            metrics.last_updated = time.time()
            
            logger.debug(f"📊 Recorded {metric_type.value} metric for {strategy_name}: {value}")
    
    def get_strategy_metrics(self, strategy_id: str) -> Optional[StrategyMetrics]:
        """
        Get metrics for a specific strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Strategy metrics or None if not found
        """
        with self._lock:
            return self._strategy_metrics.get(strategy_id)
    
    def get_top_performing_strategies(self, limit: int = 5) -> List[StrategyMetrics]:
        """
        Get top performing strategies by average operation time.
        
        Args:
            limit: Maximum number of strategies to return
            
        Returns:
            List of top performing strategies
        """
        with self._lock:
            strategies = [
                metrics for metrics in self._strategy_metrics.values()
                if metrics.total_operations > 0
            ]
            
            # Sort by average time (lower is better)
            strategies.sort(key=lambda x: x.average_time)
            
            return strategies[:limit]
    
    def get_memory_usage_summary(self) -> Dict[str, Any]:
        """
        Get memory usage summary across all strategies.
        
        Returns:
            Memory usage summary
        """
        with self._lock:
            total_memory = sum(metrics.memory_usage for metrics in self._strategy_metrics.values())
            strategy_count = len(self._strategy_metrics)
            
            return {
                'total_memory_usage': total_memory,
                'average_memory_per_strategy': total_memory / max(strategy_count, 1),
                'strategy_count': strategy_count,
                'memory_by_strategy': {
                    metrics.strategy_name: metrics.memory_usage
                    for metrics in self._strategy_metrics.values()
                }
            }
    
    def get_performance_trends(self, strategy_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance trends for a strategy over time.
        
        Args:
            strategy_id: Strategy identifier
            hours: Number of hours to analyze
            
        Returns:
            Performance trends data
        """
        with self._lock:
            metrics = self._strategy_metrics.get(strategy_id)
            if not metrics:
                return {}
            
            cutoff_time = time.time() - (hours * 3600)
            recent_snapshots = [
                snapshot for snapshot in metrics.snapshots
                if snapshot.timestamp >= cutoff_time
            ]
            
            if not recent_snapshots:
                return {}
            
            # Analyze trends
            performance_snapshots = [
                s for s in recent_snapshots if s.metric_type == MetricType.PERFORMANCE
            ]
            
            if len(performance_snapshots) < 2:
                return {'trend': 'insufficient_data'}
            
            # Calculate trend
            first_half = performance_snapshots[:len(performance_snapshots)//2]
            second_half = performance_snapshots[len(performance_snapshots)//2:]
            
            first_avg = sum(s.value for s in first_half) / len(first_half)
            second_avg = sum(s.value for s in second_half) / len(second_half)
            
            trend_direction = 'improving' if second_avg < first_avg else 'degrading'
            trend_magnitude = abs(second_avg - first_avg) / first_avg if first_avg > 0 else 0
            
            return {
                'trend': trend_direction,
                'magnitude': trend_magnitude,
                'first_half_avg': first_avg,
                'second_half_avg': second_avg,
                'data_points': len(performance_snapshots)
            }
    
    def _get_strategy_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all strategy metrics."""
        with self._lock:
            if not self._strategy_metrics:
                return {}
            
            total_operations = sum(m.total_operations for m in self._strategy_metrics.values())
            total_time = sum(m.total_time for m in self._strategy_metrics.values())
            total_memory = sum(m.memory_usage for m in self._strategy_metrics.values())
            
            return {
                'total_strategies': len(self._strategy_metrics),
                'total_operations': total_operations,
                'total_time': total_time,
                'total_memory': total_memory,
                'average_operation_time': total_time / max(total_operations, 1),
                'strategies': {
                    sid: {
                        'name': metrics.strategy_name,
                        'mode': metrics.mode.name,
                        'operations': metrics.total_operations,
                        'avg_time': metrics.average_time,
                        'memory': metrics.memory_usage,
                        'error_rate': metrics.error_rate,
                        'last_updated': metrics.last_updated
                    }
                    for sid, metrics in self._strategy_metrics.items()
                }
            }
    
    def _generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        with self._lock:
            for strategy_id, metrics in self._strategy_metrics.items():
                # High error rate recommendation
                if metrics.error_rate > 0.05:  # 5%
                    recommendations.append({
                        'strategy_id': strategy_id,
                        'strategy_name': metrics.strategy_name,
                        'type': 'high_error_rate',
                        'severity': 'high',
                        'description': f"High error rate: {metrics.error_rate:.1%}",
                        'recommendation': "Consider switching to a more stable strategy"
                    })
                
                # Slow performance recommendation
                if metrics.average_time > 0.01:  # 10ms
                    recommendations.append({
                        'strategy_id': strategy_id,
                        'strategy_name': metrics.strategy_name,
                        'type': 'slow_performance',
                        'severity': 'medium',
                        'description': f"Slow average operation time: {metrics.average_time:.3f}s",
                        'recommendation': "Consider optimizing or switching strategies"
                    })
                
                # High memory usage recommendation
                if metrics.memory_usage > 100 * 1024 * 1024:  # 100MB
                    recommendations.append({
                        'strategy_id': strategy_id,
                        'strategy_name': metrics.strategy_name,
                        'type': 'high_memory_usage',
                        'severity': 'medium',
                        'description': f"High memory usage: {metrics.memory_usage / 1024 / 1024:.1f}MB",
                        'recommendation': "Consider memory-efficient strategy alternatives"
                    })
        
        return recommendations
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health based on metrics."""
        with self._lock:
            if not self._strategy_metrics:
                return {'status': 'unknown', 'score': 0.0}
            
            # Calculate health score (0-100)
            total_strategies = len(self._strategy_metrics)
            high_error_strategies = sum(1 for m in self._strategy_metrics.values() if m.error_rate > 0.05)
            slow_strategies = sum(1 for m in self._strategy_metrics.values() if m.average_time > 0.01)
            
            error_penalty = (high_error_strategies / total_strategies) * 50
            performance_penalty = (slow_strategies / total_strategies) * 30
            
            health_score = max(0, 100 - error_penalty - performance_penalty)
            
            # Determine status
            if health_score >= 80:
                status = 'excellent'
            elif health_score >= 60:
                status = 'good'
            elif health_score >= 40:
                status = 'fair'
            else:
                status = 'poor'
            
            return {
                'status': status,
                'score': health_score,
                'total_strategies': total_strategies,
                'high_error_strategies': high_error_strategies,
                'slow_strategies': slow_strategies,
                'recommendations_count': len(self._generate_optimization_recommendations())
            }
    
    def export_metrics(self, format: str = 'json') -> Union[Dict[str, Any], str]:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format ('json' or 'summary')
            
        Returns:
            Exported metrics
        """
        metrics = self.collect_comprehensive_metrics()
        
        if format == 'summary':
            return self._format_summary(metrics)
        else:
            return metrics
    
    def _format_summary(self, metrics: Dict[str, Any]) -> str:
        """Format metrics as a human-readable summary."""
        global_metrics = metrics.get('global_metrics', {})
        system_health = metrics.get('system_health', {})
        recommendations = metrics.get('optimization_recommendations', [])
        
        summary = f"""
📊 XWNode Strategy Metrics Summary
{'=' * 50}

🏥 System Health: {system_health.get('status', 'unknown').upper()} ({system_health.get('score', 0):.1f}/100)
📈 Total Strategies: {global_metrics.get('total_strategies', 0)}
⚡ Total Operations: {global_metrics.get('total_operations', 0)}
💾 Memory Usage: {global_metrics.get('total_memory_usage', 0):.2f} MB
⏱️  Avg Operation Time: {global_metrics.get('average_performance', 0):.3f}s

🔧 Optimization Recommendations: {len(recommendations)}
"""
        
        if recommendations:
            summary += "\n📋 Top Recommendations:\n"
            for i, rec in enumerate(recommendations[:3], 1):
                summary += f"  {i}. {rec['strategy_name']}: {rec['description']}\n"
        
        return summary.strip()
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._strategy_metrics.clear()
            self._global_metrics = {
                'total_strategies': 0,
                'total_operations': 0,
                'total_memory_usage': 0.0,
                'average_performance': 0.0,
                'system_uptime': time.time(),
                'last_collection': time.time()
            }
            logger.info("🧹 Cleared all strategy metrics")


# Global metrics collector instance
_metrics_collector: Optional[StrategyMetricsCollector] = None
_metrics_lock = threading.Lock()


def get_metrics_collector() -> StrategyMetricsCollector:
    """
    Get the global metrics collector instance.
    
    Returns:
        Global StrategyMetricsCollector instance
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        with _metrics_lock:
            if _metrics_collector is None:
                _metrics_collector = StrategyMetricsCollector()
                logger.info("📊 Initialized global strategy metrics collector")
    
    return _metrics_collector


def collect_comprehensive_metrics() -> Dict[str, Any]:
    """
    Collect comprehensive metrics using the global collector.
    
    Returns:
        Complete metrics dictionary
    """
    return get_metrics_collector().collect_comprehensive_metrics()


def record_strategy_metric(
    strategy_id: str,
    strategy_name: str,
    mode: Union[NodeMode, EdgeMode],
    metric_type: MetricType,
    value: float,
    **metadata: Any
) -> None:
    """
    Record a strategy metric using the global collector.
    
    Args:
        strategy_id: Strategy identifier
        strategy_name: Strategy name
        mode: Strategy mode
        metric_type: Metric type
        value: Metric value
        **metadata: Additional metadata
    """
    get_metrics_collector().record_strategy_metric(
        strategy_id, strategy_name, mode, metric_type, value, **metadata
    )


def get_metrics_summary() -> str:
    """
    Get a formatted metrics summary.
    
    Returns:
        Human-readable metrics summary
    """
    return get_metrics_collector().export_metrics('summary')


def export_metrics(format: str = 'json') -> Union[Dict[str, Any], str]:
    """
    Export metrics in specified format.
    
    Args:
        format: Export format
        
    Returns:
        Exported metrics
    """
    return get_metrics_collector().export_metrics(format)
