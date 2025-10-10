#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/executors/aggregation/having_executor.py

HAVING Executor

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 09-Oct-2025
"""

from typing import Any, Dict, List
from ..base import AUniversalOperationExecutor
from ..contracts import Action, ExecutionContext, ExecutionResult
from ..types import OperationType

class HavingExecutor(AUniversalOperationExecutor):
    """
    HAVING operation executor.
    
    Filters grouped data
    
    Capability: Universal
    Operation Type: AGGREGATION
    """
    
    OPERATION_NAME = "HAVING"
    OPERATION_TYPE = OperationType.AGGREGATION
    SUPPORTED_NODE_TYPES = []  # Universal
    
    def _do_execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        """Execute HAVING operation."""
        params = action.params
        node = context.node
        
        result_data = self._execute_having(node, params, context)
        
        return ExecutionResult(
            success=True,
            data=result_data,
            operation=self.OPERATION_NAME,
            metadata={'operation': self.OPERATION_NAME}
        )
    
    def _execute_having(self, node: Any, params: Dict, context: ExecutionContext) -> Dict:
        """Execute having logic."""
        # Implementation here
        return {'result': 'HAVING executed', 'params': params}
