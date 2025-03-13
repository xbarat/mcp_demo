# Resource Implementation in MCP

## Overview
This document covers our implementation of various resource types in MCP, from basic static resources to dynamic resources with error handling.

## Implementations

### 1. Static Resources
```python
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return """
    {
        "app_name": "Demo MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server for learning purposes"
    }
    """
```
- Provides unchanging data
- No parameters needed
- Good for configuration and static content

### 2. Dynamic Resources with Single Parameter
```python
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```
- Simple parameter handling
- Direct string interpolation
- Good for basic dynamic content

### 3. Multi-Parameter Resources
```python
@mcp.resource("calculator://{operation}/{a}/{b}")
def calculator_resource(operation: str, a: float, b: float) -> str:
    """Dynamic calculator resource"""
    operations = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b if b != 0 else "Error: Division by zero"
    }
```
- Multiple parameters in URL
- Type conversion (str to float)
- Basic error handling

### 4. Resources with Data Lookup and Error Handling
```python
@mcp.resource("product://{product_id}")
def get_product_info(product_id: str) -> str:
    if product_id in products:
        product = products[product_id]
        return product_details
    else:
        return {"error": "Product not found"}
```
- Dictionary-based data lookup
- Error handling for invalid IDs
- Structured response format

## Key Learnings

### Resource Design Principles
1. **URL Pattern**: Use clear, RESTful-like patterns (e.g., `resource://path/{parameter}`)
2. **Type Hints**: Always include proper type hints for parameters
3. **Documentation**: Include docstrings explaining resource purpose
4. **Logging**: Add logging for monitoring and debugging

### Best Practices
- Keep resources focused on data retrieval
- Handle errors gracefully with meaningful messages
- Use appropriate data structures (dictionaries for lookups)
- Include logging for monitoring
- Return structured data (JSON-like format)

### Testing Patterns
1. Test static resources for consistency
2. Verify parameter handling
3. Check error cases
4. Validate response formats

## Common Patterns Tested

1. **Static Data** 