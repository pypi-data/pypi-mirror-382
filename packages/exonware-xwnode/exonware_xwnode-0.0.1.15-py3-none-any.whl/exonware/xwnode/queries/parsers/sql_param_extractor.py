#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/parsers/sql_param_extractor.py

SQL Parameter Extractor

Extracts structured parameters from SQL-style queries.
Uses regex for simplicity - follows DEV_GUIDELINES.md.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
Generation Date: 09-Oct-2025
"""

import re
from typing import Dict, Any, List, Union

from .base import AParamExtractor
from .errors import ParseError


class SQLParamExtractor(AParamExtractor):
    """
    SQL parameter extractor using regex.
    
    Extracts structured parameters from SQL queries for executor consumption.
    Implements IParamExtractor interface per DEV_GUIDELINES.md.
    """
    
    def extract_params(self, query: str, action_type: str) -> Dict[str, Any]:
        """
        Extract parameters based on action type.
        
        Args:
            query: SQL query string
            action_type: Type of action (SELECT, INSERT, etc.)
        
        Returns:
            Structured parameters dictionary
        """
        # Route to appropriate extractor
        extractors = {
            'SELECT': self.extract_select_params,
            'INSERT': self.extract_insert_params,
            'UPDATE': self.extract_update_params,
            'DELETE': self.extract_delete_params,
            'WHERE': self.extract_where_params,
            'COUNT': self.extract_count_params,
            'GROUP': self.extract_group_by_params,
            'ORDER': self.extract_order_by_params,
        }
        
        extractor = extractors.get(action_type)
        if extractor:
            return extractor(query)
        
        # Fallback: return raw query
        return {'raw': query}
    
    def can_parse(self, query: str) -> bool:
        """Check if query looks like SQL."""
        query_upper = query.upper()
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE']
        return any(kw in query_upper for kw in sql_keywords)
    
    def extract_select_params(self, sql: str) -> Dict[str, Any]:
        """Extract SELECT statement parameters."""
        params = {}
        
        # Extract SELECT fields
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if select_match:
            fields_str = select_match.group(1).strip()
            params['fields'] = self._split_fields(fields_str)
        else:
            params['fields'] = ['*']
        
        # Extract FROM table
        from_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if from_match:
            params['from'] = from_match.group(1)
            params['path'] = from_match.group(1)  # Alias for compatibility
        
        # Extract WHERE conditions
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            params['where'] = self._parse_where_condition(where_match.group(1).strip())
        
        # Extract ORDER BY
        order_match = re.search(r'ORDER\s+BY\s+(.*?)(?:LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if order_match:
            params['order_by'] = order_match.group(1).strip()
        
        # Extract GROUP BY
        group_match = re.search(r'GROUP\s+BY\s+(.*?)(?:HAVING|ORDER|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if group_match:
            params['group_by'] = [f.strip() for f in group_match.group(1).split(',')]
        
        # Extract LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        if limit_match:
            params['limit'] = int(limit_match.group(1))
        
        return params
    
    def extract_insert_params(self, sql: str) -> Dict[str, Any]:
        """Extract INSERT statement parameters."""
        params = {}
        
        # INSERT INTO table VALUES {...}
        into_match = re.search(r'INSERT\s+INTO\s+(\w+)', sql, re.IGNORECASE)
        if into_match:
            params['target'] = into_match.group(1)
        
        # Extract VALUES
        values_match = re.search(r'VALUES\s+(.+)', sql, re.IGNORECASE | re.DOTALL)
        if values_match:
            values_str = values_match.group(1).strip()
            # Try to parse as JSON-like dict/list
            try:
                # Remove outer braces and parse key:value pairs
                if values_str.startswith('{'):
                    params['values'] = self._parse_dict_literal(values_str)
                elif values_str.startswith('('):
                    params['values'] = self._parse_tuple_literal(values_str)
            except:
                params['values'] = values_str
        
        return params
    
    def extract_update_params(self, sql: str) -> Dict[str, Any]:
        """Extract UPDATE statement parameters."""
        params = {}
        
        # UPDATE table SET ...
        table_match = re.search(r'UPDATE\s+(\w+)', sql, re.IGNORECASE)
        if table_match:
            params['target'] = table_match.group(1)
        
        # Extract SET clause
        set_match = re.search(r'SET\s+(.+?)(?:WHERE|$)', sql, re.IGNORECASE | re.DOTALL)
        if set_match:
            params['values'] = self._parse_set_clause(set_match.group(1).strip())
        
        # Extract WHERE
        where_match = re.search(r'WHERE\s+(.+?)$', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            params['where'] = self._parse_where_condition(where_match.group(1).strip())
        
        return params
    
    def extract_delete_params(self, sql: str) -> Dict[str, Any]:
        """Extract DELETE statement parameters."""
        params = {}
        
        # DELETE FROM table
        from_match = re.search(r'DELETE\s+FROM\s+(\w+)', sql, re.IGNORECASE)
        if from_match:
            params['target'] = from_match.group(1)
        
        # Extract WHERE
        where_match = re.search(r'WHERE\s+(.+?)$', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            params['where'] = self._parse_where_condition(where_match.group(1).strip())
        
        return params
    
    def extract_where_params(self, sql: str) -> Dict[str, Any]:
        """Extract WHERE clause parameters."""
        # Extract just the condition part
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            return self._parse_where_condition(where_match.group(1).strip())
        return {}
    
    def extract_count_params(self, sql: str) -> Dict[str, Any]:
        """Extract COUNT parameters."""
        params = {}
        
        # COUNT(*) or COUNT(field)
        count_match = re.search(r'COUNT\s*\(\s*([^)]+)\s*\)', sql, re.IGNORECASE)
        if count_match:
            field = count_match.group(1).strip()
            params['field'] = field if field != '*' else None
        
        # Extract FROM
        from_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if from_match:
            params['from'] = from_match.group(1)
            params['path'] = from_match.group(1)
        
        # Extract WHERE
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            params['where'] = self._parse_where_condition(where_match.group(1).strip())
        
        return params
    
    def extract_group_by_params(self, sql: str) -> Dict[str, Any]:
        """Extract GROUP BY parameters."""
        params = {}
        
        # GROUP BY fields
        group_match = re.search(r'GROUP\s+BY\s+(.*?)(?:HAVING|ORDER|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if group_match:
            params['fields'] = [f.strip() for f in group_match.group(1).split(',')]
        
        # Extract HAVING
        having_match = re.search(r'HAVING\s+(.+?)(?:ORDER|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if having_match:
            params['having'] = self._parse_where_condition(having_match.group(1).strip())
        
        return params
    
    def extract_order_by_params(self, sql: str) -> Dict[str, Any]:
        """Extract ORDER BY parameters."""
        params = {}
        
        # ORDER BY field ASC/DESC
        order_match = re.search(r'ORDER\s+BY\s+(.*?)(?:LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if order_match:
            order_clause = order_match.group(1).strip()
            
            # Parse: field ASC, field2 DESC
            order_fields = []
            for field_spec in order_clause.split(','):
                field_spec = field_spec.strip()
                if ' DESC' in field_spec.upper():
                    field = field_spec.upper().replace(' DESC', '').strip()
                    order_fields.append({'field': field, 'direction': 'DESC'})
                elif ' ASC' in field_spec.upper():
                    field = field_spec.upper().replace(' ASC', '').strip()
                    order_fields.append({'field': field, 'direction': 'ASC'})
                else:
                    order_fields.append({'field': field_spec, 'direction': 'ASC'})
            
            params['fields'] = order_fields
        
        return params
    
    def _parse_where_condition(self, condition: str) -> Dict[str, Any]:
        """
        Parse WHERE condition into structured format.
        
        Supports: field operator value
        Examples: age > 50, name = 'John', price >= 100
        """
        condition = condition.strip()
        
        # Check for operators in order of precedence
        operators = ['>=', '<=', '!=', '<>', '>', '<', '=', 'LIKE', 'IN']
        
        for op in operators:
            # Case-insensitive for word operators
            if op.isalpha():
                pattern = rf'\s+{op}\s+'
                match = re.search(pattern, condition, re.IGNORECASE)
                if match:
                    field = condition[:match.start()].strip()
                    value = condition[match.end():].strip()
                    return {
                        'field': field,
                        'operator': op.upper(),
                        'value': self._parse_value(value) if op.upper() != 'IN' else self._parse_in_values(value)
                    }
            else:
                if op in condition:
                    parts = condition.split(op, 1)
                    if len(parts) == 2:
                        return {
                            'field': parts[0].strip(),
                            'operator': op,
                            'value': self._parse_value(parts[1].strip())
                        }
        
        # Can't parse - return as expression
        return {'expression': condition}
    
    def _parse_in_values(self, values_str: str) -> List:
        """Parse IN clause values."""
        # IN ['value1', 'value2'] or IN ('value1', 'value2')
        values_str = values_str.strip().strip('[]()').strip()
        values = [self._parse_value(v.strip()) for v in values_str.split(',')]
        return values
    
    def _parse_set_clause(self, set_str: str) -> Dict[str, Any]:
        """Parse SET clause in UPDATE."""
        assignments = {}
        
        # Split by comma
        for assignment in set_str.split(','):
            if '=' in assignment:
                field, value = assignment.split('=', 1)
                assignments[field.strip()] = self._parse_value(value.strip())
        
        return assignments
    
    def _parse_dict_literal(self, dict_str: str) -> Dict[str, Any]:
        """Parse dictionary literal from string."""
        # Simple parser for {key: value, key2: value2}
        dict_str = dict_str.strip('{}').strip()
        result = {}
        
        for pair in dict_str.split(','):
            if ':' in pair:
                key, value = pair.split(':', 1)
                result[key.strip()] = self._parse_value(value.strip())
        
        return result
    
    def _parse_tuple_literal(self, tuple_str: str) -> List[Any]:
        """Parse tuple literal from string."""
        # Simple parser for (value1, value2, value3)
        tuple_str = tuple_str.strip('()').strip()
        return [self._parse_value(v.strip()) for v in tuple_str.split(',')]

