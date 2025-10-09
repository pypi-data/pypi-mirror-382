# Tests to run manually

## Encode/decode text

Prompt:

```
Use the MCP server 'mcp-base64' to encode the file
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/test.txt`
as base64 to file:
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/test.txt.b64`.

Write the resulting intermediate file!

Then use the same MCP server to decode the file:
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/test.txt.b64`
from base64 to file
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/test.txt.b64.txt`
```

Verify results:

- View the [created txt](/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/test.txt.b64.txt).
- Text-compare the files [expected](/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.b64)
  and [actual](/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.b64.txt.b64).

## Encode/decode GIF

Prompt:

```
Use the MCP server 'mcp-base64' to encode the file
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.gif`
as base64 to file:
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.gif.b64`.

Write the resulting intermediate file!

Then use the same MCP server to decode the file:
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.gif.b64`
from base64 to file
`/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.gif.b64.gif`
```

Verify results:

- View the [created gif](/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.gif.b64.gif).
- Text-compare the files [expected](/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.b64)
  and [actual](/mnt/data/development/PRIVATE/github/mcp-base64/doc/test-files/40px-Testing.b64.gif.b64).