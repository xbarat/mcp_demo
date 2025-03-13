# MCP Learning Path: Basic Echo Server

## Overview
In this section, we successfully set up a basic MCP server using the FastMCP framework. We implemented a simple addition tool and a greeting resource, and verified their functionality through the MCP Inspector.

## Accomplishments
1. **Environment Setup**
   - Installed MCP using `uv add "mcp[cli]"`.
   - Created a new project directory.

2. **Server Implementation**
   - Created a basic server in `server.py` using FastMCP.
   - Implemented an addition tool:
     ```python
     @mcp.tool()
     def add(a: int, b: int) -> int:
         """Add two numbers"""
         return a + b
     ```
   - Implemented a greeting resource:
     ```python
     @mcp.resource("greeting://{name}")
     def get_greeting(name: str) -> str:
         """Get a personalized greeting"""
         return f"Hello, {name}!"
     ```

3. **Testing and Verification**
   - Ran the server using `mcp dev server.py`.
   - Successfully connected to the MCP Inspector at `http://localhost:5173`.
   - Tested the addition tool and greeting resource through the Inspector, confirming they work as expected.

## Tips for Beginners
To avoid wasting time during the initial stages of learning MCP, consider the following:

1. **Follow Documentation Closely**: Always refer to the official documentation for the latest commands and examples. This helps prevent confusion over outdated methods.

2. **Use the MCP Inspector**: Utilize the Inspector for testing during development. It provides a user-friendly interface to verify your tools and resources.

3. **Start Simple**: Begin with basic implementations before adding complexity. Focus on getting one tool or resource working before moving on to the next.

4. **Avoid Premature Optimization**: Don't worry about optimizing your code in the early stages. Focus on functionality first, and refactor later as needed.

5. **Check Dependencies**: Ensure all required packages are installed correctly. Use `uv add` for managing dependencies to avoid issues with missing modules.

6. **Log Errors**: If something doesn't work, check the logs for error messages. They often provide clues on what went wrong.

By following these guidelines, you can streamline your learning process and avoid common pitfalls.
