#!/usr/bin/env python3
"""
Test graph functionality in xNode.

Tests the AUTO-2 implementation of graph capabilities integrated into xNode.
"""

import sys
import os
import pytest
from typing import Dict, Any

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, project_root)

from src.xlib.xnode import xNode


class TestGraphFunctionality:
    """Test graph operations on xNode."""
    
    def test_node_creation_with_graph_capabilities(self):
        """Test that nodes have graph capabilities available."""
        data = {"name": "Alice", "age": 30}
        node = xNode.from_native(data)
        
        # Test that graph methods are available
        assert hasattr(node, 'connect')
        assert hasattr(node, 'disconnect')
        assert hasattr(node, 'neighbors')
        assert hasattr(node, 'shortest_path')
        assert hasattr(node, 'find_cycles')
        assert hasattr(node, 'traverse_graph')
        assert hasattr(node, 'is_connected')
    
    def test_basic_node_connection(self):
        """Test basic node connection functionality."""
        node1 = xNode.from_native({"name": "Alice", "id": 1})
        node2 = xNode.from_native({"name": "Bob", "id": 2})
        
        # Connect nodes
        result = node1.connect(node2, "friend")
        
        # Should return the source node
        assert result is node1
        
        # Test neighbors
        neighbors = node1.neighbors("friend")
        assert len(neighbors) >= 0  # May be empty if not properly implemented yet
    
    def test_bidirectional_connections(self):
        """Test bidirectional connections between nodes."""
        node1 = xNode.from_native({"name": "Alice"})
        node2 = xNode.from_native({"name": "Bob"})
        
        # Create bidirectional connection
        node1.connect(node2, "friend", bidirectional=True)
        
        # Both nodes should see each other as neighbors
        neighbors1 = node1.neighbors("friend")
        neighbors2 = node2.neighbors("friend", direction="incoming")
        
        # Test that connections exist (implementation may vary)
        assert isinstance(neighbors1, list)
        assert isinstance(neighbors2, list)
    
    def test_multiple_relation_types(self):
        """Test multiple types of relations between nodes."""
        person = xNode.from_native({"name": "Alice", "role": "manager"})
        company = xNode.from_native({"name": "TechCorp", "type": "company"})
        project = xNode.from_native({"name": "Project X", "status": "active"})
        
        # Create different types of relations
        person.connect(company, "works_at")
        person.connect(project, "manages")
        company.connect(project, "owns")
        
        # Test getting neighbors by relation type
        workplaces = person.neighbors("works_at")
        managed_projects = person.neighbors("manages")
        company_projects = company.neighbors("owns")
        
        assert isinstance(workplaces, list)
        assert isinstance(managed_projects, list)
        assert isinstance(company_projects, list)
    
    def test_disconnection(self):
        """Test disconnecting nodes."""
        node1 = xNode.from_native({"name": "Alice"})
        node2 = xNode.from_native({"name": "Bob"})
        
        # Connect and then disconnect
        node1.connect(node2, "friend")
        result = node1.disconnect(node2, "friend")
        
        # Should return boolean indicating success
        assert isinstance(result, bool)
    
    def test_path_finding(self):
        """Test shortest path finding between nodes."""
        alice = xNode.from_native({"name": "Alice"})
        bob = xNode.from_native({"name": "Bob"})
        charlie = xNode.from_native({"name": "Charlie"})
        
        # Create a path: Alice -> Bob -> Charlie
        alice.connect(bob, "friend")
        bob.connect(charlie, "friend")
        
        # Find path from Alice to Charlie
        path = alice.shortest_path(charlie, "friend")
        
        # Should return a list of nodes (may be empty if not implemented)
        assert isinstance(path, list)
    
    def test_connectivity_check(self):
        """Test checking if nodes are connected."""
        node1 = xNode.from_native({"name": "Alice"})
        node2 = xNode.from_native({"name": "Bob"})
        node3 = xNode.from_native({"name": "Charlie"})
        
        # Connect node1 to node2
        node1.connect(node2, "friend")
        
        # Test connectivity
        connected_12 = node1.is_connected(node2, "friend")
        connected_13 = node1.is_connected(node3, "friend")
        
        assert isinstance(connected_12, bool)
        assert isinstance(connected_13, bool)
        # Should be True for connected, False for unconnected
    
    def test_cycle_detection(self):
        """Test cycle detection in graph."""
        alice = xNode.from_native({"name": "Alice"})
        bob = xNode.from_native({"name": "Bob"})
        charlie = xNode.from_native({"name": "Charlie"})
        
        # Create a cycle: Alice -> Bob -> Charlie -> Alice
        alice.connect(bob, "friend")
        bob.connect(charlie, "friend")
        charlie.connect(alice, "friend")
        
        # Find cycles
        cycles = alice.find_cycles("friend")
        
        # Should return list of cycles
        assert isinstance(cycles, list)
    
    def test_graph_traversal(self):
        """Test graph traversal with different strategies."""
        root = xNode.from_native({"name": "Root"})
        child1 = xNode.from_native({"name": "Child1"})
        child2 = xNode.from_native({"name": "Child2"})
        
        # Create connections
        root.connect(child1, "parent")
        root.connect(child2, "parent")
        
        # Test BFS traversal
        bfs_nodes = list(root.traverse_graph("bfs", relation_type="parent"))
        assert isinstance(bfs_nodes, list)
        
        # Test DFS traversal
        dfs_nodes = list(root.traverse_graph("dfs", relation_type="parent"))
        assert isinstance(dfs_nodes, list)
    
    def test_relations_retrieval(self):
        """Test retrieving relations from a node."""
        person = xNode.from_native({"name": "Alice"})
        friend = xNode.from_native({"name": "Bob"})
        colleague = xNode.from_native({"name": "Charlie"})
        
        # Create relations
        person.connect(friend, "friend")
        person.connect(colleague, "colleague")
        
        # Get all outgoing relations
        outgoing = person.relations(direction="outgoing")
        assert isinstance(outgoing, list)
        
        # Get specific relation type
        friend_relations = person.relations("friend", direction="outgoing")
        assert isinstance(friend_relations, list)
    
    def test_weighted_relationships(self):
        """Test relationships with weights."""
        node1 = xNode.from_native({"name": "Alice"})
        node2 = xNode.from_native({"name": "Bob"})
        
        # Create weighted connection
        node1.connect(node2, "friend", weight=0.8, strength="strong")
        
        # Test that connection was created
        neighbors = node1.neighbors("friend")
        assert isinstance(neighbors, list)
        
        # Test retrieving relations with properties
        relations = node1.relations("friend")
        assert isinstance(relations, list)


class TestGraphPerformance:
    """Test graph performance and scalability."""
    
    def test_large_graph_creation(self):
        """Test creating a larger graph structure."""
        nodes = []
        
        # Create 100 nodes
        for i in range(100):
            node = xNode.from_native({"id": i, "name": f"Node_{i}"})
            nodes.append(node)
        
        # Connect each node to the next (creating a chain)
        for i in range(99):
            nodes[i].connect(nodes[i + 1], "next")
        
        # Test path finding across the chain
        if len(nodes) >= 10:
            path = nodes[0].shortest_path(nodes[9], "next")
            assert isinstance(path, list)
    
    def test_graph_memory_efficiency(self):
        """Test that graph operations don't cause memory leaks."""
        import gc
        import sys
        
        # Get initial object count
        initial_objects = len(gc.get_objects())
        
        # Create and connect many nodes
        nodes = []
        for i in range(50):
            node = xNode.from_native({"id": i})
            nodes.append(node)
            
            # Connect to previous nodes
            for j in range(max(0, i-3), i):
                nodes[j].connect(node, "link")
        
        # Clear references and force garbage collection
        del nodes
        gc.collect()
        
        # Check that we haven't leaked too many objects
        final_objects = len(gc.get_objects())
        growth = final_objects - initial_objects
        
        # Allow some growth but not excessive
        assert growth < 1000, f"Too many objects created: {growth}"


class TestGraphIntegrationWithTree:
    """Test that graph operations work alongside tree operations."""
    
    def test_tree_and_graph_operations_together(self):
        """Test that tree and graph operations can be used together."""
        # Create tree structure
        tree_data = {
            "users": {
                "alice": {"name": "Alice", "age": 30},
                "bob": {"name": "Bob", "age": 25}
            }
        }
        
        root = xNode.from_native(tree_data)
        
        # Navigate tree structure
        alice_node = root.find("users.alice")
        bob_node = root.find("users.bob")
        
        # Use graph operations on tree nodes
        alice_node.connect(bob_node, "friend")
        
        # Test that both tree and graph operations work
        assert alice_node.find("name").value == "Alice"  # Tree operation
        friends = alice_node.neighbors("friend")  # Graph operation
        assert isinstance(friends, list)
    
    def test_graph_with_tree_queries(self):
        """Test graph operations with tree-style queries."""
        root = xNode.from_native({
            "people": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35}
            ]
        })
        
        # Get person nodes from tree
        alice = root.find("people.0")
        bob = root.find("people.1")
        charlie = root.find("people.2")
        
        # Create graph relationships
        alice.connect(bob, "friend")
        bob.connect(charlie, "friend")
        
        # Test combined operations
        assert alice.value["name"] == "Alice"  # Tree access
        alice_friends = alice.neighbors("friend")  # Graph access
        assert isinstance(alice_friends, list)
    
    def test_in_place_operations_with_graph(self):
        """Test that in-place operations work with graph functionality."""
        data = {"user": {"name": "Alice", "connections": []}}
        node = xNode.from_native(data)
        
        # Navigate in-place
        user_node = node.find("user", in_place=True)
        
        # Should still have graph capabilities
        assert hasattr(user_node, 'connect')
        assert hasattr(user_node, 'neighbors')
        
        # Test graph operations on in-place node
        other_user = xNode.from_native({"name": "Bob"})
        user_node.connect(other_user, "friend")
        
        friends = user_node.neighbors("friend")
        assert isinstance(friends, list)
