"""
MCP Client - Manages connections to MCP servers
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""

    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    name: Optional[str] = None


@dataclass
class MCPTool:
    """Represents a tool from an MCP server"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: int


class MCPClient:
    """
    Client for connecting to and managing MCP servers

    Allows ReactAgent to:
    - Connect to multiple MCP servers
    - Discover available tools
    - Execute tool calls
    """

    def __init__(self):
        """Initialize MCP client"""
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP package not installed. Install with: pip install mcp"
            )

        self._servers: Dict[int, Dict[str, Any]] = {}
        self._next_server_id = 0
        self._tools_cache: Dict[int, List[MCPTool]] = {}

    async def connect_server(
        self,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
    ) -> int:
        """
        Connect to an MCP server

        Args:
            command: Server command to execute
            args: Command arguments
            env: Environment variables
            name: Optional server name for identification

        Returns:
            Server ID for future operations
        """
        server_id = self._next_server_id
        self._next_server_id += 1

        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env,
            )

            # Connect using stdio client
            stdio_transport = await stdio_client(server_params)
            read_stream, write_stream = stdio_transport

            # Create session
            session = ClientSession(read_stream, write_stream)

            # Initialize session
            await session.initialize()

            # Store server info
            self._servers[server_id] = {
                "config": MCPServerConfig(command, args, env, name),
                "session": session,
                "read_stream": read_stream,
                "write_stream": write_stream,
            }

            logger.info(
                f"Connected to MCP server (ID: {server_id}, "
                f"Name: {name or 'unnamed'}, Command: {command})"
            )

            # List and cache tools
            await self._refresh_tools(server_id)

            return server_id

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise

    async def disconnect_server(self, server_id: int) -> None:
        """
        Disconnect from an MCP server

        Args:
            server_id: Server ID to disconnect
        """
        if server_id not in self._servers:
            raise ValueError(f"Server {server_id} not found")

        try:
            server_info = self._servers[server_id]

            # Close streams
            await server_info["read_stream"].aclose()
            await server_info["write_stream"].aclose()

            # Remove from storage
            del self._servers[server_id]
            if server_id in self._tools_cache:
                del self._tools_cache[server_id]

            logger.info(f"Disconnected from MCP server (ID: {server_id})")

        except Exception as e:
            logger.error(f"Error disconnecting from server {server_id}: {e}")
            raise

    async def _refresh_tools(self, server_id: int) -> None:
        """
        Refresh tool list from server

        Args:
            server_id: Server ID to refresh
        """
        if server_id not in self._servers:
            raise ValueError(f"Server {server_id} not found")

        try:
            session = self._servers[server_id]["session"]

            # List available tools
            tools_response = await session.list_tools()

            # Convert to MCPTool objects
            tools = []
            for tool in tools_response.tools:
                mcp_tool = MCPTool(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema,
                    server_id=server_id,
                )
                tools.append(mcp_tool)

            # Cache tools
            self._tools_cache[server_id] = tools

            logger.info(
                f"Refreshed {len(tools)} tools from server {server_id}"
            )

        except Exception as e:
            logger.error(f"Error refreshing tools from server {server_id}: {e}")
            raise

    async def list_tools(self, server_id: Optional[int] = None) -> List[MCPTool]:
        """
        List available tools

        Args:
            server_id: Optional server ID to filter (None = all servers)

        Returns:
            List of available tools
        """
        if server_id is not None:
            if server_id not in self._servers:
                raise ValueError(f"Server {server_id} not found")
            return self._tools_cache.get(server_id, [])

        # Return tools from all servers
        all_tools = []
        for tools in self._tools_cache.values():
            all_tools.extend(tools)
        return all_tools

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any], server_id: Optional[int] = None
    ) -> Any:
        """
        Call a tool on an MCP server

        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments
            server_id: Optional server ID (if None, searches all servers)

        Returns:
            Tool result
        """
        # Find the tool
        target_server_id = None

        if server_id is not None:
            # Check specific server
            if server_id not in self._servers:
                raise ValueError(f"Server {server_id} not found")
            tools = self._tools_cache.get(server_id, [])
            if any(t.name == tool_name for t in tools):
                target_server_id = server_id
        else:
            # Search all servers
            for sid, tools in self._tools_cache.items():
                if any(t.name == tool_name for t in tools):
                    target_server_id = sid
                    break

        if target_server_id is None:
            raise ValueError(f"Tool '{tool_name}' not found on any connected server")

        try:
            session = self._servers[target_server_id]["session"]

            # Call the tool
            result = await session.call_tool(tool_name, arguments)

            logger.info(
                f"Called tool '{tool_name}' on server {target_server_id}"
            )

            return result

        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}': {e}")
            raise

    def get_server_info(self, server_id: int) -> Dict[str, Any]:
        """
        Get information about a connected server

        Args:
            server_id: Server ID

        Returns:
            Server information dictionary
        """
        if server_id not in self._servers:
            raise ValueError(f"Server {server_id} not found")

        server_info = self._servers[server_id]
        config = server_info["config"]

        return {
            "id": server_id,
            "name": config.name or "unnamed",
            "command": config.command,
            "args": config.args,
            "num_tools": len(self._tools_cache.get(server_id, [])),
        }

    def list_servers(self) -> List[Dict[str, Any]]:
        """
        List all connected servers

        Returns:
            List of server information dictionaries
        """
        return [self.get_server_info(sid) for sid in self._servers.keys()]

    async def close_all(self) -> None:
        """Disconnect from all servers"""
        server_ids = list(self._servers.keys())
        for server_id in server_ids:
            try:
                await self.disconnect_server(server_id)
            except Exception as e:
                logger.error(f"Error closing server {server_id}: {e}")


# Synchronous wrapper for easier integration
class MCPClientSync:
    """
    Synchronous wrapper for MCPClient

    Provides sync methods that run async operations in event loop
    """

    def __init__(self):
        """Initialize sync MCP client"""
        self._client = MCPClient()
        self._loop = None

    def _get_loop(self):
        """Get or create event loop"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    def connect_server(
        self,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
    ) -> int:
        """Connect to MCP server (sync)"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._client.connect_server(command, args, env, name)
        )

    def disconnect_server(self, server_id: int) -> None:
        """Disconnect from MCP server (sync)"""
        loop = self._get_loop()
        loop.run_until_complete(self._client.disconnect_server(server_id))

    def list_tools(self, server_id: Optional[int] = None) -> List[MCPTool]:
        """List tools (sync)"""
        loop = self._get_loop()
        return loop.run_until_complete(self._client.list_tools(server_id))

    def call_tool(
        self, tool_name: str, arguments: Dict[str, Any], server_id: Optional[int] = None
    ) -> Any:
        """Call tool (sync)"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._client.call_tool(tool_name, arguments, server_id)
        )

    def get_server_info(self, server_id: int) -> Dict[str, Any]:
        """Get server info"""
        return self._client.get_server_info(server_id)

    def list_servers(self) -> List[Dict[str, Any]]:
        """List servers"""
        return self._client.list_servers()

    def close_all(self) -> None:
        """Close all connections (sync)"""
        loop = self._get_loop()
        loop.run_until_complete(self._client.close_all())
