#!/usr/bin/env python3
"""
JSON Query Strategy

This module implements the JSON Query strategy for generic JSON operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from typing import Any, Dict, List, Optional
from .base import ADocumentQueryStrategy
from ...errors import XWNodeValueError
from ...contracts import QueryMode, QueryTrait


class JSONQueryStrategy(ADocumentQueryStrategy):
    """JSON Query strategy for generic JSON operations."""
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.JSON_QUERY
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute JSON query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid JSON query: {query}")
        return {"result": "JSON query executed", "query": query}
    
    def validate_query(self, query: str) -> bool:
        """Validate JSON query syntax."""
        if not query or not isinstance(query, str):
            return False
        return any(op in query for op in ["$", ".", "[", "]", "?", ":", "{", "}"])
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get JSON query execution plan."""
        return {
            "query_type": "JSON_QUERY",
            "complexity": "MEDIUM",
            "estimated_cost": 50
        }
    
    def path_query(self, path: str) -> Any:
        """Execute path-based query."""
        return self.execute(f"$.{path}")
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        return self.execute(f"$[?{filter_expression}]")
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        return self.execute(f"$[{', '.join(fields)}]")
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        return self.execute(f"$[sort by {sort_fields[0]}]")
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        return self.execute(f"$[{offset}:{offset + limit}]")
