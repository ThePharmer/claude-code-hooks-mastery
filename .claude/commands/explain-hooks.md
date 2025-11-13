---
allowed-tools: Read, Grep
description: Explain hook implementation details and lifecycle with examples
---

# Explain Hooks

Provide detailed explanations of Claude Code hook implementations, focusing on educational understanding.

## Instructions

- **IMPORTANT: This is an educational explanation - make it clear and accessible**
- **IMPORTANT: Use concrete examples from the actual hook implementations**
- **IMPORTANT: Explain the "why" behind design decisions, not just the "what"**
- **IMPORTANT: Reference the hook lifecycle and execution context**

## Files

@.claude/hooks/user_prompt_submit.py
@.claude/hooks/pre_tool_use.py
@.claude/hooks/post_tool_use.py
@.claude/hooks/notification.py
@.claude/hooks/stop.py
@.claude/hooks/subagent_stop.py
@.claude/hooks/pre_compact.py
@.claude/hooks/session_start.py
@ai_docs/cc_hooks_docs.md
@README.md

## Explanation Structure

1. **Hook Purpose**: What this hook does and when it fires
2. **Input Format**: JSON structure and expected fields
3. **Output Behavior**: What the hook returns and how it affects flow
4. **Exit Codes**: Meaning of different exit codes (0, 2, other)
5. **Real Example**: Concrete example from our implementation
6. **Use Cases**: When you'd use this hook pattern
7. **Common Pitfalls**: What to avoid
8. **Advanced Patterns**: Sophisticated techniques demonstrated

## Hook to Explain

$ARGUMENTS

## Default Behavior

If no specific hook is provided, give an overview of the complete hook lifecycle and how all 8 hooks work together in the claude-code-hooks-mastery architecture.
