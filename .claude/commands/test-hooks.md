---
allowed-tools: Bash, Read
description: Test hook execution with sample inputs and validate behavior
---

# Test Hooks

Execute hooks with test inputs to validate they're working correctly and demonstrate their behavior.

## Instructions

- **IMPORTANT: Test hooks safely with appropriate sample inputs**
- **IMPORTANT: Show both successful and blocking scenarios**
- **IMPORTANT: Explain what each test demonstrates**
- **IMPORTANT: Validate exit codes and output format**

## Files

@.claude/hooks/user_prompt_submit.py
@.claude/hooks/pre_tool_use.py
@.claude/hooks/post_tool_use.py
@logs/README.md

## Testing Approach

1. **Prepare Test Input**: Create appropriate JSON for hook type
2. **Execute Hook**: Run with `echo 'JSON' | uv run .claude/hooks/HOOK.py`
3. **Capture Output**: Show stdout, stderr, and exit code
4. **Validate Behavior**: Confirm it matches expected behavior
5. **Demonstrate Flow Control**: Show blocking (exit 2) examples

## Common Test Cases

### UserPromptSubmit
```bash
echo '{"prompt":"test prompt","session_id":"test-123"}' | uv run .claude/hooks/user_prompt_submit.py
```

### PreToolUse (Dangerous Command)
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"},"session_id":"test-123"}' | uv run .claude/hooks/pre_tool_use.py
echo $?  # Should be 2 (blocked)
```

### PreToolUse (Safe Command)
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"},"session_id":"test-123"}' | uv run .claude/hooks/pre_tool_use.py
echo $?  # Should be 0 (allowed)
```

## Hook to Test

$ARGUMENTS

## Default Behavior

If no specific hook is provided, run a comprehensive test suite across all 8 hooks with representative inputs.
