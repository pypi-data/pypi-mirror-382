"""
OpenAI provider implementation
"""

import os
from typing import List, Optional
import openai

from react_agent_framework.providers.base import BaseLLMProvider, Message


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider for GPT models

    Supports: gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini, gpt-3.5-turbo, etc.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize OpenAI provider

        Args:
            model: OpenAI model name
            api_key: OpenAI API key (uses OPENAI_API_KEY env if not provided)
            base_url: Custom base URL (for compatible APIs)
            organization: OpenAI organization ID
            **kwargs: Additional OpenAI client parameters
        """
        super().__init__(model, api_key, **kwargs)

        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url,
            organization=organization,
        )

    def generate(self, messages: List[Message], temperature: float = 0, **kwargs) -> str:
        """Generate response using OpenAI API"""

        # Convert Message objects to OpenAI format
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,  # type: ignore
            temperature=temperature,
            **kwargs,
        )

        return response.choices[0].message.content or ""

    def get_model_name(self) -> str:
        """Return OpenAI model name"""
        return self.model

    def __repr__(self) -> str:
        return f"OpenAIProvider(model='{self.model}')"
