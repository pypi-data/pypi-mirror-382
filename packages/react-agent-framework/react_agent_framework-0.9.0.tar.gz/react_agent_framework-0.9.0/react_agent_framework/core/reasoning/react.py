"""
ReAct (Reasoning + Acting) strategy

Classic iterative approach:
1. Think about what to do
2. Take an action
3. Observe the result
4. Repeat until answer is found
"""

from datetime import datetime
from typing import Callable, Dict
from react_agent_framework.core.reasoning.base import BaseReasoning, ReasoningResult
from react_agent_framework.providers.base import Message


class ReActReasoning(BaseReasoning):
    """
    ReAct reasoning strategy

    Iterative thought-action-observation loop
    """

    def reason(
        self,
        query: str,
        tools: Dict[str, Callable],
        tool_descriptions: Dict[str, str],
        llm_generate: Callable,
        system_prompt: str,
        **kwargs,
    ) -> ReasoningResult:
        """
        Execute ReAct reasoning

        Args:
            query: The question/task
            tools: Dictionary of available tools
            tool_descriptions: Tool descriptions
            llm_generate: Function to call LLM
            system_prompt: System instructions

        Returns:
            ReasoningResult with answer
        """
        start_time = datetime.now()
        trace = []

        # Create initial messages
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=query),
        ]

        self._log(f"\n{'='*60}")
        self._log("ReAct Reasoning Started")
        self._log(f"{'='*60}")
        self._log(f"Query: {query}\n")

        for iteration in range(self.max_iterations):
            self._log(f"\n{'='*60}")
            self._log(f"ITERATION {iteration + 1}")
            self._log(f"{'='*60}")

            # Call LLM
            response_text = llm_generate(messages)

            self._log(f"\n{response_text}")

            # Extract thought, action and input
            thought, action, action_input = self._extract_thought_action(response_text)

            # Record iteration
            iteration_data = {
                "iteration": iteration + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input,
                "llm_response": response_text,
            }

            if not action:
                # No action found, prompt for correct format
                messages.append(Message(role="assistant", content=response_text))
                messages.append(
                    Message(
                        role="user",
                        content="Please provide an Action and Action Input following the specified format.",
                    )
                )
                iteration_data["observation"] = "No action provided"
                trace.append(iteration_data)
                continue

            # Add assistant response to messages
            messages.append(Message(role="assistant", content=response_text))

            # Check for finish
            if action.lower() == "finish":
                final_answer = action_input or "No answer provided"

                iteration_data["final_answer"] = final_answer
                trace.append(iteration_data)

                self._log(f"\n{'='*60}")
                self._log("✅ FINAL ANSWER")
                self._log(f"{'='*60}")
                self._log(f"{final_answer}\n")

                return ReasoningResult(
                    answer=final_answer,
                    iterations=iteration + 1,
                    success=True,
                    trace=trace,
                    start_time=start_time,
                    end_time=datetime.now(),
                    metadata={"strategy": "react"},
                )

            # Execute tool
            if action in tools:
                observation = tools[action](action_input or "")

                self._log(f"\nObservation: {observation[:200]}...")

                messages.append(Message(role="user", content=f"Observation: {observation}"))

                iteration_data["observation"] = observation
                trace.append(iteration_data)
            else:
                error = f"Tool '{action}' not found. Available tools: {', '.join(tools.keys())}"
                messages.append(Message(role="user", content=f"Observation: {error}"))

                self._log(f"\nObservation: {error}")

                iteration_data["observation"] = error
                trace.append(iteration_data)

        # Max iterations reached
        self._log(f"\n{'='*60}")
        self._log("⚠️ Maximum iterations reached")
        self._log(f"{'='*60}\n")

        return ReasoningResult(
            answer="Maximum number of iterations reached without conclusive answer.",
            iterations=self.max_iterations,
            success=False,
            trace=trace,
            start_time=start_time,
            end_time=datetime.now(),
            metadata={"strategy": "react", "max_iterations_reached": True},
        )
