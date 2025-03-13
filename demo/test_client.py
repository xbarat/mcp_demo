import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession
from loguru import logger

class SQLExplorerClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        """Connect to the MCP server using mcp connect"""
        import subprocess
        
        process = subprocess.Popen(
            ["mcp", "connect"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.session = await ClientSession.connect_stdio(process.stdout, process.stdin)
        await self.session.initialize()
        logger.info("Connected to SQL Explorer server")

    async def run_tests(self):
        """Run SQL Explorer tests"""
        try:
            # Test 1: Basic Query
            logger.info("Test 1: Basic query")
            result = await self.session.call_tool(
                "query_data",
                arguments={"sql": "SELECT * FROM online_retail LIMIT 3"}
            )
            print("\n=== Sample Data ===")
            print(result)
            
            # Test 2: Sales Analysis
            logger.info("Test 2: Sales analysis for UK")
            uk_sales = await self.session.call_tool(
                "analyze_sales",
                arguments={"country": "United Kingdom"}
            )
            print("\n=== UK Sales Analysis ===")
            print(uk_sales)
            
            # Test 3: Global Sales
            logger.info("Test 3: Global sales analysis")
            global_sales = await self.session.call_tool(
                "analyze_sales",
                arguments={}
            )
            print("\n=== Global Sales Analysis ===")
            print(global_sales)
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.exit_stack.aclose()

async def main():
    client = SQLExplorerClient()
    try:
        await client.connect()
        await client.run_tests()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())