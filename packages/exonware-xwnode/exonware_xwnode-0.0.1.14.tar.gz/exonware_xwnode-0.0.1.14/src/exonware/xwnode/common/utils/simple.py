"""
Simple node strategy implementation.
"""

from typing import Any, Iterator, Optional, List, Dict, Union
from ..contracts import iNodeStrategy, NodeTrait


class SimpleNodeStrategy(iNodeStrategy):
    """Simple hash map-based node strategy."""
    
    def __init__(self, data: Any = None):
        self._data = data
        self._type = self._determine_type(data)
    
    @classmethod
    def create_from_data(cls, data: Any) -> 'SimpleNodeStrategy':
        """Create a new strategy instance from data."""
        return cls(data)
    
    def _determine_type(self, data: Any) -> str:
        """Determine the type of the data."""
        if isinstance(data, dict):
            return "dict"
        elif isinstance(data, list):
            return "list"
        else:
            return "leaf"
    
    def to_native(self) -> Any:
        """Convert to native Python object."""
        return self._data
    
    def size(self) -> int:
        """Get the number of items."""
        if isinstance(self._data, dict):
            return len(self._data)
        elif isinstance(self._data, list):
            return len(self._data)
        else:
            return 1 if self._data is not None else 0
    
    def is_empty(self) -> bool:
        """Check if the node is empty."""
        if isinstance(self._data, dict):
            return len(self._data) == 0
        elif isinstance(self._data, list):
            return len(self._data) == 0
        else:
            return self._data is None
    
    def insert(self, key: Any, value: Any) -> None:
        """Insert a key-value pair."""
        if isinstance(self._data, dict):
            self._data[key] = value
        elif isinstance(self._data, list):
            if isinstance(key, int):
                self._data[key] = value
            else:
                raise ValueError(f"Cannot insert with non-integer key '{key}' into list")
        else:
            # Convert to dict if it's a leaf node
            self._data = {key: value}
    
    def find(self, key: Any) -> Any:
        """Find a value by key."""
        if isinstance(self._data, dict):
            return self._data.get(key)
        elif isinstance(self._data, list):
            if isinstance(key, int) and 0 <= key < len(self._data):
                return self._data[key]
            else:
                return None
        else:
            return None
    
    def delete(self, key: Any) -> bool:
        """Delete a key-value pair."""
        if isinstance(self._data, dict):
            if key in self._data:
                del self._data[key]
                return True
            return False
        elif isinstance(self._data, list):
            if isinstance(key, int) and 0 <= key < len(self._data):
                del self._data[key]
                return True
            return False
        else:
            return False
    
    def get(self, path: str, default: Any = None) -> Optional['SimpleNodeStrategy']:
        """Get a child node by path."""
        try:
            parts = path.split('.')
            current = self._data
            
            for part in parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
                else:
                    return None
            
            return SimpleNodeStrategy(current)
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def put(self, path: str, value: Any) -> 'SimpleNodeStrategy':
        """Set a value at path."""
        # For simplicity, return a new instance
        new_data = self._data.copy() if isinstance(self._data, (dict, list)) else self._data
        
        try:
            parts = path.split('.')
            current = new_data
            
            for part in parts[:-1]:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
            
            # Set the final value
            final_key = parts[-1]
            if isinstance(current, dict):
                current[final_key] = value
            elif isinstance(current, list):
                current[int(final_key)] = value
        except (KeyError, IndexError, ValueError, TypeError):
            pass
        
        return SimpleNodeStrategy(new_data)
    
    def delete(self, path: str) -> bool:
        """Delete a node at path."""
        try:
            parts = path.split('.')
            current = self._data
            
            for part in parts[:-1]:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
            
            # Delete the final key
            final_key = parts[-1]
            if isinstance(current, dict):
                del current[final_key]
            elif isinstance(current, list):
                current.pop(int(final_key))
            
            return True
        except (KeyError, IndexError, ValueError, TypeError):
            return False
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.get(path) is not None
    
    def keys(self) -> Iterator[str]:
        """Get keys (for dict-like nodes)."""
        if isinstance(self._data, dict):
            yield from self._data.keys()
        elif isinstance(self._data, list):
            yield from (str(i) for i in range(len(self._data)))
    
    def values(self) -> Iterator['SimpleNodeStrategy']:
        """Get values (for dict-like nodes)."""
        if isinstance(self._data, dict):
            for value in self._data.values():
                yield SimpleNodeStrategy(value)
        elif isinstance(self._data, list):
            for value in self._data:
                yield SimpleNodeStrategy(value)
    
    def items(self) -> Iterator[tuple[str, 'SimpleNodeStrategy']]:
        """Get items (for dict-like nodes)."""
        if isinstance(self._data, dict):
            for key, value in self._data.items():
                yield key, SimpleNodeStrategy(value)
        elif isinstance(self._data, list):
            for i, value in enumerate(self._data):
                yield str(i), SimpleNodeStrategy(value)
    
    def __len__(self) -> int:
        """Get length."""
        if hasattr(self._data, '__len__'):
            return len(self._data)
        return 0
    
    def __iter__(self) -> Iterator['SimpleNodeStrategy']:
        """Iterate over children."""
        if isinstance(self._data, (dict, list)):
            for value in self.values():
                yield value
    
    def __getitem__(self, key: Union[str, int]) -> 'SimpleNodeStrategy':
        """Get child by key or index."""
        if isinstance(self._data, dict):
            return SimpleNodeStrategy(self._data[str(key)])
        elif isinstance(self._data, list):
            return SimpleNodeStrategy(self._data[int(key)])
        else:
            raise KeyError(key)
    
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        if isinstance(self._data, dict):
            self._data[str(key)] = value
        elif isinstance(self._data, list):
            self._data[int(key)] = value
    
    def __contains__(self, key: Union[str, int]) -> bool:
        """Check if key exists."""
        try:
            if isinstance(self._data, dict):
                return str(key) in self._data
            elif isinstance(self._data, list):
                idx = int(key)
                return 0 <= idx < len(self._data)
        except (ValueError, TypeError):
            pass
        return False
    
    # Type checking properties
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self._type == "leaf"
    
    @property
    def is_list(self) -> bool:
        """Check if this is a list node."""
        return self._type == "list"
    
    @property
    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        return self._type == "dict"
    
    @property
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        return False
    
    @property
    def is_object(self) -> bool:
        """Check if this is an object node."""
        return False
    
    @property
    def type(self) -> str:
        """Get the type of this node."""
        return self._type
    
    @property
    def value(self) -> Any:
        """Get the value of this node."""
        return self._data
    
    # Strategy information
    @property
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        return "simple"
    
    @property
    def supported_traits(self) -> List[NodeTrait]:
        """Get supported traits for this strategy."""
        return [NodeTrait.NONE]
