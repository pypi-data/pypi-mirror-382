"""
Example: Creating custom tools with decorators
"""

from react_agent_framework import ReactAgent
from datetime import datetime
import random


# Create specialized agent
agent = ReactAgent(
    name="Personal Assistant",
    description="A versatile personal assistant with various utilities",
    provider="gpt-4o-mini",
    instructions="""You are a personal assistant that helps with:
    - Date and time information
    - Random number generation
    - Temperature conversions
    Always be helpful and accurate.""",
)


@agent.tool()
def get_datetime() -> str:
    """Get current date and time"""
    now = datetime.now()
    return f"Date: {now.strftime('%Y-%m-%d')}, Time: {now.strftime('%H:%M:%S')}"


@agent.tool()
def random_number(range_str: str) -> str:
    """Generate random number. Input format: 'min-max' (e.g., '1-100')"""
    try:
        min_val, max_val = map(int, range_str.split("-"))
        number = random.randint(min_val, max_val)
        return f"Random number between {min_val} and {max_val}: {number}"
    except Exception as e:
        return f"Error: {str(e)}. Use format 'min-max' (e.g., '1-100')"


@agent.tool()
def convert_temperature(input_str: str) -> str:
    """Convert temperature. Format: 'C to F: 25' or 'F to C: 77'"""
    try:
        input_str = input_str.strip()

        if "C to F" in input_str or "c to f" in input_str:
            celsius = float(input_str.split(":")[-1].strip())
            fahrenheit = (celsius * 9 / 5) + 32
            return f"{celsius}°C = {fahrenheit}°F"

        elif "F to C" in input_str or "f to c" in input_str:
            fahrenheit = float(input_str.split(":")[-1].strip())
            celsius = (fahrenheit - 32) * 5 / 9
            return f"{fahrenheit}°F = {celsius:.2f}°C"

        else:
            return "Invalid format. Use 'C to F: value' or 'F to C: value'"

    except Exception as e:
        return f"Conversion error: {str(e)}"


@agent.tool(name="greet", description="Greet someone by name")
def greet_person(name: str) -> str:
    """Custom greeting"""
    return f"Hello, {name}! How can I assist you today?"


def main():
    print("=" * 80)
    print("CUSTOM TOOLS EXAMPLE - ReAct Agent Framework")
    print("=" * 80)

    # Show registered tools
    print("\nRegistered Tools:")
    for tool_name, tool_desc in agent.get_tools().items():
        print(f"  - {tool_name}: {tool_desc}")

    questions = [
        "What time is it now?",
        "Generate a random number between 1 and 100",
        "Convert 25 degrees Celsius to Fahrenheit",
        "Greet John",
    ]

    for question in questions:
        print(f"\n{'#' * 80}")
        print(f"Question: {question}")
        print(f"{'#' * 80}\n")

        answer = agent.run(question, verbose=True)

        print(f"\n{'=' * 80}")
        print(f"Answer: {answer}")
        print(f"{'=' * 80}\n")

        agent.clear_history()


if __name__ == "__main__":
    main()
