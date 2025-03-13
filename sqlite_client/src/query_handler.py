"""
Query Handler for SQLite MCP Client.

This module provides utilities for SQL query validation,
formatting, and processing.
"""
import re
from typing import Dict, List, Any, Tuple, Optional
from loguru import logger


def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validate a SQL query for basic syntax and security issues.
    
    Args:
        query: SQL query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for empty query
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    # Check for basic SQL injection patterns
    dangerous_patterns = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+.*\s*SET',
        r';\s*INSERT\s+INTO',
        r'--',
        r'/\*.*\*/'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, f"Query contains potentially dangerous pattern: {pattern}"
    
    # Determine query type
    query_type = get_query_type(query)
    
    # Validate based on query type
    if query_type == "SELECT":
        # Basic validation for SELECT queries
        if not re.search(r'FROM\s+\w+', query, re.IGNORECASE):
            return False, "SELECT query must include FROM clause"
    elif query_type == "INSERT":
        # Basic validation for INSERT queries
        if not re.search(r'INTO\s+\w+', query, re.IGNORECASE):
            return False, "INSERT query must include INTO clause"
    elif query_type == "UPDATE":
        # Basic validation for UPDATE queries
        if not re.search(r'SET\s+\w+\s*=', query, re.IGNORECASE):
            return False, "UPDATE query must include SET clause"
    elif query_type == "DELETE":
        # Basic validation for DELETE queries
        if not re.search(r'FROM\s+\w+', query, re.IGNORECASE):
            return False, "DELETE query must include FROM clause"
    elif query_type == "CREATE":
        # Basic validation for CREATE TABLE queries
        if not re.search(r'TABLE\s+\w+\s*\(', query, re.IGNORECASE):
            return False, "CREATE TABLE query must include table name and column definitions"
    else:
        return False, f"Unsupported query type: {query_type}"
    
    return True, None


def get_query_type(query: str) -> str:
    """Determine the type of SQL query.
    
    Args:
        query: SQL query
        
    Returns:
        Query type (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
    """
    query = query.strip().upper()
    
    if query.startswith("SELECT"):
        return "SELECT"
    elif query.startswith("INSERT"):
        return "INSERT"
    elif query.startswith("UPDATE"):
        return "UPDATE"
    elif query.startswith("DELETE"):
        return "DELETE"
    elif query.startswith("CREATE TABLE"):
        return "CREATE"
    elif query.startswith("ALTER"):
        return "ALTER"
    elif query.startswith("DROP"):
        return "DROP"
    else:
        return "UNKNOWN"


def format_query_results(results: List[Dict[str, Any]], max_width: int = 80) -> str:
    """Format query results for display.
    
    Args:
        results: List of result rows as dictionaries
        max_width: Maximum width for formatting
        
    Returns:
        Formatted string representation of results
    """
    if not results:
        return "No results found."
    
    # Get column names
    columns = list(results[0].keys())
    
    # Calculate column widths
    col_widths = {col: len(col) for col in columns}
    for row in results:
        for col in columns:
            col_widths[col] = max(col_widths[col], len(str(row.get(col, ""))))
    
    # Adjust column widths to fit max_width
    total_width = sum(col_widths.values()) + (3 * len(columns)) - 1
    if total_width > max_width:
        # Scale down column widths proportionally
        scale_factor = max_width / total_width
        for col in col_widths:
            col_widths[col] = max(10, int(col_widths[col] * scale_factor))
    
    # Create header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    separator = "-" * len(header)
    
    # Create rows
    rows = []
    for row in results:
        formatted_row = " | ".join(
            str(row.get(col, "")).ljust(col_widths[col])[:col_widths[col]] 
            for col in columns
        )
        rows.append(formatted_row)
    
    # Combine all parts
    return f"{header}\n{separator}\n" + "\n".join(rows)


def generate_sample_query(table_name: str, columns: List[Dict[str, str]]) -> str:
    """Generate a sample SELECT query for a table.
    
    Args:
        table_name: Name of the table
        columns: List of column definitions
        
    Returns:
        Sample SELECT query
    """
    column_names = [col["name"] for col in columns]
    return f"SELECT {', '.join(column_names)} FROM {table_name} LIMIT 5;"


def generate_create_table_query(table_name: str, columns: List[Dict[str, str]]) -> str:
    """Generate a CREATE TABLE query.
    
    Args:
        table_name: Name of the table
        columns: List of column definitions with name and type
        
    Returns:
        CREATE TABLE SQL statement
    """
    column_defs = []
    for col in columns:
        column_defs.append(f"{col['name']} {col['type']}")
    
    return f"CREATE TABLE {table_name} (\n  {',\n  '.join(column_defs)}\n);" 