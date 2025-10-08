#!/usr/bin/env python3
"""
Test AUTO-3 Phase 3: Advanced Data Structures.

Tests Union-Find, FSM, DAG, and Flow Graph behavioral views on xNode.
"""

import sys
import os
import pytest
from typing import Dict, Any, List

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode
from src.xlib.xnode.errors import xNodeTypeError, xNodeValueError


class TestUnionFindView:
    """Test Union-Find (Disjoint Set) behavioral view."""
    
    def test_union_find_creation(self):
        """Test creating Union-Find view from dict node."""
        node = xNode.from_native({})
        uf = node.as_union_find()
        
        assert uf.size() == 0
        assert uf.sets_count() == 0
    
    def test_make_set_operations(self):
        """Test creating individual sets."""
        node = xNode.from_native({})
        uf = node.as_union_find()
        
        # Create sets
        uf.make_set("A")
        uf.make_set("B")
        uf.make_set("C")
        
        assert uf.size() == 3
        assert uf.sets_count() == 3
        
        # Each element should be its own root
        assert uf.find("A") == "A"
        assert uf.find("B") == "B"
        assert uf.find("C") == "C"
    
    def test_union_operations(self):
        """Test union operations."""
        node = xNode.from_native({})
        uf = node.as_union_find()
        
        # Create sets
        elements = ["A", "B", "C", "D"]
        for elem in elements:
            uf.make_set(elem)
        
        assert uf.sets_count() == 4
        
        # Union some sets
        uf.union("A", "B")
        assert uf.sets_count() == 3
        assert uf.connected("A", "B")
        
        uf.union("C", "D")
        assert uf.sets_count() == 2
        assert uf.connected("C", "D")
        
        # Union the two groups
        uf.union("A", "C")
        assert uf.sets_count() == 1
        
        # All elements should be connected
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                assert uf.connected(elements[i], elements[j])
    
    def test_connected_check(self):
        """Test connectivity checking."""
        node = xNode.from_native({})
        uf = node.as_union_find()
        
        # Create disconnected sets
        uf.make_set(1)
        uf.make_set(2)
        uf.make_set(3)
        uf.make_set(4)
        
        # Connect 1-2 and 3-4
        uf.union(1, 2)
        uf.union(3, 4)
        
        # Test connectivity
        assert uf.connected(1, 2)
        assert uf.connected(3, 4)
        assert not uf.connected(1, 3)
        assert not uf.connected(2, 4)
        
        # Connect the groups
        uf.union(1, 3)
        assert uf.connected(1, 4)  # Now all connected
    
    def test_get_sets(self):
        """Test getting all sets."""
        node = xNode.from_native({})
        uf = node.as_union_find()
        
        # Create elements
        elements = ["A", "B", "C", "D", "E"]
        for elem in elements:
            uf.make_set(elem)
        
        # Create two groups
        uf.union("A", "B")
        uf.union("A", "C")  # Group 1: {A, B, C}
        uf.union("D", "E")  # Group 2: {D, E}
        
        sets = uf.get_sets()
        assert len(sets) == 2
        
        # Check that sets contain correct elements
        set_sizes = [len(s) for s in sets.values()]
        assert sorted(set_sizes) == [2, 3]
    
    def test_union_find_clear(self):
        """Test clearing union-find."""
        node = xNode.from_native({})
        uf = node.as_union_find()
        
        # Add some data
        for i in range(5):
            uf.make_set(i)
        uf.union(0, 1)
        uf.union(2, 3)
        
        assert uf.size() == 5
        assert uf.sets_count() == 3
        
        uf.clear()
        assert uf.size() == 0
        assert uf.sets_count() == 0
    
    def test_union_find_non_dict_node(self):
        """Test Union-Find view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_union_find()


class TestFSMView:
    """Test FSM (Finite State Machine) behavioral view."""
    
    def test_fsm_creation(self):
        """Test creating FSM view from dict node."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        # Initially empty
        with pytest.raises(xNodeValueError):
            fsm.current_state()
    
    def test_fsm_basic_operations(self):
        """Test basic FSM operations."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        # Add states
        fsm.add_state("start")
        fsm.add_state("middle")
        fsm.add_state("end", is_final=True)
        
        # Set start state
        fsm.set_start("start")
        assert fsm.current_state() == "start"
        assert not fsm.is_final()
        
        # Add transitions
        fsm.add_transition("start", "a", "middle")
        fsm.add_transition("middle", "b", "end")
        
        # Test transitions
        result = fsm.step("a")
        assert result == "middle"
        assert fsm.current_state() == "middle"
        
        result = fsm.step("b")
        assert result == "end"
        assert fsm.current_state() == "end"
        assert fsm.is_final()
    
    def test_fsm_accepts_string(self):
        """Test FSM string acceptance."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        # Build FSM that accepts strings ending with "ab"
        fsm.add_state("q0")  # Start state
        fsm.add_state("q1")  # Seen 'a'
        fsm.add_state("q2", is_final=True)  # Seen "ab"
        
        fsm.set_start("q0")
        
        # Transitions
        fsm.add_transition("q0", "a", "q1")
        fsm.add_transition("q0", "b", "q0")
        fsm.add_transition("q1", "a", "q1")
        fsm.add_transition("q1", "b", "q2")
        fsm.add_transition("q2", "a", "q1")
        fsm.add_transition("q2", "b", "q0")
        
        # Test acceptance
        assert fsm.accepts("ab")
        assert fsm.accepts("aab")
        assert fsm.accepts("bab")
        assert fsm.accepts("aaab")
        
        assert not fsm.accepts("a")
        assert not fsm.accepts("b")
        assert not fsm.accepts("aba")
        assert not fsm.accepts("abaa")
    
    def test_fsm_reset(self):
        """Test FSM reset functionality."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        fsm.add_state("start")
        fsm.add_state("end")
        fsm.set_start("start")
        fsm.add_transition("start", "x", "end")
        
        # Move to end state
        fsm.step("x")
        assert fsm.current_state() == "end"
        
        # Reset
        fsm.reset()
        assert fsm.current_state() == "start"
    
    def test_fsm_invalid_transitions(self):
        """Test invalid FSM operations."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        fsm.add_state("start")
        fsm.set_start("start")
        
        # Invalid transition
        with pytest.raises(xNodeValueError):
            fsm.step("invalid")
        
        # Adding transition to non-existent state
        with pytest.raises(xNodeValueError):
            fsm.add_transition("start", "x", "nonexistent")
    
    def test_fsm_get_transitions(self):
        """Test getting all transitions."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        fsm.add_state("A")
        fsm.add_state("B")
        fsm.add_transition("A", "x", "B")
        fsm.add_transition("A", "y", "A")
        
        transitions = fsm.get_transitions()
        assert len(transitions) == 2
        assert transitions[("A", "x")] == "B"
        assert transitions[("A", "y")] == "A"
    
    def test_fsm_clear(self):
        """Test clearing FSM."""
        node = xNode.from_native({})
        fsm = node.as_fsm()
        
        fsm.add_state("start")
        fsm.add_state("end")
        fsm.set_start("start")
        fsm.add_transition("start", "x", "end")
        
        fsm.clear()
        
        with pytest.raises(xNodeValueError):
            fsm.current_state()
    
    def test_fsm_non_dict_node(self):
        """Test FSM view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_fsm()


class TestDAGView:
    """Test DAG (Directed Acyclic Graph) behavioral view."""
    
    def test_dag_creation(self):
        """Test creating DAG view from dict node."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        assert len(dag.get_nodes()) == 0
        assert len(dag.get_edges()) == 0
    
    def test_dag_add_nodes_and_edges(self):
        """Test adding nodes and edges to DAG."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        # Add nodes
        dag.add_node("A", "task_a")
        dag.add_node("B", "task_b")
        dag.add_node("C", "task_c")
        
        nodes = dag.get_nodes()
        assert len(nodes) == 3
        assert nodes["A"] == "task_a"
        
        # Add edges
        dag.add_edge("A", "B", weight=1.0)
        dag.add_edge("A", "C", weight=2.0)
        dag.add_edge("B", "C", weight=1.5)
        
        edges = dag.get_edges()
        assert len(edges) == 3
        assert ("B", 1.5) in edges["B"]
    
    def test_dag_topological_sort(self):
        """Test topological sorting."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        # Create a simple DAG: A -> B -> C, A -> C
        dag.add_node("A")
        dag.add_node("B")
        dag.add_node("C")
        dag.add_edge("A", "B")
        dag.add_edge("B", "C")
        dag.add_edge("A", "C")
        
        topo_order = dag.topological_sort()
        
        # A should come before B and C
        # B should come before C
        a_idx = topo_order.index("A")
        b_idx = topo_order.index("B")
        c_idx = topo_order.index("C")
        
        assert a_idx < b_idx
        assert a_idx < c_idx
        assert b_idx < c_idx
    
    def test_dag_cycle_detection(self):
        """Test cycle detection."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        # Create nodes
        dag.add_node("A")
        dag.add_node("B")
        dag.add_node("C")
        
        # Add edges that don't create cycle
        dag.add_edge("A", "B")
        dag.add_edge("B", "C")
        
        assert not dag.has_cycle()
        
        # Try to add edge that would create cycle
        with pytest.raises(xNodeValueError):
            dag.add_edge("C", "A")  # This would create A -> B -> C -> A cycle
    
    def test_dag_longest_path(self):
        """Test longest path calculation."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        # Create DAG with weighted edges
        dag.add_node("A")
        dag.add_node("B")
        dag.add_node("C")
        dag.add_node("D")
        
        dag.add_edge("A", "B", weight=5.0)
        dag.add_edge("A", "C", weight=3.0)
        dag.add_edge("B", "D", weight=2.0)
        dag.add_edge("C", "D", weight=4.0)
        
        # Longest path from A to D should be A -> B -> D (5 + 2 = 7)
        path, distance = dag.longest_path("A", "D")
        
        assert distance == 7.0
        assert path == ["A", "B", "D"]
    
    def test_dag_no_path(self):
        """Test longest path with no connection."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        dag.add_node("A")
        dag.add_node("B")
        # No edges between A and B
        
        with pytest.raises(xNodeValueError):
            dag.longest_path("A", "B")
    
    def test_dag_clear(self):
        """Test clearing DAG."""
        node = xNode.from_native({})
        dag = node.as_dag()
        
        dag.add_node("A")
        dag.add_node("B")
        dag.add_edge("A", "B")
        
        assert len(dag.get_nodes()) == 2
        
        dag.clear()
        assert len(dag.get_nodes()) == 0
        assert len(dag.get_edges()) == 0
    
    def test_dag_non_dict_node(self):
        """Test DAG view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_dag()


class TestFlowGraphView:
    """Test Flow Graph (Network Flow) behavioral view."""
    
    def test_flow_graph_creation(self):
        """Test creating Flow Graph view from dict node."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        assert len(flow.get_nodes()) == 0
        assert len(flow.get_edges()) == 0
    
    def test_flow_graph_add_edges(self):
        """Test adding edges with capacities."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        # Add edges
        flow.add_edge("S", "A", capacity=10.0)
        flow.add_edge("S", "B", capacity=8.0)
        flow.add_edge("A", "T", capacity=5.0)
        flow.add_edge("B", "T", capacity=7.0)
        flow.add_edge("A", "B", capacity=3.0)
        
        nodes = flow.get_nodes()
        assert len(nodes) == 4
        assert "S" in nodes and "A" in nodes and "B" in nodes and "T" in nodes
        
        edges = flow.get_edges()
        assert len(edges) == 5
        assert flow.get_capacity("S", "A") == 10.0
        assert flow.get_capacity("B", "T") == 7.0
    
    def test_flow_graph_max_flow_simple(self):
        """Test maximum flow calculation."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        # Simple flow network: S -> T with capacity 10
        flow.add_edge("S", "T", capacity=10.0)
        
        max_flow = flow.max_flow("S", "T")
        assert max_flow == 10.0
    
    def test_flow_graph_max_flow_complex(self):
        """Test maximum flow with multiple paths."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        # Flow network with multiple paths
        flow.add_edge("S", "A", capacity=10.0)
        flow.add_edge("S", "B", capacity=8.0)
        flow.add_edge("A", "T", capacity=5.0)
        flow.add_edge("B", "T", capacity=7.0)
        flow.add_edge("A", "B", capacity=3.0)
        
        max_flow = flow.max_flow("S", "T")
        # Max flow should be 12 (5 through A->T + 7 through B->T)
        assert max_flow == 12.0
    
    def test_flow_graph_min_cut(self):
        """Test minimum cut calculation."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        # Simple network
        flow.add_edge("S", "A", capacity=10.0)
        flow.add_edge("A", "T", capacity=5.0)
        
        # Min cut should separate S,A from T
        cut_left, cut_right = flow.min_cut("S", "T")
        
        assert "S" in cut_left
        assert "T" in cut_right
        # The cut should separate based on the bottleneck
    
    def test_flow_graph_invalid_capacity(self):
        """Test invalid capacity handling."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        with pytest.raises(xNodeValueError):
            flow.add_edge("A", "B", capacity=-1.0)
    
    def test_flow_graph_no_path(self):
        """Test max flow with no path."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        # Add disconnected nodes
        flow.add_edge("A", "B", capacity=10.0)
        flow.add_edge("C", "D", capacity=10.0)
        
        # No path from A to C
        max_flow = flow.max_flow("A", "C")
        assert max_flow == 0.0
    
    def test_flow_graph_clear(self):
        """Test clearing flow graph."""
        node = xNode.from_native({})
        flow = node.as_flow_graph()
        
        flow.add_edge("S", "T", capacity=10.0)
        assert len(flow.get_nodes()) == 2
        
        flow.clear()
        assert len(flow.get_nodes()) == 0
        assert len(flow.get_edges()) == 0
    
    def test_flow_graph_non_dict_node(self):
        """Test Flow Graph view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_flow_graph()


class TestPhase3Integration:
    """Test integration of Phase 3 structures with existing features."""
    
    def test_structure_info_phase3(self):
        """Test structure info includes Phase 3 capabilities."""
        # Dict node should support all Phase 3 structures
        dict_node = xNode.from_native({})
        info = dict_node.structure_info()
        
        supports = info["supports"]
        assert supports["union_find"] is True
        assert supports["fsm"] is True
        assert supports["dag"] is True
        assert supports["flow_graph"] is True
        
        # List node should not support Phase 3 structures
        list_node = xNode.from_native([])
        info = list_node.structure_info()
        
        supports = info["supports"]
        assert supports["union_find"] is False
        assert supports["fsm"] is False
        assert supports["dag"] is False
        assert supports["flow_graph"] is False
    
    def test_complex_workflow_example(self):
        """Test complex workflow using multiple Phase 3 structures."""
        # Scenario: Task dependency management with networking
        
        # 1. Use DAG for task dependencies
        task_dag_node = xNode.from_native({})
        task_dag = task_dag_node.as_dag()
        
        # Add tasks
        tasks = ["init", "compile", "test", "package", "deploy"]
        for task in tasks:
            task_dag.add_node(task, f"Task: {task}")
        
        # Add dependencies
        task_dag.add_edge("init", "compile")
        task_dag.add_edge("compile", "test")
        task_dag.add_edge("compile", "package")
        task_dag.add_edge("test", "deploy")
        task_dag.add_edge("package", "deploy")
        
        # Get execution order
        execution_order = task_dag.topological_sort()
        assert execution_order[0] == "init"
        assert execution_order[-1] == "deploy"
        
        # 2. Use Union-Find for grouping related tasks
        task_groups_node = xNode.from_native({})
        task_groups = task_groups_node.as_union_find()
        
        for task in tasks:
            task_groups.make_set(task)
        
        # Group build-related tasks
        task_groups.union("compile", "test")
        task_groups.union("compile", "package")
        
        # Check grouping
        assert task_groups.connected("compile", "test")
        assert task_groups.connected("test", "package")
        assert not task_groups.connected("init", "compile")
        
        # 3. Use Flow Graph for resource allocation
        resource_flow_node = xNode.from_native({})
        resource_flow = resource_flow_node.as_flow_graph()
        
        # Model CPU resources flowing from source to tasks to sink
        resource_flow.add_edge("CPU_source", "compile", capacity=4.0)
        resource_flow.add_edge("CPU_source", "test", capacity=2.0)
        resource_flow.add_edge("compile", "CPU_sink", capacity=3.0)
        resource_flow.add_edge("test", "CPU_sink", capacity=2.0)
        
        max_cpu_usage = resource_flow.max_flow("CPU_source", "CPU_sink")
        assert max_cpu_usage == 5.0  # Total CPU that can be utilized
        
        # 4. Use FSM for task state management
        state_machine_node = xNode.from_native({})
        state_machine = state_machine_node.as_fsm()
        
        # Define task states
        states = ["pending", "running", "completed", "failed"]
        for state in states:
            is_final = state in ["completed", "failed"]
            state_machine.add_state(state, is_final=is_final)
        
        state_machine.set_start("pending")
        state_machine.add_transition("pending", "start", "running")
        state_machine.add_transition("running", "success", "completed")
        state_machine.add_transition("running", "error", "failed")
        
        # Test state transitions
        assert state_machine.current_state() == "pending"
        state_machine.step("start")
        assert state_machine.current_state() == "running"
        state_machine.step("success")
        assert state_machine.current_state() == "completed"
        assert state_machine.is_final()
    
    def test_performance_characteristics(self):
        """Test performance characteristics of Phase 3 structures."""
        import time
        
        # Test Union-Find performance
        uf_node = xNode.from_native({})
        uf = uf_node.as_union_find()
        
        start_time = time.time()
        # Create many sets and union them
        n = 100
        for i in range(n):
            uf.make_set(i)
        
        # Union in a chain
        for i in range(n - 1):
            uf.union(i, i + 1)
        
        # Check connectivity (should be very fast with path compression)
        for i in range(0, n, 10):
            uf.connected(0, i)
        
        uf_time = time.time() - start_time
        
        # Test DAG performance
        dag_node = xNode.from_native({})
        dag = dag_node.as_dag()
        
        start_time = time.time()
        # Create a larger DAG
        for i in range(50):
            dag.add_node(str(i))
        
        # Add edges in a layered structure
        for i in range(40):
            dag.add_edge(str(i), str(i + 10))
        
        # Topological sort
        topo_order = dag.topological_sort()
        
        dag_time = time.time() - start_time
        
        # All operations should complete quickly
        assert uf_time < 1.0
        assert dag_time < 1.0
        assert len(topo_order) == 50
        
        print(f"Performance results:")
        print(f"  Union-Find operations: {uf_time:.4f}s")
        print(f"  DAG operations: {dag_time:.4f}s")
