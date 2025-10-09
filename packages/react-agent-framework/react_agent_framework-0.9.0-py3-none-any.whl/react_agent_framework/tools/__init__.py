"""
Built-in tools for ReactAgent

Import tools to auto-register them via the @register_tool decorator
"""

# Import all tools to trigger registration
from react_agent_framework.tools.search import DuckDuckGoSearch
from react_agent_framework.tools.filesystem import (
    ReadFile,
    WriteFile,
    ListDirectory,
    DeleteFile,
)
from react_agent_framework.tools.computation import Calculator, CodeExecutor, Shell

# Export registry
from react_agent_framework.tools.registry import ToolRegistry

__all__ = [
    "ToolRegistry",
    # Search tools
    "DuckDuckGoSearch",
    # Filesystem tools
    "ReadFile",
    "WriteFile",
    "ListDirectory",
    "DeleteFile",
    # Computation tools
    "Calculator",
    "CodeExecutor",
    "Shell",
]
