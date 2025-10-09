"""
MCP Configuration System - Manage MCP server configurations
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""

    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    auto_connect: bool = True
    description: Optional[str] = None


class MCPConfigManager:
    """
    Manages MCP server configurations

    Supports:
    - Loading from JSON files
    - Saving configurations
    - Pre-configured popular servers
    """

    # Popular MCP servers
    POPULAR_SERVERS = {
        "filesystem": MCPServerConfig(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            description="Local filesystem access",
        ),
        "github": MCPServerConfig(
            name="github",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": ""},  # User must provide
            description="GitHub API access",
        ),
        "postgres": MCPServerConfig(
            name="postgres",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres"],
            env={"POSTGRES_CONNECTION_STRING": ""},  # User must provide
            description="PostgreSQL database access",
        ),
        "puppeteer": MCPServerConfig(
            name="puppeteer",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-puppeteer"],
            description="Browser automation",
        ),
        "slack": MCPServerConfig(
            name="slack",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-slack"],
            env={
                "SLACK_BOT_TOKEN": "",
                "SLACK_TEAM_ID": "",
            },
            description="Slack API access",
        ),
        "brave-search": MCPServerConfig(
            name="brave-search",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": ""},
            description="Brave Search API",
        ),
        "google-maps": MCPServerConfig(
            name="google-maps",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={"GOOGLE_MAPS_API_KEY": ""},
            description="Google Maps API",
        ),
    }

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize config manager

        Args:
            config_file: Path to JSON config file
        """
        self.config_file = Path(config_file) if config_file else None
        self.servers: Dict[str, MCPServerConfig] = {}

        # Load config if provided
        if self.config_file and self.config_file.exists():
            self.load_from_file(self.config_file)

    def load_from_file(self, file_path: str) -> None:
        """
        Load server configurations from JSON file

        Args:
            file_path: Path to JSON config file

        File format:
        {
            "servers": [
                {
                    "name": "filesystem",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    "auto_connect": true
                }
            ]
        }
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Config file not found: {file_path}")
                return

            with open(path, "r") as f:
                data = json.load(f)

            servers_data = data.get("servers", [])
            for server_data in servers_data:
                name = server_data.get("name")
                if not name:
                    logger.warning("Server config missing name, skipping")
                    continue

                config = MCPServerConfig(
                    name=name,
                    command=server_data["command"],
                    args=server_data["args"],
                    env=server_data.get("env"),
                    auto_connect=server_data.get("auto_connect", True),
                    description=server_data.get("description"),
                )

                self.servers[name] = config

            logger.info(f"Loaded {len(self.servers)} server configs from {file_path}")

        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def save_to_file(self, file_path: str) -> None:
        """
        Save server configurations to JSON file

        Args:
            file_path: Path to save config file
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            servers_data = []
            for config in self.servers.values():
                server_dict = asdict(config)
                servers_data.append(server_dict)

            data = {"servers": servers_data}

            with open(path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.servers)} server configs to {file_path}")

        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            raise

    def add_server(self, config: MCPServerConfig) -> None:
        """
        Add a server configuration

        Args:
            config: Server configuration
        """
        self.servers[config.name] = config
        logger.info(f"Added server config: {config.name}")

    def remove_server(self, name: str) -> None:
        """
        Remove a server configuration

        Args:
            name: Server name
        """
        if name in self.servers:
            del self.servers[name]
            logger.info(f"Removed server config: {name}")

    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """
        Get server configuration by name

        Args:
            name: Server name

        Returns:
            Server configuration or None
        """
        return self.servers.get(name)

    def list_servers(self) -> List[str]:
        """
        List configured server names

        Returns:
            List of server names
        """
        return list(self.servers.keys())

    def get_popular_server(self, name: str, **env_vars) -> MCPServerConfig:
        """
        Get a popular pre-configured server

        Args:
            name: Popular server name (filesystem, github, etc.)
            **env_vars: Environment variables to override

        Returns:
            Server configuration

        Example:
            config = manager.get_popular_server("github", GITHUB_TOKEN="ghp_...")
        """
        if name not in self.POPULAR_SERVERS:
            available = ", ".join(self.POPULAR_SERVERS.keys())
            raise ValueError(
                f"Unknown popular server '{name}'. Available: {available}"
            )

        # Get base config
        base_config = self.POPULAR_SERVERS[name]

        # Create new config with env overrides
        env = dict(base_config.env) if base_config.env else {}
        env.update(env_vars)

        return MCPServerConfig(
            name=base_config.name,
            command=base_config.command,
            args=base_config.args,
            env=env if env else None,
            auto_connect=base_config.auto_connect,
            description=base_config.description,
        )

    @classmethod
    def list_popular_servers(cls) -> Dict[str, str]:
        """
        List available popular servers

        Returns:
            Dictionary of {name: description}
        """
        return {
            name: config.description or "No description"
            for name, config in cls.POPULAR_SERVERS.items()
        }

    def create_example_config(self, file_path: str) -> None:
        """
        Create an example configuration file

        Args:
            file_path: Path to save example config
        """
        example_config = {
            "servers": [
                {
                    "name": "filesystem",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    "auto_connect": True,
                    "description": "Local filesystem access",
                },
                {
                    "name": "github",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {"GITHUB_TOKEN": "your-token-here"},
                    "auto_connect": False,
                    "description": "GitHub API access",
                },
            ]
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(example_config, f, indent=2)

        logger.info(f"Created example config at {file_path}")


def load_mcp_config(file_path: str) -> MCPConfigManager:
    """
    Convenience function to load MCP configuration

    Args:
        file_path: Path to config file

    Returns:
        Configured MCPConfigManager
    """
    manager = MCPConfigManager(file_path)
    return manager
