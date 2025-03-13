# MCP Clients: Connecting to MCP Servers

## The Problem
Until now, we've been:
1. Building servers
2. Testing with MCP Inspector
3. Using built-in tools

But what if you want to:
- Build your own client application?
- Automate interactions with MCP servers?
- Create custom testing tools?
- Integrate MCP servers into other applications?

## The Solution: MCP Client SDK

Here's how to create a client that connects to our SQL Explorer:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def main():
    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],  # Our SQL Explorer server
        env=None
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            
            # Execute a query
            result = await session.call_tool(
                "query_data", 
                arguments={"sql": "SELECT * FROM online_retail LIMIT 5"}
            )
            print("Query result:", result)
            
            # Analyze sales
            sales = await session.call_tool(
                "analyze_sales",
                arguments={"country": "United Kingdom"}
            )
            print("Sales analysis:", sales)

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Features

### 1. Server Connection
```python
server_params = StdioServerParameters(
    command="python",
    args=["server.py"]
)
```
- Connect to any MCP server
- Configure server startup
- Set environment variables

### 2. Session Management
```python
async with ClientSession(read, write) as session:
    await session.initialize()
```
- Automatic connection handling
- Session lifecycle management
- Error handling

### 3. Tool and Resource Access
```python
# List available tools
tools = await session.list_tools()

# Call a tool
result = await session.call_tool("tool_name", arguments={})

# Access a resource
content, mime_type = await session.read_resource("resource://path")
```

## Real-World Example: Automated Analysis Client

```python
async def analyze_multiple_countries(countries: list[str]):
    """Analyze sales for multiple countries"""
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            results = []
            for country in countries:
                # Analyze each country
                result = await session.call_tool(
                    "analyze_sales",
                    arguments={"country": country}
                )
                results.append(f"{country}:\n{result}")
                
            return "\n\n".join(results)

# Use the client
async def main():
    countries = ["United Kingdom", "Germany", "France"]
    results = await analyze_multiple_countries(countries)
    print(results)

asyncio.run(main())
```

## Advanced Features

### 1. Sampling Callback
```python
async def handle_sampling_message(message) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Custom response"
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn"
    )

# Use the callback
session = ClientSession(read, write, sampling_callback=handle_sampling_message)
```

### 2. Resource Handling
```python
# Read files
content, mime_type = await session.read_resource("file://data.csv")

# Access API resources
data, mime_type = await session.read_resource("api://endpoint")
```

## Best Practices

1. **Use Context Managers**
```python
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        # Work with session
```

2. **Handle Errors**
```python
try:
    result = await session.call_tool("tool_name")
except Exception as e:
    print(f"Tool call failed: {e}")
```

3. **Clean Up Resources**
```python
# Context managers handle cleanup automatically
```

## Before vs After

### Without Client SDK:
- Manual protocol implementation
- Complex connection handling
- No session management
- Error-prone interactions

### With Client SDK:
- Simple connection setup
- Managed sessions
- Easy tool/resource access
- Error handling included

## Conclusion

The MCP Client SDK transforms complex server interactions into simple, manageable code:
- Connect to any MCP server
- Use tools and resources easily
- Handle sessions automatically
- Build custom applications

Whether you're building automation tools, testing suites, or integrating MCP into larger applications, the Client SDK makes it straightforward and reliable. 