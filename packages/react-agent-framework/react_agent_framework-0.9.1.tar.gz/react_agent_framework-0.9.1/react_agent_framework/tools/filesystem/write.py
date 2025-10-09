"""
Write file tool
"""

from pathlib import Path
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class WriteFile(BaseTool):
    """
    Write contents to a file

    Safe mode prevents overwriting sensitive files
    Format: path|||content
    """

    name = "write"
    description = 'Write contents to a file. Input: "path|||content" (use ||| separator)'
    category = "filesystem"

    def __init__(self, safe_mode: bool = True, sandbox_dir: str = None, **kwargs):
        """
        Initialize write file tool

        Args:
            safe_mode: If True, prevents writing to sensitive locations
            sandbox_dir: If set, restricts writes to this directory
        """
        super().__init__(**kwargs)
        self.safe_mode = safe_mode
        self.sandbox_dir = Path(sandbox_dir).resolve() if sandbox_dir else None

        # Sensitive patterns to block in safe mode
        self.blocked_patterns = [
            ".ssh",
            ".env",
            "password",
            "credentials",
            ".key",
            "private",
            "secret",
            "/etc/",
            "/sys/",
            "/proc/",
        ]

    def validate_input(self, input_text: str) -> bool:
        """Validate input format"""
        if not input_text or "|||" not in input_text:
            return False

        file_path = input_text.split("|||")[0].strip()

        if self.safe_mode:
            path_lower = file_path.lower()
            for pattern in self.blocked_patterns:
                if pattern in path_lower:
                    return False

        return True

    def execute(self, input_text: str) -> str:
        """
        Write file contents

        Args:
            input_text: Format "file_path|||content"

        Returns:
            Success message or error
        """
        if "|||" not in input_text:
            return 'Error: Invalid format. Use "path|||content"'

        parts = input_text.split("|||", 1)
        file_path = parts[0].strip()
        content = parts[1] if len(parts) > 1 else ""

        try:
            path = Path(file_path).expanduser().resolve()

            # Check sandbox restriction
            if self.sandbox_dir:
                if not str(path).startswith(str(self.sandbox_dir)):
                    return f"Error: Path outside sandbox directory: {self.sandbox_dir}"

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {file_path}"

        except PermissionError:
            return f"Error: Permission denied: {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
