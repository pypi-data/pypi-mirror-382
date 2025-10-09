"""
MCP (Model Context Protocol) integration for ReactAgent

Allows agents to connect to MCP servers and use their tools dynamically.
"""

from react_agent_framework.mcp.client import MCPClient
from react_agent_framework.mcp.adapter import MCPToolAdapter

__all__ = [
    "MCPClient",
    "MCPToolAdapter",
]
