"""
Simple in-memory storage (no persistence)
"""

from collections import deque
from typing import List, Dict, Any, Optional
from react_agent_framework.core.memory.base import BaseMemory, MemoryMessage


class SimpleMemory(BaseMemory):
    """
    Simple in-memory buffer

    - No persistence (data lost when program ends)
    - Fast access
    - Sequential search (no semantic search)
    - Good for short sessions
    """

    def __init__(
        self,
        max_messages: Optional[int] = 100,
        session_id: Optional[str] = None,
    ):
        """
        Initialize simple memory

        Args:
            max_messages: Maximum messages to store (default 100)
            session_id: Session identifier
        """
        super().__init__(max_messages=max_messages, session_id=session_id)
        self._messages: deque = deque(maxlen=max_messages)

    def add(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add message to memory"""
        message = MemoryMessage(
            content=content,
            role=role,
            metadata=metadata or {},
        )
        self._messages.append(message)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """
        Search messages (simple keyword matching)

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            Messages containing query keywords
        """
        query_lower = query.lower()
        results = []

        for msg in self._messages:
            # Apply filters
            if filters:
                if not self._matches_filters(msg, filters):
                    continue

            # Simple keyword matching
            if query_lower in msg.content.lower():
                results.append(msg)

            if len(results) >= top_k:
                break

        return results

    def get_recent(
        self,
        n: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """Get most recent messages"""
        messages = list(self._messages)

        if filters:
            messages = [msg for msg in messages if self._matches_filters(msg, filters)]

        # Return most recent n messages
        return messages[-n:] if len(messages) > n else messages

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear all messages"""
        self._messages.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if not self._messages:
            return {
                "total_messages": 0,
                "session_id": self.session_id,
                "max_messages": self.max_messages,
            }

        return {
            "total_messages": len(self._messages),
            "session_id": self.session_id,
            "max_messages": self.max_messages,
            "oldest_message": self._messages[0].timestamp.isoformat(),
            "newest_message": self._messages[-1].timestamp.isoformat(),
            "roles": self._get_role_counts(),
        }

    def _matches_filters(self, message: MemoryMessage, filters: Dict[str, Any]) -> bool:
        """Check if message matches filters"""
        for key, value in filters.items():
            if key == "role":
                if message.role != value:
                    return False
            elif key in message.metadata:
                if message.metadata[key] != value:
                    return False
            else:
                return False
        return True

    def _get_role_counts(self) -> Dict[str, int]:
        """Count messages by role"""
        counts: Dict[str, int] = {}
        for msg in self._messages:
            counts[msg.role] = counts.get(msg.role, 0) + 1
        return counts

    def get_all(self) -> List[MemoryMessage]:
        """Get all messages"""
        return list(self._messages)

    def __len__(self) -> int:
        """Return number of messages"""
        return len(self._messages)

    def __repr__(self) -> str:
        return f"SimpleMemory(messages={len(self._messages)}, max={self.max_messages})"
