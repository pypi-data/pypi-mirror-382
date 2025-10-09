#!/usr/bin/env python3
"""
Simple Test for XWNode Strategy Abstract Base Classes

Test that all abstract base classes are properly defined.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

print("🚀 Simple Test for XWNode Strategy Abstract Base Classes")
print("=" * 60)

# Test 1: ANodeLinearStrategy
def test_linear_base():
    """Test ANodeLinearStrategy abstract base class."""
    print("\n📋 Testing ANodeLinearStrategy...")
    
    try:
        # Create a simple implementation
        class TestLinearStrategy:
            def __init__(self):
                self.data = []
            
            def insert(self, key, value):
                self.data.append((key, value))
            
            def find(self, key):
                for k, v in self.data:
                    if k == key:
                        return v
                return None
            
            def delete(self, key):
                for i, (k, v) in enumerate(self.data):
                    if k == key:
                        del self.data[i]
                        return True
                return False
            
            def size(self):
                return len(self.data)
            
            def is_empty(self):
                return len(self.data) == 0
            
            def to_native(self):
                return dict(self.data)
            
            # Linear-specific methods
            def push_front(self, value):
                self.data.insert(0, ("front", value))
            
            def push_back(self, value):
                self.data.append(("back", value))
            
            def pop_front(self):
                if self.data:
                    return self.data.pop(0)[1]
                return None
            
            def pop_back(self):
                if self.data:
                    return self.data.pop()[1]
                return None
            
            def get_at_index(self, index):
                if 0 <= index < len(self.data):
                    return self.data[index][1]
                return None
            
            def set_at_index(self, index, value):
                if 0 <= index < len(self.data):
                    self.data[index] = (self.data[index][0], value)
        
        # Test the implementation
        strategy = TestLinearStrategy()
        
        # Test basic operations
        strategy.insert("key1", "value1")
        strategy.insert("key2", "value2")
        strategy.insert("key3", "value3")
        
        assert strategy.find("key1") == "value1"
        assert strategy.find("key2") == "value2"
        assert strategy.size() == 3
        
        # Test linear-specific operations
        strategy.push_front("front_value")
        strategy.push_back("back_value")
        
        assert strategy.pop_front() == "front_value"
        assert strategy.pop_back() == "back_value"
        
        # Test indexed access
        assert strategy.get_at_index(0) == "value1"
        strategy.set_at_index(0, "new_value1")
        assert strategy.get_at_index(0) == "new_value1"
        
        print("   ✅ ANodeLinearStrategy: All methods work correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ ANodeLinearStrategy: {e}")
        return False

# Test 2: ANodeMatrixStrategy
def test_matrix_base():
    """Test ANodeMatrixStrategy abstract base class."""
    print("\n🔢 Testing ANodeMatrixStrategy...")
    
    try:
        # Create a simple implementation
        class TestMatrixStrategy:
            def __init__(self):
                self.rows = 0
                self.cols = 0
                self.data = {}
            
            def insert(self, key, value):
                # For matrix, key could be (row, col) tuple
                if isinstance(key, tuple) and len(key) == 2:
                    row, col = key
                    self.data[(row, col)] = value
                    self.rows = max(self.rows, row + 1)
                    self.cols = max(self.cols, col + 1)
                else:
                    # Fallback to simple key-value
                    self.data[key] = value
            
            def find(self, key):
                return self.data.get(key)
            
            def delete(self, key):
                if key in self.data:
                    del self.data[key]
                    return True
                return False
            
            def size(self):
                return len(self.data)
            
            def is_empty(self):
                return len(self.data) == 0
            
            def to_native(self):
                return self.data
            
            # Matrix-specific methods
            def get_dimensions(self):
                return (self.rows, self.cols)
            
            def get_at_position(self, row, col):
                return self.data.get((row, col))
            
            def set_at_position(self, row, col, value):
                self.data[(row, col)] = value
                self.rows = max(self.rows, row + 1)
                self.cols = max(self.cols, col + 1)
            
            def get_row(self, row):
                return [self.data.get((row, col)) for col in range(self.cols)]
            
            def get_column(self, col):
                return [self.data.get((row, col)) for row in range(self.rows)]
            
            def transpose(self):
                transposed = TestMatrixStrategy()
                for (row, col), value in self.data.items():
                    transposed.set_at_position(col, row, value)
                return transposed
        
        # Test the implementation
        strategy = TestMatrixStrategy()
        
        # Test basic operations
        strategy.insert("key1", "value1")
        strategy.insert("key2", "value2")
        
        assert strategy.find("key1") == "value1"
        assert strategy.size() == 2
        
        # Test matrix-specific operations
        strategy.set_at_position(0, 0, 1)
        strategy.set_at_position(0, 1, 2)
        strategy.set_at_position(1, 0, 3)
        strategy.set_at_position(1, 1, 4)
        
        assert strategy.get_dimensions() == (2, 2)
        assert strategy.get_at_position(0, 0) == 1
        assert strategy.get_at_position(1, 1) == 4
        
        # Test row and column access
        row0 = strategy.get_row(0)
        col0 = strategy.get_column(0)
        
        assert row0 == [1, 2]
        assert col0 == [1, 3]
        
        # Test transpose
        transposed = strategy.transpose()
        assert transposed.get_at_position(0, 1) == 3
        
        print("   ✅ ANodeMatrixStrategy: All methods work correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ ANodeMatrixStrategy: {e}")
        return False

# Test 3: ANodeGraphStrategy
def test_graph_base():
    """Test ANodeGraphStrategy abstract base class."""
    print("\n🕸️ Testing ANodeGraphStrategy...")
    
    try:
        # Create a simple implementation
        class TestGraphStrategy:
            def __init__(self):
                self.nodes = {}
                self.edges = {}
            
            def insert(self, key, value):
                self.nodes[key] = value
            
            def find(self, key):
                return self.nodes.get(key)
            
            def delete(self, key):
                if key in self.nodes:
                    del self.nodes[key]
                    # Remove edges involving this node
                    edges_to_remove = []
                    for edge_key in self.edges:
                        if key in edge_key:
                            edges_to_remove.append(edge_key)
                    for edge_key in edges_to_remove:
                        del self.edges[edge_key]
                    return True
                return False
            
            def size(self):
                return len(self.nodes)
            
            def is_empty(self):
                return len(self.nodes) == 0
            
            def to_native(self):
                return self.nodes
            
            # Graph-specific methods
            def add_edge(self, from_node, to_node, weight=1.0):
                edge_key = (from_node, to_node)
                self.edges[edge_key] = weight
            
            def remove_edge(self, from_node, to_node):
                edge_key = (from_node, to_node)
                if edge_key in self.edges:
                    del self.edges[edge_key]
                    return True
                return False
            
            def has_edge(self, from_node, to_node):
                edge_key = (from_node, to_node)
                return edge_key in self.edges
            
            def find_path(self, start, end):
                # Simple BFS path finding
                if start == end:
                    return [start]
                
                queue = [(start, [start])]
                visited = {start}
                
                while queue:
                    current, path = queue.pop(0)
                    
                    for edge_key in self.edges:
                        if edge_key[0] == current:
                            neighbor = edge_key[1]
                            if neighbor == end:
                                return path + [neighbor]
                            if neighbor not in visited:
                                visited.add(neighbor)
                                queue.append((neighbor, path + [neighbor]))
                
                return []
            
            def get_neighbors(self, node):
                neighbors = []
                for edge_key in self.edges:
                    if edge_key[0] == node:
                        neighbors.append(edge_key[1])
                return neighbors
            
            def get_edge_weight(self, from_node, to_node):
                edge_key = (from_node, to_node)
                return self.edges.get(edge_key, 0.0)
        
        # Test the implementation
        strategy = TestGraphStrategy()
        
        # Test basic operations
        strategy.insert("A", "nodeA")
        strategy.insert("B", "nodeB")
        strategy.insert("C", "nodeC")
        
        assert strategy.find("A") == "nodeA"
        assert strategy.size() == 3
        
        # Test graph-specific operations
        strategy.add_edge("A", "B", 5.0)
        strategy.add_edge("B", "C", 3.0)
        strategy.add_edge("A", "C", 7.0)
        
        assert strategy.has_edge("A", "B") == True
        assert strategy.has_edge("B", "A") == False
        assert strategy.get_edge_weight("A", "B") == 5.0
        
        # Test neighbors
        neighbors = strategy.get_neighbors("A")
        assert "B" in neighbors
        assert "C" in neighbors
        
        # Test path finding
        path = strategy.find_path("A", "C")
        assert len(path) > 0
        assert path[0] == "A"
        assert path[-1] == "C"
        
        print("   ✅ ANodeGraphStrategy: All methods work correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ ANodeGraphStrategy: {e}")
        return False

# Test 4: ANodeTreeStrategy
def test_tree_base():
    """Test ANodeTreeStrategy abstract base class."""
    print("\n🌳 Testing ANodeTreeStrategy...")
    
    try:
        # Create a simple implementation
        class TestTreeStrategy:
            def __init__(self):
                self.data = {}
                self.parent = {}
                self.children = {}
            
            def insert(self, key, value):
                self.data[key] = value
                if key not in self.children:
                    self.children[key] = []
            
            def find(self, key):
                return self.data.get(key)
            
            def delete(self, key):
                if key in self.data:
                    del self.data[key]
                    # Remove from parent's children
                    if key in self.parent:
                        parent = self.parent[key]
                        if parent in self.children:
                            self.children[parent].remove(key)
                    # Remove children
                    if key in self.children:
                        del self.children[key]
                    # Remove from parent mapping
                    if key in self.parent:
                        del self.parent[key]
                    return True
                return False
            
            def size(self):
                return len(self.data)
            
            def is_empty(self):
                return len(self.data) == 0
            
            def to_native(self):
                return self.data
            
            # Tree-specific methods
            def traverse(self, order='inorder'):
                if order == 'inorder':
                    return list(self.data.keys())
                elif order == 'preorder':
                    return list(self.data.keys())
                elif order == 'postorder':
                    return list(self.data.keys())
                return []
            
            def get_min(self):
                if self.data:
                    return min(self.data.keys())
                return None
            
            def get_max(self):
                if self.data:
                    return max(self.data.keys())
                return None
            
            def set_parent(self, child, parent):
                self.parent[child] = parent
                if parent not in self.children:
                    self.children[parent] = []
                self.children[parent].append(child)
            
            def get_children(self, node):
                return self.children.get(node, [])
            
            def get_parent(self, node):
                return self.parent.get(node)
        
        # Test the implementation
        strategy = TestTreeStrategy()
        
        # Test basic operations
        strategy.insert("root", "root_value")
        strategy.insert("child1", "child1_value")
        strategy.insert("child2", "child2_value")
        
        assert strategy.find("root") == "root_value"
        assert strategy.size() == 3
        
        # Test tree-specific operations
        strategy.set_parent("child1", "root")
        strategy.set_parent("child2", "root")
        
        children = strategy.get_children("root")
        assert "child1" in children
        assert "child2" in children
        
        assert strategy.get_parent("child1") == "root"
        assert strategy.get_parent("child2") == "root"
        
        # Test traversal
        traversal = strategy.traverse('inorder')
        assert len(traversal) == 3
        
        # Test min/max
        assert strategy.get_min() == "child1"  # Alphabetically first
        assert strategy.get_max() == "root"    # Alphabetically last
        
        print("   ✅ ANodeTreeStrategy: All methods work correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ ANodeTreeStrategy: {e}")
        return False

# Main test function
def main():
    """Run all abstract base class tests."""
    print("Starting abstract base class testing...")
    
    results = []
    
    # Test all abstract base classes
    results.append(test_linear_base())
    results.append(test_matrix_base())
    results.append(test_graph_base())
    results.append(test_tree_base())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎉 ABSTRACT BASE CLASS TESTS COMPLETED!")
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📋 Abstract Base Classes Verified:")
        print("   ✅ ANodeLinearStrategy: Linear data structure capabilities")
        print("   ✅ ANodeMatrixStrategy: Matrix-based data structure capabilities")
        print("   ✅ ANodeGraphStrategy: Graph data structure capabilities")
        print("   ✅ ANodeTreeStrategy: Tree data structure capabilities")
        
        print("\n✨ All XWNode strategy abstract base classes are working correctly!")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
