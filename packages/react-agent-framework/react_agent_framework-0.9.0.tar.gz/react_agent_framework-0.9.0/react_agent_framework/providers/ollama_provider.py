"""
Ollama provider implementation (local LLMs)
"""

from typing import List
import requests

from react_agent_framework.providers.base import BaseLLMProvider, Message


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider for local LLMs

    Supports: llama3.2, llama3.1, mistral, codellama, phi, etc.
    Requires Ollama running locally: https://ollama.ai
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        """
        Initialize Ollama provider

        Args:
            model: Ollama model name (e.g., llama3.2, mistral, phi)
            base_url: Ollama server URL (default: http://localhost:11434)
            **kwargs: Additional Ollama parameters
        """
        super().__init__(model, api_key=None, **kwargs)
        self.base_url = base_url.rstrip("/")

    def generate(self, messages: List[Message], temperature: float = 0, **kwargs) -> str:
        """Generate response using Ollama API"""

        # Convert messages to Ollama format
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Prepare request
        data = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {"temperature": temperature, **self.extra_params},
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=data, timeout=120)
            response.raise_for_status()

            result = response.json()
            return result.get("message", {}).get("content", "")

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Ollama request timed out. Model '{self.model}' might be slow or not available."
            )
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

    def get_model_name(self) -> str:
        """Return Ollama model name"""
        return self.model

    def list_models(self) -> List[str]:
        """
        List available Ollama models

        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except Exception as e:
            raise RuntimeError(f"Failed to list Ollama models: {str(e)}")

    def __repr__(self) -> str:
        return f"OllamaProvider(model='{self.model}', base_url='{self.base_url}')"
