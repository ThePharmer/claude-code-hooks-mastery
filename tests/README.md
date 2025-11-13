# Test Suite for Claude Code Hooks Mastery

This directory contains comprehensive test coverage for the Claude Code Hooks Mastery project, with particular emphasis on security-critical functions and hooks.

## Directory Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared pytest fixtures
├── README.md                # This file
└── hooks/                   # Hook-specific tests
    ├── __init__.py
    ├── test_pre_tool_use.py      # Security-critical hook tests
    └── test_user_prompt_submit.py # Prompt handling tests
```

## Quick Start

### Installation

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Or using UV (recommended for this project):
```bash
uv pip install -r requirements-test.txt
```

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run with verbose output:
```bash
pytest tests/ -v
```

Run with coverage report:
```bash
pytest tests/ --cov=.claude/hooks --cov-report=term-missing
```

Run only security-critical tests:
```bash
pytest tests/ -m security
```

Run only unit tests:
```bash
pytest tests/ -m unit
```

Run specific test file:
```bash
pytest tests/hooks/test_pre_tool_use.py -v
```

Run specific test class:
```bash
pytest tests/hooks/test_pre_tool_use.py::TestDangerousRmCommandDetection -v
```

Run specific test:
```bash
pytest tests/hooks/test_pre_tool_use.py::TestDangerousRmCommandDetection::test_standard_rm_rf_slash -v
```

## Test Coverage

### Security-Critical Hooks (Priority)

#### `test_pre_tool_use.py`
Tests the pre-execution security hook that blocks dangerous operations.

**Coverage includes:**
- **Dangerous rm command detection** (20+ test cases)
  - Standard rm -rf variations
  - Flag order permutations
  - Path-based blocking (/, ~, $HOME, ., .., *)
  - Case normalization
  - Whitespace handling
  - Uppercase detection
- **.env file access blocking** (15+ test cases)
  - Read/Write/Edit/MultiEdit tool blocking
  - Bash command pattern detection
  - .env.sample exception handling
- **Integration tests** (8+ test cases)
  - Exit code 2 blocking behavior
  - Error message delivery
  - Logging functionality
  - Exception handling
- **Edge cases** (10+ test cases)
  - Empty/whitespace commands
  - Missing keys
  - None values
  - Complex command chains

**Total: 60+ test cases**

#### `test_user_prompt_submit.py`
Tests the prompt submission hook that handles logging, validation, and session management.

**Coverage includes:**
- **Prompt logging** (6+ test cases)
  - Directory creation
  - File creation and appending
  - Corrupted JSON recovery
- **Session management** (12+ test cases)
  - Session directory creation
  - Session file management
  - Prompt history tracking
  - Agent naming with multi-provider fallback
  - Invalid name rejection
- **Prompt validation** (3+ test cases)
  - Validation logic
  - Case-insensitive matching
- **Integration tests** (7+ test cases)
  - Command-line flag handling
  - JSON parsing
  - Exception handling
- **Edge cases** (6+ test cases)
  - Empty prompts
  - Very long prompts
  - Special characters and Unicode
  - Missing fields

**Total: 45+ test cases**

### Overall Coverage Statistics

- **Total test cases**: 105+
- **Security-critical test cases**: 60+
- **Lines of test code**: 1,200+
- **Test-to-code ratio**: ~3:1 for security functions

## Test Organization

Tests are organized using pytest markers:

- `@pytest.mark.security` - Security-critical tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests (if any)

## Fixtures

Shared fixtures are defined in `conftest.py`:

### Temporary Directory Fixtures
- `temp_log_dir` - Temporary logs directory
- `temp_sessions_dir` - Temporary sessions directory
- `chdir_temp` - Change to temporary working directory

### Mock Data Fixtures
- `sample_tool_input` - Sample tool input data
- `sample_user_prompt_input` - Sample user prompt data
- `env_file_samples` - .env file test cases
- `dangerous_rm_commands` - Dangerous command test cases

### Utility Fixtures
- `mock_stdin` - Mock stdin with JSON data
- `mock_subprocess` - Mock subprocess.run calls
- `capture_exit` - Marker for sys.exit testing

## Best Practices

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<Feature>` (e.g., `TestDangerousRmCommandDetection`)
- Test functions: `test_<specific_behavior>` (e.g., `test_standard_rm_rf_slash`)

### Test Structure (AAA Pattern)
```python
def test_example(fixture):
    # Arrange - Set up test data and mocks
    input_data = {"key": "value"}

    # Act - Execute the function under test
    result = function_under_test(input_data)

    # Assert - Verify the expected behavior
    assert result == expected_value
```

### Testing Security Functions
- Test both positive (blocked) and negative (allowed) cases
- Cover all flag variations and permutations
- Test normalization (case, whitespace)
- Test edge cases (empty, None, missing keys)
- Verify exit codes and error messages

### Testing with UV Scripts
Since hooks use UV single-file scripts, tests import them dynamically:

```python
import importlib.util

def load_hook_module():
    hook_path = Path("/path/to/hook.py")
    spec = importlib.util.spec_from_file_location("module_name", hook_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

## Adding New Tests

1. **Create test file** in appropriate directory:
   ```bash
   touch tests/hooks/test_new_hook.py
   ```

2. **Import the module** using dynamic import:
   ```python
   def load_hook_module():
       hook_path = Path("/home/user/claude-code-hooks-mastery/.claude/hooks/new_hook.py")
       spec = importlib.util.spec_from_file_location("new_hook", hook_path)
       module = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(module)
       return module
   ```

3. **Organize tests** into classes by feature:
   ```python
   @pytest.mark.unit
   class TestFeatureName:
       def test_specific_behavior(self, fixture):
           # Test implementation
           pass
   ```

4. **Add markers** for organization:
   ```python
   @pytest.mark.security  # For security-critical tests
   @pytest.mark.unit      # For unit tests
   @pytest.mark.integration  # For integration tests
   ```

5. **Run new tests**:
   ```bash
   pytest tests/hooks/test_new_hook.py -v
   ```

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest tests/ --cov=.claude/hooks --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Coverage Goals

- **Security-critical functions**: 90%+ coverage
- **Core hooks**: 80%+ coverage
- **Utility functions**: 70%+ coverage
- **Overall project**: 70%+ coverage

## Known Limitations

1. **UV script dependencies**: Tests import hooks directly, so UV script dependencies must be available in the test environment.

2. **Subprocess mocking**: Agent naming tests mock subprocess.run, which may not catch all real-world failure modes.

3. **File system operations**: Some tests use temporary directories which may behave differently than production paths.

## Troubleshooting

### Import Errors
If you see import errors:
```bash
# Ensure you're in the project root
cd /home/user/claude-code-hooks-mastery

# Run tests with Python path
PYTHONPATH=. pytest tests/
```

### Missing Dependencies
If tests fail due to missing dependencies:
```bash
# Install test requirements
pip install -r requirements-test.txt

# For hooks that use python-dotenv
pip install python-dotenv
```

### Permission Errors
If tests fail with permission errors:
```bash
# Tests use temporary directories automatically
# But ensure logs/ directory is writable
chmod -R 755 logs/
```

## Contributing

When adding new tests:
1. Follow the AAA (Arrange-Act-Assert) pattern
2. Use descriptive test names
3. Add docstrings explaining what is tested
4. Group related tests in classes
5. Use appropriate pytest markers
6. Aim for high coverage of critical paths
7. Test both success and failure scenarios
8. Include edge cases and boundary conditions

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
