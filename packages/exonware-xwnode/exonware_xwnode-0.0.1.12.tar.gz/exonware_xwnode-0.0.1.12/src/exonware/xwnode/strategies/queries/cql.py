#!/usr/bin/env python3
"""
CQL Query Strategy

This module implements the CQL query strategy for Cassandra Query Language operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

import re
from typing import Any, Dict, List, Optional, Union
from .base import AStructuredQueryStrategy
from ...errors import XWNodeTypeError, XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class CQLStrategy(AStructuredQueryStrategy):
    """
    CQL query strategy for Cassandra Query Language operations.
    
    Supports:
    - CQL 3.0+ features
    - SELECT, INSERT, UPDATE, DELETE operations
    - CREATE, DROP, ALTER operations
    - Batch operations
    - Time-to-live (TTL) operations
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.CQL
        self._traits = QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL | QueryTrait.BATCH
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute CQL query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid CQL query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "SELECT":
            return self._execute_select(query, **kwargs)
        elif query_type == "INSERT":
            return self._execute_insert(query, **kwargs)
        elif query_type == "UPDATE":
            return self._execute_update(query, **kwargs)
        elif query_type == "DELETE":
            return self._execute_delete(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate CQL query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic CQL validation
        query = query.strip().upper()
        valid_operations = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "USE", "TRUNCATE", "BATCH", "GRANT", "REVOKE", "LIST", "DESCRIBE", "EXPLAIN"]
        
        for operation in valid_operations:
            if query.startswith(operation):
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get CQL query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "operations": self._extract_operations(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def select_query(self, table: str, columns: List[str], where_clause: str = None) -> Any:
        """Execute SELECT query."""
        query = f"SELECT {', '.join(columns)} FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return self.execute(query)
    
    def insert_query(self, table: str, data: Dict[str, Any]) -> Any:
        """Execute INSERT query."""
        columns = list(data.keys())
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})"
        return self.execute(query, values=values)
    
    def update_query(self, table: str, data: Dict[str, Any], where_clause: str = None) -> Any:
        """Execute UPDATE query."""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return self.execute(query, values=list(data.values()))
    
    def delete_query(self, table: str, where_clause: str = None) -> Any:
        """Execute DELETE query."""
        query = f"DELETE FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return self.execute(query)
    
    def join_query(self, tables: List[str], join_conditions: List[str]) -> Any:
        """Execute JOIN query."""
        # CQL doesn't support traditional JOINs, use denormalization
        raise XWNodeValueError("CQL doesn't support JOIN operations. Use denormalization instead.")
    
    def aggregate_query(self, table: str, functions: List[str], group_by: List[str] = None) -> Any:
        """Execute aggregate query."""
        query = f"SELECT {', '.join(functions)} FROM {table}"
        if group_by:
            query += f" GROUP BY {', '.join(group_by)}"
        
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from CQL query."""
        query = query.strip().upper()
        for operation in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "USE", "TRUNCATE", "BATCH", "GRANT", "REVOKE", "LIST", "DESCRIBE", "EXPLAIN"]:
            if query.startswith(operation):
                return operation
        return "UNKNOWN"
    
    def _execute_select(self, query: str, **kwargs) -> Any:
        """Execute SELECT query."""
        return {"result": "CQL SELECT executed", "query": query}
    
    def _execute_insert(self, query: str, **kwargs) -> Any:
        """Execute INSERT query."""
        return {"result": "CQL INSERT executed", "query": query}
    
    def _execute_update(self, query: str, **kwargs) -> Any:
        """Execute UPDATE query."""
        return {"result": "CQL UPDATE executed", "query": query}
    
    def _execute_delete(self, query: str, **kwargs) -> Any:
        """Execute DELETE query."""
        return {"result": "CQL DELETE executed", "query": query}
    
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
            return 120
        elif complexity == "MEDIUM":
            return 60
        else:
            return 30
    
    def _extract_operations(self, query: str) -> List[str]:
        """Extract CQL operations from query."""
        operations = []
        
        cql_operations = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "USE", "TRUNCATE", "BATCH", "GRANT", "REVOKE", "LIST", "DESCRIBE", "EXPLAIN"]
        
        for operation in cql_operations:
            if operation in query.upper():
                operations.append(operation)
        
        return operations
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "SELECT *" in query.upper():
            hints.append("Consider specifying columns instead of using *")
        
        if "WHERE" not in query.upper() and "SELECT" in query.upper():
            hints.append("Consider adding WHERE clause to limit results")
        
        if "ORDER BY" in query.upper():
            hints.append("Consider using clustering columns for ORDER BY operations")
        
        return hints
