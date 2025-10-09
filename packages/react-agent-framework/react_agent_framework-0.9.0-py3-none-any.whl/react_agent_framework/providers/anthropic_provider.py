"""
Anthropic (Claude) provider implementation
"""

import os
from typing import List, Optional

from react_agent_framework.providers.base import BaseLLMProvider, Message


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic provider for Claude models

    Supports: claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku, etc.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Anthropic provider

        Args:
            model: Anthropic model name
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env if not provided)
            **kwargs: Additional Anthropic client parameters
        """
        super().__init__(model, api_key, **kwargs)

        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    def generate(self, messages: List[Message], temperature: float = 0, **kwargs) -> str:
        """Generate response using Anthropic API"""

        # Separate system message from conversation
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({"role": msg.role, "content": msg.content})

        # Anthropic requires at least one user message
        if not conversation_messages or conversation_messages[0]["role"] != "user":
            conversation_messages.insert(0, {"role": "user", "content": "Hello"})

        max_tokens = kwargs.pop("max_tokens", 4096)

        response = self.client.messages.create(
            model=self.model,
            system=system_message or "",
            messages=conversation_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return response.content[0].text

    def get_model_name(self) -> str:
        """Return Anthropic model name"""
        return self.model

    def __repr__(self) -> str:
        return f"AnthropicProvider(model='{self.model}')"
