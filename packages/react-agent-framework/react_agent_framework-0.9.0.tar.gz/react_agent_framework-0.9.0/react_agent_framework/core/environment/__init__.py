"""
Environment system for agent interaction

Environments define:
- Observation space: What the agent can see
- Action space: What the agent can do
- State management: Current environment state
- Reward system: Optional feedback mechanism
"""

from react_agent_framework.core.environment.base import (
    BaseEnvironment,
    EnvironmentState,
    Action,
    Observation,
)
from react_agent_framework.core.environment.web import WebEnvironment
from react_agent_framework.core.environment.cli import CLIEnvironment
from react_agent_framework.core.environment.file import FileEnvironment

__all__ = [
    "BaseEnvironment",
    "EnvironmentState",
    "Action",
    "Observation",
    "WebEnvironment",
    "CLIEnvironment",
    "FileEnvironment",
]
