# MCP Development Rules

## Client Development Rules

### 1. Client Structure
- Use async/await throughout the client implementation
- Implement core components:
  ```python
  class MCPClient:
      __init__()        # Initialize session and API clients
      connect_to_server() # Handle server connection
      process_query()    # Process user queries
      chat_loop()       # Interactive interface
      cleanup()         # Resource management
  ```
- Always use AsyncExitStack for resource management
- Handle both Python and Node.js server types

### 2. Error Handling
- Implement graceful error handling at multiple levels:
  - Connection errors
  - Query processing errors
  - Tool execution errors
  - Cleanup errors
- Use try/except blocks in all async operations
- Provide meaningful error messages to users
- Handle KeyboardInterrupt gracefully

### 3. API Integration
- Use async API clients (e.g., AsyncAnthropic)
- Keep API keys secure (use environment variables)
- Handle API rate limits and timeouts
- Version lock API dependencies in requirements

### 4. Tool Management
- Cache tool listings when possible
- Validate tool availability before use
- Handle tool execution results properly
- Format tool calls and responses consistently

### 5. User Interface
- Provide clear startup messages
- Show available tools on connection
- Give clear feedback during operations
- Implement clean shutdown mechanism

## Server Development Rules

### 1. Server Structure
- Use FastMCP for server implementation
- Define clear tool and resource endpoints
- Implement proper context handling
- Use type hints for all functions

Example:
```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Service Name")

@mcp.tool()
async def tool_name(param: str, ctx: Context = None) -> str:
    """Tool documentation"""
    if ctx:
        await ctx.info("Operation started")
    # Implementation
    return result
```

### 2. Tool Design
- Each tool should have a single responsibility
- Include clear documentation strings
- Implement proper progress tracking
- Handle errors explicitly
- Return structured responses

### 3. Resource Management
- Use connection pooling for databases
- Close resources properly
- Implement proper error handling
- Use context managers where possible

### 4. Logging and Monitoring
- Use loguru for consistent logging
- Log all significant operations
- Include error context in logs
- Track operation progress

### 5. Security
- Validate all input parameters
- Sanitize SQL queries if used
- Handle sensitive data properly
- Implement proper access controls

## Best Practices

### 1. Development Workflow
- Test tools individually before integration
- Use async test frameworks
- Implement proper error scenarios
- Document all assumptions

### 2. Code Organization
```
/project
  /client
    client.py
    utils.py
    config.py
  /server
    server.py
    tools/
    resources/
  /tests
    test_client.py
    test_server.py
  README.md
  requirements.txt
```

### 3. Documentation
- Document all tools and resources
- Include usage examples
- Document error scenarios
- Keep API documentation updated

### 4. Testing
- Test both client and server independently
- Test error scenarios
- Test resource cleanup
- Test connection handling

### 5. Deployment
- Use proper dependency management
- Version all dependencies
- Document environment requirements
- Include startup scripts

## Common Pitfalls to Avoid
1. Not handling async operations properly
2. Missing error handling in cleanup
3. Not validating tool availability
4. Improper resource cleanup
5. Missing type hints
6. Inadequate error messages
7. Not handling API rate limits
8. Missing documentation

## Example Implementation Checklist
- [ ] Basic client structure
- [ ] Server connection handling
- [ ] Tool execution framework
- [ ] Error handling
- [ ] Resource cleanup
- [ ] User interface
- [ ] Documentation
- [ ] Tests
- [ ] Deployment scripts 