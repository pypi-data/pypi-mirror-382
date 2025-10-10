#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/base.py

Operation Executor Base Classes

This module provides base classes for operation executors with capability checking.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 08-Oct-2025
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .contracts import (
    IOperationExecutor,
    Action,
    ExecutionContext,
    ExecutionResult,
    NodeType
)
from .types import OperationCapability
from .errors import UnsupportedOperationError  # Reuse from root via errors.py
from ...errors import XWNodeValueError


class AOperationExecutor(IOperationExecutor):
    """
    Abstract base class for operation executors.
    
    Provides common functionality including:
    - Capability checking
    - Performance monitoring
    - Error handling
    - Validation
    """
    
    # Operation name (must be set by subclasses)
    OPERATION_NAME: str = "UNKNOWN"
    
    # Supported node types (empty = all types)
    SUPPORTED_NODE_TYPES: List[NodeType] = []
    
    # Required capabilities
    REQUIRED_CAPABILITIES: OperationCapability = OperationCapability.NONE
    
    def __init__(self):
        """Initialize operation executor."""
        self._execution_count = 0
        self._total_time = 0.0
        self._error_count = 0
    
    def execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """
        Execute operation with monitoring and error handling.
        
        This method implements the Template Method pattern:
        1. Validate
        2. Check capability
        3. Execute (delegated to subclass)
        4. Monitor performance
        """
        start_time = time.time()
        
        try:
            # Validate action
            if not self.validate(action, context):
                raise XWNodeValueError(f"Invalid action: {action.type}")
            
            # Check capability
            self.validate_capability_or_raise(context)
            
            # Execute (delegated to subclass)
            result = self._do_execute(action, context)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._execution_count += 1
            self._total_time += execution_time
            result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            self._error_count += 1
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                data=None,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    @abstractmethod
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """
        Execute the actual operation (implemented by subclasses).
        
        Args:
            action: The action to execute
            context: Execution context
            
        Returns:
            ExecutionResult with data
        """
        pass
    
    def validate(self, action: Action, context: ExecutionContext) -> bool:
        """
        Validate action before execution.
        
        Default implementation checks basic requirements.
        Subclasses can override for specific validation.
        """
        if not action or not action.type:
            return False
        if not context or not context.node:
            return False
        return True
    
    def can_execute_on(self, node_type: NodeType) -> bool:
        """
        Check if this executor can operate on the given node type.
        
        Args:
            node_type: The node type to check
            
        Returns:
            True if this executor supports the node type
        """
        # Empty list means supports all types (universal operation)
        if not self.SUPPORTED_NODE_TYPES:
            return True
        return node_type in self.SUPPORTED_NODE_TYPES
    
    def validate_capability_or_raise(self, context: ExecutionContext) -> None:
        """
        Validate operation can execute on node, raise if not.
        
        Args:
            context: Execution context
            
        Raises:
            UnsupportedOperationError: If operation cannot execute on node type
        """
        # Get node's strategy type
        if hasattr(context.node, '_strategy') and hasattr(context.node._strategy, 'STRATEGY_TYPE'):
            node_type = context.node._strategy.STRATEGY_TYPE
        elif hasattr(context.node, 'STRATEGY_TYPE'):
            node_type = context.node.STRATEGY_TYPE
        else:
            # Default to TREE for backward compatibility
            node_type = NodeType.TREE
        
        # Check if operation can execute on this node type
        if not self.can_execute_on(node_type):
            supported = [nt.name for nt in self.SUPPORTED_NODE_TYPES]
            raise UnsupportedOperationError(
                self.OPERATION_NAME,
                node_type,
                f"Requires one of: {supported}"
            )
    
    def estimate_cost(self, action: Action, context: ExecutionContext) -> int:
        """
        Estimate execution cost.
        
        Default implementation returns fixed cost.
        Subclasses can override for more accurate estimates.
        """
        return 100
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics for this executor."""
        avg_time = self._total_time / self._execution_count if self._execution_count > 0 else 0
        
        return {
            'operation': self.OPERATION_NAME,
            'execution_count': self._execution_count,
            'total_time': self._total_time,
            'average_time': avg_time,
            'error_count': self._error_count,
            'success_rate': (self._execution_count - self._error_count) / self._execution_count if self._execution_count > 0 else 1.0
        }


class AUniversalOperationExecutor(AOperationExecutor):
    """
    Base class for universal operations that work on all node types.
    
    Universal operations:
    - SELECT, INSERT, UPDATE, DELETE
    - WHERE, FILTER
    - GROUP BY, COUNT, SUM, AVG
    - PROJECT, EXTEND
    """
    
    # Universal operations support all node types (empty list)
    SUPPORTED_NODE_TYPES: List[NodeType] = []


class ATreeOperationExecutor(AOperationExecutor):
    """
    Base class for tree-specific operations.
    
    Tree operations:
    - BETWEEN, RANGE
    - ORDER BY
    - MIN, MAX (optimal on trees)
    """
    
    # Only works on tree nodes
    SUPPORTED_NODE_TYPES: List[NodeType] = [NodeType.TREE]
    REQUIRED_CAPABILITIES: OperationCapability = OperationCapability.REQUIRES_ORDERED


class AGraphOperationExecutor(AOperationExecutor):
    """
    Base class for graph-specific operations.
    
    Graph operations:
    - MATCH, PATH
    - OUT, IN_TRAVERSE
    - Graph traversal
    """
    
    # Only works on graph nodes
    SUPPORTED_NODE_TYPES: List[NodeType] = [NodeType.GRAPH, NodeType.TREE]  # Trees can act as graphs


class ALinearOperationExecutor(AOperationExecutor):
    """
    Base class for linear-specific operations.
    
    Linear operations:
    - SLICING, INDEXING
    - Sequential operations
    """
    
    # Only works on linear and matrix nodes
    SUPPORTED_NODE_TYPES: List[NodeType] = [NodeType.LINEAR, NodeType.MATRIX]


__all__ = [
    'AOperationExecutor',
    'AUniversalOperationExecutor',
    'ATreeOperationExecutor',
    'AGraphOperationExecutor',
    'ALinearOperationExecutor',
    'UnsupportedOperationError',
]
