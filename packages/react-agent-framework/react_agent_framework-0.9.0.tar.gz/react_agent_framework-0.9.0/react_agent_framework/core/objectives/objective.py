"""
Objective class for goal tracking
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class ObjectiveStatus(str, Enum):
    """Objective status enum"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ObjectivePriority(str, Enum):
    """Objective priority enum"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Objective:
    """
    Represents a goal or objective for the agent

    An objective defines what the agent should accomplish,
    with success criteria, priority, and optional deadline.

    Example:
        ```python
        objective = Objective(
            goal="Research AI agents and create summary",
            success_criteria=["Find 5+ papers", "Create markdown summary"],
            priority="high",
            deadline=datetime(2025, 10, 10)
        )
        ```
    """

    goal: str
    success_criteria: List[str] = field(default_factory=list)
    priority: ObjectivePriority = ObjectivePriority.MEDIUM
    status: ObjectiveStatus = ObjectiveStatus.PENDING
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sub_objectives: List["Objective"] = field(default_factory=list)
    parent_id: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0
    notes: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize objective ID"""
        if "id" not in self.metadata:
            import uuid

            self.metadata["id"] = str(uuid.uuid4())

        # Convert string enums to proper enums
        if isinstance(self.priority, str):
            self.priority = ObjectivePriority(self.priority)
        if isinstance(self.status, str):
            self.status = ObjectiveStatus(self.status)

    @property
    def id(self) -> str:
        """Get objective ID"""
        return self.metadata["id"]

    @property
    def is_completed(self) -> bool:
        """Check if objective is completed"""
        return self.status == ObjectiveStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if objective failed"""
        return self.status == ObjectiveStatus.FAILED

    @property
    def is_active(self) -> bool:
        """Check if objective is active (in progress)"""
        return self.status == ObjectiveStatus.IN_PROGRESS

    @property
    def is_overdue(self) -> bool:
        """Check if objective is past deadline"""
        if self.deadline is None:
            return False
        return datetime.now() > self.deadline and not self.is_completed

    def start(self) -> None:
        """Mark objective as in progress"""
        if self.status == ObjectiveStatus.PENDING:
            self.status = ObjectiveStatus.IN_PROGRESS
            self.metadata["started_at"] = datetime.now().isoformat()

    def complete(self, note: Optional[str] = None) -> None:
        """Mark objective as completed"""
        self.status = ObjectiveStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 1.0
        if note:
            self.notes.append(f"[COMPLETED] {note}")

    def fail(self, reason: str) -> None:
        """Mark objective as failed"""
        self.status = ObjectiveStatus.FAILED
        self.completed_at = datetime.now()
        self.notes.append(f"[FAILED] {reason}")

    def block(self, reason: str) -> None:
        """Mark objective as blocked"""
        self.status = ObjectiveStatus.BLOCKED
        self.notes.append(f"[BLOCKED] {reason}")

    def update_progress(self, progress: float, note: Optional[str] = None) -> None:
        """
        Update progress (0.0 to 1.0)

        Args:
            progress: Progress value between 0.0 and 1.0
            note: Optional note about the progress
        """
        self.progress = max(0.0, min(1.0, progress))
        if note:
            self.notes.append(f"[PROGRESS: {self.progress:.0%}] {note}")

        # Auto-complete if 100%
        if self.progress >= 1.0 and not self.is_completed:
            self.complete(note="Auto-completed at 100% progress")

    def add_sub_objective(self, objective: "Objective") -> None:
        """Add a sub-objective"""
        objective.parent_id = self.id
        self.sub_objectives.append(objective)

    def get_time_remaining(self) -> Optional[float]:
        """Get time remaining in seconds (None if no deadline)"""
        if self.deadline is None:
            return None
        delta = self.deadline - datetime.now()
        return delta.total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "goal": self.goal,
            "success_criteria": self.success_criteria,
            "priority": self.priority.value,
            "status": self.status.value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "metadata": self.metadata,
            "notes": self.notes,
            "sub_objectives": [obj.to_dict() for obj in self.sub_objectives],
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Objective":
        """Create from dictionary"""
        # Parse dates
        deadline = data.get("deadline")
        if deadline and isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)

        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        completed_at = data.get("completed_at")
        if completed_at and isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        # Parse sub-objectives
        sub_objectives = [cls.from_dict(obj_data) for obj_data in data.get("sub_objectives", [])]

        return cls(
            goal=data["goal"],
            success_criteria=data.get("success_criteria", []),
            priority=data.get("priority", "medium"),
            status=data.get("status", "pending"),
            deadline=deadline,
            created_at=created_at,
            completed_at=completed_at,
            metadata=data.get("metadata", {}),
            sub_objectives=sub_objectives,
            parent_id=data.get("parent_id"),
            progress=data.get("progress", 0.0),
            notes=data.get("notes", []),
        )

    def __repr__(self) -> str:
        status_emoji = {
            ObjectiveStatus.PENDING: "⏳",
            ObjectiveStatus.IN_PROGRESS: "🔄",
            ObjectiveStatus.COMPLETED: "✅",
            ObjectiveStatus.FAILED: "❌",
            ObjectiveStatus.BLOCKED: "🚫",
        }
        emoji = status_emoji.get(self.status, "")
        return f"{emoji} Objective(goal='{self.goal[:50]}...', status={self.status.value}, progress={self.progress:.0%})"
