"""
Base tool interface for all built-in tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Base class for all tools

    All tools must inherit from this class and implement the execute method
    """

    # Class attributes to be defined by subclasses
    name: str = ""
    description: str = ""
    category: str = ""  # e.g., "search", "filesystem", "computation"

    def __init__(self, **kwargs):
        """
        Initialize tool with optional configuration

        Args:
            **kwargs: Tool-specific configuration
        """
        self.config = kwargs

    @abstractmethod
    def execute(self, input_text: str) -> str:
        """
        Execute the tool with given input

        Args:
            input_text: Input for the tool

        Returns:
            Tool execution result as string
        """
        pass

    def validate_input(self, input_text: str) -> bool:
        """
        Validate input before execution (optional)

        Args:
            input_text: Input to validate

        Returns:
            True if valid, False otherwise
        """
        return True

    def get_full_name(self) -> str:
        """Get full tool name with category"""
        return f"{self.category}.{self.name}" if self.category else self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "full_name": self.get_full_name(),
        }

    def __call__(self, input_text: str) -> str:
        """Make tool callable"""
        if not self.validate_input(input_text):
            return f"Invalid input for tool {self.name}"
        return self.execute(input_text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', category='{self.category}')"
