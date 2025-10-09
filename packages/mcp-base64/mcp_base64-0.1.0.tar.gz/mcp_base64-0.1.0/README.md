# MCP Base64 Server

A Python MCP (Model Context Protocol) server for Base64 file conversion with stdio transport.

## Features

- **encode_file_to_base64**: Encode any file to base64 string
- **decode_base64_to_file**: Decode base64 content to file
- Security-focused: Only accepts absolute paths, validates against path traversal
- Binary-safe: Handles both text and binary files correctly

## Installation

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
```

## Usage

### Direct Execution

Run the MCP server:

```bash
PYTHONPATH=src ./.venv/bin/python -m mcp_base64.server
```

### IDE Configuration

For IDE plugins, add this server to your MCP configuration JSON:

```json
{
  "mcpServers": {
    "mcp-base64": {
      "command": "<PATH-TO-PROJECT/.venv/bin/python",
      "args": ["-m", "mcp_base64.server"]
    }
  }
}
```

## Tools

### encode_file_to_base64(file_path: str) -> str
Encodes a file to base64 string.

**Parameters:**
- `file_path` (str): Absolute path to file to encode

**Returns:** Base64 encoded string

### decode_base64_to_file(base64_content: str, file_path: str) -> str
Decodes base64 string to file.

**Parameters:**
- `base64_content` (str): Base64 encoded content
- `file_path` (str): Absolute path where to save decoded file

**Returns:** Success message with file path

## Development

Install development dependencies:

```bash
./.venv/bin/python -m pip install -e .[dev]
```

Run tests:

```bash
./.venv/bin/python -m pytest -q
```

Run linting:

```bash
./.venv/bin/python -m ruff check .
```

## License

See LICENSE file for details.
