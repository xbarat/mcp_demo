# SQLite MCP Client

A Python client for interacting with the SQLite MCP Server, enabling database operations and business intelligence through the Model Context Protocol.

## Features

- Execute SQL queries (SELECT, INSERT, UPDATE, DELETE)
- Manage database schema (create tables, list tables, describe tables)
- Generate business insights and update memo resources
- Async operation with proper resource management

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sqlite_client.git
cd sqlite_client

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
import asyncio
from src.client_sqlite import SQLiteMCPClient

async def main():
    # Initialize client
    client = SQLiteMCPClient()
    
    # Connect to server
    await client.connect_to_server("path/to/sqlite_server.py")
    
    # Execute a query
    result = await client.execute_query("SELECT * FROM users LIMIT 5")
    print(result)
    
    # Clean up
    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Tools Available

- `read_query`: Execute SELECT queries
- `write_query`: Execute INSERT, UPDATE, DELETE queries
- `create_table`: Create new tables
- `list_tables`: List all tables in the database
- `describe_table`: Get schema information for a table
- `append_insight`: Add business insights to the memo resource

## License

MIT 