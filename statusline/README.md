# Custom Statusline Configuration

This directory contains a custom statusline configuration for Claude Code that displays enhanced session information.

## Files

- `statusline-command.sh` - Bash script that generates the custom statusline
- `settings.json` - Claude Code settings file with statusline configuration

## Features

The custom statusline displays:
- **Model name** - Current Claude model being used
- **Progress bar** - Visual representation of context window usage
- **Context usage percentage** - Percentage of context window used
- **Token counts** - Total tokens used vs. context window size (formatted in k)
- **Cost tracking** - Estimated cost based on model pricing
- **Git branch** - Current git branch (if in a git repository)
- **Directory name** - Current working directory name

### Color Scheme
- Cyan: Model name
- Green: Progress bar fill and git branch
- Yellow: Usage percentage
- Magenta: Token counts
- Red: Cost
- Blue: Directory name
- Dim: Separators and brackets

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
