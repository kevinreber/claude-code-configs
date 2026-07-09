#!/bin/bash
# After `git push`, check if the current branch is behind origin's default branch.
# Pure informational — never blocks.

COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)

# Only act on git push commands
[[ "$COMMAND" != *"git push"* ]] && exit 0

# Bail if not in a git repo
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# Resolve default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$DEFAULT_BRANCH" ]; then
  if git show-ref --verify --quiet refs/remotes/origin/main; then
    DEFAULT_BRANCH="main"
  elif git show-ref --verify --quiet refs/remotes/origin/master; then
    DEFAULT_BRANCH="master"
  else
    exit 0
  fi
fi

CURRENT_BRANCH=$(git branch --show-current)
[ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ] && exit 0

git fetch origin "$DEFAULT_BRANCH" --quiet 2>/dev/null

BEHIND_COUNT=$(git rev-list --count "HEAD..origin/$DEFAULT_BRANCH" 2>/dev/null || echo "0")

if [ "$BEHIND_COUNT" -gt 0 ]; then
  echo ""
  echo "⚠️  $CURRENT_BRANCH is $BEHIND_COUNT commit(s) behind origin/$DEFAULT_BRANCH"
  echo "   Sync:  git fetch origin $DEFAULT_BRANCH && git merge origin/$DEFAULT_BRANCH"
fi

exit 0
