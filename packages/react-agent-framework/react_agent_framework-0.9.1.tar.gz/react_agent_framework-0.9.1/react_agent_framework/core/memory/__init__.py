"""
Memory system for ReactAgent

Supports multiple memory backends:
- SimpleMemory: In-memory buffer (no persistence)
- ChromaMemory: Vector database with semantic search
- FAISSMemory: High-performance vector search
"""

from react_agent_framework.core.memory.base import BaseMemory, MemoryMessage
from react_agent_framework.core.memory.simple import SimpleMemory

__all__ = [
    "BaseMemory",
    "MemoryMessage",
    "SimpleMemory",
]

# Optional imports for vector databases
try:
    from react_agent_framework.core.memory.chroma import ChromaMemory  # noqa: F401

    __all__.append("ChromaMemory")
except ImportError:
    pass

try:
    from react_agent_framework.core.memory.faiss import FAISSMemory  # noqa: F401

    __all__.append("FAISSMemory")
except ImportError:
    pass
