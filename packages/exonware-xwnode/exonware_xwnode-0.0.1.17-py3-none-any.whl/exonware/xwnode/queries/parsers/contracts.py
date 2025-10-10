#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/parsers/contracts.py

Parser Contracts

Interfaces for query parameter extractors.
Follows DEV_GUIDELINES.md: contracts.py for all interfaces.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.17
Generation Date: 09-Oct-2025
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IParamExtractor(ABC):
    """
    Interface for parameter extractors.
    
    Extracts structured parameters from query strings.
    """
    
    @abstractmethod
    def extract_params(self, query: str, action_type: str) -> Dict[str, Any]:
        """
        Extract structured parameters from query.
        
        Args:
            query: Raw query string
            action_type: Type of action (SELECT, INSERT, etc.)
        
        Returns:
            Structured parameters dictionary
        """
        pass
    
    @abstractmethod
    def can_parse(self, query: str) -> bool:
        """Check if this extractor can parse the query."""
        pass

