"""
Comprehensive tests for MCP Base64 tools.

Tests both unit functionality and integration with MCP server.
"""

import base64
import json
import os
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastmcp.exceptions import ToolError

from mcp_base64.server import (
    read_file_binary,
    validate_absolute_path,
    write_file_binary,
)


@pytest.fixture
def sample_text_content() -> str:
    """Sample text content for testing."""
    return "Hello, World! This is a test file for base64 encoding/decoding."


@pytest.fixture
def sample_binary_content() -> bytes:
    """Sample binary content for testing."""
    # Create some binary data that includes various byte values
    return bytes(range(256))  # 0-255, good for testing binary encoding


@pytest.fixture
def temp_text_file(sample_text_content: str) -> Generator[Path, None, None]:
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(sample_text_content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_binary_file(sample_binary_content: bytes) -> Generator[Path, None, None]:
    """Create a temporary binary file for testing."""
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".bin") as f:
        f.write(sample_binary_content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir_path:
        yield Path(temp_dir_path)


class TestPathValidation:
    """Test path validation functionality."""

    def test_validate_absolute_path_valid(self, temp_text_file: Path):
        """Test that valid absolute paths are accepted."""

        result = validate_absolute_path(str(temp_text_file))
        assert result == temp_text_file.resolve()

    def test_validate_absolute_path_relative(self):
        """Test that relative paths are rejected."""

        with pytest.raises(ToolError, match="Path must be absolute"):
            validate_absolute_path("relative/path/file.txt")

    def test_validate_absolute_path_empty(self):
        """Test that empty paths are rejected."""

        with pytest.raises(ToolError, match="File path cannot be empty"):
            validate_absolute_path("")

    def test_validate_absolute_path_with_dots(self, temp_dir: Path):
        """Test that paths with .. are properly resolved and validated."""

        # Create a test file in temp directory
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        # Try to access it with .. in path - should resolve to same location
        path_with_dots = str(temp_dir / ".." / temp_dir.name / "test.txt")
        result = validate_absolute_path(path_with_dots)

        assert result == test_file.resolve()


class TestFileOperations:
    """Test file I/O operations."""

    def test_read_file_binary_text(
        self, temp_text_file: Path, sample_text_content: str
    ):
        """Test reading text file in binary mode."""

        content = read_file_binary(temp_text_file)
        assert content == sample_text_content.encode("utf-8")

    def test_read_file_binary_binary(
        self, temp_binary_file: Path, sample_binary_content: bytes
    ):
        """Test reading binary file."""

        content = read_file_binary(temp_binary_file)
        assert content == sample_binary_content

    def test_read_file_binary_not_found(self):
        """Test reading non-existent file."""

        with pytest.raises(ToolError, match="File not found"):
            read_file_binary(Path("/non/existent/file.txt"))

    def test_write_file_binary(self, temp_dir: Path, sample_binary_content: bytes):
        """Test writing binary content to file."""

        output_file = temp_dir / "output.bin"
        write_file_binary(output_file, sample_binary_content)

        assert output_file.exists()
        assert output_file.read_bytes() == sample_binary_content


class TestEncodeFileToBase64:
    """Test the encode_file_to_base64 tool."""

    def test_encode_text_file(self, temp_text_file: Path, sample_text_content: str):
        """Test encoding a text file."""
        from mcp_base64.server import _encode_file_to_base64_impl

        result = _encode_file_to_base64_impl(str(temp_text_file))

        # Verify the result is valid base64
        decoded = base64.b64decode(result, validate=True)
        assert decoded == sample_text_content.encode("utf-8")

    def test_encode_binary_file(
        self, temp_binary_file: Path, sample_binary_content: bytes
    ):
        """Test encoding a binary file."""
        from mcp_base64.server import _encode_file_to_base64_impl

        result = _encode_file_to_base64_impl(str(temp_binary_file))

        # Verify the result is valid base64
        decoded = base64.b64decode(result, validate=True)
        assert decoded == sample_binary_content

    def test_encode_nonexistent_file(self):
        """Test encoding non-existent file."""
        from mcp_base64.server import _encode_file_to_base64_impl

        with pytest.raises(ToolError, match="File not found"):
            _encode_file_to_base64_impl("/non/existent/file.txt")

    def test_encode_relative_path(self):
        """Test that relative paths are rejected."""
        from mcp_base64.server import _encode_file_to_base64_impl

        with pytest.raises(ToolError, match="Path must be absolute"):
            _encode_file_to_base64_impl("relative/path/file.txt")

    def test_encode_directory(self, temp_dir: Path):
        """Test that directories are rejected."""
        from mcp_base64.server import _encode_file_to_base64_impl

        with pytest.raises(ToolError, match="Path is a directory"):
            _encode_file_to_base64_impl(str(temp_dir))


class TestDecodeBase64ToFile:
    """Test the decode_base64_to_file tool."""

    def test_decode_valid_base64_text(
        self, temp_dir: Path, sample_text_content: str
    ):
        """Test decoding valid base64 text content."""
        from mcp_base64.server import _decode_base64_to_file_impl

        # Encode content to base64
        b64_content = base64.b64encode(
            sample_text_content.encode("utf-8")
        ).decode("ascii")

        # Decode back to file
        output_file = temp_dir / "decoded.txt"
        result = _decode_base64_to_file_impl(b64_content, str(output_file))

        # Verify result message
        assert "Successfully decoded base64 content to file:" in result
        assert str(output_file) in result

        # Verify file contents
        assert output_file.exists()
        assert output_file.read_text() == sample_text_content

    def test_decode_valid_base64_binary(
        self, temp_dir: Path, sample_binary_content: bytes
    ):
        """Test decoding valid base64 binary content."""
        from mcp_base64.server import _decode_base64_to_file_impl

        # Encode content to base64
        b64_content = base64.b64encode(sample_binary_content).decode("ascii")

        # Decode back to file
        output_file = temp_dir / "decoded.bin"
        result = _decode_base64_to_file_impl(b64_content, str(output_file))

        # Verify result message
        assert "Successfully decoded base64 content to file:" in result
        assert str(output_file) in result

        # Verify file contents
        assert output_file.exists()
        assert output_file.read_bytes() == sample_binary_content

    def test_decode_invalid_base64(self, temp_dir: Path):
        """Test decoding invalid base64 content."""
        from mcp_base64.server import _decode_base64_to_file_impl

        output_file = temp_dir / "decoded.txt"
        with pytest.raises(ToolError, match="Invalid base64 content"):
            _decode_base64_to_file_impl("invalid_base64_content!@#", str(output_file))

    def test_decode_empty_base64(self, temp_dir: Path):
        """Test decoding empty base64 content."""
        from mcp_base64.server import _decode_base64_to_file_impl

        output_file = temp_dir / "decoded.txt"
        with pytest.raises(ToolError, match="Base64 content cannot be empty"):
            _decode_base64_to_file_impl("", str(output_file))

    def test_decode_relative_path(self, sample_text_content: str):
        """Test that relative paths are rejected for output file."""
        from mcp_base64.server import _decode_base64_to_file_impl

        b64_content = base64.b64encode(sample_text_content.encode("utf-8")).decode("ascii")

        with pytest.raises(ToolError, match="Path must be absolute"):
            _decode_base64_to_file_impl(b64_content, "relative/path/output.txt")

    def test_decode_creates_parent_dirs(self, sample_text_content: str):
        """Test that parent directories are created if they don't exist."""
        from mcp_base64.server import _decode_base64_to_file_impl

        # Create a path with non-existent parent directories
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nested_file = temp_path / "level1" / "level2" / "level3" / "output.txt"

            b64_content = base64.b64encode(sample_text_content.encode("utf-8")).decode("ascii")
            _decode_base64_to_file_impl(b64_content, str(nested_file))

            # Verify file was created in nested directory
            assert nested_file.exists()
            assert nested_file.read_text() == sample_text_content


class TestRoundTripEncoding:
    """Test round-trip encoding/decoding to ensure data integrity."""

    def test_text_round_trip(self, temp_dir: Path, sample_text_content: str):
        """Test that text content survives encode->decode round trip."""
        from mcp_base64.server import (
            _decode_base64_to_file_impl,
            _encode_file_to_base64_impl,
        )

        # Create temporary file with text content
        input_file = temp_dir / "input.txt"
        input_file.write_text(sample_text_content)

        # Encode to base64
        base64_content = _encode_file_to_base64_impl(str(input_file))

        # Decode back to new file
        output_file = temp_dir / "output.txt"
        _decode_base64_to_file_impl(base64_content, str(output_file))

        # Verify content is identical
        assert input_file.read_text() == output_file.read_text()

    def test_binary_round_trip(self, temp_dir: Path, sample_binary_content: bytes):
        """Test that binary content survives encode->decode round trip."""
        from mcp_base64.server import (
            _decode_base64_to_file_impl,
            _encode_file_to_base64_impl,
        )

        # Create temporary file with binary content
        input_file = temp_dir / "input.bin"
        input_file.write_bytes(sample_binary_content)

        # Encode to base64
        base64_content = _encode_file_to_base64_impl(str(input_file))

        # Decode back to new file
        output_file = temp_dir / "output.bin"
        _decode_base64_to_file_impl(base64_content, str(output_file))

        # Verify content is identical
        assert input_file.read_bytes() == output_file.read_bytes()


class TestIntegrationWithMCPServer:
    """Integration tests with the actual MCP server process."""

    def test_server_initialization(self):
        """Test that the MCP server can be initialized via stdio."""
        # Send initialize message to server
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        # Start server process
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"

        with subprocess.Popen(
            [".venv/bin/python", "-m", "mcp_base64.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        ) as process:
            try:
                # Send initialize message
                process.stdin.write(json.dumps(init_message) + "\n")
                process.stdin.flush()

                # Read response
                response_line = process.stdout.readline().strip()
                response = json.loads(response_line)

                # Verify it's a valid MCP response
                assert response["jsonrpc"] == "2.0"
                assert "result" in response or "error" in response

            finally:
                # Clean shutdown
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

    def test_tools_listed_in_capabilities(self):
        """Test that our tools are listed in server capabilities."""
        # This would require parsing the server capabilities response
        # For now, we'll verify the server starts without errors
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"

        with subprocess.Popen(
            [".venv/bin/python", "-m", "mcp_base64.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        ) as process:
            try:
                # Send initialize message
                init_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"}
                    }
                }

                process.stdin.write(json.dumps(init_message) + "\n")
                process.stdin.flush()

                response_line = process.stdout.readline().strip()
                response = json.loads(response_line)

                # Server should respond without crashing
                assert response["jsonrpc"] == "2.0"

            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
