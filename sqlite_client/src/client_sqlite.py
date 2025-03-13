"""
SQLite MCP Client - Main implementation.

This client connects to a SQLite MCP server and provides methods
for executing SQL queries, managing schema, and generating business insights.
"""
import asyncio
import sys
import json
from typing import Optional, Dict, List, Any, Union
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import AsyncAnthropic
from loguru import logger

from .config import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    MAX_TOKENS,
    DEFAULT_SERVER_PATH,
    TIMEOUT_SECONDS,
    RETRY_ATTEMPTS,
    RETRY_DELAY
)

class SQLiteMCPClient:
    """Client for interacting with SQLite MCP Server."""
    
    def __init__(self):
        """Initialize the SQLite MCP client."""
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = AsyncAnthropic()
        self.tools_cache = None
        
        # Local storage for insights
        self._insights = []
        
        # Configure logger
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    
    async def connect_to_server(self, server_script_path: str = DEFAULT_SERVER_PATH, db_path: str = None):
        """Connect to the SQLite MCP server.
        
        Args:
            server_script_path: Path to the server script or command
            db_path: Path to the SQLite database file
        """
        logger.info(f"Connecting to SQLite MCP server: {server_script_path}")
        
        # Determine if it's a Python script or a command
        is_python = server_script_path.endswith('.py')
        
        # Set up command and arguments
        if is_python:
            command = "python"
            args = [server_script_path]
        else:
            command = server_script_path
            args = []
        
        # Add database path if provided
        if db_path:
            args.extend(["--db-path", db_path])
        
        # Set up server parameters
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )
        
        # Connect to the server
        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            
            # Initialize the session
            await self.session.initialize()
            
            # Cache available tools
            await self._cache_tools()
            
            logger.info(f"Connected to server with tools: {[tool['name'] for tool in self.tools_cache]}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            await self.cleanup()
            raise
    
    async def _cache_tools(self):
        """Cache the available tools from the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        response = await self.session.list_tools()
        self.tools_cache = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
    
    async def execute_read_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query.
        
        Args:
            query: SQL SELECT query
            
        Returns:
            List of result rows as dictionaries
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info(f"Executing read query: {query}")
        try:
            result = await self.call_tool_with_retry("read_query", {"query": query})
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            logger.error(f"Error executing read query: {str(e)}")
            return []
    
    async def execute_write_query(self, query: str) -> Dict[str, int]:
        """Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL modification query
            
        Returns:
            Dictionary with affected_rows count
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info(f"Executing write query: {query}")
        try:
            result = await self.call_tool_with_retry("write_query", {"query": query})
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            return {"affected_rows": 0}
        except Exception as e:
            logger.error(f"Error executing write query: {str(e)}")
            return {"affected_rows": 0}
    
    async def create_table(self, query: str) -> Dict[str, str]:
        """Create a new table.
        
        Args:
            query: CREATE TABLE SQL statement
            
        Returns:
            Confirmation message
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info(f"Creating table: {query}")
        try:
            result = await self.call_tool_with_retry("create_table", {"query": query})
            return {"message": result if isinstance(result, str) else str(result)}
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            return {"message": f"Error: {str(e)}"}
    
    async def list_tables(self) -> List[str]:
        """Get a list of all tables in the database.
        
        Returns:
            List of table names
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info("Listing tables")
        try:
            result = await self.call_tool_with_retry("list_tables", {})
            if isinstance(result, list):
                return [table["name"] for table in result if isinstance(table, dict) and "name" in table]
            return []
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            return []
    
    async def describe_table(self, table_name: str) -> List[Dict[str, str]]:
        """Get schema information for a table.
        
        Args:
            table_name: Name of the table to describe
            
        Returns:
            List of column definitions
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info(f"Describing table: {table_name}")
        try:
            result = await self.call_tool_with_retry("describe_table", {"table_name": table_name})
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            logger.error(f"Error describing table: {str(e)}")
            return []
    
    async def append_insight(self, insight: str, blocking: bool = True) -> Dict[str, str]:
        """Add a business insight to the memo resource.
        
        Args:
            insight: Business insight text
            blocking: Whether to wait for the operation to complete
            
        Returns:
            Confirmation message
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info(f"Appending insight: {insight}")
        
        # Store locally for backup
        self._insights.append(insight)
        
        if not blocking:
            # Create a task and return immediately
            asyncio.create_task(self._append_insight_task(insight))
            return {"message": "Insight submission started (non-blocking)"}
        
        try:
            # Use a direct call with a shorter timeout
            result = await asyncio.wait_for(
                self.session.call_tool("append_insight", {"insight": insight}),
                timeout=5
            )
            
            # Parse the result
            if hasattr(result, "content") and isinstance(result.content, list) and len(result.content) > 0:
                if hasattr(result.content[0], "text"):
                    return {"message": result.content[0].text}
            
            return {"message": "Insight added to memo"}
        except asyncio.TimeoutError:
            logger.warning("Append insight timed out, but the operation may have succeeded")
            return {"message": "Insight submission timed out, but may have succeeded"}
        except Exception as e:
            logger.error(f"Error appending insight: {str(e)}")
            return {"message": f"Error: {str(e)}"}
    
    async def _append_insight_task(self, insight: str):
        """Background task for appending insights.
        
        Args:
            insight: Business insight text
        """
        try:
            # Use a direct call with a shorter timeout
            result = await asyncio.wait_for(
                self.session.call_tool("append_insight", {"insight": insight}),
                timeout=5
            )
            logger.info(f"Background insight added successfully")
        except asyncio.TimeoutError:
            logger.warning("Background insight submission timed out, but may have succeeded")
        except Exception as e:
            logger.error(f"Error in background insight task: {str(e)}")
    
    async def get_insights_memo(self) -> str:
        """Get the current business insights memo.
        
        Returns:
            The memo content as a string
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        logger.info("Retrieving insights memo")
        
        try:
            # Try with read_resource first
            try:
                result = await asyncio.wait_for(
                    self.session.read_resource("memo://insights"),
                    timeout=5
                )
                
                # Parse the result
                if hasattr(result, "content"):
                    content = result.content
                    if hasattr(content, "text"):
                        return content.text
                    return str(content)
                return str(result)
            except Exception as e:
                logger.warning(f"Server memo retrieval failed: {str(e)}, using local insights")
                
                # Fall back to locally stored insights
                if not self._insights:
                    return "No business insights have been discovered yet."
                
                insights = "\n".join(f"- {insight}" for insight in self._insights)
                
                memo = "📊 Business Intelligence Memo 📊\n\n"
                memo += "Key Insights Discovered:\n\n"
                memo += insights
                
                if len(self._insights) > 1:
                    memo += "\n\nSummary:\n"
                    memo += f"Analysis has revealed {len(self._insights)} key business insights that suggest opportunities for strategic optimization and growth."
                
                return memo
        except Exception as e:
            logger.error(f"Error retrieving insights memo: {str(e)}")
            return f"Error retrieving memo: {str(e)}"
    
    async def analyze_with_claude(self, query: str) -> str:
        """Process a query using Claude and available tools.
        
        Args:
            query: The user's query
            
        Returns:
            Claude's response with tool results
        """
        if not self.session or not self.tools_cache:
            raise RuntimeError("Not connected to server or tools not cached")
        
        try:
            messages = [{"role": "user", "content": query}]
            
            # Initial Claude API call
            response = await self.anthropic.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages,
                tools=self.tools_cache
            )
            
            # Process response and handle tool calls
            final_text = []
            
            assistant_message_content = []
            for content in response.content:
                if content.type == 'text':
                    final_text.append(content.text)
                    assistant_message_content.append(content)
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    
                    # Execute tool call
                    result = await self.call_tool_with_retry(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                    
                    assistant_message_content.append(content)
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message_content
                    })
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result
                            }
                        ]
                    })
                    
                    # Get next response from Claude
                    response = await self.anthropic.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=MAX_TOKENS,
                        messages=messages,
                        tools=self.tools_cache
                    )
                    
                    final_text.append(response.content[0].text)
            
            return "\n".join(final_text)
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    def _print_help(self):
        """Print help information."""
        print("\nAvailable Commands:")
        print("  help          - Show this help message")
        print("  quit          - Exit the client")
        print("\nQuery Examples:")
        print("  'Show me all tables'")
        print("  'Create a new table called products'")
        print("  'What insights can you find in the orders data?'")
        print("\nAvailable Tools:")
        if self.tools_cache:
            for tool in self.tools_cache:
                print(f"  {tool['name']} - {tool['description']}")
    
    async def chat_loop(self):
        """Run an interactive chat loop."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        print("\nSQLite MCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        print("Type 'help' for available commands.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'help':
                    self._print_help()
                    continue
                
                try:
                    response = await self.analyze_with_claude(query)
                    print("\n" + response)
                except Exception as e:
                    print(f"\nError processing query: {str(e)}")
                    print("Type 'quit' to exit or try another query.")
                    
            except KeyboardInterrupt:
                print("\nReceived interrupt, cleaning up...")
                break
            except EOFError:
                print("\nEOF received, exiting...")
                break
            except Exception as e:
                print(f"\nUnexpected error: {str(e)}")
                print("Type 'quit' to exit or try another query.")
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            # Close the exit stack which will handle all resources
            try:
                await self.exit_stack.aclose()
                logger.info("Resources cleaned up")
            except Exception as e:
                logger.error(f"Error during exit stack cleanup: {str(e)}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def call_with_timeout(self, coro, timeout=TIMEOUT_SECONDS):
        """Execute a coroutine with a timeout.
        
        Args:
            coro: The coroutine to execute
            timeout: Timeout in seconds
            
        Returns:
            The result of the coroutine
            
        Raises:
            TimeoutError: If the operation times out
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout} seconds")
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    async def execute_with_cancellation_handling(self, coro):
        """Execute a coroutine with cancellation handling.
        
        Args:
            coro: The coroutine to execute
            
        Returns:
            The result of the coroutine
        """
        try:
            return await coro
        except asyncio.CancelledError:
            logger.info("Operation was cancelled")
            # Perform any necessary cleanup
            await self.cleanup()
            raise

    def parse_response(self, response):
        """Parse a response from the server.
        
        Args:
            response: The response from the server
            
        Returns:
            The parsed response content
        """
        try:
            # Handle TextContent objects
            if hasattr(response, "content"):
                content = response.content
                # Handle list of TextContent objects
                if isinstance(content, list) and len(content) > 0:
                    if hasattr(content[0], "text"):
                        content = content[0].text
                # Handle single TextContent object
                elif hasattr(content, "text"):
                    content = content.text
            else:
                content = response
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except (json.JSONDecodeError, TypeError):
                # Try to parse as Python literal
                try:
                    import ast
                    return ast.literal_eval(content)
                except (SyntaxError, ValueError):
                    # Return as is if not parseable
                    return content
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return None

    async def call_tool_with_retry(self, tool_name, args, max_retries=RETRY_ATTEMPTS, retry_delay=RETRY_DELAY):
        """Call a tool with retry logic.
        
        Args:
            tool_name: Name of the tool to call
            args: Arguments for the tool
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            The result of the tool call
        """
        retries = 0
        last_error = None
        
        # Use a longer timeout for specific tools that might take longer
        tool_timeouts = {
            "append_insight": 60,  # 60 seconds for append_insight
            "default": TIMEOUT_SECONDS
        }
        
        timeout = tool_timeouts.get(tool_name, tool_timeouts["default"])
        
        while retries <= max_retries:
            try:
                result = await self.call_with_timeout(
                    self.session.call_tool(tool_name, args),
                    timeout=timeout
                )
                return self.parse_response(result)
            except Exception as e:
                last_error = e
                retries += 1
                if retries <= max_retries:
                    logger.warning(f"Tool call failed, retrying ({retries}/{max_retries}): {str(e)}")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Tool call failed after {max_retries} retries: {str(e)}")
                    raise last_error


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m sqlite_client.src.client_sqlite <server_path> [db_path]")
        sys.exit(1)
    
    server_path = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    client = SQLiteMCPClient()
    try:
        await client.connect_to_server(server_path, db_path)
        await client.chat_loop()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!") 