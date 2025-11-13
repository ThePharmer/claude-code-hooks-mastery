# Contributing to Claude Code Hooks Mastery

Thank you for your interest in contributing to this educational repository! This guide will help you get started, whether you're a beginner learning about Claude Code hooks or an experienced developer adding advanced features.

## Table of Contents

1. [Welcome](#welcome)
2. [Getting Started](#getting-started)
3. [Understanding the Project Structure](#understanding-the-project-structure)
4. [Learning Paths](#learning-paths)
5. [Making Changes](#making-changes)
6. [Code Standards](#code-standards)
7. [Testing Your Changes](#testing-your-changes)
8. [Submitting Contributions](#submitting-contributions)
9. [Common Patterns](#common-patterns)
10. [Getting Help](#getting-help)

## Welcome

This is an **educational repository** designed to help developers understand and master Claude Code hooks. Whether you're:

- Learning hooks for the first time
- Building production-ready security patterns
- Experimenting with AI agent architectures
- Contributing improvements back to the community

...you're in the right place. This guide will help you contribute in a way that benefits both the project and your learning journey.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **[Astral UV](https://docs.astral.sh/uv/getting-started/installation/)** - Python package installer (required for all hooks)
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** - Anthropic's CLI tool
- **Git** - Version control
- Basic familiarity with Python and markdown

Optional (recommended for advanced features):

- **ElevenLabs API key** - Premium text-to-speech integration
- **OpenAI API key** - GPT-4 completions and TTS
- **Anthropic API key** - Claude completions
- **Ollama** - Local LLM with `gpt-oss:20b` model

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-code-hooks-mastery.git
   cd claude-code-hooks-mastery
   ```
3. Add the upstream repository for syncing:
   ```bash
   git remote add upstream https://github.com/ThePharmer/claude-code-hooks-mastery.git
   ```

### Initial Setup

1. **Verify dependencies are installed:**
   ```bash
   uv --version          # Should show UV version
   claude --version      # Should show Claude Code version
   ```

2. **Check the hook configuration:**
   ```bash
   cat .claude/settings.json | jq .
   ```

3. **Review existing hooks to understand the codebase:**
   ```bash
   ls -la .claude/hooks/
   ```

4. **Test a hook manually:**
   ```bash
   echo '{"prompt":"test"}' | uv run .claude/hooks/user_prompt_submit.py --log-only
   ```

If all these work, you're ready to contribute!

## Understanding the Project Structure

Here's a quick overview of the key directories:

```
claude-code-hooks-mastery/
├── .claude/                        # Claude Code configuration
│   ├── settings.json              # Hook definitions and permissions
│   ├── hooks/                     # 8 hook implementations (Python + UV)
│   │   ├── user_prompt_submit.py  # Most powerful hook - runs first
│   │   ├── pre_tool_use.py        # Security blocking - runs before tools
│   │   ├── post_tool_use.py       # Result logging - runs after tools
│   │   ├── notification.py        # Custom notifications with TTS
│   │   ├── stop.py                # AI-generated completions
│   │   ├── subagent_stop.py       # Subagent completion tracking
│   │   ├── pre_compact.py         # Transcript backup
│   │   ├── session_start.py       # Development context loading
│   │   └── utils/                 # Shared utilities
│   ├── agents/                    # Sub-agent definitions
│   │   ├── meta-agent.md          # Agent that creates agents
│   │   ├── hello-world-agent.md   # Simple learning example
│   │   └── ...                    # 10+ other specialized agents
│   ├── commands/                  # Custom slash commands
│   ├── output-styles/             # 8 response formatting styles
│   ├── status_lines/              # 4 status line variants
│   └── data/                      # Session data (auto-generated)
├── logs/                          # Hook execution logs (gitignored)
├── ai_docs/                       # Anthropic documentation references
├── README.md                      # Project overview
├── CLAUDE.md                      # Detailed project notes (READ THIS!)
└── CONTRIBUTING.md                # This file
```

**Key files to study before contributing:**

- **`.claude/settings.json`** - Central configuration for all hooks
- **`README.md`** - Hook lifecycle, flow control, and examples
- **`CLAUDE.md`** - Educational content and learning paths
- **`.claude/hooks/user_prompt_submit.py`** - Best example of hook implementation

## Learning Paths

Before making changes, choose your learning path based on your current level. See `CLAUDE.md` for detailed information.

### Beginner Path (Start Here!)

If you're new to Claude Code hooks:

1. Read `ai_docs/cc_hooks_docs.md` for hook fundamentals
2. Study `.claude/agents/hello-world-agent.md` for a simple example
3. Review `README.md` sections on hook lifecycle
4. Test output styles: `/output-style genui`
5. Run a command and examine logs: `cat logs/user_prompt_submit.json | jq .`
6. **First Contribution:** Add a new output style or simple sub-agent

### Intermediate Path (Building Skills)

For developers comfortable with hooks:

1. Study `README.md` hook error codes and flow control sections
2. Understand `.claude/hooks/user_prompt_submit.py` thoroughly
3. Learn `.claude/hooks/pre_tool_use.py` security patterns
4. Create custom sub-agents using the meta-agent
5. Implement simple status line modifications
6. **Second Contribution:** Enhance an existing hook with new features

### Advanced Path (Expert Level)

For experienced developers:

1. Master `.claude/hooks/stop.py` completion message generation
2. Build multi-agent workflows with agent chaining
3. Implement sophisticated flow control with JSON decisions
4. Integrate external services (ElevenLabs, OpenAI, Anthropic)
5. Create production-ready security patterns
6. **Advanced Contributions:** Complex hook enhancements, new agents, or integrations

## Making Changes

### Contribution Types

Good contributions include:

- **Bug fixes** in existing hooks
- **New sub-agents** for specialized tasks
- **New output styles** for response formatting
- **Documentation improvements** with examples
- **New custom commands** for workflows
- **Test improvements** and testing utilities
- **Status line enhancements**
- **Security improvements**

### Before You Start

1. **Check the issues** - Comment if you plan to work on something
2. **Create a branch** - Use descriptive names:
   ```bash
   git checkout -b add/cryptocurrency-agent
   git checkout -b fix/hook-timeout-issue
   git checkout -b docs/hook-examples
   ```
3. **Read CLAUDE.md** - Understand project philosophy and patterns
4. **Test in isolation first** - Don't test against production
5. **Keep changes focused** - One feature or fix per pull request

### Workflow Example

Let's say you want to add a new output style:

```bash
# Create a branch
git checkout -b add/json-output-style

# Create your output style
cat > .claude/output-styles/json-compact.md << 'EOF'
---
name: json-compact
description: Compact JSON format for API responses
---

Format all responses as valid, minified JSON...
EOF

# Test it locally
/output-style json-compact

# Review what you changed
git diff

# Commit with clear message
git add .claude/output-styles/json-compact.md
git commit -m "Add json-compact output style for API responses"

# Push to your fork
git push origin add/json-output-style
```

## Code Standards

This project follows specific standards to maintain consistency and educational value.

### UV Single-File Scripts

All Python hooks use **UV single-file scripts** with embedded dependencies:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.28.0",
#     "python-dotenv>=0.19.0",
# ]
# ///

import sys
import json
import requests
from dotenv import load_dotenv

# Your hook code here
```

**Benefits:**

- No virtual environment management needed
- Each hook is self-contained and portable
- Fast execution with UV's dependency resolution
- Clear separation from main project dependencies

**Guidelines:**

- Keep dependencies minimal - only import what you use
- Pin major versions: `requests>=2.28.0`
- Test that `uv run` works in isolation
- Add comments explaining non-obvious dependencies

### Hook Standards

Every hook must follow these patterns:

**1. Execution Timeout - 60 Seconds Maximum**

All hooks have a 60-second execution limit. Keep hooks fast:

```python
# Good: Fast and responsive
start = time.time()
if time.time() - start > 55:  # Leave 5s buffer
    print("TIMEOUT: Hook taking too long", file=sys.stderr)
    sys.exit(1)
```

**2. Exit Code Meanings**

- **Exit 0:** Success (output shown if applicable)
- **Exit 2:** Blocking error (stderr fed to Claude)
- **Other:** Non-blocking error (shown to user)

```python
# Block a tool execution
print("BLOCKED: Dangerous command detected", file=sys.stderr)
sys.exit(2)  # Tells Claude about the block

# Non-blocking error
print("Warning: Tool may have side effects", file=sys.stderr)
sys.exit(1)  # Shows warning but doesn't block
```

**3. JSON Input Parsing**

Hooks receive JSON via stdin:

```python
import json
import sys

try:
    payload = json.load(sys.stdin)
    prompt = payload.get("prompt", "")
    session_id = payload.get("session_id", "")
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)
```

**4. JSON Output Control**

Return JSON for sophisticated control:

```python
import json

# Block with reason
decision = {
    "decision": "block",
    "reason": "Security validation failed: dangerous pattern detected"
}
print(json.dumps(decision))
sys.exit(0)

# Suppress output
output = {
    "suppressOutput": True,
    "continue": True
}
print(json.dumps(output))
sys.exit(0)
```

**5. Security Patterns**

Always validate input and avoid dangerous operations:

```python
import re
import os

# Validate dangerous patterns
dangerous_patterns = [
    r'rm\s+.*-[rf]',      # rm -rf variants
    r'sudo\s+rm',         # sudo rm commands
    r'>\s*/etc/',         # Writing to system
]

def is_dangerous(command):
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False

# Never access sensitive files directly
if '.env' in command or '~/.ssh' in command:
    print("BLOCKED: Sensitive file access", file=sys.stderr)
    sys.exit(2)
```

**6. Logging Patterns**

Log events consistently as JSON:

```python
import json
from datetime import datetime

def log_event(event_name, data):
    """Append event to logs/[event_name].json"""
    log_file = f"logs/{event_name}.json"

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": os.getenv("CLAUDE_CODE_SESSION_ID", "unknown"),
        **data
    }

    # Append to log file (create if doesn't exist)
    entries = []
    if os.path.exists(log_file):
        try:
            with open(log_file) as f:
                entries = json.load(f)
        except:
            entries = []

    entries.append(entry)
    os.makedirs("logs", exist_ok=True)
    with open(log_file, "w") as f:
        json.dump(entries, f, indent=2)

# Usage
log_event("user_prompt_submit", {
    "prompt": prompt,
    "validation_passed": True
})
```

### Sub-Agent Standards

Sub-agents are system prompts in markdown format. They must have:

```markdown
---
name: agent-name
description: When Claude should use this agent (critical!)
tools: Tool1, Tool2, Tool3  # Optional - inherits all if omitted
color: Cyan  # Visual identifier in terminal
model: sonnet  # Optional - haiku | sonnet | opus
---

# Purpose
You are a [role description].

## Instructions
1. Step-by-step what the agent should do
2. How to approach problems
3. How to report results

## Report/Response Format
How to communicate results back to the primary agent.
```

**Critical Rule:** The content is a **system prompt**, not a user prompt. This is the #1 mistake when creating agents. See `README.md` for details.

### Documentation Standards

All documentation should:

- Use clear, concise language
- Include concrete examples
- Reference related sections with links
- Use code blocks with syntax highlighting
- Follow markdown conventions
- Explain "why" not just "what"

### Code Comments

Write comments that explain intent:

```python
# Good: Explains why
# Check for .env access since it contains secrets
if '.env' in tool_input:
    sys.exit(2)

# Bad: States the obvious
# Check if .env is in tool_input
if '.env' in tool_input:
    sys.exit(2)
```

## Testing Your Changes

### Manual Hook Testing

Test hooks in isolation before committing:

```bash
# Test user_prompt_submit hook
echo '{"prompt":"test prompt","session_id":"test-session"}' | \
  uv run .claude/hooks/user_prompt_submit.py --log-only

# Test pre_tool_use hook with dangerous command
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | \
  uv run .claude/hooks/pre_tool_use.py

# Check exit code
echo $?

# View generated logs
cat logs/user_prompt_submit.json | jq .
```

### Integration Testing

Test hooks within Claude Code:

1. **Enable a single hook** in `.claude/settings.json`
2. **Run a prompt** that triggers the hook
3. **Check logs** for the expected output
4. **Verify behavior** - does it block, log, or enhance as expected?

Example testing sequence:

```bash
# 1. Check current logs don't have your test data
cat logs/user_prompt_submit.json | jq '.[-1]'

# 2. Run Claude Code with a test prompt
claude

# 3. At the prompt, type a simple test
# "What is 2 + 2?"

# 4. Press Ctrl-D to exit

# 5. Verify your hook captured the prompt
cat logs/user_prompt_submit.json | jq '.[-1]'

# 6. Check the format matches expectations
cat logs/user_prompt_submit.json | jq 'map(.prompt)' | head -5
```

### Agent Testing

Test sub-agents in Claude Code:

```bash
# 1. Start Claude Code
claude

# 2. At the prompt, ask Claude to use your agent
# "Use [your-agent-name] to [task description]"

# 3. Let Claude Code run

# 4. Verify the agent executed correctly
# - Did it produce the right output?
# - Did it follow the system prompt?
# - Did it report results clearly?
```

### Pre-Submission Checklist

Before submitting a PR, verify:

- [ ] Code follows the standards above
- [ ] Hook exits with correct codes (0, 2, other)
- [ ] JSON input/output is valid
- [ ] Tested manually and works correctly
- [ ] No hardcoded API keys or secrets
- [ ] Dependencies are minimal and pinned
- [ ] Documentation is clear and complete
- [ ] No infinite loops (especially in Stop hooks)
- [ ] Code timeout is under 60 seconds
- [ ] Commit message is clear and descriptive

## Submitting Contributions

### Preparing Your Pull Request

1. **Sync with upstream** before creating your PR:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test one final time** to ensure everything works

3. **Write a clear commit message:**
   ```
   Add cryptocurrency sub-agent for market analysis

   - Creates new sub-agent with crypto-specific instructions
   - Integrates with existing price API utilities
   - Includes examples in agent description
   - Follows standard agent template format
   ```

4. **Push to your fork:**
   ```bash
   git push origin your-branch-name
   ```

5. **Create a pull request** with:
   - **Title:** Clear, descriptive summary
   - **Description:** Explain what, why, and how
   - **Testing:** How to test this change
   - **References:** Link any related issues

### Pull Request Template

```markdown
## Description
Brief explanation of the change.

## Type of Change
- [ ] New hook feature
- [ ] New sub-agent
- [ ] New output style
- [ ] Bug fix
- [ ] Documentation improvement
- [ ] Other: ___

## Testing
How was this tested? Include specific commands:
```
echo '{}' | uv run .claude/hooks/...
```

## Related Issues
Fixes #(issue number) if applicable

## Checklist
- [ ] Code follows standards in CONTRIBUTING.md
- [ ] Tested manually
- [ ] No API keys or secrets in code
- [ ] Documentation is clear
- [ ] Commit messages are descriptive
```

### What Makes a Good Contribution

We love contributions that:

1. **Are well-tested** - Includes manual testing steps
2. **Are focused** - One feature or fix per PR
3. **Have clear intent** - Explains why this change matters
4. **Follow patterns** - Matches existing code style
5. **Document thoroughly** - Includes examples for users
6. **Consider security** - Reviews safety implications
7. **Are educational** - Others can learn from your code

### What We Won't Accept

- Contributions with hardcoded API keys or secrets
- Hooks that exceed 60-second timeout
- Code that ignores security patterns
- PRs without test instructions
- Changes that break existing functionality without fixing something
- Un-reviewed dependencies

## Common Patterns

### Pattern 1: Adding a New Output Style

Output styles are markdown files in `.claude/output-styles/`:

```markdown
---
name: my-style
description: Short description of when to use this style
---

# Response Format Instructions

Format all responses using [describe your format].

Include examples if helpful.

Maintain readability while [specific formatting goal].
```

**Test it:** `/output-style my-style`

### Pattern 2: Creating a New Sub-Agent

Create a markdown file in `.claude/agents/`:

```markdown
---
name: my-agent
description: Build X to solve Y problem (this description tells Claude when to use you)
tools: Bash, Read, Write  # Optional - defaults to all
color: Green
model: sonnet
---

# Purpose
You are an expert in [domain]. Your role is to [primary responsibility].

## Core Instructions
1. Follow these steps to solve problems
2. Always validate your work
3. Report results in this format

## Response Format
Provide your findings as:
- Key insights
- Recommendations
- Next steps
```

**Test it:** In Claude Code, ask it to use your agent for a task.

### Pattern 3: Enhancing an Existing Hook

Study the existing hook first, then add features:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "python-dotenv>=0.19.0",
# ]
# ///

import json
import sys
import os
from datetime import datetime

# Read input
payload = json.load(sys.stdin)

# Add your enhancement here
# Remember: exit codes 0, 2, or other
# JSON output for complex control

# Example: validate before logging
if validate_input(payload):
    log_event("hook_name", payload)
    sys.exit(0)
else:
    print("Invalid input", file=sys.stderr)
    sys.exit(2)
```

### Pattern 4: Adding Security Validations

Security improvements are always welcome:

```python
def is_safe_command(command):
    """Check if command is safe to execute."""
    dangerous_patterns = [
        r'rm\s+.*-[rf]',
        r'sudo\s+rm',
        r'chmod\s+777',
        r'>\s*/etc/',
        r'>\s*/root/',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    return True

# Use in hook
if not is_safe_command(tool_input):
    print("BLOCKED: Unsafe command pattern", file=sys.stderr)
    sys.exit(2)
```

## Getting Help

### Resources

- **Official Claude Code Docs:** [docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code)
- **Sub-Agents Video:** [YouTube tutorial](https://youtu.be/7B2HJr0Y68g)
- **Status Lines & Output Styles:** [YouTube walkthrough](https://youtu.be/mJhsWrEv-Go)
- **Project Documentation:** See `CLAUDE.md`
- **Hook Examples:** Review `.claude/hooks/`

### Asking Questions

- **In issues:** Ask about specific features or bugs
- **In PRs:** Discuss your approach before implementing
- **In comments:** Explain your reasoning and ask for feedback
- **On YouTube:** Follow [IndyDevDan](https://www.youtube.com/@indydevdan) for additional tutorials

### Code Review

When we review your PR, we'll:

1. Check it follows the standards
2. Ensure it's well-tested
3. Verify security implications
4. Confirm it aligns with project goals
5. Provide constructive feedback

We appreciate your patience during review. This is a learning project, so discussions about your code are valuable learning opportunities.

## Code of Conduct

This is an educational community. We expect:

- **Respectful interaction** - Treat all contributors with respect
- **Constructive feedback** - Help each other improve
- **Patience with learning** - This is a learning project
- **No harassment** - Create a welcoming environment
- **Focus on ideas** - Discuss code and approaches, not people

## Final Words

Thank you for contributing to Claude Code Hooks Mastery! Whether you're:

- Adding your first documentation improvement
- Creating your first sub-agent
- Implementing a sophisticated security pattern
- Helping others learn through your examples

...you're making this project better for everyone.

The philosophy of this project is: "Figure out how to scale it up. Build the thing that builds the thing." Your contributions help others build better things with Claude Code.

Happy hacking!

---

**Questions?** Open an issue or start a discussion. We're here to help you succeed.
