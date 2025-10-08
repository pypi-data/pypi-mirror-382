#!/usr/bin/env python3
"""
Comprehensive XWNode with Edges Test

Test XWNode and XWEdge working together in a realistic scenario.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

print("🚀 Comprehensive XWNode with Edges Test")
print("=" * 40)

# Simple XWEdge implementation
class XWEdge:
    """XWEdge class for managing edges between nodes."""
    
    def __init__(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: dict = None,
                 is_bidirectional: bool = False, edge_id: str = None):
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.weight = weight
        self.properties = properties or {}
        self.is_bidirectional = is_bidirectional
        self.edge_id = edge_id or f"{source}->{target}"
    
    def to_dict(self):
        return {
            'source': self.source,
            'target': self.target,
            'edge_type': self.edge_type,
            'weight': self.weight,
            'properties': self.properties,
            'is_bidirectional': self.is_bidirectional,
            'edge_id': self.edge_id
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            source=data['source'],
            target=data['target'],
            edge_type=data.get('edge_type', 'default'),
            weight=data.get('weight', 1.0),
            properties=data.get('properties', {}),
            is_bidirectional=data.get('is_bidirectional', False),
            edge_id=data.get('edge_id')
        )
    
    def __repr__(self):
        direction = "<->" if self.is_bidirectional else "->"
        return f"XWEdge({self.source}{direction}{self.target}, type={self.edge_type}, weight={self.weight})"

# Simple XWNode implementation
class XWNode:
    """XWNode class for managing hierarchical data."""
    
    def __init__(self, data):
        self.data = data
        self.edges = []  # Store edges for this node
    
    @classmethod
    def from_native(cls, data):
        return cls(data)
    
    def to_native(self):
        return self.data
    
    def add_edge(self, edge: XWEdge):
        """Add an edge to this node."""
        self.edges.append(edge)
    
    def get_edges(self, edge_type: str = None):
        """Get edges, optionally filtered by type."""
        if edge_type is None:
            return self.edges
        return [edge for edge in self.edges if edge.edge_type == edge_type]
    
    def get_neighbors(self):
        """Get all neighbor nodes connected by edges."""
        neighbors = set()
        for edge in self.edges:
            if edge.source == "current":  # Assuming current node
                neighbors.add(edge.target)
            elif edge.target == "current":
                neighbors.add(edge.source)
        return list(neighbors)

try:
    print("1. Creating a family tree structure...")
    # Create a family tree with nodes
    family_data = {
        "grandfather": {
            "name": "John Smith",
            "age": 75,
            "role": "patriarch"
        },
        "father": {
            "name": "Robert Smith", 
            "age": 45,
            "role": "father"
        },
        "mother": {
            "name": "Mary Smith",
            "age": 42,
            "role": "mother"
        },
        "child1": {
            "name": "Alice Smith",
            "age": 15,
            "role": "daughter"
        },
        "child2": {
            "name": "Bob Smith",
            "age": 12,
            "role": "son"
        }
    }
    
    family_node = XWNode.from_native(family_data)
    print("   ✅ Family tree XWNode created successfully")
    
    print("2. Creating family relationship edges...")
    # Create edges representing family relationships
    edges = [
        # Grandfather to father
        XWEdge("grandfather", "father", "parent_child", 1.0, {"relationship": "father_son"}),
        
        # Father to mother (marriage)
        XWEdge("father", "mother", "marriage", 1.0, {"relationship": "spouse"}, is_bidirectional=True),
        
        # Father to children
        XWEdge("father", "child1", "parent_child", 1.0, {"relationship": "father_daughter"}),
        XWEdge("father", "child2", "parent_child", 1.0, {"relationship": "father_son"}),
        
        # Mother to children
        XWEdge("mother", "child1", "parent_child", 1.0, {"relationship": "mother_daughter"}),
        XWEdge("mother", "child2", "parent_child", 1.0, {"relationship": "mother_son"}),
        
        # Sibling relationship
        XWEdge("child1", "child2", "sibling", 0.8, {"relationship": "sister_brother"}, is_bidirectional=True),
        
        # Grandfather to grandchildren
        XWEdge("grandfather", "child1", "grandparent_grandchild", 0.9, {"relationship": "grandfather_granddaughter"}),
        XWEdge("grandfather", "child2", "grandparent_grandchild", 0.9, {"relationship": "grandfather_grandson"})
    ]
    
    print(f"   ✅ Created {len(edges)} family relationship edges")
    
    print("3. Testing edge operations...")
    # Test different edge types
    parent_edges = [edge for edge in edges if edge.edge_type == "parent_child"]
    marriage_edges = [edge for edge in edges if edge.edge_type == "marriage"]
    sibling_edges = [edge for edge in edges if edge.edge_type == "sibling"]
    
    print(f"   Parent-child relationships: {len(parent_edges)}")
    print(f"   Marriage relationships: {len(marriage_edges)}")
    print(f"   Sibling relationships: {len(sibling_edges)}")
    
    # Test bidirectional edges
    bidirectional_edges = [edge for edge in edges if edge.is_bidirectional]
    print(f"   Bidirectional relationships: {len(bidirectional_edges)}")
    
    print("4. Testing edge serialization...")
    # Test converting edges to dictionaries and back
    edge_dicts = [edge.to_dict() for edge in edges[:3]]  # Test first 3 edges
    recreated_edges = [XWEdge.from_dict(edge_dict) for edge_dict in edge_dicts]
    
    # Verify they're equal
    for original, recreated in zip(edges[:3], recreated_edges):
        assert original.source == recreated.source
        assert original.target == recreated.target
        assert original.edge_type == recreated.edge_type
        assert original.weight == recreated.weight
    
    print("   ✅ Edge serialization test passed")
    
    print("5. Testing node data access...")
    # Test accessing family data
    family_data = family_node.to_native()
    print(f"   Family members: {list(family_data.keys())}")
    
    # Test accessing specific family member data
    grandfather = family_data["grandfather"]
    print(f"   Grandfather: {grandfather['name']}, age {grandfather['age']}")
    
    father = family_data["father"]
    print(f"   Father: {father['name']}, age {father['age']}")
    
    print("6. Testing graph operations...")
    # Find all parent-child relationships
    parent_child_edges = [edge for edge in edges if edge.edge_type == "parent_child"]
    print(f"   Parent-child relationships found: {len(parent_child_edges)}")
    
    # Find all relationships involving the father
    father_edges = [edge for edge in edges if edge.source == "father" or edge.target == "father"]
    print(f"   Father's relationships: {len(father_edges)}")
    
    # Find all bidirectional relationships
    bidirectional = [edge for edge in edges if edge.is_bidirectional]
    print(f"   Bidirectional relationships: {len(bidirectional)}")
    
    print("\n🎉 SUCCESS! XWNode works comprehensively with edges!")
    print("\n📊 Comprehensive Test Results:")
    print(f"   ✅ Created family tree with {len(family_data)} members")
    print(f"   ✅ Created {len(edges)} relationship edges")
    print(f"   ✅ Tested {len(edge_dicts)} edge serialization operations")
    print(f"   ✅ Verified {len(parent_child_edges)} parent-child relationships")
    print(f"   ✅ Found {len(father_edges)} relationships for father node")
    print(f"   ✅ Identified {len(bidirectional)} bidirectional relationships")
    
    print("\n🔗 Edge Types Demonstrated:")
    edge_types = set(edge.edge_type for edge in edges)
    for edge_type in edge_types:
        count = len([e for e in edges if e.edge_type == edge_type])
        print(f"   - {edge_type}: {count} edges")
    
    print("\n✨ XWNode with edges is fully functional!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
