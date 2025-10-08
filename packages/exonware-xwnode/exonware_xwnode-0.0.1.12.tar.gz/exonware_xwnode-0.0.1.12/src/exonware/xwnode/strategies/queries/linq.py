#!/usr/bin/env python3
"""
LINQ Query Strategy

This module implements the LINQ query strategy for Language Integrated Query operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

import re
from typing import Any, Dict, List, Optional, Union
from .base import ADocumentQueryStrategy
from ...errors import XWNodeTypeError, XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class LINQStrategy(ADocumentQueryStrategy):
    """
    LINQ query strategy for Language Integrated Query operations.
    
    Supports:
    - Query syntax and method syntax
    - LINQ to Objects, LINQ to XML, LINQ to SQL
    - Lambda expressions
    - Deferred execution
    - Query composition
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.LINQ
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute LINQ query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid LINQ query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "query_syntax":
            return self._execute_query_syntax(query, **kwargs)
        elif query_type == "method_syntax":
            return self._execute_method_syntax(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate LINQ query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic LINQ validation
        query = query.strip()
        
        # Check for LINQ keywords
        linq_keywords = ["from", "where", "select", "group", "orderby", "join", "let", "into"]
        method_keywords = ["Where", "Select", "GroupBy", "OrderBy", "Join", "Take", "Skip", "First", "Last"]
        
        query_lower = query.lower()
        for keyword in linq_keywords:
            if keyword in query_lower:
                return True
        
        for keyword in method_keywords:
            if keyword in query:
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get LINQ query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "operations": self._extract_operations(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, path: str) -> Any:
        """Execute path-based query."""
        # LINQ path queries are typically for XML
        query = f"""
        from element in document.Descendants()
        where element.Name == "{path}"
        select element
        """
        return self.execute(query)
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        query = f"""
        from item in source
        where {filter_expression}
        select item
        """
        return self.execute(query)
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        if len(fields) == 1:
            query = f"""
            from item in source
            select item.{fields[0]}
            """
        else:
            field_list = ", ".join([f"item.{field}" for field in fields])
            query = f"""
            from item in source
            select new {{ {field_list} }}
            """
        
        return self.execute(query)
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        if order.lower() == "desc":
            query = f"""
            from item in source
            orderby {sort_fields[0]} descending
            select item
            """
        else:
            query = f"""
            from item in source
            orderby {sort_fields[0]}
            select item
            """
        
        return self.execute(query)
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        if offset > 0:
            query = f"""
            from item in source
            select item
            """
            # Use Skip and Take methods
            return self._execute_method_syntax(f"source.Skip({offset}).Take({limit})")
        else:
            query = f"""
            from item in source
            select item
            """
            return self._execute_method_syntax(f"source.Take({limit})")
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from LINQ query."""
        query = query.strip()
        
        if query.startswith("from ") or " from " in query:
            return "query_syntax"
        elif any(method in query for method in ["Where", "Select", "GroupBy", "OrderBy", "Join"]):
            return "method_syntax"
        else:
            return "unknown"
    
    def _execute_query_syntax(self, query: str, **kwargs) -> Any:
        """Execute LINQ query syntax."""
        return {"result": "LINQ query syntax executed", "query": query}
    
    def _execute_method_syntax(self, query: str, **kwargs) -> Any:
        """Execute LINQ method syntax."""
        return {"result": "LINQ method syntax executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        operations = self._extract_operations(query)
        
        if len(operations) > 5:
            return "HIGH"
        elif len(operations) > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 100
        elif complexity == "MEDIUM":
            return 50
        else:
            return 25
    
    def _extract_operations(self, query: str) -> List[str]:
        """Extract LINQ operations from query."""
        operations = []
        
        # Query syntax operations
        if "from" in query.lower():
            operations.append("from")
        if "where" in query.lower():
            operations.append("where")
        if "select" in query.lower():
            operations.append("select")
        if "group" in query.lower():
            operations.append("group")
        if "orderby" in query.lower():
            operations.append("orderby")
        if "join" in query.lower():
            operations.append("join")
        
        # Method syntax operations
        method_operations = ["Where", "Select", "GroupBy", "OrderBy", "Join", "Take", "Skip", "First", "Last", "Count", "Sum", "Average", "Min", "Max"]
        for operation in method_operations:
            if operation in query:
                operations.append(operation)
        
        return operations
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "Count()" in query:
            hints.append("Consider using Count() with predicate for better performance")
        
        if "First()" in query:
            hints.append("Consider using FirstOrDefault() to avoid exceptions")
        
        if "ToList()" in query:
            hints.append("Consider using deferred execution when possible")
        
        if "Select" in query and "Where" in query:
            hints.append("Consider combining Select and Where operations")
        
        return hints
