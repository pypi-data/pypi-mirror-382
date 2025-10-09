"""
Example: Using MCP (Model Context Protocol) servers with ReactAgent

This example demonstrates how to connect to MCP servers and use their tools.

Prerequisites:
    pip install mcp
    npm install -g @modelcontextprotocol/server-filesystem
"""

from react_agent_framework import ReactAgent

# Optional: Import MCP config manager for pre-configured servers
try:
    from react_agent_framework.mcp.config import MCPConfigManager
except ImportError:
    print("MCP not installed. Install with: pip install mcp")
    exit(1)


def example_filesystem_server():
    """
    Example: Connect to filesystem MCP server

    The filesystem server provides tools for reading/writing files
    """
    print("=" * 80)
    print("EXAMPLE 1: Filesystem MCP Server")
    print("=" * 80)

    # Create agent
    agent = ReactAgent(
        name="File Assistant",
        description="An assistant that can access local files via MCP",
        provider="gpt-4o-mini",
    )

    # Connect to filesystem MCP server
    # This will auto-register all filesystem tools
    server_id = agent.add_mcp_server(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        name="filesystem",
        auto_register=True,
    )

    print(f"\n✓ Connected to filesystem server (ID: {server_id})")

    # List available MCP tools
    print("\nAvailable MCP tools:")
    for tool_desc in agent.list_mcp_tools():
        print(f"  {tool_desc}")

    # Use the agent with MCP tools
    print("\n" + "#" * 80)
    print("Question: List the files in /tmp directory")
    print("#" * 80 + "\n")

    answer = agent.run("List the files in /tmp directory", verbose=True)

    print("\n" + "=" * 80)
    print(f"Answer: {answer}")
    print("=" * 80 + "\n")

    # Cleanup
    agent.disconnect_mcp_server(server_id)


def example_multiple_servers():
    """
    Example: Connect to multiple MCP servers simultaneously
    """
    print("=" * 80)
    print("EXAMPLE 2: Multiple MCP Servers")
    print("=" * 80)

    # Create agent
    agent = ReactAgent(
        name="Multi-Tool Assistant",
        description="An assistant with access to multiple MCP servers",
        provider="gpt-4o-mini",
    )

    # Connect to filesystem server
    fs_server_id = agent.add_mcp_server(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        name="filesystem",
    )

    print(f"\n✓ Connected to filesystem server (ID: {fs_server_id})")

    # Note: You can connect to more servers if you have them installed
    # For example:
    # github_server_id = agent.add_mcp_server(
    #     command="npx",
    #     args=["-y", "@modelcontextprotocol/server-github"],
    #     env={"GITHUB_TOKEN": "ghp_..."},
    #     name="github",
    # )

    # List all connected servers
    print("\nConnected MCP servers:")
    for server in agent.list_mcp_servers():
        print(f"  - {server['name']} (ID: {server['id']}, Tools: {server['num_tools']})")

    # List all available tools
    print("\nAll available MCP tools:")
    for tool_desc in agent.list_mcp_tools():
        print(f"  {tool_desc}")

    # Cleanup
    agent.disconnect_mcp_server(fs_server_id)


def example_with_config():
    """
    Example: Using pre-configured popular MCP servers
    """
    print("=" * 80)
    print("EXAMPLE 3: Pre-configured MCP Servers")
    print("=" * 80)

    # List popular servers
    print("\nPopular MCP servers:")
    for name, desc in MCPConfigManager.list_popular_servers().items():
        print(f"  - {name}: {desc}")

    # Get pre-configured server
    config_manager = MCPConfigManager()

    # Get filesystem server config
    fs_config = config_manager.get_popular_server("filesystem")

    print(f"\n✓ Using pre-configured server: {fs_config.name}")
    print(f"  Command: {fs_config.command}")
    print(f"  Args: {' '.join(fs_config.args)}")

    # Create agent and connect using config
    agent = ReactAgent(
        name="Config Assistant",
        description="An assistant using pre-configured MCP servers",
        provider="gpt-4o-mini",
    )

    server_id = agent.add_mcp_server(
        command=fs_config.command,
        args=fs_config.args,
        env=fs_config.env,
        name=fs_config.name,
    )

    print(f"\n✓ Connected to {fs_config.name} server")

    # Cleanup
    agent.disconnect_mcp_server(server_id)


def example_custom_mcp_server():
    """
    Example: Connect to a custom MCP server

    This demonstrates how to connect to your own MCP server
    """
    print("=" * 80)
    print("EXAMPLE 4: Custom MCP Server")
    print("=" * 80)

    agent = ReactAgent(
        name="Custom Assistant",
        description="An assistant with custom MCP server",
        provider="gpt-4o-mini",
    )

    # Example: Connect to a custom MCP server
    # Replace with your actual server command and args
    try:
        server_id = agent.add_mcp_server(
            command="python",
            args=["path/to/your/mcp_server.py"],
            name="custom",
            auto_register=True,
        )

        print(f"\n✓ Connected to custom server (ID: {server_id})")

        # Use the custom tools
        tools = agent.list_mcp_tools(server_id)
        print(f"\nCustom server provides {len(tools)} tools")

        # Cleanup
        agent.disconnect_mcp_server(server_id)

    except Exception as e:
        print(f"\n✗ Failed to connect to custom server: {e}")
        print("  (This is expected if you don't have a custom server)")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "MCP INTEGRATION EXAMPLES" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Check if MCP is available
    try:
        from react_agent_framework.mcp.client import MCP_AVAILABLE

        if not MCP_AVAILABLE:
            print("❌ MCP package not installed.")
            print("   Install with: pip install mcp")
            return
    except ImportError:
        print("❌ MCP package not installed.")
        print("   Install with: pip install mcp")
        return

    # Run examples
    try:
        # Example 1: Basic filesystem server
        example_filesystem_server()
        input("\nPress Enter to continue to next example...")

        # Example 2: Multiple servers
        example_multiple_servers()
        input("\nPress Enter to continue to next example...")

        # Example 3: Pre-configured servers
        example_with_config()
        input("\nPress Enter to continue to next example...")

        # Example 4: Custom server
        example_custom_mcp_server()

    except KeyboardInterrupt:
        print("\n\n✓ Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
