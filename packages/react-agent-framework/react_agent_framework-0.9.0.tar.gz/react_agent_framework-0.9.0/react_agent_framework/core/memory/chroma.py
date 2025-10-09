"""
ChromaDB vector memory implementation
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from react_agent_framework.core.memory.base import BaseMemory, MemoryMessage


class ChromaMemory(BaseMemory):
    """
    Vector memory using ChromaDB

    Features:
    - Semantic search using embeddings
    - Persistent storage
    - Metadata filtering
    - Multiple embedding functions (OpenAI, sentence-transformers, etc)
    """

    def __init__(
        self,
        collection_name: str = "agent_memory",
        persist_directory: str = "./chroma_db",
        embedding_function: str = "default",
        embedding_model: Optional[str] = None,
        max_messages: Optional[int] = None,
        session_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize ChromaDB memory

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
            embedding_function: Type of embedding ("default", "openai", "sentence-transformers")
            embedding_model: Model name for embeddings
            max_messages: Maximum messages to store
            session_id: Session identifier
            api_key: API key for OpenAI embeddings
        """
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")

        super().__init__(max_messages=max_messages, session_id=session_id)

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )

        # Set up embedding function
        self.embedding_fn = self._get_embedding_function(
            embedding_function, embedding_model, api_key
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "ReactAgent memory storage"},
        )

    def _get_embedding_function(self, func_type: str, model: Optional[str], api_key: Optional[str]):
        """Get embedding function based on type"""
        if func_type == "openai":
            if not api_key:
                import os

                api_key = os.getenv("OPENAI_API_KEY")

            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name=model or "text-embedding-3-small",
            )

        elif func_type == "sentence-transformers":
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model or "all-MiniLM-L6-v2"
            )

        else:
            # Default embedding function
            return embedding_functions.DefaultEmbeddingFunction()

    def add(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add message to vector database"""
        message = MemoryMessage(
            content=content,
            role=role,
            metadata=metadata or {},
        )

        # Prepare metadata for Chroma
        chroma_metadata = {
            "role": role,
            "timestamp": message.timestamp.isoformat(),
            "session_id": self.session_id,
            **message.metadata,
        }

        # Add to collection
        self.collection.add(
            ids=[str(uuid.uuid4())],
            documents=[content],
            metadatas=[chroma_metadata],
        )

        # Check max_messages limit
        if self.max_messages:
            count = self.collection.count()
            if count > self.max_messages:
                # Remove oldest messages
                self._remove_oldest(count - self.max_messages)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """
        Semantic search using vector similarity

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            Most similar messages
        """
        # Build where filter
        where_filter = {"session_id": self.session_id}
        if filters:
            where_filter.update(filters)

        # Query collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
        )

        # Convert to MemoryMessage objects
        messages = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                timestamp_str = metadata.pop("timestamp", None)
                role = metadata.pop("role", "user")
                metadata.pop("session_id", None)

                timestamp = (
                    datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                )

                messages.append(
                    MemoryMessage(
                        content=doc,
                        role=role,
                        timestamp=timestamp,
                        metadata=metadata,
                    )
                )

        return messages

    def get_recent(
        self,
        n: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """Get most recent messages"""
        # Build where filter
        where_filter = {"session_id": self.session_id}
        if filters:
            where_filter.update(filters)

        # Get all matching messages
        results = self.collection.get(
            where=where_filter,
            limit=n if n else None,
        )

        # Convert to MemoryMessage objects
        messages = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                timestamp_str = metadata.pop("timestamp", None)
                role = metadata.pop("role", "user")
                metadata.pop("session_id", None)

                timestamp = (
                    datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                )

                messages.append(
                    MemoryMessage(
                        content=doc,
                        role=role,
                        timestamp=timestamp,
                        metadata=metadata,
                    )
                )

        # Sort by timestamp and return most recent
        messages.sort(key=lambda x: x.timestamp)
        return messages[-n:] if len(messages) > n else messages

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear messages from session"""
        target_session = session_id or self.session_id

        # Delete all documents with this session_id
        results = self.collection.get(
            where={"session_id": target_session},
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_count = self.collection.count()

        # Get session messages
        session_results = self.collection.get(
            where={"session_id": self.session_id},
        )

        session_count = len(session_results["ids"]) if session_results["ids"] else 0

        return {
            "total_messages": total_count,
            "session_messages": session_count,
            "session_id": self.session_id,
            "collection_name": self.collection_name,
            "max_messages": self.max_messages,
            "persist_directory": self.persist_directory,
        }

    def _remove_oldest(self, n: int) -> None:
        """Remove n oldest messages"""
        results = self.collection.get(
            where={"session_id": self.session_id},
        )

        if not results["ids"]:
            return

        # Sort by timestamp
        items = list(zip(results["ids"], results["metadatas"], results["documents"]))
        items.sort(key=lambda x: x[1].get("timestamp", ""))

        # Delete oldest n items
        ids_to_delete = [item[0] for item in items[:n]]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

    def delete_collection(self) -> None:
        """Delete entire collection (use with caution!)"""
        self.client.delete_collection(self.collection_name)

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"ChromaMemory(session_messages={stats['session_messages']}, total={stats['total_messages']})"
