"""
Multi-provider example - Using different LLM providers
"""

from react_agent_framework import ReactAgent
from react_agent_framework.providers import (
    AnthropicProvider,
)


# Example 1: OpenAI (default - simple string)
print("=" * 80)
print("EXAMPLE 1: OpenAI Provider")
print("=" * 80)

agent_openai = ReactAgent(
    name="OpenAI Assistant", provider="gpt-4o-mini"  # Simple string, defaults to OpenAI
)


@agent_openai.tool()
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}! Nice to meet you!"


print(f"\nAgent: {agent_openai}")
print(f"Provider info: {agent_openai.get_provider_info()}")


# Example 2: OpenAI (explicit URL-style)
print("\n" + "=" * 80)
print("EXAMPLE 2: OpenAI with URL-style")
print("=" * 80)

agent_openai_url = ReactAgent(
    name="OpenAI URL Assistant", provider="openai://gpt-4o-mini"  # URL-style
)

print(f"Agent: {agent_openai_url}")


# Example 3: Anthropic Claude (URL-style)
print("\n" + "=" * 80)
print("EXAMPLE 3: Anthropic Claude Provider")
print("=" * 80)

agent_claude = ReactAgent(
    name="Claude Assistant", provider="anthropic://claude-3-5-sonnet-20241022"
)


@agent_claude.tool()
def calculate(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


print(f"Agent: {agent_claude}")
print(f"Provider info: {agent_claude.get_provider_info()}")


# Example 4: Anthropic Claude (object-style)
print("\n" + "=" * 80)
print("EXAMPLE 4: Anthropic with Provider Object")
print("=" * 80)

claude_provider = AnthropicProvider(
    model="claude-3-5-sonnet-20241022",
    # api_key="your-key-here"  # Optional, uses env
)

agent_claude_obj = ReactAgent(name="Claude Object Assistant", provider=claude_provider)

print(f"Agent: {agent_claude_obj}")


# Example 5: Google Gemini
print("\n" + "=" * 80)
print("EXAMPLE 5: Google Gemini Provider")
print("=" * 80)

agent_gemini = ReactAgent(name="Gemini Assistant", provider="google://gemini-1.5-flash")

print(f"Agent: {agent_gemini}")
print(f"Provider info: {agent_gemini.get_provider_info()}")


# Example 6: Ollama (local LLM)
print("\n" + "=" * 80)
print("EXAMPLE 6: Ollama (Local) Provider")
print("=" * 80)

agent_ollama = ReactAgent(
    name="Ollama Assistant", provider="ollama://llama3.2"  # Requires Ollama running locally
)


@agent_ollama.tool()
def get_time() -> str:
    """Get current time"""
    from datetime import datetime

    return datetime.now().strftime("%H:%M:%S")


print(f"Agent: {agent_ollama}")
print(f"Provider info: {agent_ollama.get_provider_info()}")


# Example 7: Auto-detection from model name
print("\n" + "=" * 80)
print("EXAMPLE 7: Auto-detection")
print("=" * 80)

# These will be auto-detected based on model name prefix:
agent_auto_claude = ReactAgent(provider="claude-3-5-sonnet-20241022")  # Auto -> Anthropic
agent_auto_gemini = ReactAgent(provider="gemini-1.5-flash")  # Auto -> Google
agent_auto_llama = ReactAgent(provider="llama3.2")  # Auto -> Ollama

print(f"Auto Claude: {agent_auto_claude.get_provider_info()}")
print(f"Auto Gemini: {agent_auto_gemini.get_provider_info()}")
print(f"Auto Llama: {agent_auto_llama.get_provider_info()}")


# Example 8: Comparison table
print("\n" + "=" * 80)
print("PROVIDER COMPARISON")
print("=" * 80)

providers = [
    ("OpenAI", agent_openai),
    ("Anthropic", agent_claude),
    ("Google", agent_gemini),
    ("Ollama", agent_ollama),
]

print(f"\n{'Provider':<15} {'Model':<30} {'Tools':<10}")
print("-" * 60)

for name, agent in providers:
    info = agent.get_provider_info()
    print(f"{info['provider']:<15} {info['model']:<30} {len(agent.get_tools()):<10}")

print("\n" + "=" * 80)
print("All providers configured successfully!")
print("=" * 80)
