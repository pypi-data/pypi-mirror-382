- use uv to manage dependency
- run command with uv like `uv run ...`
- i've set up the pypi token with bash variable "PYPI_TOKEN", source ~/.bashrc or ~/.zshrc first
- implement base on `https://github.com/modelcontextprotocol/python-sdk`

## Testing Local MCP Server

### Start MCP Inspector Web UI
```bash
npx @modelcontextprotocol/inspector
```

This will:
- Start Inspector at `http://localhost:6274`
- Provide authentication token in URL
- Open browser automatically

### Configure Server Connection in Inspector
- **Transport Type**: STDIO
- **Command**: `uv`
- **Arguments**: `["run", "python", "-m", "codex_as_mcp"]`
- **Working Directory**: `/Users/kky/Projects/codex-as-mcp`

If you see quick request timeouts, increase Inspector timeouts or use `test.sh` which exports:
- `MCP_SERVER_REQUEST_TIMEOUT=300000`
- `MCP_REQUEST_TIMEOUT_RESET_ON_PROGRESS=true`
- `MCP_REQUEST_MAX_TOTAL_TIMEOUT=28800000`

### Available Tools to Test
- **`spawn_agent`**: Run Codex agent inside a directory and return its stdout

Inputs:
- `prompt` (string): Everything the agent should know/do.
- `work_directory` (string): Absolute path where the agent works.

Behavior:
- Executes: `codex e --cd <work_directory> --skip-git-repo-check --full-auto --search "<prompt>"`
- Wraps the prompt in quotes; escapes inner quotes.
- Sends periodic progress heartbeats so Inspector won’t time out.

### Server Modes
- Single mode: always writable (Codex edits files in `work_directory`).
  Use with care and run inside the intended project folder.

## Note
- You are using zsh terminal
