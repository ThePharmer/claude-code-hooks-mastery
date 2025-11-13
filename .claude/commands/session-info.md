---
allowed-tools: Bash, Read
description: Display information about current and past Claude Code sessions
---

# Session Info

Show detailed information about Claude Code sessions, including agent names, prompt history, and session metadata.

## Instructions

- **IMPORTANT: Parse session JSON files carefully**
- **IMPORTANT: Respect privacy - only show metadata, not full prompts**
- **IMPORTANT: Show agent naming patterns and session progression**
- **IMPORTANT: Highlight interesting session characteristics**

## Commands

- List sessions: !`ls -1t .claude/data/sessions/*.json 2>/dev/null | head -10`
- Session count: !`ls -1 .claude/data/sessions/*.json 2>/dev/null | wc -l`
- Current session: !`echo $CLAUDE_SESSION_ID`

## Files

@.claude/hooks/user_prompt_submit.py
@.claude/status_lines/status_line_v3.py

## Session Information to Display

1. **Session Metadata**
   - Session ID
   - Creation timestamp
   - Agent name (if assigned)
   - Total prompts in session

2. **Session History**
   - Recent sessions (last 10)
   - Session naming patterns
   - Session activity timeline

3. **Agent Analysis**
   - Most common agent names
   - Agent naming strategy (Ollama, Anthropic, OpenAI)
   - Unique agent names generated

4. **Session Stats**
   - Total sessions tracked
   - Average prompts per session
   - Oldest and newest sessions

## Output Format

Show:
- **Current Session**: Details about active session
- **Recent Sessions**: Last 10 sessions with key info
- **Statistics**: Overall session metrics
- **Agent Names**: Interesting agent naming examples

## Session Filter

$ARGUMENTS

## Default Behavior

If no session ID provided, show information about the current session and a summary of recent sessions.
