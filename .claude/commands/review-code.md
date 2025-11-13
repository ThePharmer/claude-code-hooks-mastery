---
allowed-tools: Bash(git:*), Read, Grep
description: Review code changes and provide feedback on implementation quality
---

# Code Review

Analyze recent code changes and provide comprehensive feedback on code quality, security, and best practices.

## Instructions

- **IMPORTANT: Focus on providing constructive, educational feedback**
- **IMPORTANT: Highlight both strengths and areas for improvement**
- **IMPORTANT: Reference project standards from CLAUDE.md and CONTRIBUTING.md**
- **IMPORTANT: Check for security vulnerabilities and hook best practices**

## Commands

- Recent changes: !`git diff HEAD~3 HEAD`
- Modified files: !`git diff --name-only HEAD~3 HEAD`
- Recent commits: !`git log -3 --oneline`

## Files

@CONTRIBUTING.md
@CLAUDE.md

## Analysis Focus

1. **Code Quality**
   - UV single-file script compliance
   - Error handling patterns
   - Documentation and comments

2. **Security**
   - Sensitive data handling
   - Command injection vulnerabilities
   - Exit code usage (especially exit 2 for blocking)

3. **Hook Best Practices**
   - 60-second timeout compliance
   - Proper JSON input/output
   - Logging patterns

4. **Educational Value**
   - Clear examples for learners
   - Comprehensive documentation
   - Alignment with project philosophy

## Output Format

Provide a structured review with:
- **Summary**: Overall assessment
- **Strengths**: What's done well
- **Improvements**: Specific suggestions
- **Security**: Any concerns or validations needed
- **Learning**: Educational value for users

## Review Target

$ARGUMENTS
