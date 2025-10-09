# Task — Build a **Python MCP Server** (stdio) for Base64 file conversion — *MVP-first* (2025-10-08)

---

## Clarification & Planning Phase
Before implementation, if any part of this task is **unclear or under-specified**, ask up to **3 concise clarification questions**.
Keep them factual (no speculation) and grouped into one short list.
Once assumptions are clarified or documented, proceed autonomously without further questions
unless something makes execution **impossible**.

Also keep the plan compact (aim to use **≤ 1/3 of the context window**). Defer details to the *Restart Kit* file created below.

---

## SDK Choice
Use **either**:
- **FastMCP** (Python package often named `mcp` or `fastmcp`), **or**
- The **official Python MCP SDK** (`mcp` / `mcp-python`).

**Requirement:** stdio transport. Pick the SDK you implement fastest. Keep parameter descriptions visible in Cline.

---

## Golden Rules (keep it fast & correct)
1. Build a **real MCP server with stdio transport**, not two loose scripts.
2. **Deliver a minimal, running MVP first**, then iterate.
3. **Stick to Python**; do not switch stacks unless explicitly requested.
4. **Write & run tests early**; short feedback loops.
5. **Do not invent APIs**. If something is unknown, stub and add a short TODO in README.
6. Keep stdio clean for MCP JSON-RPC (no noisy prints).

---

## Project Layout (strict)
- `pyproject.toml` (build system + deps)
- `src/mcp_base64/server.py` (stdio runner + tools)
- `tests/test_tools.py` (pytest + pytest-asyncio; binary & text cases)
- `README.md` (install, run via stdio, tools table, usage examples)
- `.github/workflows/ci.yml` (lint + test)
- **`RESTART.md` (Restart Kit — see below)**

---

## **Build Phase Step 0 — Create a State Handoff / Restart Kit (RESTART.md)**
As the **first action in Build**, write a concise `RESTART.md` into the project root so a new chat with an empty context can resume work instantly.

Include these sections (short bullet points, keep file **≤ 250 lines**):
1. **Project Summary** — one paragraph purpose & scope.
2. **Decisions & Assumptions** — list the key choices (SDK, stdio, paths) and any assumptions made.
3. **Commands & How-To-Run** — exact commands for: install, run (stdio), quick JSON-RPC smoke test, run tests.
4. **File Map** — brief tree of important files (server entry, tools, tests, CI).
5. **Dependencies** — runtime & dev deps with minimal versions; any environment variables (no secrets; use placeholders).
6. **Tools API Contract** — names, signatures, param descriptions, error behavior.
7. **Test Plan** — what the tests cover; acceptance criteria.
8. **Open TODOs / Next Steps** — prioritized checklist for the next iteration.
9. **Resume Instructions** — “If you’re resuming from scratch, run these commands in order…”

Then continue with implementation. When posting long content to chat, refer to the file and paste only a short summary.

---

## Tools (exact signatures & behavior)
Implement exactly these two tools with type hints **and parameter descriptions** so Cline shows proper help:
- `encode_file_to_base64(file_path: str) -> str`
- `decode_base64_to_file(base64_content: str, file_path: str) -> str`

**Requirements**
- Use `pathlib.Path` and **absolute paths only** (validate input; reject traversal).
- Read/write **binary** for arbitrary files.
- On errors, use the SDK's idiomatic tool error:
  - FastMCP: raise `ToolError("message")`.
  - Official SDK: return an MCP **error response** with a concise message (custom exception mapped to error is fine).
- **Parameter descriptions** (so Cline shows them):
  - **If using FastMCP**: add `pydantic.Field(description=...)` to each parameter.
  - **If using official SDK**: use whatever the SDK supports (e.g., decorator/schema args or pydantic models) to set each parameter's **description**.
  - Also include short docstrings (NumPy-style) as a fallback.

**Example (FastMCP style)**
```python
from pathlib import Path
from pydantic import Field
from mcp import tool  # or from fastmcp import mcp as tool decorator, depending on your SDK
# If FastMCP specifically: from mcp.server.fastmcp import ToolError

@tool()
async def encode_file_to_base64(
    file_path: str = Field(description="Absolute path to an existing file to encode.")
) -> str:
    """Return base64 of the file's bytes."""
    # implement…
```

**Example (Official mcp-python style, schematic)**
```python
from pydantic import BaseModel, Field
from mcp import tool  # official SDK decorator

class EncodeArgs(BaseModel):
    file_path: str = Field(description="Absolute path to an existing file to encode.")

@tool()  # ensure the SDK exposes EncodeArgs schema so descriptions are visible
async def encode_file_to_base64(args: EncodeArgs) -> str:
    """Return base64 of the file's bytes."""
    # implement…
```

---

## Coding Conventions
- Python >= 3.10, type hints, small pure functions.
- Use `ruff` or `flake8`; concise docstrings.
- No global mutable state.

---

## Speed Heuristics
- Scaffold → compile → **write `RESTART.md`** → implement `encode` → quick test → implement `decode` → extend tests.
- Defer extras (Docker, PyPI) until core tests pass.

---

## README (concise)
Include: install steps, how to run via **stdio**, tools table, minimal JSON-RPC example, short FAQ/TODO. When writing long Markdown, commit it to the repo (the user prefers downloadable files).

---

## CI
- GitHub Actions: set Python 3.11, install deps, run `ruff`/`flake8` and `pytest -q` on push/PR.

---

## Acceptance Tests (must pass locally)
1. **Initialize over stdio** (run from project root with editable path):
   ```bash
   PYTHONPATH=src python -m mcp_base64.server <<'EOF'
   {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
   EOF
   ```
   Expected: a valid MCP `initialize` response.
2. **Round-trip**: encoding a small binary (e.g., 1KB PNG) with `encode_file_to_base64` and decoding with `decode_base64_to_file` reproduces identical bytes (assert in tests).

---

## Concrete Deliverables
1. `pyproject.toml` with deps: `pydantic`, `pytest`, `pytest-asyncio`, `ruff` or `flake8`, and one MCP SDK (**FastMCP or official mcp-python**).
2. `src/mcp_base64/server.py` with:
   - Two tools above
   - stdio runner (SDK-appropriate)
   - Proper error handling per SDK
3. `tests/test_tools.py` covering text & binary files using temp dirs.
4. `README.md` (short, with exact run commands and examples).
5. `.github/workflows/ci.yml` to lint and test.
6. **`RESTART.md`** with the sections listed above.

---

## Run Commands (examples)
- **Local run (stdio)**:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -e .
  PYTHONPATH=src python -m mcp_base64.server
  ```
- **Quick JSON-RPC smoke test**:
  ```bash
  printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n' | PYTHONPATH=src python -m mcp_base64.server
  ```
- **Tests**:
  ```bash
  pytest -q
  ```

---

## Notes
- Keep answers short and code-first. Provide minimal commands to run and test.
- Use the *Clarification & Planning Phase* once at the start; then proceed autonomously.
- Always write long Markdown to files in the repo; keep chat output brief and link to files.
