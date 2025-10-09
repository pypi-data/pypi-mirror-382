# Magentic MCP Server

# Faster Delivery. Smarter Observability. Built-In with AI.

### Agent configuration

You need to generate an access token from https://flowlens.magentic.ai

```json
"flowlens-mcp": {
    "command": "pipx",
    "args": [
        "run",
        "--spec",
        "magentic-mcp-server==0.1.17",
        "flowlens-server",
        "your-token"
    ],
    "type": "stdio"
}
```

# Claude Code

```bash
claude mcp add flowlens-mcp --transport stdio -- pipx run --spec "magentic-mcp-server==0.1.17" flowlens-server your-token
```