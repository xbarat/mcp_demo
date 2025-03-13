#!/usr/bin/env python
"""
SQLite MCP Client - Test Create Table

A simple test script to debug the create_table functionality.
"""
import asyncio
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import SQLiteMCPClient
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")


async def test_create_table():
    """Test the create_table functionality."""
    print("SQLite MCP Client - Test Create Table")
    print("====================================\n")
    
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
        
        # Get the create_table tool schema
        create_table_tool = next((tool for tool in client.tools_cache if tool['name'] == 'create_table'), None)
        if create_table_tool:
            print("Create Table Tool Schema:")
            print(json.dumps(create_table_tool['input_schema'], indent=2))
            print()
        
        # Test create_table
        print("Testing create_table...")
        
        # Create a test table
        create_test = """
        CREATE TABLE IF NOT EXISTS test_table (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          value REAL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        print(f"SQL: {create_test.strip()}")
        
        # First, try with the direct session call
        print("\n1. Testing direct session call...")
        try:
            direct_result = await client.session.call_tool("create_table", {"query": create_test})
            print(f"Direct result type: {type(direct_result)}")
            print(f"Direct result: {direct_result}")
        except Exception as e:
            print(f"Error in direct call: {str(e)}")
        
        # Then try with the client method
        print("\n2. Testing client.create_table method...")
        try:
            result = await client.create_table(create_test)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        # List tables to verify
        print("\n3. Verifying table creation...")
        tables = await client.list_tables()
        print(f"Tables in database: {tables}")
        
        if "test_table" in tables:
            print("✅ Test table created successfully!")
        else:
            print("❌ Test table not found in database!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        await client.cleanup()
        print("\nTest completed. Resources cleaned up.")


if __name__ == "__main__":
    asyncio.run(test_create_table()) 