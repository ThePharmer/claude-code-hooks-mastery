# Kintsugi-Agent: Self-Improving Meta-Agent System

> *"The art of repairing broken pottery with gold, making it more beautiful than before."*

## Project Vision

Build a **self-improving meta-agent system** that autonomously analyzes and improves agent performance using Claude Agent SDK integrated with Claude Code CLI hooks infrastructure. Like the Japanese art of Kintsugi, this system finds fractures in agent performance and repairs them with wisdom, making agents stronger and more capable.

**Primary Goal:** Autonomous agent improvement through performance tracking → multi-dimensional analysis → generation → validation → deployment loop.

**Success Criteria:** Measurable improvement in agent quality (correctness, cost, reliability, speed) without manual intervention.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Phase 1: Core Improvement Loop](#phase-1-core-improvement-loop)
3. [Phase 2: Self-Improvement Architecture](#phase-2-self-improvement-architecture)
4. [Phoenix Pattern Integration](#phoenix-pattern-integration)
5. [Multi-Dimensional Analysis Framework](#multi-dimensional-analysis-framework)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Configuration Reference](#configuration-reference)

---

## System Architecture

### Overview: Hybrid CLI + SDK

The system uses a **three-layer architecture** that preserves existing Claude Code CLI hooks while adding SDK intelligence:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: CLI Hooks (Enhanced)                              │
│  ─────────────────────────────────────                      │
│  • PostToolUse: Performance tracking                        │
│  • SubagentStop: Phoenix restart detection                  │
│  • UserPromptSubmit: Context injection                      │
│                                                              │
│  Storage: logs/performance/<agent-name>.json                │
└──────────────────┬──────────────────────────────────────────┘
                   │ reads/writes
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: SDK Orchestration (New)                           │
│  ─────────────────────────────────                          │
│  • Multi-dimensional analyzer                               │
│  • Config generator                                         │
│  • A/B tester (Bayesian)                                   │
│  • Drift monitor                                            │
│  • Cost tracker                                             │
│  • Rollback manager                                         │
│                                                              │
│  Storage: logs/improvements/<agent-name>/                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ deploys
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: CLI Deployment (Enhanced)                         │
│  ─────────────────────────────────────                      │
│  • Write improved configs to .claude/agents/                │
│  • Trigger Phoenix restart (configurable)                   │
│  • Version tracking in .claude/data/agent_versions/         │
└─────────────────────────────────────────────────────────────┘
```

**Why This Architecture:**
- ✅ Repo-agnostic: Works in any Claude Code project
- ✅ Preserves existing infrastructure
- ✅ Minimal refactoring required
- ✅ Clean separation of concerns
- ✅ Scales to multiple repos

---

## Phase 1: Core Improvement Loop

### Component 1: Enhanced Performance Tracking

#### 1.1 PostToolUse Hook Enhancement

**File:** `.claude/hooks/post_tool_use.py`

Add agent-specific performance tracking to existing hook:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "anthropic",
# ]
# ///

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def extract_agent_context(input_data: dict) -> dict:
    """Extract agent execution context from tool use data."""
    # Detect if this is a subagent execution
    agent_name = input_data.get('context', {}).get('agent_name', 'main')

    # Extract tool details
    tool_name = input_data.get('tool', {}).get('name', 'unknown')
    tool_args = input_data.get('tool', {}).get('arguments', {})

    # Extract result
    result = input_data.get('result', {})
    success = not result.get('error') and result.get('success', True)
    error_message = result.get('error')

    # Extract timing if available
    execution_time_ms = input_data.get('execution_time_ms', 0)

    return {
        'timestamp': datetime.now().isoformat(),
        'agent': agent_name,
        'tool': tool_name,
        'tool_args': tool_args,
        'success': success,
        'execution_time_ms': execution_time_ms,
        'error': error_message,
        'session_id': os.getenv('CLAUDE_SESSION_ID', 'unknown')
    }

def log_performance(perf_record: dict):
    """Log performance data to agent-specific file."""
    agent_name = perf_record['agent']

    # Create performance log directory
    perf_log_dir = Path.cwd() / 'logs' / 'performance'
    perf_log_dir.mkdir(parents=True, exist_ok=True)
    perf_log_path = perf_log_dir / f'{agent_name}.json'

    # Load existing data
    if perf_log_path.exists():
        with open(perf_log_path, 'r') as f:
            try:
                perf_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                perf_data = []
    else:
        perf_data = []

    # Append new record
    perf_data.append(perf_record)

    # Write back
    with open(perf_log_path, 'w') as f:
        json.dump(perf_data, f, indent=2)

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Ensure standard log directory exists (existing behavior)
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'post_tool_use.json'

        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data (existing behavior)
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        # NEW: Extract and log performance metrics
        perf_record = extract_agent_context(input_data)
        log_performance(perf_record)

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Exit cleanly on any other error
        sys.exit(0)

if __name__ == '__main__':
    main()
```

**Performance Log Schema:** `logs/performance/<agent-name>.json`

```json
[
  {
    "timestamp": "2025-11-14T12:34:56.789Z",
    "agent": "crypto-coin-analyzer-opus",
    "tool": "WebSearch",
    "tool_args": {"query": "bitcoin price"},
    "success": true,
    "execution_time_ms": 2341,
    "error": null,
    "session_id": "abc123"
  },
  {
    "timestamp": "2025-11-14T12:45:10.123Z",
    "agent": "crypto-coin-analyzer-opus",
    "tool": "Write",
    "tool_args": {"file_path": "/tmp/analysis.md"},
    "success": false,
    "execution_time_ms": 145,
    "error": "Permission denied: /tmp/analysis.md",
    "session_id": "abc123"
  }
]
```

---

### Component 2: Multi-Dimensional Performance Analysis

**Implements principles from claude-memory-extractor:**
1. Multi-dimensional analysis (not just metrics)
2. Epistemic humility (confidence scores, assumptions)
3. Methodology over technical details
4. Gate functions for prevention
5. Default to extraction (low confidence threshold)
6. Contextual triggers for application
7. Traceability through source references

#### 2.1 Analysis Framework Tool

**File:** `sdk/tools/multi_dimensional_analyzer.py`

```python
#!/usr/bin/env python3
"""
Multi-Dimensional Performance Analyzer

Analyzes agent performance using claude-memory-extractor principles:
- Root cause analysis (Five Whys)
- Behavioral pattern detection
- Prevention strategy design (gate functions)
- Epistemic humility checks
- Contextual trigger identification
"""

from anthropic import Anthropic
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class PerformanceMetrics:
    """Basic performance metrics."""
    def __init__(self, data: List[dict]):
        self.total_executions = len(data)
        self.successes = sum(1 for d in data if d.get('success', False))
        self.success_rate = self.successes / self.total_executions if self.total_executions > 0 else 0.0

        execution_times = [d.get('execution_time_ms', 0) for d in data]
        self.avg_execution_time_ms = sum(execution_times) / len(execution_times) if execution_times else 0.0

        # Categorize errors
        errors = [d.get('error') for d in data if d.get('error')]
        self.common_errors = self._categorize_errors(errors)

    def _categorize_errors(self, errors: List[str]) -> List[tuple]:
        """Group similar errors."""
        error_counts = {}
        for error in errors:
            error_type = self._categorize_error(error)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        # Return top 3 most common
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message into common patterns."""
        if not error_message:
            return 'unknown'

        error_lower = error_message.lower()

        if 'permission' in error_lower or 'denied' in error_lower:
            return 'permission_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        elif 'not found' in error_lower or '404' in error_lower:
            return 'resource_not_found'
        elif 'rate limit' in error_lower or '429' in error_lower:
            return 'rate_limit_error'
        elif 'json' in error_lower or 'parse' in error_lower:
            return 'parsing_error'
        else:
            return 'other_error'

    def to_dict(self) -> dict:
        return {
            'total_executions': self.total_executions,
            'success_rate': self.success_rate,
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'common_errors': [{'type': e[0], 'count': e[1]} for e in self.common_errors]
        }

class MultiDimensionalAnalyzer:
    """
    Analyzes agent performance using multi-dimensional framework.

    Uses Anthropic's structured outputs (tool use) for analysis.
    """

    def __init__(self):
        self.client = Anthropic()

    def analyze_agent(self, agent_name: str) -> Optional[dict]:
        """
        Perform multi-dimensional analysis of agent performance.

        Returns None if insufficient data or no improvement needed.
        """
        # Load performance data
        perf_log_path = Path(f'logs/performance/{agent_name}.json')
        if not perf_log_path.exists():
            return {'error': f'No performance data for {agent_name}'}

        with open(perf_log_path) as f:
            perf_data = json.load(f)

        # Check minimum executions (need at least 5 for baseline)
        if len(perf_data) < 5:
            return {
                'agent_name': agent_name,
                'improvement_needed': False,
                'reason': f'Insufficient data: {len(perf_data)} executions (need 5 minimum)'
            }

        # Calculate current metrics (rolling window of last 50)
        recent_data = perf_data[-50:]
        current_metrics = PerformanceMetrics(recent_data)

        # Load baseline
        baseline_metrics = self._load_baseline(agent_name, perf_data)

        # Check trigger conditions
        if not self._should_analyze(current_metrics, baseline_metrics, len(perf_data)):
            return {
                'agent_name': agent_name,
                'improvement_needed': False,
                'reason': 'No trigger conditions met',
                'current_metrics': current_metrics.to_dict()
            }

        # Load current agent config
        agent_config = self._load_agent_config(agent_name)

        # Perform multi-dimensional analysis using structured outputs
        analysis = self._multi_dimensional_analysis(
            agent_name,
            recent_data,
            agent_config,
            current_metrics,
            baseline_metrics
        )

        # Store analysis result
        self._store_analysis(agent_name, analysis)

        return analysis

    def _multi_dimensional_analysis(
        self,
        agent_name: str,
        performance_data: List[dict],
        agent_config: str,
        current_metrics: PerformanceMetrics,
        baseline_metrics: PerformanceMetrics
    ) -> dict:
        """
        Perform multi-dimensional analysis using Anthropic's tool use.

        Analysis dimensions:
        1. Root Cause Analysis (Five Whys)
        2. Behavioral Pattern Detection
        3. Prevention Strategy (Gate Functions)
        4. Epistemic Humility Assessment
        5. Contextual Trigger Identification
        """

        # Define analysis tools for structured output
        tools = [
            {
                "name": "record_multi_dimensional_analysis",
                "description": "Record a multi-dimensional analysis of agent performance with root cause, patterns, prevention strategies, and epistemic humility checks",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "root_cause_analysis": {
                            "type": "object",
                            "description": "Five Whys analysis tracing from symptoms to root cause",
                            "properties": {
                                "surface_symptom": {"type": "string"},
                                "why_1": {"type": "string"},
                                "why_2": {"type": "string"},
                                "why_3": {"type": "string"},
                                "why_4": {"type": "string"},
                                "root_cause": {"type": "string"}
                            },
                            "required": ["surface_symptom", "why_1", "root_cause"]
                        },
                        "behavioral_patterns": {
                            "type": "array",
                            "description": "Recurring behavioral patterns detected in agent execution",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "pattern": {"type": "string"},
                                    "frequency": {"type": "number"},
                                    "driver": {"type": "string", "description": "Psychological or systemic driver of this pattern"}
                                },
                                "required": ["pattern", "frequency"]
                            }
                        },
                        "prevention_strategies": {
                            "type": "array",
                            "description": "Gate functions and preventive measures to avoid failures",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "strategy": {"type": "string"},
                                    "gate_function": {"type": "string", "description": "Concrete check to perform before action"},
                                    "prevents": {"type": "string", "description": "What failure class this prevents"}
                                },
                                "required": ["strategy", "gate_function", "prevents"]
                            }
                        },
                        "improvement_recommendations": {
                            "type": "array",
                            "description": "Specific actionable recommendations",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["PROMPT_CLARIFICATION", "TOOL_ADDITION", "TOOL_REMOVAL", "ERROR_HANDLING", "INSTRUCTION_REORDERING", "GATE_FUNCTION"]
                                    },
                                    "description": {"type": "string"},
                                    "methodology_focus": {"type": "boolean", "description": "Is this a methodology lesson (true) or technical detail (false)?"},
                                    "requires_approval": {"type": "boolean"},
                                    "expected_impact": {
                                        "type": "string",
                                        "enum": ["LOW", "MEDIUM", "HIGH"]
                                    },
                                    "contextual_triggers": {
                                        "type": "array",
                                        "description": "When to apply this recommendation",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["type", "description", "methodology_focus", "requires_approval", "expected_impact"]
                            }
                        },
                        "epistemic_humility": {
                            "type": "object",
                            "description": "Uncertainty acknowledgment and confidence assessment",
                            "properties": {
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence in analysis (1-5 scale)",
                                    "minimum": 1,
                                    "maximum": 5
                                },
                                "confidence_reasoning": {"type": "string"},
                                "assumptions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "alternative_interpretations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "evidence_needed": {"type": "string", "description": "What would prove this analysis wrong?"},
                                "tradeoffs": {"type": "string", "description": "Are there competing valid approaches?"}
                            },
                            "required": ["confidence", "confidence_reasoning", "assumptions"]
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                        }
                    },
                    "required": ["root_cause_analysis", "behavioral_patterns", "prevention_strategies", "improvement_recommendations", "epistemic_humility", "priority"]
                }
            }
        ]

        # Create analysis prompt
        prompt = f"""You are analyzing the performance of a Claude Code sub-agent using a multi-dimensional framework inspired by claude-memory-extractor.

Agent: {agent_name}

Current Configuration:
{agent_config}

Performance Data (last {len(performance_data)} executions):
{json.dumps(performance_data[-20:], indent=2)}

Current Metrics:
- Success Rate: {current_metrics.success_rate:.1%}
- Avg Execution Time: {current_metrics.avg_execution_time_ms:.0f}ms
- Common Errors: {current_metrics.common_errors}

Baseline Metrics:
- Success Rate: {baseline_metrics.success_rate:.1%}
- Avg Execution Time: {baseline_metrics.avg_execution_time_ms:.0f}ms

Perform a multi-dimensional analysis:

1. **Root Cause Analysis (Five Whys):**
   - Start with surface symptom (e.g., "30% failure rate")
   - Ask "why" repeatedly to find root cause
   - Go beyond symptoms to systemic issues

2. **Behavioral Pattern Detection:**
   - What recurring patterns exist in failures?
   - Does the agent exhibit overconfidence, risk aversion, or tool bias?
   - What psychological or systemic drivers cause these patterns?

3. **Prevention Strategies (Gate Functions):**
   - Design concrete preventive checks before actions
   - Focus on stopping failures before they happen
   - Example: "Before Read, check file exists with Glob"

4. **Improvement Recommendations:**
   - Focus on METHODOLOGY (transferable lessons) over technical details
   - Mark requires_approval=true for: tool changes, structural changes, low-confidence improvements
   - Specify contextual triggers (when to apply this)

5. **Epistemic Humility:**
   - Confidence score (1-5) with reasoning
   - What assumptions are you making?
   - What alternative interpretations exist?
   - What evidence would prove you wrong?
   - Are there genuine tradeoffs (competing valid approaches)?

Prioritize improvements by composite score:
- Correctness: 50% weight (task completion quality)
- Cost: 25% weight (token efficiency)
- Reliability: 15% weight (consistent success)
- Speed: 10% weight (execution time)

Use the record_multi_dimensional_analysis tool to provide structured output."""

        # Call Claude with tool use
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            tools=tools,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract tool use result
        for content in message.content:
            if content.type == "tool_use" and content.name == "record_multi_dimensional_analysis":
                analysis_result = content.input

                # Add metadata
                analysis_result['agent_name'] = agent_name
                analysis_result['improvement_needed'] = True
                analysis_result['current_metrics'] = current_metrics.to_dict()
                analysis_result['baseline_metrics'] = baseline_metrics.to_dict()
                analysis_result['analysis_timestamp'] = datetime.now().isoformat()

                # Add source traceability
                analysis_result['source_sessions'] = list(set(d['session_id'] for d in performance_data))
                analysis_result['data_points_analyzed'] = len(performance_data)

                return analysis_result

        # Fallback if no tool use
        return {
            'agent_name': agent_name,
            'improvement_needed': False,
            'reason': 'Analysis failed to produce structured output'
        }

    def _should_analyze(
        self,
        current: PerformanceMetrics,
        baseline: PerformanceMetrics,
        total_executions: int
    ) -> bool:
        """
        Hybrid trigger strategy:
        1. Threshold: failure rate >30%
        2. Threshold: >20% degradation from baseline
        3. Execution-based: Every 50 executions
        """
        # Threshold trigger: failure rate >30%
        if current.success_rate < 0.7:
            return True

        # Threshold trigger: significant degradation
        if baseline.success_rate - current.success_rate > 0.2:
            return True

        # Execution-based trigger: every 50 executions
        if total_executions % 50 == 0:
            return True

        return False

    def _load_baseline(self, agent_name: str, perf_data: List[dict]) -> PerformanceMetrics:
        """
        Load or establish baseline data.

        Hybrid approach:
        - Use existing baseline if available
        - Create from first 5-20 executions if missing
        """
        baseline_path = Path(f'logs/baselines/{agent_name}.json')

        if baseline_path.exists():
            with open(baseline_path) as f:
                baseline_data = json.load(f)
        else:
            # Establish new baseline from first 5-20 executions
            baseline_data = perf_data[:min(20, len(perf_data))]
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            with open(baseline_path, 'w') as f:
                json.dump(baseline_data, f, indent=2)

        return PerformanceMetrics(baseline_data)

    def _load_agent_config(self, agent_name: str) -> str:
        """Find and load agent config file."""
        paths_to_check = [
            Path(f'.claude/agents/{agent_name}.md'),
            Path(f'.claude/agents/crypto/{agent_name}.md'),
        ]

        for path in paths_to_check:
            if path.exists():
                with open(path) as f:
                    return f.read()

        return f"# Agent config not found for {agent_name}"

    def _store_analysis(self, agent_name: str, analysis: dict):
        """Store analysis result for tracking and traceability."""
        analysis_dir = Path(f'logs/improvements/{agent_name}')
        analysis_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_path = analysis_dir / f'analysis_{timestamp}.json'

        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"✅ Analysis stored: {analysis_path}", file=sys.stderr)
```

---

### Component 3: Config Generation System

#### 3.1 Improved Config Generator

**File:** `sdk/tools/config_generator.py`

```python
#!/usr/bin/env python3
"""
Agent Config Generator

Generates improved agent configurations based on multi-dimensional analysis.
Focuses on methodology improvements over technical details.
"""

from anthropic import Anthropic
from pathlib import Path
import json
from datetime import datetime
import sys

class ConfigGenerator:
    def __init__(self):
        self.client = Anthropic()

    def generate_improved_config(
        self,
        agent_name: str,
        analysis: dict
    ) -> tuple[Optional[str], List[dict]]:
        """
        Generate improved agent configuration.

        Returns:
            (improved_config, recommendations_applied) or (None, []) if all require approval
        """
        # Load current config
        current_config_path = self._find_agent_config(agent_name)
        with open(current_config_path) as f:
            current_config = f.read()

        # Filter recommendations
        all_recommendations = analysis.get('improvement_recommendations', [])

        # Separate auto-approve vs manual approval
        auto_approve = [r for r in all_recommendations if not r.get('requires_approval', False)]
        needs_approval = [r for r in all_recommendations if r.get('requires_approval', False)]

        # Notify about pending approvals
        if needs_approval:
            self._create_pending_approval(agent_name, analysis, needs_approval)

        if not auto_approve:
            return None, []  # All recommendations require manual approval

        # Generate improved config using LLM
        improved_config = self._generate_config_with_llm(
            agent_name,
            current_config,
            auto_approve,
            analysis
        )

        # Store as candidate
        candidate_timestamp = self._store_candidate(
            agent_name,
            improved_config,
            auto_approve,
            analysis
        )

        return improved_config, auto_approve

    def _generate_config_with_llm(
        self,
        agent_name: str,
        current_config: str,
        recommendations: List[dict],
        analysis: dict
    ) -> str:
        """Generate improved config using Claude."""

        # Extract key insights from multi-dimensional analysis
        root_cause = analysis.get('root_cause_analysis', {})
        prevention_strategies = analysis.get('prevention_strategies', [])

        prompt = f"""You are improving a Claude Code sub-agent configuration based on multi-dimensional analysis.

Agent: {agent_name}

Current Configuration:
{current_config}

Root Cause Analysis:
{json.dumps(root_cause, indent=2)}

Prevention Strategies (Gate Functions):
{json.dumps(prevention_strategies, indent=2)}

Improvement Recommendations to Apply:
{json.dumps(recommendations, indent=2)}

Generate an improved agent configuration that:

1. **Maintains Structure:**
   - Keep same frontmatter (name, description, tools, model, color)
   - Preserve agent's core purpose and domain

2. **Methodology Focus:**
   - Add process improvements (how to approach problems)
   - NOT context-specific technical fixes
   - Example good: "Verify file paths with Glob before Read"
   - Example bad: "Change timeout from 30s to 60s"

3. **Gate Functions:**
   - Add concrete preventive checks before actions
   - Example: "Before using WebFetch, verify URL format and accessibility"

4. **Clarity Improvements:**
   - Make instructions more specific where failures occurred
   - Add examples for ambiguous scenarios
   - Improve error handling guidance

5. **Preserve Quality:**
   - Don't remove existing good instructions
   - Keep successful patterns
   - Build on what works

Output ONLY the complete improved configuration in markdown format with frontmatter."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def _find_agent_config(self, agent_name: str) -> Path:
        """Find agent config file (handles subdirectories)."""
        paths_to_check = [
            Path(f'.claude/agents/{agent_name}.md'),
            Path(f'.claude/agents/crypto/{agent_name}.md'),
        ]

        for path in paths_to_check:
            if path.exists():
                return path

        raise FileNotFoundError(f'Agent config not found: {agent_name}')

    def _store_candidate(
        self,
        agent_name: str,
        config: str,
        recommendations: List[dict],
        analysis: dict
    ) -> str:
        """Store candidate config for A/B testing."""
        candidate_dir = Path(f'logs/improvements/{agent_name}/candidates')
        candidate_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        candidate_path = candidate_dir / f'candidate_{timestamp}.md'

        # Store config
        with open(candidate_path, 'w') as f:
            f.write(config)

        # Store metadata
        metadata = {
            'timestamp': timestamp,
            'agent_name': agent_name,
            'recommendations_applied': recommendations,
            'analysis_summary': {
                'root_cause': analysis.get('root_cause_analysis', {}).get('root_cause'),
                'confidence': analysis.get('epistemic_humility', {}).get('confidence'),
                'priority': analysis.get('priority')
            },
            'status': 'testing',
            'test_results': []
        }

        metadata_path = candidate_dir / f'candidate_{timestamp}.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"📝 Candidate config stored: {candidate_path}", file=sys.stderr)

        return timestamp

    def _create_pending_approval(
        self,
        agent_name: str,
        analysis: dict,
        recommendations: List[dict]
    ):
        """Create pending approval notification."""
        pending_dir = Path('.claude/data/pending_improvements')
        pending_dir.mkdir(parents=True, exist_ok=True)

        approval_id = f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        approval_path = pending_dir / f'{approval_id}.json'

        with open(approval_path, 'w') as f:
            json.dump({
                'id': approval_id,
                'agent_name': agent_name,
                'timestamp': datetime.now().isoformat(),
                'recommendations': recommendations,
                'analysis': analysis,
                'status': 'pending'
            }, f, indent=2)

        # Print notification
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🔔 APPROVAL REQUIRED                                        ║
╠══════════════════════════════════════════════════════════════╣
║  Agent: {agent_name:<51} ║
║  Approval ID: {approval_id:<45} ║
║                                                              ║
║  {len(recommendations)} recommendation(s) require manual review            ║
║                                                              ║
║  Use: /approve-improvement {approval_id}    ║
╚══════════════════════════════════════════════════════════════╝
""", file=sys.stderr)
```

---

### Component 4: Bayesian A/B Testing with Hybrid Cross-Session Testing

#### 4.1 Bayesian A/B Testing Framework

**File:** `sdk/tools/ab_tester.py`

```python
#!/usr/bin/env python3
"""
Bayesian A/B Testing Framework

Uses Beta distribution for performance comparison with cross-session support.
Tests run across Phoenix restarts to ensure real-world validation.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Optional, Dict, List
import math

class BayesianABTester:
    """
    Bayesian A/B testing using Beta distribution.

    Criteria:
    - Minimum 10 runs per variant
    - Improvement threshold: 10%
    - Confidence threshold: 75% for promotion
    - Supports cross-session testing (survives Phoenix restarts)
    """

    def __init__(self):
        self.min_runs = 10
        self.improvement_threshold = 0.10  # 10%
        self.confidence_threshold = 0.75   # 75%

    def start_test(
        self,
        agent_name: str,
        baseline_config_path: str,
        candidate_config_path: str,
        candidate_timestamp: str
    ) -> str:
        """
        Start new A/B test.

        Returns test_id for tracking.
        """
        test_id = f"{agent_name}_{candidate_timestamp}"

        test_dir = Path(f'logs/improvements/{agent_name}/ab_tests')
        test_dir.mkdir(parents=True, exist_ok=True)

        test_data = {
            'test_id': test_id,
            'agent_name': agent_name,
            'baseline_config': baseline_config_path,
            'candidate_config': candidate_config_path,
            'candidate_timestamp': candidate_timestamp,
            'started_at': datetime.now().isoformat(),
            'status': 'running',
            'baseline_runs': [],
            'candidate_runs': [],
            'sessions': [],  # Track which sessions contributed
            'result': None
        }

        test_path = test_dir / f'{test_id}.json'
        with open(test_path, 'w') as f:
            json.dump(test_data, f, indent=2)

        print(f"🧪 A/B test started: {test_id}")
        return test_id

    def record_run(
        self,
        test_id: str,
        variant: str,  # 'baseline' or 'candidate'
        performance_data: dict,
        session_id: str
    ):
        """
        Record a single test run for a variant.

        Supports cross-session testing.
        """
        test_path = self._get_test_path(test_id)

        with open(test_path) as f:
            test_data = json.load(f)

        # Record session if new
        if session_id not in test_data['sessions']:
            test_data['sessions'].append(session_id)

        # Add run data
        run_record = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'success': performance_data.get('success', False),
            'execution_time_ms': performance_data.get('execution_time_ms', 0),
            'error': performance_data.get('error')
        }

        if variant == 'baseline':
            test_data['baseline_runs'].append(run_record)
        elif variant == 'candidate':
            test_data['candidate_runs'].append(run_record)
        else:
            raise ValueError(f"Invalid variant: {variant}")

        # Check if we can evaluate
        baseline_count = len(test_data['baseline_runs'])
        candidate_count = len(test_data['candidate_runs'])

        if baseline_count >= self.min_runs and candidate_count >= self.min_runs:
            # Evaluate test
            result = self._evaluate_test(test_data)
            test_data['result'] = result
            test_data['status'] = 'completed'
            test_data['completed_at'] = datetime.now().isoformat()

        # Save updated test data
        with open(test_path, 'w') as f:
            json.dump(test_data, f, indent=2)

    def _evaluate_test(self, test_data: dict) -> dict:
        """
        Evaluate A/B test using Bayesian comparison.

        Uses Beta distribution for success rate comparison.
        """
        # Calculate success rates
        baseline_successes = sum(1 for r in test_data['baseline_runs'] if r['success'])
        baseline_total = len(test_data['baseline_runs'])
        baseline_rate = baseline_successes / baseline_total if baseline_total > 0 else 0

        candidate_successes = sum(1 for r in test_data['candidate_runs'] if r['success'])
        candidate_total = len(test_data['candidate_runs'])
        candidate_rate = candidate_successes / candidate_total if candidate_total > 0 else 0

        # Beta distribution parameters (using uniform prior)
        baseline_alpha = baseline_successes + 1
        baseline_beta = (baseline_total - baseline_successes) + 1

        candidate_alpha = candidate_successes + 1
        candidate_beta = (candidate_total - candidate_successes) + 1

        # Monte Carlo simulation to calculate P(candidate > baseline)
        probability_candidate_better = self._monte_carlo_comparison(
            baseline_alpha, baseline_beta,
            candidate_alpha, candidate_beta
        )

        # Calculate improvement magnitude
        improvement = (candidate_rate - baseline_rate) / baseline_rate if baseline_rate > 0 else 0

        # Decision logic
        decision = 'reject'
        reason = ''

        if probability_candidate_better >= self.confidence_threshold:
            if improvement >= self.improvement_threshold:
                decision = 'promote'
                reason = f'Candidate shows {improvement:.1%} improvement with {probability_candidate_better:.1%} confidence'
            else:
                decision = 'reject'
                reason = f'Improvement {improvement:.1%} below {self.improvement_threshold:.1%} threshold'
        else:
            decision = 'reject'
            reason = f'Confidence {probability_candidate_better:.1%} below {self.confidence_threshold:.1%} threshold'

        return {
            'decision': decision,
            'reason': reason,
            'baseline_success_rate': baseline_rate,
            'candidate_success_rate': candidate_rate,
            'improvement': improvement,
            'confidence': probability_candidate_better,
            'baseline_runs': baseline_total,
            'candidate_runs': candidate_total,
            'sessions_tested': len(test_data['sessions']),
            'cross_session': len(test_data['sessions']) > 1
        }

    def _monte_carlo_comparison(
        self,
        baseline_alpha: float,
        baseline_beta: float,
        candidate_alpha: float,
        candidate_beta: float,
        samples: int = 10000
    ) -> float:
        """
        Monte Carlo simulation to calculate P(candidate > baseline).

        Samples from Beta distributions and compares.
        """
        import random

        candidate_wins = 0

        for _ in range(samples):
            # Sample from Beta distributions
            baseline_sample = self._beta_sample(baseline_alpha, baseline_beta)
            candidate_sample = self._beta_sample(candidate_alpha, candidate_beta)

            if candidate_sample > baseline_sample:
                candidate_wins += 1

        return candidate_wins / samples

    def _beta_sample(self, alpha: float, beta: float) -> float:
        """Sample from Beta distribution using gamma samples."""
        import random

        # Beta(α, β) = Gamma(α, 1) / (Gamma(α, 1) + Gamma(β, 1))
        x = self._gamma_sample(alpha, 1.0)
        y = self._gamma_sample(beta, 1.0)

        return x / (x + y)

    def _gamma_sample(self, alpha: float, beta: float) -> float:
        """Sample from Gamma distribution using Marsaglia and Tsang method."""
        import random

        if alpha < 1:
            # Use Johnk's generator for alpha < 1
            alpha += 1
            u = random.random()
            gamma_sample = self._gamma_sample(alpha, beta)
            return gamma_sample * (u ** (1.0 / alpha))

        # Marsaglia and Tsang method for alpha >= 1
        d = alpha - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)

        while True:
            x = random.gauss(0, 1)
            v = (1.0 + c * x) ** 3

            if v <= 0:
                continue

            u = random.random()
            x_squared = x * x

            if u < 1 - 0.0331 * x_squared * x_squared:
                return d * v / beta

            if math.log(u) < 0.5 * x_squared + d * (1 - v + math.log(v)):
                return d * v / beta

    def _get_test_path(self, test_id: str) -> Path:
        """Get path to test data file."""
        # Extract agent name from test_id
        agent_name = test_id.rsplit('_', 2)[0]
        return Path(f'logs/improvements/{agent_name}/ab_tests/{test_id}.json')

    def get_test_status(self, test_id: str) -> dict:
        """Get current status of A/B test."""
        test_path = self._get_test_path(test_id)

        if not test_path.exists():
            return {'error': f'Test not found: {test_id}'}

        with open(test_path) as f:
            return json.load(f)

    def promote_candidate(self, test_id: str) -> bool:
        """
        Promote candidate config to production.

        Only succeeds if test result is 'promote'.
        """
        test_data = self.get_test_status(test_id)

        if test_data.get('result', {}).get('decision') != 'promote':
            print(f"❌ Cannot promote: test decision is not 'promote'")
            return False

        agent_name = test_data['agent_name']
        candidate_config = test_data['candidate_config']

        # Find production config path
        production_path = self._find_production_config_path(agent_name)

        # Backup current production
        self._backup_config(production_path)

        # Copy candidate to production
        with open(candidate_config) as f:
            new_config = f.read()

        with open(production_path, 'w') as f:
            f.write(new_config)

        # Update version tracking
        self._update_version_tracking(agent_name, test_data)

        print(f"✅ Promoted candidate config for {agent_name}")
        print(f"   Improvement: {test_data['result']['improvement']:.1%}")
        print(f"   Confidence: {test_data['result']['confidence']:.1%}")

        return True

    def _find_production_config_path(self, agent_name: str) -> Path:
        """Find production config path for agent."""
        paths_to_check = [
            Path(f'.claude/agents/{agent_name}.md'),
            Path(f'.claude/agents/crypto/{agent_name}.md'),
        ]

        for path in paths_to_check:
            if path.exists():
                return path

        raise FileNotFoundError(f'Production config not found: {agent_name}')

    def _backup_config(self, config_path: Path):
        """Backup current production config."""
        backup_dir = Path('.claude/data/agent_versions')
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'{config_path.stem}_{timestamp}.md'

        with open(config_path) as f:
            config_content = f.read()

        with open(backup_path, 'w') as f:
            f.write(config_content)

    def _update_version_tracking(self, agent_name: str, test_data: dict):
        """Update version tracking after promotion."""
        version_file = Path(f'.claude/data/agent_versions/{agent_name}_versions.json')

        if version_file.exists():
            with open(version_file) as f:
                versions = json.load(f)
        else:
            versions = []

        versions.append({
            'timestamp': datetime.now().isoformat(),
            'test_id': test_data['test_id'],
            'improvement': test_data['result']['improvement'],
            'confidence': test_data['result']['confidence'],
            'promoted': True
        })

        version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(version_file, 'w') as f:
            json.dump(versions, f, indent=2)
```

#### 4.2 Hybrid Testing Support

The A/B testing framework supports both **synthetic testing** and **real-world testing**:

**Synthetic Testing (Optional Phase 1.5):**
- Generate test scenarios using LLM
- Run both variants against same scenarios
- Fast iteration, controlled conditions
- Good for regression testing

**Real-World Testing (Required):**
- Run both variants in actual user sessions
- Cross-session support (tests survive restarts)
- Higher confidence in real-world performance
- Preferred for final promotion decision

**Configuration:** Tests default to real-world testing. Synthetic testing can be added in Phase 1.5 if needed.

---

### Component 5: Phoenix Pattern Integration

#### 5.1 Overview

The **Phoenix Pattern** enables automatic agent restarts when improvements are deployed, ensuring the new configuration takes effect immediately without manual intervention.

**Key Principle:** Only restart when configuration changes justify it. Minor wording changes don't require restarts.

#### 5.2 SubagentStop Hook Enhancement

**File:** `.claude/hooks/subagent_stop.py`

Add Phoenix restart detection:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import json
import sys
from pathlib import Path
from datetime import datetime

def check_restart_needed(agent_name: str) -> bool:
    """
    Check if Phoenix restart is needed for this agent.

    Reads .claude/data/restart_signals/{agent_name}.json
    """
    signal_path = Path(f'.claude/data/restart_signals/{agent_name}.json')

    if not signal_path.exists():
        return False

    with open(signal_path) as f:
        signal_data = json.load(f)

    return signal_data.get('restart_needed', False)

def get_continuation_prompt(agent_name: str) -> str:
    """Get continuation prompt from restart signal."""
    signal_path = Path(f'.claude/data/restart_signals/{agent_name}.json')

    with open(signal_path) as f:
        signal_data = json.load(f)

    return signal_data.get('continuation_prompt', 'Continue with improved configuration.')

def clear_restart_signal(agent_name: str):
    """Clear restart signal after processing."""
    signal_path = Path(f'.claude/data/restart_signals/{agent_name}.json')

    if signal_path.exists():
        signal_path.unlink()

def should_trigger_restart(change_type: str) -> bool:
    """
    Determine if change type justifies restart.

    Reads from sdk/config/phoenix_config.json
    """
    config_path = Path('sdk/config/phoenix_config.json')

    if not config_path.exists():
        # Default configuration
        default_triggers = {
            'tool_addition': True,
            'tool_removal': True,
            'major_prompt_changes': True,
            'minor_wording_changes': False
        }
        return default_triggers.get(change_type, False)

    with open(config_path) as f:
        config = json.load(f)

    triggers = config.get('restart_triggers', {})
    return triggers.get(change_type, False)

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Log to standard file
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'subagent_stop.json'

        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        log_data.append(input_data)

        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        # NEW: Check for Phoenix restart signal
        agent_name = input_data.get('agent_name', 'unknown')

        if check_restart_needed(agent_name):
            continuation_prompt = get_continuation_prompt(agent_name)
            clear_restart_signal(agent_name)

            # Print restart command to stdout (Claude Code will see this)
            restart_message = f"""
╔══════════════════════════════════════════════════════════════╗
║  🔥 PHOENIX RESTART TRIGGERED                                ║
╠══════════════════════════════════════════════════════════════╣
║  Agent: {agent_name:<51} ║
║                                                              ║
║  Improved configuration detected. Restarting session...     ║
║                                                              ║
║  Continuation: {continuation_prompt:<43} ║
╚══════════════════════════════════════════════════════════════╝

To restart: claude --continue "{continuation_prompt}"
"""
            print(restart_message)

        sys.exit(0)

    except Exception:
        sys.exit(0)

if __name__ == '__main__':
    main()
```

#### 5.3 Phoenix Configuration

**File:** `sdk/config/phoenix_config.json`

```json
{
  "restart_triggers": {
    "tool_addition": true,
    "tool_removal": true,
    "major_prompt_changes": true,
    "minor_wording_changes": false
  },
  "restart_command_template": "claude --continue \"{continuation_prompt}\"",
  "preserve_session_state": true,
  "notification_style": "banner"
}
```

**Restart Trigger Detection:**

The orchestrator analyzes config diffs to determine change type:

```python
def detect_change_type(baseline_config: str, new_config: str) -> str:
    """
    Detect type of configuration change.

    Returns: 'tool_addition', 'tool_removal', 'major_prompt_changes', 'minor_wording_changes'
    """
    # Parse frontmatter to check tools
    baseline_tools = extract_tools_from_config(baseline_config)
    new_tools = extract_tools_from_config(new_config)

    if len(new_tools) > len(baseline_tools):
        return 'tool_addition'
    elif len(new_tools) < len(baseline_tools):
        return 'tool_removal'

    # Check prompt changes (exclude frontmatter)
    baseline_prompt = extract_prompt_from_config(baseline_config)
    new_prompt = extract_prompt_from_config(new_config)

    # Use simple diff ratio
    diff_ratio = calculate_diff_ratio(baseline_prompt, new_prompt)

    if diff_ratio > 0.3:  # >30% change
        return 'major_prompt_changes'
    else:
        return 'minor_wording_changes'
```

---

### Component 6: Cost Tracking & Rollback Manager

#### 6.1 Cost Tracker

**File:** `sdk/tools/cost_tracker.py`

```python
#!/usr/bin/env python3
"""
Cost Tracker for LLM API calls

Tracks token usage and costs across all improvement operations.
Provides warnings when approaching budget limits.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Optional

class CostTracker:
    """
    Track API costs across all LLM calls.

    Pricing (as of 2025):
    - Claude Sonnet 4.5: $3/MTok input, $15/MTok output
    - GPT-4: $30/MTok input, $60/MTok output
    """

    # Pricing per 1M tokens (in USD)
    PRICING = {
        'claude-sonnet-4-5-20250929': {'input': 3.00, 'output': 15.00},
        'claude-opus-4-20250514': {'input': 15.00, 'output': 75.00},
        'gpt-4-turbo-2024-04-09': {'input': 10.00, 'output': 30.00},
        'gpt-4o-2024-05-13': {'input': 5.00, 'output': 15.00},
    }

    def __init__(self, budget_limit_usd: Optional[float] = None):
        self.budget_limit = budget_limit_usd
        self.cost_log_path = Path('logs/costs/improvement_costs.json')
        self.cost_log_path.parent.mkdir(parents=True, exist_ok=True)

    def track_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str,
        agent_name: str
    ):
        """Track a single LLM API call."""
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        record = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': cost,
            'operation': operation,  # 'analysis', 'config_generation', etc.
            'agent_name': agent_name
        }

        # Load existing log
        if self.cost_log_path.exists():
            with open(self.cost_log_path) as f:
                cost_log = json.load(f)
        else:
            cost_log = []

        cost_log.append(record)

        # Save updated log
        with open(self.cost_log_path, 'w') as f:
            json.dump(cost_log, f, indent=2)

        # Check budget
        if self.budget_limit:
            total_cost = self._calculate_total_cost(cost_log)
            if total_cost >= self.budget_limit * 0.9:
                self._warn_budget(total_cost, self.budget_limit)

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a single call."""
        if model not in self.PRICING:
            print(f"⚠️  Unknown model pricing: {model}. Using Claude Sonnet 4.5 default.")
            model = 'claude-sonnet-4-5-20250929'

        pricing = self.PRICING[model]

        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def _calculate_total_cost(self, cost_log: list) -> float:
        """Calculate total cost from log."""
        return sum(r['cost_usd'] for r in cost_log)

    def _warn_budget(self, current: float, limit: float):
        """Print budget warning."""
        percentage = (current / limit) * 100

        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  BUDGET WARNING                                          ║
╠══════════════════════════════════════════════════════════════╣
║  Current spend: ${current:.2f}                                        ║
║  Budget limit:  ${limit:.2f}                                         ║
║  Usage:         {percentage:.1f}%                                      ║
║                                                              ║
║  Approaching budget limit!                                   ║
╚══════════════════════════════════════════════════════════════╝
""")

    def get_summary(self) -> Dict:
        """Get cost summary."""
        if not self.cost_log_path.exists():
            return {'total_cost': 0, 'calls': 0}

        with open(self.cost_log_path) as f:
            cost_log = json.load(f)

        total_cost = self._calculate_total_cost(cost_log)

        # Group by operation
        by_operation = {}
        for record in cost_log:
            op = record['operation']
            if op not in by_operation:
                by_operation[op] = {'cost': 0, 'calls': 0}
            by_operation[op]['cost'] += record['cost_usd']
            by_operation[op]['calls'] += 1

        return {
            'total_cost': total_cost,
            'total_calls': len(cost_log),
            'by_operation': by_operation,
            'budget_limit': self.budget_limit,
            'budget_remaining': self.budget_limit - total_cost if self.budget_limit else None
        }
```

#### 6.2 Rollback Manager

**File:** `sdk/tools/rollback_manager.py`

```python
#!/usr/bin/env python3
"""
Rollback Manager

Automatically rolls back agent improvements when degradation is detected.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Optional

class RollbackManager:
    """
    Manage automatic rollbacks of agent configurations.

    Default rollback triggers:
    - Performance degradation >10%
    - Critical failures (3+ consecutive)
    """

    def __init__(
        self,
        degradation_threshold: float = 0.10,  # 10%
        critical_failure_count: int = 3
    ):
        self.degradation_threshold = degradation_threshold
        self.critical_failure_count = critical_failure_count

    def check_rollback_needed(
        self,
        agent_name: str,
        recent_performance: list
    ) -> Optional[dict]:
        """
        Check if rollback is needed based on recent performance.

        Returns rollback decision or None if no rollback needed.
        """
        if len(recent_performance) < 5:
            return None  # Need minimum data

        # Check for critical failures (consecutive)
        consecutive_failures = 0
        for perf in reversed(recent_performance):
            if not perf.get('success', False):
                consecutive_failures += 1
            else:
                break

        if consecutive_failures >= self.critical_failure_count:
            return {
                'trigger': 'critical_failures',
                'reason': f'{consecutive_failures} consecutive failures detected',
                'action': 'rollback'
            }

        # Check for performance degradation
        baseline_metrics = self._load_baseline_metrics(agent_name)
        if not baseline_metrics:
            return None

        current_success_rate = sum(1 for p in recent_performance if p.get('success', False)) / len(recent_performance)
        baseline_success_rate = baseline_metrics.get('success_rate', 1.0)

        degradation = baseline_success_rate - current_success_rate

        if degradation > self.degradation_threshold:
            return {
                'trigger': 'performance_degradation',
                'reason': f'{degradation:.1%} degradation from baseline',
                'baseline_rate': baseline_success_rate,
                'current_rate': current_success_rate,
                'action': 'rollback'
            }

        return None

    def execute_rollback(self, agent_name: str) -> bool:
        """
        Execute rollback to previous version.

        Uses version tracking to find last good version.
        """
        # Find previous version
        version_file = Path(f'.claude/data/agent_versions/{agent_name}_versions.json')

        if not version_file.exists():
            print(f"❌ No version history found for {agent_name}")
            return False

        with open(version_file) as f:
            versions = json.load(f)

        if len(versions) < 2:
            print(f"❌ No previous version to rollback to for {agent_name}")
            return False

        # Get last promoted version (current) and previous
        current_version = versions[-1]
        previous_version = versions[-2]

        # Find backup file for previous version
        backup_files = sorted(Path('.claude/data/agent_versions').glob(f'{agent_name}_*.md'))

        if len(backup_files) < 2:
            print(f"❌ Backup file not found for {agent_name}")
            return False

        # Use second-to-last backup (last is current version)
        rollback_file = backup_files[-2]

        # Find production config
        production_path = self._find_production_config(agent_name)

        # Backup current (failed) version
        failed_backup = Path(f'.claude/data/agent_versions/{agent_name}_failed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
        with open(production_path) as f:
            failed_config = f.read()
        with open(failed_backup, 'w') as f:
            f.write(failed_config)

        # Restore previous version
        with open(rollback_file) as f:
            previous_config = f.read()
        with open(production_path, 'w') as f:
            f.write(previous_config)

        # Log rollback
        self._log_rollback(agent_name, current_version, previous_version)

        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ↩️  ROLLBACK EXECUTED                                       ║
╠══════════════════════════════════════════════════════════════╣
║  Agent: {agent_name:<51} ║
║                                                              ║
║  Rolled back to previous version                            ║
║  Failed version backed up to:                               ║
║  {str(failed_backup):<60} ║
╚══════════════════════════════════════════════════════════════╝
""")

        return True

    def _find_production_config(self, agent_name: str) -> Path:
        """Find production config path."""
        paths = [
            Path(f'.claude/agents/{agent_name}.md'),
            Path(f'.claude/agents/crypto/{agent_name}.md'),
        ]

        for path in paths:
            if path.exists():
                return path

        raise FileNotFoundError(f'Production config not found: {agent_name}')

    def _load_baseline_metrics(self, agent_name: str) -> Optional[dict]:
        """Load baseline metrics for comparison."""
        baseline_path = Path(f'logs/baselines/{agent_name}.json')

        if not baseline_path.exists():
            return None

        with open(baseline_path) as f:
            baseline_data = json.load(f)

        # Calculate success rate from baseline data
        successes = sum(1 for d in baseline_data if d.get('success', False))
        total = len(baseline_data)

        return {
            'success_rate': successes / total if total > 0 else 1.0,
            'total_runs': total
        }

    def _log_rollback(self, agent_name: str, failed_version: dict, restored_version: dict):
        """Log rollback event."""
        rollback_log = Path('logs/rollbacks/rollback_log.json')
        rollback_log.parent.mkdir(parents=True, exist_ok=True)

        if rollback_log.exists():
            with open(rollback_log) as f:
                log_data = json.load(f)
        else:
            log_data = []

        log_data.append({
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'failed_version': failed_version,
            'restored_version': restored_version
        })

        with open(rollback_log, 'w') as f:
            json.dump(log_data, f, indent=2)
```

---

### Component 7: Meta-Evolution Orchestrator

#### 7.1 Main Orchestrator

**File:** `sdk/meta_evolution_orchestrator.py`

```python
#!/usr/bin/env python3
"""
Meta-Evolution Orchestrator

Main orchestration script that coordinates the entire improvement loop:
1. Monitor agents
2. Analyze performance
3. Generate improved configs
4. Manage A/B testing
5. Promote/reject based on results
6. Trigger Phoenix restarts
7. Track costs
"""

from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Optional
import sys

from tools.multi_dimensional_analyzer import MultiDimensionalAnalyzer
from tools.config_generator import ConfigGenerator
from tools.ab_tester import BayesianABTester
from tools.cost_tracker import CostTracker
from tools.rollback_manager import RollbackManager

class MetaEvolutionOrchestrator:
    """
    Orchestrates the complete agent improvement lifecycle.

    Phase 1: Monitors all agents except meta-agent itself.
    """

    def __init__(self, budget_limit_usd: Optional[float] = None):
        self.analyzer = MultiDimensionalAnalyzer()
        self.config_generator = ConfigGenerator()
        self.ab_tester = BayesianABTester()
        self.cost_tracker = CostTracker(budget_limit_usd)
        self.rollback_manager = RollbackManager()

        self.excluded_agents = [
            'meta-agent',  # Phase 1: Don't improve the improver
            'meta-evolution-orchestrator'
        ]

    def run(self):
        """
        Main orchestration loop.

        Steps:
        1. Get all agents to monitor
        2. Analyze each agent
        3. Generate improved configs (where needed)
        4. Start/continue A/B tests
        5. Check test results and promote/reject
        6. Trigger Phoenix restarts
        7. Check rollback conditions
        8. Report summary
        """
        print("🔄 Meta-Evolution Orchestrator Starting...")
        print(f"   Excluded agents: {', '.join(self.excluded_agents)}")
        print()

        # Step 1: Get agents to monitor
        agents = self._get_agents_to_monitor()
        print(f"📊 Monitoring {len(agents)} agents")
        print()

        results = {
            'analyzed': [],
            'improved': [],
            'tests_started': [],
            'tests_completed': [],
            'promoted': [],
            'rejected': [],
            'rolled_back': [],
            'errors': []
        }

        # Step 2-3: Analyze and generate improvements
        for agent_name in agents:
            try:
                print(f"Analyzing {agent_name}...")
                analysis = self.analyzer.analyze_agent(agent_name)

                if not analysis:
                    continue

                results['analyzed'].append(agent_name)

                # Track cost
                # Note: In real implementation, MultiDimensionalAnalyzer would return token usage
                # For now, we'll track when we know API calls are made

                if not analysis.get('improvement_needed', False):
                    print(f"  ✓ No improvement needed")
                    continue

                # Generate improved config
                print(f"  Generating improved config...")
                improved_config, recommendations = self.config_generator.generate_improved_config(
                    agent_name,
                    analysis
                )

                if improved_config:
                    results['improved'].append(agent_name)

                    # Step 4: Start A/B test
                    print(f"  Starting A/B test...")
                    test_id = self._start_or_continue_test(
                        agent_name,
                        improved_config,
                        analysis
                    )

                    if test_id:
                        results['tests_started'].append(test_id)

                print()

            except Exception as e:
                results['errors'].append({'agent': agent_name, 'error': str(e)})
                print(f"  ❌ Error: {e}")
                print()

        # Step 5: Check completed tests
        print("Checking A/B test results...")
        completed_tests = self._check_completed_tests()

        for test_id, test_data in completed_tests:
            agent_name = test_data['agent_name']
            result = test_data.get('result', {})
            decision = result.get('decision')

            results['tests_completed'].append(test_id)

            if decision == 'promote':
                print(f"  ✅ Promoting {agent_name}")
                success = self.ab_tester.promote_candidate(test_id)

                if success:
                    results['promoted'].append(agent_name)

                    # Trigger Phoenix restart if needed
                    self._trigger_phoenix_restart_if_needed(agent_name, test_data)

            elif decision == 'reject':
                print(f"  ❌ Rejecting {agent_name}: {result.get('reason')}")
                results['rejected'].append(agent_name)

        print()

        # Step 7: Check rollback conditions
        print("Checking rollback conditions...")
        for agent_name in agents:
            rollback_decision = self._check_rollback(agent_name)

            if rollback_decision:
                print(f"  ↩️  Rollback needed for {agent_name}: {rollback_decision['reason']}")
                success = self.rollback_manager.execute_rollback(agent_name)

                if success:
                    results['rolled_back'].append(agent_name)

        print()

        # Step 8: Print summary
        self._print_summary(results)

        # Print cost summary
        cost_summary = self.cost_tracker.get_summary()
        print(f"\n💰 Total cost: ${cost_summary['total_cost']:.4f}")

        if cost_summary.get('budget_remaining'):
            print(f"   Remaining budget: ${cost_summary['budget_remaining']:.2f}")

    def _get_agents_to_monitor(self) -> List[str]:
        """Get list of agent names to monitor (excluding meta-agent)."""
        agent_files = []

        # Check .claude/agents/
        agents_dir = Path('.claude/agents')
        if agents_dir.exists():
            agent_files.extend(agents_dir.glob('*.md'))

            # Check subdirectories (like crypto/)
            for subdir in agents_dir.iterdir():
                if subdir.is_dir():
                    agent_files.extend(subdir.glob('*.md'))

        # Extract agent names (stem without .md)
        agent_names = [f.stem for f in agent_files]

        # Filter out excluded agents
        return [name for name in agent_names if name not in self.excluded_agents]

    def _start_or_continue_test(
        self,
        agent_name: str,
        improved_config: str,
        analysis: dict
    ) -> Optional[str]:
        """Start new A/B test or continue existing one."""
        # Find baseline config
        baseline_path = self._find_agent_config(agent_name)

        # Store candidate config temporarily
        candidate_timestamp = analysis.get('analysis_timestamp', datetime.now().isoformat()).replace(':', '').replace('.', '')
        candidate_dir = Path(f'logs/improvements/{agent_name}/candidates')
        candidate_dir.mkdir(parents=True, exist_ok=True)
        candidate_path = candidate_dir / f'candidate_{candidate_timestamp}.md'

        with open(candidate_path, 'w') as f:
            f.write(improved_config)

        # Start test
        test_id = self.ab_tester.start_test(
            agent_name,
            str(baseline_path),
            str(candidate_path),
            candidate_timestamp
        )

        return test_id

    def _check_completed_tests(self) -> List[tuple]:
        """Check for completed A/B tests."""
        completed = []

        # Find all test files
        improvements_dir = Path('logs/improvements')
        if not improvements_dir.exists():
            return completed

        for agent_dir in improvements_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            ab_tests_dir = agent_dir / 'ab_tests'
            if not ab_tests_dir.exists():
                continue

            for test_file in ab_tests_dir.glob('*.json'):
                with open(test_file) as f:
                    test_data = json.load(f)

                if test_data.get('status') == 'completed':
                    completed.append((test_data['test_id'], test_data))

        return completed

    def _trigger_phoenix_restart_if_needed(self, agent_name: str, test_data: dict):
        """Trigger Phoenix restart if configuration change justifies it."""
        # Load Phoenix config
        phoenix_config_path = Path('sdk/config/phoenix_config.json')

        if not phoenix_config_path.exists():
            return  # No Phoenix config, skip restart

        with open(phoenix_config_path) as f:
            phoenix_config = json.load(f)

        # Detect change type
        baseline_config_path = test_data['baseline_config']
        candidate_config_path = test_data['candidate_config']

        with open(baseline_config_path) as f:
            baseline_config = f.read()
        with open(candidate_config_path) as f:
            candidate_config = f.read()

        change_type = self._detect_change_type(baseline_config, candidate_config)

        # Check if this change type triggers restart
        restart_triggers = phoenix_config.get('restart_triggers', {})

        if not restart_triggers.get(change_type, False):
            print(f"  ℹ️  Change type '{change_type}' does not trigger restart")
            return

        # Create restart signal
        signal_dir = Path('.claude/data/restart_signals')
        signal_dir.mkdir(parents=True, exist_ok=True)

        signal_path = signal_dir / f'{agent_name}.json'

        with open(signal_path, 'w') as f:
            json.dump({
                'restart_needed': True,
                'agent_name': agent_name,
                'change_type': change_type,
                'continuation_prompt': f'Continue with improved {agent_name} configuration',
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

        print(f"  🔥 Phoenix restart signal created for {agent_name}")

    def _detect_change_type(self, baseline: str, candidate: str) -> str:
        """
        Detect type of configuration change.

        Returns: 'tool_addition', 'tool_removal', 'major_prompt_changes', 'minor_wording_changes'
        """
        # Simple implementation - check for tool changes in frontmatter
        baseline_tools = self._extract_tools(baseline)
        candidate_tools = self._extract_tools(candidate)

        if len(candidate_tools) > len(baseline_tools):
            return 'tool_addition'
        elif len(candidate_tools) < len(baseline_tools):
            return 'tool_removal'

        # Check magnitude of prompt changes (excluding frontmatter)
        baseline_prompt = self._extract_prompt(baseline)
        candidate_prompt = self._extract_prompt(candidate)

        # Simple diff ratio
        diff_ratio = self._calculate_diff_ratio(baseline_prompt, candidate_prompt)

        if diff_ratio > 0.3:  # >30% change
            return 'major_prompt_changes'
        else:
            return 'minor_wording_changes'

    def _extract_tools(self, config: str) -> List[str]:
        """Extract tools from frontmatter."""
        tools = []
        in_frontmatter = False

        for line in config.split('\n'):
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue

            if in_frontmatter and line.strip().startswith('- '):
                # Assuming tools are listed with "- toolname"
                tool = line.strip()[2:].strip()
                if tool:
                    tools.append(tool)

        return tools

    def _extract_prompt(self, config: str) -> str:
        """Extract prompt content (everything after frontmatter)."""
        parts = config.split('---')
        if len(parts) >= 3:
            return '---'.join(parts[2:])
        return config

    def _calculate_diff_ratio(self, text1: str, text2: str) -> float:
        """Calculate simple diff ratio between two texts."""
        # Very simple implementation - count changed words
        words1 = set(text1.split())
        words2 = set(text2.split())

        total_words = len(words1.union(words2))
        if total_words == 0:
            return 0.0

        different_words = len(words1.symmetric_difference(words2))
        return different_words / total_words

    def _check_rollback(self, agent_name: str) -> Optional[dict]:
        """Check if agent needs rollback."""
        # Load recent performance
        perf_log_path = Path(f'logs/performance/{agent_name}.json')

        if not perf_log_path.exists():
            return None

        with open(perf_log_path) as f:
            perf_data = json.load(f)

        # Check last 20 runs
        recent_perf = perf_data[-20:] if len(perf_data) >= 20 else perf_data

        return self.rollback_manager.check_rollback_needed(agent_name, recent_perf)

    def _find_agent_config(self, agent_name: str) -> Path:
        """Find agent config file."""
        paths = [
            Path(f'.claude/agents/{agent_name}.md'),
            Path(f'.claude/agents/crypto/{agent_name}.md'),
        ]

        for path in paths:
            if path.exists():
                return path

        raise FileNotFoundError(f'Agent config not found: {agent_name}')

    def _print_summary(self, results: dict):
        """Print orchestration summary."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║  📊 ORCHESTRATION SUMMARY                                    ║
╠══════════════════════════════════════════════════════════════╣""")

        print(f"║  Agents analyzed:    {len(results['analyzed']):<39} ║")
        print(f"║  Improvements generated: {len(results['improved']):<35} ║")
        print(f"║  Tests started:      {len(results['tests_started']):<39} ║")
        print(f"║  Tests completed:    {len(results['tests_completed']):<39} ║")
        print(f"║  Configs promoted:   {len(results['promoted']):<39} ║")
        print(f"║  Configs rejected:   {len(results['rejected']):<39} ║")
        print(f"║  Rollbacks executed: {len(results['rolled_back']):<39} ║")
        print(f"║  Errors:             {len(results['errors']):<39} ║")

        print("╚══════════════════════════════════════════════════════════════╝")

        # Print details if any
        if results['promoted']:
            print(f"\n✅ Promoted: {', '.join(results['promoted'])}")

        if results['rejected']:
            print(f"\n❌ Rejected: {', '.join(results['rejected'])}")

        if results['rolled_back']:
            print(f"\n↩️  Rolled back: {', '.join(results['rolled_back'])}")

        if results['errors']:
            print(f"\n⚠️  Errors:")
            for error in results['errors']:
                print(f"   - {error['agent']}: {error['error']}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Meta-Evolution Orchestrator')
    parser.add_argument('--budget', type=float, help='Budget limit in USD', default=None)

    args = parser.parse_args()

    orchestrator = MetaEvolutionOrchestrator(budget_limit_usd=args.budget)
    orchestrator.run()


if __name__ == '__main__':
    main()
```

#### 7.2 Slash Command Integration

**File:** `.claude/commands/improve-agents.md`

```markdown
---
description: Trigger meta-evolution orchestrator to analyze and improve agents
tags: [improvement, meta]
---

Execute the meta-evolution orchestrator to analyze agent performance, generate improvements, and manage A/B testing.

Run the orchestrator:

```bash
cd /home/user/claude-code-hooks-mastery
python3 sdk/meta_evolution_orchestrator.py
```

The orchestrator will:
1. Analyze all monitored agents
2. Generate improved configurations where needed
3. Start/continue A/B tests
4. Promote successful improvements
5. Trigger Phoenix restarts if configured
6. Report summary with costs

Note: This is a Phase 1 manual trigger. Phase 2 will enable automatic scheduling.
```

---

## Phase 2: Self-Improvement Architecture (Design Only - Not Implemented)

### Overview

Phase 2 extends the system to **monitor the meta-evolution system itself**, enabling the improver to improve itself.

### Key Principles

1. **Separate Tracking Domain:**
   - Track meta-agent's **recommendation quality**, not just task completion
   - Metrics: accuracy of improvement predictions, false positive rate, analysis depth

2. **Delayed Validation:**
   - Validate meta-agent decisions after A/B test results
   - Compare predicted improvement vs. actual improvement
   - Track recommendation acceptance rate

3. **Recursive Depth Limit:**
   - Prevent infinite loops with max recursion depth = 2
   - Meta-agent improves itself once, then stops

4. **Clean Separation:**
   - Phase 1 code remains unchanged
   - Phase 2 adds new monitoring layer on top
   - No refactoring required

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Meta-Meta Layer (Phase 2)                                  │
│  ─────────────────────────────────                          │
│  • Monitors meta-evolution-orchestrator                     │
│  • Tracks recommendation quality                            │
│  • Validates predictions vs. outcomes                       │
│  • Improves analysis methodology                            │
│                                                              │
│  Storage: logs/meta_evolution/self_improvement/             │
└──────────────────┬──────────────────────────────────────────┘
                   │ observes
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  Meta Layer (Phase 1)                                       │
│  ─────────────────────────────                              │
│  • Meta-evolution-orchestrator                              │
│  • Multi-dimensional analyzer                               │
│  • Config generator                                         │
│  • A/B tester                                               │
│                                                              │
│  Storage: logs/improvements/                                │
└──────────────────┬──────────────────────────────────────────┘
                   │ improves
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Layer (Base)                                         │
│  ─────────────────────────────────                          │
│  • All sub-agents                                           │
│  • Performance tracking                                     │
│                                                              │
│  Storage: logs/performance/                                 │
└─────────────────────────────────────────────────────────────┘
```

### Validation Metrics for Meta-Agent

1. **Prediction Accuracy:**
   - Predicted improvement % vs. actual improvement %
   - Mean absolute error (MAE)

2. **Recommendation Quality:**
   - % of recommendations that improve performance when applied
   - False positive rate (recommended improvement that degraded performance)

3. **Analysis Depth:**
   - Root cause accuracy (validated by human review)
   - Epistemic humility calibration (are confidence scores accurate?)

4. **Efficiency:**
   - Cost per successful improvement
   - Time to generate analysis

### Implementation Notes

**Phase 2 Components (Future):**
- `sdk/meta_meta/recommendation_validator.py` - Validates meta-agent predictions
- `sdk/meta_meta/self_improvement_analyzer.py` - Analyzes meta-agent itself
- `sdk/meta_meta/methodology_improver.py` - Improves analysis methodology

**Critical Design Decision:**
- Phase 2 uses the **same tools** (MultiDimensionalAnalyzer, ConfigGenerator) but applies them to the meta-agent
- This ensures consistency and avoids code duplication

---

## Implementation Roadmap

### Week 1-2: Enhanced Hooks + Performance Tracking

**Goals:**
- ✅ Enhanced PostToolUse hook with agent-specific tracking
- ✅ Performance log schema defined
- ✅ Baseline establishment logic

**Deliverables:**
- `.claude/hooks/post_tool_use.py` (enhanced)
- `logs/performance/<agent-name>.json` (schema)
- `logs/baselines/<agent-name>.json` (schema)

**Testing:**
- Run several sub-agent sessions
- Verify performance logs are created
- Verify baselines are established

---

### Week 3-4: Multi-Dimensional Analyzer + Config Generator

**Goals:**
- ✅ Multi-dimensional analysis framework
- ✅ Structured output using tool use
- ✅ Config generation with LLM
- ✅ Approval workflow for risky changes

**Deliverables:**
- `sdk/tools/multi_dimensional_analyzer.py`
- `sdk/tools/config_generator.py`
- `.claude/data/pending_improvements/` (directory)

**Testing:**
- Manually run analyzer on test agent
- Verify structured analysis output
- Generate improved config and review quality
- Test approval workflow

---

### Week 4-5: A/B Testing + Phoenix Pattern

**Goals:**
- ✅ Bayesian A/B testing framework
- ✅ Cross-session testing support
- ✅ Phoenix restart detection
- ✅ Configuration-based restart triggers

**Deliverables:**
- `sdk/tools/ab_tester.py`
- `.claude/hooks/subagent_stop.py` (enhanced)
- `sdk/config/phoenix_config.json`
- `logs/improvements/<agent-name>/ab_tests/` (directory)

**Testing:**
- Start A/B test with synthetic agent
- Run test across multiple sessions (simulate Phoenix restart)
- Verify promotion/rejection logic
- Test Phoenix restart signal

---

### Week 6: Cost Tracking + Rollback Manager

**Goals:**
- ✅ Cost tracking for all LLM calls
- ✅ Budget warnings
- ✅ Automatic rollback on degradation
- ✅ Version tracking

**Deliverables:**
- `sdk/tools/cost_tracker.py`
- `sdk/tools/rollback_manager.py`
- `logs/costs/improvement_costs.json`
- `.claude/data/agent_versions/` (directory)

**Testing:**
- Track costs during analysis + config generation
- Simulate degradation and verify rollback
- Test version tracking

---

### Week 7: Orchestrator + Slash Command

**Goals:**
- ✅ Complete orchestration loop
- ✅ Integration of all components
- ✅ Slash command for manual trigger
- ✅ Summary reporting

**Deliverables:**
- `sdk/meta_evolution_orchestrator.py`
- `.claude/commands/improve-agents.md`
- `.claude/commands/approve-improvement.md`
- `.claude/commands/rollback-agent.md`
- `.claude/commands/improvement-status.md`

**Testing:**
- Run full orchestration with test agents
- Verify all components integrate correctly
- Test slash commands
- Review summary reports

---

### Week 8: Full System Testing

**Goals:**
- ✅ End-to-end testing with real agents
- ✅ Multi-session testing (cross-Phoenix)
- ✅ Performance validation
- ✅ Documentation updates

**Deliverables:**
- Test results report
- Updated KINTSUGI_AGENT_PROMPT.md
- Updated CLAUDE.md
- Demo video/walkthrough

**Testing:**
- Run orchestrator on 3+ real agents
- Verify improvements over multiple cycles
- Test edge cases (no data, insufficient runs, etc.)
- Validate cost tracking accuracy

---

## Configuration Reference

### Environment Variables

```bash
# API Keys (optional for local LLMs)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."

# Budget limit (optional)
export IMPROVEMENT_BUDGET_USD="10.00"

# Orchestrator settings
export META_EVOLUTION_LOG_LEVEL="INFO"
```

### Configuration Files

#### 1. Phoenix Configuration

**File:** `sdk/config/phoenix_config.json`

```json
{
  "restart_triggers": {
    "tool_addition": true,
    "tool_removal": true,
    "major_prompt_changes": true,
    "minor_wording_changes": false
  },
  "restart_command_template": "claude --continue \"{continuation_prompt}\"",
  "preserve_session_state": true,
  "notification_style": "banner"
}
```

**Options:**
- `restart_triggers`: Which change types trigger restarts
- `restart_command_template`: Command template for restart
- `preserve_session_state`: Whether to preserve session state across restarts
- `notification_style`: "banner" or "simple"

#### 2. Orchestrator Configuration

**File:** `sdk/config/orchestrator_config.json`

```json
{
  "excluded_agents": [
    "meta-agent",
    "meta-evolution-orchestrator"
  ],
  "analysis_triggers": {
    "failure_rate_threshold": 0.30,
    "degradation_threshold": 0.20,
    "execution_interval": 50
  },
  "ab_testing": {
    "min_runs": 10,
    "improvement_threshold": 0.10,
    "confidence_threshold": 0.75
  },
  "rollback": {
    "degradation_threshold": 0.10,
    "critical_failure_count": 3
  },
  "budget": {
    "limit_usd": null,
    "warning_threshold": 0.90
  }
}
```

#### 3. Analysis Priorities

**File:** `sdk/config/analysis_priorities.json`

```json
{
  "composite_weights": {
    "correctness": 0.50,
    "cost": 0.25,
    "reliability": 0.15,
    "speed": 0.10
  },
  "confidence_thresholds": {
    "auto_approve": 4,
    "requires_approval": 3
  }
}
```

### Trigger Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Failure rate | >30% | Trigger analysis |
| Degradation from baseline | >20% | Trigger analysis |
| Execution count | Every 50 runs | Trigger analysis |
| Consecutive failures | 3+ | Trigger rollback |
| Performance degradation | >10% | Trigger rollback |
| Budget usage | >90% | Warning |
| Improvement confidence | <75% | Reject promotion |
| Improvement magnitude | <10% | Reject promotion |

### Cost Limits

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|-------|---------------------|----------------------|
| Claude Sonnet 4.5 | $3.00 | $15.00 |
| Claude Opus 4 | $15.00 | $75.00 |
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-4o | $5.00 | $15.00 |

**Recommended budgets:**
- Development/testing: $5-10
- Production (per week): $20-50
- Enterprise: Custom

### Rollback Rules

**Automatic Rollback Triggers:**
1. **Critical failures:** 3+ consecutive failures
2. **Performance degradation:** >10% drop from baseline
3. **User-initiated:** Manual rollback command

**Rollback Process:**
1. Backup current (failed) config
2. Restore previous version from version history
3. Log rollback event
4. Notify user

**Rollback Safety:**
- Always backup before rollback
- Maintain full version history
- Log all rollback events
- Require at least 2 versions in history

---

## Appendix: Slash Commands

### 1. `/improve-agents` - Manual Orchestrator Trigger

**Usage:**
```
/improve-agents
```

**Description:**
Manually trigger the meta-evolution orchestrator to analyze and improve all monitored agents.

**Output:**
- Analysis summary for each agent
- Improvement recommendations
- A/B test status
- Promotion/rejection decisions
- Cost summary

**When to use:**
- Weekly maintenance runs
- After deploying new agents
- Before major releases

---

### 2. `/approve-improvement <id>` - Approve Pending Improvement

**Usage:**
```
/approve-improvement crypto-coin-analyzer-opus_20251114_123456
```

**Description:**
Approve a pending improvement that requires manual review. The improvement will be applied and A/B tested.

**Arguments:**
- `<id>`: Approval ID from pending improvement notification

**Output:**
- Confirmation of approval
- A/B test started notification

**When to use:**
- When you receive approval request notification
- After reviewing pending improvement recommendations

---

### 3. `/rollback-agent <agent-name>` - Manual Rollback

**Usage:**
```
/rollback-agent crypto-coin-analyzer-opus
```

**Description:**
Manually rollback an agent to its previous version.

**Arguments:**
- `<agent-name>`: Name of agent to rollback

**Output:**
- Rollback confirmation
- Version information
- Backup location

**When to use:**
- When you notice unexpected behavior
- After failed improvement
- Testing purposes

**Safety:**
- Requires at least 2 versions in history
- Current config backed up before rollback
- Rollback event logged

---

### 4. `/improvement-status` - View Improvement Dashboard

**Usage:**
```
/improvement-status
```

**Description:**
Display comprehensive dashboard of improvement system status.

**Output:**
- Active A/B tests with progress
- Pending approvals
- Recent promotions/rejections
- Recent rollbacks
- Cost summary
- Next scheduled run (Phase 2)

**Dashboard Sections:**

1. **Active A/B Tests:**
   - Test ID
   - Agent name
   - Progress (X/10 baseline, Y/10 candidate)
   - Status

2. **Pending Approvals:**
   - Approval ID
   - Agent name
   - Recommendation count
   - Timestamp

3. **Recent Activity (Last 7 days):**
   - Promotions
   - Rejections
   - Rollbacks

4. **Cost Tracking:**
   - Total spend
   - Budget remaining
   - Cost by operation

**When to use:**
- Daily status checks
- Before/after orchestrator runs
- Monitoring system health

---

**File:** `.claude/commands/approve-improvement.md`

```markdown
---
description: Approve pending improvement recommendation
tags: [improvement, approval]
---

Approve a pending improvement that requires manual review.

Usage: /approve-improvement <approval-id>

Example: /approve-improvement crypto-coin-analyzer-opus_20251114_123456

The system will:
1. Load the pending improvement
2. Generate the improved config
3. Start A/B testing
4. Report progress

To view pending approvals, use: /improvement-status
```

---

**File:** `.claude/commands/rollback-agent.md`

```markdown
---
description: Manually rollback agent to previous version
tags: [improvement, rollback]
---

Rollback an agent to its previous version.

Usage: /rollback-agent <agent-name>

Example: /rollback-agent crypto-coin-analyzer-opus

The system will:
1. Backup current config
2. Restore previous version
3. Log rollback event
4. Report status

Safety: Requires at least 2 versions in history.
```

---

**File:** `.claude/commands/improvement-status.md`

```markdown
---
description: View comprehensive improvement system dashboard
tags: [improvement, monitoring]
---

Display the improvement system status dashboard.

Run the status checker:

```bash
cd /home/user/claude-code-hooks-mastery
python3 sdk/tools/improvement_dashboard.py
```

The dashboard shows:
- Active A/B tests with progress
- Pending approvals
- Recent promotions/rejections
- Recent rollbacks
- Cost tracking summary

This helps you monitor the meta-evolution system health and track improvement progress.
```

---

## Summary

This comprehensive Kintsugi-Agent system provides:

✅ **Complete Component Coverage:**
1. Enhanced performance tracking (PostToolUse hook)
2. Multi-dimensional analysis (Five Whys, behavioral patterns, gate functions)
3. Config generation (methodology-focused improvements)
4. Bayesian A/B testing (cross-session support)
5. Phoenix Pattern (configurable restarts)
6. Cost tracking and rollback management
7. Meta-evolution orchestrator (full integration)

✅ **Phase 2 Architecture:**
- Self-improvement design for meta-agent
- Clean separation from Phase 1
- No refactoring required

✅ **Implementation Roadmap:**
- 8-week detailed plan
- Clear deliverables and testing criteria
- Progressive integration

✅ **Configuration Reference:**
- All configuration files documented
- Environment variables
- Trigger thresholds
- Cost limits
- Rollback rules

✅ **Slash Commands:**
- `/improve-agents` - Manual trigger
- `/approve-improvement <id>` - Approve pending
- `/rollback-agent <name>` - Manual rollback
- `/improvement-status` - Dashboard

The system is designed to be **repo-agnostic**, **preserves existing infrastructure**, and enables **autonomous agent improvement** with proper safety mechanisms (rollback, cost tracking, approval workflows).

Like Kintsugi pottery, this system finds fractures in agent performance and repairs them with wisdom—making agents stronger, more reliable, and more beautiful than before.
