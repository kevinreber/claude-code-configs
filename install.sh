#!/bin/bash

# Claude Code Configurations Installer
# Installs configurations to ~/.claude/

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"

# Print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show usage
usage() {
    cat << EOF
Claude Code Configurations Installer

Usage: ./install.sh [OPTIONS]

Options:
    --all           Install all configurations
    --commands      Install slash commands
    --skills        Install skills
    --hooks         Install hooks (copies examples)
    --guardrails    Install guardrails
    --templates     Install CLAUDE.md templates
    --mcp           Install MCP server configurations
    --symlink       Use symlinks instead of copying (for development)
    --dry-run       Show what would be installed without installing
    --uninstall     Remove installed configurations
    -h, --help      Show this help message

Examples:
    ./install.sh --all              # Install everything
    ./install.sh --commands --skills # Install commands and skills
    ./install.sh --symlink --all    # Symlink all configs (for development)
EOF
    exit 0
}

# Create directory if it doesn't exist
ensure_dir() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
        print_info "Created directory: $1"
    fi
}

# Copy or symlink files
install_files() {
    local src="$1"
    local dest="$2"
    local use_symlink="$3"
    local dry_run="$4"

    if [[ ! -d "$src" ]]; then
        print_warning "Source directory not found: $src"
        return
    fi

    ensure_dir "$dest"

    for file in "$src"/*; do
        if [[ -f "$file" ]]; then
            local filename=$(basename "$file")
            local dest_file="$dest/$filename"

            if [[ "$dry_run" == "true" ]]; then
                if [[ "$use_symlink" == "true" ]]; then
                    echo "Would symlink: $file -> $dest_file"
                else
                    echo "Would copy: $file -> $dest_file"
                fi
            else
                if [[ "$use_symlink" == "true" ]]; then
                    ln -sf "$file" "$dest_file"
                    print_info "Symlinked: $filename"
                else
                    cp "$file" "$dest_file"
                    print_info "Copied: $filename"
                fi
            fi
        elif [[ -d "$file" ]]; then
            local dirname=$(basename "$file")
            install_files "$file" "$dest/$dirname" "$use_symlink" "$dry_run"
        fi
    done
}

# Install commands
install_commands() {
    print_info "Installing slash commands..."
    install_files "$SCRIPT_DIR/commands" "$CLAUDE_DIR/commands" "$USE_SYMLINK" "$DRY_RUN"
    print_success "Slash commands installed"
}

# Install skills
install_skills() {
    print_info "Installing skills..."
    install_files "$SCRIPT_DIR/skills" "$CLAUDE_DIR/skills" "$USE_SYMLINK" "$DRY_RUN"
    print_success "Skills installed"
}

# Install hooks
install_hooks() {
    print_info "Installing hooks..."
    ensure_dir "$CLAUDE_DIR/hooks"
    install_files "$SCRIPT_DIR/hooks" "$CLAUDE_DIR/hooks" "$USE_SYMLINK" "$DRY_RUN"
    print_warning "Hooks are examples only. You'll need to configure them in your settings."
    print_success "Hook examples installed"
}

# Install guardrails
install_guardrails() {
    print_info "Installing guardrails..."
    install_files "$SCRIPT_DIR/guardrails" "$CLAUDE_DIR/guardrails" "$USE_SYMLINK" "$DRY_RUN"
    print_info "Append guardrails to your CLAUDE.md: cat ~/.claude/guardrails/no-secrets.md >> CLAUDE.md"
    print_success "Guardrails installed"
}

# Install templates
install_templates() {
    print_info "Installing CLAUDE.md templates..."
    install_files "$SCRIPT_DIR/templates" "$CLAUDE_DIR/templates" "$USE_SYMLINK" "$DRY_RUN"
    print_info "Copy a template to your project: cp ~/.claude/templates/typescript-node/CLAUDE.md ./CLAUDE.md"
    print_success "Templates installed"
}

# Install MCP configurations
install_mcp() {
    print_info "Installing MCP server configurations..."
    install_files "$SCRIPT_DIR/mcp-servers" "$CLAUDE_DIR/mcp-servers" "$USE_SYMLINK" "$DRY_RUN"
    print_warning "MCP configs need to be added to your Claude settings manually."
    print_success "MCP configurations installed"
}

# Uninstall
uninstall() {
    print_warning "This will remove Claude configurations from $CLAUDE_DIR"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local dirs=("commands" "skills" "hooks" "guardrails" "templates" "mcp-servers")
        for dir in "${dirs[@]}"; do
            if [[ -d "$CLAUDE_DIR/$dir" ]]; then
                rm -rf "$CLAUDE_DIR/$dir"
                print_info "Removed: $CLAUDE_DIR/$dir"
            fi
        done
        print_success "Configurations uninstalled"
    else
        print_info "Uninstall cancelled"
    fi
}

# Parse arguments
USE_SYMLINK="false"
DRY_RUN="false"
INSTALL_ALL="false"
INSTALL_COMMANDS="false"
INSTALL_SKILLS="false"
INSTALL_HOOKS="false"
INSTALL_GUARDRAILS="false"
INSTALL_TEMPLATES="false"
INSTALL_MCP="false"
DO_UNINSTALL="false"

if [[ $# -eq 0 ]]; then
    usage
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            INSTALL_ALL="true"
            shift
            ;;
        --commands)
            INSTALL_COMMANDS="true"
            shift
            ;;
        --skills)
            INSTALL_SKILLS="true"
            shift
            ;;
        --hooks)
            INSTALL_HOOKS="true"
            shift
            ;;
        --guardrails)
            INSTALL_GUARDRAILS="true"
            shift
            ;;
        --templates)
            INSTALL_TEMPLATES="true"
            shift
            ;;
        --mcp)
            INSTALL_MCP="true"
            shift
            ;;
        --symlink)
            USE_SYMLINK="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --uninstall)
            DO_UNINSTALL="true"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Execute
if [[ "$DO_UNINSTALL" == "true" ]]; then
    uninstall
    exit 0
fi

if [[ "$DRY_RUN" == "true" ]]; then
    print_info "Dry run mode - no changes will be made"
fi

if [[ "$USE_SYMLINK" == "true" ]]; then
    print_info "Using symlinks (development mode)"
fi

echo ""
print_info "Installing to: $CLAUDE_DIR"
echo ""

if [[ "$INSTALL_ALL" == "true" ]]; then
    install_commands
    install_skills
    install_hooks
    install_guardrails
    install_templates
    install_mcp
else
    [[ "$INSTALL_COMMANDS" == "true" ]] && install_commands
    [[ "$INSTALL_SKILLS" == "true" ]] && install_skills
    [[ "$INSTALL_HOOKS" == "true" ]] && install_hooks
    [[ "$INSTALL_GUARDRAILS" == "true" ]] && install_guardrails
    [[ "$INSTALL_TEMPLATES" == "true" ]] && install_templates
    [[ "$INSTALL_MCP" == "true" ]] && install_mcp
fi

echo ""
print_success "Installation complete!"
echo ""
print_info "Next steps:"
echo "  1. Restart Claude Code to load new configurations"
echo "  2. Use /command-name to invoke slash commands"
echo "  3. Copy templates to your projects as needed"
echo ""
