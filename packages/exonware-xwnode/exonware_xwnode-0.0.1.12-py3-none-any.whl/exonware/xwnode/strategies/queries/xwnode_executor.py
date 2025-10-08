#!/usr/bin/env python3
"""
XWNode Query Action Executor

This module implements the XWNode query action executor that provides
a unified interface for executing queries across all supported query types
using the existing XWNode strategy system.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.12
Generation Date: January 2, 2025
"""

from typing import Any, Dict, List, Optional, Type
from datetime import datetime

from .base import AQueryActionExecutor
from .xwquery_strategy import XWQueryScriptStrategy
from ...base import XWNodeBase
from ...contracts import QueryMode, QueryTrait
from ...errors import XWNodeTypeError, XWNodeValueError


class XWNodeQueryActionExecutor(AQueryActionExecutor):
    """
    XWNode implementation of query action executor.
    
    This executor provides a unified interface for executing queries across
    all 35+ supported query types using the existing XWNode strategy system.
    """
    
    def __init__(self):
        super().__init__()
        self._mode = QueryMode.AUTO
        self._traits = QueryTrait.STRUCTURED | QueryTrait.ANALYTICAL | QueryTrait.BATCH
        
        # All supported query types from XWNode
        self._supported_queries = [
            # Structured & Document Query Languages
            "SQL", "HIVEQL", "PIG", "CQL", "N1QL", "KQL", "DATALOG", 
            "MQL", "PARTIQL",
            
            # Search Query Languages
            "ELASTIC_DSL", "EQL", "LUCENE",
            
            # Time Series & Monitoring
            "FLUX", "PROMQL",
            
            # Data Streaming
            "KSQL",
            
            # Graph Query Languages
            "GRAPHQL", "SPARQL", "GREMLIN", "CYPHER", "GQL",
            
            # ORM / Integrated Query
            "LINQ", "HQL",
            
            # Markup & Document Structure
            "JSONIQ", "JMESPATH", "JQ", "XQUERY", "XPATH",
            
            # Logs & Analytics
            "LOGQL", "SPL",
            
            # SQL Engines
            "TRINO_SQL", "BIGQUERY_SQL", "SNOWFLAKE_SQL",
            
            # Generic Query Languages
            "XML_QUERY", "JSON_QUERY"
        ]
        
        self._strategy_cache = {}
        self._execution_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "execution_times": []
        }
    
    def execute_query(self, query: str, query_type: str, **kwargs) -> Any:
        """Execute a query using the appropriate XWNode strategy."""
        if not self.validate_query(query, query_type):
            raise XWNodeValueError(f"Invalid {query_type} query: {query}")
        
        start_time = datetime.now()
        self._execution_stats["total_queries"] += 1
        
        try:
            # Get or create strategy instance
            strategy = self._get_strategy(query_type)
            
            # Execute the query
            result = strategy.execute(query, **kwargs)
            
            # Update stats
            execution_time = (datetime.now() - start_time).total_seconds()
            self._execution_stats["successful_queries"] += 1
            self._execution_stats["execution_times"].append(execution_time)
            
            return {
                "result": result,
                "query_type": query_type,
                "execution_time": f"{execution_time:.3f}s",
                "backend": "XWNODE",
                "strategy_used": strategy.__class__.__name__
            }
            
        except Exception as e:
            self._execution_stats["failed_queries"] += 1
            raise XWNodeValueError(f"Query execution failed: {e}")
    
    def validate_query(self, query: str, query_type: str) -> bool:
        """Validate if XWNode can handle this query type."""
        if query_type.upper() not in self._supported_queries:
            return False
        
        try:
            strategy = self._get_strategy(query_type)
            return strategy.validate_query(query)
        except Exception:
            return False
    
    def get_supported_query_types(self) -> List[str]:
        """Get list of query types supported by XWNode."""
        return self._supported_queries.copy()
    
    def _get_strategy(self, query_type: str) -> Any:
        """Get or create strategy instance for query type."""
        query_type_upper = query_type.upper()
        
        if query_type_upper in self._strategy_cache:
            return self._strategy_cache[query_type_upper]
        
        # Import and create strategy instance
        strategy_class = self._get_strategy_class(query_type_upper)
        if not strategy_class:
            raise XWNodeValueError(f"No strategy available for query type: {query_type}")
        
        strategy = strategy_class()
        self._strategy_cache[query_type_upper] = strategy
        return strategy
    
    def _get_strategy_class(self, query_type: str) -> Optional[Type]:
        """Get strategy class for query type."""
        strategy_map = {
            "SQL": "sql",
            "HIVEQL": "hiveql",
            "PIG": "pig",
            "CQL": "cql",
            "N1QL": "n1ql",
            "KQL": "kql",
            "DATALOG": "datalog",
            "MQL": "mql",
            "PARTIQL": "partiql",
            "ELASTIC_DSL": "elastic_dsl",
            "EQL": "eql",
            "LUCENE": "lucene",
            "FLUX": "flux",
            "PROMQL": "promql",
            "KSQL": "ksql",
            "GRAPHQL": "graphql",
            "SPARQL": "sparql",
            "GREMLIN": "gremlin",
            "CYPHER": "cypher",
            "GQL": "gql",
            "LINQ": "linq",
            "HQL": "hql",
            "JSONIQ": "jsoniq",
            "JMESPATH": "jmespath",
            "JQ": "jq",
            "XQUERY": "xquery",
            "XPATH": "xpath",
            "LOGQL": "logql",
            "SPL": "spl",
            "TRINO_SQL": "trino_sql",
            "BIGQUERY_SQL": "bigquery_sql",
            "SNOWFLAKE_SQL": "snowflake_sql",
            "XML_QUERY": "xml_query",
            "JSON_QUERY": "json_query"
        }
        
        module_name = strategy_map.get(query_type)
        if not module_name:
            return None
        
        try:
            module = __import__(f'.{module_name}', fromlist=['.'], package=__package__)
            strategy_class_name = f"{query_type.title()}Strategy"
            return getattr(module, strategy_class_name, None)
        except (ImportError, AttributeError):
            return None
    
    def to_native(self) -> XWQueryScriptStrategy:
        """Convert to XWQueryScriptStrategy using actions."""
        return XWQueryScriptStrategy()
    
    def to_actions_tree(self, query: str) -> XWNodeBase:
        """Convert query to actions tree using XWQuery Script."""
        script_strategy = XWQueryScriptStrategy()
        return script_strategy.parse_script(query).get_actions_tree()
    
    def from_actions_tree(self, actions_tree: XWNodeBase) -> str:
        """Convert actions tree to query using XWQuery Script."""
        script_strategy = XWQueryScriptStrategy(actions_tree)
        return script_strategy.to_format("SQL")  # Default to SQL
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        stats = self._execution_stats.copy()
        
        if stats["execution_times"]:
            stats["avg_execution_time"] = sum(stats["execution_times"]) / len(stats["execution_times"])
            stats["min_execution_time"] = min(stats["execution_times"])
            stats["max_execution_time"] = max(stats["execution_times"])
        else:
            stats["avg_execution_time"] = 0
            stats["min_execution_time"] = 0
            stats["max_execution_time"] = 0
        
        stats["success_rate"] = (
            stats["successful_queries"] / stats["total_queries"] 
            if stats["total_queries"] > 0 else 0
        )
        
        return stats
    
    def clear_cache(self):
        """Clear strategy cache."""
        self._strategy_cache.clear()
    
    def reset_stats(self):
        """Reset execution statistics."""
        self._execution_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "execution_times": []
        }
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get XWNode backend information."""
        return {
            "backend": "XWNODE",
            "version": "0.0.1",
            "capabilities": [
                "multi_language_queries",
                "format_agnostic",
                "strategy_pattern",
                "enterprise_features",
                "xwquery_script_support"
            ],
            "supported_query_types": len(self._supported_queries),
            "performance_class": "high_performance",
            "execution_stats": self.get_execution_stats()
        }
    
    def estimate_cost(self, query: str, query_type: str) -> Dict[str, Any]:
        """Estimate execution cost for XWNode."""
        try:
            strategy = self._get_strategy(query_type)
            plan = strategy.get_query_plan(query)
            
            return {
                "backend": "XWNODE",
                "complexity": plan.get("complexity", "UNKNOWN"),
                "estimated_cost": plan.get("estimated_cost", 0),
                "execution_time": f"{plan.get('estimated_cost', 0)}ms",
                "memory_usage": "low",
                "strategy_used": strategy.__class__.__name__
            }
        except Exception:
            return {
                "backend": "XWNODE",
                "complexity": "UNKNOWN",
                "estimated_cost": 0,
                "execution_time": "0ms",
                "memory_usage": "low",
                "strategy_used": "Unknown"
            }
    
    def execute(self, query: str, context: Dict[str, Any] = None, **kwargs) -> Any:
        """Execute query using XWNode strategies."""
        # Determine query type automatically if not specified
        query_type = kwargs.get('query_type', self._detect_query_type(query))
        return self.execute_query(query, query_type, **kwargs)
    
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get query execution plan."""
        query_type = self._detect_query_type(query)
        try:
            strategy = self._get_strategy(query_type)
            return strategy.get_query_plan(query)
        except Exception:
            return {
                "query_type": query_type,
                "complexity": "UNKNOWN",
                "estimated_cost": 0,
                "backend": "XWNODE"
            }
    
    def can_handle(self, query_string: str) -> bool:
        """Check if XWNode can handle this query."""
        query_type = self._detect_query_type(query_string)
        return query_type in self._supported_queries
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations."""
        return self._supported_queries.copy()
    
    def estimate_complexity(self, query_string: str) -> Dict[str, Any]:
        """Estimate query complexity."""
        query_type = self._detect_query_type(query_string)
        return self.estimate_cost(query_string, query_type)
    
    def _detect_query_type(self, query: str) -> str:
        """Detect query type from query string."""
        query_upper = query.upper()
        
        # Simple detection logic
        if any(keyword in query_upper for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']):
            return "SQL"
        elif 'MATCH' in query_upper and ('(' in query or ')' in query):
            return "CYPHER"
        elif 'PREFIX' in query_upper or 'SELECT' in query_upper and 'WHERE' in query_upper:
            return "SPARQL"
        elif query.strip().startswith('{') and 'query' in query_upper:
            return "GRAPHQL"
        elif 'FROM' in query_upper and 'WHERE' in query_upper:
            return "KQL"
        else:
            return "SQL"  # Default fallback
