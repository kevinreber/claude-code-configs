# Claude Code Hooks

Hooks are shell commands that execute in response to Claude Code events.

## Available Hook Types

| Hook | Trigger | Use Case |
|------|---------|----------|
| `PreToolUse` | Before any tool executes | Validation, confirmation prompts |
| `PostToolUse` | After any tool executes | Logging, notifications, auto-formatting |
| `Notification` | When Claude wants your attention | Desktop alerts |
| `Stop` | When Claude finishes a response | Cleanup, summaries |

## Configuration

Hooks are configured in your Claude settings file (`.claude/settings.json` or global settings):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "echo 'About to modify: $TOOL_INPUT'"
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "command": "/path/to/hook-script.sh"
      }
    ]
  }
}
```

## Environment Variables

Hooks receive context through environment variables:

- `$TOOL_NAME` - Name of the tool being used
- `$TOOL_INPUT` - JSON input to the tool
- `$TOOL_OUTPUT` - JSON output (PostToolUse only)
- `$SESSION_ID` - Current session identifier
- `$WORKING_DIR` - Current working directory

## Example Configurations

See the individual files in this directory for ready-to-use hook configurations.

## Tips

1. **Keep hooks fast** - Slow hooks degrade the experience
2. **Handle errors gracefully** - Failing hooks can block operations
3. **Use matchers wisely** - Specific matchers reduce unnecessary executions
4. **Test thoroughly** - Buggy hooks can cause unexpected behavior
