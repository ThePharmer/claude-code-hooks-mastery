---
allowed-tools: Bash, Read, Grep
description: Analyze log files for patterns, errors, and insights
---

# Analyze Logs

Parse and analyze hook execution logs to identify patterns, errors, and usage statistics.

## Instructions

- **IMPORTANT: Parse JSON log files properly**
- **IMPORTANT: Identify interesting patterns and anomalies**
- **IMPORTANT: Provide statistical summaries**
- **IMPORTANT: Highlight security-relevant events (blocks, sensitive file access)**

## Commands

- List all logs: !`ls -lh logs/*.json 2>/dev/null || echo "No logs found"`
- Log entry counts: !`for f in logs/*.json; do echo "$f: $(wc -l < "$f" 2>/dev/null || echo 0)"; done`

## Files

@logs/README.md

## Analysis Categories

1. **Hook Execution Frequency**
   - Which hooks are called most often
   - Execution timeline and patterns

2. **Security Events**
   - Blocked commands (exit code 2 from pre_tool_use)
   - Sensitive file access attempts
   - Dangerous command patterns detected

3. **Tool Usage Patterns**
   - Most commonly used tools
   - Command patterns and workflows

4. **Session Activity**
   - Active sessions over time
   - Agent naming patterns
   - Session duration estimates

5. **Error Analysis**
   - Hook failures or exceptions
   - Timeout issues
   - Invalid input patterns

## Output Format

Provide:
- **Summary Statistics**: Entry counts, date ranges
- **Top Patterns**: Most frequent events
- **Security Highlights**: Blocks and interventions
- **Anomalies**: Unusual or interesting events
- **Recommendations**: Suggested improvements or investigations

## Analysis Scope

$ARGUMENTS

## Default Behavior

If no specific scope provided, analyze all logs comprehensively with focus on the most recent 100 entries per log type.
