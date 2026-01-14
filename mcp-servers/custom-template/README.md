# Custom MCP Server Template

A starting point for creating your own MCP server to extend Claude's capabilities.

## Quick Start

1. Copy this directory to your desired location
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the server:
   ```bash
   npm start
   ```

## Adding to Claude Code

Add to your Claude settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "custom": {
      "command": "node",
      "args": ["/path/to/custom-template/server.js"]
    }
  }
}
```

## Adding New Tools

1. Add the tool definition in `ListToolsRequestSchema` handler
2. Add the tool implementation in `CallToolRequestSchema` handler

### Tool Definition Structure

```javascript
{
  name: 'tool_name',
  description: 'What the tool does',
  inputSchema: {
    type: 'object',
    properties: {
      param1: {
        type: 'string',
        description: 'Parameter description',
      },
    },
    required: ['param1'],
  },
}
```

### Tool Implementation

```javascript
case 'tool_name': {
  const { param1 } = args;
  // Your logic here
  return {
    content: [{ type: 'text', text: 'Result' }],
  };
}
```

## Best Practices

1. **Validate inputs** - Check all required parameters
2. **Handle errors gracefully** - Return `isError: true` for failures
3. **Keep tools focused** - Each tool should do one thing well
4. **Document clearly** - Descriptions help Claude use tools correctly
5. **Log for debugging** - Use `console.error` (not `console.log`)

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP SDK on GitHub](https://github.com/modelcontextprotocol/sdk)
- [Example Servers](https://github.com/modelcontextprotocol/servers)
