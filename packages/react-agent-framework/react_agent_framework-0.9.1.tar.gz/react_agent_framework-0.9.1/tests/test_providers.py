"""
Test provider classes and factory
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from react_agent_framework.providers.base import BaseLLMProvider, Message
from react_agent_framework.providers.factory import create_provider
from react_agent_framework.providers.openai_provider import OpenAIProvider
from react_agent_framework.providers.ollama_provider import OllamaProvider


class TestMessage:
    """Test Message dataclass"""

    def test_message_creation(self):
        """Test Message can be created"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_roles(self):
        """Test different message roles"""
        roles = ["system", "user", "assistant"]
        for role in roles:
            msg = Message(role=role, content="test")
            assert msg.role == role


class TestBaseLLMProvider:
    """Test BaseLLMProvider abstract class"""

    def test_cannot_instantiate_base_provider(self):
        """Test BaseLLMProvider cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseLLMProvider(model="test")

    def test_base_provider_init_signature(self):
        """Test base provider requires model parameter"""

        class TestProvider(BaseLLMProvider):
            def generate(self, messages, temperature=0, **kwargs):
                return "test"

            def get_model_name(self):
                return self.model

        provider = TestProvider(model="test-model", api_key="key123")
        assert provider.model == "test-model"
        assert provider.api_key == "key123"


class TestProviderFactory:
    """Test create_provider factory function"""

    def test_return_existing_provider(self):
        """Test factory returns existing provider instance"""
        provider = Mock(spec=BaseLLMProvider)
        result = create_provider(provider)
        assert result is provider

    @patch('openai.OpenAI')
    def test_openai_url_style(self, mock_openai):
        """Test creating OpenAI provider with URL style"""
        provider = create_provider("openai://gpt-4o-mini", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o-mini"

    def test_ollama_url_style(self):
        """Test creating Ollama provider with URL style"""
        provider = create_provider("ollama://llama3.2")
        assert isinstance(provider, OllamaProvider)
        assert provider.model == "llama3.2"

    def test_llama_auto_detection(self):
        """Test Llama model auto-detection"""
        provider = create_provider("llama3.2")
        assert isinstance(provider, OllamaProvider)

    def test_mistral_auto_detection(self):
        """Test Mistral model auto-detection"""
        provider = create_provider("mistral")
        assert isinstance(provider, OllamaProvider)

    @patch('openai.OpenAI')
    def test_default_to_openai(self, mock_openai):
        """Test unknown models default to OpenAI"""
        provider = create_provider("gpt-4o-mini", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

    def test_api_key_passed_through(self):
        """Test API key is passed to provider"""
        provider = create_provider("openai://gpt-4", api_key="test-key")
        assert provider.api_key == "test-key"

    def test_unknown_provider_type_error(self):
        """Test error on unknown provider type"""
        with pytest.raises(ValueError, match="Unknown provider type"):
            create_provider("unknown://model")


class TestOpenAIProvider:
    """Test OpenAI provider"""

    @patch('openai.OpenAI')
    def test_provider_initialization(self, mock_openai):
        """Test OpenAI provider can be initialized"""
        provider = OpenAIProvider(model="gpt-4o-mini", api_key="test-key")
        assert provider.model == "gpt-4o-mini"
        assert provider.api_key == "test-key"

    @patch('openai.OpenAI')
    def test_get_model_name(self, mock_openai):
        """Test get_model_name returns correct model"""
        provider = OpenAIProvider(model="gpt-4o-mini")
        assert provider.get_model_name() == "gpt-4o-mini"

    @patch('openai.OpenAI')
    def test_generate_method(self, mock_openai):
        """Test generate method calls OpenAI API"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated response"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(model="gpt-4o-mini", api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        result = provider.generate(messages, temperature=0.7)

        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_repr(self, mock_openai):
        """Test __repr__ method"""
        provider = OpenAIProvider(model="gpt-4o-mini")
        assert "OpenAIProvider" in repr(provider)
        assert "gpt-4o-mini" in repr(provider)


class TestOllamaProvider:
    """Test Ollama provider"""

    def test_provider_initialization(self):
        """Test Ollama provider can be initialized"""
        provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")
        assert provider.model == "llama3.2"
        assert provider.base_url == "http://localhost:11434"

    def test_default_base_url(self):
        """Test default base URL"""
        provider = OllamaProvider(model="llama3.2")
        assert provider.base_url == "http://localhost:11434"

    def test_get_model_name(self):
        """Test get_model_name returns correct model"""
        provider = OllamaProvider(model="llama3.2")
        assert provider.get_model_name() == "llama3.2"

    @patch('requests.post')
    def test_generate_method(self, mock_post):
        """Test generate method calls Ollama API"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Ollama response"}
        }
        mock_post.return_value = mock_response

        provider = OllamaProvider(model="llama3.2")
        messages = [Message(role="user", content="Hello")]

        result = provider.generate(messages, temperature=0.8)

        assert result == "Ollama response"
        mock_post.assert_called_once()

        # Verify the request was made correctly
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/chat"
        assert call_args[1]["json"]["model"] == "llama3.2"
        assert call_args[1]["json"]["options"]["temperature"] == 0.8

    @patch('requests.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        provider = OllamaProvider(model="llama3.2")
        messages = [Message(role="user", content="Hello")]

        with pytest.raises(ConnectionError, match="Cannot connect to Ollama"):
            provider.generate(messages)

    @patch('requests.post')
    def test_timeout_error(self, mock_post):
        """Test timeout error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        provider = OllamaProvider(model="llama3.2")
        messages = [Message(role="user", content="Hello")]

        with pytest.raises(TimeoutError, match="Ollama request timed out"):
            provider.generate(messages)

    @patch('requests.get')
    def test_list_models(self, mock_get):
        """Test list_models method"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2"},
                {"name": "mistral"},
                {"name": "phi"}
            ]
        }
        mock_get.return_value = mock_response

        provider = OllamaProvider(model="llama3.2")
        models = provider.list_models()

        assert models == ["llama3.2", "mistral", "phi"]
        mock_get.assert_called_once()

    def test_repr(self):
        """Test __repr__ method"""
        provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")
        assert "OllamaProvider" in repr(provider)
        assert "llama3.2" in repr(provider)
        assert "http://localhost:11434" in repr(provider)


class TestProviderFactoryOptional:
    """Test factory with optional providers (anthropic, google)"""

    def test_anthropic_url_style_import_error(self):
        """Test Anthropic creation raises ImportError if package not installed"""
        with patch.dict('sys.modules', {'anthropic': None}):
            # This should trigger the ImportError from AnthropicProvider.__init__
            # We expect ImportError, not crash
            with pytest.raises(ImportError, match="Anthropic package not installed"):
                create_provider("anthropic://claude-3-5-sonnet-20241022")

    def test_google_url_style_import_error(self):
        """Test Google creation raises ImportError if package not installed"""
        with patch.dict('sys.modules', {'google.generativeai': None}):
            # This should trigger the ImportError from GoogleProvider.__init__
            # We expect ImportError, not crash
            with pytest.raises(ImportError, match="Google Generative AI package not installed"):
                create_provider("google://gemini-1.5-flash")

    def test_claude_auto_detection_import_error(self):
        """Test Claude auto-detection raises ImportError if package not installed"""
        with patch.dict('sys.modules', {'anthropic': None}):
            with pytest.raises(ImportError, match="Anthropic package not installed"):
                create_provider("claude-3-5-sonnet-20241022")

    def test_gemini_auto_detection_import_error(self):
        """Test Gemini auto-detection raises ImportError if package not installed"""
        with patch.dict('sys.modules', {'google': None}):
            with pytest.raises(ImportError):
                create_provider("gemini-1.5-flash")


class TestProviderMessageConversion:
    """Test message conversion for different providers"""

    @patch('openai.OpenAI')
    def test_openai_message_conversion(self, mock_openai):
        """Test OpenAI converts messages correctly"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "response"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(model="gpt-4o-mini")
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi"),
            Message(role="user", content="How are you?"),
        ]

        provider.generate(messages)

        # Verify messages were passed correctly
        call_args = mock_client.chat.completions.create.call_args
        api_messages = call_args[1]["messages"]
        assert len(api_messages) == 4
        assert api_messages[0]["role"] == "system"
        assert api_messages[1]["role"] == "user"

    @patch('requests.post')
    def test_ollama_message_conversion(self, mock_post):
        """Test Ollama converts messages correctly"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"content": "response"}}
        mock_post.return_value = mock_response

        provider = OllamaProvider(model="llama3.2")
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi"),
        ]

        provider.generate(messages)

        # Verify messages were converted to Ollama format
        call_args = mock_post.call_args
        ollama_messages = call_args[1]["json"]["messages"]
        assert len(ollama_messages) == 2
        assert ollama_messages[0]["role"] == "user"
        assert ollama_messages[0]["content"] == "Hello"
