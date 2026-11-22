#!/usr/bin/env bash
set -euo pipefail

target=${1:-all}
missing=0

if [[ "$target" != "graphviz" && "$target" != "mermaid" && "$target" != "all" ]]; then
  echo "Usage: check-tools.sh [graphviz|mermaid|all]" >&2
  exit 2
fi

if [[ "$target" == "graphviz" || "$target" == "all" ]]; then
  if command -v dot >/dev/null 2>&1; then
    printf 'Graphviz: %s\n' "$(command -v dot)"
  else
    echo "Graphviz is not installed. Review and install it with an approved package manager." >&2
    missing=1
  fi
fi

if [[ "$target" == "mermaid" || "$target" == "all" ]]; then
  if command -v mmdc >/dev/null 2>&1; then
    printf 'Mermaid CLI: %s\n' "$(command -v mmdc)"
  else
    echo "Mermaid CLI is not installed. Review and install it from an approved registry." >&2
    missing=1
  fi
fi

[[ "$missing" -eq 0 ]] || exit 1
echo "Requested diagram renderer is available."
