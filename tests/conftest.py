"""
Pytest configuration and shared fixtures for test suite.

This module provides reusable fixtures for testing hooks,
including mock objects, temporary directories, and test data.
"""

import json
import tempfile
from pathlib import Path
import pytest
import sys
import os


@pytest.fixture
def temp_log_dir(tmp_path):
    """
    Create a temporary logs directory for testing.

    Returns:
        Path: Path to temporary logs directory
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


@pytest.fixture
def temp_sessions_dir(tmp_path):
    """
    Create a temporary sessions directory for testing.

    Returns:
        Path: Path to temporary sessions directory
    """
    sessions_dir = tmp_path / ".claude" / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


@pytest.fixture
def sample_tool_input():
    """
    Provide sample tool input data for testing.

    Returns:
        dict: Sample tool input data
    """
    return {
        "tool_name": "Bash",
        "tool_input": {
            "command": "echo 'Hello, World!'"
        },
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_user_prompt_input():
    """
    Provide sample user prompt input data for testing.

    Returns:
        dict: Sample user prompt input data
    """
    return {
        "session_id": "test-session-456",
        "prompt": "Help me write some Python code",
        "timestamp": "2025-11-13T12:00:00Z"
    }


@pytest.fixture
def mock_stdin(monkeypatch):
    """
    Factory fixture to mock stdin with JSON data.

    Usage:
        def test_example(mock_stdin):
            mock_stdin({"key": "value"})
            # stdin now contains JSON data
    """
    def _mock_stdin(data):
        import io
        json_data = json.dumps(data)
        monkeypatch.setattr('sys.stdin', io.StringIO(json_data))
    return _mock_stdin


@pytest.fixture
def capture_exit():
    """
    Fixture to capture sys.exit calls.

    Usage:
        def test_example(capture_exit):
            with pytest.raises(SystemExit) as exc_info:
                # code that calls sys.exit()
            assert exc_info.value.code == 0
    """
    # This is a marker fixture; actual capturing is done with pytest.raises
    pass


@pytest.fixture
def chdir_temp(tmp_path, monkeypatch):
    """
    Change working directory to temporary directory for testing.

    Args:
        tmp_path: pytest's tmp_path fixture
        monkeypatch: pytest's monkeypatch fixture
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def mock_subprocess(monkeypatch):
    """
    Mock subprocess.run for testing external command calls.

    Returns:
        Mock object that can be configured for different test scenarios
    """
    class MockCompletedProcess:
        def __init__(self, returncode=0, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    class MockSubprocess:
        def __init__(self):
            self.calls = []
            self.return_value = MockCompletedProcess()

        def run(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return self.return_value

        def set_return(self, returncode=0, stdout="", stderr=""):
            self.return_value = MockCompletedProcess(returncode, stdout, stderr)

    mock = MockSubprocess()
    monkeypatch.setattr('subprocess.run', mock.run)
    return mock


@pytest.fixture
def env_file_samples():
    """
    Provide sample .env file paths and commands for testing.

    Returns:
        dict: Dictionary of test cases for .env file access
    """
    return {
        "blocked_paths": [
            "/path/to/.env",
            "/home/user/.env",
            "project/.env",
            ".env"
        ],
        "allowed_paths": [
            "/path/to/.env.sample",
            "/home/user/.env.example",
            "project/.env.template"
        ],
        "blocked_commands": [
            "cat .env",
            "echo SECRET=value > .env",
            "touch .env",
            "cp .env .env.backup",
            "mv .env.old .env"
        ],
        "allowed_commands": [
            "cat .env.sample",
            "echo EXAMPLE=value > .env.sample",
            "cp .env.sample .env.local"
        ]
    }


@pytest.fixture
def dangerous_rm_commands():
    """
    Provide comprehensive list of dangerous rm commands for testing.

    Returns:
        dict: Dictionary with blocked and allowed commands
    """
    return {
        "blocked": [
            "rm -rf /",
            "rm -rf /*",
            "rm -rf ~",
            "rm -rf ~/",
            "rm -rf $HOME",
            "rm -rf .",
            "rm -rf ..",
            "rm -rf *",
            "rm -fr /tmp",
            "rm -Rf /var",
            "rm --recursive --force /",
            "rm --force --recursive /",
            "rm -r -f /tmp",
            "rm -f -r /tmp",
            "RM -RF /",  # Uppercase
            "  rm   -rf   /  ",  # Extra spaces
            "rm -rf/ ",  # No space before path
            "sudo rm -rf /",
            "rm -rfv /tmp/*",
            "rm -rf ./",
            "rm -rf ../",
        ],
        "allowed": [
            "rm file.txt",
            "rm -f file.txt",
            "rm /tmp/specific-file.txt",
            "ls -la",
            "echo 'test'",
            "mkdir -p /tmp/test",
            "rm -r /tmp/safe-directory-with-specific-name",  # Without -f
        ]
    }
