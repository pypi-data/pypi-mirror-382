# MCP Base64 Server

A Python MCP (Model Context Protocol) server for Base64 file conversion with stdio transport.

## Features

- **encode_file_to_base64**: Encode any file to base64 string
- **decode_base64_to_file**: Decode base64 content to file
- Binary-safe: Handles both text and binary files correctly

## Usage

### IDE Configuration
For IDE plugins, add this server to your MCP configuration JSON:
```json
{
  "mcpServers": {
    "ollama": {
      "command": "uvx",
      "args": [
        "mcp-ollama"
      ]
    }
  }
}
```

### Direct Execution
```bash
git clone https://github.com/Wuodan/mcp-base64.git
cd mcp-base64
python3 -m venv .venv
./.venv/bin/python -m pip install -e .
./.venv/bin/python -m mcp_base64.server
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
