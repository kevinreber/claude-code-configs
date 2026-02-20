# Custom Statusline Configuration

This directory contains a custom statusline configuration for Claude Code that displays enhanced session information.

## Files

- `statusline-command.sh` - Bash script that generates the custom statusline
- `settings.json` - Claude Code settings file with statusline configuration

## Preview

In a git repo with uncommitted changes:
```
👤 kreber[a1b2c3d4] | 🤖 Claude Sonnet 4.6 | 📊 [====                ] 21% | 42k/200k | 🪙 $0.13 | 🌿 main | ✏️  +12 -3 | 📁 my-project
```

In a git repo with no uncommitted changes:
```
👤 kreber[a1b2c3d4] | 🤖 Claude Sonnet 4.6 | 📊 [========            ] 43% | 86k/200k | 🪙 $0.31 | 🌿 feat/new-feature | 📁 my-project
```

Outside a git repo:
```
👤 kreber | 🤖 Claude Sonnet 4.6 | 📊 [==                  ] 9% | 18k/200k | 🪙 $0.05 | 📁 some-dir
```

## Features

The custom statusline displays:
- 👤 **Account name** - Your logged-in account (auto-detected, leftmost position)
- 🤖 **Model name** - Current Claude model being used
- 📊 **Progress bar** - Visual representation of context window usage
- **Context usage percentage** - Percentage of context window used
- **Token counts** - Total tokens used vs. context window size (formatted in k)
- 🪙 **Cost tracking** - Estimated cost based on model pricing
- 🌿 **Git branch** - Current git branch (if in a git repository)
- ✏️  **Git diff stat** - Lines added/removed in working tree vs HEAD (only shown when there are changes)
- 📁 **Directory name** - Current working directory name
- **Session name** - Session name if renamed, otherwise truncated session ID

### Color Scheme
- Magenta: Account name and token counts
- Cyan: Model name
- Green: Progress bar fill and git branch, lines added
- Yellow: Usage percentage and session name
- Red: Cost, lines removed
- Blue: Directory name
- Dim: Separators, brackets, and session brackets

## Installation

1. Copy `statusline-command.sh` to your `~/.claude/` directory:
   ```bash
   cp statusline-command.sh ~/.claude/
   chmod +x ~/.claude/statusline-command.sh
   ```

2. Update your Claude Code settings (or merge with existing `~/.claude/settings.json`):
   ```bash
   cp settings.json ~/.claude/settings.json
   ```

   Or manually add to your settings:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "/Users/YOUR_USERNAME/.claude/statusline-command.sh"
     }
   }
   ```

3. The account name is automatically detected from your Claude login (`~/.claude.json`).

   If auto-detection doesn't work, you can set it manually:

   **Option A**: Set an environment variable in your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export CLAUDE_ACCOUNT="your-username"
   ```

   **Option B**: Create an account file:
   ```bash
   echo "your-username" > ~/.claude/account
   ```

## Requirements

- `jq` - JSON processor for parsing input
- `bc` - Calculator for cost calculations
- `git` - For git branch display

Install requirements on macOS:
```bash
brew install jq bc
```

## Pricing

The script includes pricing for:
- **Claude Sonnet 4.5**: $3 per MTok input, $15 per MTok output
- **Claude Opus 4.5**: $15 per MTok input, $75 per MTok output

Update the pricing in `statusline-command.sh` if model prices change.

## Customization

You can customize:
- Colors (ANSI color codes in lines 86-93)
- Progress bar width (line 67)
- Token formatting threshold (line 19)
- Cost display format (lines 60-64)

## Additional Resources

For more statusline styling examples and inspiration:
- [ccstatusline](https://github.com/sirmalloc/ccstatusline) - Collection of Claude Code statusline examples with various styling approaches
