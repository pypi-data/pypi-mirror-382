#!/usr/bin/env python3
"""
Utility Functions for XWQuery Console

Formatting, display, and UI helper functions.
"""

import json
from typing import Any, List, Dict, Optional


def print_banner():
    """Print console banner."""
    banner = """
================================================================
            XWQuery Interactive Console v0.0.1
================================================================
  Type .help for commands | .examples for sample queries
  Type .exit or Ctrl+C to quit
================================================================
"""
    print(banner)


def print_collections_info(stats: Dict[str, int]):
    """Print information about loaded collections."""
    print("\nCollections loaded:")
    for name, count in stats.items():
        print(f"  • {name:12} ({count:4} records)")
    print()


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
  .help              - Show this help message
  .collections       - List all collections with record counts
  .show <collection> - Show sample records from collection
  .examples [type]   - Show example queries (optionally filtered by type)
  .clear             - Clear the screen
  .exit              - Exit the console

Query Examples:
  SELECT * FROM users WHERE age > 30
  SELECT name, age FROM users
  SELECT category, COUNT(*) FROM products GROUP BY category
  
For more examples, type: .examples
"""
    print(help_text)


def print_examples_list():
    """Print list of example categories."""
    print("""
Example Categories:
  .examples core         - Core CRUD operations (SELECT, INSERT, UPDATE, DELETE, CREATE, DROP)
  .examples filtering    - Filtering operations (WHERE, FILTER, LIKE, IN, HAS, BETWEEN, RANGE)
  .examples aggregation  - Aggregation operations (COUNT, SUM, AVG, MIN, MAX, GROUP BY)
  .examples ordering     - Ordering operations (ORDER BY)
  .examples graph        - Graph operations (MATCH, PATH, TRAVERSE)
  .examples projection   - Projection operations (PROJECT, EXTEND)
  .examples advanced     - Advanced operations (JOIN, UNION, WINDOW)
  .examples all          - Show all examples
""")


def format_results(data: Any, max_rows: int = 20) -> str:
    """
    Format query results for display.
    
    Args:
        data: Result data to format
        max_rows: Maximum number of rows to display
    
    Returns:
        Formatted string
    """
    if data is None:
        return "No results"
    
    if isinstance(data, dict):
        # Check for common result structures
        if 'items' in data and isinstance(data['items'], list):
            return format_list_results(data['items'], max_rows)
        elif 'result' in data:
            return format_results(data['result'], max_rows)
        elif 'count' in data:
            return f"Count: {data['count']}"
        else:
            return json.dumps(data, indent=2)
    
    elif isinstance(data, list):
        return format_list_results(data, max_rows)
    
    else:
        return str(data)


def format_list_results(items: List[Any], max_rows: int = 20) -> str:
    """Format list of items as a table or JSON."""
    if not items:
        return "No results"
    
    total_count = len(items)
    display_items = items[:max_rows]
    
    # Try to format as table if items are dicts with same keys
    if all(isinstance(item, dict) for item in display_items):
        result = format_table(display_items)
    else:
        # Fallback to JSON
        result = json.dumps(display_items, indent=2)
    
    # Add count info
    if total_count > max_rows:
        result += f"\n\n... showing {max_rows} of {total_count} results"
    else:
        result += f"\n\nTotal: {total_count} results"
    
    return result


def format_table(items: List[Dict[str, Any]], max_col_width: int = 30) -> str:
    """
    Format list of dicts as an ASCII table.
    
    Args:
        items: List of dictionaries to format
        max_col_width: Maximum column width
    
    Returns:
        ASCII table string
    """
    if not items:
        return "No data"
    
    # Get all keys
    keys = list(items[0].keys())
    
    # Calculate column widths
    col_widths = {}
    for key in keys:
        col_widths[key] = min(
            max(
                len(str(key)),
                max(len(str(item.get(key, ''))) for item in items)
            ),
            max_col_width
        )
    
    # Build table
    lines = []
    
    # Header
    header = "| " + " | ".join(
        str(key).ljust(col_widths[key]) for key in keys
    ) + " |"
    separator = "+-" + "-+-".join("-" * col_widths[key] for key in keys) + "-+"
    
    lines.append(separator)
    lines.append(header)
    lines.append(separator)
    
    # Rows
    for item in items:
        row = "| " + " | ".join(
            truncate_str(str(item.get(key, '')), col_widths[key]).ljust(col_widths[key])
            for key in keys
        ) + " |"
        lines.append(row)
    
    lines.append(separator)
    
    return "\n".join(lines)


def truncate_str(s: str, max_len: int) -> str:
    """Truncate string to max length."""
    if len(s) <= max_len:
        return s
    return s[:max_len-3] + "..."


def format_error(error: Exception) -> str:
    """Format error message."""
    error_type = type(error).__name__
    return f"[ERROR] {error_type}: {str(error)}"


def format_success(message: str) -> str:
    """Format success message."""
    return f"[OK] {message}"


def format_execution_time(seconds: float) -> str:
    """Format execution time."""
    if seconds < 0.001:
        return f"Execution time: <0.001s"
    elif seconds < 1:
        return f"Execution time: {seconds:.3f}s"
    else:
        return f"Execution time: {seconds:.2f}s"


def clear_screen():
    """Clear the console screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_collection_sample(collection_name: str, data: List[Dict], sample_size: int = 5):
    """Print a sample of records from a collection."""
    if not data:
        print(f"Collection '{collection_name}' is empty")
        return
    
    print(f"\nSample from '{collection_name}' ({len(data)} total records):")
    print(format_table(data[:sample_size]))
    
    if len(data) > sample_size:
        print(f"\n... showing {sample_size} of {len(data)} records")

