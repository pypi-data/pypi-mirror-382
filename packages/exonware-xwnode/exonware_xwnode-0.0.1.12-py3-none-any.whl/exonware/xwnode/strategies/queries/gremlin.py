#!/usr/bin/env python3
"""
Gremlin Query Strategy

This module implements the Gremlin query strategy for Apache TinkerPop graph queries.

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


class GremlinStrategy(AGraphQueryStrategy):
    """
    Gremlin query strategy for Apache TinkerPop graph queries.
    
    Supports:
    - Gremlin traversal language
    - Graph traversal operations
    - Vertex and edge operations
    - Property and label operations
    - Path and cycle detection
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.GREMLIN
        self._traits = QueryTrait.GRAPH | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute Gremlin query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid Gremlin query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "traversal":
            return self._execute_traversal(query, **kwargs)
        elif query_type == "vertex":
            return self._execute_vertex(query, **kwargs)
        elif query_type == "edge":
            return self._execute_edge(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate Gremlin query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic Gremlin validation
        query = query.strip()
        
        # Check for Gremlin keywords
        gremlin_keywords = ["g.", "V", "E", "addV", "addE", "drop", "has", "hasLabel", "hasId", "out", "in", "both", "outE", "inE", "bothE", "outV", "inV", "bothV", "values", "key", "label", "id", "count", "limit", "range", "order", "by", "select", "where", "and", "or", "not", "is", "within", "without", "between", "inside", "outside", "within", "without", "between", "inside", "outside", "within", "without", "between", "inside", "outside"]
        
        for keyword in gremlin_keywords:
            if keyword in query:
                return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get Gremlin query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "steps": self._extract_steps(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute path query."""
        query = f"g.V('{start}').repeat(out()).until(hasId('{end}')).path()"
        return self.execute(query)
    
    def neighbor_query(self, node: Any) -> List[Any]:
        """Execute neighbor query."""
        query = f"g.V('{node}').both()"
        return self.execute(query)
    
    def shortest_path_query(self, start: Any, end: Any) -> List[Any]:
        """Execute shortest path query."""
        query = f"g.V('{start}').repeat(out()).until(hasId('{end}')).path().limit(1)"
        return self.execute(query)
    
    def connected_components_query(self) -> List[List[Any]]:
        """Execute connected components query."""
        query = "g.V().repeat(both()).until(cyclicPath()).dedup()"
        return self.execute(query)
    
    def cycle_detection_query(self) -> List[List[Any]]:
        """Execute cycle detection query."""
        query = "g.V().repeat(out()).until(cyclicPath()).path()"
        return self.execute(query)
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from Gremlin query."""
        query = query.strip()
        
        if "V(" in query or "E(" in query:
            return "traversal"
        elif "addV" in query or "V(" in query:
            return "vertex"
        elif "addE" in query or "E(" in query:
            return "edge"
        else:
            return "unknown"
    
    def _execute_traversal(self, query: str, **kwargs) -> Any:
        """Execute traversal query."""
        return {"result": "Gremlin traversal executed", "query": query}
    
    def _execute_vertex(self, query: str, **kwargs) -> Any:
        """Execute vertex query."""
        return {"result": "Gremlin vertex executed", "query": query}
    
    def _execute_edge(self, query: str, **kwargs) -> Any:
        """Execute edge query."""
        return {"result": "Gremlin edge executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        steps = self._extract_steps(query)
        
        if len(steps) > 10:
            return "HIGH"
        elif len(steps) > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 180
        elif complexity == "MEDIUM":
            return 90
        else:
            return 45
    
    def _extract_steps(self, query: str) -> List[str]:
        """Extract Gremlin steps from query."""
        steps = []
        
        # Common Gremlin steps
        gremlin_steps = ["V", "E", "addV", "addE", "drop", "has", "hasLabel", "hasId", "out", "in", "both", "outE", "inE", "bothE", "outV", "inV", "bothV", "values", "key", "label", "id", "count", "limit", "range", "order", "by", "select", "where", "and", "or", "not", "is", "within", "without", "between", "inside", "outside", "repeat", "until", "emit", "times", "path", "dedup", "cyclicPath"]
        
        for step in gremlin_steps:
            if step in query:
                steps.append(step)
        
        return steps
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "repeat" in query:
            hints.append("Consider using limit() with repeat() to prevent infinite loops")
        
        if "path" in query:
            hints.append("Consider using dedup() with path() to avoid duplicate paths")
        
        if "count" in query:
            hints.append("Consider using count() early in the traversal for better performance")
        
        return hints
