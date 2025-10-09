"""
Base provider interface for LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a message in the conversation"""

    role: str  # "system", "user", "assistant"
    content: str


class BaseLLMProvider(ABC):
    """
    Base class for all LLM providers

    All providers must implement this interface to work with ReactAgent
    """

    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the provider

        Args:
            model: Model name/identifier
            api_key: API key (if required)
            **kwargs: Provider-specific arguments
        """
        self.model = model
        self.api_key = api_key
        self.extra_params = kwargs

    @abstractmethod
    def generate(self, messages: List[Message], temperature: float = 0, **kwargs) -> str:
        """
        Generate a response from messages

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0-1)
            **kwargs: Additional generation parameters

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model name/identifier

        Returns:
            Model name string
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model}')"
