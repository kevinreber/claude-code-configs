# MCP Server Configurations

Model Context Protocol (MCP) server configurations for extending Claude Code capabilities.

## What is MCP?

MCP (Model Context Protocol) allows Claude to interact with external tools and services through a standardized protocol. MCP servers provide:

- Additional tools Claude can use
- Access to external data sources
- Integration with services (databases, APIs, etc.)

## Configuration

MCP servers are configured in Claude Code settings:

**Global settings** (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

**Project settings** (`.claude/settings.json`):
```json
{
  "mcpServers": {
    "project-db": {
      "command": "node",
      "args": ["./mcp-servers/database-server.js"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

## Available Configurations

| Server | Purpose | Setup Complexity |
|--------|---------|------------------|
| `filesystem` | Extended file operations | Easy |
| `github` | GitHub integration | Easy |
| `postgres` | PostgreSQL database access | Medium |
| `sqlite` | SQLite database access | Easy |
| `fetch` | HTTP requests | Easy |
| `memory` | Knowledge graph storage | Easy |
| `puppeteer` | Web automation | Medium |

## Usage

1. Copy the desired configuration from this directory
2. Add it to your Claude settings
3. Restart Claude Code to load the server
4. The server's tools will be available in your session

## Security Notes

- MCP servers run with your user permissions
- Be careful with servers that access sensitive data
- Review server code before using third-party servers
- Use environment variables for secrets (not hardcoded)

## Creating Custom Servers

See `custom-template/` for a starting point for creating your own MCP servers.

## Troubleshooting

**Server not loading:**
- Check the command path is correct
- Verify dependencies are installed
- Check Claude Code logs for errors

**Tools not appearing:**
- Restart Claude Code after configuration changes
- Verify JSON syntax in settings file
- Check server process is running
