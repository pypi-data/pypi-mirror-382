# RESTART.md - State Handoff / Restart Kit

## Summary
Building a Python MCP Server for Base64 file conversion with stdio transport using FastMCP SDK.

## Decisions/Assumptions
- **SDK**: FastMCP (chosen for maturity and better tooling)
- **Transport**: stdio (as specified)
- **Python Version**: ≥ 3.10 with type hints
- **Project Structure**: Following strict layout from task file
- **Paths**: Absolute paths only, with validation against path traversal

## Commands

### Setup
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .[dev]
```

### Run Server (stdio)
```bash
PYTHONPATH=src ./.venv/bin/python -m mcp_base64.server
```

### JSON-RPC Smoke Test
```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n' | PYTHONPATH=src ./.venv/bin/python -m mcp_base64.server
```

### Tests
```bash
./.venv/bin/python -m pytest -q
```

### Linting
```bash
./.venv/bin/python -m ruff check .
```

## File Map
- `pyproject.toml` - Build system, dependencies, tool configs
- `src/mcp_base64/server.py` - Main MCP server with stdio transport
- `tests/test_tools.py` - Unit and integration tests
- `README.md` - Documentation (to be created)
- `.github/workflows/ci.yml` - CI pipeline (to be created)
- `artifacts/` - Test logs and outputs
- `RESTART.md` - This file

## Dependencies
- `fastmcp>=0.2.0` - MCP server framework
- `pydantic>=2.0.0` - Parameter descriptions and validation
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support
- `ruff>=0.1.0` - Linting and formatting

## Environment Variables
- `PYTHONPATH=src` - For module imports
- No secrets or external API keys required

## Tools API Contract

### encode_file_to_base64(file_path: str) -> str
**Description**: Encodes a file to base64 string
**Parameters**:
- `file_path` (str): Absolute path to file to encode (required)
**Returns**: Base64 encoded string
**Errors**: ToolError for invalid paths, permission issues, or file not found

### decode_base64_to_file(base64_content: str, file_path: str) -> str
**Description**: Decodes base64 string to file
**Parameters**:
- `base64_content` (str): Base64 encoded content (required)
- `file_path` (str): Absolute path where to save decoded file (required)
**Returns**: Success message with file path
**Errors**: ToolError for invalid base64, invalid paths, or permission issues

## Test Plan

### Unit Tests
- Test encode_file_to_base64 with binary and text files
- Test decode_base64_to_file with valid and invalid base64
- Test path validation (reject relative paths, traversal attempts)
- Test error handling for missing files, permission issues

### Integration Tests
- Test stdio JSON-RPC communication
- Test round-trip encoding/decoding with sample files
- Test parameter descriptions appear in MCP schema
- Test server initialization and cleanup

### Sample Data
- Create `tests/sample.bin` - Small binary file for testing
- Use existing test files in `doc/test-files/` for additional testing

## Acceptance Criteria
1. `initialize` over stdio returns valid MCP response
2. Encode→decode round-trip reproduces identical bytes
3. All tools show parameter descriptions in MCP UI
4. Absolute path validation prevents directory traversal
5. Comprehensive error handling with structured ToolError responses

## TODOs/Next Steps
1. Implement core server and tools ✅ (in progress)
2. Add comprehensive tests
3. Create README and CI pipeline
4. Run verification tests and capture logs
5. Ensure all acceptance criteria met

## Resume Instructions
If restarting development:
1. Install dependencies with `./.venv/bin/python -m pip install -e .[dev]`
2. Run tests with `./.venv/bin/python -m pytest -q`
3. Run server with `PYTHONPATH=src ./.venv/bin/python -m mcp_base64.server`
4. Check `artifacts/` for latest test logs
