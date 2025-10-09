#!/usr/bin/env python
"""
ReAct Agent Framework CLI using Typer
"""

import typer
from rich.console import Console
from rich.panel import Panel
from duckduckgo_search import DDGS

from react_agent_framework import ReactAgent, __version__

app = typer.Typer(
    name="react-agent",
    help="ReAct Agent Framework - CLI for creating agents with reasoning and acting",
    add_completion=False,
)
console = Console()


def create_agent(model: str, max_iterations: int) -> ReactAgent:
    """Create and configure agent with built-in tools"""
    agent = ReactAgent(
        name="CLI Assistant",
        description="A command-line AI assistant",
        provider=model,
        max_iterations=max_iterations,
    )

    @agent.tool()
    def search(query: str) -> str:
        """Search the internet for information"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

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

    return agent


@app.command()
def ask(
    question: str = typer.Argument(..., help="The question you want to ask the agent"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show step-by-step agent reasoning"
    ),
    model: str = typer.Option(
        "gpt-4o-mini", "--model", "-m", help="OpenAI model to use (gpt-4o-mini, gpt-4, etc)"
    ),
    max_iterations: int = typer.Option(
        10, "--max-iterations", "-i", help="Maximum number of agent iterations"
    ),
):
    """
    Ask a question to the ReAct agent and get an answer
    """
    try:
        # Create agent
        agent = create_agent(model, max_iterations)

        # Show question
        console.print()
        console.print(
            Panel(f"[bold cyan]{question}[/bold cyan]", title="🤔 Question", border_style="cyan")
        )

        # Run agent
        if not verbose:
            with console.status("[bold green]Processing...", spinner="dots"):
                answer = agent.run(question, verbose=False)
        else:
            console.print("\n[bold yellow]⚙️  Processing (verbose mode)[/bold yellow]\n")
            answer = agent.run(question, verbose=True)

        # Show final answer
        console.print()
        console.print(
            Panel(
                f"[bold green]{answer}[/bold green]", title="✅ Final Answer", border_style="green"
            )
        )
        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def interactive(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show step-by-step agent reasoning"
    ),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="OpenAI model to use"),
):
    """
    Interactive mode - ask multiple questions in sequence
    """
    console.print()
    console.print(
        Panel(
            "[bold cyan]Interactive Mode - ReAct Agent Framework[/bold cyan]\n\n"
            "Type your questions or 'exit' to quit.\n"
            f"Verbose mode: [yellow]{'Enabled' if verbose else 'Disabled'}[/yellow]\n"
            f"Model: [yellow]{model}[/yellow]",
            title="🤖 ReAct Agent",
            border_style="cyan",
        )
    )
    console.print()

    # Create agent once
    agent = create_agent(model, max_iterations=10)

    while True:
        try:
            # Get question
            question = console.input("[bold cyan]❓ Question:[/bold cyan] ")

            if question.lower() in ["exit", "quit", "q"]:
                console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                break

            if not question.strip():
                continue

            # Run agent
            if not verbose:
                with console.status("[bold green]Processing...", spinner="dots"):
                    answer = agent.run(question, verbose=False)
            else:
                console.print("\n[bold yellow]⚙️  Processing:[/bold yellow]\n")
                answer = agent.run(question, verbose=True)

            # Show answer
            console.print()
            console.print(
                Panel(f"[bold green]{answer}[/bold green]", title="✅ Answer", border_style="green")
            )
            console.print()

            # Clear history for next question
            agent.clear_history()

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}\n")


@app.command()
def version():
    """
    Show framework version
    """
    console.print()
    console.print(
        Panel(
            "[bold cyan]ReAct Agent Framework[/bold cyan]\n"
            f"Version: [yellow]{__version__}[/yellow]\n"
            "Default model: [yellow]gpt-4o-mini[/yellow]",
            title="📋 Version",
            border_style="cyan",
        )
    )
    console.print()


def main():
    """CLI entry point"""
    app()


if __name__ == "__main__":
    main()
