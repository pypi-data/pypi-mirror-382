# Task — Build a **Python MCP Server** (stdio) for Base64 file conversion

---

## Clarification & Planning Phase
Before implementation, if any part of this task is **unclear or under-specified**, ask up to **3 concise clarification questions** in one short list.
Once assumptions are clarified or documented, proceed autonomously without further questions unless something makes execution **impossible**.
Keep the plan compact (use **≤ 1/3 context window**). Defer lower‑level details to `RESTART.md` and code comments.

---

## Environment & Command Rules (important — IntelliJ/Cline uses a fresh shell per command)
- **Do NOT rely on `source .venv/bin/activate`**; activation won’t persist to the next command.
- Always run tools via one of these **stateless-safe** patterns:
  - **Explicit venv path:** `./.venv/bin/python -m pip …`, `./.venv/bin/python -m pytest -q`, `./.venv/bin/ruff check .`
  - **or** prefix PATH per command: `PATH=".venv/bin:$PATH" python -m pytest -q`
  - **or** assume system python but **always** use module form: `python -m pip …`, `python -m pytest -q`
- **Do NOT recreate or re‑activate** the venv unless explicitly instructed.
- **Do NOT run any Node/NPX commands to generate pipeline files** (e.g., `npx mcp-actions`). If CI is needed, **write the YAML directly**.

---

## SDK Choice
Use **either**:
- **FastMCP** (Python), **or**
- The **official Python MCP SDK** (`mcp` / `mcp-python`).

**Requirement:** stdio transport. Keep parameter descriptions visible in Cline.

---

## Golden Rules (keep it fast & correct)
1. Build a **real MCP server with stdio transport**, not two loose scripts.
2. **Deliver a minimal, running MVP first**, then iterate.
3. **Stick to Python**; do not switch stacks unless explicitly requested.
4. **Write & run tests early**; short feedback loops.
5. **Do not invent APIs**. If unknown, stub and add a short TODO in README.
6. Keep stdio clean for MCP JSON-RPC (no noisy prints).

---

## Project Layout (strict)
- `pyproject.toml` (build system + deps)
- `src/mcp_base64/server.py` (stdio runner + tools)
- `tests/test_tools.py` (pytest + pytest-asyncio; binary & text cases)
- `README.md` (install, run via stdio, tools table, usage examples)
- `.github/workflows/ci.yml` (lint + test, written directly — no generators)
- **`RESTART.md` (Restart Kit — see below)**
- `artifacts/` (captured logs from lint/unit/integration runs; see Verification)

---

## **Build Phase Step 0 — Create `RESTART.md` (State Handoff / Restart Kit)**
Short bullet points, ≤ 250 lines:
- Summary, decisions/assumptions (SDK, stdio, paths)
- Commands: install, run (stdio), JSON‑RPC smoke test, tests
- File map; dependencies; env vars (no secrets)
- Tools API contract (names, signatures, param descriptions, errors)
- Test plan (unit + integration); acceptance criteria
- TODOs/next steps; resume instructions

---

## Tools (exact signatures & behavior)
- `encode_file_to_base64(file_path: str) -> str`
- `decode_base64_to_file(base64_content: str) -> str`
Requirements:
- Use `pathlib.Path`; **absolute paths only** (validate; reject traversal)
- Binary I/O; concise errors (FastMCP: `ToolError(…)`; official SDK: proper MCP error)
- Parameter **descriptions** visible to Cline (Pydantic Field or SDK schema); brief docstrings

---

## Coding Conventions
- Python ≥ 3.10; type hints; small pure functions
- `ruff` (preferred) or `flake8`; concise docstrings
- No global mutable state

---

## **Verification — EXECUTE, CAPTURE, PARSE, FIX**
You **must run**, **capture stdout+stderr**, **parse** for problems, and **fix** until clean. Save raw logs under `artifacts/` and post a short summary table.

If a test requires a file and none exists, automatically generate a small sample file (1–2 KB).
Do not fail the test for missing inputs; creating them is part of the task.

### Commands to run
1. **Lint:** `./.venv/bin/ruff check .` (or `PATH=".venv/bin:$PATH" ruff check .`)
2. **Unit tests:** `./.venv/bin/python -m pytest -q`
3. **Integration test (stdio JSON‑RPC):**
   - Launch the server (subprocess) and send messages:
     - `initialize`
     - call `encode_file_to_base64` on a **sample binary file**
       - If no suitable file exists, **create one automatically** (e.g., write random bytes or use a tiny PNG)
     - call `decode_base64_to_file` to restore to a temp path
       - assert byte-for-byte equality
       - Verify parameter descriptions are present in the tool schema.
       - Tear down cleanly.

### Capture & parse
- Save outputs to:
  - `artifacts/lint.log`
  - `artifacts/unit-test.log`
  - `artifacts/integration-test.log`
- Treat as failure if (case‑insensitive): `error`, `failed`, `traceback`, `exception`, or non‑zero exit
- Lint must report **0 issues** (or auto‑fixed); tests must pass (xfail/skip ok if documented in `RESTART.md`)

### Report in chat (concise)
- 3‑row table: *command*, *exit code*, *summary* (e.g., “10 passed in 0.42s”)
- If failures/warnings occurred, list changes and **re‑run** until green
- Do **not** declare “Task Completed” until all three commands are green and logs exist

---

## README (concise)
Explain install, stdio run, tools, minimal JSON‑RPC example, short FAQ/TODO. Write long Markdown to files; keep chat brief.

---

## CI
Write `.github/workflows/ci.yml` directly (no generators). Use Python 3.11, install deps, run `ruff` and `pytest -q`.

---

## Acceptance Tests (must pass locally)
1) `initialize` over stdio returns valid MCP response.  
2) Encode→decode round‑trip reproduces identical bytes.

---

## Run Commands (examples)
```bash
# no activation reliance; explicit venv paths
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e . ruff pytest pytest-asyncio

# run
PYTHONPATH=src ./.venv/bin/python -m mcp_base64.server

# quick smoke
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n' | PYTHONPATH=src ./.venv/bin/python -m mcp_base64.server

# tests
./.venv/bin/python -m pytest -q
```

---

## Notes
- One clarification round at start; then proceed autonomously.
- Prefer files over chat for long content. Keep logs under `artifacts/`.
- No `npx`/generators; write CI YAML directly.
