"""
Comprehensive unit tests for user_prompt_submit.py hook.

This module tests prompt validation, logging, session management,
and agent naming functionality of the user_prompt_submit hook.
"""

import json
import pytest
from pathlib import Path
from io import StringIO
import importlib.util
from unittest.mock import Mock, patch


# Import the hook module
def load_hook_module():
    """Load the user_prompt_submit.py hook module dynamically."""
    hook_path = Path("/home/user/claude-code-hooks-mastery/.claude/hooks/user_prompt_submit.py")
    spec = importlib.util.spec_from_file_location("user_prompt_submit", hook_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def user_prompt_submit():
    """Fixture to load the user_prompt_submit module."""
    return load_hook_module()


# ============================================================================
# Prompt Logging Tests
# ============================================================================

@pytest.mark.unit
class TestLogUserPrompt:
    """Test prompt logging functionality."""

    def test_log_creates_directory_if_missing(self, user_prompt_submit, chdir_temp):
        """Test that logging creates logs directory if it doesn't exist."""
        session_id = "test-session-001"
        input_data = {
            "session_id": session_id,
            "prompt": "Test prompt",
            "timestamp": "2025-11-13T12:00:00Z"
        }

        # Ensure logs directory doesn't exist
        log_dir = chdir_temp / "logs"
        assert not log_dir.exists()

        # Call log function
        user_prompt_submit.log_user_prompt(session_id, input_data)

        # Check that directory was created
        assert log_dir.exists()
        assert (log_dir / "user_prompt_submit.json").exists()

    def test_log_creates_new_file_with_first_entry(self, user_prompt_submit, chdir_temp):
        """Test that logging creates new file with first entry."""
        session_id = "test-session-002"
        input_data = {
            "session_id": session_id,
            "prompt": "First prompt",
            "timestamp": "2025-11-13T12:00:00Z"
        }

        user_prompt_submit.log_user_prompt(session_id, input_data)

        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        assert log_file.exists()

        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert isinstance(log_data, list)
        assert len(log_data) == 1
        assert log_data[0]["session_id"] == session_id
        assert log_data[0]["prompt"] == "First prompt"

    def test_log_appends_to_existing_file(self, user_prompt_submit, chdir_temp):
        """Test that logging appends to existing log file."""
        log_dir = chdir_temp / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "user_prompt_submit.json"

        # Create initial log data
        initial_data = [
            {"session_id": "old-session", "prompt": "Old prompt"}
        ]
        with open(log_file, 'w') as f:
            json.dump(initial_data, f)

        # Log new entry
        new_data = {
            "session_id": "new-session",
            "prompt": "New prompt",
            "timestamp": "2025-11-13T12:00:00Z"
        }
        user_prompt_submit.log_user_prompt("new-session", new_data)

        # Verify both entries exist
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert len(log_data) == 2
        assert log_data[0]["session_id"] == "old-session"
        assert log_data[1]["session_id"] == "new-session"

    def test_log_handles_corrupted_json(self, user_prompt_submit, chdir_temp):
        """Test that corrupted JSON file is replaced."""
        log_dir = chdir_temp / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "user_prompt_submit.json"

        # Write corrupted JSON
        with open(log_file, 'w') as f:
            f.write("invalid json {{{")

        # Log new entry
        new_data = {
            "session_id": "new-session",
            "prompt": "New prompt"
        }
        user_prompt_submit.log_user_prompt("new-session", new_data)

        # Verify file is valid and contains new entry
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert isinstance(log_data, list)
        assert len(log_data) == 1
        assert log_data[0]["session_id"] == "new-session"


# ============================================================================
# Session Management Tests
# ============================================================================

@pytest.mark.unit
class TestManageSessionData:
    """Test session data management functionality."""

    def test_creates_session_directory_if_missing(self, user_prompt_submit, chdir_temp):
        """Test that session directory is created if it doesn't exist."""
        session_id = "test-session-003"
        prompt = "Test prompt for session"

        # Ensure directory doesn't exist
        sessions_dir = chdir_temp / ".claude" / "data" / "sessions"
        assert not sessions_dir.exists()

        # Manage session data
        user_prompt_submit.manage_session_data(session_id, prompt, name_agent=False)

        # Check that directory was created
        assert sessions_dir.exists()

    def test_creates_new_session_file(self, user_prompt_submit, chdir_temp):
        """Test that new session file is created."""
        session_id = "test-session-004"
        prompt = "First session prompt"

        user_prompt_submit.manage_session_data(session_id, prompt, name_agent=False)

        session_file = chdir_temp / ".claude" / "data" / "sessions" / f"{session_id}.json"
        assert session_file.exists()

        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert session_data["session_id"] == session_id
        assert isinstance(session_data["prompts"], list)
        assert len(session_data["prompts"]) == 1
        assert session_data["prompts"][0] == prompt

    def test_appends_prompt_to_existing_session(self, user_prompt_submit, chdir_temp):
        """Test that prompt is appended to existing session."""
        session_id = "test-session-005"

        # Create initial session
        sessions_dir = chdir_temp / ".claude" / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session_file = sessions_dir / f"{session_id}.json"

        initial_data = {
            "session_id": session_id,
            "prompts": ["First prompt"]
        }
        with open(session_file, 'w') as f:
            json.dump(initial_data, f)

        # Add new prompt
        user_prompt_submit.manage_session_data(session_id, "Second prompt", name_agent=False)

        # Verify both prompts exist
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert len(session_data["prompts"]) == 2
        assert session_data["prompts"][0] == "First prompt"
        assert session_data["prompts"][1] == "Second prompt"

    def test_handles_corrupted_session_file(self, user_prompt_submit, chdir_temp):
        """Test that corrupted session file is replaced."""
        session_id = "test-session-006"

        # Create corrupted session file
        sessions_dir = chdir_temp / ".claude" / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session_file = sessions_dir / f"{session_id}.json"

        with open(session_file, 'w') as f:
            f.write("corrupted json {{{")

        # Manage session data
        user_prompt_submit.manage_session_data(session_id, "New prompt", name_agent=False)

        # Verify file is valid
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert session_data["session_id"] == session_id
        assert len(session_data["prompts"]) == 1
        assert session_data["prompts"][0] == "New prompt"

    @patch('subprocess.run')
    def test_agent_naming_with_ollama_success(self, mock_run, user_prompt_submit, chdir_temp):
        """Test agent naming with successful Ollama call."""
        session_id = "test-session-007"
        prompt = "Create a test agent"

        # Mock successful Ollama response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "TestAgent123"
        mock_run.return_value = mock_result

        user_prompt_submit.manage_session_data(session_id, prompt, name_agent=True)

        session_file = chdir_temp / ".claude" / "data" / "sessions" / f"{session_id}.json"
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert "agent_name" in session_data
        assert session_data["agent_name"] == "TestAgent123"

    @patch('subprocess.run')
    def test_agent_naming_ollama_exception_fallback_to_anthropic(self, mock_run, user_prompt_submit, chdir_temp):
        """Test agent naming falls back from Ollama to Anthropic when exception is raised."""
        session_id = "test-session-008"
        prompt = "Create another agent"

        # Mock Ollama raising exception (e.g., timeout) and Anthropic success
        call_count = [0]

        def mock_run_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call is Ollama
                raise TimeoutError("Ollama timeout")
            else:  # Second call is Anthropic
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = "AnthropicAgent"
                return mock_result

        mock_run.side_effect = mock_run_side_effect

        user_prompt_submit.manage_session_data(session_id, prompt, name_agent=True)

        session_file = chdir_temp / ".claude" / "data" / "sessions" / f"{session_id}.json"
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert "agent_name" in session_data
        assert session_data["agent_name"] == "AnthropicAgent"

    @patch('subprocess.run')
    def test_agent_naming_all_providers_fail(self, mock_run, user_prompt_submit, chdir_temp):
        """Test that session continues even if all naming providers fail."""
        session_id = "test-session-009"
        prompt = "Create agent with failing providers"

        # Mock all providers failing
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        # Should not raise exception
        user_prompt_submit.manage_session_data(session_id, prompt, name_agent=True)

        session_file = chdir_temp / ".claude" / "data" / "sessions" / f"{session_id}.json"
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        # Session should exist but without agent_name
        assert session_data["session_id"] == session_id
        assert "agent_name" not in session_data

    @patch('subprocess.run')
    def test_agent_naming_invalid_name_rejected(self, mock_run, user_prompt_submit, chdir_temp):
        """Test that invalid agent names are rejected."""
        session_id = "test-session-010"
        prompt = "Create agent"

        # Mock Ollama returning invalid name (multiple words)
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Invalid Name With Spaces"
        mock_run.return_value = mock_result

        user_prompt_submit.manage_session_data(session_id, prompt, name_agent=True)

        session_file = chdir_temp / ".claude" / "data" / "sessions" / f"{session_id}.json"
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        # Invalid name should be rejected
        assert "agent_name" not in session_data

    def test_agent_naming_not_overwrite_existing(self, user_prompt_submit, chdir_temp):
        """Test that existing agent name is not overwritten."""
        session_id = "test-session-011"

        # Create session with existing agent name
        sessions_dir = chdir_temp / ".claude" / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session_file = sessions_dir / f"{session_id}.json"

        initial_data = {
            "session_id": session_id,
            "prompts": ["First prompt"],
            "agent_name": "ExistingAgent"
        }
        with open(session_file, 'w') as f:
            json.dump(initial_data, f)

        # Try to name agent again
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "NewAgent"
            mock_run.return_value = mock_result

            user_prompt_submit.manage_session_data(session_id, "Second prompt", name_agent=True)

        # Verify existing name is preserved
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert session_data["agent_name"] == "ExistingAgent"


# ============================================================================
# Prompt Validation Tests
# ============================================================================

@pytest.mark.unit
class TestValidatePrompt:
    """Test prompt validation functionality."""

    def test_empty_blocked_patterns_allows_all(self, user_prompt_submit):
        """Test that empty blocked patterns allows all prompts."""
        is_valid, reason = user_prompt_submit.validate_prompt("Any prompt text")
        assert is_valid is True
        assert reason is None

    def test_normal_prompts_are_valid(self, user_prompt_submit):
        """Test that normal prompts are valid."""
        prompts = [
            "Help me write a Python function",
            "Explain how to use Claude Code",
            "Create a test for my code",
            "Refactor this function"
        ]

        for prompt in prompts:
            is_valid, reason = user_prompt_submit.validate_prompt(prompt)
            assert is_valid is True
            assert reason is None

    def test_validation_is_case_insensitive(self, user_prompt_submit):
        """Test that validation is case-insensitive."""
        # Note: Current implementation has empty blocked_patterns
        # This test documents the expected behavior
        is_valid, reason = user_prompt_submit.validate_prompt("TEST PROMPT")
        assert is_valid is True


# ============================================================================
# Integration Tests: Full Hook Behavior
# ============================================================================

@pytest.mark.integration
class TestUserPromptSubmitIntegration:
    """Integration tests for the complete hook behavior."""

    def test_main_with_no_flags(self, user_prompt_submit, monkeypatch, chdir_temp):
        """Test main function with no command-line flags."""
        input_data = {
            "session_id": "integration-001",
            "prompt": "Test prompt",
            "timestamp": "2025-11-13T12:00:00Z"
        }

        # Mock stdin and argv
        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py'])

        # Run main
        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        assert exc_info.value.code == 0

        # Verify logging occurred
        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        assert log_file.exists()

    def test_main_with_log_only_flag(self, user_prompt_submit, monkeypatch, chdir_temp):
        """Test main function with --log-only flag."""
        input_data = {
            "session_id": "integration-002",
            "prompt": "Test prompt with log only",
            "timestamp": "2025-11-13T12:00:00Z"
        }

        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py', '--log-only'])

        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        assert exc_info.value.code == 0

        # Verify logging occurred
        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        assert log_file.exists()

    def test_main_with_store_last_prompt_flag(self, user_prompt_submit, monkeypatch, chdir_temp):
        """Test main function with --store-last-prompt flag."""
        input_data = {
            "session_id": "integration-003",
            "prompt": "Test prompt to store",
            "timestamp": "2025-11-13T12:00:00Z"
        }

        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py', '--store-last-prompt'])

        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        assert exc_info.value.code == 0

        # Verify session was created
        session_file = chdir_temp / ".claude" / "data" / "sessions" / "integration-003.json"
        assert session_file.exists()

    @patch('subprocess.run')
    def test_main_with_name_agent_flag(self, mock_run, user_prompt_submit, monkeypatch, chdir_temp):
        """Test main function with --name-agent flag."""
        input_data = {
            "session_id": "integration-004",
            "prompt": "Create a new agent",
            "timestamp": "2025-11-13T12:00:00Z"
        }

        # Mock successful agent naming
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "IntegrationAgent"
        mock_run.return_value = mock_result

        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py', '--name-agent'])

        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        assert exc_info.value.code == 0

        # Verify agent name was set
        session_file = chdir_temp / ".claude" / "data" / "sessions" / "integration-004.json"
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        assert session_data.get("agent_name") == "IntegrationAgent"

    def test_main_handles_invalid_json(self, user_prompt_submit, monkeypatch):
        """Test that main handles invalid JSON gracefully."""
        monkeypatch.setattr('sys.stdin', StringIO("invalid json {{{"))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py'])

        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        # Should exit gracefully with code 0
        assert exc_info.value.code == 0

    def test_main_handles_exceptions_gracefully(self, user_prompt_submit, monkeypatch):
        """Test that main handles unexpected exceptions gracefully."""
        input_data = {
            "session_id": "integration-005",
            "prompt": "Test exception handling"
        }

        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py'])

        # Mock Path to raise exception
        def mock_path_constructor(*args, **kwargs):
            raise PermissionError("Simulated error")

        with patch('pathlib.Path', side_effect=mock_path_constructor):
            with pytest.raises(SystemExit) as exc_info:
                user_prompt_submit.main()

            # Should exit gracefully
            assert exc_info.value.code == 0


# ============================================================================
# Edge Cases and Boundary Conditions
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_prompt(self, user_prompt_submit, chdir_temp):
        """Test that empty prompt is logged correctly."""
        session_id = "edge-001"
        input_data = {
            "session_id": session_id,
            "prompt": ""
        }

        user_prompt_submit.log_user_prompt(session_id, input_data)

        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert len(log_data) == 1
        assert log_data[0]["prompt"] == ""

    def test_very_long_prompt(self, user_prompt_submit, chdir_temp):
        """Test that very long prompts are handled correctly."""
        session_id = "edge-002"
        long_prompt = "A" * 10000  # 10,000 character prompt

        input_data = {
            "session_id": session_id,
            "prompt": long_prompt
        }

        user_prompt_submit.log_user_prompt(session_id, input_data)

        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert log_data[0]["prompt"] == long_prompt

    def test_prompt_with_special_characters(self, user_prompt_submit, chdir_temp):
        """Test that prompts with special characters are handled."""
        session_id = "edge-003"
        special_prompt = "Test with special chars: \n\t\"quotes\" 'apostrophe' <html> & symbols"

        input_data = {
            "session_id": session_id,
            "prompt": special_prompt
        }

        user_prompt_submit.log_user_prompt(session_id, input_data)

        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert log_data[0]["prompt"] == special_prompt

    def test_unicode_in_prompt(self, user_prompt_submit, chdir_temp):
        """Test that Unicode characters are handled correctly."""
        session_id = "edge-004"
        unicode_prompt = "Test with Unicode: 你好 🚀 café naïve"

        input_data = {
            "session_id": session_id,
            "prompt": unicode_prompt
        }

        user_prompt_submit.log_user_prompt(session_id, input_data)

        log_file = chdir_temp / "logs" / "user_prompt_submit.json"
        with open(log_file, 'r') as f:
            log_data = json.load(f)

        assert log_data[0]["prompt"] == unicode_prompt

    def test_missing_session_id(self, user_prompt_submit, monkeypatch, chdir_temp):
        """Test that missing session_id is handled."""
        input_data = {
            "prompt": "Test prompt without session"
        }

        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py'])

        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        # Should handle gracefully
        assert exc_info.value.code == 0

    def test_missing_prompt_field(self, user_prompt_submit, monkeypatch, chdir_temp):
        """Test that missing prompt field is handled."""
        input_data = {
            "session_id": "edge-005"
        }

        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(input_data)))
        monkeypatch.setattr('sys.argv', ['user_prompt_submit.py'])

        with pytest.raises(SystemExit) as exc_info:
            user_prompt_submit.main()

        # Should handle gracefully
        assert exc_info.value.code == 0
