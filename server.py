from mcp.server.fastmcp import FastMCP, Context
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
async def query_data(sql: str, ctx: Context = None) -> str:
    """Execute SQL queries safely with basic context usage"""
    # Use context for logging if available
    if ctx:
        await ctx.info(f"Executing query: {sql}")
    
    conn = sqlite3.connect("online_retail.db")
    try:
        result = conn.execute(sql).fetchall()
        
        if ctx:
            await ctx.info("Query completed successfully")
            
        return "\n".join(str(row) for row in result)
    except Exception as e:
        if ctx:
            await ctx.error(f"Query failed: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def analyze_sales(country: str = None, ctx: Context = None) -> str:
    """Analyze sales data with basic progress tracking"""
    if ctx:
        await ctx.info("Starting analysis...")
        await ctx.report_progress(1, 2)  # Simple 2-step progress
    
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
            
        if ctx:
            await ctx.info("Analysis complete")
            await ctx.report_progress(2, 2)
            
        return "\n".join(f"{row[0]}: {row[1]} orders, ${row[2]:.2f} revenue" for row in result)
    except Exception as e:
        if ctx:
            await ctx.error(f"Analysis failed: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()