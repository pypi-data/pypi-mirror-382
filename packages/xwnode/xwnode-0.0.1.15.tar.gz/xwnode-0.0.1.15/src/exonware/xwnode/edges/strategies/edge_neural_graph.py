"""
Neural Graph Edge Strategy Implementation

This module implements the NEURAL_GRAPH strategy for neural network
computation graphs with automatic differentiation and gradient tracking.
"""

from typing import Any, Iterator, Dict, List, Set, Optional, Tuple, Callable, Union
from collections import defaultdict, deque
import math
from enum import Enum
from ._base_edge import aEdgeStrategy
from ...types import EdgeMode, EdgeTrait


class ActivationFunction(Enum):
    """Common activation functions."""
    LINEAR = "linear"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    RELU = "relu"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    SWISH = "swish"
    GELU = "gelu"


class NeuralEdge:
    """Represents a connection between neural network nodes."""
    
    def __init__(self, edge_id: str, source: str, target: str, 
                 weight: float = 1.0, **properties):
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.weight = float(weight)
        self.properties = properties.copy()
        
        # Gradient tracking for backpropagation
        self.gradient = 0.0
        self.accumulated_gradient = 0.0
        self.gradient_history: List[float] = []
        
        # Training metadata
        self.last_forward_value = 0.0
        self.last_backward_value = 0.0
        self.update_count = 0
        self.learning_rate = properties.get('learning_rate', 0.01)
        
        # Regularization
        self.l1_lambda = properties.get('l1_lambda', 0.0)
        self.l2_lambda = properties.get('l2_lambda', 0.0)
        self.dropout_rate = properties.get('dropout_rate', 0.0)
        self.is_frozen = properties.get('frozen', False)
    
    def forward(self, input_value: float) -> float:
        """Forward pass through edge."""
        self.last_forward_value = input_value
        return input_value * self.weight
    
    def backward(self, gradient: float) -> float:
        """Backward pass for gradient computation."""
        self.gradient = gradient * self.last_forward_value
        self.accumulated_gradient += self.gradient
        self.last_backward_value = gradient * self.weight
        return self.last_backward_value
    
    def update_weight(self, optimizer_func: Optional[Callable] = None) -> None:
        """Update weight based on accumulated gradients."""
        if self.is_frozen:
            return
        
        if optimizer_func:
            # Custom optimizer
            self.weight = optimizer_func(self.weight, self.accumulated_gradient)
        else:
            # Simple SGD with regularization
            regularization = 0.0
            
            # L1 regularization
            if self.l1_lambda > 0:
                regularization += self.l1_lambda * (1 if self.weight > 0 else -1)
            
            # L2 regularization
            if self.l2_lambda > 0:
                regularization += self.l2_lambda * self.weight
            
            # Weight update
            self.weight -= self.learning_rate * (self.accumulated_gradient + regularization)
        
        # Store gradient history
        self.gradient_history.append(self.accumulated_gradient)
        if len(self.gradient_history) > 1000:  # Limit history size
            self.gradient_history = self.gradient_history[-1000:]
        
        # Reset accumulated gradient
        self.accumulated_gradient = 0.0
        self.update_count += 1
    
    def reset_gradients(self) -> None:
        """Reset all gradient information."""
        self.gradient = 0.0
        self.accumulated_gradient = 0.0
    
    def get_weight_statistics(self) -> Dict[str, float]:
        """Get statistics about weight updates."""
        if not self.gradient_history:
            return {'mean_gradient': 0.0, 'gradient_variance': 0.0}
        
        mean_grad = sum(self.gradient_history) / len(self.gradient_history)
        variance = sum((g - mean_grad) ** 2 for g in self.gradient_history) / len(self.gradient_history)
        
        return {
            'mean_gradient': mean_grad,
            'gradient_variance': variance,
            'gradient_magnitude': abs(mean_grad),
            'update_count': self.update_count
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.edge_id,
            'source': self.source,
            'target': self.target,
            'weight': self.weight,
            'gradient': self.gradient,
            'accumulated_gradient': self.accumulated_gradient,
            'learning_rate': self.learning_rate,
            'l1_lambda': self.l1_lambda,
            'l2_lambda': self.l2_lambda,
            'dropout_rate': self.dropout_rate,
            'is_frozen': self.is_frozen,
            'update_count': self.update_count,
            'properties': self.properties
        }


class NeuralNode:
    """Represents a node in the neural computation graph."""
    
    def __init__(self, node_id: str, activation: ActivationFunction = ActivationFunction.LINEAR,
                 bias: float = 0.0, **properties):
        self.node_id = node_id
        self.activation = activation
        self.bias = bias
        self.properties = properties.copy()
        
        # Computation state
        self.value = 0.0
        self.gradient = 0.0
        self.pre_activation = 0.0
        
        # Training metadata
        self.is_input = properties.get('is_input', False)
        self.is_output = properties.get('is_output', False)
        self.is_frozen = properties.get('frozen', False)
        
        # Batch processing
        self.batch_values: List[float] = []
        self.batch_gradients: List[float] = []
    
    def activate(self, x: float) -> float:
        """Apply activation function."""
        if self.activation == ActivationFunction.LINEAR:
            return x
        elif self.activation == ActivationFunction.SIGMOID:
            return 1.0 / (1.0 + math.exp(-x))
        elif self.activation == ActivationFunction.TANH:
            return math.tanh(x)
        elif self.activation == ActivationFunction.RELU:
            return max(0.0, x)
        elif self.activation == ActivationFunction.LEAKY_RELU:
            alpha = self.properties.get('leaky_alpha', 0.01)
            return x if x > 0 else alpha * x
        elif self.activation == ActivationFunction.ELU:
            alpha = self.properties.get('elu_alpha', 1.0)
            return x if x > 0 else alpha * (math.exp(x) - 1)
        elif self.activation == ActivationFunction.SWISH:
            return x * (1.0 / (1.0 + math.exp(-x)))
        elif self.activation == ActivationFunction.GELU:
            return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x**3)))
        else:
            return x
    
    def activate_derivative(self, x: float) -> float:
        """Compute derivative of activation function."""
        if self.activation == ActivationFunction.LINEAR:
            return 1.0
        elif self.activation == ActivationFunction.SIGMOID:
            s = self.activate(x)
            return s * (1.0 - s)
        elif self.activation == ActivationFunction.TANH:
            t = math.tanh(x)
            return 1.0 - t * t
        elif self.activation == ActivationFunction.RELU:
            return 1.0 if x > 0 else 0.0
        elif self.activation == ActivationFunction.LEAKY_RELU:
            alpha = self.properties.get('leaky_alpha', 0.01)
            return 1.0 if x > 0 else alpha
        elif self.activation == ActivationFunction.ELU:
            alpha = self.properties.get('elu_alpha', 1.0)
            return 1.0 if x > 0 else alpha * math.exp(x)
        else:
            return 1.0
    
    def forward(self, input_sum: float) -> float:
        """Forward pass through node."""
        self.pre_activation = input_sum + self.bias
        self.value = self.activate(self.pre_activation)
        return self.value
    
    def backward(self, gradient: float) -> float:
        """Backward pass for gradient computation."""
        activation_grad = self.activate_derivative(self.pre_activation)
        self.gradient = gradient * activation_grad
        return self.gradient


class xNeuralGraphStrategy(aEdgeStrategy):
    """
    Neural Graph strategy for neural network computation graphs.
    
    Supports automatic differentiation, gradient-based optimization,
    and various neural network architectures with backpropagation.
    """
    
    def __init__(self, traits: EdgeTrait = EdgeTrait.NONE, **options):
        """Initialize the Neural Graph strategy."""
        super().__init__(EdgeMode.NEURAL_GRAPH, traits, **options)
        
        self.default_learning_rate = options.get('learning_rate', 0.01)
        self.enable_autodiff = options.get('enable_autodiff', True)
        self.batch_size = options.get('batch_size', 32)
        self.enable_regularization = options.get('enable_regularization', True)
        
        # Core storage
        self._edges: Dict[str, NeuralEdge] = {}  # edge_id -> NeuralEdge
        self._nodes: Dict[str, NeuralNode] = {}  # node_id -> NeuralNode
        self._outgoing: Dict[str, List[str]] = defaultdict(list)  # source -> [edge_ids]
        self._incoming: Dict[str, List[str]] = defaultdict(list)  # target -> [edge_ids]
        
        # Network topology
        self._input_nodes: Set[str] = set()
        self._output_nodes: Set[str] = set()
        self._hidden_nodes: Set[str] = set()
        self._topological_order: List[str] = []
        
        # Training state
        self._training_mode = True
        self._epoch_count = 0
        self._total_loss = 0.0
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def get_supported_traits(self) -> EdgeTrait:
        """Get the traits supported by the neural graph strategy."""
        return (EdgeTrait.DIRECTED | EdgeTrait.WEIGHTED | EdgeTrait.SPARSE)
    
    def _generate_edge_id(self) -> str:
        """Generate unique edge ID."""
        self._edge_id_counter += 1
        return f"neural_edge_{self._edge_id_counter}"
    
    def _compute_topological_order(self) -> None:
        """Compute topological ordering for forward/backward passes."""
        # Kahn's algorithm
        in_degree = defaultdict(int)
        for node_id in self._nodes:
            in_degree[node_id] = len(self._incoming[node_id])
        
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        order = []
        
        while queue:
            current = queue.popleft()
            order.append(current)
            
            for edge_id in self._outgoing[current]:
                edge = self._edges[edge_id]
                target = edge.target
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)
        
        self._topological_order = order
    
    # ============================================================================
    # CORE EDGE OPERATIONS
    # ============================================================================
    
    def add_edge(self, source: str, target: str, **properties) -> str:
        """Add neural connection edge."""
        weight = properties.pop('weight', 1.0)
        edge_id = properties.pop('edge_id', self._generate_edge_id())
        
        if edge_id in self._edges:
            raise ValueError(f"Edge ID {edge_id} already exists")
        
        # Create neural edge
        neural_edge = NeuralEdge(edge_id, source, target, weight, **properties)
        
        # Store edge
        self._edges[edge_id] = neural_edge
        self._outgoing[source].append(edge_id)
        self._incoming[target].append(edge_id)
        
        # Ensure nodes exist
        if source not in self._nodes:
            self.add_neural_node(source)
        if target not in self._nodes:
            self.add_neural_node(target)
        
        self._edge_count += 1
        self._compute_topological_order()
        
        return edge_id
    
    def remove_edge(self, source: str, target: str, edge_id: Optional[str] = None) -> bool:
        """Remove neural edge."""
        if edge_id and edge_id in self._edges:
            edge = self._edges[edge_id]
            if edge.source == source and edge.target == target:
                # Remove from indices
                del self._edges[edge_id]
                self._outgoing[source].remove(edge_id)
                self._incoming[target].remove(edge_id)
                
                self._edge_count -= 1
                self._compute_topological_order()
                return True
        else:
            # Find edge by endpoints
            for edge_id in self._outgoing.get(source, []):
                edge = self._edges[edge_id]
                if edge.target == target:
                    return self.remove_edge(source, target, edge_id)
        
        return False
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists."""
        for edge_id in self._outgoing.get(source, []):
            edge = self._edges[edge_id]
            if edge.target == target:
                return True
        return False
    
    def get_edge_data(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get edge data."""
        for edge_id in self._outgoing.get(source, []):
            edge = self._edges[edge_id]
            if edge.target == target:
                return edge.to_dict()
        return None
    
    def neighbors(self, vertex: str, direction: str = 'out') -> Iterator[str]:
        """Get neighbors of vertex."""
        if direction in ['out', 'both']:
            for edge_id in self._outgoing.get(vertex, []):
                edge = self._edges[edge_id]
                yield edge.target
        
        if direction in ['in', 'both']:
            for edge_id in self._incoming.get(vertex, []):
                edge = self._edges[edge_id]
                yield edge.source
    
    def degree(self, vertex: str, direction: str = 'out') -> int:
        """Get degree of vertex."""
        if direction == 'out':
            return len(self._outgoing.get(vertex, []))
        elif direction == 'in':
            return len(self._incoming.get(vertex, []))
        else:  # both
            return len(self._outgoing.get(vertex, [])) + len(self._incoming.get(vertex, []))
    
    def edges(self, data: bool = False) -> Iterator[tuple]:
        """Get all edges."""
        for edge in self._edges.values():
            if data:
                yield (edge.source, edge.target, edge.to_dict())
            else:
                yield (edge.source, edge.target)
    
    def vertices(self) -> Iterator[str]:
        """Get all vertices."""
        return iter(self._nodes.keys())
    
    def __len__(self) -> int:
        """Get number of edges."""
        return self._edge_count
    
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._nodes)
    
    def clear(self) -> None:
        """Clear all data."""
        self._edges.clear()
        self._nodes.clear()
        self._outgoing.clear()
        self._incoming.clear()
        self._input_nodes.clear()
        self._output_nodes.clear()
        self._hidden_nodes.clear()
        self._topological_order.clear()
        
        self._epoch_count = 0
        self._total_loss = 0.0
        self._edge_count = 0
        self._edge_id_counter = 0
    
    def add_vertex(self, vertex: str) -> None:
        """Add vertex (neural node)."""
        if vertex not in self._nodes:
            self.add_neural_node(vertex)
    
    def remove_vertex(self, vertex: str) -> bool:
        """Remove vertex and all its edges."""
        if vertex not in self._nodes:
            return False
        
        # Remove all outgoing edges
        outgoing_edges = list(self._outgoing.get(vertex, []))
        for edge_id in outgoing_edges:
            edge = self._edges[edge_id]
            self.remove_edge(edge.source, edge.target, edge_id)
        
        # Remove all incoming edges
        incoming_edges = list(self._incoming.get(vertex, []))
        for edge_id in incoming_edges:
            edge = self._edges[edge_id]
            self.remove_edge(edge.source, edge.target, edge_id)
        
        # Remove node
        del self._nodes[vertex]
        self._input_nodes.discard(vertex)
        self._output_nodes.discard(vertex)
        self._hidden_nodes.discard(vertex)
        
        self._compute_topological_order()
        return True
    
    # ============================================================================
    # NEURAL NETWORK OPERATIONS
    # ============================================================================
    
    def add_neural_node(self, node_id: str, activation: ActivationFunction = ActivationFunction.LINEAR,
                       bias: float = 0.0, node_type: str = 'hidden', **properties) -> None:
        """Add neural network node."""
        node = NeuralNode(node_id, activation, bias, **properties)
        
        if node_type == 'input':
            node.is_input = True
            self._input_nodes.add(node_id)
        elif node_type == 'output':
            node.is_output = True
            self._output_nodes.add(node_id)
        else:
            self._hidden_nodes.add(node_id)
        
        self._nodes[node_id] = node
        self._compute_topological_order()
    
    def set_node_value(self, node_id: str, value: float) -> None:
        """Set node value (for input nodes)."""
        if node_id in self._nodes:
            self._nodes[node_id].value = value
    
    def get_node_value(self, node_id: str) -> float:
        """Get node value."""
        return self._nodes.get(node_id, NeuralNode("")).value
    
    def forward_pass(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """Perform forward pass through network."""
        # Set input values
        for node_id, value in inputs.items():
            if node_id in self._input_nodes:
                self.set_node_value(node_id, value)
        
        # Process nodes in topological order
        for node_id in self._topological_order:
            if node_id not in self._input_nodes:  # Skip input nodes
                node = self._nodes[node_id]
                
                # Compute weighted sum of inputs
                input_sum = 0.0
                for edge_id in self._incoming[node_id]:
                    edge = self._edges[edge_id]
                    source_value = self._nodes[edge.source].value
                    input_sum += edge.forward(source_value)
                
                # Apply activation function
                node.forward(input_sum)
        
        # Return output values
        return {node_id: self.get_node_value(node_id) for node_id in self._output_nodes}
    
    def backward_pass(self, target_outputs: Dict[str, float], 
                     loss_function: str = 'mse') -> float:
        """Perform backward pass for gradient computation."""
        # Compute loss and output gradients
        total_loss = 0.0
        
        for node_id in self._output_nodes:
            node = self._nodes[node_id]
            target = target_outputs.get(node_id, 0.0)
            
            if loss_function == 'mse':
                # Mean squared error
                error = node.value - target
                total_loss += 0.5 * error * error
                node.gradient = error
            elif loss_function == 'cross_entropy':
                # Cross entropy (simplified)
                total_loss += -target * math.log(max(1e-15, node.value))
                node.gradient = node.value - target
            else:
                # Default to MSE
                error = node.value - target
                total_loss += 0.5 * error * error
                node.gradient = error
        
        # Backpropagate gradients
        for node_id in reversed(self._topological_order):
            if node_id not in self._output_nodes:  # Skip output nodes (already have gradients)
                node = self._nodes[node_id]
                node.gradient = 0.0
                
                # Accumulate gradients from outgoing edges
                for edge_id in self._outgoing[node_id]:
                    edge = self._edges[edge_id]
                    target_node = self._nodes[edge.target]
                    node.gradient += edge.backward(target_node.gradient)
                
                # Apply activation derivative
                if not node.is_input:
                    node.gradient = node.backward(node.gradient)
        
        self._total_loss += total_loss
        return total_loss
    
    def update_weights(self, optimizer_func: Optional[Callable] = None) -> None:
        """Update all edge weights based on gradients."""
        for edge in self._edges.values():
            edge.update_weight(optimizer_func)
    
    def train_step(self, inputs: Dict[str, float], targets: Dict[str, float],
                  loss_function: str = 'mse') -> float:
        """Perform one training step (forward + backward + update)."""
        # Forward pass
        outputs = self.forward_pass(inputs)
        
        # Backward pass
        loss = self.backward_pass(targets, loss_function)
        
        # Update weights
        if self._training_mode:
            self.update_weights()
        
        return loss
    
    def reset_gradients(self) -> None:
        """Reset all gradients to zero."""
        for edge in self._edges.values():
            edge.reset_gradients()
        for node in self._nodes.values():
            node.gradient = 0.0
    
    def set_training_mode(self, training: bool) -> None:
        """Set training mode (affects weight updates)."""
        self._training_mode = training
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Get comprehensive network statistics."""
        if not self._nodes:
            return {'nodes': 0, 'edges': 0, 'layers': 0}
        
        # Compute layer depths
        layer_depths = {}
        for node_id in self._topological_order:
            if node_id in self._input_nodes:
                layer_depths[node_id] = 0
            else:
                max_input_depth = max(
                    (layer_depths.get(self._edges[edge_id].source, 0) 
                     for edge_id in self._incoming[node_id]),
                    default=-1
                )
                layer_depths[node_id] = max_input_depth + 1
        
        max_depth = max(layer_depths.values()) if layer_depths else 0
        
        # Weight statistics
        weights = [edge.weight for edge in self._edges.values()]
        gradients = [edge.accumulated_gradient for edge in self._edges.values()]
        
        return {
            'nodes': len(self._nodes),
            'edges': self._edge_count,
            'input_nodes': len(self._input_nodes),
            'hidden_nodes': len(self._hidden_nodes),
            'output_nodes': len(self._output_nodes),
            'layers': max_depth + 1,
            'training_mode': self._training_mode,
            'epoch_count': self._epoch_count,
            'total_loss': self._total_loss,
            'avg_weight': sum(weights) / len(weights) if weights else 0,
            'weight_variance': sum((w - sum(weights)/len(weights))**2 for w in weights) / len(weights) if len(weights) > 1 else 0,
            'avg_gradient': sum(abs(g) for g in gradients) / len(gradients) if gradients else 0
        }
    
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    
    @property
    def backend_info(self) -> Dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'NEURAL_GRAPH',
            'backend': 'Computation graph with automatic differentiation',
            'enable_autodiff': self.enable_autodiff,
            'default_learning_rate': self.default_learning_rate,
            'batch_size': self.batch_size,
            'complexity': {
                'forward_pass': 'O(V + E)',
                'backward_pass': 'O(V + E)',
                'weight_update': 'O(E)',
                'memory': 'O(V + E)',
                'training_step': 'O(V + E)'
            }
        }
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.get_network_statistics()
        
        return {
            'nodes': stats['nodes'],
            'edges': stats['edges'],
            'layers': stats['layers'],
            'parameters': self._edge_count,  # Each edge is a parameter
            'training_mode': stats['training_mode'],
            'avg_weight': f"{stats['avg_weight']:.4f}",
            'avg_gradient': f"{stats['avg_gradient']:.6f}",
            'memory_usage': f"{self._edge_count * 150 + len(self._nodes) * 100} bytes (estimated)"
        }
