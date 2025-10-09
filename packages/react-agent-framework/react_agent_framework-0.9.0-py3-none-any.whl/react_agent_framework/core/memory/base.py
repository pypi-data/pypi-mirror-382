"""
Base memory interface for ReactAgent
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class MemoryMessage:
    """
    A message stored in memory

    Attributes:
        content: The message content
        role: Message role (user, assistant, system)
        timestamp: When the message was created
        metadata: Additional metadata (session_id, tags, etc)
    """

    content: str
    role: str = "user"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryMessage":
        """Create from dictionary"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            content=data["content"],
            role=data.get("role", "user"),
            timestamp=timestamp,
            metadata=data.get("metadata", {}),
        )


class BaseMemory(ABC):
    """
    Abstract base class for memory implementations

    All memory backends must implement these methods
    """

    def __init__(
        self,
        max_messages: Optional[int] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize memory

        Args:
            max_messages: Maximum number of messages to store (None = unlimited)
            session_id: Session identifier for multi-session support
        """
        self.max_messages = max_messages
        self.session_id = session_id or "default"

    @abstractmethod
    def add(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a message to memory

        Args:
            content: Message content
            role: Message role (user, assistant, system)
            metadata: Additional metadata
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """
        Search for relevant messages

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters (e.g., {"role": "user"})

        Returns:
            List of relevant messages
        """
        pass

    @abstractmethod
    def get_recent(
        self,
        n: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """
        Get most recent messages

        Args:
            n: Number of messages to retrieve
            filters: Metadata filters

        Returns:
            List of recent messages
        """
        pass

    @abstractmethod
    def clear(self, session_id: Optional[str] = None) -> None:
        """
        Clear memory

        Args:
            session_id: Clear specific session (None = current session)
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with stats (total_messages, sessions, etc)
        """
        pass

    def add_conversation(
        self,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a conversation pair (user + assistant)

        Args:
            user_message: User's message
            assistant_message: Assistant's response
            metadata: Shared metadata for both messages
        """
        self.add(user_message, role="user", metadata=metadata)
        self.add(assistant_message, role="assistant", metadata=metadata)

    def get_context(
        self,
        query: Optional[str] = None,
        max_tokens: int = 2000,
        use_search: bool = True,
    ) -> List[MemoryMessage]:
        """
        Get relevant context for current query

        Args:
            query: Current query (if None, just get recent)
            max_tokens: Approximate token limit
            use_search: Use semantic search if available

        Returns:
            List of relevant messages for context
        """
        if query and use_search:
            # Get semantically relevant messages
            messages = self.search(query, top_k=10)
        else:
            # Just get recent messages
            messages = self.get_recent(n=10)

        # Simple token estimation (4 chars ≈ 1 token)
        total_chars = 0
        context = []

        for msg in reversed(messages):
            msg_chars = len(msg.content)
            if total_chars + msg_chars > max_tokens * 4:
                break
            context.insert(0, msg)
            total_chars += msg_chars

        return context
