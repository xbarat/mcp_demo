#!/usr/bin/env python
"""
SQLite MCP Client - Simple Insight Test

A very simple test script to verify the append_insight functionality.
"""
import asyncio
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import SQLiteMCPClient
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")


async def simple_insight_test():
    """Run a simple test of the append_insight functionality."""
    print("SQLite MCP Client - Simple Insight Test")
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
        
        # Add an insight (non-blocking)
        print("Adding insight (non-blocking)...")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        insight = f"Simple test insight created at {timestamp}"
        
        result = await client.append_insight(insight, blocking=False)
        print(f"Result: {result}")
        print("Waiting 3 seconds for background task...")
        await asyncio.sleep(3)
        
        # Try to get the memo
        print("\nAttempting to get insights memo...")
        try:
            memo = await client.get_insights_memo()
            print("\nMemo content:")
            print("-------------")
            print(memo)
            
            if insight in memo:
                print("\n✅ Success! Insight found in memo.")
            else:
                print("\n❌ Insight not found in memo.")
        except Exception as e:
            print(f"\n❌ Error retrieving memo: {e}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        await client.cleanup()
        print("\nTest completed. Resources cleaned up.")


if __name__ == "__main__":
    asyncio.run(simple_insight_test()) 