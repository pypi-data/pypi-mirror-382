"""
Read file tool
"""

from pathlib import Path
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class ReadFile(BaseTool):
    """
    Read contents from a file

    Safe mode prevents reading sensitive files
    """

    name = "read"
    description = "Read contents from a file. Input: file path"
    category = "filesystem"

    def __init__(self, safe_mode: bool = True, max_size_mb: int = 10, **kwargs):
        """
        Initialize read file tool

        Args:
            safe_mode: If True, prevents reading sensitive files
            max_size_mb: Maximum file size in MB
        """
        super().__init__(**kwargs)
        self.safe_mode = safe_mode
        self.max_size_bytes = max_size_mb * 1024 * 1024

        # Sensitive patterns to block in safe mode
        self.blocked_patterns = [
            ".ssh",
            ".env",
            "password",
            "credentials",
            ".key",
            "private",
            "secret",
        ]

    def validate_input(self, input_text: str) -> bool:
        """Validate file path"""
        if not input_text or not input_text.strip():
            return False

        if self.safe_mode:
            path_lower = input_text.lower()
            for pattern in self.blocked_patterns:
                if pattern in path_lower:
                    return False

        return True

    def execute(self, input_text: str) -> str:
        """
        Read file contents

        Args:
            input_text: File path

        Returns:
            File contents or error message
        """
        file_path = input_text.strip()

        try:
            path = Path(file_path).expanduser().resolve()

            # Check if file exists
            if not path.exists():
                return f"Error: File not found: {file_path}"

            # Check if it's a file
            if not path.is_file():
                return f"Error: Not a file: {file_path}"

            # Check file size
            file_size = path.stat().st_size
            if file_size > self.max_size_bytes:
                return f"Error: File too large ({file_size / 1024 / 1024:.2f} MB). Max: {self.max_size_bytes / 1024 / 1024} MB"

            # Read file
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return content

        except UnicodeDecodeError:
            return f"Error: Cannot read file (binary or unsupported encoding): {file_path}"
        except PermissionError:
            return f"Error: Permission denied: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
