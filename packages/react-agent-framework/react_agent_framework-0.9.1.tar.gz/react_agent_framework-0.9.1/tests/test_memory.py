"""
Test memory classes
"""

import pytest
from react_agent_framework.core.memory import SimpleMemory
from react_agent_framework.core.memory.base import MemoryMessage
from react_agent_framework.providers.base import Message


class TestMemoryMessage:
    """Test MemoryMessage dataclass"""

    def test_message_creation(self):
        """Test MemoryMessage can be created"""
        msg = MemoryMessage(content="Hello", role="user")
        assert msg.content == "Hello"
        assert msg.role == "user"
        assert msg.timestamp is not None
        assert msg.metadata == {}

    def test_message_with_metadata(self):
        """Test MemoryMessage with metadata"""
        metadata = {"session_id": "123", "tag": "important"}
        msg = MemoryMessage(content="Test", role="assistant", metadata=metadata)
        assert msg.metadata == metadata

    def test_to_dict(self):
        """Test converting MemoryMessage to dict"""
        msg = MemoryMessage(content="Test", role="user")
        data = msg.to_dict()

        assert isinstance(data, dict)
        assert data["content"] == "Test"
        assert data["role"] == "user"
        assert "timestamp" in data
        assert "metadata" in data

    def test_from_dict(self):
        """Test creating MemoryMessage from dict"""
        data = {
            "content": "Test message",
            "role": "assistant",
            "metadata": {"key": "value"}
        }
        msg = MemoryMessage.from_dict(data)

        assert msg.content == "Test message"
        assert msg.role == "assistant"
        assert msg.metadata == {"key": "value"}


class TestSimpleMemory:
    """Test SimpleMemory implementation"""

    def test_initialization(self):
        """Test SimpleMemory can be initialized"""
        memory = SimpleMemory()
        assert memory is not None
        assert len(memory.get_all()) == 0

    def test_initialization_with_max_messages(self):
        """Test SimpleMemory with max_messages parameter"""
        memory = SimpleMemory(max_messages=5)
        assert memory.max_messages == 5

    def test_add_message(self):
        """Test adding a single message"""
        memory = SimpleMemory()
        memory.add("Hello", role="user")

        messages = memory.get_all()
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"

    def test_add_multiple_messages(self):
        """Test adding multiple messages"""
        memory = SimpleMemory()
        memory.add("Hello", role="user")
        memory.add("Hi there!", role="assistant")
        memory.add("How are you?", role="user")

        messages = memory.get_all()
        assert len(messages) == 3
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[2].role == "user"

    def test_max_messages_limit(self):
        """Test max_messages limit enforces FIFO behavior"""
        memory = SimpleMemory(max_messages=3)

        memory.add("Message 1", role="user")
        memory.add("Response 1", role="assistant")
        memory.add("Message 2", role="user")
        memory.add("Response 2", role="assistant")

        messages = memory.get_all()
        assert len(messages) == 3
        # Should keep last 3 messages (dropped "Message 1")
        assert messages[0].content == "Response 1"
        assert messages[1].content == "Message 2"
        assert messages[2].content == "Response 2"

    def test_get_recent(self):
        """Test getting recent messages"""
        memory = SimpleMemory()
        memory.add("Message 1", role="user")
        memory.add("Response 1", role="assistant")
        memory.add("Message 2", role="user")
        memory.add("Response 2", role="assistant")

        recent = memory.get_recent(2)
        assert len(recent) == 2
        assert recent[0].content == "Message 2"
        assert recent[1].content == "Response 2"

    def test_get_recent_more_than_available(self):
        """Test get_recent when requesting more messages than available"""
        memory = SimpleMemory()
        memory.add("Hello", role="user")

        recent = memory.get_recent(10)
        assert len(recent) == 1

    def test_clear(self):
        """Test clearing memory"""
        memory = SimpleMemory()
        memory.add("Hello", role="user")
        memory.add("Hi", role="assistant")

        assert len(memory.get_all()) == 2

        memory.clear()
        assert len(memory.get_all()) == 0

    def test_get_all_returns_list(self):
        """Test get_all returns a list"""
        memory = SimpleMemory()
        messages = memory.get_all()
        assert isinstance(messages, list)

    def test_message_format(self):
        """Test messages are stored as MemoryMessage objects"""
        memory = SimpleMemory()
        memory.add("Test message", role="user")

        messages = memory.get_all()
        msg = messages[0]

        assert isinstance(msg, MemoryMessage)
        assert hasattr(msg, "role")
        assert hasattr(msg, "content")
        assert hasattr(msg, "timestamp")
        assert hasattr(msg, "metadata")

    def test_system_message(self):
        """Test adding system messages"""
        memory = SimpleMemory()
        memory.add("You are a helpful assistant", role="system")
        memory.add("Hello", role="user")

        messages = memory.get_all()
        assert messages[0].role == "system"
        assert messages[1].role == "user"

    def test_memory_conversation_flow(self):
        """Test realistic conversation flow"""
        memory = SimpleMemory()

        # System message
        memory.add("You are helpful", role="system")

        # First exchange
        memory.add("What is 2+2?", role="user")
        memory.add("2+2 equals 4", role="assistant")

        # Second exchange
        memory.add("What about 3+3?", role="user")
        memory.add("3+3 equals 6", role="assistant")

        messages = memory.get_all()
        assert len(messages) == 5
        assert messages[0].role == "system"
        assert messages[-1].content == "3+3 equals 6"

    def test_add_conversation(self):
        """Test add_conversation helper method"""
        memory = SimpleMemory()
        memory.add_conversation("Hello", "Hi there!")

        messages = memory.get_all()
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi there!"

    def test_search_simple(self):
        """Test simple keyword search"""
        memory = SimpleMemory()
        memory.add("I like Python programming", role="user")
        memory.add("Python is great!", role="assistant")
        memory.add("What about Java?", role="user")

        results = memory.search("Python")
        assert len(results) == 2
        assert all("python" in msg.content.lower() for msg in results)

    def test_search_with_filters(self):
        """Test search with role filters"""
        memory = SimpleMemory()
        memory.add("User message with Python", role="user")
        memory.add("Assistant message with Python", role="assistant")
        memory.add("Another user message with Python", role="user")

        results = memory.search("Python", filters={"role": "user"})
        assert len(results) == 2
        assert all(msg.role == "user" for msg in results)

    def test_get_stats(self):
        """Test get_stats method"""
        memory = SimpleMemory(max_messages=100)
        memory.add("Message 1", role="user")
        memory.add("Response 1", role="assistant")

        stats = memory.get_stats()
        assert isinstance(stats, dict)
        assert stats["total_messages"] == 2
        assert stats["max_messages"] == 100
        assert "oldest_message" in stats
        assert "newest_message" in stats

    def test_len_method(self):
        """Test __len__ method"""
        memory = SimpleMemory()
        assert len(memory) == 0

        memory.add("Test", role="user")
        assert len(memory) == 1

        memory.add("Test 2", role="user")
        assert len(memory) == 2

    def test_repr_method(self):
        """Test __repr__ method"""
        memory = SimpleMemory(max_messages=50)
        memory.add("Test", role="user")

        repr_str = repr(memory)
        assert "SimpleMemory" in repr_str
        assert "1" in repr_str  # 1 message
        assert "50" in repr_str  # max 50


class TestChromaMemory:
    """Test ChromaDB memory (if available)"""

    def test_import_without_chromadb(self):
        """Test ChromaMemory import fails gracefully without package"""
        try:
            from react_agent_framework.core.memory import ChromaMemory

            # If import succeeds, creating instance should fail
            with pytest.raises(ImportError, match="ChromaDB not installed"):
                ChromaMemory()
        except ImportError:
            # OK if import itself fails
            pass


class TestFAISSMemory:
    """Test FAISS memory (if available)"""

    def test_import_without_faiss(self):
        """Test FAISSMemory import fails gracefully without package"""
        try:
            from react_agent_framework.core.memory import FAISSMemory

            # If import succeeds, creating instance should fail
            with pytest.raises(ImportError, match="FAISS not installed"):
                FAISSMemory()
        except ImportError:
            # OK if import itself fails
            pass


class TestMemoryIntegration:
    """Test memory integration with Message objects"""

    def test_simple_memory_with_message_objects(self):
        """Test SimpleMemory can work with Message objects"""
        memory = SimpleMemory()

        # Add using strings
        memory.add("Hello", role="user")

        # Get messages and convert to Message objects
        messages = memory.get_all()
        message_objects = [Message(role=m.role, content=m.content) for m in messages]

        assert len(message_objects) == 1
        assert isinstance(message_objects[0], Message)
        assert message_objects[0].role == "user"
        assert message_objects[0].content == "Hello"

    def test_memory_preserves_order(self):
        """Test memory preserves message order"""
        memory = SimpleMemory()

        expected_order = [
            ("user", "First"),
            ("assistant", "Second"),
            ("user", "Third"),
        ]

        for role, content in expected_order:
            memory.add(content, role=role)

        messages = memory.get_all()

        for i, (role, content) in enumerate(expected_order):
            assert messages[i].role == role
            assert messages[i].content == content

    def test_memory_empty_content(self):
        """Test memory handles empty content"""
        memory = SimpleMemory()
        memory.add("", role="user")

        messages = memory.get_all()
        assert len(messages) == 1
        assert messages[0].content == ""

    def test_memory_long_content(self):
        """Test memory handles long content"""
        memory = SimpleMemory()
        long_text = "A" * 10000
        memory.add(long_text, role="user")

        messages = memory.get_all()
        assert messages[0].content == long_text
        assert len(messages[0].content) == 10000

    def test_memory_special_characters(self):
        """Test memory handles special characters"""
        memory = SimpleMemory()
        special_text = "Hello\nWorld\t!\r\n"
        memory.add(special_text, role="user")

        messages = memory.get_all()
        assert messages[0].content == special_text

    def test_memory_unicode(self):
        """Test memory handles unicode characters"""
        memory = SimpleMemory()
        unicode_text = "Hello 世界 🌍 Привет"
        memory.add(unicode_text, role="user")

        messages = memory.get_all()
        assert messages[0].content == unicode_text

    def test_memory_metadata(self):
        """Test memory handles metadata"""
        memory = SimpleMemory()
        metadata = {"session_id": "abc123", "importance": "high"}
        memory.add("Important message", role="user", metadata=metadata)

        messages = memory.get_all()
        assert messages[0].metadata == metadata

    def test_get_context(self):
        """Test get_context method"""
        memory = SimpleMemory()
        memory.add("Hello", role="user")
        memory.add("Hi there!", role="assistant")
        memory.add("How are you?", role="user")

        context = memory.get_context(query="Hello", max_tokens=1000)
        assert isinstance(context, list)
        assert len(context) > 0
        assert all(isinstance(msg, MemoryMessage) for msg in context)
