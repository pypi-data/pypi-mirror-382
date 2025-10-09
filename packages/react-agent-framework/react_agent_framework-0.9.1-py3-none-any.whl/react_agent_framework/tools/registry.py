"""
Tool registry for managing and discovering built-in tools
"""

from typing import Dict, List, Type, Optional
from react_agent_framework.tools.base import BaseTool


class ToolRegistry:
    """
    Registry for managing and discovering tools

    Provides methods to register, retrieve, and filter tools by category
    """

    _tools: Dict[str, Type[BaseTool]] = {}
    _instances: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """
        Register a tool class

        Args:
            tool_class: Tool class to register

        Returns:
            The registered tool class
        """
        # Create temporary instance to get metadata
        temp_instance = tool_class()
        full_name = temp_instance.get_full_name()

        cls._tools[full_name] = tool_class
        cls._tools[temp_instance.name] = tool_class  # Also register by simple name

        return tool_class

    @classmethod
    def get(cls, tool_name: str, **config) -> Optional[BaseTool]:
        """
        Get tool instance by name

        Args:
            tool_name: Tool name (e.g., "search.duckduckgo" or "duckduckgo")
            **config: Configuration for tool initialization

        Returns:
            Tool instance or None if not found
        """
        tool_class = cls._tools.get(tool_name)
        if not tool_class:
            return None

        # Return cached instance or create new one
        cache_key = f"{tool_name}:{str(sorted(config.items()))}"
        if cache_key not in cls._instances:
            cls._instances[cache_key] = tool_class(**config)

        return cls._instances[cache_key]

    @classmethod
    def get_by_category(cls, category: str) -> List[BaseTool]:
        """
        Get all tools in a category

        Args:
            category: Category name (e.g., "search", "filesystem")

        Returns:
            List of tool instances in the category
        """
        tools = []
        for tool_name, tool_class in cls._tools.items():
            if "." in tool_name:  # Skip simple name aliases
                temp = tool_class()
                if temp.category == category:
                    tools.append(temp)
        return tools

    @classmethod
    def list_all(cls) -> List[str]:
        """
        List all registered tool names

        Returns:
            List of tool names
        """
        return [name for name in cls._tools.keys() if "." in name]

    @classmethod
    def list_categories(cls) -> List[str]:
        """
        List all available categories

        Returns:
            List of unique categories
        """
        categories = set()
        for tool_name in cls._tools.keys():
            if "." in tool_name:
                category = tool_name.split(".")[0]
                categories.add(category)
        return sorted(list(categories))

    @classmethod
    def find_tools(cls, pattern: str) -> List[BaseTool]:
        """
        Find tools matching a pattern

        Patterns:
        - "search.*" - All search tools
        - "filesystem.read" - Specific tool
        - "*" - All tools

        Args:
            pattern: Search pattern

        Returns:
            List of matching tool instances
        """
        tools = []

        if pattern == "*":
            # Return all tools
            for tool_name in cls.list_all():
                tool = cls.get(tool_name)
                if tool:
                    tools.append(tool)
        elif pattern.endswith(".*"):
            # Category wildcard (e.g., "search.*")
            category = pattern[:-2]
            tools = cls.get_by_category(category)
        else:
            # Specific tool
            tool = cls.get(pattern)
            if tool:
                tools.append(tool)

        return tools

    @classmethod
    def clear(cls):
        """Clear all registered tools (useful for testing)"""
        cls._tools.clear()
        cls._instances.clear()


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """
    Decorator to register a tool class

    Usage:
        @register_tool
        class MyTool(BaseTool):
            ...
    """
    return ToolRegistry.register(tool_class)
