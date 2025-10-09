"""
Base environment interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Action:
    """
    Action taken in environment

    Represents what the agent does
    """

    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        params_str = ", ".join([f"{k}={v}" for k, v in self.parameters.items()])
        return f"Action({self.name}({params_str}))"


@dataclass
class Observation:
    """
    Observation from environment

    Represents what the agent sees
    """

    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_string(self) -> str:
        """Convert observation to string representation"""
        if isinstance(self.data, str):
            return self.data
        elif isinstance(self.data, dict):
            return "\n".join([f"{k}: {v}" for k, v in self.data.items()])
        elif isinstance(self.data, list):
            return "\n".join([str(item) for item in self.data])
        else:
            return str(self.data)


@dataclass
class EnvironmentState:
    """
    Current state of environment

    Tracks environment status and history
    """

    current_observation: Optional[Observation] = None
    action_history: List[Action] = field(default_factory=list)
    observation_history: List[Observation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    step_count: int = 0

    def add_step(self, action: Action, observation: Observation) -> None:
        """Record a step (action + observation)"""
        self.action_history.append(action)
        self.observation_history.append(observation)
        self.current_observation = observation
        self.step_count += 1


class BaseEnvironment(ABC):
    """
    Abstract base class for environments

    Defines interface for agent-environment interaction
    """

    def __init__(self, name: str = "Environment"):
        """
        Initialize environment

        Args:
            name: Environment name
        """
        self.name = name
        self.state = EnvironmentState()
        self._is_initialized = False

    @abstractmethod
    def reset(self) -> Observation:
        """
        Reset environment to initial state

        Returns:
            Initial observation
        """
        pass

    @abstractmethod
    def step(self, action: Action) -> Observation:
        """
        Execute action and return observation

        Args:
            action: Action to execute

        Returns:
            Resulting observation
        """
        pass

    @abstractmethod
    def get_available_actions(self) -> List[str]:
        """
        Get list of available action names

        Returns:
            List of action names
        """
        pass

    @abstractmethod
    def get_observation_space(self) -> Dict[str, Any]:
        """
        Describe what can be observed

        Returns:
            Description of observation space
        """
        pass

    def initialize(self) -> Observation:
        """
        Initialize environment (first-time setup)

        Returns:
            Initial observation
        """
        if not self._is_initialized:
            self._setup()
            self._is_initialized = True

        return self.reset()

    def _setup(self) -> None:
        """
        One-time setup (override if needed)

        Called before first reset
        """
        pass

    def get_state(self) -> EnvironmentState:
        """Get current environment state"""
        return self.state

    def get_current_observation(self) -> Optional[Observation]:
        """Get most recent observation"""
        return self.state.current_observation

    def get_history(self, n: int = 10) -> List[tuple[Action, Observation]]:
        """
        Get recent action-observation pairs

        Args:
            n: Number of recent steps to return

        Returns:
            List of (action, observation) tuples
        """
        history = list(zip(self.state.action_history, self.state.observation_history))
        return history[-n:] if len(history) > n else history

    def render(self) -> str:
        """
        Render current state as string

        Returns:
            Human-readable state representation
        """
        obs = self.get_current_observation()
        if obs is None:
            return f"{self.name}: Not initialized"

        return f"""{self.name}
Steps: {self.state.step_count}
Current observation:
{obs.to_string()}"""

    def close(self) -> None:
        """
        Cleanup environment resources

        Override if cleanup is needed
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', steps={self.state.step_count})"

    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
