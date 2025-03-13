from mcp.server.fastmcp import FastMCP
from loguru import logger

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

