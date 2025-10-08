"""
#exonware/xwnode/src/exonware/xwnode/strategies/manager.py

Enhanced Strategy Manager

This module provides the enhanced StrategyManager class that integrates:
- Flyweight pattern for memory optimization
- Data pattern detection for intelligent strategy selection
- Performance monitoring for optimization recommendations
- Lazy materialization and strategy management

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: 07-Sep-2025
"""

import time
import threading
from typing import Dict, Optional, Any, Union, List
from exonware.xwsystem import get_logger

logger = get_logger(__name__)
from ..types import NodeMode, EdgeMode, NodeTrait, EdgeTrait
from .registry import get_registry
from .advisor import get_advisor
from .migration import get_migrator
from .flyweight import get_flyweight
from .pattern_detector import get_detector, DataProfile
from .performance_monitor import get_monitor, OperationType
from ..errors import (
    XWNodeStrategyError, XWNodeError, 
    XWNodeStrategyError, XWNodeUnsupportedCapabilityError
)



class StrategyManager:
    """
    Enhanced strategy manager with integrated optimization components.
    
    This class handles:
    - Lazy materialization of strategies with flyweight optimization
    - Intelligent pattern detection for AUTO mode selection
    - Performance monitoring and optimization recommendations
    - Strategy migration and validation
    - Memory-efficient strategy management
    """
    
    def __init__(self, 
                 node_mode: NodeMode = NodeMode.AUTO,
                 edge_mode: EdgeMode = EdgeMode.AUTO,
                 node_traits: NodeTrait = NodeTrait.NONE,
                 edge_traits: EdgeTrait = EdgeTrait.NONE,
                 **options):
        """Initialize the enhanced strategy manager."""
        self._node_mode_requested = node_mode
        self._edge_mode_requested = edge_mode
        self._node_traits = node_traits
        self._edge_traits = edge_traits
        self._options = options
        
        # Lazy materialization state
        self._node_strategy = None
        self._edge_strategy = None
        self._node_locked = False
        self._edge_locked = False
        
        # Performance tracking
        self._node_metrics = {"operations": 0, "last_migration": None}
        self._edge_metrics = {"operations": 0, "last_migration": None}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Get global instances
        self._registry = get_registry()
        self._advisor = get_advisor()
        self._migrator = get_migrator()
        
        # Enhanced components
        self._flyweight = get_flyweight()
        self._detector = get_detector()
        self._monitor = get_monitor()
        
        # Strategy IDs for monitoring
        self._node_strategy_id = f"node_{id(self)}"
        self._edge_strategy_id = f"edge_{id(self)}"
        
        edge_name = edge_mode.name if edge_mode is not None else "None"
        logger.debug(f"🔧 Enhanced StrategyManager initialized: node={node_mode.name}, edge={edge_name}")
    
    def _materialize_node_strategy(self) -> None:
        """Lazily materialize the node strategy with enhanced optimization."""
        if self._node_strategy is not None:
            return
        
        with self._lock:
            if self._node_strategy is not None:  # Double-check
                return
            
            start_time = time.time()
            
            # Determine actual mode (AUTO or explicit)
            if self._node_mode_requested == NodeMode.AUTO:
                actual_mode = self._select_node_mode_enhanced()
            else:
                actual_mode = self._node_mode_requested
            
            # Create strategy instance using flyweight pattern
            try:
                strategy_class = self._registry.get_node_strategy_class(actual_mode)
                self._node_strategy = self._flyweight.get_node_strategy(
                    strategy_class,
                    mode=actual_mode,
                    traits=self._node_traits,
                    **self._options
                )
                self._node_locked = True
                
                # Record strategy creation
                creation_time = time.time() - start_time
                self._monitor.record_operation(
                    self._node_strategy_id,
                    OperationType.CREATE,
                    creation_time,
                    error=False
                )
                
                logger.info(f"🎯 Materialized node strategy: {actual_mode.name} (flyweight optimized)")
                
            except XWNodeStrategyError as e:
                logger.error(f"❌ Requested node strategy '{actual_mode.name}' is not available")
                self._monitor.record_operation(
                    self._node_strategy_id,
                    OperationType.CREATE,
                    time.time() - start_time,
                    error=True
                )
                raise XWNodeError(
                    message=f"Requested node strategy '{actual_mode.name}' is not available. "
                           f"Available strategies: {', '.join([mode.name for mode in self._registry.list_node_modes()])}",
                    cause=e
                )
            except Exception as e:
                logger.error(f"❌ Failed to materialize node strategy {actual_mode.name}: {e}")
                self._monitor.record_operation(
                    self._node_strategy_id,
                    OperationType.CREATE,
                    time.time() - start_time,
                    error=True
                )
                raise XWNodeError(message=f"Failed to materialize strategy '{actual_mode.name}': {e}", cause=e)
    
    def _materialize_edge_strategy(self) -> None:
        """Lazily materialize the edge strategy."""
        if self._edge_strategy is not None:
            return
        
        # If edge mode is None (disabled for DATA_INTERCHANGE_OPTIMIZED), skip materialization
        if self._edge_mode_requested is None:
            logger.debug("🚫 Edge strategy disabled (None mode)")
            return
        
        with self._lock:
            if self._edge_strategy is not None:  # Double-check
                return
            
            # Determine actual mode (AUTO or explicit)
            if self._edge_mode_requested == EdgeMode.AUTO:
                actual_mode = self._select_edge_mode()
            else:
                actual_mode = self._edge_mode_requested
            
            # Create strategy instance - no fallbacks allowed
            try:
                self._edge_strategy = self._registry.get_edge_strategy(
                    actual_mode,
                    traits=self._edge_traits,
                    **self._options
                )
                self._edge_locked = True
                
                logger.info(f"🎯 Materialized edge strategy: {actual_mode.name}")
                
            except XWNodeStrategyError as e:
                logger.error(f"❌ Requested edge strategy '{actual_mode.name}' is not available")
                raise XWNodeError(
                    message=f"Requested edge strategy '{actual_mode.name}' is not available. "
                           f"Available strategies: {', '.join([mode.name for mode in self._registry.list_edge_modes()])}",
                    cause=e
                )
            except Exception as e:
                logger.error(f"❌ Failed to materialize edge strategy {actual_mode.name}: {e}")
                raise XWNodeError(message=f"Failed to materialize edge strategy '{actual_mode.name}': {e}", cause=e)
    
    def _select_node_mode_enhanced(self) -> NodeMode:
        """
        Enhanced node mode selection using pattern detection.
        
        Returns:
            Optimal node mode based on data analysis
        """
        # Analyze data if available
        initial_data = self._options.get('initial_data')
        if initial_data is not None:
            try:
                # Create data profile
                profile = self._detector.analyze_data(initial_data, **self._options)
                
                # Get recommendation
                recommendation = self._detector.recommend_node_strategy(profile, **self._options)
                
                logger.debug(f"🤖 Pattern-based recommendation: {recommendation.mode.name} "
                           f"(confidence: {recommendation.confidence:.2f})")
                
                return recommendation.mode
                
            except Exception as e:
                logger.warning(f"⚠️ Pattern detection failed, falling back to heuristic selection: {e}")
        
        # Fallback to original heuristic selection
        return self._select_node_mode()
    
    def _select_node_mode(self) -> NodeMode:
        """Select optimal node mode using advisor heuristics."""
        # Quick data type-based selection for common cases
        is_dict = self._options.get('is_dict', False)
        is_list = self._options.get('is_list', False)
        has_numeric_indices = self._options.get('has_numeric_indices', False)
        is_string_keys = self._options.get('is_string_keys', False)
        initial_size = self._options.get('initial_size', 0)
        initial_data = self._options.get('initial_data')
        
        # Check if this is a leaf/primitive value that will use "value" key
        # These should use TREE_GRAPH_HYBRID to maintain backward compatibility
        # But fall back to HASH_MAP if TREE_GRAPH_HYBRID is not available
        if ((initial_data is not None and not isinstance(initial_data, (dict, list))) or
            (initial_data is None)) and not is_dict and not is_list:
            # Use TREE_GRAPH_HYBRID for XWNode compatibility
            from .impls.node_tree_graph_hybrid import TreeGraphHybridStrategy
            return NodeMode.TREE_GRAPH_HYBRID
        
        # Fast path for simple data type patterns
        if is_list or has_numeric_indices:
            # Data that looks like a list/array
            if initial_size < 100:
                return NodeMode.ARRAY_LIST
            else:
                return NodeMode.ARRAY_LIST  # Could be enhanced with other list strategies later
        elif is_dict and is_string_keys:
            # String-keyed dictionary - check for prefix patterns
            keys = list(self._options.get('initial_data', {}).keys()) if 'initial_data' in self._options else []
            if len(keys) > 3 and any(key.startswith(other) for key in keys for other in keys if key != other):
                return NodeMode.TRIE  # Looks like prefix-heavy data
            else:
                return NodeMode.HASH_MAP  # Regular dictionary
        elif is_dict:
            # Non-string keys or mixed keys
            return NodeMode.HASH_MAP
        
        # Build data profile for advisor for complex cases
        data_profile = {
            'size': self._options.get('size', initial_size),
            'operations': self._node_metrics.get('operations', {}),
            'persistent': self._options.get('persistent', False),
            'write_heavy': self._options.get('write_heavy', False),
            'connectivity': self._options.get('connectivity', False),
            'streaming': self._options.get('streaming', False),
            'frequency': self._options.get('frequency', False),
            'binary': self._options.get('binary', False),
            'updates': self._options.get('updates', False),
        }
        
        # Get recommendation from advisor
        recommendation = self._advisor.suggest_node_strategy(data_profile)
        
        logger.debug(f"🤖 Node mode recommendation: {recommendation.mode.name} "
                    f"({recommendation.estimated_gain_percent:.1f}% gain)")
        
        return recommendation.mode
    
    def _select_edge_mode(self) -> EdgeMode:
        """Select optimal edge mode using advisor heuristics."""
        # Build graph profile for advisor
        graph_profile = {
            'vertices': self._options.get('vertices', 0),
            'edges': self._options.get('edges', 0),
            'spatial': self._options.get('spatial', False),
            'temporal': self._options.get('temporal', False),
            'hyper': self._options.get('hyper', False),
            'undirected': self._options.get('undirected', False),
            'high_churn': self._options.get('high_churn', False),
            'dimensions': self._options.get('dimensions', 2),
        }
        
        # Get recommendation from advisor
        recommendation = self._advisor.suggest_edge_strategy(graph_profile)
        
        logger.debug(f"🤖 Edge mode recommendation: {recommendation.mode.name} "
                    f"({recommendation.estimated_gain_percent:.1f}% gain)")
        
        return recommendation.mode
    
    def get_node_strategy(self) -> Any:
        """Get the node strategy instance (materializes if needed)."""
        self._materialize_node_strategy()
        return self._node_strategy
    
    def get_edge_strategy(self) -> Any:
        """Get the edge strategy instance (materializes if needed)."""
        if self._edge_mode_requested is None:
            return None  # Edge strategy disabled
        self._materialize_edge_strategy()
        return self._edge_strategy
    
    def rebuild_node_strategy(self, mode: NodeMode, *, allow_loss: bool = False) -> 'StrategyManager':
        """
        Rebuild node strategy with new mode.
        
        Args:
            mode: New node mode
            allow_loss: Whether to allow data loss during migration
            
        Returns:
            Self for chaining
            
        Raises:
            IllegalMigrationError: If migration is not allowed
        """
        with self._lock:
            if self._node_locked and not allow_loss:
                # Check if migration would cause data loss
                current_mode = self._get_current_node_mode()
                if current_mode and self._would_lose_data(current_mode, mode, is_node=True):
                    raise XWNodeStrategyError(
                        current_mode.name, mode.name,
                        "Migration would cause data loss. Use allow_loss=True to override."
                    )
            
            # Save data from current strategy before rebuilding
            old_data = None
            if self._node_strategy is not None:
                try:
                    old_data = self._node_strategy.to_native()
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract data during migration: {e}")
            
            # Rebuild strategy
            self._node_strategy = None
            self._node_locked = False
            self._node_mode_requested = mode
            
            # Materialize new strategy
            self._materialize_node_strategy()
            
            # Restore data to new strategy
            if old_data is not None and self._node_strategy is not None:
                try:
                    if isinstance(old_data, dict):
                        for key, value in old_data.items():
                            self._node_strategy.put(key, value)
                    elif isinstance(old_data, list):
                        for i, value in enumerate(old_data):
                            self._node_strategy.put(str(i), value)
                    else:
                        # For leaf nodes, store as value
                        self._node_strategy.put("value", old_data)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to restore data during migration: {e}")
            
            # Update metrics
            self._node_metrics["last_migration"] = time.time()
            
            logger.info(f"🔄 Rebuilt node strategy to {mode.name}")
            return self
    
    def rebuild_edge_strategy(self, mode: EdgeMode, *, allow_loss: bool = False) -> 'StrategyManager':
        """
        Rebuild edge strategy with new mode.
        
        Args:
            mode: New edge mode
            allow_loss: Whether to allow data loss during migration
            
        Returns:
            Self for chaining
            
        Raises:
            IllegalMigrationError: If migration is not allowed
        """
        with self._lock:
            if self._edge_locked and not allow_loss:
                # Check if migration would cause data loss
                current_mode = self._get_current_edge_mode()
                if current_mode and self._would_lose_data(current_mode, mode, is_node=False):
                    raise XWNodeStrategyError(
                        current_mode.name, mode.name,
                        "Migration would cause data loss. Use allow_loss=True to override."
                    )
            
            # Rebuild strategy
            self._edge_strategy = None
            self._edge_locked = False
            self._edge_mode_requested = mode
            
            # Materialize new strategy
            self._materialize_edge_strategy()
            
            # Update metrics
            self._edge_metrics["last_migration"] = time.time()
            
            logger.info(f"🔄 Rebuilt edge strategy to {mode.name}")
            return self
    
    def _get_current_node_mode(self) -> Optional[NodeMode]:
        """Get current node mode if materialized."""
        if self._node_strategy is None:
            return None
        
        # Try to get mode from strategy
        try:
            return self._node_strategy.mode
        except AttributeError:
            return self._node_mode_requested
    
    def _get_current_edge_mode(self) -> Optional[EdgeMode]:
        """Get current edge mode if materialized."""
        if self._edge_strategy is None:
            return None
        
        # Try to get mode from strategy
        try:
            return self._edge_strategy.mode
        except AttributeError:
            return self._edge_mode_requested
    
    def _would_lose_data(self, from_mode: Union[NodeMode, EdgeMode], 
                        to_mode: Union[NodeMode, EdgeMode], is_node: bool) -> bool:
        """Check if migration would cause data loss."""
        # Get recommendation to assess data loss risk
        if is_node:
            recommendation = self._advisor.suggest_node_strategy({}, from_mode)
        else:
            recommendation = self._advisor.suggest_edge_strategy({}, from_mode)
        
        return recommendation.data_loss_risk
    
    def record_operation(self, operation: str, duration: float, 
                        memory_usage: float = 0.0, is_node: bool = True) -> None:
        """Record operation for performance monitoring."""
        strategy_id = f"{self._get_current_node_mode().name if is_node else self._get_current_edge_mode().name}"
        
        # Record with enhanced monitor
        operation_type = OperationType(operation.lower()) if hasattr(OperationType, operation.upper()) else OperationType.GET
        monitor_id = self._node_strategy_id if is_node else self._edge_strategy_id
        
        self._monitor.record_operation(
            strategy_id=monitor_id,
            operation=operation_type,
            duration=duration,
            memory_usage=memory_usage,
            error=False
        )
        
        # Also record with advisor for backward compatibility
        self._advisor.record_operation(
            strategy_id=strategy_id,
            operation=operation,
            duration=duration,
            memory_usage=memory_usage,
            is_node=is_node
        )
        
        # Update local metrics
        if is_node:
            self._node_metrics["operations"] += 1
        else:
            self._edge_metrics["operations"] += 1
    
    def get_performance_profile(self, is_node: bool = True) -> Dict[str, Any]:
        """Get performance profile for current strategy."""
        strategy_id = f"{self._get_current_node_mode().name if is_node else self._get_current_edge_mode().name}"
        return self._advisor.get_performance_profile(strategy_id, is_node)
    
    def get_enhanced_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary with all metrics."""
        return {
            'flyweight_stats': self._flyweight.get_stats(),
            'monitor_summary': self._monitor.get_performance_summary(),
            'detector_stats': self._detector.get_stats(),
            'strategy_info': self.get_strategy_info()
        }
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations for current strategies."""
        recommendations = {}
        
        # Get node strategy recommendations
        if self._node_strategy is not None:
            node_recommendations = self._monitor.generate_recommendations(self._node_strategy_id)
            recommendations['node'] = [
                {
                    'type': rec.recommendation_type,
                    'confidence': rec.confidence,
                    'reasoning': rec.reasoning,
                    'estimated_improvement': rec.estimated_improvement,
                    'alternative': rec.alternative_strategy
                }
                for rec in node_recommendations
            ]
        
        # Get edge strategy recommendations
        if self._edge_strategy is not None:
            edge_recommendations = self._monitor.generate_recommendations(self._edge_strategy_id)
            recommendations['edge'] = [
                {
                    'type': rec.recommendation_type,
                    'confidence': rec.confidence,
                    'reasoning': rec.reasoning,
                    'estimated_improvement': rec.estimated_improvement,
                    'alternative': rec.alternative_strategy
                }
                for rec in edge_recommendations
            ]
        
        return recommendations
    
    def analyze_data_patterns(self, data: Any, **context: Any) -> DataProfile:
        """Analyze data patterns for strategy optimization."""
        return self._detector.analyze_data(data, **context)
    
    def get_flyweight_stats(self) -> Dict[str, Any]:
        """Get flyweight pattern statistics."""
        return self._flyweight.get_stats()
    
    def clear_flyweight_cache(self) -> None:
        """Clear flyweight cache to free memory."""
        self._flyweight.clear_cache()
        logger.info("🧹 Cleared flyweight cache")
    
    def get_monitor_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operation history from monitor."""
        return self._monitor.get_operation_history(limit)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get comprehensive strategy information."""
        with self._lock:
            return {
                "node": {
                    "requested_mode": self._node_mode_requested.name,
                    "current_mode": self._get_current_node_mode().name if self._node_strategy else None,
                    "materialized": self._node_strategy is not None,
                    "locked": self._node_locked,
                    "traits": str(self._node_traits),
                    "metrics": self._node_metrics.copy(),
                    "performance": self.get_performance_profile(is_node=True) if self._node_strategy else None
                },
                "edge": {
                    "requested_mode": self._edge_mode_requested.name,
                    "current_mode": self._get_current_edge_mode().name if self._edge_strategy else None,
                    "materialized": self._edge_strategy is not None,
                    "locked": self._edge_locked,
                    "traits": str(self._edge_traits),
                    "metrics": self._edge_metrics.copy(),
                    "performance": self.get_performance_profile(is_node=False) if self._edge_strategy else None
                },
                "options": self._options.copy()
            }
    
    def check_capability(self, capability: Union[NodeTrait, EdgeTrait], is_node: bool = True) -> bool:
        """Check if current strategy supports a capability."""
        if is_node:
            return capability in self._node_traits
        else:
            return capability in self._edge_traits
    
    def require_capability(self, capability: Union[NodeTrait, EdgeTrait], is_node: bool = True) -> None:
        """Require a capability, raising error if not supported."""
        if not self.check_capability(capability, is_node):
            current_mode = self._get_current_node_mode() if is_node else self._get_current_edge_mode()
            current_traits = self._node_traits if is_node else self._edge_traits
            
            raise XWNodeUnsupportedCapabilityError(
                capability=str(capability),
                strategy=current_mode.name if current_mode else "unmaterialized",
                available_capabilities=[str(trait) for trait in current_traits]
            )
    
    # ============================================================================
    # STRATEGY MIGRATION
    # ============================================================================
    
    def migrate_node_strategy(self, target_mode: NodeMode, 
                             target_traits: NodeTrait = NodeTrait.NONE,
                             **options) -> None:
        """Migrate the current node strategy to a new mode."""
        with self._lock:
            if self._node_strategy is None:
                # No current strategy, just update the requested mode
                self._node_mode_requested = target_mode
                self._node_traits = target_traits
                return
            
            logger.info(f"🔄 Migrating node strategy: {self._get_current_node_mode().name} → {target_mode.name}")
            
            # Use migrator to perform the migration
            new_strategy = self._migrator.execute_node_migration(
                self._node_strategy, target_mode, target_traits, **options
            )
            
            # Update manager state
            self._node_strategy = new_strategy
            self._node_mode_requested = target_mode
            self._node_traits = target_traits
            
            logger.info(f"✅ Node strategy migration completed")
    
    def migrate_edge_strategy(self, target_mode: EdgeMode,
                             target_traits: EdgeTrait = EdgeTrait.NONE,
                             **options) -> None:
        """Migrate the current edge strategy to a new mode."""
        with self._lock:
            if self._edge_strategy is None:
                # No current strategy, just update the requested mode
                self._edge_mode_requested = target_mode
                self._edge_traits = target_traits
                return
            
            logger.info(f"🔄 Migrating edge strategy: {self._get_current_edge_mode().name} → {target_mode.name}")
            
            # Use migrator to perform the migration
            new_strategy = self._migrator.execute_edge_migration(
                self._edge_strategy, target_mode, target_traits, **options
            )
            
            # Update manager state
            self._edge_strategy = new_strategy
            self._edge_mode_requested = target_mode
            self._edge_traits = target_traits
            
            logger.info(f"✅ Edge strategy migration completed")
    
    def plan_node_migration(self, target_mode: NodeMode,
                           target_traits: NodeTrait = NodeTrait.NONE) -> Any:
        """Plan a migration for the current node strategy."""
        current_mode = self._get_current_node_mode()
        current_traits = self._node_traits
        data_size = len(self._node_strategy) if self._node_strategy else 0
        
        return self._migrator.plan_node_migration(
            current_mode, target_mode, current_traits, target_traits, data_size
        )
    
    def plan_edge_migration(self, target_mode: EdgeMode,
                           target_traits: EdgeTrait = EdgeTrait.NONE) -> Any:
        """Plan a migration for the current edge strategy."""
        current_mode = self._get_current_edge_mode()
        current_traits = self._edge_traits
        edge_count = len(self._edge_strategy) if self._edge_strategy else 0
        vertex_count = self._edge_strategy.vertex_count() if self._edge_strategy else 0
        
        return self._migrator.plan_edge_migration(
            current_mode, target_mode, current_traits, target_traits, edge_count, vertex_count
        )
    
    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get basic performance report for this strategy manager."""
        node_mode = self._get_current_node_mode()
        edge_mode = self._get_current_edge_mode()
        
        return {
            'current_node_strategy': node_mode.name if node_mode else "unknown",
            'current_edge_strategy': edge_mode.name if edge_mode else "unknown",
            'node_strategy_active': self._node_strategy is not None,
            'edge_strategy_active': self._edge_strategy is not None
        }
    
    def copy(self) -> 'StrategyManager':
        """Create a deep copy of this strategy manager."""
        new_manager = StrategyManager(
            node_mode=self._node_mode_requested,
            edge_mode=self._edge_mode_requested,
            node_traits=self._node_traits,
            edge_traits=self._edge_traits,
            **self._options
        )
        
        # Copy the materialized strategies if they exist
        if self._node_strategy is not None:
            new_manager._node_strategy = self._node_strategy
            new_manager._node_locked = True
        
        if self._edge_strategy is not None:
            new_manager._edge_strategy = self._edge_strategy
            new_manager._edge_locked = True
        
        return new_manager
    
    def create_node_strategy(self, data: Any) -> Any:
        """Create a node strategy from data and return the internal representation."""
        self._materialize_node_strategy()
        
        if self._node_strategy is not None:
            return self._node_strategy.create_from_data(data)
        else:
            # This should never happen if _materialize_node_strategy() worked correctly
            raise XWNodeError(
                message="Node strategy materialization failed but no exception was raised"
            )
    
    def create_reference_strategy(self, uri: str, reference_type: str = "generic", metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Create a reference strategy."""
        self._materialize_node_strategy()
        
        if self._node_strategy is not None:
            # Use the strategy's reference creation method if available
            if hasattr(self._node_strategy, 'create_reference'):
                return self._node_strategy.create_reference(uri, reference_type, metadata or {})
            else:
                # Create a reference using the strategy's factory
                reference_data = {
                    'uri': uri,
                    'reference_type': reference_type,
                    'metadata': metadata or {},
                    '_type': 'reference'
                }
                return self._node_strategy.create_from_data(reference_data)
        else:
            # This should never happen if _materialize_node_strategy() worked correctly
            raise XWNodeError(
                message="Node strategy materialization failed but no exception was raised"
            )
    
    def create_object_strategy(self, uri: str, object_type: str, mime_type: Optional[str] = None, size: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Create an object strategy."""
        self._materialize_node_strategy()
        
        if self._node_strategy is not None:
            # Use the strategy's object creation method if available
            if hasattr(self._node_strategy, 'create_object'):
                return self._node_strategy.create_object(uri, object_type, mime_type, size, metadata or {})
            else:
                # Create an object using the strategy's factory
                object_data = {
                    'uri': uri,
                    'object_type': object_type,
                    'mime_type': mime_type,
                    'size': size,
                    'metadata': metadata or {},
                    '_type': 'object'
                }
                return self._node_strategy.create_from_data(object_data)
        else:
            # This should never happen if _materialize_node_strategy() worked correctly
            raise XWNodeError(
                message="Node strategy materialization failed but no exception was raised"
            )
    
    def create_edge_strategy(self) -> Any:
        """Create an edge strategy."""
        self._materialize_edge_strategy()
        
        if self._edge_strategy is not None:
            return self._edge_strategy
        else:
            # This should never happen if _materialize_edge_strategy() worked correctly
            raise XWNodeError(
                message="Edge strategy materialization failed but no exception was raised"
            )
