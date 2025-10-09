"""
List directory tool
"""

from pathlib import Path
from react_agent_framework.tools.base import BaseTool
from react_agent_framework.tools.registry import register_tool


@register_tool
class ListDirectory(BaseTool):
    """
    List contents of a directory
    """

    name = "list"
    description = (
        "List files and directories in a path. Input: directory path (default: current directory)"
    )
    category = "filesystem"

    def __init__(self, show_hidden: bool = False, **kwargs):
        """
        Initialize list directory tool

        Args:
            show_hidden: If True, shows hidden files (starting with .)
        """
        super().__init__(**kwargs)
        self.show_hidden = show_hidden

    def execute(self, input_text: str) -> str:
        """
        List directory contents

        Args:
            input_text: Directory path (empty for current directory)

        Returns:
            Formatted list of files and directories
        """
        dir_path = input_text.strip() if input_text.strip() else "."

        try:
            path = Path(dir_path).expanduser().resolve()

            # Check if directory exists
            if not path.exists():
                return f"Error: Directory not found: {dir_path}"

            # Check if it's a directory
            if not path.is_dir():
                return f"Error: Not a directory: {dir_path}"

            # List contents
            items = []
            for item in sorted(path.iterdir()):
                # Skip hidden files if needed
                if not self.show_hidden and item.name.startswith("."):
                    continue

                item_type = "DIR " if item.is_dir() else "FILE"
                size = ""
                if item.is_file():
                    size_bytes = item.stat().st_size
                    if size_bytes < 1024:
                        size = f"{size_bytes}B"
                    elif size_bytes < 1024 * 1024:
                        size = f"{size_bytes / 1024:.1f}KB"
                    else:
                        size = f"{size_bytes / 1024 / 1024:.1f}MB"

                items.append(f"{item_type} {item.name:<50} {size}")

            if not items:
                return f"Directory is empty: {dir_path}"

            header = f"Contents of {path}:\n" + "=" * 70 + "\n"
            return header + "\n".join(items)

        except PermissionError:
            return f"Error: Permission denied: {dir_path}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
