"""
Memory system demonstration

Shows different memory backends: Simple, Chroma, FAISS
"""

from react_agent_framework import ReactAgent
from react_agent_framework.core.memory import SimpleMemory

# Import optional memory backends
try:
    from react_agent_framework.core.memory import ChromaMemory

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from react_agent_framework.core.memory import FAISSMemory

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


def demo_simple_memory():
    """Demo 1: Simple Memory (in-memory buffer)"""
    print("=" * 80)
    print("DEMO 1: SIMPLE MEMORY")
    print("=" * 80)

    agent = ReactAgent(
        name="Memory Assistant",
        provider="gpt-4o-mini",
        memory=SimpleMemory(max_messages=50),
    )

    # Built-in calculator
    @agent.tool()
    def calculate(expression: str) -> str:
        """Calculate mathematical expressions"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    print("\nConversation 1:")
    answer1 = agent.run("My name is Marcos", verbose=False)
    print("Q: My name is Marcos")
    print(f"A: {answer1}\n")

    print("Conversation 2 (should remember name):")
    answer2 = agent.run("What is my name?", verbose=False)
    print("Q: What is my name?")
    print(f"A: {answer2}\n")

    print("Conversation 3:")
    answer3 = agent.run("Calculate 15 * 8", verbose=False)
    print("Q: Calculate 15 * 8")
    print(f"A: {answer3}\n")

    print("Conversation 4 (should remember previous calculation):")
    answer4 = agent.run("What was my previous calculation?", verbose=False)
    print("Q: What was my previous calculation?")
    print(f"A: {answer4}\n")

    # Memory stats
    print("Memory Stats:")
    stats = agent.memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_chroma_memory():
    """Demo 2: ChromaDB Memory (vector database)"""
    if not CHROMA_AVAILABLE:
        print("\n⚠️  ChromaDB not available. Install with: pip install chromadb")
        return

    print("\n" + "=" * 80)
    print("DEMO 2: CHROMA MEMORY (Vector Database)")
    print("=" * 80)

    agent = ReactAgent(
        name="Smart Assistant",
        provider="gpt-4o-mini",
        memory=ChromaMemory(
            collection_name="demo_memory",
            persist_directory="./chroma_demo",
            embedding_function="default",  # or "openai" with API key
        ),
    )

    # Add some knowledge
    print("\nAdding knowledge to memory...")
    agent.memory.add("Python was created by Guido van Rossum in 1991", role="system")
    agent.memory.add("Python is known for its simple and readable syntax", role="system")
    agent.memory.add("React is a JavaScript library for building user interfaces", role="system")
    agent.memory.add("FastAPI is a modern web framework for Python", role="system")

    # Search memory
    print("\nSearching memory for 'Python programming'...")
    results = agent.memory.search("Python programming", top_k=2)
    for i, msg in enumerate(results, 1):
        print(f"{i}. [{msg.role}] {msg.content}")

    # Run agent with memory context
    print("\nAsking agent:")
    answer = agent.run("Tell me about Python", verbose=False)
    print("Q: Tell me about Python")
    print(f"A: {answer}\n")

    # Memory stats
    print("Memory Stats:")
    stats = agent.memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_faiss_memory():
    """Demo 3: FAISS Memory (high-performance)"""
    if not FAISS_AVAILABLE:
        print("\n⚠️  FAISS not available. Install with: pip install faiss-cpu")
        return

    print("\n" + "=" * 80)
    print("DEMO 3: FAISS MEMORY (High Performance)")
    print("=" * 80)

    agent = ReactAgent(
        name="Performance Assistant",
        provider="gpt-4o-mini",
        memory=FAISSMemory(
            index_path="./faiss_demo",
            dimension=1536,  # OpenAI embedding dimension
            index_type="Flat",  # or "IVF", "HNSW"
        ),
    )

    print("\nAdding technical documentation to memory...")
    agent.memory.add(
        "Docker is a platform for developing, shipping, and running applications in containers",
        role="system",
    )
    agent.memory.add(
        "Kubernetes is an orchestration system for automating deployment, scaling, and management",
        role="system",
    )
    agent.memory.add("Git is a distributed version control system", role="system")

    # Semantic search
    print("\nSearching for 'container technology'...")
    results = agent.memory.search("container technology", top_k=2)
    for i, msg in enumerate(results, 1):
        print(f"{i}. [{msg.role}] {msg.content}")

    # Run agent
    print("\nAsking agent:")
    answer = agent.run("What do you know about containerization?", verbose=False)
    print("Q: What do you know about containerization?")
    print(f"A: {answer}\n")

    # Memory stats
    print("Memory Stats:")
    stats = agent.memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_memory_comparison():
    """Demo 4: Compare memory search capabilities"""
    print("\n" + "=" * 80)
    print("DEMO 4: MEMORY SEARCH COMPARISON")
    print("=" * 80)

    # Create simple memory
    simple_mem = SimpleMemory()
    simple_mem.add("The quick brown fox jumps over the lazy dog")
    simple_mem.add("Python is a programming language")
    simple_mem.add("Machine learning is a subset of artificial intelligence")

    print("\nSimple Memory (keyword matching):")
    results = simple_mem.search("programming", top_k=2)
    for msg in results:
        print(f"  - {msg.content}")

    if CHROMA_AVAILABLE:
        print("\nChroma Memory (semantic search):")
        chroma_mem = ChromaMemory(
            collection_name="comparison_test",
            persist_directory="./chroma_test",
        )
        chroma_mem.add("The quick brown fox jumps over the lazy dog")
        chroma_mem.add("Python is a programming language")
        chroma_mem.add("Machine learning is a subset of artificial intelligence")

        # Semantic search should find related content even without exact keywords
        results = chroma_mem.search("coding in Python", top_k=2)
        for msg in results:
            print(f"  - {msg.content}")


def main():
    """Run all demos"""
    print("\n🧠 MEMORY SYSTEM DEMONSTRATION\n")

    # Demo 1: Simple Memory
    demo_simple_memory()

    # Demo 2: ChromaDB
    demo_chroma_memory()

    # Demo 3: FAISS
    demo_faiss_memory()

    # Demo 4: Comparison
    demo_memory_comparison()

    print("\n" + "=" * 80)
    print("✅ All demos completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
