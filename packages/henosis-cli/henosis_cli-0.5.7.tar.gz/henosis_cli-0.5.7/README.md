# Henosis CLI

the BEST terminal agent designed for uncompromising performance

Henosis CLI is a streamlined, professional terminal client for the Henosis multi-provider streaming chat backend. It supports OpenAI, Gemini, Anthropic, xAI (Grok), DeepSeek, and Moonshot Kimi via the Henosis server, and includes optional client-executed file/shell tools with approvals and sandboxing.

Key features
- Interactive chat over SSE with usage/cost summaries
- Model picker and per-turn controls (tools on/off, control level, reasoning effort)
- Client approvals at Level 2 for write/exec operations (approve once/session/always)
- Agent scope (safe host directory) when enabling tools in host mode
- Optional web search controls for OpenAI models (domain allow-list, include sources, location hints)
- Saves conversations to server threads and commits usage for billing where enabled

Install
- pip: pip install henosis-cli
- pipx (recommended): pipx install henosis-cli

Quick start
- Run the CLI: henosis-cli
- Default server: https://henosis.us/api_v2 (override with HENOSIS_SERVER or --server)
- Dev server: henosis-cli --dev (uses HENOSIS_DEV_SERVER or http://127.0.0.1:8000)
- Authenticate when prompted. Use /model to pick a model and /tools on to enable tools.

Common commands
- /menu or /settings: Open settings menu
- /model: Select a model (gpt-5, gemini-2.5-pro, grok-4-fast-reasoning, deepseek-chat, etc.)
- /tools on|off|default: Toggle per-request tool availability
- /fs workspace|host|default: Set filesystem scope (workspace = sandbox; host = Agent scope)
- /hostbase <abs path>: Set Agent scope root directory when fs=host
- /level 1|2|3: Control level (1 read-only; 2 write/exec with approval; 3 no approvals)
- /map on|off: Inject CODEBASE_MAP.md into your first message
- /websearch on|off|domains|sources|location: Configure OpenAI web search options
- /title <name>: Name the current chat thread
- /clear: Reset chat history
- /login, /logout, /whoami: Auth helpers

Configuration
- Server base URL
  - Env: HENOSIS_SERVER (default https://henosis.us/api_v2)
  - Flag: --server https://your-server
  - Dev shortcut: --dev (env HENOSIS_DEV_SERVER or http://127.0.0.1:8000)
- Optional Agent Mode (developer WebSocket bridge): --agent-mode

Local tools and sandboxing (optional)
- The CLI can execute a safe subset of tools locally when the server requests client-side execution.
- Tools include read_file, write_file, append_file, list_dir, apply_patch, run_command.
- At Level 2, destructive tools and command executions prompt for approval (once/session/always).
- Workspace root: by default, the workspace scope is the current working directory at the moment you launch the CLI. No dedicated per-terminal sandbox is created unless you override it.
- Override root: set --workspace-dir /path/to/root (or HENOSIS_WORKSPACE_DIR) to operate in a different directory for the session.
- Host scope can be constrained to an Agent scope directory (set via /hostbase) when fs=host.

Notes
- Requires Python 3.9+
- The CLI ships with rich and prompt_toolkit for a nicer UI by default.
- The reusable local tools library is available as a module (henosis_cli_tools).

Support
- Email: henosis@henosis.us

Build and publish (maintainers)
- Bump version in pyproject.toml
- Build: python -m pip install build twine && python -m build
- Upload to PyPI: python -m twine upload dist/*
- Or to TestPyPI: python -m twine upload --repository testpypi dist/*
