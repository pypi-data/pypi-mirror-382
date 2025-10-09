"""
Safe shell command executor tool
"""

import subprocess
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class Shell(BaseTool):
    """
    Execute safe shell commands

    Restricted to read-only commands for security
    """

    name = "shell"
    description = "Execute safe shell commands. Input: shell command"
    category = "computation"

    def __init__(self, safe_mode: bool = True, timeout: int = 10, **kwargs):
        """
        Initialize shell tool

        Args:
            safe_mode: If True, only allows read-only commands
            timeout: Command timeout in seconds
        """
        super().__init__(**kwargs)
        self.safe_mode = safe_mode
        self.timeout = timeout

        # Allowed commands in safe mode (read-only)
        self.safe_commands = [
            "ls",
            "pwd",
            "echo",
            "cat",
            "head",
            "tail",
            "grep",
            "find",
            "wc",
            "date",
            "whoami",
            "hostname",
            "uname",
            "df",
            "du",
            "which",
            "whereis",
        ]

        # Blocked commands (destructive)
        self.blocked_commands = [
            "rm",
            "rmdir",
            "mv",
            "cp",
            "chmod",
            "chown",
            "kill",
            "sudo",
            "su",
            "shutdown",
            "reboot",
            "dd",
            "mkfs",
            "format",
        ]

    def validate_input(self, input_text: str) -> bool:
        """
        Validate command for security

        Args:
            input_text: Command to validate

        Returns:
            True if safe, False otherwise
        """
        if not input_text or not input_text.strip():
            return False

        command = input_text.strip().lower()

        # Check for blocked commands
        for blocked in self.blocked_commands:
            if command.startswith(blocked) or f" {blocked}" in command:
                return False

        # In safe mode, only allow whitelisted commands
        if self.safe_mode:
            base_command = command.split()[0]
            if base_command not in self.safe_commands:
                return False

        # Block dangerous patterns
        dangerous_patterns = [">", ">>", "|", ";", "&", "$(", "`"]
        for pattern in dangerous_patterns:
            if pattern in command:
                return False

        return True

    def execute(self, input_text: str) -> str:
        """
        Execute shell command

        Args:
            input_text: Shell command

        Returns:
            Command output or error message
        """
        command = input_text.strip()

        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            # Get output
            output = result.stdout.strip()
            errors = result.stderr.strip()

            if result.returncode != 0:
                if errors:
                    return f"Command failed (exit code {result.returncode}):\n{errors}"
                else:
                    return f"Command failed with exit code {result.returncode}"

            if output:
                return output
            elif errors:
                return errors
            else:
                return "Command executed successfully (no output)"

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
