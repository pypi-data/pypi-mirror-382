#!/usr/bin/env python3
"""
Test AUTO-3 Phase 4: Neural and Hypergraph Structures.

Tests Neural Graph and Hypergraph behavioral views on xNode.
"""

import sys
import os
import pytest
import math
from typing import Dict, Any, List, Set

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode
from src.xlib.xnode.errors import xNodeTypeError, xNodeValueError


class TestNeuralGraphView:
    """Test Neural Graph (Computational Graph) behavioral view."""
    
    def test_neural_graph_creation(self):
        """Test creating Neural Graph view from dict node."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        assert len(neural.get_operations()) == 0
        assert len(neural.get_forward_values()) == 0
        assert len(neural.get_gradients()) == 0
    
    def test_add_operations(self):
        """Test adding neural operations."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Add input operations
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("input2", "input", value=3.0)
        
        # Add computation operations
        neural.add_operation("add1", "add")
        neural.add_operation("mult1", "multiply")
        
        operations = neural.get_operations()
        assert len(operations) == 4
        assert operations["input1"]["type"] == "input"
        assert operations["input1"]["params"]["value"] == 2.0
        assert operations["add1"]["type"] == "add"
    
    def test_add_edges(self):
        """Test adding edges between operations."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Create operations
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("input2", "input", value=3.0)
        neural.add_operation("add1", "add")
        
        # Add edges
        neural.add_edge("input1", "add1")
        neural.add_edge("input2", "add1")
        
        operations = neural.get_operations()
        assert "input1" in operations["add1"]["inputs"]
        assert "input2" in operations["add1"]["inputs"]
        assert "add1" in operations["input1"]["outputs"]
        assert "add1" in operations["input2"]["outputs"]
    
    def test_simple_forward_pass(self):
        """Test simple forward pass computation."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Build simple addition graph: input1 + input2 = result
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("input2", "input", value=3.0)
        neural.add_operation("add1", "add")
        
        neural.add_edge("input1", "add1")
        neural.add_edge("input2", "add1")
        
        # Compile and execute
        neural.compile_graph()
        result = neural.forward()
        
        assert result["input1"] == 2.0
        assert result["input2"] == 3.0
        assert result["add1"] == 5.0
    
    def test_complex_forward_pass(self):
        """Test complex forward pass with multiple operations."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Build graph: (input1 + input2) * input3 
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("input2", "input", value=3.0)
        neural.add_operation("input3", "input", value=4.0)
        neural.add_operation("add1", "add")
        neural.add_operation("mult1", "multiply")
        
        # Connect: input1, input2 -> add1 -> mult1 <- input3
        neural.add_edge("input1", "add1")
        neural.add_edge("input2", "add1")
        neural.add_edge("add1", "mult1")
        neural.add_edge("input3", "mult1")
        
        neural.compile_graph()
        result = neural.forward()
        
        assert result["add1"] == 5.0  # 2 + 3
        assert result["mult1"] == 20.0  # 5 * 4
    
    def test_activation_functions(self):
        """Test neural activation functions."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Test ReLU
        neural.add_operation("input1", "input", value=-2.0)
        neural.add_operation("input2", "input", value=3.0)
        neural.add_operation("relu1", "relu")
        neural.add_operation("relu2", "relu")
        
        neural.add_edge("input1", "relu1")
        neural.add_edge("input2", "relu2")
        
        neural.compile_graph()
        result = neural.forward()
        
        assert result["relu1"] == 0.0  # max(0, -2)
        assert result["relu2"] == 3.0  # max(0, 3)
    
    def test_sigmoid_activation(self):
        """Test sigmoid activation function."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        neural.add_operation("input1", "input", value=0.0)
        neural.add_operation("sigmoid1", "sigmoid")
        
        neural.add_edge("input1", "sigmoid1")
        
        neural.compile_graph()
        result = neural.forward()
        
        # sigmoid(0) = 0.5
        assert abs(result["sigmoid1"] - 0.5) < 1e-6
    
    def test_linear_transformation(self):
        """Test linear transformation operation."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("linear1", "linear", weight=3.0, bias=1.0)
        
        neural.add_edge("input1", "linear1")
        
        neural.compile_graph()
        result = neural.forward()
        
        # linear: 3.0 * 2.0 + 1.0 = 7.0
        assert result["linear1"] == 7.0
    
    def test_backward_pass_simple(self):
        """Test simple backward pass (gradient computation)."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Simple chain: input1 -> add1 (with constant)
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("const1", "input", value=3.0)
        neural.add_operation("add1", "add")
        
        neural.add_edge("input1", "add1")
        neural.add_edge("const1", "add1")
        
        neural.compile_graph()
        neural.forward()
        
        # Backward pass
        gradients = neural.backward()
        
        # Gradient should flow equally to both inputs
        assert gradients["input1"] == 1.0
        assert gradients["const1"] == 1.0
        assert gradients["add1"] == 1.0
    
    def test_backward_pass_multiplication(self):
        """Test backward pass through multiplication."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("input2", "input", value=3.0)
        neural.add_operation("mult1", "multiply")
        
        neural.add_edge("input1", "mult1")
        neural.add_edge("input2", "mult1")
        
        neural.compile_graph()
        neural.forward()
        gradients = neural.backward()
        
        # For multiplication: d/dx(x*y) = y, d/dy(x*y) = x
        assert gradients["input1"] == 3.0  # input2's value
        assert gradients["input2"] == 2.0  # input1's value
    
    def test_cycle_detection(self):
        """Test cycle detection in neural graph."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        neural.add_operation("op1", "add")
        neural.add_operation("op2", "add")
        neural.add_operation("op3", "add")
        
        # Create cycle: op1 -> op2 -> op3 -> op1
        neural.add_edge("op1", "op2")
        neural.add_edge("op2", "op3")
        neural.add_edge("op3", "op1")
        
        with pytest.raises(xNodeValueError):
            neural.compile_graph()
    
    def test_ml_workflow_example(self):
        """Test realistic ML workflow example."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Simple neural network: input -> linear -> relu -> linear -> output
        neural.add_operation("input", "input", value=1.0)
        neural.add_operation("hidden", "linear", weight=2.0, bias=0.5)
        neural.add_operation("activation", "relu")
        neural.add_operation("output", "linear", weight=1.5, bias=0.0)
        
        # Connect layers
        neural.add_edge("input", "hidden")
        neural.add_edge("hidden", "activation")
        neural.add_edge("activation", "output")
        
        neural.compile_graph()
        
        # Forward pass
        forward_result = neural.forward()
        
        # Verify computations
        hidden_out = 2.0 * 1.0 + 0.5  # 2.5
        relu_out = max(0.0, hidden_out)  # 2.5
        output_out = 1.5 * relu_out + 0.0  # 3.75
        
        assert forward_result["hidden"] == 2.5
        assert forward_result["activation"] == 2.5
        assert forward_result["output"] == 3.75
        
        # Backward pass
        gradients = neural.backward()
        
        # Check that gradients exist for all operations
        assert "input" in gradients
        assert "hidden" in gradients
        assert "activation" in gradients
        assert "output" in gradients
    
    def test_dynamic_input_values(self):
        """Test changing input values between forward passes."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        neural.add_operation("x", "input", value=0.0)
        neural.add_operation("y", "add")
        neural.add_edge("x", "y")
        
        neural.compile_graph()
        
        # First forward pass
        result1 = neural.forward({"x": 5.0})
        assert result1["y"] == 5.0
        
        # Second forward pass with different input
        result2 = neural.forward({"x": 10.0})
        assert result2["y"] == 10.0
    
    def test_neural_graph_clear(self):
        """Test clearing neural graph."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        neural.add_operation("input1", "input", value=2.0)
        neural.add_operation("add1", "add")
        neural.add_edge("input1", "add1")
        
        assert len(neural.get_operations()) == 2
        
        neural.clear()
        assert len(neural.get_operations()) == 0
        assert len(neural.get_forward_values()) == 0
        assert len(neural.get_gradients()) == 0
    
    def test_neural_graph_non_dict_node(self):
        """Test Neural Graph view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_neural_graph()


class TestHypergraphView:
    """Test Hypergraph behavioral view."""
    
    def test_hypergraph_creation(self):
        """Test creating Hypergraph view from dict node."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        assert len(hg.get_vertices()) == 0
        assert len(hg.get_hyperedges()) == 0
    
    def test_add_vertices(self):
        """Test adding vertices to hypergraph."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        hg.add_vertex("A", "vertex_a")
        hg.add_vertex("B", "vertex_b")
        hg.add_vertex("C", "vertex_c")
        
        vertices = hg.get_vertices()
        assert len(vertices) == 3
        assert vertices["A"] == "vertex_a"
        assert vertices["B"] == "vertex_b"
    
    def test_add_hyperedges(self):
        """Test adding hyperedges connecting multiple vertices."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        # Add vertices
        vertices = ["A", "B", "C", "D"]
        for v in vertices:
            hg.add_vertex(v, f"vertex_{v}")
        
        # Add hyperedges
        hg.add_hyperedge("edge1", ["A", "B"], weight=1.0)
        hg.add_hyperedge("edge2", ["A", "B", "C"], weight=2.0)
        hg.add_hyperedge("edge3", ["B", "C", "D"], weight=1.5)
        
        hyperedges = hg.get_hyperedges()
        assert len(hyperedges) == 3
        
        edge1 = hyperedges["edge1"]
        assert edge1.vertices == ["A", "B"]
        assert edge1.weight == 1.0
        
        edge2 = hyperedges["edge2"]
        assert set(edge2.vertices) == {"A", "B", "C"}
        assert edge2.weight == 2.0
    
    def test_incident_edges(self):
        """Test finding incident edges for vertices."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        # Setup hypergraph
        for v in ["A", "B", "C", "D"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B"])
        hg.add_hyperedge("e2", ["A", "C"])
        hg.add_hyperedge("e3", ["B", "C", "D"])
        
        # Test incident edges
        incident_a = hg.incident_edges("A")
        assert set(incident_a) == {"e1", "e2"}
        
        incident_b = hg.incident_edges("B")
        assert set(incident_b) == {"e1", "e3"}
        
        incident_d = hg.incident_edges("D")
        assert incident_d == ["e3"]
    
    def test_neighbors(self):
        """Test finding neighbors of vertices."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        # Setup hypergraph
        for v in ["A", "B", "C", "D"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B", "C"])  # Triangle
        hg.add_hyperedge("e2", ["C", "D"])       # Edge
        
        # Test neighbors
        neighbors_a = hg.neighbors("A")
        assert neighbors_a == {"B", "C"}
        
        neighbors_c = hg.neighbors("C")
        assert neighbors_c == {"A", "B", "D"}
        
        neighbors_d = hg.neighbors("D")
        assert neighbors_d == {"C"}
    
    def test_degree(self):
        """Test vertex degree calculation."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B"])
        hg.add_hyperedge("e2", ["A", "C"])
        hg.add_hyperedge("e3", ["A", "B", "C"])
        
        # A is in 3 edges, B is in 2 edges, C is in 2 edges
        assert hg.degree("A") == 3
        assert hg.degree("B") == 2
        assert hg.degree("C") == 2
    
    def test_edge_size(self):
        """Test hyperedge size calculation."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C", "D"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("binary", ["A", "B"])
        hg.add_hyperedge("triangle", ["A", "B", "C"])
        hg.add_hyperedge("quad", ["A", "B", "C", "D"])
        
        assert hg.edge_size("binary") == 2
        assert hg.edge_size("triangle") == 3
        assert hg.edge_size("quad") == 4
    
    def test_intersecting_edges(self):
        """Test finding intersecting hyperedges."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C", "D", "E"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B", "C"])
        hg.add_hyperedge("e2", ["B", "C", "D"])  # Intersects e1 at B,C
        hg.add_hyperedge("e3", ["D", "E"])       # Intersects e2 at D
        hg.add_hyperedge("e4", ["E"])            # Doesn't intersect others
        
        intersecting_e1 = hg.find_intersecting_edges("e1")
        assert "e2" in intersecting_e1
        assert "e3" not in intersecting_e1
        assert "e4" not in intersecting_e1
        
        intersecting_e2 = hg.find_intersecting_edges("e2")
        assert "e1" in intersecting_e2
        assert "e3" in intersecting_e2
    
    def test_connected_components(self):
        """Test finding connected components in hypergraph."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        # Create two disconnected components
        for v in ["A", "B", "C", "D", "E", "F"]:
            hg.add_vertex(v)
        
        # Component 1: A-B-C connected via hyperedges
        hg.add_hyperedge("e1", ["A", "B"])
        hg.add_hyperedge("e2", ["B", "C"])
        
        # Component 2: D-E-F connected
        hg.add_hyperedge("e3", ["D", "E", "F"])
        
        components = hg.connected_components()
        assert len(components) == 2
        
        # Check components contain correct vertices
        component_sizes = [len(comp) for comp in components]
        assert sorted(component_sizes) == [3, 3]
        
        # Verify actual vertices in components
        all_vertices = set()
        for comp in components:
            all_vertices.update(comp)
        assert all_vertices == {"A", "B", "C", "D", "E", "F"}
    
    def test_uniform_hypergraph(self):
        """Test uniform hypergraph detection."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C", "D", "E", "F"]:
            hg.add_vertex(v)
        
        # All edges have size 3 (3-uniform)
        hg.add_hyperedge("e1", ["A", "B", "C"])
        hg.add_hyperedge("e2", ["D", "E", "F"])
        
        assert hg.uniform_hypergraph(3) is True
        assert hg.uniform_hypergraph(2) is False
        
        # Add edge of different size
        hg.add_hyperedge("e3", ["A", "D"])
        assert hg.uniform_hypergraph(3) is False
        assert hg.uniform_hypergraph(2) is False
    
    def test_remove_vertex(self):
        """Test removing vertex and incident edges."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C", "D"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B"])
        hg.add_hyperedge("e2", ["A", "C", "D"])
        hg.add_hyperedge("e3", ["B", "C"])
        
        # Remove vertex A (should remove e1 and e2)
        hg.remove_vertex("A")
        
        vertices = hg.get_vertices()
        assert "A" not in vertices
        assert len(vertices) == 3
        
        hyperedges = hg.get_hyperedges()
        assert "e1" not in hyperedges
        assert "e2" not in hyperedges
        assert "e3" in hyperedges  # Should remain
    
    def test_remove_hyperedge(self):
        """Test removing hyperedge."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B"])
        hg.add_hyperedge("e2", ["A", "B", "C"])
        
        # Remove hyperedge e1
        hg.remove_hyperedge("e1")
        
        hyperedges = hg.get_hyperedges()
        assert "e1" not in hyperedges
        assert "e2" in hyperedges
        
        # Check incident edges updated
        incident_a = hg.incident_edges("A")
        assert "e1" not in incident_a
        assert "e2" in incident_a
    
    def test_hypergraph_statistics(self):
        """Test hypergraph statistics calculation."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C", "D"]:
            hg.add_vertex(v)
        
        hg.add_hyperedge("e1", ["A", "B"])         # Size 2
        hg.add_hyperedge("e2", ["A", "B", "C"])    # Size 3
        hg.add_hyperedge("e3", ["C", "D"])         # Size 2
        
        stats = hg.statistics()
        
        assert stats["vertices"] == 4
        assert stats["hyperedges"] == 3
        assert stats["avg_edge_size"] == (2 + 3 + 2) / 3  # 2.33...
        assert stats["max_edge_size"] == 3
        assert stats["min_edge_size"] == 2
        
        # Vertex degrees: A=2, B=2, C=2, D=1
        assert stats["max_vertex_degree"] == 2
        assert stats["min_vertex_degree"] == 1
        assert stats["avg_vertex_degree"] == (2 + 2 + 2 + 1) / 4  # 1.75
    
    def test_social_network_example(self):
        """Test realistic social network hypergraph example."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        # People
        people = ["Alice", "Bob", "Carol", "David", "Eve"]
        for person in people:
            hg.add_vertex(person, f"Person: {person}")
        
        # Social groups (hyperedges)
        hg.add_hyperedge("work_team", ["Alice", "Bob", "Carol"], team_type="work")
        hg.add_hyperedge("study_group", ["Bob", "David", "Eve"], subject="ML")
        hg.add_hyperedge("family", ["Alice", "Carol"], relation="sisters")
        hg.add_hyperedge("book_club", ["Carol", "David"], hobby="reading")
        
        # Analyze social network
        
        # Who has the most social connections?
        degrees = {person: hg.degree(person) for person in people}
        most_social = max(degrees, key=degrees.get)
        assert most_social in ["Bob", "Carol"]  # Both have degree 2
        
        # Who are Bob's social contacts?
        bob_contacts = hg.neighbors("Bob")
        assert bob_contacts == {"Alice", "Carol", "David", "Eve"}
        
        # What groups is Carol in?
        carol_groups = hg.incident_edges("Carol")
        assert set(carol_groups) == {"work_team", "family", "book_club"}
        
        # Are all people in one connected social network?
        components = hg.connected_components()
        assert len(components) == 1  # Everyone is connected
        assert components[0] == set(people)
    
    def test_hypergraph_clear(self):
        """Test clearing hypergraph."""
        node = xNode.from_native({})
        hg = node.as_hypergraph()
        
        for v in ["A", "B", "C"]:
            hg.add_vertex(v)
        hg.add_hyperedge("e1", ["A", "B", "C"])
        
        assert len(hg.get_vertices()) == 3
        assert len(hg.get_hyperedges()) == 1
        
        hg.clear()
        assert len(hg.get_vertices()) == 0
        assert len(hg.get_hyperedges()) == 0
    
    def test_hypergraph_non_dict_node(self):
        """Test Hypergraph view with non-dict node."""
        node = xNode.from_native([1, 2, 3])
        
        with pytest.raises(xNodeTypeError):
            node.as_hypergraph()


class TestPhase4Integration:
    """Test integration of Phase 4 structures with existing features."""
    
    def test_structure_info_phase4(self):
        """Test structure info includes Phase 4 capabilities."""
        # Dict node should support all Phase 4 structures
        dict_node = xNode.from_native({})
        info = dict_node.structure_info()
        
        supports = info["supports"]
        assert supports["neural_graph"] is True
        assert supports["hypergraph"] is True
        
        # List node should not support Phase 4 structures
        list_node = xNode.from_native([])
        info = list_node.structure_info()
        
        supports = info["supports"]
        assert supports["neural_graph"] is False
        assert supports["hypergraph"] is False
    
    def test_ml_pipeline_workflow(self):
        """Test complete ML pipeline using multiple Phase 4 structures."""
        # Scenario: ML workflow with neural computation and hypergraph relationships
        
        # 1. Build neural network for feature processing
        neural_node = xNode.from_native({})
        neural = neural_node.as_neural_graph()
        
        # Feature extraction network
        neural.add_operation("feature1", "input", value=0.8)
        neural.add_operation("feature2", "input", value=0.6)
        neural.add_operation("feature3", "input", value=0.9)
        
        # Hidden layer
        neural.add_operation("hidden1", "linear", weight=1.2, bias=0.1)
        neural.add_operation("hidden2", "linear", weight=0.8, bias=0.2)
        neural.add_operation("activation1", "relu")
        neural.add_operation("activation2", "relu")
        
        # Output layer
        neural.add_operation("output", "add")
        
        # Connect network
        neural.add_edge("feature1", "hidden1")
        neural.add_edge("feature2", "hidden1")
        neural.add_edge("feature3", "hidden2")
        neural.add_edge("hidden1", "activation1")
        neural.add_edge("hidden2", "activation2")
        neural.add_edge("activation1", "output")
        neural.add_edge("activation2", "output")
        
        neural.compile_graph()
        neural_result = neural.forward()
        
        # Verify neural computation
        hidden1_out = 1.2 * (0.8 + 0.6) + 0.1  # 1.78
        hidden2_out = 0.8 * 0.9 + 0.2  # 0.92
        activation1_out = max(0, hidden1_out)  # 1.78
        activation2_out = max(0, hidden2_out)  # 0.92
        output_result = activation1_out + activation2_out  # 2.7
        
        assert abs(neural_result["output"] - output_result) < 1e-6
        
        # 2. Model relationships using hypergraph
        relationship_node = xNode.from_native({})
        relations = relationship_node.as_hypergraph()
        
        # Add entities
        entities = ["user1", "user2", "user3", "item1", "item2", "session1"]
        for entity in entities:
            relations.add_vertex(entity, f"entity_{entity}")
        
        # Model complex relationships
        relations.add_hyperedge("interaction1", ["user1", "item1", "session1"], 
                               interaction_type="purchase")
        relations.add_hyperedge("interaction2", ["user2", "item1", "session1"], 
                               interaction_type="view")
        relations.add_hyperedge("similarity", ["user1", "user2"], 
                               similarity_score=0.85)
        relations.add_hyperedge("co_occurrence", ["item1", "item2"], 
                                frequency=12)
        
        # Analyze relationships
        user1_neighbors = relations.neighbors("user1")
        assert "item1" in user1_neighbors
        assert "session1" in user1_neighbors
        assert "user2" in user1_neighbors
        
        item1_incident = relations.incident_edges("item1")
        assert "interaction1" in item1_incident
        assert "interaction2" in item1_incident
        assert "co_occurrence" in item1_incident
        
        # Check connectivity
        components = relations.connected_components()
        assert len(components) == 1  # All entities connected
        
        # 3. Integration verification
        assert len(neural.get_operations()) > 0
        assert len(relations.get_vertices()) > 0
        assert neural_result["output"] > 0
        assert len(user1_neighbors) > 0
    
    def test_computational_graph_analysis(self):
        """Test computational graph analysis capabilities."""
        node = xNode.from_native({})
        neural = node.as_neural_graph()
        
        # Build analysis network
        operations = ["data_input", "preprocessing", "feature_extraction", 
                     "model_inference", "postprocessing", "output"]
        
        for i, op in enumerate(operations):
            if i == 0:
                neural.add_operation(op, "input", value=1.0)
            else:
                neural.add_operation(op, "linear", weight=1.1, bias=0.0)
        
        # Create pipeline
        for i in range(len(operations) - 1):
            neural.add_edge(operations[i], operations[i + 1])
        
        neural.compile_graph()
        
        # Analyze computational complexity
        ops_count = len(neural.get_operations())
        assert ops_count == 6
        
        # Forward pass
        result = neural.forward()
        
        # Check pipeline execution
        assert result["data_input"] == 1.0
        assert result["output"] > 1.0  # Should be amplified through pipeline
        
        # Backward pass for gradient analysis
        gradients = neural.backward()
        
        # All operations should have gradients
        assert len(gradients) == ops_count
        assert all(grad != 0 for grad in gradients.values())
    
    def test_performance_characteristics_phase4(self):
        """Test performance characteristics of Phase 4 structures."""
        import time
        
        # Test Neural Graph performance
        neural_node = xNode.from_native({})
        neural = neural_node.as_neural_graph()
        
        start_time = time.time()
        
        # Create larger neural network
        n_inputs = 20
        n_hidden = 10
        
        # Input layer
        for i in range(n_inputs):
            neural.add_operation(f"input_{i}", "input", value=float(i) * 0.1)
        
        # Hidden layer
        for i in range(n_hidden):
            neural.add_operation(f"hidden_{i}", "linear", weight=1.0, bias=0.0)
            neural.add_operation(f"relu_{i}", "relu")
            
            # Connect to some inputs
            for j in range(0, n_inputs, 2):  # Connect to every other input
                neural.add_edge(f"input_{j}", f"hidden_{i}")
            
            neural.add_edge(f"hidden_{i}", f"relu_{i}")
        
        # Output layer
        neural.add_operation("output", "add")
        for i in range(n_hidden):
            neural.add_edge(f"relu_{i}", "output")
        
        # Compile and execute
        neural.compile_graph()
        forward_result = neural.forward()
        backward_result = neural.backward()
        
        neural_time = time.time() - start_time
        
        # Test Hypergraph performance
        hg_node = xNode.from_native({})
        hg = hg_node.as_hypergraph()
        
        start_time = time.time()
        
        # Create larger hypergraph
        n_vertices = 50
        n_edges = 25
        
        # Add vertices
        for i in range(n_vertices):
            hg.add_vertex(f"v_{i}", f"vertex_{i}")
        
        # Add hyperedges with random connectivity
        import random
        random.seed(42)  # For reproducible results
        
        for i in range(n_edges):
            # Each edge connects 2-5 vertices
            edge_size = random.randint(2, 5)
            vertices = [f"v_{j}" for j in random.sample(range(n_vertices), edge_size)]
            hg.add_hyperedge(f"e_{i}", vertices, weight=random.uniform(0.5, 2.0))
        
        # Analyze hypergraph
        components = hg.connected_components()
        stats = hg.statistics()
        
        # Find high-degree vertices
        high_degree_vertices = []
        for i in range(n_vertices):
            if hg.degree(f"v_{i}") >= 3:
                high_degree_vertices.append(f"v_{i}")
        
        hg_time = time.time() - start_time
        
        # Performance assertions
        assert neural_time < 2.0  # Neural graph operations should be fast
        assert hg_time < 2.0      # Hypergraph operations should be fast
        
        assert len(forward_result) > n_inputs  # All operations executed
        assert len(backward_result) > n_inputs  # All gradients computed
        assert len(components) >= 1           # At least one component
        assert stats["vertices"] == n_vertices
        assert stats["hyperedges"] == n_edges
        
        print(f"Performance results:")
        print(f"  Neural Graph ({n_inputs} inputs, {n_hidden} hidden): {neural_time:.4f}s")
        print(f"  Hypergraph ({n_vertices} vertices, {n_edges} edges): {hg_time:.4f}s")
        print(f"  High-degree vertices: {len(high_degree_vertices)}")
        print(f"  Connected components: {len(components)}")
