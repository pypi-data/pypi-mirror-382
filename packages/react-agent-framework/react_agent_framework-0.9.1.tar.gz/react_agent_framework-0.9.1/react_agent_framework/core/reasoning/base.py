"""
Base reasoning strategy interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime


@dataclass
class ReasoningResult:
    """
    Result of reasoning process

    Contains the final answer and execution trace
    """

    answer: str
    iterations: int
    success: bool
    trace: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> float:
        """Get execution duration in seconds"""
        if self.end_time is None:
            return 0.0
        delta = self.end_time - self.start_time
        return delta.total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "answer": self.answer,
            "iterations": self.iterations,
            "success": self.success,
            "trace": self.trace,
            "metadata": self.metadata,
            "duration": self.duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class BaseReasoning(ABC):
    """
    Abstract base class for reasoning strategies

    Each strategy implements a different approach to problem-solving
    """

    def __init__(
        self,
        max_iterations: int = 10,
        verbose: bool = False,
    ):
        """
        Initialize reasoning strategy

        Args:
            max_iterations: Maximum reasoning iterations
            verbose: Enable verbose output
        """
        self.max_iterations = max_iterations
        self.verbose = verbose

    @abstractmethod
    def reason(
        self,
        query: str,
        tools: Dict[str, Callable],
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
        **kwargs,
    ) -> ReasoningResult:
        """
        Execute reasoning strategy

        Args:
            query: The question/task
            tools: Dictionary of available tools
            tool_descriptions: Tool descriptions
            llm_generate: Function to call LLM
            system_prompt: System instructions
            **kwargs: Additional arguments

        Returns:
            ReasoningResult with answer and trace
        """
        pass

    def _log(self, message: str) -> None:
        """Log message if verbose"""
        if self.verbose:
            print(message)

    def _extract_thought_action(
        self, text: str
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract thought, action and input from text

        Standard format:
        Thought: [reasoning]
        Action: [tool name]
        Action Input: [input]
        """
        lines = text.strip().split("\n")
        thought = None
        action = None
        action_input = None

        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                action_input = line.replace("Action Input:", "").strip()

        return thought, action, action_input

    def _create_react_prompt(self, system_prompt: str, tools_desc: str, query: str) -> str:
        """
        Create standard ReAct-style prompt

        Args:
            system_prompt: Base system instructions
            tools_desc: Tools description
            query: User query

        Returns:
            Complete prompt
        """
        return f"""{system_prompt}

Available tools:
{tools_desc}

You must follow this format EXACTLY:

Thought: [your reasoning about what to do]
Action: [tool name]
Action Input: [input for the tool]

You will receive:
Observation: [action result]

Continue this cycle until you can answer. When you have the final answer, use:

Thought: [final reasoning]
Action: finish
Action Input: [your final answer]

IMPORTANT:
- Use EXACTLY the names "Thought:", "Action:", "Action Input:", "Observation:"
- Always start with a Thought
- Each action must have an input
- Use "finish" when you have the complete answer

Query: {query}"""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(max_iterations={self.max_iterations})"
