#!/usr/bin/env python
"""
SQLite MCP Client - Test Append Insight

A simple test script to debug the append_insight functionality.
"""
import asyncio
import os
import sys
import json
import time
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import SQLiteMCPClient
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")


async def test_append_insight():
    """Test the append_insight functionality."""
    print("SQLite MCP Client - Test Append Insight")
    print("======================================\n")
    
    # Get server path from environment or use default
    server_path = os.getenv("SQLITE_SERVER_PATH", "mcp-server-sqlite")
    db_path = os.getenv("SQLITE_DB_PATH", "~/test.db")
    
    print(f"Connecting to server: {server_path}")
    print(f"Database path: {db_path}\n")
    
    # Initialize client
    client = SQLiteMCPClient()
    
    try:
        # Connect to server
        await client.connect_to_server(server_path, db_path)
        print("Connected to server successfully\n")
        
        # Print available tools
        print(f"Available tools: {[tool['name'] for tool in client.tools_cache]}\n")
        
        # Get the append_insight tool schema
        append_insight_tool = next((tool for tool in client.tools_cache if tool['name'] == 'append_insight'), None)
        if append_insight_tool:
            print("Append Insight Tool Schema:")
            print(json.dumps(append_insight_tool['input_schema'], indent=2))
            print()
        
        # Test append_insight
        print("Testing append_insight...")
        
        # Create a test insight
        insight_text = f"Test insight created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"Insight: {insight_text}")
        
        # First, try with the direct session call
        print("\n1. Testing direct session call...")
        try:
            start_time = time.time()
            direct_result = await asyncio.wait_for(
                client.session.call_tool("append_insight", {"insight": insight_text}),
                timeout=10
            )
            elapsed = time.time() - start_time
            print(f"Direct result type: {type(direct_result)}")
            print(f"Direct result: {direct_result}")
            print(f"Completed in {elapsed:.2f} seconds")
        except asyncio.TimeoutError:
            print("❌ Direct call timed out after 10 seconds")
        except Exception as e:
            print(f"❌ Error in direct call: {str(e)}")
        
        # Then try with the client method (blocking)
        print("\n2. Testing client.append_insight method (blocking)...")
        try:
            start_time = time.time()
            result = await client.append_insight(insight_text, blocking=True)
            elapsed = time.time() - start_time
            print(f"Result: {result}")
            print(f"Completed in {elapsed:.2f} seconds")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Then try with the client method (non-blocking)
        print("\n3. Testing client.append_insight method (non-blocking)...")
        try:
            start_time = time.time()
            result = await client.append_insight(insight_text, blocking=False)
            elapsed = time.time() - start_time
            print(f"Result: {result}")
            print(f"Returned in {elapsed:.2f} seconds")
            
            # Wait a bit for the background task
            print("Waiting 5 seconds for background task...")
            await asyncio.sleep(5)
            print("Continued after waiting")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Get insights memo
        print("\n4. Retrieving insights memo...")
        try:
            start_time = time.time()
            memo = await client.get_insights_memo()
            elapsed = time.time() - start_time
            
            print("\nBusiness Insights Memo:")
            print("----------------------")
            print(memo)
            print(f"Retrieved in {elapsed:.2f} seconds")
            
            if insight_text in memo:
                print("✅ Insight found in memo!")
            else:
                print("❌ Insight not found in memo!")
        except Exception as e:
            print(f"❌ Error retrieving insights memo: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        await client.cleanup()
        print("\nTest completed. Resources cleaned up.")


if __name__ == "__main__":
    asyncio.run(test_append_insight()) 