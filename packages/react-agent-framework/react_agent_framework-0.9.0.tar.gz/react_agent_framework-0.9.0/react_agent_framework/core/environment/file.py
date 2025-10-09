"""
File system environment

Allows agents to navigate and interact with file system
"""

import os
from typing import Dict, Any, List
from react_agent_framework.core.environment.base import (
    BaseEnvironment,
    Action,
    Observation,
)


class FileEnvironment(BaseEnvironment):
    """
    File system environment

    Enables file and directory operations
    """

    def __init__(
        self,
        root_directory: str = ".",
        safe_mode: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
    ):
        """
        Initialize file environment

        Args:
            root_directory: Root directory for operations
            safe_mode: Restrict operations to safe actions
            max_file_size: Maximum file size to read (bytes)
        """
        super().__init__(name="FileEnvironment")
        self.root_directory = os.path.abspath(root_directory)
        self.safe_mode = safe_mode
        self.max_file_size = max_file_size

        self.current_directory = self.root_directory

        # Sensitive file patterns
        self.sensitive_patterns = [
            ".ssh",
            ".env",
            "password",
            "secret",
            "credential",
            ".key",
            "token",
            "id_rsa",
        ]

    def reset(self) -> Observation:
        """Reset to root directory"""
        self.current_directory = self.root_directory

        # List initial directory contents
        contents = self._list_directory(self.current_directory)

        obs = Observation(
            data={
                "directory": self.current_directory,
                "contents": contents,
                "status": "ready",
            }
        )

        self.state.current_observation = obs
        return obs

    def step(self, action: Action) -> Observation:
        """
        Execute file action

        Supported actions:
        - list: List directory contents
        - read: Read file
        - write: Write file
        - create_dir: Create directory
        - navigate: Change directory
        - search: Search for files
        """
        action_name = action.name.lower()

        if action_name == "list":
            path = action.parameters.get("path", self.current_directory)
            return self._list_action(path)

        elif action_name == "read":
            filepath = action.parameters.get("filepath", "")
            return self._read_file(filepath)

        elif action_name == "write":
            filepath = action.parameters.get("filepath", "")
            content = action.parameters.get("content", "")
            return self._write_file(filepath, content)

        elif action_name == "create_dir":
            dirname = action.parameters.get("dirname", "")
            return self._create_directory(dirname)

        elif action_name == "navigate":
            path = action.parameters.get("path", "")
            return self._navigate(path)

        elif action_name == "search":
            pattern = action.parameters.get("pattern", "")
            return self._search_files(pattern)

        else:
            obs = Observation(
                data=f"Unknown action: {action_name}",
                metadata={"error": True},
            )
            self.state.add_step(action, obs)
            return obs

    def _list_action(self, path: str) -> Observation:
        """List directory contents"""
        try:
            full_path = self._resolve_path(path)

            if not os.path.isdir(full_path):
                obs = Observation(
                    data={"error": f"Not a directory: {path}"},
                    metadata={"error": True},
                )
                return obs

            contents = self._list_directory(full_path)

            obs = Observation(
                data={
                    "action": "list",
                    "path": full_path,
                    "contents": contents,
                    "count": len(contents),
                }
            )

            return obs

        except Exception as e:
            obs = Observation(
                data={"action": "list", "error": str(e)},
                metadata={"error": True},
            )
            return obs

    def _read_file(self, filepath: str) -> Observation:
        """Read file contents"""
        try:
            full_path = self._resolve_path(filepath)

            # Safety checks
            if self.safe_mode and self._is_sensitive_file(full_path):
                obs = Observation(
                    data={"error": "Access denied: Sensitive file"},
                    metadata={"error": True, "safe_mode": True},
                )
                return obs

            if not os.path.isfile(full_path):
                obs = Observation(
                    data={"error": f"File not found: {filepath}"},
                    metadata={"error": True},
                )
                return obs

            # Check file size
            file_size = os.path.getsize(full_path)
            if file_size > self.max_file_size:
                obs = Observation(
                    data={
                        "error": f"File too large: {file_size} bytes (max: {self.max_file_size})"
                    },
                    metadata={"error": True},
                )
                return obs

            # Read file
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            obs = Observation(
                data={
                    "action": "read",
                    "filepath": full_path,
                    "content": content,
                    "size": file_size,
                }
            )

            return obs

        except Exception as e:
            obs = Observation(
                data={"action": "read", "error": str(e)},
                metadata={"error": True},
            )
            return obs

    def _write_file(self, filepath: str, content: str) -> Observation:
        """Write content to file"""
        try:
            full_path = self._resolve_path(filepath)

            # Safety checks
            if self.safe_mode and self._is_sensitive_file(full_path):
                obs = Observation(
                    data={"error": "Access denied: Sensitive file"},
                    metadata={"error": True, "safe_mode": True},
                )
                return obs

            # Write file
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            obs = Observation(
                data={
                    "action": "write",
                    "filepath": full_path,
                    "bytes_written": len(content),
                    "success": True,
                }
            )

            return obs

        except Exception as e:
            obs = Observation(
                data={"action": "write", "error": str(e)},
                metadata={"error": True},
            )
            return obs

    def _create_directory(self, dirname: str) -> Observation:
        """Create directory"""
        try:
            full_path = self._resolve_path(dirname)

            os.makedirs(full_path, exist_ok=True)

            obs = Observation(
                data={
                    "action": "create_dir",
                    "path": full_path,
                    "success": True,
                }
            )

            return obs

        except Exception as e:
            obs = Observation(
                data={"action": "create_dir", "error": str(e)},
                metadata={"error": True},
            )
            return obs

    def _navigate(self, path: str) -> Observation:
        """Change current directory"""
        try:
            full_path = self._resolve_path(path)

            if not os.path.isdir(full_path):
                obs = Observation(
                    data={"error": f"Directory not found: {path}"},
                    metadata={"error": True},
                )
                return obs

            self.current_directory = full_path
            contents = self._list_directory(full_path)

            obs = Observation(
                data={
                    "action": "navigate",
                    "directory": full_path,
                    "contents": contents,
                }
            )

            return obs

        except Exception as e:
            obs = Observation(
                data={"action": "navigate", "error": str(e)},
                metadata={"error": True},
            )
            return obs

    def _search_files(self, pattern: str) -> Observation:
        """Search for files matching pattern"""
        try:
            import fnmatch

            matches = []

            for root, dirs, files in os.walk(self.current_directory):
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, self.current_directory)
                        matches.append(rel_path)

                # Limit results
                if len(matches) >= 100:
                    break

            obs = Observation(
                data={
                    "action": "search",
                    "pattern": pattern,
                    "matches": matches,
                    "count": len(matches),
                }
            )

            return obs

        except Exception as e:
            obs = Observation(
                data={"action": "search", "error": str(e)},
                metadata={"error": True},
            )
            return obs

    def _list_directory(self, path: str) -> List[Dict[str, Any]]:
        """List directory contents with metadata"""
        contents = []

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)

                item_info = {
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "path": item_path,
                }

                if not is_dir:
                    try:
                        item_info["size"] = os.path.getsize(item_path)
                    except (OSError, PermissionError):
                        item_info["size"] = 0

                contents.append(item_info)

        except Exception:
            pass

        return contents

    def _resolve_path(self, path: str) -> str:
        """Resolve path relative to current directory"""
        if os.path.isabs(path):
            return os.path.abspath(path)
        else:
            return os.path.abspath(os.path.join(self.current_directory, path))

    def _is_sensitive_file(self, filepath: str) -> bool:
        """Check if file is sensitive"""
        filepath_lower = filepath.lower()

        for pattern in self.sensitive_patterns:
            if pattern in filepath_lower:
                return True

        return False

    def get_available_actions(self) -> List[str]:
        """Get available file actions"""
        return ["list", "read", "write", "create_dir", "navigate", "search"]

    def get_observation_space(self) -> Dict[str, Any]:
        """Describe file observation space"""
        return {
            "directory": "Current directory path",
            "contents": "Directory contents list",
            "filepath": "File path",
            "content": "File content",
            "size": "File size in bytes",
            "matches": "Search results",
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current file system status"""
        return {
            "current_directory": self.current_directory,
            "root_directory": self.root_directory,
            "safe_mode": self.safe_mode,
            "steps": self.state.step_count,
        }
