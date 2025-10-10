#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/parsers/base.py

Parser Base Classes

Abstract base class for parameter extractors.
Follows DEV_GUIDELINES.md: base.py extends contracts.py interfaces.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 09-Oct-2025
"""

from abc import ABC
from typing import Dict, Any, Union

from .contracts import IParamExtractor
from .errors import ParseError


class AParamExtractor(IParamExtractor, ABC):
    """
    Abstract base class for parameter extractors.
    
    Extends IParamExtractor interface per DEV_GUIDELINES.md.
    """
    
    def _parse_value(self, value_str: str) -> Union[str, int, float, bool, None]:
        """
        Parse value from string to appropriate type.
        
        Args:
            value_str: String representation of value
        
        Returns:
            Parsed value with correct type
        """
        value_str = value_str.strip().strip('"').strip("'")
        
        # Try boolean
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        if value_str.lower() == 'null' or value_str.lower() == 'none':
            return None
        
        # Try number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Return as string
        return value_str
    
    def _split_fields(self, fields_str: str) -> list:
        """Split comma-separated fields, handling nested expressions."""
        if fields_str.strip() == '*':
            return ['*']
        
        fields = []
        current = []
        paren_depth = 0
        
        for char in fields_str:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                fields.append(''.join(current).strip())
                current = []
                continue
            current.append(char)
        
        if current:
            fields.append(''.join(current).strip())
        
        return fields

