"""
Provider factory for creating providers from strings or objects
"""

from typing import Union, Optional
from urllib.parse import urlparse

from react_agent_framework.providers.base import BaseLLMProvider
from react_agent_framework.providers.openai_provider import OpenAIProvider
from react_agent_framework.providers.anthropic_provider import AnthropicProvider
from react_agent_framework.providers.google_provider import GoogleProvider
from react_agent_framework.providers.ollama_provider import OllamaProvider


def create_provider(
    provider: Union[str, BaseLLMProvider], api_key: Optional[str] = None
) -> BaseLLMProvider:
    """
    Create a provider from a string or return existing provider

    Supports URL-style strings:
    - "openai://gpt-4o-mini"
    - "anthropic://claude-3-5-sonnet-20241022"
    - "google://gemini-1.5-flash"
    - "ollama://llama3.2"

    Or simple model names (defaults to OpenAI):
    - "gpt-4o-mini" -> OpenAIProvider
    - "claude-3-5-sonnet" -> AnthropicProvider (if starts with claude)
    - "gemini-1.5-flash" -> GoogleProvider (if starts with gemini)

    Args:
        provider: Provider string or BaseLLMProvider instance
        api_key: API key for the provider (optional)

    Returns:
        BaseLLMProvider instance

    Examples:
        >>> create_provider("openai://gpt-4")
        >>> create_provider("anthropic://claude-3-5-sonnet-20241022")
        >>> create_provider("gpt-4o-mini")  # Defaults to OpenAI
    """

    # If already a provider instance, return it
    if isinstance(provider, BaseLLMProvider):
        return provider

    # Parse string provider
    if "://" in provider:
        # URL-style: "provider://model"
        parsed = urlparse(provider)
        provider_type = parsed.scheme.lower()
        model = parsed.netloc + parsed.path

        if provider_type == "openai":
            return OpenAIProvider(model=model, api_key=api_key)
        elif provider_type == "anthropic":
            return AnthropicProvider(model=model, api_key=api_key)
        elif provider_type == "google":
            return GoogleProvider(model=model, api_key=api_key)
        elif provider_type == "ollama":
            # For Ollama, path might contain base_url
            base_url = parsed.hostname or "http://localhost:11434"
            if parsed.port:
                base_url = f"http://{parsed.hostname}:{parsed.port}"
            return OllamaProvider(model=model, base_url=base_url)
        else:
            raise ValueError(
                f"Unknown provider type: {provider_type}. "
                f"Supported: openai, anthropic, google, ollama"
            )
    else:
        # Simple model name - detect provider
        model = provider.lower()

        if model.startswith("claude"):
            return AnthropicProvider(model=provider, api_key=api_key)
        elif model.startswith("gemini"):
            return GoogleProvider(model=provider, api_key=api_key)
        elif model.startswith(("llama", "mistral", "phi", "codellama")):
            return OllamaProvider(model=provider)
        else:
            # Default to OpenAI
            return OpenAIProvider(model=provider, api_key=api_key)
