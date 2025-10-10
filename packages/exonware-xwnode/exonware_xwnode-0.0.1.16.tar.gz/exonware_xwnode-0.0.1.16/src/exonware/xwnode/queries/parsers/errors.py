#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/queries/parsers/errors.py

Parser Errors

Module-specific errors for query parsers.
Extends root error classes per DEV_GUIDELINES.md - no redundancy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.16
Generation Date: 09-Oct-2025
"""

# Import and REUSE root error classes per DEV_GUIDELINES
from ...errors import XWNodeError, XWNodeValueError


class ParserError(XWNodeError):
    """
    Base error for parser operations.
    
    Extends XWNodeError from root - follows DEV_GUIDELINES principle.
    """
    pass


class ParseError(ParserError):
    """Raised when query parsing fails."""
    
    def __init__(self, query: str, reason: str, position: int = None):
        message = f"Failed to parse query: {reason}"
        if position is not None:
            message += f" at position {position}"
        super().__init__(message)
        self.query = query
        self.reason = reason
        self.position = position


class UnsupportedSyntaxError(ParserError):
    """Raised when syntax is not supported."""
    pass


__all__ = [
    'ParserError',
    'ParseError',
    'UnsupportedSyntaxError',
]

