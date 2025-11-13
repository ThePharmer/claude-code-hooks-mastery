---
allowed-tools: Bash, Read, Grep
description: Analyze sub-agent usage patterns and statistics
---

# Agent Usage Statistics

Analyze which sub-agents are being used, how often, and for what purposes.

## Instructions

- **IMPORTANT: Parse logs for agent invocations**
- **IMPORTANT: Show both general and specialized agent usage**
- **IMPORTANT: Identify underutilized agents that could be valuable**
- **IMPORTANT: Provide recommendations for agent usage optimization**

## Commands

- List available agents: !`ls -1 .claude/agents/*.md | wc -l`
- Search logs for agent calls: !`grep -i "agent" logs/*.json 2>/dev/null | wc -l || echo 0`
- Subagent stop events: !`wc -l < logs/subagent_stop.json 2>/dev/null || echo 0`

## Files

@.claude/agents/meta-agent.md
@logs/subagent_stop.json
@CLAUDE.md

## Analysis Areas

1. **Agent Inventory**
   - Total agents available (23)
   - Categories: crypto (13), codebase improvement (6), general (4)
   - Specialized vs. general-purpose agents

2. **Usage Frequency**
   - Most frequently invoked agents
   - Least used agents (potential for deprecation or promotion)
   - Usage patterns over time

3. **Agent Performance**
   - Completion rates
   - Average execution time (from logs)
   - Common failure modes

4. **Crypto Agent Analysis**
   - Usage across different model tiers (haiku, sonnet, opus)
   - Most popular crypto research workflows
   - Cost-effectiveness analysis

5. **Recommendations**
   - Underutilized powerful agents
   - Agent combinations that work well together
   - Gaps in agent coverage

## Output Format

Show:
- **Inventory Summary**: All available agents by category
- **Usage Statistics**: Frequency and patterns
- **Top Agents**: Most valuable agents by usage
- **Recommendations**: How to leverage agents better
- **Optimization Ideas**: Agent workflow improvements

## Analysis Scope

$ARGUMENTS

## Default Behavior

If no specific scope provided, analyze all available agents and provide comprehensive usage statistics with recommendations.
