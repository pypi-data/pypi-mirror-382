# Task — Build a **Python MCP Server** (stdio) for Base64 file conversion

---

## Clarification & Planning Phase
Before implementation, if any part of this task is **unclear or under-specified**, ask up to **3 concise clarification questions**.
Keep them factual (no speculation) and grouped into one short list.
Once assumptions are clarified or documented, proceed autonomously without further questions
unless something makes execution **impossible**.

Keep the plan compact (aim to use **≤ 1/3 of the context window**). Defer lower‑level details to the *Restart Kit* and code comments.

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
- `artifacts/` (captured logs from lint/unit/integration runs; see Verification below)

---

## **Build Phase Step 0 — Create a State Handoff / Restart Kit (RESTART.md)**
As the **first action in Build**, write a concise `RESTART.md` into the project root so a new chat with an empty context can resume work instantly.

Include (≤ 250 lines, bullet points okay):
1. **Project Summary** — purpose & scope.
2. **Decisions & Assumptions** — SDK, stdio, paths.
3. **Commands & How-To-Run** — install, run (stdio), JSON-RPC smoke test, run tests.
4. **File Map** — server entry, tools, tests, CI.
5. **Dependencies** — runtime/dev deps; env vars (no secrets).
6. **Tools API Contract** — names, signatures, param descriptions, error behavior.
7. **Test Plan** — unit + integration; acceptance criteria.
8. **Open TODOs / Next Steps** — prioritized.
9. **Resume Instructions** — “If resuming from scratch, run these in order: …”

---

## Tools (exact signatures & behavior)
Implement exactly two tools with type hints **and parameter descriptions** so Cline shows proper help:
- `encode_file_to_base64(file_path: str) -> str`
- `decode_base64_to_file(base64_content: str) -> str`

**Requirements**
- Use `pathlib.Path` and **absolute paths only** (validate input; reject traversal).
- Read/write **binary** for arbitrary files.
- On errors, use the SDK's idiomatic tool error:
  - FastMCP: raise `ToolError("message")`.
  - Official SDK: return an MCP **error response** with a concise message (custom exception mapped to error is fine).
- **Parameter descriptions** (so Cline shows them):
  - **FastMCP**: `pydantic.Field(description=...)` per parameter.
  - **Official SDK**: use schema/decorator or Pydantic models to attach `description`.
  - Include concise docstrings (NumPy-style) as a fallback.

**Example (schema hint only)**
```python
from pydantic import Field

@mcp.tool()
async def encode_file_to_base64(
    file_path: str = Field(description="Absolute path to an existing file to encode.")
) -> str:
    ...
```

---

## Coding Conventions
- Python >= 3.10, type hints, small pure functions.
- Use `ruff` or `flake8`; concise docstrings.
- No global mutable state.

---

## **Verification — Must EXECUTE, CAPTURE, PARSE, and FIX**
You **must run** the following locally (inside the task environment), **capture stdout+stderr**, **parse** for problems, and **fix** until clean. Save raw logs under `artifacts/` and include a short summary table in chat.

### Commands to run
1. **Lint**: `ruff check .` (or `flake8 .`)
2. **Unit tests**: `pytest -q`
3. **Integration test** (stdio JSON-RPC):
   - Launch the server (subprocess) and send JSON-RPC messages:
     - `initialize`
     - call `encode_file_to_base64` on a sample binary (1–2 KB)
     - call `decode_base64_to_file` to restore to a temp path
     - assert byte‑for‑byte equality
   - Verify that **parameter descriptions** are present in the tool schema (SDK-appropriate).
   - Tear down the process cleanly.

### Capture & parse
- Save full outputs to:
  - `artifacts/lint.log`
  - `artifacts/unit-test.log`
  - `artifacts/integration-test.log`
- Parse outputs and **treat as failure** if any of these appear (case-insensitive):
  - `error`, `failed`, `traceback`, `exception`, or any **non-zero exit code**
  - For lint: any diagnostics **other than 0 issues** (or non-zero exit code)
  - For pytest: any tests not **passed** (xfail/skip allowed if intentional and documented in `RESTART.md`)

### Report in chat (concise)
- Provide a **3-row table** with: *command*, *exit code*, *summary* (e.g., “10 passed in 0.42s”).
- If failures/warnings occurred, list **what you changed** and **re-run** until green.

You **may not** declare “Task Completed” until all three commands are green and logs are present under `artifacts/`.

---

## Speed Heuristics
- Scaffold → compile → **write `RESTART.md`** → implement `encode` → quick unit test → implement `decode` → unit tests → integration test → lint → iterate fixes.
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
2. **Round‑trip**: encoding a small binary with `encode_file_to_base64` and decoding with `decode_base64_to_file` reproduces identical bytes (assert in tests).

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
7. **`artifacts/`** with `lint.log`, `unit-test.log`, `integration-test.log` from the **final green run**.

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
