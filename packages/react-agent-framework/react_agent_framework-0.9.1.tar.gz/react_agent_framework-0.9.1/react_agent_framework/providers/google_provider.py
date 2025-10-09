"""
Google (Gemini) provider implementation
"""

import os
from typing import List, Optional

from react_agent_framework.providers.base import BaseLLMProvider, Message


class GoogleProvider(BaseLLMProvider):
    """
    Google provider for Gemini models

    Supports: gemini-pro, gemini-1.5-pro, gemini-1.5-flash, etc.
    """

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Google provider

        Args:
            model: Google model name
            api_key: Google API key (uses GOOGLE_API_KEY env if not provided)
            **kwargs: Additional Google client parameters
        """
        super().__init__(model, api_key, **kwargs)

        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Google Generative AI package not installed. Install with: pip install google-generativeai"
            )

        genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.genai = genai
        self.model_instance = genai.GenerativeModel(self.model)

    def generate(self, messages: List[Message], temperature: float = 0, **kwargs) -> str:
        """Generate response using Google Gemini API"""

        # Convert messages to Gemini format
        # Gemini uses "model" and "user" roles
        gemini_messages = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg.content]})
            else:  # user
                gemini_messages.append({"role": "user", "parts": [msg.content]})

        # Configure generation
        generation_config = {
            "temperature": temperature,
            **kwargs,
        }

        # Create chat or generate
        if len(gemini_messages) > 1:
            chat = self.model_instance.start_chat(history=gemini_messages[:-1])
            response = chat.send_message(
                gemini_messages[-1]["parts"][0],
                generation_config=generation_config,
            )
        else:
            prompt = system_instruction or ""
            if gemini_messages:
                prompt += "\n\n" + gemini_messages[0]["parts"][0]

            response = self.model_instance.generate_content(
                prompt, generation_config=generation_config
            )

        return response.text

    def get_model_name(self) -> str:
        """Return Google model name"""
        return self.model

    def __repr__(self) -> str:
        return f"GoogleProvider(model='{self.model}')"
