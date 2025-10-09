"""
ReAct Agent Framework - Complete framework for creating intelligent agents

Features:
- Multi-provider support: OpenAI, Anthropic, Google, Ollama
- Built-in tools: Search, Filesystem, Computation
- Memory systems: Simple, ChromaDB, FAISS
- Objectives: Goal-oriented agent management
- Reasoning strategies: ReAct, ReWOO, Reflection, Plan-Execute
- Environments: Web, CLI, File system interaction
- MCP Integration: Connect to Model Context Protocol servers
"""

__version__ = "0.9.0"
__author__ = "Marcos"
__description__ = "Complete AI agent framework with MCP support, environments, multiple reasoning strategies, multi-provider support, built-in tools, memory, and objectives"

from react_agent_framework.core.react_agent import ReactAgent
from react_agent_framework.core.objectives.objective import Objective
from react_agent_framework.core.memory import SimpleMemory, ChromaMemory, FAISSMemory
from react_agent_framework.providers import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    OllamaProvider,
)

__all__ = [
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
]
