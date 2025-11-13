#!/bin/bash

################################################################################
# Claude Code Hooks Mastery - Setup and Validation Script
################################################################################
# This script validates your environment and ensures all components are
# properly configured for the educational hook repository.
#
# Usage: ./scripts/setup.sh
################################################################################

set -euo pipefail

# Color codes for output (if terminal supports it)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    MAGENTA=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Get the script's directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Counters for summary
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Arrays for tracking results
declare -a FAILED_CHECKS
declare -a WARNING_MESSAGES
declare -a SUCCESS_MESSAGES

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_section() {
    echo -e "\n${BOLD}${MAGENTA}▶ $1${NC}"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
    SUCCESS_MESSAGES+=("$1")
}

print_failure() {
    echo -e "  ${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
    FAILED_CHECKS+=("$1")
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
    WARNING_MESSAGES+=("$1")
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

print_solution() {
    echo -e "    ${CYAN}→${NC} ${YELLOW}Solution:${NC} $1"
}

################################################################################
# Environment Validation
################################################################################

check_environment() {
    print_header "1. Environment Validation"

    print_section "Checking Required Tools"

    # Check UV
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version 2>&1 | head -n1)
        print_success "UV is installed ($UV_VERSION)"
    else
        print_failure "UV is not installed (REQUIRED)"
        print_solution "Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
        print_solution "Or visit: https://docs.astral.sh/uv/getting-started/installation/"
    fi

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
        PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python 3.8+ is available ($PYTHON_VERSION)"
        else
            print_failure "Python 3.8+ required, found $PYTHON_VERSION"
            print_solution "Install Python 3.8 or higher from https://www.python.org/downloads/"
        fi
    else
        print_failure "Python 3 is not installed (REQUIRED)"
        print_solution "Install Python 3.8+: https://www.python.org/downloads/"
    fi

    # Check Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git is installed ($GIT_VERSION)"
    else
        print_failure "Git is not installed (REQUIRED)"
        print_solution "Install Git: https://git-scm.com/downloads"
    fi

    # Verify .claude/ directory
    if [ -d "$PROJECT_ROOT/.claude" ]; then
        print_success ".claude/ directory exists"
    else
        print_failure ".claude/ directory not found"
        print_solution "This doesn't appear to be a valid Claude Code Hooks repository"
    fi
}

################################################################################
# Optional API Key Detection
################################################################################

check_api_keys() {
    print_header "2. Optional API Key Detection"

    print_info "These API keys are optional but enhance functionality:"
    echo ""

    # Check ElevenLabs API Key
    if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
        print_success "ELEVENLABS_API_KEY is set (Premium TTS enabled)"
    else
        print_warning "ELEVENLABS_API_KEY not set (Premium TTS disabled)"
        print_solution "Get API key from: https://elevenlabs.io/"
        print_solution "Export: export ELEVENLABS_API_KEY='your-key-here'"
    fi

    # Check OpenAI API Key
    if [ -n "${OPENAI_API_KEY:-}" ]; then
        print_success "OPENAI_API_KEY is set (OpenAI LLM fallback enabled)"
    else
        print_warning "OPENAI_API_KEY not set (OpenAI features disabled)"
        print_solution "Get API key from: https://platform.openai.com/api-keys"
        print_solution "Export: export OPENAI_API_KEY='your-key-here'"
    fi

    # Check Anthropic API Key
    if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
        print_success "ANTHROPIC_API_KEY is set (Anthropic LLM fallback enabled)"
    else
        print_warning "ANTHROPIC_API_KEY not set (Anthropic features disabled)"
        print_solution "Get API key from: https://console.anthropic.com/"
        print_solution "Export: export ANTHROPIC_API_KEY='your-key-here'"
    fi

    echo ""
    print_info "Note: Hooks will fallback to local services (pyttsx3, Ollama) if keys are missing"
}

################################################################################
# Hook Validation
################################################################################

check_hooks() {
    print_header "3. Hook Validation"

    local hooks_dir="$PROJECT_ROOT/.claude/hooks"

    if [ ! -d "$hooks_dir" ]; then
        print_failure "Hooks directory not found at $hooks_dir"
        return
    fi

    # Define all expected hooks
    declare -a HOOK_FILES=(
        "user_prompt_submit.py"
        "pre_tool_use.py"
        "post_tool_use.py"
        "notification.py"
        "stop.py"
        "subagent_stop.py"
        "pre_compact.py"
        "session_start.py"
    )

    print_section "Checking Hook Files"

    for hook in "${HOOK_FILES[@]}"; do
        local hook_path="$hooks_dir/$hook"

        if [ ! -f "$hook_path" ]; then
            print_failure "Hook not found: $hook"
            continue
        fi

        # Check if executable
        if [ ! -x "$hook_path" ]; then
            # Try to make it executable
            chmod +x "$hook_path" 2>/dev/null || true
        fi

        print_success "Found: $hook"
    done

    print_section "Testing Hook Execution with UV"

    for hook in "${HOOK_FILES[@]}"; do
        local hook_path="$hooks_dir/$hook"

        if [ ! -f "$hook_path" ]; then
            continue
        fi

        # Test UV execution with simple JSON input
        # Different hooks expect different JSON structures
        local test_json=""

        case "$hook" in
            user_prompt_submit.py)
                test_json='{"prompt":"test","sessionId":"test-session"}'
                ;;
            pre_tool_use.py)
                test_json='{"tool":"Bash","parameters":{"command":"echo test"}}'
                ;;
            post_tool_use.py)
                test_json='{"tool":"Bash","output":"test output"}'
                ;;
            notification.py)
                test_json='{"message":"test notification"}'
                ;;
            stop.py)
                test_json='{"sessionId":"test-session"}'
                ;;
            subagent_stop.py)
                test_json='{"agent":"test-agent","sessionId":"test-session"}'
                ;;
            pre_compact.py)
                test_json='{"sessionId":"test-session"}'
                ;;
            session_start.py)
                test_json='{"sessionId":"test-session"}'
                ;;
        esac

        # Run the hook with test JSON (suppress output, just check exit code)
        if echo "$test_json" | timeout 5 uv run "$hook_path" &> /dev/null; then
            print_success "Executable with UV: $hook"
        else
            # Exit code might be non-zero intentionally, check if UV can at least run it
            if timeout 5 uv run --version &> /dev/null; then
                print_warning "Hook runs but may have returned non-zero exit: $hook"
                print_solution "This may be normal behavior - check hook logs for details"
            else
                print_failure "Cannot execute with UV: $hook"
                print_solution "Check UV installation and hook dependencies"
            fi
        fi
    done
}

################################################################################
# Settings Validation
################################################################################

check_settings() {
    print_header "4. Settings Validation"

    local settings_file="$PROJECT_ROOT/.claude/settings.json"

    print_section "Validating settings.json"

    if [ ! -f "$settings_file" ]; then
        print_failure "settings.json not found at $settings_file"
        print_solution "Create .claude/settings.json with hook configurations"
        return
    fi

    # Check if valid JSON
    if jq empty "$settings_file" 2>/dev/null; then
        print_success "settings.json is valid JSON"
    else
        print_failure "settings.json is invalid JSON"
        print_solution "Fix JSON syntax errors in .claude/settings.json"
        return
    fi

    # Check for hook configurations
    local hook_types=(
        "UserPromptSubmit"
        "PreToolUse"
        "PostToolUse"
        "Notification"
        "Stop"
        "SubagentStop"
        "PreCompact"
        "SessionStart"
    )

    print_section "Checking Hook Configurations"

    for hook_type in "${hook_types[@]}"; do
        if jq -e ".hooks.$hook_type" "$settings_file" &> /dev/null; then
            print_success "Hook configured: $hook_type"
        else
            print_warning "Hook not configured: $hook_type"
            print_solution "Add $hook_type configuration to .claude/settings.json"
        fi
    done

    # Check status line configuration
    print_section "Checking Status Line Configuration"

    if jq -e '.statusLine' "$settings_file" &> /dev/null; then
        local status_type=$(jq -r '.statusLine.type // "not set"' "$settings_file")
        local status_command=$(jq -r '.statusLine.command // "not set"' "$settings_file")
        print_success "Status line configured (type: $status_type)"
        print_info "Command: $status_command"
    else
        print_warning "Status line not configured"
        print_solution "Add statusLine configuration to .claude/settings.json"
    fi

    # Check permissions
    print_section "Checking Permissions"

    if jq -e '.permissions' "$settings_file" &> /dev/null; then
        local allow_count=$(jq '.permissions.allow | length' "$settings_file")
        local deny_count=$(jq '.permissions.deny | length' "$settings_file")
        print_success "Permissions configured ($allow_count allowed, $deny_count denied)"
    else
        print_warning "Permissions not configured"
        print_solution "Add permissions configuration to .claude/settings.json"
    fi
}

################################################################################
# Directory Structure Check
################################################################################

check_directories() {
    print_header "5. Directory Structure Check"

    print_section "Checking Expected Directories"

    local expected_dirs=(
        ".claude"
        ".claude/hooks"
        ".claude/agents"
        ".claude/commands"
        ".claude/output-styles"
        ".claude/status_lines"
        "ai_docs"
        "scripts"
    )

    for dir in "${expected_dirs[@]}"; do
        local full_path="$PROJECT_ROOT/$dir"
        if [ -d "$full_path" ]; then
            print_success "Directory exists: $dir"
        else
            print_warning "Directory missing: $dir"
        fi
    done

    print_section "Creating Auto-Generated Directories"

    # Create logs directory if missing
    local logs_dir="$PROJECT_ROOT/logs"
    if [ ! -d "$logs_dir" ]; then
        mkdir -p "$logs_dir"
        print_success "Created logs/ directory"
    else
        print_success "logs/ directory exists"
    fi

    # Create sessions directory if missing
    local sessions_dir="$PROJECT_ROOT/.claude/data/sessions"
    if [ ! -d "$sessions_dir" ]; then
        mkdir -p "$sessions_dir"
        print_success "Created .claude/data/sessions/ directory"
    else
        print_success ".claude/data/sessions/ directory exists"
    fi

    print_section "Checking Key Files"

    local key_files=(
        "README.md"
        "CLAUDE.md"
        ".claude/settings.json"
    )

    for file in "${key_files[@]}"; do
        local full_path="$PROJECT_ROOT/$file"
        if [ -f "$full_path" ]; then
            print_success "File exists: $file"
        else
            print_warning "File missing: $file"
        fi
    done
}

################################################################################
# Summary Report
################################################################################

print_summary() {
    print_header "Setup Validation Summary"

    local total_checks=$((CHECKS_PASSED + CHECKS_FAILED))

    echo -e "${BOLD}Results:${NC}"
    echo -e "  ${GREEN}✓ Passed:${NC}  $CHECKS_PASSED"
    echo -e "  ${RED}✗ Failed:${NC}  $CHECKS_FAILED"
    echo -e "  ${YELLOW}⚠ Warnings:${NC} $WARNINGS"
    echo -e "  ${BLUE}━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${BOLD}Total:${NC}    $total_checks checks"

    # Show failed checks
    if [ $CHECKS_FAILED -gt 0 ]; then
        echo -e "\n${BOLD}${RED}Failed Checks:${NC}"
        for check in "${FAILED_CHECKS[@]}"; do
            echo -e "  ${RED}✗${NC} $check"
        done
    fi

    # Show warnings
    if [ $WARNINGS -gt 0 ]; then
        echo -e "\n${BOLD}${YELLOW}Warnings:${NC}"
        for warning in "${WARNING_MESSAGES[@]}"; do
            echo -e "  ${YELLOW}⚠${NC} $warning"
        done
    fi

    # Overall status
    echo ""
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}${GREEN}✓ Setup validation passed!${NC}"
        echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${BOLD}Next Steps:${NC}"
        echo -e "  1. ${CYAN}Review logs directory:${NC} ls -la logs/"
        echo -e "  2. ${CYAN}Test a hook manually:${NC} echo '{\"prompt\":\"test\"}' | uv run .claude/hooks/user_prompt_submit.py"
        echo -e "  3. ${CYAN}Start Claude Code:${NC} claude"
        echo -e "  4. ${CYAN}Check status line:${NC} It should display session info at the top"
        echo -e "  5. ${CYAN}View hook logs:${NC} tail -f logs/user_prompt_submit.json"

        if [ $WARNINGS -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}Note: Some optional features are disabled due to missing API keys.${NC}"
            echo -e "${YELLOW}The repository will still work with local fallbacks.${NC}"
        fi
    else
        echo -e "${BOLD}${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}${RED}✗ Setup validation failed!${NC}"
        echo -e "${BOLD}${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${BOLD}Action Required:${NC}"
        echo -e "  Fix the failed checks listed above before using this repository."
        echo -e "  Refer to the ${CYAN}Solution${NC} messages for guidance."
    fi

    echo ""
    echo -e "${BOLD}Resources:${NC}"
    echo -e "  ${BLUE}•${NC} Project Documentation: ${CYAN}CLAUDE.md${NC}"
    echo -e "  ${BLUE}•${NC} Hook Documentation: ${CYAN}ai_docs/cc_hooks_docs.md${NC}"
    echo -e "  ${BLUE}•${NC} Claude Code Docs: ${CYAN}https://docs.anthropic.com/en/docs/claude-code/hooks${NC}"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    echo -e "${BOLD}${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                        ║"
    echo "║           Claude Code Hooks Mastery - Setup Validator                 ║"
    echo "║                                                                        ║"
    echo "║  Educational repository demonstrating complete hook lifecycle         ║"
    echo "║                                                                        ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    print_info "Project Root: $PROJECT_ROOT"
    print_info "Validating environment and configuration..."

    # Run all checks
    check_environment
    check_api_keys
    check_hooks
    check_settings
    check_directories

    # Print summary
    print_summary

    # Exit with appropriate code
    if [ $CHECKS_FAILED -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main "$@"
