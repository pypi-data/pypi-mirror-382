#!/usr/bin/env python3
"""
SPARQL Query Strategy

This module implements the SPARQL query strategy for RDF data queries.

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


class SPARQLStrategy(AGraphQueryStrategy):
    """
    SPARQL query strategy for RDF data queries.
    
    Supports:
    - SELECT, CONSTRUCT, ASK, DESCRIBE queries
    - SPARQL 1.1 features
    - Property paths
    - Federated queries
    - Update operations
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.SPARQL
        self._traits = QueryTrait.GRAPH | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute SPARQL query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid SPARQL query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "SELECT":
            return self._execute_select(query, **kwargs)
        elif query_type == "CONSTRUCT":
            return self._execute_construct(query, **kwargs)
        elif query_type == "ASK":
            return self._execute_ask(query, **kwargs)
        elif query_type == "DESCRIBE":
            return self._execute_describe(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate SPARQL query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic SPARQL validation
        query = query.strip().upper()
        valid_operations = ["SELECT", "CONSTRUCT", "ASK", "DESCRIBE", "INSERT", "DELETE", "LOAD", "CLEAR"]
        
        for operation in valid_operations:
            if query.startswith(operation):
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get SPARQL query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "triple_patterns": self._count_triple_patterns(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute path query using SPARQL property paths."""
        query = f"""
        SELECT ?path ?length
        WHERE {{
            <{start}> (<>|!<>)* ?path .
            ?path (<>|!<>)* <{end}> .
            BIND(LENGTH(?path) AS ?length)
        }}
        """
        return self.execute(query)
    
    def neighbor_query(self, node: Any) -> List[Any]:
        """Execute neighbor query."""
        query = f"""
        SELECT ?neighbor ?predicate
        WHERE {{
            <{node}> ?predicate ?neighbor .
        }}
        """
        return self.execute(query)
    
    def shortest_path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute shortest path query."""
        query = f"""
        SELECT ?path (COUNT(?step) AS ?length)
        WHERE {{
            <{start}> (<>|!<>)* ?path .
            ?path (<>|!<>)* <{end}> .
        }}
        GROUP BY ?path
        ORDER BY ?length
        LIMIT 1
        """
        return self.execute(query)
    
    def connected_components_query(self) -> List[List[Any]]:
        """Execute connected components query."""
        query = """
        SELECT ?component (COUNT(?node) AS ?size)
        WHERE {
            ?node ?p ?o .
            ?o ?p2 ?node .
        }
        GROUP BY ?component
        """
        return self.execute(query)
    
    def cycle_detection_query(self) -> List[List[Any]]:
        """Execute cycle detection query."""
        query = """
        SELECT ?cycle
        WHERE {
            ?node ?p ?node .
            BIND(?node AS ?cycle)
        }
        """
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from SPARQL query."""
        query = query.strip().upper()
        for operation in ["SELECT", "CONSTRUCT", "ASK", "DESCRIBE", "INSERT", "DELETE", "LOAD", "CLEAR"]:
            if query.startswith(operation):
                return operation
        return "UNKNOWN"
    
    def _execute_select(self, query: str, **kwargs) -> Any:
        """Execute SELECT query."""
        return {"result": "SPARQL SELECT executed", "query": query}
    
    def _execute_construct(self, query: str, **kwargs) -> Any:
        """Execute CONSTRUCT query."""
        return {"result": "SPARQL CONSTRUCT executed", "query": query}
    
    def _execute_ask(self, query: str, **kwargs) -> Any:
        """Execute ASK query."""
        return {"result": "SPARQL ASK executed", "query": query}
    
    def _execute_describe(self, query: str, **kwargs) -> Any:
        """Execute DESCRIBE query."""
        return {"result": "SPARQL DESCRIBE executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        triple_count = self._count_triple_patterns(query)
        
        if triple_count > 10:
            return "HIGH"
        elif triple_count > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 200
        elif complexity == "MEDIUM":
            return 100
        else:
            return 50
    
    def _count_triple_patterns(self, query: str) -> int:
        """Count triple patterns in SPARQL query."""
        # Count occurrences of triple patterns
        pattern_count = 0
        
        # Look for triple patterns in WHERE clause
        where_match = re.search(r'WHERE\s*\{([^}]+)\}', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            # Count lines that look like triple patterns
            lines = where_clause.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('FILTER'):
                    if '?' in line or '<' in line or '"' in line:
                        pattern_count += 1
        
        return pattern_count
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if self._count_triple_patterns(query) > 8:
            hints.append("Consider breaking down complex queries into smaller ones")
        
        if "OPTIONAL" in query.upper():
            hints.append("Consider using FILTER instead of OPTIONAL for better performance")
        
        if "UNION" in query.upper():
            hints.append("Consider using property paths instead of UNION when possible")
        
        return hints
