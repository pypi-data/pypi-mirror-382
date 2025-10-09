"""
FastAPI-style example - Simple and elegant agent creation
"""

from react_agent_framework import ReactAgent
from duckduckgo_search import DDGS


# Create agent with rich configuration
agent = ReactAgent(
    name="Research Assistant",
    description="An AI assistant specialized in web research and calculations",
    provider="gpt-4o-mini",
    instructions="You are a helpful research assistant. Always provide accurate and well-researched answers.",
    max_iterations=10,
)


# Register tools using decorators (FastAPI style!)
@agent.tool()
def search(query: str) -> str:
    """Search the internet for information"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "No results found."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result['title']}\n   {result['body']}\n   URL: {result['href']}"
            )

        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search error: {str(e)}"


@agent.tool()
def calculate(expression: str) -> str:
    """Perform mathematical calculations"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def main():
    print("=" * 80)
    print("FASTAPI-STYLE EXAMPLE - ReAct Agent Framework")
    print("=" * 80)

    questions = [
        "What is the capital of France and how many inhabitants does it have?",
        "Calculate 15% of 340",
        "Search for the latest trends in AI agents",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'#' * 80}")
        print(f"QUESTION {i}: {question}")
        print(f"{'#' * 80}\n")

        answer = agent.run(question, verbose=True)

        print(f"\n{'=' * 80}")
        print(f"FINAL ANSWER: {answer}")
        print(f"{'=' * 80}\n")

        # Clear history for next question
        agent.clear_history()


if __name__ == "__main__":
    main()
