#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Extract values from JSON
model_name=$(echo "$input" | jq -r '.model.display_name // .model.id')
model_id=$(echo "$input" | jq -r '.model.id')
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
total_output=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
used_percentage=$(echo "$input" | jq -r '.context_window.used_percentage // 0')

# Calculate total tokens used
total_tokens=$((total_input + total_output))

# Format tokens in k format
if [ $total_tokens -ge 1000 ]; then
    total_tokens_formatted="$((total_tokens / 1000))k"
else
    total_tokens_formatted="${total_tokens}"
fi

if [ $context_size -ge 1000 ]; then
    context_size_formatted="$((context_size / 1000))k"
else
    context_size_formatted="${context_size}"
fi

# Round percentage to integer
used_percentage_int=$(printf "%.0f" "$used_percentage")

# Calculate cost based on model pricing
# Prices are per million tokens
case "$model_id" in
    claude-sonnet-4-5-20250929)
        # Claude Sonnet 4.5: $3 per MTok input, $15 per MTok output
        input_cost_per_mtok=3.0
        output_cost_per_mtok=15.0
        ;;
    claude-opus-4-5-20251101)
        # Claude Opus 4.5: $15 per MTok input, $75 per MTok output
        input_cost_per_mtok=15.0
        output_cost_per_mtok=75.0
        ;;
    *)
        # Default to Sonnet 4.5 pricing
        input_cost_per_mtok=3.0
        output_cost_per_mtok=15.0
        ;;
esac

# Calculate cost in dollars
input_cost=$(echo "scale=4; $total_input * $input_cost_per_mtok / 1000000" | bc)
output_cost=$(echo "scale=4; $total_output * $output_cost_per_mtok / 1000000" | bc)
total_cost=$(echo "scale=4; $input_cost + $output_cost" | bc)

# Format cost display
if (( $(echo "$total_cost < 0.01" | bc -l) )); then
    cost_formatted="<\$0.01"
else
    cost_formatted=$(printf "\$%.2f" "$total_cost")
fi

# Create progress bar (20 characters wide)
bar_width=20
filled=$((used_percentage_int * bar_width / 100))
empty=$((bar_width - filled))

# Build progress bar with separate colors for brackets and fill
filled_bar=""
for ((i=0; i<filled; i++)); do filled_bar+="="; done
for ((i=0; i<empty; i++)); do filled_bar+=" "; done

# Get git branch (skip locks)
branch=""
if [ -d "$current_dir/.git" ] || git -C "$current_dir" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$current_dir" --no-optional-locks branch --show-current 2>/dev/null)
fi

# Get directory name
dir_name=$(basename "$current_dir")

# ANSI color codes
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
MAGENTA='\033[35m'
RED='\033[31m'
RESET='\033[0m'
DIM='\033[2m'

# Output status line with colors
# Progress bar with DIM brackets and GREEN fill
if [ -n "$branch" ]; then
    printf "${CYAN}%s${RESET} ${DIM}|${RESET} ${DIM}[${RESET}${GREEN}%s${RESET}${DIM}]${RESET} ${YELLOW}%s%%${RESET} ${DIM}|${RESET} ${MAGENTA}%s${MAGENTA}/${MAGENTA}%s${RESET} ${DIM}|${RESET} ${RED}%s${RESET} ${DIM}|${RESET} ${GREEN}%s${RESET} ${DIM}|${RESET} ${BLUE}%s${RESET}" \
        "$model_name" \
        "$filled_bar" \
        "$used_percentage_int" \
        "$total_tokens_formatted" \
        "$context_size_formatted" \
        "$cost_formatted" \
        "$branch" \
        "$dir_name"
else
    printf "${CYAN}%s${RESET} ${DIM}|${RESET} ${DIM}[${RESET}${GREEN}%s${RESET}${DIM}]${RESET} ${YELLOW}%s%%${RESET} ${DIM}|${RESET} ${BLUE}%s${RESET}/${MAGENTA}%s${RESET} ${DIM}|${RESET} ${RED}%s${RESET} ${DIM}|${RESET} ${CYAN}%s${RESET}" \
        "$model_name" \
        "$filled_bar" \
        "$used_percentage_int" \
        "$total_tokens_formatted" \
        "$context_size_formatted" \
        "$cost_formatted" \
        "$dir_name"
fi
