#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys
import re
from pathlib import Path

# Import error logger for structured error logging
try:
    from error_logger import log_error, log_warning, log_critical
except ImportError:
    # Fallback if error_logger not available
    def log_error(*args, **kwargs): pass
    def log_warning(*args, **kwargs): pass
    def log_critical(*args, **kwargs): pass

def is_dangerous_rm_command(command):
    """
    Comprehensive detection of dangerous rm commands.
    Matches various forms of rm -rf and similar destructive patterns.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = ' '.join(command.lower().split())
    
    # Pattern 1: Standard rm -rf variations
    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf, rm -fr, rm -Rf, etc.
        r'\brm\s+.*-[a-z]*f[a-z]*r',  # rm -fr variations
        r'\brm\s+--recursive\s+--force',  # rm --recursive --force
        r'\brm\s+--force\s+--recursive',  # rm --force --recursive
        r'\brm\s+-r\s+.*-f',  # rm -r ... -f
        r'\brm\s+-f\s+.*-r',  # rm -f ... -r
    ]
    
    # Check for dangerous patterns
    for pattern in patterns:
        if re.search(pattern, normalized):
            return True
    
    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    dangerous_paths = [
        r'/',           # Root directory
        r'/\*',         # Root with wildcard
        r'~',           # Home directory
        r'~/',          # Home directory path
        r'\$HOME',      # Home environment variable
        r'\.\.',        # Parent directory references
        r'\*',          # Wildcards in general rm -rf context
        r'\.',          # Current directory
        r'\.\s*$',      # Current directory at end of command
    ]
    
    if re.search(r'\brm\s+.*-[a-z]*r', normalized):  # If rm has recursive flag
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True
    
    return False

def contains_file_access_command(command):
    """
    Check if a bash command contains file-access operations.
    Returns True only if the command actually reads/writes/executes files.

    This prevents false positives from:
    - git commit messages mentioning sensitive files
    - echo/printf statements containing file-like text
    - comments and documentation
    """
    # Check for redirection FIRST - if there's redirection, it's always file access
    # This must be checked before safe commands (echo/printf with redirection IS file access)
    command_lower = command.lower().strip()
    if re.search(r'[<>]', command_lower):
        # Has redirection - definitely file access
        return True

    # Safe commands that don't access files (even if they mention filenames)
    # These are only safe if there's NO redirection (checked above)
    safe_command_prefixes = [
        r'^git\s+commit\b',      # git commit messages are just text
        r'^git\s+log\b',         # git log output is just text
        r'^git\s+show\b',        # git show output is just text
        r'^git\s+diff\b',        # git diff output is just text
        r'^git\s+status\b',      # git status output is just text
        r'^git\s+branch\b',      # git branch names are just text
        r'^git\s+tag\b',         # git tag names are just text
        r'^echo\b',              # echo is just text output (without redirection)
        r'^printf\b',            # printf is just text output (without redirection)
        r'^#',                   # comments
        r'^export\s+\w+\s*=',    # environment variable exports (not file access)
    ]

    # Check if command starts with a safe command prefix
    for safe_pattern in safe_command_prefixes:
        if re.search(safe_pattern, command_lower):
            return False

    # Commands that actually access files (read/write/execute)
    file_access_commands = [
        r'\bcat\b',          # read files
        r'\bvim?\b',         # vi or vim - edit files
        r'\bnano\b',         # edit files
        r'\bemacs\b',        # edit files
        r'\bless\b',         # read files
        r'\bmore\b',         # read files
        r'\bhead\b',         # read files
        r'\btail\b',         # read files
        r'\bcp\b',           # copy files
        r'\bmv\b',           # move files
        r'\brm\b',           # remove files
        r'\bchmod\b',        # modify file permissions
        r'\bchown\b',        # modify file ownership
        r'\btouch\b',        # create/modify files
        r'\bln\b',           # create links
        r'\bscp\b',          # secure copy files
        r'\brsync\b',        # sync files
        r'\btar\b',          # archive files
        r'\bzip\b',          # compress files
        r'\bunzip\b',        # decompress files
        r'\bgunzip\b',       # decompress files
        r'\bbzip2\b',        # compress files
        r'\bxz\b',           # compress files
        r'\bsed\b',          # stream editor (can modify files with -i)
        r'\bawk\b',          # can read files
        r'\bgrep\b',         # can read files
        r'\bfind\b',         # can execute commands on files
        r'\bsource\b',       # execute file contents
        r'\b\.\s+\S',        # dot command (source) - ". filename"
        r'<\s*\S',           # input redirection - "< file"
        r'>\s*\S',           # output redirection - "> file"
        r'>>\s*\S',          # append redirection - ">> file"
    ]

    # Check if command contains file-access operations
    for file_cmd_pattern in file_access_commands:
        if re.search(file_cmd_pattern, command_lower):
            return True

    return False

def is_sensitive_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access sensitive files containing secrets, credentials, or keys.

    BLOCKED FILE PATTERNS:
    - .env files (environment variables with secrets)
    - *.pem, *.key (private keys)
    - *.p12, *.pfx (certificate files)
    - id_rsa, id_ed25519, id_ecdsa, id_dsa (SSH private keys)
    - credentials.json, credentials.yaml (credential files)
    - secrets.json, secrets.yaml (secret files)
    - .aws/credentials, .aws/config (AWS credentials)
    - .ssh/config (SSH configuration)

    ALLOWED EXCEPTIONS:
    - .env.sample, .env.example (template files)
    - *.pub (public keys are safe)

    CONTEXT-AWARE BLOCKING (prevents false positives):
    - Read/Write/Edit tools: Always check file paths
    - Bash tool: Only check if command contains file-access operations
      (prevents blocking git commit messages, echo statements, etc.)
    """
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        # Define sensitive file patterns with clear categories
        sensitive_patterns = {
            # Environment files
            'env_files': [
                r'\.env(?!\.sample|\.example)',  # .env but not .env.sample or .env.example
            ],
            # Private key files
            'private_keys': [
                r'\.pem(?:\s|$)',  # PEM private keys
                r'\.key(?:\s|$)',  # Generic key files
                r'\.p12(?:\s|$)',  # PKCS12 certificate files
                r'\.pfx(?:\s|$)',  # PFX certificate files
            ],
            # SSH keys (block private keys only, not .pub public keys)
            'ssh_keys': [
                r'\bid_rsa(?!\.pub)',  # SSH RSA private key
                r'\bid_ed25519(?!\.pub)',  # SSH Ed25519 private key
                r'\bid_ecdsa(?!\.pub)',  # SSH ECDSA private key
                r'\bid_dsa(?!\.pub)',  # SSH DSA private key
            ],
            # Credential and secret files
            'credentials': [
                r'\bcredentials\.json',  # JSON credentials
                r'\bcredentials\.ya?ml',  # YAML credentials
                r'\bsecrets?\.json',  # JSON secrets
                r'\bsecrets?\.ya?ml',  # YAML secrets
            ],
            # Cloud provider and SSH config files
            'config_files': [
                r'\.aws/credentials',  # AWS credentials
                r'\.aws/config',  # AWS config (may contain secrets)
                r'\.ssh/config',  # SSH config (may contain sensitive info)
            ],
        }

        # Check file paths for file-based tools
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')

            # Check against all sensitive patterns
            for category, patterns in sensitive_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, file_path):
                        return True, category, file_path

        # Check bash commands for sensitive file access (context-aware)
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')

            # Only check for sensitive files if the command actually accesses files
            # This prevents false positives from git commit messages, echo statements, etc.
            if contains_file_access_command(command):
                # Check against all sensitive patterns in bash commands
                for category, patterns in sensitive_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, command):
                            return True, category, command

    return False, None, None

def is_dangerous_command(command):
    """
    Detect dangerous command patterns beyond rm -rf.

    BLOCKED PATTERNS:
    - chmod 777 or chmod -R 777 (overly permissive permissions)
    - curl ... | sh/bash (piping downloads to shell)
    - wget ... | sh/bash (piping downloads to shell)
    - eval ... (executing arbitrary code)
    - dd ... (disk destroyer - can wipe drives)
    - mkfs ... (filesystem creation - destructive)
    - fdisk, parted (disk partitioning tools)
    - fork bombs: :(){ :|:& };:
    - command injection via $() or `` in untrusted contexts

    Returns: (is_dangerous: bool, reason: str)
    """
    # Normalize command by removing extra spaces
    normalized = ' '.join(command.split())
    normalized_lower = normalized.lower()

    # Pattern 1: Overly permissive chmod (777 or equivalent octal like 0777)
    # Blocks: chmod 777, chmod -R 777, chmod 0777, chmod a+rwx
    chmod_patterns = [
        r'\bchmod\s+(-R\s+)?0?777\b',  # chmod 777 or chmod -R 777
        r'\bchmod\s+(-R\s+)?a=rwx\b',  # chmod a=rwx (equivalent to 777)
        r'\bchmod\s+(-R\s+)?ugo\+rwx\b',  # chmod ugo+rwx (equivalent to 777)
    ]
    for pattern in chmod_patterns:
        if re.search(pattern, normalized):
            return True, "chmod 777 (overly permissive file permissions)"

    # Pattern 2: Pipe to shell (curl/wget | sh/bash)
    # This is a common attack vector for executing malicious code
    pipe_to_shell_patterns = [
        r'curl\s+.*\|\s*(bash|sh|zsh|fish)\b',  # curl ... | bash
        r'wget\s+.*\|\s*(bash|sh|zsh|fish)\b',  # wget ... | bash
        r'fetch\s+.*\|\s*(bash|sh|zsh|fish)\b',  # fetch ... | bash
    ]
    for pattern in pipe_to_shell_patterns:
        if re.search(pattern, normalized_lower):
            return True, "piping download to shell (potential code execution risk)"

    # Pattern 3: eval with user input (very dangerous)
    # eval can execute arbitrary code
    if re.search(r'\beval\s+', normalized):
        return True, "eval command (arbitrary code execution risk)"

    # Pattern 4: Disk destroyer (dd)
    # dd can wipe entire drives if misused
    dd_patterns = [
        r'\bdd\s+.*of=/dev/',  # dd ... of=/dev/sda (writing to disk)
        r'\bdd\s+.*if=/dev/zero',  # dd if=/dev/zero (zeroing data)
        r'\bdd\s+.*if=/dev/random',  # dd if=/dev/random (random data)
    ]
    for pattern in dd_patterns:
        if re.search(pattern, normalized_lower):
            return True, "dd command targeting disk devices (potential data loss)"

    # Pattern 5: Filesystem creation (mkfs)
    # mkfs formats/creates filesystems, destroying existing data
    if re.search(r'\bmkfs\b', normalized_lower):
        return True, "mkfs command (filesystem creation - destructive)"

    # Pattern 6: Disk partitioning tools (fdisk, parted)
    # These can modify partition tables, leading to data loss
    partition_tools = {
        r'\bfdisk\b': 'fdisk',
        r'\bparted\b': 'parted',
        r'\bgdisk\b': 'gdisk',
    }
    for pattern, tool_name in partition_tools.items():
        if re.search(pattern, normalized_lower):
            return True, f"disk partitioning tool ({tool_name}) detected"

    # Pattern 7: Fork bomb detection
    # :(){ :|:& };: is a classic fork bomb
    fork_bomb_patterns = [
        r':\(\)\s*\{',  # :(){
        r'\|\s*:\s*&',  # |:&
    ]
    fork_bomb_score = sum(1 for p in fork_bomb_patterns if re.search(p, normalized))
    if fork_bomb_score >= 2:
        return True, "fork bomb pattern detected"

    # Pattern 8: Dangerous command substitution patterns
    # $(rm -rf /) or `rm -rf /` type patterns
    if re.search(r'\$\([^)]*\b(rm|dd|mkfs|fdisk)\b', normalized_lower):
        return True, "command substitution with dangerous commands"
    if re.search(r'`[^`]*\b(rm|dd|mkfs|fdisk)\b', normalized_lower):
        return True, "command substitution with dangerous commands"

    return False, None

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # SECURITY CHECK 1: Sensitive file access protection
        # Blocks access to credentials, keys, secrets, and other sensitive files
        is_sensitive, category, target = is_sensitive_file_access(tool_name, tool_input)
        if is_sensitive:
            # Log the blocked sensitive file access
            log_critical(
                hook_name='pre_tool_use',
                error_type='SENSITIVE_FILE_BLOCKED',
                message=f'Blocked access to sensitive {category}',
                context={
                    'session_id': input_data.get('session_id', 'unknown'),
                    'tool_name': tool_name,
                    'category': category,
                    'target': target
                }
            )

            print(f"BLOCKED: Access to sensitive {category} is prohibited", file=sys.stderr)
            print(f"Target: {target}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Sensitive files protected:", file=sys.stderr)
            print("  - .env files (use .env.sample for templates)", file=sys.stderr)
            print("  - Private keys (*.pem, *.key, *.p12, *.pfx)", file=sys.stderr)
            print("  - SSH keys (id_rsa, id_ed25519, etc.)", file=sys.stderr)
            print("  - Credentials (credentials.json, secrets.yaml, etc.)", file=sys.stderr)
            print("  - Cloud configs (.aws/credentials, .ssh/config)", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude

        # SECURITY CHECK 2 & 3: Dangerous command protection (Bash tool only)
        if tool_name == 'Bash':
            command = tool_input.get('command', '')

            # Check for dangerous rm -rf commands
            if is_dangerous_rm_command(command):
                # Log the blocked dangerous rm command
                log_critical(
                    hook_name='pre_tool_use',
                    error_type='DANGEROUS_RM_BLOCKED',
                    message='Blocked dangerous rm -rf command',
                    context={
                        'session_id': input_data.get('session_id', 'unknown'),
                        'tool_name': tool_name,
                        'command': command
                    }
                )

                print("BLOCKED: Dangerous rm command detected and prevented", file=sys.stderr)
                print(f"Command: {command}", file=sys.stderr)
                print("", file=sys.stderr)
                print("This protection prevents accidental deletion of:", file=sys.stderr)
                print("  - System directories (/, /usr, /etc)", file=sys.stderr)
                print("  - Home directory and all contents", file=sys.stderr)
                print("  - Recursive deletions with wildcards", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude

            # Check for other dangerous command patterns
            is_dangerous, reason = is_dangerous_command(command)
            if is_dangerous:
                # Log the blocked dangerous command
                log_critical(
                    hook_name='pre_tool_use',
                    error_type='DANGEROUS_COMMAND_BLOCKED',
                    message=f'Blocked dangerous command: {reason}',
                    context={
                        'session_id': input_data.get('session_id', 'unknown'),
                        'tool_name': tool_name,
                        'command': command,
                        'reason': reason
                    }
                )

                print(f"BLOCKED: Dangerous command pattern detected - {reason}", file=sys.stderr)
                print(f"Command: {command}", file=sys.stderr)
                print("", file=sys.stderr)
                print("Protected command patterns:", file=sys.stderr)
                print("  - chmod 777 (overly permissive permissions)", file=sys.stderr)
                print("  - curl/wget | sh (piping to shell)", file=sys.stderr)
                print("  - eval (arbitrary code execution)", file=sys.stderr)
                print("  - dd/mkfs/fdisk (disk operations)", file=sys.stderr)
                print("  - Fork bombs and command injection", file=sys.stderr)
                sys.exit(2)  # Exit code 2 blocks tool call and shows error to Claude
        
        # Ensure log directory exists
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'pre_tool_use.json'
        
        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        # Log JSON parsing failure
        log_error(
            hook_name='pre_tool_use',
            error_type='JSON_PARSE_ERROR',
            message='Failed to parse JSON input',
            context={'error': str(e)},
            exception=e
        )
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()