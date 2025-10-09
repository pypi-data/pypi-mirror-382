"""
Reasoning strategies for agents

Different approaches to problem-solving:
- ReAct: Reasoning + Acting (iterative)
- ReWOO: Reasoning Without Observation (plan-then-execute)
- Reflection: Self-critique and improvement
- PlanExecute: Detailed planning followed by execution
"""

from react_agent_framework.core.reasoning.base import BaseReasoning, ReasoningResult
from react_agent_framework.core.reasoning.react import ReActReasoning
from react_agent_framework.core.reasoning.rewoo import ReWOOReasoning
from react_agent_framework.core.reasoning.reflection import ReflectionReasoning
from react_agent_framework.core.reasoning.plan_execute import PlanExecuteReasoning

__all__ = [
    "BaseReasoning",
    "ReasoningResult",
    "ReActReasoning",
    "ReWOOReasoning",
    "ReflectionReasoning",
    "PlanExecuteReasoning",
]
