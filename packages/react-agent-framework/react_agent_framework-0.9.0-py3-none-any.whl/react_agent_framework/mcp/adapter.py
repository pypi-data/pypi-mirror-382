"""
MCP Tool Adapter - Converts MCP tools to ReactAgent format
"""

from typing import Dict, Any, Callable, List
import json
import logging

from react_agent_framework.mcp.client import MCPClient, MCPClientSync, MCPTool

logger = logging.getLogger(__name__)


class MCPToolAdapter:
    """
    Adapts MCP tools to ReactAgent's tool system

    Converts MCP tool definitions to callable Python functions
    that can be registered with @agent.tool()
    """

    def __init__(self, mcp_client: MCPClientSync):
        """
        Initialize adapter

        Args:
            mcp_client: MCP client instance
        """
        self.mcp_client = mcp_client

    def create_tool_function(self, mcp_tool: MCPTool) -> Callable:
        """
        Create a callable function from an MCP tool

        Args:
            mcp_tool: MCP tool definition

        Returns:
            Callable function that executes the MCP tool
        """

        def tool_function(**kwargs) -> str:
            """Dynamically created MCP tool function"""
            try:
                # Call the MCP tool
                result = self.mcp_client.call_tool(
                    tool_name=mcp_tool.name,
                    arguments=kwargs,
                    server_id=mcp_tool.server_id,
                )

                # Convert result to string
                if hasattr(result, "content"):
                    # MCP ToolResult object
                    content = result.content
                    if isinstance(content, list):
                        # Multiple content items
                        text_parts = []
                        for item in content:
                            if hasattr(item, "text"):
                                text_parts.append(item.text)
                            elif isinstance(item, dict) and "text" in item:
                                text_parts.append(item["text"])
                            else:
                                text_parts.append(str(item))
                        return "\n".join(text_parts)
                    elif hasattr(content, "text"):
                        return content.text
                    elif isinstance(content, dict) and "text" in content:
                        return content["text"]
                    else:
                        return str(content)
                else:
                    return str(result)

            except Exception as e:
                error_msg = f"Error calling MCP tool '{mcp_tool.name}': {str(e)}"
                logger.error(error_msg)
                return error_msg

        # Set function metadata
        tool_function.__name__ = mcp_tool.name
        tool_function.__doc__ = mcp_tool.description or f"MCP tool: {mcp_tool.name}"

        return tool_function

    def get_tool_metadata(self, mcp_tool: MCPTool) -> Dict[str, Any]:
        """
        Extract tool metadata for ReactAgent

        Args:
            mcp_tool: MCP tool definition

        Returns:
            Dictionary with tool name and description
        """
        return {
            "name": mcp_tool.name,
            "description": mcp_tool.description or f"MCP tool: {mcp_tool.name}",
        }

    def register_tools_with_agent(self, agent, server_id: int = None) -> int:
        """
        Register MCP tools with a ReactAgent

        Args:
            agent: ReactAgent instance
            server_id: Optional server ID (None = all servers)

        Returns:
            Number of tools registered
        """
        # Get available tools
        mcp_tools = self.mcp_client.list_tools(server_id)

        registered_count = 0

        for mcp_tool in mcp_tools:
            try:
                # Create function
                tool_func = self.create_tool_function(mcp_tool)

                # Get metadata
                metadata = self.get_tool_metadata(mcp_tool)

                # Register with agent using decorator
                agent.tool(
                    name=metadata["name"], description=metadata["description"]
                )(tool_func)

                registered_count += 1
                logger.info(f"Registered MCP tool: {mcp_tool.name}")

            except Exception as e:
                logger.error(f"Failed to register tool '{mcp_tool.name}': {e}")

        return registered_count

    def create_tool_description(self, mcp_tool: MCPTool) -> str:
        """
        Create detailed tool description from MCP tool

        Args:
            mcp_tool: MCP tool definition

        Returns:
            Formatted tool description
        """
        desc = f"{mcp_tool.name}: {mcp_tool.description}"

        # Add parameter info if available
        if mcp_tool.input_schema:
            schema = mcp_tool.input_schema
            if "properties" in schema:
                params = []
                required = schema.get("required", [])

                for param_name, param_info in schema["properties"].items():
                    param_type = param_info.get("type", "any")
                    param_desc = param_info.get("description", "")
                    is_required = param_name in required

                    param_str = f"  - {param_name} ({param_type})"
                    if is_required:
                        param_str += " [required]"
                    if param_desc:
                        param_str += f": {param_desc}"

                    params.append(param_str)

                if params:
                    desc += "\n\nParameters:\n" + "\n".join(params)

        return desc

    def list_available_tools(self, server_id: int = None) -> List[str]:
        """
        List available MCP tools with descriptions

        Args:
            server_id: Optional server ID (None = all servers)

        Returns:
            List of tool descriptions
        """
        mcp_tools = self.mcp_client.list_tools(server_id)
        return [self.create_tool_description(tool) for tool in mcp_tools]


def create_mcp_tool_wrapper(
    mcp_client: MCPClientSync, tool_name: str, server_id: int = None
) -> Callable:
    """
    Convenience function to create a single MCP tool wrapper

    Args:
        mcp_client: MCP client instance
        tool_name: Name of tool to wrap
        server_id: Optional server ID

    Returns:
        Callable function that executes the MCP tool
    """
    # Find the tool
    tools = mcp_client.list_tools(server_id)
    mcp_tool = None

    for tool in tools:
        if tool.name == tool_name:
            mcp_tool = tool
            break

    if mcp_tool is None:
        raise ValueError(f"Tool '{tool_name}' not found")

    # Create adapter and function
    adapter = MCPToolAdapter(mcp_client)
    return adapter.create_tool_function(mcp_tool)
