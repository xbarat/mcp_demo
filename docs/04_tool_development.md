# Advanced Tool Development in MCP

## Overview
This document covers our implementation of advanced MCP tools, focusing on complex parameter handling, async operations, and real-world applications.

## Key Concepts

### 1. Tool Structure
```python
@mcp.tool()
def tool_name(
    required_param: type,
    optional_param: Optional[type] = default_value,
    ctx: Context = None
) -> ReturnType:
    """Docstring with clear description
    
    Args:
        required_param: Description
        optional_param: Description
        ctx: MCP context for advanced features
    Returns:
        Description of return value
    """
```

### 2. Type Hints and Validation
```python
from typing import Dict, List, Optional

# Complex parameter types
options: Dict[str, bool] = {"feature1": True}
items: List[str] = ["item1", "item2"]
nullable: Optional[str] = None
```

## Implementations

### 1. Text Analysis Tool
```python
@mcp.tool()
def analyze_text(
    text: str,
    options: Dict[str, bool] = {"count_words": True, "count_chars": True},
    exclude_words: Optional[List[str]] = None
) -> Dict[str, any]:
    """Text analysis with configurable options"""
```

#### Testing:
```python
# Basic usage
result = analyze_text("Hello world!")
assert "word_count" in result

# With options
result = analyze_text(
    "Hello world!",
    options={"count_words": True},
    exclude_words=["hello"]
)
```

### 2. Async Document Processing
```python
@mcp.tool()
async def process_items(
    items: List[str],
    delay: float = 0.5,
    ctx: Context = None
) -> Dict[str, any]:
    """Async processing with progress tracking"""
```

#### Testing:
```python
# Basic usage
result = await process_items(["item1", "item2"])

# With progress tracking
result = await process_items(
    ["item1", "item2"],
    delay=1.0,
    ctx=context
)
```

## Real World Example: Document Analysis System

### 1. File Upload Tool
```python
@mcp.tool()
async def upload_document(content: str, filename: str, ctx: Context):
    """Handle document uploads"""
```

### 2. Document Analysis Tool
```python
@mcp.tool()
async def analyze_document(
    file_id: str,
    analysis_options: Dict[str, bool],
    ctx: Context = None
):
    """Analyze document content"""
```

### Usage Flow:
1. Upload document
2. Get file ID
3. Request analysis
4. Monitor progress
5. Retrieve results

## Best Practices

### 1. Tool Design
- Single responsibility principle
- Clear parameter naming
- Comprehensive docstrings
- Appropriate default values
- Error handling

### 2. Type Hints
- Use specific types
- Include Optional for nullable parameters
- Use compound types (Dict, List) appropriately
- Document type constraints

### 3. Async Operations
- Use async for I/O operations
- Implement progress tracking
- Handle cancellation
- Provide status updates

### 4. Error Handling
- Catch specific exceptions
- Return meaningful error messages
- Log errors appropriately
- Maintain type consistency in error cases

## Common Patterns

### 1. Progress Tracking
```python
if ctx:
    await ctx.report_progress(current, total)
    ctx.info(f"Progress: {current}/{total}")
```

### 2. Error Handling
```python
try:
    result = process_data()
    return {"status": "success", "data": result}
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return {"status": "error", "message": str(e)}
```

### 3. Parameter Validation
```python
def validate_options(options: Dict[str, bool]) -> bool:
    required_keys = ["feature1", "feature2"]
    return all(key in options for key in required_keys)
```

## Discussion Points

### 1. Tool vs Resource Choice
- Tools for actions/computation
- Resources for data retrieval
- When to use each

### 2. Async Considerations
- When to use async
- Progress tracking importance
- Error handling in async context

### 3. Type System Benefits
- Code clarity
- IDE support
- Runtime validation
- Documentation

### 4. Performance Monitoring
- Logging strategies
- Progress tracking
- Error reporting
- Performance metrics

## Moving Forward
- Consider caching strategies
- Implement more complex validation
- Add support for different file types
- Enhance error handling
- Implement retry mechanisms

## Notes to Remember
1. Always include proper type hints
2. Document your tools thoroughly
3. Implement proper error handling
4. Use async when appropriate
5. Track progress for long-running operations
6. Log important events and errors
