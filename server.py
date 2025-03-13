from mcp.server.fastmcp import FastMCP, Context
from loguru import logger
from typing import List, Dict, Optional
import asyncio
import time

# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logger.info(f"Adding {a} and {b}")
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    logger.info(f"Generating greeting for {name}")
    return f"Hello, {name}!"

# Add new static resource
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    logger.info("Fetching app configuration")
    return """
    {
        "app_name": "Demo MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server for learning purposes"
    }
    """

# Add new dynamic resource with multiple parameters
@mcp.resource("calculator://{operation}/{a}/{b}")
def calculator_resource(operation: str, a: float, b: float) -> str:
    """Dynamic calculator resource"""
    logger.info(f"Calculating {operation} for {a} and {b}")
    operations = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b if b != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return f"Error: Unknown operation '{operation}'"
    
    result = operations[operation]()
    return f"Result of {operation}({a}, {b}) = {result}"

@mcp.resource("user://{user_id}")
def get_user_info(user_id: str) -> str:
    """Get user information by ID"""
    logger.info(f"Fetching user info for {user_id}")
    return """
    {
        "user_id": "123",
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    """

# Sample product data for demonstration
products = {
    "123": {
        "product_id": "123",
        "name": "Product A",
        "price": 19.99,
        "description": "A simple product description"
    },
    "456": {
        "product_id": "456",
        "name": "Product B",
        "price": 29.99,
        "description": "Another product description"
    }
}

@mcp.resource("product://{product_id}")
def get_product_info(product_id: str) -> str:
    """Get product information by ID"""
    logger.info(f"Fetching product info for {product_id}")
    
    # Check if the product_id exists in the products dictionary
    if product_id in products:
        product = products[product_id]
        return f"""
        {{
            "product_id": "{product['product_id']}",
            "name": "{product['name']}",
            "price": {product['price']},
            "description": "{product['description']}"
        }}
        """
    else:
        return f"""
        {{
            "error": "Product not found."
        }}
        """

# 1. Tool with multiple parameters and type validation
@mcp.tool()
def analyze_text(
    text: str,
    options: Dict[str, bool] = {"count_words": True, "count_chars": True},
    exclude_words: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Analyze text with configurable options
    
    Args:
        text: Text to analyze
        options: Dictionary of analysis options
        exclude_words: List of words to exclude from counting
    """
    logger.info(f"Analyzing text with options: {options}")
    
    result = {}
    words = text.split()
    
    if exclude_words:
        words = [w for w in words if w.lower() not in exclude_words]
    
    if options.get("count_words"):
        result["word_count"] = len(words)
    
    if options.get("count_chars"):
        result["char_count"] = len(text)
        
    return result

# 2. Async tool with progress tracking
@mcp.tool()
async def process_items(items: List[str], delay: float = 0.5, ctx: Context = None) -> Dict[str, any]:
    """
    Process a list of items asynchronously with progress tracking
    
    Args:
        items: List of items to process
        delay: Delay between items (for demo purposes)
        ctx: MCP context for progress tracking
    """
    logger.info(f"Processing {len(items)} items")
    results = []
    
    for i, item in enumerate(items):
        start_time = time.time()
        
        # Simulate processing
        await asyncio.sleep(delay)
        results.append(f"Processed {item}")
        
        # Track progress
        if ctx:
            await ctx.report_progress(i + 1, len(items))
            ctx.info(f"Processed item {i + 1}/{len(items)}")
            
        processing_time = time.time() - start_time
        logger.info(f"Item {item} processed in {processing_time:.2f}s")
    
    return {
        "processed_count": len(results),
        "results": results,
        "total_time": time.time() - start_time
    }

# The Flow:
# 1. Resources (Data Access)
@mcp.resource("analysis://{file_id}")
async def get_analysis_results(file_id: str) -> str:
    """GET endpoint - for retrieving data"""
    # Check status, get results, etc.

# 2. Tools (Actions/Processing)
@mcp.tool()
async def upload_document(content: str, filename: str, ctx: Context):
    """Action - handles file upload"""
    # Process upload

@mcp.tool()
async def analyze_document(file_id: str, analysis_options: Dict):
    """Action - performs analysis"""
    # Do analysis

