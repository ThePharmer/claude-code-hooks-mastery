# Scripts Directory

This directory contains utility scripts for the Claude Code Hooks Mastery repository.

## setup.sh

Comprehensive setup and validation script that ensures your environment is properly configured.

### Usage

```bash
# Run from project root
./scripts/setup.sh

# Or from any directory
bash /path/to/claude-code-hooks-mastery/scripts/setup.sh
```

### What It Checks

1. **Environment Validation**
   - UV installation (required)
   - Python 3.8+ availability (required)
   - Git installation (required)
   - .claude/ directory structure

2. **Optional API Key Detection**
   - ELEVENLABS_API_KEY (Premium TTS)
   - OPENAI_API_KEY (LLM fallback)
   - ANTHROPIC_API_KEY (LLM fallback)
   - Note: Keys are optional, hooks fallback to local services

3. **Hook Validation**
   - All 8 hook files exist
   - Hooks are executable
   - UV can run each hook
   - Test JSON input to each hook

4. **Settings Validation**
   - .claude/settings.json is valid JSON
   - All 8 hook types are configured
   - Status line configuration
   - Permissions configuration

5. **Directory Structure**
   - Expected directories exist
   - Auto-creates logs/ directory
   - Auto-creates .claude/data/sessions/ directory
   - Checks for key documentation files

### Exit Codes

- **0**: All required checks passed (warnings are acceptable)
- **1**: One or more required checks failed

### Output Features

- Color-coded output (if terminal supports it)
- Success, failure, and warning indicators
- Helpful solution messages for failures
- Comprehensive summary report
- Next steps guidance

### Example Output

```
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║           Claude Code Hooks Mastery - Setup Validator                 ║
║                                                                        ║
║  Educational repository demonstrating complete hook lifecycle         ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Environment Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ Checking Required Tools
  ✓ UV is installed (uv 0.8.17)
  ✓ Python 3.8+ is available (Python 3.11.2)
  ✓ Git is installed (git version 2.39.0)
  ✓ .claude/ directory exists

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup Validation Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results:
  ✓ Passed:  45
  ✗ Failed:  0
  ⚠ Warnings: 3
  ━━━━━━━━━━━━━━━━
  Total:    45 checks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Setup validation passed!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
  1. Review logs directory: ls -la logs/
  2. Test a hook manually: echo '{"prompt":"test"}' | uv run .claude/hooks/user_prompt_submit.py
  3. Start Claude Code: claude
  4. Check status line: It should display session info at the top
  5. View hook logs: tail -f logs/user_prompt_submit.json
```

### Troubleshooting

#### Script hangs during hook validation

The hook validation tests run UV to verify each hook can execute. If UV needs to download dependencies, this can take time on first run.

**Solution**: Be patient on first run, or skip hook execution tests by commenting out that section.

#### Permission denied

**Solution**: Ensure the script is executable:
```bash
chmod +x scripts/setup.sh
```

#### TERM environment variable not set

If you see this warning, the script will still work but colors may not display correctly.

**Solution**: Set TERM before running:
```bash
TERM=xterm ./scripts/setup.sh
```

### When to Run This Script

- **Initial setup**: After cloning the repository
- **After updates**: When pulling changes that modify hooks or configuration
- **Before reporting issues**: To verify your environment is correctly configured
- **Periodic checks**: To ensure your setup remains valid

### Integration with CI/CD

This script can be used in CI/CD pipelines to validate the repository structure:

```yaml
# Example GitHub Actions workflow
- name: Validate Setup
  run: ./scripts/setup.sh
```

### Customization

The script is designed to be educational and self-documenting. Feel free to:

- Modify check functions for your specific needs
- Add additional validation steps
- Adjust timeout values for hook tests
- Customize color schemes

The script uses bash's `set -euo pipefail` for robust error handling and follows shell script best practices.
