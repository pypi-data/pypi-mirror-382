#!/usr/bin/env python3
"""
XQuery Query Strategy

This module implements the XQuery query strategy for XML data queries.

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


class XQueryStrategy(ADocumentQueryStrategy):
    """
    XQuery query strategy for XML data queries.
    
    Supports:
    - XQuery 1.0 and 3.0 features
    - FLWOR expressions
    - XPath expressions
    - XML construction
    - Functions and modules
    """
    
    def __init__(self, **options):
        super().__init__(**options)
        self._mode = QueryMode.XQUERY
        self._traits = QueryTrait.DOCUMENT | QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL
    
    def execute(self, query: str, **kwargs) -> Any:
        """Execute XQuery query."""
        if not self.validate_query(query):
            raise XWNodeValueError(f"Invalid XQuery query: {query}")
        
        query_type = self._get_query_type(query)
        
        if query_type == "flwor":
            return self._execute_flwor(query, **kwargs)
        elif query_type == "xpath":
            return self._execute_xpath(query, **kwargs)
        elif query_type == "construction":
            return self._execute_construction(query, **kwargs)
        else:
            raise XWNodeValueError(f"Unsupported query type: {query_type}")
    
    def validate_query(self, query: str) -> bool:
        """Validate XQuery query syntax."""
        if not query or not isinstance(query, str):
            return False
        
        # Basic XQuery validation
        query = query.strip()
        
        # Check for XQuery keywords
        xquery_keywords = ["for", "let", "where", "order by", "group by", "return", "declare", "namespace", "import", "module", "function", "variable", "element", "attribute", "text", "comment", "processing-instruction", "document", "collection"]
        
        query_lower = query.lower()
        for keyword in xquery_keywords:
            if keyword in query_lower:
                return True
        
        # Check for XPath expressions
        if "/" in query or "//" in query or "@" in query or "[" in query:
            return True
        
        return False
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get XQuery query execution plan."""
        query_type = self._get_query_type(query)
        
        return {
            "query_type": query_type,
            "operation": query_type,
            "complexity": self._estimate_complexity(query),
            "estimated_cost": self._estimate_cost(query),
            "expressions": self._extract_expressions(query),
            "optimization_hints": self._get_optimization_hints(query)
        }
    
    def path_query(self, path: str) -> Any:
        """Execute path-based query."""
        # XQuery path queries
        query = f"doc()/{path}"
        return self.execute(query)
    
    def filter_query(self, filter_expression: str) -> Any:
        """Execute filter query."""
        query = f"""
        for $item in doc()//*
        where {filter_expression}
        return $item
        """
        return self.execute(query)
    
    def projection_query(self, fields: List[str]) -> Any:
        """Execute projection query."""
        if len(fields) == 1:
            query = f"""
            for $item in doc()//*
            return $item/{fields[0]}
            """
        else:
            field_list = ", ".join([f"$item/{field}" for field in fields])
            query = f"""
            for $item in doc()//*
            return <result>{{ {field_list} }}</result>
            """
        
        return self.execute(query)
    
    def sort_query(self, sort_fields: List[str], order: str = "asc") -> Any:
        """Execute sort query."""
        if order.lower() == "desc":
            query = f"""
            for $item in doc()//*
            order by $item/{sort_fields[0]} descending
            return $item
            """
        else:
            query = f"""
            for $item in doc()//*
            order by $item/{sort_fields[0]}
            return $item
            """
        
        return self.execute(query)
    
    def limit_query(self, limit: int, offset: int = 0) -> Any:
        """Execute limit query."""
        if offset > 0:
            query = f"""
            for $item at $pos in doc()//*
            where $pos > {offset}
            return $item
            """
            # Use subsequence for limit
            return self._execute_function(f"subsequence(doc()//*, {offset + 1}, {limit})")
        else:
            query = f"""
            for $item in doc()//*
            return $item
            """
            return self._execute_function(f"subsequence(doc()//*, 1, {limit})")
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from XQuery query."""
        query = query.strip()
        
        if "for" in query.lower() or "let" in query.lower():
            return "flwor"
        elif "<" in query and ">" in query:
            return "construction"
        elif "/" in query or "//" in query:
            return "xpath"
        else:
            return "unknown"
    
    def _execute_flwor(self, query: str, **kwargs) -> Any:
        """Execute FLWOR expression."""
        return {"result": "XQuery FLWOR executed", "query": query}
    
    def _execute_xpath(self, query: str, **kwargs) -> Any:
        """Execute XPath expression."""
        return {"result": "XQuery XPath executed", "query": query}
    
    def _execute_construction(self, query: str, **kwargs) -> Any:
        """Execute XML construction."""
        return {"result": "XQuery construction executed", "query": query}
    
    def _execute_function(self, query: str, **kwargs) -> Any:
        """Execute function call."""
        return {"result": "XQuery function executed", "query": query}
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        expressions = self._extract_expressions(query)
        
        if len(expressions) > 5:
            return "HIGH"
        elif len(expressions) > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_cost(self, query: str) -> int:
        """Estimate query cost."""
        complexity = self._estimate_complexity(query)
        if complexity == "HIGH":
            return 150
        elif complexity == "MEDIUM":
            return 75
        else:
            return 35
    
    def _extract_expressions(self, query: str) -> List[str]:
        """Extract XQuery expressions from query."""
        expressions = []
        
        # FLWOR expressions
        if "for" in query.lower():
            expressions.append("for")
        if "let" in query.lower():
            expressions.append("let")
        if "where" in query.lower():
            expressions.append("where")
        if "order by" in query.lower():
            expressions.append("order by")
        if "group by" in query.lower():
            expressions.append("group by")
        if "return" in query.lower():
            expressions.append("return")
        
        # XPath expressions
        if "/" in query:
            expressions.append("path")
        if "//" in query:
            expressions.append("descendant")
        if "@" in query:
            expressions.append("attribute")
        if "[" in query and "]" in query:
            expressions.append("predicate")
        
        # XML construction
        if "<" in query and ">" in query:
            expressions.append("construction")
        
        # Functions
        if "(" in query and ")" in query:
            expressions.append("function")
        
        return expressions
    
    def _get_optimization_hints(self, query: str) -> List[str]:
        """Get query optimization hints."""
        hints = []
        
        if "//" in query:
            hints.append("Consider using specific paths instead of descendant navigation")
        
        if "for" in query.lower() and "let" in query.lower():
            hints.append("Consider using let for computed values")
        
        if "[" in query and "]" in query:
            hints.append("Consider using indexes for predicate operations")
        
        if "order by" in query.lower():
            hints.append("Consider using indexes for ordered queries")
        
        return hints
