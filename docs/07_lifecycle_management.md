# Lifecycle Management in MCP

## The Problem
When running MCP servers in production, developers face several critical challenges:
1. Database connections remain open after server shutdown
2. Resources aren't properly cleaned up
3. No initialization of required services on startup
4. Memory leaks from unmanaged resources
5. No way to gracefully handle startup/shutdown

Here's what happens without lifecycle management:

```python
# Without Lifecycle Management - Problems waiting to happen
from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("Demo")

# Global connection - Bad practice!
db = sqlite3.connect("database.db")

@mcp.tool()
def query_data(sql: str) -> str:
    try:
        # Using global connection
        result = db.execute(sql).fetchall()
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    # Connection never closes!
```

Problems with this approach:
- Database connection stays open indefinitely
- No proper initialization
- Resources leak
- Crashes can leave things in bad state
- No cleanup on shutdown

## The Solution: Lifecycle Management

MCP provides lifecycle management through the lifespan handler:

```python
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator
import sqlite3
from loguru import logger

# Define your application state
@dataclass
class AppState:
    """Application state and resources"""
    db: sqlite3.Connection
    is_ready: bool = False
    query_count: int = 0

# Lifecycle manager
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    """Manage application lifecycle"""
    logger.info("🚀 Starting server...")
    
    # Initialize resources
    db = sqlite3.connect("database.db")
    state = AppState(db=db)
    
    try:
        # Startup tasks
        logger.info("📡 Initializing database...")
        db.execute("PRAGMA journal_mode=WAL")  # Example initialization
        state.is_ready = True
        logger.info("✅ Server ready!")
        
        yield state  # Server runs here
        
    finally:
        # Cleanup tasks
        logger.info("🔄 Shutting down...")
        db.close()
        logger.info("✅ Cleanup complete!")

# Create MCP server with lifecycle management
mcp = FastMCP("Demo", lifespan=app_lifespan)

@mcp.tool()
async def query_data(sql: str, ctx: Context) -> str:
    """Query with managed database connection"""
    state = ctx.state  # Get managed state
    
    try:
        result = state.db.execute(sql).fetchall()
        state.query_count += 1  # Track queries
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

## Key Benefits

### 1. Resource Management
```python
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    # Initialize
    db = sqlite3.connect("database.db")
    try:
        yield AppState(db=db)
    finally:
        # Cleanup
        db.close()
```
- Resources properly initialized
- Guaranteed cleanup
- No memory leaks

### 2. State Management
```python
@dataclass
class AppState:
    db: sqlite3.Connection
    query_count: int = 0
```
- Centralized state management
- Type-safe state access
- Shared resources

### 3. Startup/Shutdown Hooks
```python
# In lifespan manager
try:
    # Startup tasks
    await initialize_resources()
    yield state
finally:
    # Shutdown tasks
    await cleanup_resources()
```
- Controlled startup sequence
- Graceful shutdown
- Resource cleanup

## Real-World Example

Here's a complete example with multiple resources:

```python
@dataclass
class AppState:
    db: sqlite3.Connection
    cache: dict
    start_time: float
    query_count: int = 0

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    """Production-ready lifecycle management"""
    import time
    
    logger.info("🚀 Starting server initialization...")
    start_time = time.time()
    
    # Initialize resources
    try:
        # 1. Database
        logger.info("📡 Connecting to database...")
        db = sqlite3.connect("database.db")
        db.execute("PRAGMA journal_mode=WAL")
        
        # 2. Cache
        logger.info("💾 Initializing cache...")
        cache = {}
        
        # 3. Create state
        state = AppState(
            db=db,
            cache=cache,
            start_time=start_time
        )
        
        logger.info("✅ Initialization complete!")
        yield state
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        logger.info("🔄 Starting cleanup...")
        
        # 1. Close database
        try:
            db.close()
            logger.info("✅ Database connection closed")
        except Exception as e:
            logger.error(f"❌ Database cleanup failed: {e}")
            
        # 2. Clear cache
        try:
            cache.clear()
            logger.info("✅ Cache cleared")
        except Exception as e:
            logger.error(f"❌ Cache cleanup failed: {e}")
        
        logger.info("✅ Cleanup complete!")
```

## Before vs After

### Without Lifecycle Management:
- Resources leak
- Unpredictable startup
- Crash-prone shutdown
- No state management
- Hard to debug issues

### With Lifecycle Management:
- Controlled resource lifecycle
- Clean startup sequence
- Graceful shutdown
- Centralized state
- Better error handling

## Best Practices

1. **Define Clear State**
```python
@dataclass
class AppState:
    """Document your state clearly"""
    db: sqlite3.Connection
    is_ready: bool = False
```

2. **Handle Errors**
```python
try:
    # Initialize
    yield state
except Exception:
    # Handle startup/runtime errors
finally:
    # Always cleanup
```

3. **Log Important Events**
```python
logger.info("Starting up...")
logger.error("Failed to initialize...")
```

4. **Clean Up Resources**
```python
finally:
    db.close()
    cache.clear()
```

## Conclusion

Lifecycle management transforms your MCP server from a potential resource leak into a robust, production-ready application:
- Resources are properly managed
- Startup/shutdown is controlled
- State is centralized
- Cleanup is guaranteed
- Errors are handled gracefully

By implementing proper lifecycle management, you create a more reliable and maintainable MCP server that's ready for production use. 