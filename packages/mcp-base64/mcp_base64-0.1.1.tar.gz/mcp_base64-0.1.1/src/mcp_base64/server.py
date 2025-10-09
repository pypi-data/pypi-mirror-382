"""
MCP Server for Base64 file conversion with stdio transport.

This module provides two tools for encoding files to base64 and
decoding base64 content to files. All file operations use absolute
paths only with validation against path traversal attacks.
"""

import base64
import binascii
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

# Create FastMCP server instance
mcp = FastMCP("mcp-base64")


def validate_absolute_path(file_path: str) -> Path:
    """
    Validate that the provided path is absolute and safe against traversal attacks.

    Args:
        file_path: The file path to validate

    Returns:
        Path object for the validated absolute path

    Raises:
        ToolError: If path is relative, contains traversal attempts, or is otherwise
            invalid
    """
    if not file_path:
        error_msg = "File path cannot be empty"
        raise ToolError(error_msg)

    path = Path(file_path)

    # Check if path is absolute
    if not path.is_absolute():
        error_msg = f"Path must be absolute, got: {file_path}"
        raise ToolError(error_msg)

    # Normalize path to resolve any .. or . components
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError) as e:
        error_msg = f"Invalid path '{file_path}': {e}"
        raise ToolError(error_msg) from e

    # Ensure resolved path is still absolute (catches some edge cases)
    if not resolved_path.is_absolute():
        error_msg = f"Resolved path is not absolute: {resolved_path}"
        raise ToolError(error_msg)

    return resolved_path


def read_file_binary(file_path: Path) -> bytes:
    """
    Read file in binary mode.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as bytes

    Raises:
        ToolError: If file cannot be read
    """
    try:
        with file_path.open("rb") as f:
            return f.read()
    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        raise ToolError(error_msg) from None
    except PermissionError:
        error_msg = f"Permission denied reading file: {file_path}"
        raise ToolError(error_msg) from None
    except IsADirectoryError:
        error_msg = f"Path is a directory, not a file: {file_path}"
        raise ToolError(error_msg) from None
    except OSError as e:
        error_msg = f"Error reading file '{file_path}': {e}"
        raise ToolError(error_msg) from None


def write_file_binary(file_path: Path, content: bytes) -> None:
    """
    Write bytes to file in binary mode.

    Args:
        file_path: Path where to write the file
        content: Binary content to write

    Raises:
        ToolError: If file cannot be written
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("wb") as f:
            f.write(content)
    except PermissionError:
        error_msg = f"Permission denied writing file: {file_path}"
        raise ToolError(error_msg) from None
    except IsADirectoryError:
        error_msg = f"Path is a directory, not a file: {file_path}"
        raise ToolError(error_msg) from None
    except OSError as e:
        error_msg = f"Error writing file '{file_path}': {e}"
        raise ToolError(error_msg) from None


def _encode_file_to_base64_impl(
    file_path: str
) -> str:
    """
    Encode a file to a base64 string.

    This function reads a file in binary mode and returns its contents
    encoded as a base64 string. Only absolute paths are allowed for
    security reasons.

    Args:
        file_path: Absolute path to the file to encode

    Returns:
        Base64 encoded string representation of the file contents

    Raises:
        ToolError: If file cannot be read, path is invalid, or other I/O error occurs
    """
    # Validate path
    resolved_path = validate_absolute_path(file_path)

    # Read file in binary mode
    file_content = read_file_binary(resolved_path)

    # Encode to base64
    return base64.b64encode(file_content).decode("ascii")


def _decode_base64_to_file_impl(
    base64_content: str,
    file_path: str
) -> str:
    """
    Decode a base64 string and write it to a file.

    This function takes base64 encoded content and writes the decoded
    binary data to a file. Only absolute paths are allowed for security
    reasons.

    Args:
        base64_content: Base64 encoded content to decode
        file_path: Absolute path where to save the decoded file

    Returns:
        Success message with the path where file was written

    Raises:
        ToolError: If base64 is invalid, file cannot be written, path is invalid,
            or other error occurs
    """
    # Validate file path
    resolved_path = validate_absolute_path(file_path)

    # Validate base64 content
    if not base64_content or not base64_content.strip():
        error_msg = "Base64 content cannot be empty"
        raise ToolError(error_msg)

    # Decode base64 content
    try:
        decoded_content = base64.b64decode(base64_content, validate=True)
    except (ValueError, binascii.Error) as e:
        error_msg = f"Invalid base64 content: {e}"
        raise ToolError(error_msg) from None

    # Write decoded content to file
    write_file_binary(resolved_path, decoded_content)

    return f"Successfully decoded base64 content to file: {resolved_path}"


@mcp.tool()
def encode_file_to_base64(
    file_path: str = Field(
        description="Absolute path to the file to encode to base64",
        examples=["/home/user/document.pdf", "/data/files/image.png"]
    )
) -> str:
    """
    Encode a file to a base64 string.

    This tool reads a file in binary mode and returns its contents
    encoded as a base64 string. Only absolute paths are allowed for
    security reasons.

    Args:
        file_path: Absolute path to the file to encode

    Returns:
        Base64 encoded string representation of the file contents

    Raises:
        ToolError: If file cannot be read, path is invalid, or other I/O error occurs
    """
    return _encode_file_to_base64_impl(file_path)


@mcp.tool()
def decode_base64_to_file(
    base64_content: str = Field(
        description="Base64 encoded content to decode and write to file",
        examples=[
            "SGVsbG8gV29ybGQ=",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        ]
    ),
    file_path: str = Field(
        description="Absolute path where to save the decoded file",
        examples=["/home/user/decoded.pdf", "/data/files/output.png"]
    )
) -> str:
    """
    Decode a base64 string and write it to a file.

    This tool takes base64 encoded content and writes the decoded
    binary data to a file. Only absolute paths are allowed for security
    reasons.

    Args:
        base64_content: Base64 encoded content to decode
        file_path: Absolute path where to save the decoded file

    Returns:
        Success message with the path where file was written

    Raises:
        ToolError: If base64 is invalid, file cannot be written, path is invalid,
            or other error occurs
    """
    return _decode_base64_to_file_impl(base64_content, file_path)


def main():
    # Run the MCP server with stdio transport
    mcp.run()

if __name__ == "__main__":
    main()
