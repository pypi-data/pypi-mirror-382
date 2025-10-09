"""
FAISS vector memory implementation for high-performance similarity search
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

try:
    import faiss
    import numpy as np

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None
    np = None  # type: ignore

from react_agent_framework.core.memory.base import BaseMemory, MemoryMessage


class FAISSMemory(BaseMemory):
    """
    Vector memory using FAISS (Facebook AI Similarity Search)

    Features:
    - Very fast similarity search
    - Support for large-scale datasets
    - Multiple index types (Flat, IVF, HNSW)
    - Persistent storage
    - Requires manual embedding generation
    """

    def __init__(
        self,
        index_path: str = "./faiss_index",
        dimension: int = 1536,
        index_type: str = "Flat",
        embedding_model: str = "text-embedding-3-small",
        max_messages: Optional[int] = None,
        session_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize FAISS memory

        Args:
            index_path: Directory to save index and metadata
            dimension: Embedding dimension (1536 for OpenAI, 384 for MiniLM)
            index_type: FAISS index type ("Flat", "IVF", "HNSW")
            embedding_model: OpenAI embedding model
            max_messages: Maximum messages to store
            session_id: Session identifier
            api_key: OpenAI API key
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS not installed. Install with: pip install faiss-cpu (or faiss-gpu)"
            )

        super().__init__(max_messages=max_messages, session_id=session_id)

        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.dimension = dimension
        self.index_type = index_type
        self.embedding_model = embedding_model

        # Initialize OpenAI client for embeddings
        if not api_key:
            import os

            api_key = os.getenv("OPENAI_API_KEY")

        from openai import OpenAI

        self.openai_client = OpenAI(api_key=api_key)

        # Create or load FAISS index
        self.index = self._create_index()

        # Store messages and metadata separately
        self.messages: List[MemoryMessage] = []

        # Load existing data if available
        self._load()

    def _create_index(self):
        """Create FAISS index based on type"""
        if self.index_type == "Flat":
            # Exact search, slower but accurate
            return faiss.IndexFlatL2(self.dimension)

        elif self.index_type == "IVF":
            # Inverted file index, faster for large datasets
            quantizer = faiss.IndexFlatL2(self.dimension)
            return faiss.IndexIVFFlat(quantizer, self.dimension, 100)

        elif self.index_type == "HNSW":
            # Hierarchical Navigable Small World, very fast
            return faiss.IndexHNSWFlat(self.dimension, 32)

        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

    def _get_embedding(self, text: str) -> "np.ndarray":
        """Generate embedding for text using OpenAI"""
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model,
        )
        embedding = np.array(response.data[0].embedding, dtype=np.float32)
        return embedding

    def add(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add message to FAISS index"""
        message = MemoryMessage(
            content=content,
            role=role,
            metadata=metadata or {},
        )

        # Add session_id to metadata
        message.metadata["session_id"] = self.session_id

        # Generate embedding
        embedding = self._get_embedding(content)

        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))

        # Store message
        self.messages.append(message)

        # Check max_messages limit
        if self.max_messages and len(self.messages) > self.max_messages:
            self._remove_oldest()

        # Auto-save
        self._save()

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """
        Semantic search using FAISS

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            Most similar messages
        """
        if len(self.messages) == 0:
            return []

        # Generate query embedding
        query_embedding = self._get_embedding(query)

        # Search in FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), min(top_k * 2, len(self.messages))
        )

        # Get messages
        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(self.messages):
                msg = self.messages[idx]

                # Apply filters
                if filters:
                    if not self._matches_filters(msg, filters):
                        continue

                # Check session
                if msg.metadata.get("session_id") != self.session_id:
                    continue

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
        # Filter by session and other criteria
        filtered = []
        for msg in reversed(self.messages):
            if msg.metadata.get("session_id") != self.session_id:
                continue

            if filters and not self._matches_filters(msg, filters):
                continue

            filtered.append(msg)

            if len(filtered) >= n:
                break

        return list(reversed(filtered))

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear messages from session"""
        target_session = session_id or self.session_id

        # Filter out messages from target session
        new_messages = []
        for msg in self.messages:
            if msg.metadata.get("session_id") != target_session:
                new_messages.append(msg)

        # Rebuild index if messages were removed
        if len(new_messages) != len(self.messages):
            self.messages = new_messages
            self._rebuild_index()
            self._save()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        session_count = sum(
            1 for msg in self.messages if msg.metadata.get("session_id") == self.session_id
        )

        return {
            "total_messages": len(self.messages),
            "session_messages": session_count,
            "session_id": self.session_id,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "max_messages": self.max_messages,
            "index_path": str(self.index_path),
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

    def _remove_oldest(self) -> None:
        """Remove oldest message from current session"""
        # Find oldest message in current session
        oldest_idx = None
        oldest_time = None

        for i, msg in enumerate(self.messages):
            if msg.metadata.get("session_id") == self.session_id:
                if oldest_time is None or msg.timestamp < oldest_time:
                    oldest_time = msg.timestamp
                    oldest_idx = i

        if oldest_idx is not None:
            self.messages.pop(oldest_idx)
            self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from messages"""
        self.index = self._create_index()

        if self.messages:
            embeddings = []
            for msg in self.messages:
                emb = self._get_embedding(msg.content)
                embeddings.append(emb)

            embeddings_array = np.vstack(embeddings)
            self.index.add(embeddings_array)

    def _save(self) -> None:
        """Save index and messages to disk"""
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))

        # Save messages
        messages_data = [msg.to_dict() for msg in self.messages]
        with open(self.index_path / "messages.json", "w") as f:
            json.dump(messages_data, f, indent=2)

    def _load(self) -> None:
        """Load index and messages from disk"""
        index_file = self.index_path / "index.faiss"
        messages_file = self.index_path / "messages.json"

        if index_file.exists() and messages_file.exists():
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))

            # Load messages
            with open(messages_file, "r") as f:
                messages_data = json.load(f)
                self.messages = [MemoryMessage.from_dict(data) for data in messages_data]

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"FAISSMemory(session_messages={stats['session_messages']}, total={stats['total_messages']}, type={self.index_type})"
