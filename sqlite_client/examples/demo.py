#!/usr/bin/env python
"""
SQLite MCP Client Demo

This script demonstrates how to use the SQLite MCP Client
to interact with a SQLite database through the MCP server.
"""
import asyncio
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import SQLiteMCPClient
from src.query_handler import format_query_results
from src.insight_gen import analyze_query_results, format_insights_for_memo


async def demo():
    """Run a demonstration of the SQLite MCP Client."""
    print("SQLite MCP Client Demo")
    print("======================\n")
    
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
        
        # Create tables
        print("\n1. Creating tables...")
        
        # Create users table
        create_users = """
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          email TEXT UNIQUE,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        result = await client.create_table(create_users)
        print(f"Users table created: {result['message']}")
        
        # Create orders table
        create_orders = """
        CREATE TABLE IF NOT EXISTS orders (
          id INTEGER PRIMARY KEY,
          user_id INTEGER,
          amount REAL NOT NULL,
          status TEXT,
          order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        result = await client.create_table(create_orders)
        print(f"Orders table created: {result['message']}")
        
        # List tables
        print("\n2. Listing tables...")
        tables = await client.list_tables()
        print(f"Tables in database: {tables}")
        
        # Describe tables
        print("\n3. Describing users table...")
        users_schema = await client.describe_table("users")
        print(json.dumps(users_schema, indent=2))
        
        # Insert data
        print("\n4. Inserting sample data...")
        
        # Clear existing data
        await client.execute_write_query("DELETE FROM orders")
        await client.execute_write_query("DELETE FROM users")
        
        # Insert users
        insert_users = """
        INSERT INTO users (name, email) VALUES 
          ('John Doe', 'john@example.com'),
          ('Jane Smith', 'jane@example.com'),
          ('Bob Johnson', 'bob@example.com'),
          ('Alice Brown', 'alice@example.com'),
          ('Charlie Davis', 'charlie@example.com')
        """
        users_result = await client.execute_write_query(insert_users)
        print(f"Inserted users: {users_result}")
        
        # Insert orders
        insert_orders = """
        INSERT INTO orders (user_id, amount, status) VALUES 
          (1, 99.99, 'completed'),
          (1, 49.50, 'pending'),
          (2, 149.99, 'completed'),
          (3, 29.99, 'completed'),
          (4, 199.99, 'pending'),
          (2, 59.99, 'completed'),
          (5, 79.99, 'cancelled'),
          (3, 39.99, 'completed'),
          (4, 89.99, 'pending'),
          (5, 129.99, 'completed')
        """
        orders_result = await client.execute_write_query(insert_orders)
        print(f"Inserted orders: {orders_result}")
        
        # Query data
        print("\n5. Querying data...")
        
        # Simple SELECT
        select_users = "SELECT * FROM users LIMIT 3"
        users_data = await client.execute_read_query(select_users)
        print("\nUsers:")
        print(format_query_results(users_data))
        
        # Join query
        join_query = """
        SELECT u.name, o.amount, o.status, o.order_date
        FROM users u
        JOIN orders o ON u.id = o.user_id
        ORDER BY o.order_date DESC
        LIMIT 5
        """
        join_data = await client.execute_read_query(join_query)
        print("\nUser Orders:")
        print(format_query_results(join_data))
        
        # Aggregate query
        agg_query = """
        SELECT status, COUNT(*) as order_count, SUM(amount) as total_amount
        FROM orders
        GROUP BY status
        """
        agg_data = await client.execute_read_query(agg_query)
        print("\nOrder Statistics by Status:")
        print(format_query_results(agg_data))
        
        # Generate insights
        print("\n6. Generating business insights...")
        insights = analyze_query_results(agg_query, agg_data)
        for insight in insights:
            print(f"- {insight}")
        
        # Add insight to memo
        insight_text = format_insights_for_memo(
            insights, 
            agg_query, 
            "Order Status Analysis"
        )
        try:
            print("\nAttempting to add insight to memo...")
            # Use non-blocking mode to avoid waiting for the operation to complete
            result = await client.append_insight(insight_text, blocking=False)
            print(f"Insight submission: {result['message']}")
            # Give the background task a moment to start
            await asyncio.sleep(1)
            print("Continuing with demo...")
        except Exception as e:
            print(f"Warning: Could not add insight to memo: {str(e)}")
            print("Continuing with demo...")
        
        # Get insights memo
        print("\n7. Retrieving insights memo...")
        try:
            # Wait a bit to allow the insight to be processed
            print("Waiting for insights to be processed...")
            await asyncio.sleep(3)
            
            memo = await client.get_insights_memo()
            print("\nBusiness Insights Memo:")
            print("----------------------")
            print(memo)
            
            # Check if the insight was added
            if "Order Status Analysis" in memo:
                print("\n✅ Insight successfully added to memo!")
            else:
                print("\n⚠️ Insight may not have been added to memo yet.")
        except Exception as e:
            print(f"Warning: Could not retrieve insights memo: {str(e)}")
            print("Continuing with demo...")
        
        # Interactive analysis with Claude
        print("\n8. Interactive analysis with Claude...")
        print("Type 'quit' to exit.")
        
        while True:
            query = input("\nEnter a question about the data: ")
            if query.lower() == 'quit':
                break
            
            response = await client.analyze_with_claude(query)
            print("\nClaude's response:")
            print(response)
    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        await client.cleanup()
        print("\nDemo completed. Resources cleaned up.")


if __name__ == "__main__":
    asyncio.run(demo()) 