"""
ObjectiveTracker for managing multiple objectives
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from react_agent_framework.core.objectives.objective import (
    Objective,
    ObjectiveStatus,
    ObjectivePriority,
)


class ObjectiveTracker:
    """
    Tracks and manages multiple objectives

    Features:
    - Priority-based sorting
    - Automatic status updates
    - Progress tracking
    - Dependency management
    - Reporting and statistics
    """

    def __init__(self):
        """Initialize objective tracker"""
        self.objectives: Dict[str, Objective] = {}

    def add(self, objective: Objective) -> str:
        """
        Add objective to tracker

        Args:
            objective: Objective to add

        Returns:
            Objective ID
        """
        self.objectives[objective.id] = objective
        return objective.id

    def create(
        self,
        goal: str,
        success_criteria: Optional[List[str]] = None,
        priority: str = "medium",
        deadline: Optional[datetime] = None,
        **kwargs,
    ) -> Objective:
        """
        Create and add new objective

        Args:
            goal: The goal description
            success_criteria: List of success criteria
            priority: Priority level (low, medium, high, critical)
            deadline: Optional deadline
            **kwargs: Additional Objective parameters

        Returns:
            Created objective
        """
        objective = Objective(
            goal=goal,
            success_criteria=success_criteria or [],
            priority=priority,
            deadline=deadline,
            **kwargs,
        )
        self.add(objective)
        return objective

    def get(self, objective_id: str) -> Optional[Objective]:
        """Get objective by ID"""
        return self.objectives.get(objective_id)

    def remove(self, objective_id: str) -> bool:
        """
        Remove objective

        Args:
            objective_id: Objective ID to remove

        Returns:
            True if removed, False if not found
        """
        if objective_id in self.objectives:
            del self.objectives[objective_id]
            return True
        return False

    def get_active(self) -> List[Objective]:
        """Get all active (in progress) objectives"""
        return [obj for obj in self.objectives.values() if obj.is_active]

    def get_pending(self) -> List[Objective]:
        """Get all pending objectives"""
        return [obj for obj in self.objectives.values() if obj.status == ObjectiveStatus.PENDING]

    def get_completed(self) -> List[Objective]:
        """Get all completed objectives"""
        return [obj for obj in self.objectives.values() if obj.is_completed]

    def get_failed(self) -> List[Objective]:
        """Get all failed objectives"""
        return [obj for obj in self.objectives.values() if obj.is_failed]

    def get_overdue(self) -> List[Objective]:
        """Get all overdue objectives"""
        return [obj for obj in self.objectives.values() if obj.is_overdue]

    def get_by_priority(
        self, priority: ObjectivePriority, include_completed: bool = False
    ) -> List[Objective]:
        """
        Get objectives by priority

        Args:
            priority: Priority level
            include_completed: Include completed objectives

        Returns:
            List of objectives with specified priority
        """
        objectives = [obj for obj in self.objectives.values() if obj.priority == priority]

        if not include_completed:
            objectives = [obj for obj in objectives if not obj.is_completed]

        return objectives

    def get_next(self) -> Optional[Objective]:
        """
        Get next objective to work on based on priority

        Priority order: CRITICAL > HIGH > MEDIUM > LOW
        Within same priority, sorts by deadline (earliest first)

        Returns:
            Next objective or None
        """
        pending = self.get_pending()
        if not pending:
            return None

        # Sort by priority (critical first) then by deadline
        priority_order = {
            ObjectivePriority.CRITICAL: 0,
            ObjectivePriority.HIGH: 1,
            ObjectivePriority.MEDIUM: 2,
            ObjectivePriority.LOW: 3,
        }

        def sort_key(obj: Objective):
            priority_value = priority_order.get(obj.priority, 999)
            deadline_value = obj.deadline.timestamp() if obj.deadline else float("inf")
            return (priority_value, deadline_value)

        pending.sort(key=sort_key)
        return pending[0]

    def start_next(self) -> Optional[Objective]:
        """
        Start next pending objective

        Returns:
            Started objective or None
        """
        next_obj = self.get_next()
        if next_obj:
            next_obj.start()
        return next_obj

    def complete(self, objective_id: str, note: Optional[str] = None) -> bool:
        """
        Mark objective as completed

        Args:
            objective_id: Objective ID
            note: Optional completion note

        Returns:
            True if completed, False if not found
        """
        obj = self.get(objective_id)
        if obj:
            obj.complete(note)
            return True
        return False

    def fail(self, objective_id: str, reason: str) -> bool:
        """
        Mark objective as failed

        Args:
            objective_id: Objective ID
            reason: Failure reason

        Returns:
            True if failed, False if not found
        """
        obj = self.get(objective_id)
        if obj:
            obj.fail(reason)
            return True
        return False

    def update_progress(
        self, objective_id: str, progress: float, note: Optional[str] = None
    ) -> bool:
        """
        Update objective progress

        Args:
            objective_id: Objective ID
            progress: Progress value (0.0 to 1.0)
            note: Optional note

        Returns:
            True if updated, False if not found
        """
        obj = self.get(objective_id)
        if obj:
            obj.update_progress(progress, note)
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get tracker statistics

        Returns:
            Dictionary with statistics
        """
        total = len(self.objectives)
        completed = len(self.get_completed())
        failed = len(self.get_failed())
        active = len(self.get_active())
        pending = len(self.get_pending())
        overdue = len(self.get_overdue())

        completion_rate = (completed / total * 100) if total > 0 else 0.0
        failure_rate = (failed / total * 100) if total > 0 else 0.0

        # Calculate average progress
        avg_progress = (
            sum(obj.progress for obj in self.objectives.values()) / total if total > 0 else 0.0
        )

        return {
            "total_objectives": total,
            "completed": completed,
            "failed": failed,
            "active": active,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": f"{completion_rate:.1f}%",
            "failure_rate": f"{failure_rate:.1f}%",
            "average_progress": f"{avg_progress:.1%}",
        }

    def get_summary(self) -> str:
        """
        Get human-readable summary

        Returns:
            Summary string
        """
        stats = self.get_stats()
        lines = [
            "📊 Objectives Summary",
            "=" * 50,
            f"Total: {stats['total_objectives']}",
            f"✅ Completed: {stats['completed']} ({stats['completion_rate']})",
            f"❌ Failed: {stats['failed']} ({stats['failure_rate']})",
            f"🔄 Active: {stats['active']}",
            f"⏳ Pending: {stats['pending']}",
            f"⚠️  Overdue: {stats['overdue']}",
            f"📈 Average Progress: {stats['average_progress']}",
        ]

        # Add next objective
        next_obj = self.get_next()
        if next_obj:
            lines.append("")
            lines.append(f"🎯 Next: {next_obj.goal}")

        return "\n".join(lines)

    def clear_completed(self) -> int:
        """
        Remove all completed objectives

        Returns:
            Number of objectives removed
        """
        completed_ids = [obj.id for obj in self.get_completed()]
        for obj_id in completed_ids:
            self.remove(obj_id)
        return len(completed_ids)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "objectives": {obj_id: obj.to_dict() for obj_id, obj in self.objectives.items()},
            "stats": self.get_stats(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectiveTracker":
        """Create from dictionary"""
        tracker = cls()
        objectives_data = data.get("objectives", {})
        for obj_data in objectives_data.values():
            objective = Objective.from_dict(obj_data)
            tracker.add(objective)
        return tracker

    def __len__(self) -> int:
        """Return number of objectives"""
        return len(self.objectives)

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"ObjectiveTracker(total={stats['total_objectives']}, active={stats['active']}, completed={stats['completed']})"
