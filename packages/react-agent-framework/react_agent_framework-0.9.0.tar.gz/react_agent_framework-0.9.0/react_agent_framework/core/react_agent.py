"""
ReactAgent with multi-provider support
"""

from datetime import datetime
from typing import Callable, Dict, List, Optional, Any, Union
from functools import wraps
from dotenv import load_dotenv

from react_agent_framework.providers.base import BaseLLMProvider, Message
from react_agent_framework.providers.factory import create_provider
from react_agent_framework.core.memory.base import BaseMemory
from react_agent_framework.core.memory.simple import SimpleMemory
from react_agent_framework.core.objectives.objective import Objective
from react_agent_framework.core.objectives.tracker import ObjectiveTracker

# MCP support (optional)
try:
    from react_agent_framework.mcp.client import MCPClientSync
    from react_agent_framework.mcp.adapter import MCPToolAdapter

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

load_dotenv()


class ReactAgent:
    """
    ReAct Agent with FastAPI-style API and multi-provider support

    Example:
        ```python
        # OpenAI (default)
        agent = ReactAgent(
            name="Assistant",
            provider="gpt-4o-mini"
        )

        # Anthropic Claude
        agent = ReactAgent(
            name="Assistant",
            provider="anthropic://claude-3-5-sonnet-20241022"
        )

        # Google Gemini
        agent = ReactAgent(
            name="Assistant",
            provider="google://gemini-1.5-flash"
        )

        # Ollama (local)
        agent = ReactAgent(
            name="Assistant",
            provider="ollama://llama3.2"
        )

        @agent.tool()
        def search(query: str) -> str:
            '''Search the internet'''
            return results

        answer = agent.run("What is the capital of France?")
        ```
    """

    def __init__(
        self,
        name: str = "ReactAgent",
        description: str = "An intelligent ReAct agent",
        provider: Union[str, BaseLLMProvider] = "gpt-4o-mini",
        instructions: Optional[str] = None,
        temperature: float = 0,
        max_iterations: int = 10,
        api_key: Optional[str] = None,
        execution_date: Optional[datetime] = None,
        memory: Optional[BaseMemory] = None,
        enable_memory: bool = False,
        objectives: Optional[List[Objective]] = None,
    ):
        """
        Initialize ReactAgent

        Args:
            name: Agent name
            description: Agent description
            provider: LLM provider (string or BaseLLMProvider instance)
                     Examples: "gpt-4o-mini", "anthropic://claude-3-5-sonnet",
                              "google://gemini-1.5-flash", "ollama://llama3.2"
            instructions: Custom instructions for the agent
            temperature: Model temperature (0-1)
            max_iterations: Maximum iterations
            api_key: API key for the provider (uses env if not provided)
            execution_date: Execution date (uses now() if not provided)
            memory: Memory backend (SimpleMemory, ChromaMemory, FAISSMemory)
            enable_memory: Enable simple memory if no memory backend provided
            objectives: List of objectives for the agent to pursue
        """
        self.name = name
        self.description = description
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.execution_date = execution_date or datetime.now()

        # Create or use provider
        self.provider = create_provider(provider, api_key=api_key)

        self._tools: Dict[str, Callable] = {}
        self._tool_descriptions: Dict[str, str] = {}
        self.history: List[Dict[str, Any]] = []

        # Setup memory
        if memory is not None:
            self.memory: Optional[BaseMemory] = memory
        elif enable_memory:
            self.memory = SimpleMemory(max_messages=100)
        else:
            self.memory = None

        # Setup objectives
        self.objectives = ObjectiveTracker()
        if objectives:
            for obj in objectives:
                self.objectives.add(obj)

        # Setup MCP
        self.mcp_client: Optional[Any] = None
        self.mcp_adapter: Optional[Any] = None
        if MCP_AVAILABLE:
            self.mcp_client = MCPClientSync()
            self.mcp_adapter = MCPToolAdapter(self.mcp_client)

        # Default instructions
        self._instructions = instructions or self._get_default_instructions()

    def _get_default_instructions(self) -> str:
        """Returns default agent instructions"""
        return f"""You are {self.name}.

Description: {self.description}

Execution date: {self.execution_date.strftime('%Y-%m-%d %H:%M:%S')}
Provider: {self.provider.get_model_name()}

You are a ReAct (Reasoning + Acting) agent that solves problems by alternating between thinking and acting."""

    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        """
        Decorator to register a tool

        Args:
            name: Tool name (uses function name if not provided)
            description: Tool description (uses docstring if not provided)

        Example:
            ```python
            @agent.tool()
            def search(query: str) -> str:
                '''Search information on the internet'''
                return search_function(query)
            ```
        """

        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_desc = description or func.__doc__ or "No description"

            self._tools[tool_name] = func
            self._tool_descriptions[tool_name] = tool_desc.strip()

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def use_tools(self, *patterns: str, **tool_configs):
        """
        Register built-in tools by pattern

        Patterns:
        - "*" - All available tools
        - "search.*" - All search tools
        - "filesystem.*" - All filesystem tools
        - "computation.*" - All computation tools
        - "filesystem.read" - Specific tool

        Examples:
            agent.use_tools("search.*")  # All search tools
            agent.use_tools("filesystem.read", "filesystem.write")
            agent.use_tools("computation.calculator")
            agent.use_tools("*")  # All tools

        Args:
            *patterns: Tool patterns to register
            **tool_configs: Configuration for tool initialization
        """
        from react_agent_framework.tools.registry import ToolRegistry

        for pattern in patterns:
            tools = ToolRegistry.find_tools(pattern)
            for tool in tools:
                # Create wrapper function for the tool
                def tool_wrapper(input_text: str, tool_instance=tool) -> str:
                    return tool_instance(input_text)

                # Register tool
                self._tools[tool.name] = tool_wrapper
                self._tool_descriptions[tool.name] = tool.description

    def _create_system_prompt(self) -> str:
        """Creates system prompt with available tools and objectives"""
        tools_desc = "\n".join(
            [f"- {name}: {desc}" for name, desc in self._tool_descriptions.items()]
        )

        # Add objectives section if there are any
        objectives_section = ""
        if len(self.objectives) > 0:
            active = self.objectives.get_active()
            pending = self.objectives.get_pending()

            if active or pending:
                objectives_section = "\n\n## Your Current Objectives:\n"

                if active:
                    objectives_section += "\n🔄 Active Objectives:\n"
                    for obj in active:
                        objectives_section += f"- [{obj.priority.value.upper()}] {obj.goal} (Progress: {obj.progress:.0%})\n"
                        if obj.success_criteria:
                            objectives_section += (
                                f"  Success criteria: {', '.join(obj.success_criteria)}\n"
                            )

                if pending:
                    objectives_section += "\n⏳ Pending Objectives:\n"
                    for obj in pending[:3]:  # Show top 3 pending
                        objectives_section += f"- [{obj.priority.value.upper()}] {obj.goal}\n"

                objectives_section += "\nIMPORTANT: Keep these objectives in mind while working. Update progress when you make meaningful steps toward completing them.\n"

        return f"""{self._instructions}

Available tools:
{tools_desc}{objectives_section}

You must follow this format EXACTLY:

Thought: [your reasoning about what to do]
Action: [tool name]
Action Input: [input for the tool]

You will receive:
Observation: [action result]

Continue this cycle until you can answer. When you have the final answer, use:

Thought: [final reasoning]
Action: finish
Action Input: [your final answer]

IMPORTANT:
- Use EXACTLY the names "Thought:", "Action:", "Action Input:", "Observation:"
- Always start with a Thought
- Each action must have an input
- Use "finish" when you have the complete answer"""

    def _extract_thought_action(
        self, text: str
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Extracts thought, action and input from text"""
        lines = text.strip().split("\n")
        thought = None
        action = None
        action_input = None

        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                action_input = line.replace("Action Input:", "").strip()

        return thought, action, action_input

    def run(self, query: str, verbose: bool = False) -> str:
        """
        Run the agent with a query

        Args:
            query: The question/task
            verbose: If True, shows reasoning process

        Returns:
            The agent's final answer
        """
        # Add user query to memory
        if self.memory:
            self.memory.add(query, role="user")

        # Get relevant context from memory
        memory_context = ""
        if self.memory:
            context_messages = self.memory.get_context(query, max_tokens=1000)
            if context_messages:
                memory_context = "\n\nRelevant conversation history:\n"
                for msg in context_messages:
                    memory_context += f"[{msg.role}]: {msg.content}\n"

        # Create system prompt with memory context
        system_prompt = self._create_system_prompt()
        if memory_context:
            system_prompt += memory_context

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=query),
        ]

        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n{'='*60}")
                print(f"ITERATION {iteration + 1}")
                print(f"{'='*60}")

            # Call LLM via provider
            response_text = self.provider.generate(messages=messages, temperature=self.temperature)

            if verbose:
                print(f"\n{response_text}")

            # Extract thought, action and input
            thought, action, action_input = self._extract_thought_action(response_text)

            if not action:
                messages.append(Message(role="assistant", content=response_text))
                messages.append(
                    Message(
                        role="user",
                        content="Please provide an Action and Action Input following the specified format.",
                    )
                )
                continue

            # Add to messages
            messages.append(Message(role="assistant", content=response_text))

            # Check for finish
            if action.lower() == "finish":
                final_answer = action_input or "No answer provided"

                # Add assistant answer to memory
                if self.memory:
                    self.memory.add(final_answer, role="assistant")

                self.history.append(
                    {
                        "iteration": iteration + 1,
                        "thought": thought,
                        "action": action,
                        "final_answer": final_answer,
                    }
                )
                return final_answer

            # Execute tool
            if action in self._tools:
                observation = self._tools[action](action_input or "")

                if verbose:
                    obs_display = (
                        f"{observation[:200]}..." if len(observation) > 200 else observation
                    )
                    print(f"\nObservation: {obs_display}")

                messages.append(Message(role="user", content=f"Observation: {observation}"))

                self.history.append(
                    {
                        "iteration": iteration + 1,
                        "thought": thought,
                        "action": action,
                        "action_input": action_input,
                        "observation": observation,
                    }
                )
            else:
                error = (
                    f"Tool '{action}' not found. Available tools: {', '.join(self._tools.keys())}"
                )
                messages.append(Message(role="user", content=f"Observation: {error}"))

                if verbose:
                    print(f"\nObservation: {error}")

        return "Maximum number of iterations reached without conclusive answer."

    async def arun(self, query: str, verbose: bool = False) -> str:
        """
        Async version of run (future implementation)

        Args:
            query: The question/task
            verbose: If True, shows reasoning process

        Returns:
            The agent's final answer
        """
        # For now, just calls sync version
        # Future: implement with async providers
        return self.run(query, verbose)

    def clear_history(self) -> None:
        """Clears execution history"""
        self.history = []

    def get_tools(self) -> Dict[str, str]:
        """Returns dictionary with registered tools and their descriptions"""
        return self._tool_descriptions.copy()

    def get_provider_info(self) -> Dict[str, str]:
        """Returns information about the current provider"""
        return {
            "provider": self.provider.__class__.__name__,
            "model": self.provider.get_model_name(),
        }

    def add_mcp_server(
        self,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        auto_register: bool = True,
    ) -> int:
        """
        Connect to an MCP server and optionally auto-register its tools

        Args:
            command: Server command to execute
            args: Command arguments
            env: Environment variables
            name: Optional server name
            auto_register: Automatically register server tools with agent

        Returns:
            Server ID

        Example:
            # Connect to filesystem MCP server
            server_id = agent.add_mcp_server(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                name="filesystem"
            )

            # Connect to GitHub MCP server
            server_id = agent.add_mcp_server(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_TOKEN": "ghp_..."},
                name="github"
            )
        """
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP package not installed. Install with: pip install mcp"
            )

        if self.mcp_client is None:
            raise RuntimeError("MCP client not initialized")

        # Connect to server
        server_id = self.mcp_client.connect_server(command, args, env, name)

        # Auto-register tools if requested
        if auto_register and self.mcp_adapter:
            num_registered = self.mcp_adapter.register_tools_with_agent(self, server_id)
            print(f"✓ Registered {num_registered} tools from MCP server '{name or server_id}'")

        return server_id

    def list_mcp_servers(self) -> List[Dict[str, Any]]:
        """
        List connected MCP servers

        Returns:
            List of server information dictionaries
        """
        if not MCP_AVAILABLE or self.mcp_client is None:
            return []

        return self.mcp_client.list_servers()

    def list_mcp_tools(self, server_id: Optional[int] = None) -> List[str]:
        """
        List available MCP tools with descriptions

        Args:
            server_id: Optional server ID to filter (None = all servers)

        Returns:
            List of tool descriptions
        """
        if not MCP_AVAILABLE or self.mcp_adapter is None:
            return []

        return self.mcp_adapter.list_available_tools(server_id)

    def disconnect_mcp_server(self, server_id: int) -> None:
        """
        Disconnect from an MCP server

        Args:
            server_id: Server ID to disconnect
        """
        if not MCP_AVAILABLE or self.mcp_client is None:
            return

        self.mcp_client.disconnect_server(server_id)

    def __repr__(self) -> str:
        provider_info = self.get_provider_info()
        mcp_info = ""
        if MCP_AVAILABLE and self.mcp_client:
            num_servers = len(self.mcp_client.list_servers())
            if num_servers > 0:
                mcp_info = f", mcp_servers={num_servers}"
        return f"ReactAgent(name='{self.name}', provider={provider_info['provider']}, model='{provider_info['model']}', tools={len(self._tools)}{mcp_info})"
