# SQLite MCP Client Debug Plan

## 1. Resource Cleanup Issues

### Problem
The client is experiencing errors during cleanup, particularly when operations are interrupted or canceled. The error log shows:
```
Error during cleanup: unhandled errors in a TaskGroup (1 sub-exception)
```

### Root Cause Analysis
- The `AsyncExitStack` is not properly handling task cancellation
- When a task is canceled (e.g., by KeyboardInterrupt), the cleanup process encounters unhandled exceptions
- The error occurs in the `aclose()` method of the `AsyncExitStack`

### Solution Steps
1. Implement proper exception handling in the cleanup method:
   ```python
   async def cleanup(self):
       """Clean up resources."""
       try:
           if self.session:
               # First close the session
               try:
                   await self.session.close()
               except Exception as e:
                   logger.error(f"Error closing session: {str(e)}")
           
           # Then close the exit stack
           try:
               await self.exit_stack.aclose()
               logger.info("Resources cleaned up")
           except Exception as e:
               logger.error(f"Error during exit stack cleanup: {str(e)}")
       except Exception as e:
           logger.error(f"Error during cleanup: {str(e)}")
   ```

2. Add timeout handling for long-running operations:
   ```python
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
   ```

3. Implement graceful cancellation handling:
   ```python
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
   ```

## 2. Response Parsing Issues

### Problem
The client has inconsistent handling of responses from the server, particularly with TextContent objects. This causes errors when parsing responses.

### Root Cause Analysis
- The server returns responses as TextContent objects, but the client sometimes expects direct string content
- The response format is inconsistent across different tools
- Error handling for parsing failures is inadequate

### Solution Steps
1. Create a unified response parsing function:
   ```python
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
   ```

2. Implement retry logic for transient errors:
   ```python
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
       
       while retries <= max_retries:
           try:
               result = await self.session.call_tool(tool_name, args)
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
   ```

## 3. Interactive Mode Improvements

### Problem
The interactive mode lacks robustness, particularly in error handling and user experience.

### Root Cause Analysis
- Error recovery is minimal
- No command history
- Limited help and guidance for users

### Solution Steps
1. Add command history using the `readline` module:
   ```python
   def setup_readline():
       """Set up readline for command history."""
       try:
           import readline
           import atexit
           import os
           
           histfile = os.path.join(os.path.expanduser("~"), ".sqlite_mcp_history")
           try:
               readline.read_history_file(histfile)
               readline.set_history_length(1000)
           except FileNotFoundError:
               pass
           
           atexit.register(readline.write_history_file, histfile)
           return True
       except (ImportError, ModuleNotFoundError):
           return False
   ```

2. Implement better error recovery in the chat loop:
   ```python
   async def chat_loop(self):
       """Run an interactive chat loop."""
       if not self.session:
           raise RuntimeError("Not connected to server")
       
       # Set up readline if available
       has_readline = setup_readline()
       if has_readline:
           print("Command history is enabled.")
       
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
   ```

3. Add a help command:
   ```python
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
   ```

## 4. Performance Optimization

### Problem
The client could benefit from performance optimizations, particularly for repeated operations.

### Root Cause Analysis
- No connection pooling
- No caching for frequently used queries
- Memory usage not optimized

### Solution Steps
1. Implement basic caching for query results:
   ```python
   class QueryCache:
       """Simple cache for query results."""
       
       def __init__(self, max_size=100, ttl=300):
           """Initialize the cache.
           
           Args:
               max_size: Maximum number of items in the cache
               ttl: Time to live in seconds
           """
           self.cache = {}
           self.max_size = max_size
           self.ttl = ttl
       
       def get(self, key):
           """Get an item from the cache.
           
           Args:
               key: Cache key
               
           Returns:
               The cached item or None if not found or expired
           """
           if key in self.cache:
               item, timestamp = self.cache[key]
               if time.time() - timestamp < self.ttl:
                   return item
               else:
                   # Remove expired item
                   del self.cache[key]
           return None
       
       def set(self, key, value):
           """Set an item in the cache.
           
           Args:
               key: Cache key
               value: Value to cache
           """
           # Remove oldest item if cache is full
           if len(self.cache) >= self.max_size:
               oldest_key = min(self.cache, key=lambda k: self.cache[k][1])
               del self.cache[oldest_key]
           
           self.cache[key] = (value, time.time())
       
       def clear(self):
           """Clear the cache."""
           self.cache.clear()
   ```

2. Add the cache to the client:
   ```python
   def __init__(self):
       """Initialize the SQLite MCP client."""
       # Initialize session and client objects
       self.session: Optional[ClientSession] = None
       self.exit_stack = AsyncExitStack()
       self.anthropic = AsyncAnthropic()
       self.tools_cache = None
       
       # Add query cache
       self.query_cache = QueryCache()
       
       # Configure logger
       logger.remove()
       logger.add(sys.stderr, level="INFO")
   ```

3. Use the cache in query methods:
   ```python
   async def execute_read_query(self, query: str, use_cache=True) -> List[Dict[str, Any]]:
       """Execute a SELECT query.
       
       Args:
           query: SQL SELECT query
           use_cache: Whether to use the cache
           
       Returns:
           List of result rows as dictionaries
       """
       if not self.session:
           raise RuntimeError("Not connected to server")
       
       # Check cache if enabled
       if use_cache:
           cached_result = self.query_cache.get(query)
           if cached_result is not None:
               logger.info(f"Using cached result for query: {query}")
               return cached_result
       
       logger.info(f"Executing read query: {query}")
       result = await self.session.call_tool("read_query", {"query": query})
       try:
           # Parse the response
           parsed_result = self.parse_response(result)
           
           # Cache the result if enabled
           if use_cache:
               self.query_cache.set(query, parsed_result)
           
           return parsed_result
       except Exception as e:
           logger.error(f"Failed to parse response: {result.content}")
           return []
   ```

## Implementation Timeline

1. **Day 1: Resource Cleanup Fixes**
   - Implement improved cleanup method
   - Add timeout handling
   - Test cancellation handling

2. **Day 2: Response Parsing Improvements**
   - Create unified response parsing function
   - Implement retry logic
   - Update all tool methods to use the new parsing

3. **Day 3: Interactive Mode Enhancements**
   - Add command history
   - Implement better error recovery
   - Add help command

4. **Day 4: Performance Optimizations**
   - Implement query caching
   - Optimize memory usage
   - Add connection pooling if needed

5. **Day 5: Testing and Documentation**
   - Test all fixes
   - Update documentation
   - Create additional examples 