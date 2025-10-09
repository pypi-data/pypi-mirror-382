"""
Example demonstrating built-in tools usage
"""

from react_agent_framework import ReactAgent

# Import tools to register them


def main():
    """Demonstrates different built-in tools"""

    print("=" * 80)
    print("BUILT-IN TOOLS DEMO")
    print("=" * 80)

    # Example 1: Calculator tool
    print("\n1. CALCULATOR TOOL")
    print("-" * 80)

    agent1 = ReactAgent(
        name="Math Assistant",
        provider="gpt-4o-mini",
        temperature=0,
    )

    # Register computation tools
    agent1.use_tools("computation.calculator")

    result = agent1.run(
        "What is 25 * 4 + 100 / 2?",
        verbose=True,
    )

    print(f"\n{'='*80}")
    print(f"FINAL ANSWER: {result}")
    print(f"{'='*80}")

    # Example 2: Filesystem tools
    print("\n\n2. FILESYSTEM TOOLS")
    print("-" * 80)

    agent2 = ReactAgent(
        name="File Assistant",
        provider="gpt-4o-mini",
        temperature=0,
    )

    # Register filesystem tools
    agent2.use_tools("filesystem.*")

    result = agent2.run(
        "List all Python files in the current directory",
        verbose=True,
    )

    print(f"\n{'='*80}")
    print(f"FINAL ANSWER: {result}")
    print(f"{'='*80}")

    # Example 3: Search tool
    print("\n\n3. SEARCH TOOL")
    print("-" * 80)

    agent3 = ReactAgent(
        name="Search Assistant",
        provider="gpt-4o-mini",
        temperature=0,
    )

    # Register search tools
    agent3.use_tools("search.duckduckgo")

    result = agent3.run(
        "What is the latest version of Python?",
        verbose=True,
    )

    print(f"\n{'='*80}")
    print(f"FINAL ANSWER: {result}")
    print(f"{'='*80}")

    # Example 4: Mix of tools
    print("\n\n4. MULTIPLE TOOLS")
    print("-" * 80)

    agent4 = ReactAgent(
        name="Multi-tool Assistant",
        provider="gpt-4o-mini",
        temperature=0,
    )

    # Register multiple tool categories
    agent4.use_tools(
        "search.duckduckgo",
        "computation.calculator",
        "filesystem.list",
    )

    result = agent4.run(
        "Search for the current Python version, calculate 2024 - 1991 (Python's birth year), and list the current directory",
        verbose=True,
    )

    print(f"\n{'='*80}")
    print(f"FINAL ANSWER: {result}")
    print(f"{'='*80}")

    # Example 5: All tools
    print("\n\n5. ALL TOOLS AT ONCE")
    print("-" * 80)

    agent5 = ReactAgent(
        name="Super Assistant",
        provider="gpt-4o-mini",
        temperature=0,
    )

    # Register ALL available tools
    agent5.use_tools("*")

    print(f"\nRegistered tools: {', '.join(agent5.get_tools().keys())}")

    result = agent5.run(
        "Calculate 15 * 3 and tell me the result",
        verbose=True,
    )

    print(f"\n{'='*80}")
    print(f"FINAL ANSWER: {result}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
