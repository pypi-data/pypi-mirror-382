"""
Delete file tool
"""

from pathlib import Path
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class DeleteFile(BaseTool):
    """
    Delete a file

    Safe mode prevents deleting sensitive files
    """

    name = "delete"
    description = "Delete a file. Input: file path"
    category = "filesystem"

    def __init__(self, safe_mode: bool = True, **kwargs):
        """
        Initialize delete file tool

        Args:
            safe_mode: If True, prevents deleting sensitive files
        """
        super().__init__(**kwargs)
        self.safe_mode = safe_mode

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
        Delete file

        Args:
            input_text: File path

        Returns:
            Success message or error
        """
        file_path = input_text.strip()

        try:
            path = Path(file_path).expanduser().resolve()

            # Check if file exists
            if not path.exists():
                return f"Error: File not found: {file_path}"

            # Check if it's a file
            if not path.is_file():
                return f"Error: Not a file (use with caution): {file_path}"

            # Delete file
            path.unlink()

            return f"Successfully deleted: {file_path}"

        except PermissionError:
            return f"Error: Permission denied: {file_path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
