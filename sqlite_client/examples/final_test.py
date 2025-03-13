#!/usr/bin/env python
"""
SQLite MCP Client - Final Test

A final test script to demonstrate the working functionality.
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


async def final_test():
    """Run a final test of the SQLite MCP Client."""
    print("SQLite MCP Client - Final Test")
    print("============================\n")
    
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
        
        # 1. Create a simple table
        print("1. Creating a simple table...")
        create_test = """
        CREATE TABLE IF NOT EXISTS final_test (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          value REAL
        )
        """
        result = await client.create_table(create_test)
        print(f"Result: {result}\n")
        
        # 2. Insert some data
        print("2. Inserting data...")
        insert_data = """
        INSERT INTO final_test (name, value) VALUES 
          ('Test 1', 10.5),
          ('Test 2', 20.7),
          ('Test 3', 30.9)
        """
        result = await client.execute_write_query(insert_data)
        print(f"Result: {result}\n")
        
        # 3. Query the data
        print("3. Querying data...")
        query = "SELECT * FROM final_test"
        result = await client.execute_read_query(query)
        print(f"Result: {result}\n")
        
        # 4. Add an insight (non-blocking)
        print("4. Adding insight (non-blocking)...")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        insight1 = f"First test insight created at {timestamp}"
        
        result = await client.append_insight(insight1, blocking=False)
        print(f"Result: {result}")
        print("Waiting 2 seconds...")
        await asyncio.sleep(2)
        print("Continuing...\n")
        
        # 5. Add another insight (blocking)
        print("5. Adding another insight (blocking)...")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        insight2 = f"Second test insight created at {timestamp}"
        
        result = await client.append_insight(insight2, blocking=True)
        print(f"Result: {result}\n")
        
        # 6. Get insights memo
        print("6. Getting insights memo...")
        memo = await client.get_insights_memo()
        print("\nMemo content:")
        print("-------------")
        print(memo)
        print()
        
        # Check if insights were added
        success = True
        if insight1 not in memo:
            print(f"❌ First insight not found in memo.")
            success = False
        if insight2 not in memo:
            print(f"❌ Second insight not found in memo.")
            success = False
            
        if success:
            print("✅ Success! All insights found in memo.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        await client.cleanup()
        print("\nTest completed. Resources cleaned up.")


if __name__ == "__main__":
    asyncio.run(final_test()) 