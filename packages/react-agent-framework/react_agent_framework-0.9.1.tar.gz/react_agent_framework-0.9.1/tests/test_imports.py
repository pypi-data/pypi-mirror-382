"""
Test module imports and __all__ exports
"""

import pytest


class TestBasicImports:
    """Test basic framework imports"""

    def test_import_react_agent(self):
        """Test ReactAgent can be imported"""
        from react_agent_framework import ReactAgent
        assert ReactAgent is not None

    def test_import_objective(self):
        """Test Objective can be imported"""
        from react_agent_framework import Objective
        assert Objective is not None

    def test_import_memory_classes(self):
        """Test memory classes can be imported"""
        from react_agent_framework import SimpleMemory, ChromaMemory, FAISSMemory
        assert SimpleMemory is not None
        assert ChromaMemory is not None
        assert FAISSMemory is not None

    def test_import_providers(self):
        """Test provider classes can be imported"""
        from react_agent_framework import (
            BaseLLMProvider,
            OpenAIProvider,
            AnthropicProvider,
            GoogleProvider,
            OllamaProvider,
        )
        assert BaseLLMProvider is not None
        assert OpenAIProvider is not None
        assert AnthropicProvider is not None
        assert GoogleProvider is not None
        assert OllamaProvider is not None


class TestModuleExports:
    """Test __all__ exports"""

    def test_all_exports(self):
        """Test __all__ contains expected exports"""
        import react_agent_framework

        expected_exports = {
            "ReactAgent",
            "Objective",
            "SimpleMemory",
            "ChromaMemory",
            "FAISSMemory",
            "BaseLLMProvider",
            "OpenAIProvider",
            "AnthropicProvider",
            "GoogleProvider",
            "OllamaProvider",
        }

        assert hasattr(react_agent_framework, "__all__")
        actual_exports = set(react_agent_framework.__all__)
        assert expected_exports == actual_exports

    def test_version_attribute(self):
        """Test __version__ is defined"""
        import react_agent_framework

        assert hasattr(react_agent_framework, "__version__")
        assert isinstance(react_agent_framework.__version__, str)
        assert len(react_agent_framework.__version__) > 0


class TestOptionalImports:
    """Test optional imports gracefully fail"""

    def test_faiss_import_without_package(self):
        """Test FAISS import doesn't crash without package"""
        try:
            from react_agent_framework.core.memory import FAISSMemory

            # If it imports, creating instance should fail gracefully
            with pytest.raises(ImportError, match="FAISS not installed"):
                FAISSMemory()
        except ImportError:
            # OK if the import itself fails
            pass

    def test_chroma_import_without_package(self):
        """Test ChromaDB import doesn't crash without package"""
        try:
            from react_agent_framework.core.memory import ChromaMemory

            # If it imports, creating instance should fail gracefully
            with pytest.raises(ImportError, match="ChromaDB not installed"):
                ChromaMemory()
        except ImportError:
            # OK if the import itself fails
            pass

    def test_mcp_client_import(self):
        """Test MCP client can be imported even without MCP package"""
        try:
            from react_agent_framework.mcp.client import MCPClientSync

            # Should be able to create client (but not use it without MCP)
            client = MCPClientSync()
            assert client is not None
        except ImportError:
            pytest.fail("MCP client should be importable even without MCP package")


class TestCoreModules:
    """Test core module imports"""

    def test_import_providers_module(self):
        """Test providers module imports"""
        from react_agent_framework import providers

        assert hasattr(providers, "OpenAIProvider")
        assert hasattr(providers, "AnthropicProvider")
        assert hasattr(providers, "GoogleProvider")
        assert hasattr(providers, "OllamaProvider")

    def test_import_memory_module(self):
        """Test memory module imports"""
        from react_agent_framework.core import memory

        assert hasattr(memory, "SimpleMemory")
        assert hasattr(memory, "ChromaMemory")
        assert hasattr(memory, "FAISSMemory")

    def test_import_objectives_module(self):
        """Test objectives module imports"""
        from react_agent_framework.core.objectives import Objective, ObjectiveTracker

        assert Objective is not None
        assert ObjectiveTracker is not None

    def test_import_tools_module(self):
        """Test tools module imports"""
        from react_agent_framework.tools import registry

        assert hasattr(registry, "ToolRegistry")


class TestExamples:
    """Test example files can be imported"""

    def test_import_examples_module(self):
        """Test examples module exists"""
        import react_agent_framework.examples

        assert react_agent_framework.examples is not None

    def test_examples_directory_exists(self):
        """Test examples directory has files"""
        import react_agent_framework.examples
        import os

        examples_dir = os.path.dirname(react_agent_framework.examples.__file__)
        assert os.path.exists(examples_dir)
        assert os.path.isdir(examples_dir)
