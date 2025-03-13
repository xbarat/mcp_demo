# SQL Explorer Implementation in MCP

## Overview
The SQL Explorer demonstrates how to create an MCP server that interfaces with a SQLite database, providing both direct query capabilities and analytical tools.

## Implementation

### Server Setup
```python
from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("SQLite Explorer")
```

### Components

1. **Schema Resource**
```python
@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect("online_retail.db")
    schema = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return "\n".join(sql[0] for sql in schema if sql[0])
```
- Provides database structure information
- Accessible via `schema://main`
- Useful for understanding table layouts

2. **Query Tool**
```python
@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect("online_retail.db")
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"
```
- Executes arbitrary SQL queries
- Returns results as formatted strings
- Includes error handling

3. **Analysis Tool**
```python
@mcp.tool()
def analyze_sales(country: str = None) -> str:
    """Analyze sales data for a specific country or all countries"""
    # Implementation details...
```
- Provides pre-built analysis functionality
- Optional country filtering
- Returns formatted sales statistics

## Usage Examples

### 1. Basic Queries
```sql
-- Get sample data
SELECT * FROM online_retail LIMIT 5;

-- Get unique countries
SELECT DISTINCT Country FROM online_retail;
```

### 2. Sales Analysis
```python
# Analyze specific country
analyze_sales(country="United Kingdom")
# Result: "United Kingdom: 23494 orders, $8187806.36 revenue"

# Analyze all countries (top 10 by revenue)
analyze_sales()
```

### 3. Schema Inspection