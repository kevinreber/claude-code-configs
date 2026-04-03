# Claude Code Hooks

Hooks are shell commands that execute in response to Claude Code events.

## Available Hook Types

| Hook | Trigger | Use Case |
|------|---------|----------|
| `PreToolUse` | Before any tool executes | Validation, confirmation prompts |
| `PostToolUse` | After any tool executes | Logging, notifications, auto-formatting |
| `Notification` | When Claude wants your attention | Desktop alerts |
| `PermissionRequest` | When Claude needs permission to proceed | Permission alerts, sound notifications |
| `Stop` | When Claude finishes a response | Cleanup, summaries |

## Configuration

Hooks are configured in your Claude settings file (`.claude/settings.json` or global settings):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'About to modify: $TOOL_INPUT'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/hook-script.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Claude finished'"
          }
        ]
      }
    ]
  }
}
```

### Matcher Property

The `matcher` is a case-sensitive string pattern to match tool names:
- Simple strings: `"Edit"`, `"Write"`, `"Bash"`
- Regex patterns: `"Edit|Write"`, `"Notebook.*"`
- Match all: `".*"` or omit the matcher field

**Note:** `Stop` and `Notification` events do not use matchers - omit the field entirely.

### Hook Types

- `type: "command"` - Execute a shell command
- `type: "prompt"` - Send to LLM for evaluation (Stop events only)

## Environment Variables

Hooks receive context through environment variables:

- `$TOOL_NAME` - Name of the tool being used
- `$TOOL_INPUT` - JSON input to the tool
- `$TOOL_OUTPUT` - JSON output (PostToolUse only)
- `$SESSION_ID` - Current session identifier
- `$WORKING_DIR` - Current working directory

## Example Configurations

See the individual files in this directory for ready-to-use hook configurations.

## Platform Notes

The notification hooks in `.claude/settings.json` use `osascript` for macOS desktop notifications. These are **macOS-only**. On other platforms, replace with your preferred notification method:

- **Linux:** `notify-send "Claude Code" "Claude has finished"` (requires `libnotify`)
- **Windows (WSL):** `powershell.exe -Command "New-BurntToastNotification -Text 'Claude Code','Claude has finished'"` (requires BurntToast module)

The `2>/dev/null || true` suffix ensures hooks fail silently on unsupported platforms.

## Tips

1. **Keep hooks fast** - Slow hooks degrade the experience
2. **Handle errors gracefully** - Failing hooks can block operations
3. **Use matchers wisely** - Specific matchers reduce unnecessary executions
4. **Test thoroughly** - Buggy hooks can cause unexpected behavior
