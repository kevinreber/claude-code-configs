#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: render.sh <source-file> [png|svg] [--open] [--scale N]" >&2
}

[[ $# -ge 1 ]] || { usage; exit 2; }
source_file=$1
shift
format=png
open_output=false
scale=2

if [[ $# -gt 0 && ( "$1" == "png" || "$1" == "svg" ) ]]; then
  format=$1
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --open) open_output=true; shift ;;
    --scale)
      [[ $# -ge 2 ]] || { echo "Error: --scale requires a value." >&2; exit 2; }
      scale=$2
      shift 2
      ;;
    *) echo "Error: unknown argument '$1'." >&2; usage; exit 2 ;;
  esac
done

[[ -f "$source_file" ]] || { echo "Error: source file not found: $source_file" >&2; exit 1; }
[[ "$scale" =~ ^[1-9][0-9]*$ ]] || { echo "Error: --scale must be a positive integer." >&2; exit 2; }

extension=${source_file##*.}
output_file=${source_file%.*}.${format}

case "$extension" in
  dot)
    command -v dot >/dev/null 2>&1 || { echo "Error: Graphviz is not installed." >&2; exit 1; }
    if [[ "$format" == "png" ]]; then
      dot -Tpng -Gdpi="$((scale * 96))" -o "$output_file" "$source_file"
    else
      dot -Tsvg -o "$output_file" "$source_file"
    fi
    ;;
  mmd)
    command -v mmdc >/dev/null 2>&1 || { echo "Error: Mermaid CLI is not installed." >&2; exit 1; }
    if [[ "$format" == "png" ]]; then
      mmdc -i "$source_file" -o "$output_file" -b white -s "$scale"
    else
      mmdc -i "$source_file" -o "$output_file" -b white
    fi
    ;;
  *) echo "Error: use a .dot or .mmd source file." >&2; exit 1 ;;
esac

echo "Rendered: $output_file"
if "$open_output"; then
  if command -v open >/dev/null 2>&1; then
    open "$output_file"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$output_file"
  else
    echo "View: $output_file"
  fi
fi
