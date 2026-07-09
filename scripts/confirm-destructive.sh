#!/bin/bash
# Block destructive bash commands before execution.
# Exits non-zero to make Claude pause for user confirmation.

DESTRUCTIVE_PATTERNS=(
  'rm -rf +/( |$)'
  'rm -rf +~( |$)'
  'rm -rf +\*( |$)'
  'rm -rf +\$[A-Z_]+( |$)'
  'git push.*--force'
  'git push.*(^| )-f( |$)'
  'git reset --hard'
  'git clean -fd'
  'git branch -D'
  '\bdrop +table\b'
  '\bdrop +database\b'
  '\btruncate +table\b'
  '\bdelete +from\b.*\bwhere\b'
  'kubectl delete (namespace|pv|pvc)'
  'docker system prune'
  'docker volume prune'
  ':\(\)\{ *:\|:& *\};:'
  'mkfs\.'
  'dd if=.*of=/dev/'
)

COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

for pattern in "${DESTRUCTIVE_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -iqE "$pattern"; then
    echo "⛔  Destructive command intercepted by ~/.claude/scripts/confirm-destructive.sh"
    echo ""
    echo "    Command : $COMMAND"
    echo "    Matched : $pattern"
    echo ""
    echo "Review carefully before allowing. If this is intentional, approve in the prompt."
    exit 1
  fi
done

exit 0
