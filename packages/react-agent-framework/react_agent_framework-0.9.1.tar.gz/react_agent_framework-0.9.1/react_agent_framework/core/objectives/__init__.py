"""
Objectives system for goal-oriented agents

Enables agents to track and pursue specific goals with priorities,
deadlines, and success criteria.
"""

from react_agent_framework.core.objectives.objective import Objective, ObjectiveStatus
from react_agent_framework.core.objectives.tracker import ObjectiveTracker

__all__ = [
    "Objective",
    "ObjectiveStatus",
    "ObjectiveTracker",
]
