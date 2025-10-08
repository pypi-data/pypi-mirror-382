#!/usr/bin/env python3
"""
Cypher Query Strategy

This module implements the Cypher query strategy for Neo4j graph queries.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

import re
from typing import Any, Dict, List, Optional, Union
from .base import AGraphQueryStrategy
from ...errors import XWNodeTypeError, XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class CypherStrategy(AGraphQueryStrategy):
    """
    Cypher query strategy for Neo4j graph queries.
    
    Supports:
    - Cypher query language
    - MATCH, CREATE, MERGE, DELETE operations
    - WHERE clauses and conditions
    - RETURN and WITH clauses
    - Path expressions and patterns
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.CYPHER
        self._traits = QueryTrait.GRAPH | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute Cypher query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid Cypher query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "MATCH":
            return self._execute_match(query, **kwargs)
        elif query_type == "CREATE":
            return self._execute_create(query, **kwargs)
        elif query_type == "MERGE":
            return self._execute_merge(query, **kwargs)
        elif query_type == "DELETE":
            return self._execute_delete(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate Cypher query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic Cypher validation
        query = query.strip().upper()
        valid_operations = ["MATCH", "CREATE", "MERGE", "DELETE", "SET", "REMOVE", "RETURN", "WITH", "UNWIND", "CALL", "LOAD", "USING"]
        
        for operation in valid_operations:
            if query.startswith(operation):
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get Cypher query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "patterns": self._extract_patterns(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute path query."""
        query = f"MATCH p = (start {{id: '{start}'}})-[*]->(end {{id: '{end}'}}) RETURN p"
        return self.execute(query)
    
    def neighbor_query(self, node: Any) -> List[Any]:
        """Execute neighbor query."""
        query = f"MATCH (n {{id: '{node}'}})-[r]-(neighbor) RETURN neighbor"
        return self.execute(query)
    
    def shortest_path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute shortest path query."""
        query = f"MATCH p = shortestPath((start {{id: '{start}'}})-[*]->(end {{id: '{end}'}})) RETURN p"
        return self.execute(query)
    
    def connected_components_query(self) -> List[List[Any]]:
        """Execute connected components query."""
        query = "MATCH (n) RETURN n, size((n)-[*]-()) as component_size"
        return self.execute(query)
    
    def cycle_detection_query(self) -> List[List[Any]]:
        """Execute cycle detection query."""
        query = "MATCH p = (n)-[r*]->(n) RETURN p"
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from Cypher query."""
        query = query.strip().upper()
        for operation in ["MATCH", "CREATE", "MERGE", "DELETE", "SET", "REMOVE", "RETURN", "WITH", "UNWIND", "CALL", "LOAD", "USING"]:
            if query.startswith(operation):
                return operation
        return "UNKNOWN"
    
    def _execute_match(self, query: str, **kwargs) -> Any:
        """Execute MATCH query."""
        return {"result": "Cypher MATCH executed", "query": query}
    
    def _execute_create(self, query: str, **kwargs) -> Any:
        """Execute CREATE query."""
        return {"result": "Cypher CREATE executed", "query": query}
    
    def _execute_merge(self, query: str, **kwargs) -> Any:
        """Execute MERGE query."""
        return {"result": "Cypher MERGE executed", "query": query}
    
    def _execute_delete(self, query: str, **kwargs) -> Any:
        """Execute DELETE query."""
        return {"result": "Cypher DELETE executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        patterns = self._extract_patterns(query)
        
        if len(patterns) > 5:
            return "HIGH"
        elif len(patterns) > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 160
        elif complexity == "MEDIUM":
            return 80
        else:
            return 40
    
    def _extract_patterns(self, query: str) -> List[str]:
        """Extract Cypher patterns from query."""
        patterns = []
        
        # Look for node patterns
        node_patterns = re.findall(r'\([^)]+\)', query)
        patterns.extend(node_patterns)
        
        # Look for relationship patterns
        rel_patterns = re.findall(r'\[[^\]]+\]', query)
        patterns.extend(rel_patterns)
        
        return patterns
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "MATCH" in query.upper() and "WHERE" not in query.upper():
            hints.append("Consider adding WHERE clause to limit results")
        
        if "shortestPath" in query:
            hints.append("Consider using indexes for shortestPath operations")
        
        if "RETURN *" in query.upper():
            hints.append("Consider specifying specific properties instead of using *")
        
        return hints
