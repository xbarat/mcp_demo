from mcp.server.fastmcp import FastMCP
from loguru import logger
import sqlite3

mcp = FastMCP("SQLite Explorer")

@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect("online_retail.db")
    schema = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return "\n".join(sql[0] for sql in schema if sql[0])

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect("online_retail.db")
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def analyze_sales(country: str = None) -> str:
    """Analyze sales data for a specific country or all countries"""
    conn = sqlite3.connect("online_retail.db")
    try:
        if country:
            query = """
            SELECT Country, COUNT(DISTINCT InvoiceNo) as OrderCount, 
                   SUM(CAST(Quantity AS REAL) * CAST(UnitPrice AS REAL)) as Revenue
            FROM online_retail 
            WHERE Country = ?
            GROUP BY Country
            """
            result = conn.execute(query, (country,)).fetchall()
        else:
            query = """
            SELECT Country, COUNT(DISTINCT InvoiceNo) as OrderCount, 
                   SUM(CAST(Quantity AS REAL) * CAST(UnitPrice AS REAL)) as Revenue
            FROM online_retail 
            GROUP BY Country
            ORDER BY Revenue DESC LIMIT 10
            """
            result = conn.execute(query).fetchall()
        return "\n".join(f"{row[0]}: {row[1]} orders, ${row[2]:.2f} revenue" for row in result)
    except Exception as e:
        return f"Error: {str(e)}"