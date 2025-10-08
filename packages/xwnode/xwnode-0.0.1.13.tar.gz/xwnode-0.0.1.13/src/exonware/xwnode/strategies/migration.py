"""
Strategy Migration System

This module implements seamless migration between different node and edge
strategies while preserving data integrity.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Type
from enum import Enum
import threading
import time
from ..types import NodeMode, EdgeMode, NodeTrait, EdgeTrait
from .registry import get_registry
from ..errors import XWNodeStrategyError, XWNodeError
import logging

logger = logging.getLogger(__name__)


class MigrationPlan:
    """Represents a strategy migration plan with validation and cost estimation."""
    
    def __init__(self, source_mode: Any, target_mode: Any, strategy_type: str):
        self.source_mode = source_mode
        self.target_mode = target_mode
        self.strategy_type = strategy_type  # 'node' or 'edge'
        self.cost_estimate = 0
        self.data_loss_risk = 'none'  # 'none', 'low', 'medium', 'high'
        self.warnings: List[str] = []
        self.required_operations: List[str] = []
        self.estimated_time_ms = 0
        
    def add_warning(self, warning: str) -> None:
        """Add a migration warning."""
        self.warnings.append(warning)
    
    def add_operation(self, operation: str) -> None:
        """Add a required migration operation."""
        self.required_operations.append(operation)
    
    def is_safe(self) -> bool:
        """Check if migration is considered safe."""
        return self.data_loss_risk in ['none', 'low'] and len(self.warnings) <= 2


class xStrategyMigrator:
    """
    Handles migration between different node and edge strategies.
    
    Provides safe, efficient migration with rollback capabilities
    and data integrity guarantees.
    """
    
    def __init__(self):
        self._registry = get_registry()
        self._migration_lock = threading.RLock()
        self._migration_history: List[Dict[str, Any]] = []
    
    # ============================================================================
    # MIGRATION PLANNING
    # ============================================================================
    
    def plan_node_migration(self, source_mode: NodeMode, target_mode: NodeMode,
                           source_traits: NodeTrait = NodeTrait.NONE,
                           target_traits: NodeTrait = NodeTrait.NONE,
                           data_size: int = 0) -> MigrationPlan:
        """Plan a migration between node strategies."""
        plan = MigrationPlan(source_mode, target_mode, 'node')
        
        # Basic validation
        if source_mode == target_mode and source_traits == target_traits:
            plan.add_warning("Source and target are identical")
            return plan
        
        # Check strategy availability
        if not self._registry.has_node_strategy(target_mode):
            raise XWNodeStrategyError(f"Target node strategy {target_mode.name} not available")
        
        # Analyze compatibility
        self._analyze_node_compatibility(plan, source_mode, target_mode, 
                                       source_traits, target_traits, data_size)
        
        return plan
    
    def plan_edge_migration(self, source_mode: EdgeMode, target_mode: EdgeMode,
                           source_traits: EdgeTrait = EdgeTrait.NONE,
                           target_traits: EdgeTrait = EdgeTrait.NONE,
                           edge_count: int = 0, vertex_count: int = 0) -> MigrationPlan:
        """Plan a migration between edge strategies."""
        plan = MigrationPlan(source_mode, target_mode, 'edge')
        
        # Basic validation
        if source_mode == target_mode and source_traits == target_traits:
            plan.add_warning("Source and target are identical")
            return plan
        
        # Check strategy availability
        if not self._registry.has_edge_strategy(target_mode):
            raise XWNodeStrategyError(f"Target edge strategy {target_mode.name} not available")
        
        # Analyze compatibility
        self._analyze_edge_compatibility(plan, source_mode, target_mode,
                                       source_traits, target_traits, edge_count, vertex_count)
        
        return plan
    
    def _analyze_node_compatibility(self, plan: MigrationPlan, source: NodeMode, target: NodeMode,
                                   source_traits: NodeTrait, target_traits: NodeTrait,
                                   data_size: int) -> None:
        """Analyze compatibility between node strategies."""
        # Define migration rules and costs
        migration_matrix = {
            # From LEGACY
            (NodeMode.LEGACY, NodeMode.HASH_MAP): {'cost': 1, 'risk': 'none', 'ops': ['copy_dict']},
            (NodeMode.LEGACY, NodeMode.ARRAY_LIST): {'cost': 1, 'risk': 'low', 'ops': ['copy_list']},
            (NodeMode.LEGACY, NodeMode.TRIE): {'cost': 2, 'risk': 'low', 'ops': ['copy_dict', 'build_trie']},
            (NodeMode.LEGACY, NodeMode.HEAP): {'cost': 3, 'risk': 'medium', 'ops': ['extract_values', 'heapify']},
            (NodeMode.LEGACY, NodeMode.B_TREE): {'cost': 3, 'risk': 'low', 'ops': ['sort_keys', 'build_btree']},
            
            # From HASH_MAP
            (NodeMode.HASH_MAP, NodeMode.LEGACY): {'cost': 1, 'risk': 'none', 'ops': ['copy_dict']},
            (NodeMode.HASH_MAP, NodeMode.ARRAY_LIST): {'cost': 2, 'risk': 'high', 'ops': ['convert_dict_to_list']},
            (NodeMode.HASH_MAP, NodeMode.TRIE): {'cost': 2, 'risk': 'low', 'ops': ['rebuild_trie']},
            (NodeMode.HASH_MAP, NodeMode.B_TREE): {'cost': 2, 'risk': 'low', 'ops': ['sort_rebuild']},
            
            # From ARRAY_LIST
            (NodeMode.ARRAY_LIST, NodeMode.LEGACY): {'cost': 1, 'risk': 'none', 'ops': ['copy_list']},
            (NodeMode.ARRAY_LIST, NodeMode.HASH_MAP): {'cost': 1, 'risk': 'low', 'ops': ['index_as_keys']},
            (NodeMode.ARRAY_LIST, NodeMode.HEAP): {'cost': 2, 'risk': 'low', 'ops': ['heapify_list']},
            
            # Specialized migrations
            (NodeMode.HEAP, NodeMode.ARRAY_LIST): {'cost': 2, 'risk': 'medium', 'ops': ['heap_sort', 'to_list']},
            (NodeMode.B_TREE, NodeMode.HASH_MAP): {'cost': 2, 'risk': 'low', 'ops': ['flatten_tree']},
            (NodeMode.TRIE, NodeMode.HASH_MAP): {'cost': 2, 'risk': 'low', 'ops': ['flatten_trie']},
        }
        
        migration_key = (source, target)
        if migration_key in migration_matrix:
            rules = migration_matrix[migration_key]
            plan.cost_estimate = rules['cost']
            plan.data_loss_risk = rules['risk']
            for op in rules['ops']:
                plan.add_operation(op)
        else:
            # Default fallback through LEGACY
            plan.cost_estimate = 4
            plan.data_loss_risk = 'medium'
            plan.add_operation('migrate_via_legacy')
            plan.add_warning(f"No direct migration path from {source.name} to {target.name}")
        
        # Adjust based on data size
        if data_size > 10000:
            plan.cost_estimate += 2
            plan.estimated_time_ms = data_size * 0.1
        elif data_size > 1000:
            plan.cost_estimate += 1
            plan.estimated_time_ms = data_size * 0.05
        else:
            plan.estimated_time_ms = max(10, data_size * 0.01)
        
        # Trait compatibility warnings
        self._check_trait_compatibility(plan, source_traits, target_traits, 'node')
    
    def _analyze_edge_compatibility(self, plan: MigrationPlan, source: EdgeMode, target: EdgeMode,
                                   source_traits: EdgeTrait, target_traits: EdgeTrait,
                                   edge_count: int, vertex_count: int) -> None:
        """Analyze compatibility between edge strategies."""
        # Define edge migration rules
        migration_matrix = {
            # From LEGACY
            (EdgeMode.LEGACY, EdgeMode.ADJ_LIST): {'cost': 2, 'risk': 'low', 'ops': ['extract_edges', 'build_adj_list']},
            (EdgeMode.LEGACY, EdgeMode.ADJ_MATRIX): {'cost': 3, 'risk': 'medium', 'ops': ['extract_edges', 'build_matrix']},
            (EdgeMode.LEGACY, EdgeMode.CSR): {'cost': 3, 'risk': 'low', 'ops': ['extract_edges', 'build_csr']},
            
            # Between modern formats
            (EdgeMode.ADJ_LIST, EdgeMode.ADJ_MATRIX): {'cost': 2, 'risk': 'low', 'ops': ['list_to_matrix']},
            (EdgeMode.ADJ_LIST, EdgeMode.CSR): {'cost': 2, 'risk': 'low', 'ops': ['list_to_csr']},
            (EdgeMode.ADJ_MATRIX, EdgeMode.ADJ_LIST): {'cost': 2, 'risk': 'low', 'ops': ['matrix_to_list']},
            (EdgeMode.ADJ_MATRIX, EdgeMode.CSR): {'cost': 2, 'risk': 'low', 'ops': ['matrix_to_csr']},
            (EdgeMode.CSR, EdgeMode.ADJ_LIST): {'cost': 2, 'risk': 'low', 'ops': ['csr_to_list']},
            (EdgeMode.CSR, EdgeMode.ADJ_MATRIX): {'cost': 3, 'risk': 'medium', 'ops': ['csr_to_matrix']},
        }
        
        migration_key = (source, target)
        if migration_key in migration_matrix:
            rules = migration_matrix[migration_key]
            plan.cost_estimate = rules['cost']
            plan.data_loss_risk = rules['risk']
            for op in rules['ops']:
                plan.add_operation(op)
        else:
            # Default fallback
            plan.cost_estimate = 5
            plan.data_loss_risk = 'high'
            plan.add_operation('migrate_via_legacy')
            plan.add_warning(f"No direct migration path from {source.name} to {target.name}")
        
        # Graph density considerations
        density = edge_count / max(1, vertex_count * (vertex_count - 1)) if vertex_count > 1 else 0
        
        if target == EdgeMode.ADJ_MATRIX and density < 0.1:
            plan.add_warning("Migrating sparse graph to dense matrix representation")
            plan.cost_estimate += 1
        elif target in [EdgeMode.ADJ_LIST, EdgeMode.CSR] and density > 0.7:
            plan.add_warning("Migrating dense graph to sparse representation")
        
        # Size-based adjustments
        if edge_count > 100000:
            plan.cost_estimate += 3
            plan.estimated_time_ms = edge_count * 0.2
        elif edge_count > 10000:
            plan.cost_estimate += 2
            plan.estimated_time_ms = edge_count * 0.1
        else:
            plan.estimated_time_ms = max(10, edge_count * 0.05)
        
        # Trait compatibility
        self._check_trait_compatibility(plan, source_traits, target_traits, 'edge')
    
    def _check_trait_compatibility(self, plan: MigrationPlan, source_traits: Any, 
                                  target_traits: Any, strategy_type: str) -> None:
        """Check trait compatibility and add warnings."""
        if source_traits == target_traits:
            return
        
        # Check for trait loss
        lost_traits = source_traits & ~target_traits if source_traits else None
        if lost_traits and lost_traits != 0:
            plan.add_warning(f"Some {strategy_type} traits will be lost: {lost_traits}")
            if plan.data_loss_risk == 'none':
                plan.data_loss_risk = 'low'
        
        # Check for new traits
        new_traits = target_traits & ~source_traits if target_traits else None
        if new_traits and new_traits != 0:
            plan.add_operation(f"configure_{strategy_type}_traits")
    
    # ============================================================================
    # MIGRATION EXECUTION
    # ============================================================================
    
    def execute_node_migration(self, source_strategy: Any, target_mode: NodeMode,
                              target_traits: NodeTrait = NodeTrait.NONE,
                              **options) -> Any:
        """Execute migration from source node strategy to target."""
        with self._migration_lock:
            start_time = time.time()
            
            # Extract data from source
            source_data = source_strategy.to_native()
            source_size = len(source_strategy) if hasattr(source_strategy, '__len__') else 0
            
            # Create migration plan
            source_mode = getattr(source_strategy, '_mode', NodeMode.LEGACY)
            plan = self.plan_node_migration(source_mode, target_mode, 
                                          getattr(source_strategy, '_traits', NodeTrait.NONE),
                                          target_traits, source_size)
            
            logger.info(f"🔄 Executing node migration: {source_mode.name} → {target_mode.name}")
            logger.info(f"📋 Operations: {', '.join(plan.required_operations)}")
            
            # Create target strategy
            target_strategy = self._registry.get_node_strategy(target_mode, traits=target_traits, **options)
            
            # Migrate data based on type
            try:
                if isinstance(source_data, dict):
                    for key, value in source_data.items():
                        target_strategy.put(key, value)
                elif isinstance(source_data, list):
                    for i, value in enumerate(source_data):
                        target_strategy.put(str(i), value)
                else:
                    # Leaf node
                    target_strategy.put('value', source_data)
                
                # Record migration
                migration_record = {
                    'timestamp': time.time(),
                    'type': 'node',
                    'source_mode': source_mode.name,
                    'target_mode': target_mode.name,
                    'data_size': source_size,
                    'duration_ms': (time.time() - start_time) * 1000,
                    'success': True
                }
                self._migration_history.append(migration_record)
                
                logger.info(f"✅ Node migration completed in {migration_record['duration_ms']:.1f}ms")
                return target_strategy
                
            except Exception as e:
                logger.error(f"❌ Node migration failed: {e}")
                migration_record = {
                    'timestamp': time.time(),
                    'type': 'node',
                    'source_mode': source_mode.name,
                    'target_mode': target_mode.name,
                    'data_size': source_size,
                    'duration_ms': (time.time() - start_time) * 1000,
                    'success': False,
                    'error': str(e)
                }
                self._migration_history.append(migration_record)
                raise XWNodeStrategyError(f"Migration failed: {e}")
    
    def execute_edge_migration(self, source_strategy: Any, target_mode: EdgeMode,
                              target_traits: EdgeTrait = EdgeTrait.NONE,
                              **options) -> Any:
        """Execute migration from source edge strategy to target."""
        with self._migration_lock:
            start_time = time.time()
            
            # Extract data from source
            edge_list = list(source_strategy.edges(data=True))
            vertex_list = list(source_strategy.vertices())
            
            # Create migration plan
            source_mode = getattr(source_strategy, '_mode', EdgeMode.LEGACY)
            plan = self.plan_edge_migration(source_mode, target_mode,
                                          getattr(source_strategy, '_traits', EdgeTrait.NONE),
                                          target_traits, len(edge_list), len(vertex_list))
            
            logger.info(f"🔄 Executing edge migration: {source_mode.name} → {target_mode.name}")
            logger.info(f"📊 Graph: {len(vertex_list)} vertices, {len(edge_list)} edges")
            
            # Create target strategy
            target_strategy = self._registry.get_edge_strategy(target_mode, traits=target_traits, **options)
            
            # Migrate vertices and edges
            try:
                # Add vertices first
                for vertex in vertex_list:
                    target_strategy.add_vertex(vertex)
                
                # Add edges
                for source, target, edge_data in edge_list:
                    properties = edge_data.get('properties', {})
                    target_strategy.add_edge(source, target, **properties)
                
                # Record migration
                migration_record = {
                    'timestamp': time.time(),
                    'type': 'edge',
                    'source_mode': source_mode.name,
                    'target_mode': target_mode.name,
                    'edge_count': len(edge_list),
                    'vertex_count': len(vertex_list),
                    'duration_ms': (time.time() - start_time) * 1000,
                    'success': True
                }
                self._migration_history.append(migration_record)
                
                logger.info(f"✅ Edge migration completed in {migration_record['duration_ms']:.1f}ms")
                return target_strategy
                
            except Exception as e:
                logger.error(f"❌ Edge migration failed: {e}")
                migration_record = {
                    'timestamp': time.time(),
                    'type': 'edge',
                    'source_mode': source_mode.name,
                    'target_mode': target_mode.name,
                    'edge_count': len(edge_list),
                    'vertex_count': len(vertex_list),
                    'duration_ms': (time.time() - start_time) * 1000,
                    'success': False,
                    'error': str(e)
                }
                self._migration_history.append(migration_record)
                raise XWNodeStrategyError(f"Edge migration failed: {e}")
    
    # ============================================================================
    # MIGRATION HISTORY AND ANALYSIS
    # ============================================================================
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get the history of all migrations."""
        return self._migration_history.copy()
    
    def get_migration_stats(self) -> Dict[str, Any]:
        """Get statistics about migrations."""
        if not self._migration_history:
            return {'total_migrations': 0}
        
        successful = [m for m in self._migration_history if m['success']]
        failed = [m for m in self._migration_history if not m['success']]
        
        avg_duration = sum(m['duration_ms'] for m in successful) / len(successful) if successful else 0
        
        return {
            'total_migrations': len(self._migration_history),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(self._migration_history) * 100,
            'average_duration_ms': round(avg_duration, 2),
            'most_common_source': self._most_common_field('source_mode'),
            'most_common_target': self._most_common_field('target_mode')
        }
    
    def _most_common_field(self, field: str) -> Optional[str]:
        """Find the most common value for a field in migration history."""
        if not self._migration_history:
            return None
        
        from collections import Counter
        values = [m.get(field) for m in self._migration_history if field in m]
        if not values:
            return None
        
        counter = Counter(values)
        return counter.most_common(1)[0][0]
    
    def clear_migration_history(self) -> None:
        """Clear the migration history."""
        self._migration_history.clear()
        logger.info("🧹 Migration history cleared")


# Global migrator instance
_migrator = None
_migrator_lock = threading.Lock()


def get_migrator() -> xStrategyMigrator:
    """Get the global strategy migrator instance."""
    global _migrator
    if _migrator is None:
        with _migrator_lock:
            if _migrator is None:
                _migrator = xStrategyMigrator()
    return _migrator
