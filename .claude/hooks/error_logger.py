#!/usr/bin/env python3
"""
Error Logging Utilities for Claude Code Hooks

Shared module for structured error logging across all hooks.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any


class ErrorLogger:
    """Structured error logging for hooks."""

    def __init__(self, log_file: str = "logs/errors.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_error(
        self,
        hook_name: str,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "ERROR",
        exception: Optional[Exception] = None,
    ) -> None:
        """
        Log a structured error.

        Args:
            hook_name: Name of the hook (e.g., 'pre_tool_use')
            error_type: Type of error (e.g., 'JSON_PARSE_ERROR', 'TIMEOUT', 'VALIDATION_FAILED')
            message: Human-readable error message
            context: Additional context (session_id, tool_name, etc.)
            severity: ERROR, WARNING, CRITICAL
            exception: Original exception if available
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": hook_name,
            "error_type": error_type,
            "severity": severity,
            "message": message,
            "context": context or {},
        }

        # Add exception details if available
        if exception:
            error_entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
            }

        # Append to log file
        try:
            # Read existing entries
            entries = []
            if self.log_file.exists():
                try:
                    with open(self.log_file, 'r') as f:
                        content = f.read().strip()
                        if content:
                            entries = json.loads(content)
                except json.JSONDecodeError:
                    # Corrupted log file - start fresh but back up old one
                    backup_file = self.log_file.with_suffix('.json.corrupt')
                    if self.log_file.exists():
                        self.log_file.rename(backup_file)
                    entries = []

            # Append new entry
            entries.append(error_entry)

            # Write back (keep last 1000 entries)
            with open(self.log_file, 'w') as f:
                json.dump(entries[-1000:], f, indent=2)

        except IOError as e:
            # If we can't write to the log file, at least print to stderr
            print(f"CRITICAL: Could not write to error log: {e}", file=sys.stderr)
            print(json.dumps(error_entry, indent=2), file=sys.stderr)

    def log_warning(self, hook_name: str, error_type: str, message: str, context: Optional[Dict] = None) -> None:
        """Log a warning."""
        self.log_error(hook_name, error_type, message, context, severity="WARNING")

    def log_critical(
        self,
        hook_name: str,
        error_type: str,
        message: str,
        context: Optional[Dict] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """Log a critical error."""
        self.log_error(hook_name, error_type, message, context, severity="CRITICAL", exception=exception)

    def get_recent_errors(self, limit: int = 10, hook_name: Optional[str] = None) -> list:
        """Get recent errors, optionally filtered by hook."""
        if not self.log_file.exists():
            return []

        try:
            with open(self.log_file, 'r') as f:
                entries = json.load(f)

            # Filter by hook if specified
            if hook_name:
                entries = [e for e in entries if e.get('hook') == hook_name]

            # Return most recent
            return entries[-limit:]
        except (json.JSONDecodeError, IOError):
            return []

    def get_error_counts(self) -> Dict[str, int]:
        """Get error counts by type."""
        if not self.log_file.exists():
            return {}

        try:
            with open(self.log_file, 'r') as f:
                entries = json.load(f)

            counts = {}
            for entry in entries:
                error_type = entry.get('error_type', 'UNKNOWN')
                counts[error_type] = counts.get(error_type, 0) + 1

            return counts
        except (json.JSONDecodeError, IOError):
            return {}


# Singleton instance
_error_logger = None


def get_error_logger() -> ErrorLogger:
    """Get the global error logger instance."""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger


# Convenience functions
def log_error(hook_name: str, error_type: str, message: str, **kwargs) -> None:
    """Log an error using the global logger."""
    get_error_logger().log_error(hook_name, error_type, message, **kwargs)


def log_warning(hook_name: str, error_type: str, message: str, **kwargs) -> None:
    """Log a warning using the global logger."""
    get_error_logger().log_warning(hook_name, error_type, message, **kwargs)


def log_critical(hook_name: str, error_type: str, message: str, **kwargs) -> None:
    """Log a critical error using the global logger."""
    get_error_logger().log_critical(hook_name, error_type, message, **kwargs)


if __name__ == '__main__':
    # Test the error logger
    logger = ErrorLogger()

    # Test different severity levels
    logger.log_warning(
        'test_hook',
        'TEST_WARNING',
        'This is a test warning',
        context={'test': True}
    )

    logger.log_error(
        'test_hook',
        'TEST_ERROR',
        'This is a test error',
        context={'test': True}
    )

    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger.log_critical(
            'test_hook',
            'TEST_CRITICAL',
            'This is a test critical error',
            context={'test': True},
            exception=e
        )

    # Show recent errors
    recent = logger.get_recent_errors(limit=5)
    print(f"\nRecent errors ({len(recent)}):")
    print(json.dumps(recent, indent=2))

    # Show error counts
    counts = logger.get_error_counts()
    print(f"\nError counts:")
    print(json.dumps(counts, indent=2))
