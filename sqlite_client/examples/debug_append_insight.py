#!/usr/bin/env python
"""
SQLite MCP Client - Debug Append Insight

A detailed test script to debug the append_insight functionality
with additional logging and error handling.
"""
import asyncio
import os
import sys
import time
import traceback
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import SQLiteMCPClient
from loguru import logger

# Configure logger to show more detailed information
logger.remove()
logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}")


async def debug_append_insight():
    """Debug the append_insight functionality with detailed logging."""
    print("SQLite MCP Client - Debug Append Insight")
    print("=======================================\n")
    
    # Get server path from environment or use default
    server_path = os.getenv("SQLITE_SERVER_PATH", "mcp-server-sqlite")
    db_path = os.getenv("SQLITE_DB_PATH", "~/test.db")
    
    print(f"Connecting to server: {server_path}")
    print(f"Database path: {db_path}\n")
    
    # Initialize client
    client = SQLiteMCPClient()
    
    try:
        # Connect to server
        logger.debug("Attempting to connect to server...")
        start_time = time.time()
        await client.connect_to_server(server_path, db_path)
        connect_time = time.time() - start_time
        logger.debug(f"Connected to server in {connect_time:.2f} seconds")
        print(f"Connected to server successfully in {connect_time:.2f} seconds\n")
        
        # Print available tools
        logger.debug(f"Available tools: {[tool['name'] for tool in client.tools_cache]}")
        print(f"Available tools: {[tool['name'] for tool in client.tools_cache]}\n")
        
        # 1. Test direct tool call (low-level)
        print("1. Testing direct tool call (low-level)...")
        insight_text = "Test insight from direct tool call"
        
        try:
            logger.debug(f"Making direct tool call: append_insight with '{insight_text}'")
            start_time = time.time()
            
            # Direct call without retry logic
            result = await asyncio.wait_for(
                client.session.call_tool("append_insight", {"insight": insight_text}),
                timeout=10
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"Direct tool call completed in {elapsed:.2f} seconds")
            logger.debug(f"Raw result: {result}")
            
            print(f"Direct call result: {result}")
            print(f"Completed in {elapsed:.2f} seconds\n")
        except Exception as e:
            logger.error(f"Error in direct tool call: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"Error in direct tool call: {str(e)}\n")
        
        # 2. Test blocking append_insight
        print("2. Testing blocking append_insight...")
        insight_text = "Test insight from blocking call"
        
        try:
            logger.debug(f"Making blocking call: append_insight with '{insight_text}'")
            start_time = time.time()
            
            result = await client.append_insight(insight_text, blocking=True)
            
            elapsed = time.time() - start_time
            logger.debug(f"Blocking call completed in {elapsed:.2f} seconds")
            logger.debug(f"Result: {result}")
            
            print(f"Result: {result}")
            print(f"Completed in {elapsed:.2f} seconds\n")
        except Exception as e:
            logger.error(f"Error in blocking append_insight: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"Error in blocking append_insight: {str(e)}\n")
        
        # 3. Test non-blocking append_insight
        print("3. Testing non-blocking append_insight...")
        insight_text = "Test insight from non-blocking call"
        
        try:
            logger.debug(f"Making non-blocking call: append_insight with '{insight_text}'")
            start_time = time.time()
            
            result = await client.append_insight(insight_text, blocking=False)
            
            elapsed = time.time() - start_time
            logger.debug(f"Non-blocking call returned in {elapsed:.2f} seconds")
            logger.debug(f"Result: {result}")
            
            print(f"Result: {result}")
            print(f"Returned in {elapsed:.2f} seconds")
            
            print("Waiting for background task to complete...")
            await asyncio.sleep(5)  # Give the background task time to complete
            print("Continued after waiting\n")
        except Exception as e:
            logger.error(f"Error in non-blocking append_insight: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"Error in non-blocking append_insight: {str(e)}\n")
        
        # 4. Get insights memo
        print("4. Retrieving insights memo...")
        try:
            logger.debug("Retrieving insights memo...")
            start_time = time.time()
            
            memo = await client.get_insights_memo()
            
            elapsed = time.time() - start_time
            logger.debug(f"Retrieved memo in {elapsed:.2f} seconds")
            
            print("\nBusiness Insights Memo:")
            print("----------------------")
            print(memo)
            print(f"Retrieved in {elapsed:.2f} seconds")
        except Exception as e:
            logger.error(f"Error retrieving insights memo: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"Error retrieving insights memo: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        print("\nCleaning up resources...")
        logger.debug("Cleaning up resources...")
        start_time = time.time()
        
        await client.cleanup()
        
        elapsed = time.time() - start_time
        logger.debug(f"Cleanup completed in {elapsed:.2f} seconds")
        print(f"Resources cleaned up in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(debug_append_insight()) 