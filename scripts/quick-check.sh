#!/bin/bash
################################################################################
# Claude Code Hooks Mastery - Quick Check Script
################################################################################
# A fast validation script that checks only the essentials without testing
# hook execution. Use this for quick sanity checks.
#
# Usage: ./scripts/quick-check.sh
################################################################################

set -euo pipefail

# Color codes
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    BOLD=''
    NC=''
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FAILED=0

echo -e "${BOLD}${BLUE}Claude Code Hooks Mastery - Quick Check${NC}\n"

# Check UV
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓${NC} UV installed: $(uv --version 2>&1 | head -n1)"
else
    echo -e "${RED}✗${NC} UV not found"
    FAILED=1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python available: $(python3 --version 2>&1)"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    FAILED=1
fi

# Check .claude directory
if [ -d "$PROJECT_ROOT/.claude" ]; then
    echo -e "${GREEN}✓${NC} .claude/ directory exists"
else
    echo -e "${RED}✗${NC} .claude/ directory missing"
    FAILED=1
fi

# Check hooks
HOOK_COUNT=$(ls -1 "$PROJECT_ROOT/.claude/hooks/"*.py 2>/dev/null | wc -l)
if [ "$HOOK_COUNT" -eq 8 ]; then
    echo -e "${GREEN}✓${NC} All 8 hooks present"
else
    echo -e "${YELLOW}⚠${NC} Found $HOOK_COUNT hooks (expected 8)"
fi

# Check settings.json
if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
    if jq empty "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} settings.json valid"
        CONFIGURED=$(jq ".hooks | keys | length" "$PROJECT_ROOT/.claude/settings.json")
        echo -e "${GREEN}✓${NC} Configured hooks: $CONFIGURED"
    else
        echo -e "${RED}✗${NC} settings.json invalid JSON"
        FAILED=1
    fi
else
    echo -e "${RED}✗${NC} settings.json not found"
    FAILED=1
fi

# Check logs directory
if [ -d "$PROJECT_ROOT/logs" ]; then
    echo -e "${GREEN}✓${NC} logs/ directory exists"
else
    echo -e "${YELLOW}⚠${NC} logs/ directory missing (will be auto-created)"
    mkdir -p "$PROJECT_ROOT/logs"
fi

# Check API keys
echo ""
echo -e "${BOLD}Optional API Keys:${NC}"
[ -n "${ELEVENLABS_API_KEY:-}" ] && echo -e "${GREEN}✓${NC} ELEVENLABS_API_KEY set" || echo -e "${YELLOW}⚠${NC} ELEVENLABS_API_KEY not set"
[ -n "${OPENAI_API_KEY:-}" ] && echo -e "${GREEN}✓${NC} OPENAI_API_KEY set" || echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY not set"
[ -n "${ANTHROPIC_API_KEY:-}" ] && echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY set" || echo -e "${YELLOW}⚠${NC} ANTHROPIC_API_KEY not set"

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ Quick check passed!${NC}"
    echo -e "Run ${BLUE}./scripts/setup.sh${NC} for comprehensive validation."
    exit 0
else
    echo -e "${RED}${BOLD}✗ Quick check failed!${NC}"
    echo -e "Run ${BLUE}./scripts/setup.sh${NC} for detailed diagnostics."
    exit 1
fi
