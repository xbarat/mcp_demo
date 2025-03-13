# Changelog

## [0.2.1] - 2025-03-13

### Added
- Local storage for insights to ensure they're always available
- Fallback mechanism for memo retrieval when server-side retrieval fails
- Improved error handling for resource operations

### Fixed
- Fixed issues with `append_insight` timing out due to resource update notifications
- Improved `get_insights_memo` to handle server-side retrieval failures
- Reduced timeouts for direct tool calls to avoid long waits

### Changed
- Modified `append_insight` to use a shorter timeout (5 seconds) for direct calls
- Updated demo script to handle potential failures gracefully
- Added additional test scripts for debugging and verification

### Not Working
- Client is not retrieving insights from the server; Tempmorary fallback to self._insights
- Interactive mode failed to work with discrpancies in Claude API call

## [0.2.0] - 2025-03-13

### Added
- Non-blocking mode for `append_insight` method to prevent demo from hanging
- Tool-specific timeout settings to handle long-running operations
- Background task processing for insights submission
- Better error handling in demo script with graceful fallbacks

### Fixed
- Fixed timeout issues with `append_insight` tool
- Improved response parsing for TextContent objects
- Fixed cleanup errors during task cancellation
- Enhanced error recovery in interactive mode

### Changed
- Increased timeout for `append_insight` tool to 60 seconds
- Modified retry logic to use tool-specific delay settings
- Updated demo script to use non-blocking approach for insights

## [0.1.0] - 2025-03-12

### Added
- Initial implementation of SQLite MCP Client
- Core SQL operations (read_query, write_query, create_table)
- Schema operations (list_tables, describe_table)
- Business intelligence features (append_insight, get_insights_memo)
- Interactive mode with Claude integration
- Demo script showcasing client capabilities 