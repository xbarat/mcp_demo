"""
Business Insight Generation for SQLite MCP Client.

This module provides utilities for generating business insights
from SQL query results and managing the insights memo.
"""
from typing import Dict, List, Any, Optional
from loguru import logger


def analyze_query_results(
    query: str,
    results: List[Dict[str, Any]],
    table_name: Optional[str] = None
) -> List[str]:
    """Analyze query results to generate potential business insights.
    
    Args:
        query: The SQL query that generated the results
        results: List of result rows as dictionaries
        table_name: Optional table name for context
        
    Returns:
        List of potential business insights
    """
    insights = []
    
    if not results:
        return ["No data available for analysis."]
    
    # Basic statistics
    row_count = len(results)
    insights.append(f"Query returned {row_count} rows of data.")
    
    # Analyze based on query type
    if "COUNT" in query.upper() and row_count == 1:
        # Count query
        for key, value in results[0].items():
            if "COUNT" in key.upper():
                insights.append(f"Total count: {value}")
    
    elif "AVG" in query.upper() or "SUM" in query.upper() or "MIN" in query.upper() or "MAX" in query.upper():
        # Aggregate query
        for row in results:
            for key, value in row.items():
                if any(agg in key.upper() for agg in ["AVG", "SUM", "MIN", "MAX"]):
                    insights.append(f"{key}: {value}")
    
    elif "GROUP BY" in query.upper():
        # Group by query - look for patterns
        if row_count > 1:
            # Find the grouped column and the measure columns
            grouped_col = None
            measure_cols = []
            
            for key in results[0].keys():
                if key in query.upper().split("GROUP BY")[1]:
                    grouped_col = key
                else:
                    measure_cols.append(key)
            
            if grouped_col and measure_cols:
                # Find the top value
                top_row = max(results, key=lambda x: float(x[measure_cols[0]]) if isinstance(x[measure_cols[0]], (int, float)) or str(x[measure_cols[0]]).isdigit() else 0)
                insights.append(f"Top {grouped_col}: {top_row[grouped_col]} with {measure_cols[0]} of {top_row[measure_cols[0]]}")
                
                # Find the bottom value
                bottom_row = min(results, key=lambda x: float(x[measure_cols[0]]) if isinstance(x[measure_cols[0]], (int, float)) or str(x[measure_cols[0]]).isdigit() else float('inf'))
                insights.append(f"Bottom {grouped_col}: {bottom_row[grouped_col]} with {measure_cols[0]} of {bottom_row[measure_cols[0]]}")
    
    return insights


def format_insights_for_memo(insights: List[str], query: str, context: str = "") -> str:
    """Format insights for addition to the memo resource.
    
    Args:
        insights: List of insight strings
        query: The SQL query that generated the insights
        context: Additional context information
        
    Returns:
        Formatted insight text for the memo
    """
    if not insights:
        return ""
    
    # Format the query for display
    formatted_query = f"```sql\n{query}\n```"
    
    # Format the insights
    formatted_insights = "\n".join([f"- {insight}" for insight in insights])
    
    # Combine with context
    if context:
        result = f"## Business Insight: {context}\n\n{formatted_query}\n\n{formatted_insights}\n"
    else:
        result = f"## Business Insight\n\n{formatted_query}\n\n{formatted_insights}\n"
    
    return result


def generate_insight_from_schema(
    table_name: str,
    columns: List[Dict[str, str]]
) -> str:
    """Generate insights based on database schema.
    
    Args:
        table_name: Name of the table
        columns: List of column definitions
        
    Returns:
        Insight text about the schema
    """
    column_types = {}
    for col in columns:
        col_type = col.get("type", "").upper()
        if col_type not in column_types:
            column_types[col_type] = []
        column_types[col_type].append(col.get("name"))
    
    insights = [f"Table '{table_name}' has {len(columns)} columns:"]
    
    for col_type, cols in column_types.items():
        insights.append(f"- {len(cols)} {col_type} columns: {', '.join(cols)}")
    
    # Identify potential key columns
    potential_keys = []
    for col in columns:
        col_name = col.get("name", "").lower()
        col_type = col.get("type", "").upper()
        if "id" in col_name or col_name.endswith("_id") or "key" in col_name:
            potential_keys.append(col_name)
    
    if potential_keys:
        insights.append(f"- Potential key columns: {', '.join(potential_keys)}")
    
    # Identify potential date columns
    date_columns = []
    for col in columns:
        col_name = col.get("name", "").lower()
        col_type = col.get("type", "").upper()
        if ("date" in col_name or "time" in col_name or 
            "DATE" in col_type or "TIME" in col_type):
            date_columns.append(col_name)
    
    if date_columns:
        insights.append(f"- Date/time columns: {', '.join(date_columns)}")
    
    return format_insights_for_memo(
        insights, 
        f"DESCRIBE {table_name}", 
        f"Schema Analysis for {table_name}"
    ) 