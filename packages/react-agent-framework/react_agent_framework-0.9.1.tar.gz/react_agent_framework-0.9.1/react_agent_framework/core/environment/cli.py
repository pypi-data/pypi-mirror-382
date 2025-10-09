"""
CLI environment for command-line interaction

Allows agents to execute shell commands
"""

import subprocess
from typing import Dict, Any, List
from react_agent_framework.core.environment.base import (
    BaseEnvironment,
    Action,
    Observation,
)


class CLIEnvironment(BaseEnvironment):
    """
    Command-line interface environment

    Enables shell command execution
    """

    def __init__(
        self,
        working_directory: str = ".",
        safe_mode: bool = True,
        timeout: int = 30,
    ):
        """
        Initialize CLI environment

        Args:
            working_directory: Starting directory
            safe_mode: Restrict to safe commands only
            timeout: Command timeout in seconds
        """
        super().__init__(name="CLIEnvironment")
        self.working_directory = working_directory
        self.safe_mode = safe_mode
        self.timeout = timeout

        # Safe commands whitelist
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
            "df",
            "du",
            "which",
            "whereis",
        ]

        # Blocked commands
        self.blocked_commands = [
            "rm",
            "rmdir",
            "mv",
            "chmod",
            "chown",
            "kill",
            "sudo",
            "su",
            "shutdown",
            "reboot",
        ]

        self.current_directory = working_directory
        self.last_command = None
        self.last_output = None

    def reset(self) -> Observation:
        """Reset to initial state"""
        self.current_directory = self.working_directory
        self.last_command = None
        self.last_output = None

        obs = Observation(
            data={
                "directory": self.current_directory,
                "status": "ready",
                "message": "CLI environment ready",
            }
        )

        self.state.current_observation = obs
        return obs

    def step(self, action: Action) -> Observation:
        """
        Execute CLI action

        Supported actions:
        - execute: Run shell command
        - cd: Change directory
        - pwd: Print working directory
        """
        action_name = action.name.lower()

        if action_name == "execute":
            command = action.parameters.get("command", "")
            return self._execute_command(command)

        elif action_name == "cd":
            directory = action.parameters.get("directory", "")
            return self._change_directory(directory)

        elif action_name == "pwd":
            return self._print_working_directory()

        else:
            obs = Observation(
                data=f"Unknown action: {action_name}",
                metadata={"error": True},
            )
            self.state.add_step(action, obs)
            return obs

    def _execute_command(self, command: str) -> Observation:
        """Execute shell command"""
        # Validate command
        if not self._is_safe_command(command):
            obs = Observation(
                data={
                    "command": command,
                    "error": "Command blocked by safe mode",
                    "exit_code": -1,
                },
                metadata={"error": True, "safe_mode": True},
            )
            return obs

        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.current_directory,
            )

            self.last_command = command
            self.last_output = result.stdout

            obs = Observation(
                data={
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode,
                    "success": result.returncode == 0,
                }
            )

            return obs

        except subprocess.TimeoutExpired:
            obs = Observation(
                data={
                    "command": command,
                    "error": f"Command timed out after {self.timeout}s",
                    "exit_code": -1,
                },
                metadata={"error": True, "timeout": True},
            )
            return obs

        except Exception as e:
            obs = Observation(
                data={
                    "command": command,
                    "error": str(e),
                    "exit_code": -1,
                },
                metadata={"error": True},
            )
            return obs

    def _change_directory(self, directory: str) -> Observation:
        """Change working directory"""
        import os

        try:
            new_dir = os.path.join(self.current_directory, directory)
            new_dir = os.path.abspath(new_dir)

            if os.path.isdir(new_dir):
                self.current_directory = new_dir
                obs = Observation(
                    data={
                        "action": "cd",
                        "directory": self.current_directory,
                        "success": True,
                    }
                )
            else:
                obs = Observation(
                    data={
                        "action": "cd",
                        "error": f"Directory not found: {directory}",
                        "success": False,
                    },
                    metadata={"error": True},
                )

            return obs

        except Exception as e:
            obs = Observation(
                data={
                    "action": "cd",
                    "error": str(e),
                    "success": False,
                },
                metadata={"error": True},
            )
            return obs

    def _print_working_directory(self) -> Observation:
        """Get current working directory"""
        obs = Observation(
            data={
                "action": "pwd",
                "directory": self.current_directory,
            }
        )

        return obs

    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        if not self.safe_mode:
            return True

        command_lower = command.lower().strip()

        # Check blocked commands
        for blocked in self.blocked_commands:
            if command_lower.startswith(blocked) or f" {blocked}" in command_lower:
                return False

        # In safe mode, only allow whitelisted commands
        base_command = command_lower.split()[0] if command_lower else ""
        return base_command in self.safe_commands

    def get_available_actions(self) -> List[str]:
        """Get available CLI actions"""
        return ["execute", "cd", "pwd"]

    def get_observation_space(self) -> Dict[str, Any]:
        """Describe CLI observation space"""
        return {
            "stdout": "Command standard output",
            "stderr": "Command standard error",
            "exit_code": "Command exit code",
            "directory": "Current working directory",
            "success": "Whether command succeeded",
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current CLI status"""
        return {
            "directory": self.current_directory,
            "last_command": self.last_command,
            "safe_mode": self.safe_mode,
            "steps": self.state.step_count,
        }
