"""
Configuration settings for the SQLite MCP Client.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Claude API settings
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

# SQLite MCP Server settings
DEFAULT_SERVER_PATH = os.getenv("SQLITE_SERVER_PATH", "mcp-server-sqlite")
DEFAULT_DB_PATH = os.getenv("SQLITE_DB_PATH", "~/test.db")

# Client settings
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "90"))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "5"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 