"""
Tests for SQLite MCP Client.
"""
import pytest
import asyncio
import os
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import SQLiteMCPClient


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization."""
    client = SQLiteMCPClient()
    assert client is not None
    assert client.session is None
    assert client.tools_cache is None


@pytest.mark.asyncio
async def test_query_validation():
    """Test query validation."""
    from src.query_handler import validate_query, get_query_type
    
    # Test valid queries
    valid_select = "SELECT * FROM users"
    is_valid, error = validate_query(valid_select)
    assert is_valid
    assert error is None
    assert get_query_type(valid_select) == "SELECT"
    
    valid_insert = "INSERT INTO users (name, email) VALUES ('Test', 'test@example.com')"
    is_valid, error = validate_query(valid_insert)
    assert is_valid
    assert error is None
    assert get_query_type(valid_insert) == "INSERT"
    
    # Test invalid queries
    invalid_query = "SELECT * FROM"
    is_valid, error = validate_query(invalid_query)
    assert not is_valid
    assert error is not None
    
    dangerous_query = "SELECT * FROM users; DROP TABLE users"
    is_valid, error = validate_query(dangerous_query)
    assert not is_valid
    assert error is not None


@pytest.mark.asyncio
async def test_insight_generation():
    """Test insight generation."""
    from src.insight_gen import analyze_query_results, format_insights_for_memo
    
    # Sample query results
    query = "SELECT status, COUNT(*) as order_count, SUM(amount) as total_amount FROM orders GROUP BY status"
    results = [
        {"status": "completed", "order_count": 5, "total_amount": 479.95},
        {"status": "pending", "order_count": 3, "total_amount": 339.48},
        {"status": "cancelled", "order_count": 1, "total_amount": 79.99}
    ]
    
    # Generate insights
    insights = analyze_query_results(query, results)
    assert len(insights) > 0
    
    # Format insights for memo
    memo_text = format_insights_for_memo(insights, query, "Order Status Analysis")
    assert "Order Status Analysis" in memo_text
    assert "```sql" in memo_text


@pytest.mark.asyncio
async def test_result_formatting():
    """Test result formatting."""
    from src.query_handler import format_query_results
    
    # Sample results
    results = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ]
    
    # Format results
    formatted = format_query_results(results)
    assert "id" in formatted
    assert "name" in formatted
    assert "email" in formatted
    assert "John Doe" in formatted
    assert "Jane Smith" in formatted


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 